"""Final own-service/cleanup/resource audit; no dispatch or foreign data reads."""

import hashlib
import json
import secrets
import socket
import subprocess
import time
from pathlib import Path

from research.debian_private.ipc import RUNTIME, SECURE
from research.private_service.http import call
from research.private_service.protocol import request, require

BASE = Path("/var/lib/aa-private-install-20261017")


def main():
    subprocess.run(
        [
            "systemctl",
            "restart",
            "aa-private-api.service",
            "aa-private-signer.service",
            "aa-private-verifier.service",
        ],
        check=True,
    )
    for attempt in range(50):
        try:
            with socket.create_connection(("127.0.0.1", 8765), timeout=0.2):
                break
        except OSError:
            require(attempt < 49, 503, "PRIVATE_API_START_TIMEOUT")
            time.sleep(0.1)
    c = json.loads((SECURE / "registrar/bootstrap/config.json").read_bytes())
    token = next(
        t["token"] for t in c["tokens"] if t["tenant"] == "test-a" and t["role"] == "client"
    )
    cases = []
    for name in [
        "single-job.json",
        "completion-job.json",
        "qualified-job.json",
        "complete-service-job.json",
    ]:
        j = json.loads((BASE / name).read_bytes())["job_id"]
        status, _ = call("http://127.0.0.1:8765", token, "GET", f"/v1/jobs/{j}/report")
        require(status == 410, 503, "REPORT_NOT_BLOCKED")
        cases.append({"job": j, "get_after_final_restart": status})
    signed = request(
        c["keys"]["sender"]["private"],
        "test-a",
        "sender",
        "/v1/jobs",
        {"scenario": "a4-write16-v1", "receiver_kid": "receiver"},
        secrets.token_hex(16),
        secrets.token_hex(32),
    )
    status, error = call("http://127.0.0.1:8765", token, "POST", "/v1/jobs", signed)
    require(status == 403 and error["code"] == "KEY_REVOKED", 503, "ADMISSION_NOT_CLOSED")
    guard = Path("/sys/fs/cgroup/system.slice/aa-private-watchdog.service")
    work = Path("/sys/fs/cgroup/aa.slice/aa-private.slice")
    quotas = [list(map(int, (p / "cpu.max").read_text().split())) for p in [work, guard]]
    mem = [int((p / "memory.max").read_text()) for p in [work, guard]]
    assert all(q[1] == 100000 for q in quotas) and sum(q[0] for q in quotas) <= 40000
    assert sum(mem) <= 838767616
    properties = {}
    for name in ["api", "signer", "verifier", "collector", "runner", "watchdog"]:
        text = subprocess.check_output(
            [
                "systemctl",
                "show",
                "aa-private-" + name + ".service",
                "-p",
                "MainPID",
                "-p",
                "ActiveState",
                "-p",
                "MemoryCurrent",
                "-p",
                "MemoryMax",
                "-p",
                "MemorySwapMax",
                "-p",
                "TasksMax",
            ]
        ).decode()
        properties[name] = dict(l.split("=", 1) for l in text.splitlines())
    assert properties["collector"]["MainPID"] == "0" and properties["runner"]["MainPID"] == "0"
    assert not (RUNTIME / "collector.sock").exists() and (SECURE / "collector/HARDSTOP").is_file()
    assert json.loads(Path("/etc/aa-private/collector.json").read_bytes())["retired"] is True
    assert not list((SECURE / "api/jobs").rglob("content.key"))
    assert not list((SECURE / "verifier").iterdir()) and not list((SECURE / "verdicts").iterdir())
    assert not (SECURE / "qualification").exists() and not (SECURE / "runner/pending.json").exists()
    assert Path("/sys/kernel/tracing/kprobe_events").read_text().strip() == ""
    before = json.loads((BASE / "before.json").read_bytes())
    central = subprocess.check_output(
        [
            "systemctl",
            "show",
            "ki-hilfezentrum.service",
            "-p",
            "MainPID",
            "-p",
            "ActiveState",
            "-p",
            "MemoryCurrent",
            "-p",
            "MemoryMax",
            "-p",
            "CPUQuotaPerSecUSec",
            "-p",
            "TasksMax",
        ]
    ).decode()
    assert "MainPID=1011380" in central and "ActiveState=active" in central
    rootcheck = subprocess.run(
        [
            "/usr/bin/python3",
            "-B",
            "-c",
            "from research.private_service.limits import unprivileged;from research.private_service.protocol import Problem\ntry:unprivileged()\nexcept Problem as e:raise SystemExit(0 if e.code=='PRIVILEGED_API_FORBIDDEN' else 2)\nraise SystemExit(1)",
        ],
        cwd="/opt/aa-private",
        capture_output=True,
        check=False,
        timeout=5,
    )
    assert rootcheck.returncode == 0
    stat = {
        k: int(v)
        for k, v in (l.split() for l in Path("/proc/vmstat").read_text().splitlines())
        if k in ["pswpin", "pswpout"]
    }
    assert stat == {"pswpin": 0, "pswpout": 0}
    state = {
        "cases": cases,
        "fresh_job_to_revoked_receiver": {"status": status, "code": error["code"]},
        "native_root_api_refusal": True,
        "services": properties,
        "aggregate_with_guard": {
            "cpu_max": quotas,
            "memory_max_bytes": mem,
            "memory_total_bytes": sum(mem),
            "host_cpu_percent": sum(q[0] for q in quotas) / 8000,
        },
        "swap_counters": stat,
        "central": central,
        "central_unit_unchanged": hashlib.sha256(
            Path("/etc/systemd/system/ki-hilfezentrum.service").read_bytes()
        ).hexdigest()
        == before["central_unit_sha256"],
        "listeners": subprocess.check_output(["ss", "-ltn"]).decode(),
        "collector_test_epoch_retired": True,
        "own_capture_probe_definitions_remaining": 0,
        "job_content_keys_remaining": 0,
        "qualification_temp_tree_absent": True,
        "private_api_config_stat": {
            "mode": oct(Path("/etc/aa-private/api.json").stat().st_mode & 0o777),
            "uid": Path("/etc/aa-private/api.json").stat().st_uid,
            "gid": Path("/etc/aa-private/api.json").stat().st_gid,
        },
        "clock_floor_retained": True,
        "aborted": (RUNTIME / "ABORT").exists(),
        "monotonic_ns": time.monotonic_ns(),
    }
    assert state["central_unit_unchanged"] and not state["aborted"]
    (BASE / "final-state.json").write_text(json.dumps(state, indent=2))
    print(json.dumps(state))


if __name__ == "__main__":
    main()
