"""Destructive counterexamples only in our bounded cgroups/encrypted test files."""

import json
import secrets
import subprocess
import time
from pathlib import Path

from research.debian_private.ipc import RUNTIME, SECURE


def main():
    checks = []

    def check(name, value, **extra):
        checks.append({"case": name, "pass": bool(value), **extra})

    def unit(name, properties, code, timeout=15):
        subprocess.run(
            ["systemctl", "reset-failed", "aa-private-limit-" + name + ".service"],
            check=False,
            capture_output=True,
        )
        command = [
            "systemd-run",
            "--unit=aa-private-limit-" + name,
            "--slice=aa-private.slice",
            "--wait",
            "--pipe",
            "--property=MemorySwapMax=0",
            "--property=LimitCORE=0",
            "--property=RuntimeMaxSec=8",
        ]
        command += ["--property=" + p for p in properties]
        return subprocess.run(
            command + ["/usr/bin/python3", "-B", "-c", code],
            capture_output=True,
            timeout=timeout,
            check=False,
        )

    def state(name):
        raw = subprocess.check_output(
            [
                "systemctl",
                "show",
                "aa-private-" + name + ".service",
                "-p",
                "MainPID",
                "-p",
                "ActiveState",
                "-p",
                "Result",
                "-p",
                "ExecMainStatus",
            ]
        ).decode()
        return dict(l.split("=", 1) for l in raw.splitlines())

    guard = RUNTIME / "guard-check"
    guard.write_bytes(b"operator-only-stop-qualification")
    guard.chmod(0o600)
    subprocess.run(["systemctl", "start", "--no-block", "aa-private-runner.service"], check=True)
    for _ in range(40):
        runner = state("runner")
        collector = state("collector")
        if int(runner["MainPID"]) and int(collector["MainPID"]):
            break
        time.sleep(0.1)
    check(
        "real runner and collector started in guard-only mode",
        int(runner["MainPID"]) > 0 and int(collector["MainPID"]) > 0,
        runner_pid=runner["MainPID"],
        collector_pid=collector["MainPID"],
    )
    # OOM is confined to a new 24 MiB child cgroup, then the guardian must stop
    # the actual waiting runner AND collector, without a synthetic write.
    oom = unit("ram", ["MemoryMax=24M", "TasksMax=2"], "x=bytearray(200*1024*1024)")
    check("hard RAM limit kills allocation", oom.returncode != 0, result=oom.returncode)
    for _ in range(50):
        if (
            (RUNTIME / "ABORT").exists()
            and not int(state("runner")["MainPID"])
            and not int(state("collector")["MainPID"])
        ):
            break
        time.sleep(0.1)
    stopped = {"runner": state("runner"), "collector": state("collector")}
    abort = json.loads((RUNTIME / "ABORT").read_bytes()) if (RUNTIME / "ABORT").exists() else []
    check(
        "automatic OOM guard stops real runner and collector",
        "scope_oom" in abort and all(not int(s["MainPID"]) for s in stopped.values()),
        abort=abort,
        states=stopped,
    )
    guard.unlink()
    Path("/var/lib/aa-private-install-20261017/guard-latest.json").write_text(
        json.dumps(checks, indent=2)
    )
    assert checks[-1]["pass"], "leave hardstop closed on failed guard test"
    # Only the observed controlled OOM is acknowledged; no automatic rearming.
    subprocess.run(["systemctl", "stop", "aa-private-watchdog.service"], check=True)
    (RUNTIME / "ABORT").unlink()
    subprocess.run(["systemctl", "start", "aa-private-watchdog.service"], check=True)
    subprocess.run(["systemctl", "start", "aa-private-collector.socket"], check=True)
    cpu = unit(
        "cpu",
        ["CPUQuota=10%", "MemoryMax=32M", "TasksMax=2", "RuntimeMaxSec=3"],
        "while True: pass",
    )
    summary = subprocess.check_output(
        ["systemctl", "show", "aa-private-limit-cpu.service", "-p", "Result", "-p", "CPUUsageNSec"]
    ).decode()
    props = dict(l.split("=", 1) for l in summary.splitlines())
    check(
        "CPU quota and wall timeout bound busy loop",
        cpu.returncode != 0
        and props["Result"] == "timeout"
        and int(props["CPUUsageNSec"]) < 700000000,
        properties=props,
    )
    tasks = unit(
        "tasks",
        ["TasksMax=2", "MemoryMax=32M"],
        "import os,time,errno\np=os.fork()\nif not p:time.sleep(1);os._exit(0)\ntry:q=os.fork()\nexcept OSError as e:os.waitpid(p,0);raise SystemExit(0 if e.errno==errno.EAGAIN else 2)\nos.waitpid(p,0);raise SystemExit(1)",
    )
    check("hard task limit rejects third process", tasks.returncode == 0)
    target = SECURE / "collector/byte-limit-check"
    size = unit(
        "bytes",
        ["MemoryMax=32M", "TasksMax=2", "LimitFSIZE=4096"],
        f"import os,errno\nf=os.open({str(target)!r},os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)\nos.write(f,b'x'*8192)\ntry:os.write(f,b'y')\nexcept OSError as e:raise SystemExit(0 if e.errno==errno.EFBIG else 2)\nraise SystemExit(1)",
    )
    check(
        "hard file byte limit",
        size.returncode == 0 and target.stat().st_size == 4096,
        size=target.stat().st_size,
    )
    target.unlink()
    # Separate tiny crypto epoch: no key backup, encrypted bytes, then wrong-key
    # restore after key destruction. Never touch the running API epoch mapping.
    backing = SECURE.parent / "restore-probe.ciphertext"
    with backing.open("xb") as f:
        f.truncate(16 * 1024 * 1024)
    loop = subprocess.check_output(["losetup", "--find", "--show", str(backing)]).decode().strip()
    mount = SECURE / "collector/restore-check"
    mount.mkdir()
    key = secrets.token_bytes(64)

    def open_map(k):
        subprocess.run(
            [
                "cryptsetup",
                "open",
                "--type",
                "plain",
                "--cipher",
                "aes-xts-plain64",
                "--key-size",
                "512",
                "--key-file",
                "-",
                "--keyfile-size",
                "64",
                loop,
                "aa-private-restore-probe",
            ],
            input=k,
            check=True,
            capture_output=True,
        )

    try:
        open_map(key)
        subprocess.run(
            ["mkfs.ext4", "-q", "-O", "^has_journal", "/dev/mapper/aa-private-restore-probe"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "mount",
                "-o",
                "nodev,nosuid,noexec",
                "/dev/mapper/aa-private-restore-probe",
                str(mount),
            ],
            check=True,
            capture_output=True,
        )
        marker = b"AA-PRIVATE-SYNTHETIC-ENCRYPTION-PROBE-" + secrets.token_bytes(32)
        (mount / "synthetic").write_bytes(marker)
        subprocess.run(["umount", str(mount)], check=True)
        check("no plaintext marker in encrypted backing", marker not in backing.read_bytes())
        subprocess.run(["cryptsetup", "close", "aa-private-restore-probe"], check=True)
        del key
        open_map(secrets.token_bytes(64))
        restore = subprocess.run(
            [
                "mount",
                "-o",
                "ro,nodev,nosuid,noexec",
                "/dev/mapper/aa-private-restore-probe",
                str(mount),
            ],
            capture_output=True,
            check=False,
        )
        check(
            "wrong-key ciphertext restore cannot mount",
            restore.returncode != 0,
            result=restore.returncode,
        )
        if restore.returncode == 0:
            subprocess.run(["umount", str(mount)], check=True)
        subprocess.run(["cryptsetup", "close", "aa-private-restore-probe"], check=True)
    finally:
        subprocess.run(["losetup", "-d", loop], check=True)
        backing.unlink()
        mount.rmdir()
    record = {
        "checks": checks,
        "failed": [c["case"] for c in checks if not c["pass"]],
        "scope": "no action; controlled cgroup OOM/CPU/tasks/byte/time and separate random-key restore epoch",
        "ram_zeroization_or_offline_physical_erasure_proven": False,
    }
    Path("/var/lib/aa-private-install-20261017/limit-checks.json").write_text(
        json.dumps(record, indent=2)
    )
    print(json.dumps(record))
    return int(bool(record["failed"]))


if __name__ == "__main__":
    raise SystemExit(main())
