"""Actual channel qualification in explicitly isolated guest; no Writer action."""

import ctypes
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path


def main():
    if platform.system() != "Linux" or os.geteuid() != 0:
        raise RuntimeError("authorized guest root required")
    result = {
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "uid": os.geteuid(),
        "distribution": Path("/etc/os-release").read_text(),
        "capabilities": [
            x
            for x in Path("/proc/self/status").read_text().splitlines()
            if x.startswith(("Cap", "Seccomp", "NoNewPrivs"))
        ],
        "boot_hash": hashlib.sha256(
            Path("/proc/sys/kernel/random/boot_id").read_bytes()
        ).hexdigest(),
    }
    trace = Path("/sys/kernel/tracing")
    result["tracepoints"] = {}
    for event in [
        "syscalls/sys_enter_write",
        "syscalls/sys_exit_write",
        "sched/sched_process_exit",
    ]:
        path = trace / "events" / event / "format"
        try:
            data = path.read_bytes()
            result["tracepoints"][event] = {
                "status": "BELEGT",
                "sha256": hashlib.sha256(data).hexdigest(),
                "fields": [x.strip() for x in data.decode().splitlines() if "field:" in x],
            }
        except OSError as error:
            result["tracepoints"][event] = {"status": "UNBEKANNT", "errno": error.errno}
    command = ["auditctl", "-s"]
    r = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    result["audit"] = {
        "command": command,
        "exit": r.returncode,
        "status_fields": r.stdout.splitlines(),
        "stderr_bytes": len(r.stderr.encode()),
    }
    libc = ctypes.CDLL(None, use_errno=True)
    libc.fanotify_init.argtypes = [ctypes.c_uint, ctypes.c_uint]
    libc.fanotify_init.restype = ctypes.c_int
    fd = libc.fanotify_init(0x1 | 0x2 | 0x80, os.O_RDONLY | os.O_CLOEXEC)
    result["fanotify"] = {
        "init_result": fd,
        "errno": ctypes.get_errno() if fd < 0 else None,
        "flags": "NOTIFY/CLOEXEC/NONBLOCK/REPORT_PIDFD",
        "records_read": 0,
    }
    if fd >= 0:
        os.close(fd)
    for name in ["unprivileged_bpf_disabled", "perf_event_paranoid"]:
        result[name] = Path("/proc/sys/kernel/" + name).read_text().strip()
    result["logical_agent_identity"] = "UNBEKANNT"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
