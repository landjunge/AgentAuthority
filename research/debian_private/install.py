"""Private bootstrap and units. No production paths, listeners or keys replaced."""

import hashlib
import json
import os
import pwd
import subprocess
from pathlib import Path

from research.debian_private.ipc import SECURE
from research.private_service.configuration import api_configuration
from research.private_service.demo import initialize
from research.private_service.protocol import create_ca

SYSTEM = Path("/etc/systemd/system")


def owner(path, name, mode=0o600):
    entry = pwd.getpwnam(name)
    os.chown(path, entry.pw_uid, entry.pw_gid)
    path.chmod(mode)


def main():
    os.umask(0o077)
    protocol = Path("/opt/aa-private/research/a4_completion/protocol.py")
    require_target = Path("../a2_linux/protocol.py")
    if protocol.is_symlink():
        assert protocol.readlink() == require_target
    else:
        assert not protocol.exists()
        protocol.symlink_to(require_target)
    assert "aa-private.slice" in Path("/proc/self/cgroup").read_text()
    assert SECURE.is_mount() and (Path("/run/aa-private/epoch")).is_file()
    bootstrap = SECURE / "registrar/bootstrap"
    config, _root, keys = initialize(bootstrap)
    report = SECURE / "signer/report.pem"
    Path(config["report_private_key"]).rename(report)
    owner(report, "aa-signer")
    runner = SECURE / "runner/runner.pem"
    Path(config["runner_private_key"]).rename(runner)
    owner(runner, "aa-runner")
    keys["runner"]["private"] = str(runner)
    (SECURE / "runner/config.json").write_text(json.dumps({"token": config["runner_token"]}))
    owner(SECURE / "runner/config.json", "aa-runner")
    ca, public = create_ca(SECURE / "collector/transport")
    ca.rename(SECURE / "collector/transport.pem")
    (SECURE / "collector/transport").rmdir()
    (SECURE / "collector/HARDSTOP").write_text(
        "Unqualified until all Linux storage/isolation/resource prerequisites pass.\n"
    )
    (SECURE / "collector/tmp").mkdir(mode=0o711)
    (SECURE / "collector/tmp").chmod(0o711)
    (SECURE / "collector/tmp/compiler").mkdir(mode=0o700)
    conf = Path("/etc/aa-private")
    conf.mkdir(mode=0o755)
    conf.chmod(0o755)
    (conf / "api.json").write_text(json.dumps(api_configuration(config)))
    os.chown(conf / "api.json", 0, pwd.getpwnam("aa-api").pw_gid)
    (conf / "api.json").chmod(0o640)
    (conf / "collector-public.json").write_text(json.dumps({"public": public}))
    (conf / "collector-public.json").chmod(0o444)
    (conf / "report-public.json").write_text(json.dumps({"public": config["report_public_key"]}))
    (conf / "report-public.json").chmod(0o444)
    (conf / "collector.json").write_text(
        json.dumps({k: keys[k]["public"] for k in ("sender", "receiver")})
    )
    # Full synthetic operator credentials remain encrypted; API receives only hashes.
    config["report_private_key"] = str(report)
    config["runner_private_key"] = str(runner)
    config["keys"] = keys
    for p in bootstrap.rglob("*"):
        owner(p, "aa-registrar", 0o700 if p.is_dir() else 0o600)
    owner(bootstrap, "aa-registrar", 0o700)
    (bootstrap / "config.json").write_text(json.dumps(config))
    owner(bootstrap / "config.json", "aa-registrar")
    common = """Slice=aa-private.slice
WorkingDirectory=/opt/aa-private
Environment=PYTHONDONTWRITEBYTECODE=1
UMask=0077
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectKernelLogs=yes
ProtectControlGroups=yes
ProtectClock=yes
ProtectProc=invisible
RestrictSUIDSGID=yes
RestrictRealtime=yes
LockPersonality=yes
RestrictNamespaces=yes
MemorySwapMax=0
LimitCORE=0
LimitNOFILE=64
TimeoutStopSec=5
KillMode=control-group
SendSIGKILL=yes
StandardOutput=null
StandardError=null
InaccessiblePaths=-/opt/4allpass -/opt/ki-helper-runtime -/opt/ki-hilfezentrum -/var/www -/srv -/var/lib/docker -/run/docker.sock -/etc/ssh -/etc/ssl/private
"""
    units = {}
    for name, allowed in [
        ("signer", "aa-api"),
        ("verifier", "aa-api"),
        ("control", "aa-runner"),
        ("collector", "aa-runner"),
    ]:
        service = "api" if name == "control" else name
        unit = f"""[Unit]
Description=Private AA {name} authenticated local channel
ConditionPathIsMountPoint=/var/lib/aa-private/secure
[Socket]
ListenStream=/run/aa-private/{name}.sock
SocketUser={"root" if name in ("control", "collector") else "aa-" + name}
SocketGroup={allowed}
SocketMode=0660
Backlog=2
Service=aa-private-{service}.service
RemoveOnStop=yes
"""
        units["aa-private-" + name + ".socket"] = unit
    units["aa-private-api.service"] = (
        """[Unit]
Description=Private Agent Authority loopback API
Requires=aa-private-signer.socket aa-private-verifier.socket aa-private-control.socket aa-private-watchdog.service
After=aa-private-signer.socket aa-private-verifier.socket aa-private-watchdog.service
ConditionPathIsMountPoint=/var/lib/aa-private/secure
ConditionPathExists=/run/aa-private/epoch
[Service]
User=aa-api
Group=aa-api
Environment=MALLOC_ARENA_MAX=2
ExecStart=/usr/bin/python3 -B -m research.debian_private.api
CapabilityBoundingSet=
AmbientCapabilities=
RestrictAddressFamilies=AF_UNIX AF_INET
IPAddressDeny=any
IPAddressAllow=localhost
SystemCallFilter=~bpf perf_event_open ptrace process_vm_readv process_vm_writev
MemoryMax=128M
TasksMax=8
ReadWritePaths=/var/lib/aa-private/secure/api
InaccessiblePaths=/var/lib/aa-private/secure/signer /var/lib/aa-private/secure/verifier /var/lib/aa-private/secure/runner /var/lib/aa-private/secure/registrar /var/lib/aa-private/secure/collector /var/lib/aa-private/secure/verdicts
TemporaryFileSystem=/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
TemporaryFileSystem=/var/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
"""
        + common
    )
    for name, mem in [("signer", 96), ("verifier", 192)]:
        units["aa-private-" + name + ".service"] = (
            f"""[Unit]
Description=Private AA isolated {name}
ConditionPathIsMountPoint=/var/lib/aa-private/secure
[Service]
User=aa-{name}
Group={"aa-signer" if name == "verifier" else "aa-" + name}
ExecStart=/usr/bin/python3 -B -m research.debian_private.components {name}
CapabilityBoundingSet=
AmbientCapabilities=
RestrictAddressFamilies=AF_UNIX
PrivateNetwork=yes
SystemCallFilter=~bpf perf_event_open ptrace process_vm_readv process_vm_writev
MemoryMax={mem}M
TasksMax=4
ReadWritePaths=/var/lib/aa-private/secure/{name}"""
            + (" /var/lib/aa-private/secure/verdicts" if name == "verifier" else "")
            + """
TemporaryFileSystem=/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
TemporaryFileSystem=/var/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
"""
            + common
        )
    units["aa-private-collector.service"] = (
        """[Unit]
Description=Private AA constrained synthetic collector
ConditionPathIsMountPoint=/var/lib/aa-private/secure
ConditionPathExists=/run/aa-private/epoch
Requires=aa-private-watchdog.service
After=aa-private-watchdog.service
[Service]
User=root
ExecStart=/usr/bin/python3 -B -m research.debian_private.collector
CapabilityBoundingSet=CAP_KILL CAP_BPF CAP_PERFMON CAP_SYS_ADMIN CAP_SETUID CAP_SETGID CAP_CHOWN CAP_DAC_OVERRIDE
AmbientCapabilities=CAP_SETUID
RestrictAddressFamilies=AF_UNIX AF_NETLINK
PrivateNetwork=yes
MemoryMax=512M
TasksMax=12
LimitMEMLOCK=64M
LimitFSIZE=16M
RuntimeMaxSec=180
ReadWritePaths=/var/lib/aa-private/secure/collector /var/lib/aa-private/secure/verifier /sys/kernel/tracing
ReadWritePaths=/sys/kernel/debug/tracing
BindPaths=/var/lib/aa-private/secure/collector/tmp:/tmp
BindPaths=/var/lib/aa-private/secure/collector/tmp:/var/tmp
Environment=TMPDIR=/tmp/compiler
Environment=BCC_KERNEL_SOURCE=/opt/aa-private/kernel-headers-view
"""
        + common
    )
    units["aa-private-runner.service"] = (
        """[Unit]
Description=Private AA single synthetic runner, operator started
Requires=aa-private-control.socket aa-private-collector.socket aa-private-watchdog.service
After=aa-private-api.service aa-private-watchdog.service
ConditionPathIsMountPoint=/var/lib/aa-private/secure
ConditionPathExists=/run/aa-private/epoch
[Service]
Type=oneshot
User=aa-runner
Group=aa-runner
ExecStart=/usr/bin/python3 -B -m research.debian_private.runner
CapabilityBoundingSet=
AmbientCapabilities=
RestrictAddressFamilies=AF_UNIX AF_INET
IPAddressDeny=any
IPAddressAllow=localhost
MemoryMax=64M
TasksMax=2
TimeoutStartSec=175
ReadWritePaths=/var/lib/aa-private/secure/runner
TemporaryFileSystem=/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
TemporaryFileSystem=/var/tmp:rw,nosuid,nodev,noexec,noswap,size=4M
"""
        + common
    )
    units["aa-private-collector.service"] += (
        "InaccessiblePaths=/var/lib/aa-private/secure/signer /var/lib/aa-private/secure/runner /var/lib/aa-private/secure/registrar /var/lib/aa-private/secure/api /var/lib/aa-private/secure/verdicts\n"
    )
    units["aa-private-runner.service"] = units["aa-private-runner.service"].replace(
        "RuntimeMaxSec=175", "TimeoutStartSec=175"
    )
    for name, value in units.items():
        p = SYSTEM / name
        assert not p.exists()
        p.write_text(value)
        p.chmod(0o644)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(
        ["systemd-analyze", "verify", *[str(SYSTEM / n) for n in units]], check=True, timeout=15
    )
    subprocess.run(
        [
            "systemctl",
            "start",
            "aa-private-control.socket",
            "aa-private-signer.socket",
            "aa-private-verifier.socket",
            "aa-private-collector.socket",
            "aa-private-api.service",
        ],
        check=True,
        timeout=15,
    )
    record = {
        "units": {n: hashlib.sha256(v.encode()).hexdigest() for n, v in units.items()},
        "accounts": {
            n: pwd.getpwnam(n).pw_uid
            for n in [
                "aa-api",
                "aa-signer",
                "aa-verifier",
                "aa-runner",
                "aa-registrar",
                "aa-test-a",
                "aa-test-b",
            ]
        },
        "report_public_key": config["report_public_key"],
        "root_public_key": config["root_pins"]["test-a"],
        "loopback": "127.0.0.1:8765",
        "runner_hardstop": True,
        "enabled_on_boot": False,
    }
    Path("/var/lib/aa-private-install-20261017/installed.json").write_text(
        json.dumps(record, indent=2)
    )
    print(json.dumps(record))


if __name__ == "__main__":
    main()
