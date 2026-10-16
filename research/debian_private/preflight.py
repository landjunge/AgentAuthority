"""Practical UID/key/socket and encrypted-storage prerequisites, before any action."""

import json
import pwd
import subprocess
import time
from pathlib import Path

from research.debian_private.ipc import RUNTIME, SECURE


def as_user(name, code):
    p = pwd.getpwnam(name)
    return subprocess.run(
        ["/usr/bin/python3", "-B", "-c", code],
        user=p.pw_uid,
        group=p.pw_gid,
        extra_groups=[],
        cwd="/opt/aa-private",
        env={"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        timeout=6,
        check=False,
    )


def main():
    checks = []

    def check(name, passed, **extra):
        checks.append({"case": name, "pass": passed, **extra})

    targets = {
        "aa-signer": SECURE / "signer/report.pem",
        "aa-runner": SECURE / "runner/runner.pem",
        "aa-registrar": SECURE / "registrar/bootstrap/root/ca-private.pem",
        "aa-api": SECURE / "api/service.sqlite",
    }
    for actor in (
        "aa-api",
        "aa-signer",
        "aa-verifier",
        "aa-runner",
        "aa-registrar",
        "aa-test-a",
        "aa-test-b",
    ):
        for owner, path in targets.items():
            if actor == owner:
                continue
            code = f"""import os,errno
try:
 fd=os.open({str(path)!r},os.O_RDONLY|os.O_NOFOLLOW);os.close(fd)
except OSError as e:
 raise SystemExit(0 if e.errno==errno.EACCES else 2)
raise SystemExit(1)
"""
            result = as_user(actor, code)
            check(actor + " denied " + owner + " object", result.returncode == 0)
    for actor in ("aa-api", "aa-signer", "aa-verifier", "aa-registrar", "aa-test-a", "aa-test-b"):
        result = as_user(
            actor,
            "import socket,errno\ns=socket.socket(socket.AF_UNIX)\ntry:s.connect('/run/aa-private/collector.sock')\nexcept OSError as e:raise SystemExit(0 if e.errno==errno.EACCES else 2)\nraise SystemExit(1)",
        )
        check(actor + " denied collector socket", result.returncode == 0)
    for actor in ("aa-runner", "aa-verifier", "aa-registrar", "aa-test-a", "aa-test-b"):
        result = as_user(
            actor,
            "import socket,errno\ns=socket.socket(socket.AF_UNIX)\ntry:s.connect('/run/aa-private/signer.sock')\nexcept OSError as e:raise SystemExit(0 if e.errno==errno.EACCES else 2)\nraise SystemExit(1)",
        )
        check(actor + " denied signer socket", result.returncode == 0)
    result = as_user(
        "aa-api",
        "from research.debian_private.ipc import component\nfrom research.private_service.protocol import Problem\ntry:component('report',{'arbitrary':'sign this'})\nexcept Problem as e:raise SystemExit(0 if e.code=='IPC_COMPONENT_FAILED' else 2)\nraise SystemExit(1)",
    )
    check("real signer refuses arbitrary API signing", result.returncode == 0)
    result = as_user(
        "aa-api",
        "from research.debian_private.ipc import component\nfrom research.private_service.protocol import Problem\ntry:component('verify',{'payload':{},'pins':{},'expected':{'job_id':'0'*32}})\nexcept Problem as e:raise SystemExit(0 if e.code=='IPC_COMPONENT_FAILED' else 2)\nraise SystemExit(1)",
    )
    check("real verifier refuses invented independent pin", result.returncode == 0)
    result = as_user(
        "aa-api",
        "import ctypes,errno,struct\nr=ctypes.CDLL(None,use_errno=True);a=ctypes.create_string_buffer(struct.pack('7I',2,4,4,1,0,0,0));v=r.syscall(321,0,ctypes.byref(a),28);raise SystemExit(0 if v==-1 and ctypes.get_errno()==errno.EPERM else 1)",
    )
    check("API UID BPF syscall denied by kernel", result.returncode == 0)
    states = {}
    for name in ("api", "signer", "verifier"):
        service = "aa-private-" + name + ".service"
        result = subprocess.check_output(
            [
                "systemctl",
                "show",
                service,
                "-p",
                "MainPID",
                "-p",
                "ActiveState",
                "-p",
                "User",
                "-p",
                "MemoryMax",
                "-p",
                "MemorySwapMax",
                "-p",
                "TasksMax",
            ]
        ).decode()
        state = dict(l.split("=", 1) for l in result.splitlines())
        if int(state["MainPID"]):
            raw = Path("/proc/" + state["MainPID"] + "/status").read_text()
            caps = {
                l.split(":")[0]: l.split()[1]
                for l in raw.splitlines()
                if l.startswith(("CapEff:", "CapPrm:", "CapInh:", "CapAmb:", "NoNewPrivs:"))
            }
            check(
                name + " actual unprivileged process",
                all(int(v, 16) == 0 for k, v in caps.items() if k.startswith("Cap"))
                and caps["NoNewPrivs"] == "1",
                capabilities=caps,
            )
        else:
            check(name + " running", False)
        states[name] = state
    check("secure mount active", SECURE.is_mount())
    mount = subprocess.check_output(["findmnt", "--json", str(SECURE)]).decode()
    check(
        "encrypted mapped source and noexec nosuid nodev",
        all(s in mount for s in ("/dev/mapper/aa-private-epoch", "noexec", "nosuid", "nodev")),
    )
    dump = subprocess.check_output(
        ["dumpe2fs", "-h", "/dev/mapper/aa-private-epoch"], stderr=subprocess.DEVNULL
    ).decode()
    features = next(l for l in dump.splitlines() if l.startswith("Filesystem features:"))
    check("encrypted volume no ext4 journal", "has_journal" not in features)
    crypto = subprocess.check_output(["cryptsetup", "status", "aa-private-epoch"]).decode()
    check("AES XTS 512-bit active", "aes-xts-plain64" in crypto and "512 bits" in crypto)
    check(
        "aggregate swap disabled",
        Path("/sys/fs/cgroup/aa.slice/aa-private.slice/memory.swap.max").read_text().strip() == "0",
    )
    check(
        "aggregate CPU hard quota",
        0
        < int(Path("/sys/fs/cgroup/aa.slice/aa-private.slice/cpu.max").read_text().split()[0])
        <= 40000
        and Path("/sys/fs/cgroup/aa.slice/aa-private.slice/cpu.max").read_text().split()[1]
        == "100000",
    )
    check(
        "fresh monitor, no abort",
        not (RUNTIME / "ABORT").exists()
        and time.time() - (RUNTIME / "heartbeat").stat().st_mtime < 2.5,
    )
    record = {
        "checks": checks,
        "passed": sum(c["pass"] for c in checks),
        "failed": [c["case"] for c in checks if not c["pass"]],
        "services": states,
        "scope": "prerequisites only; no synthetic action performed",
    }
    Path("/var/lib/aa-private-install-20261017/preflight.json").write_text(
        json.dumps(record, indent=2)
    )
    print(json.dumps(record))
    return int(bool(record["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
