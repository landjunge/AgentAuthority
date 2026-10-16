"""Host health guard; fixed production endpoint and only our cgroup may be stopped."""

import http.client
import json
import os
import socket
import subprocess
import time
from pathlib import Path

CG = Path("/sys/fs/cgroup/aa.slice/aa-private.slice")
ROOT = Path("/run/aa-private")
OUT = Path("/var/lib/aa-private-install-20261017/health.jsonl")


def cpu():
    return list(map(int, Path("/proc/stat").read_text().splitlines()[0].split()[1:9]))


def sample(previous, elapsed):
    current = cpu()
    d = [a - b for a, b in zip(current, previous)]
    mem = {
        s[0].rstrip(":"): int(s[1]) * 1024
        for l in Path("/proc/meminfo").read_text().splitlines()
        if len(s := l.split()) == 3
    }
    start = time.monotonic()
    try:
        with socket.create_connection(("172.18.0.1", 8787), timeout=1):
            pass
        c = http.client.HTTPConnection("172.18.0.1", 8787, timeout=1)
        c.request("GET", "/health")
        response = c.getresponse()
        status = response.status
        # Do not read or log application bodies, headers or credentials.
        c.close()
    except OSError:
        status = 0
    active = (
        subprocess.run(
            ["systemctl", "is-active", "--quiet", "ki-hilfezentrum.service"], timeout=2, check=False
        ).returncode
        == 0
    )
    scope = {}
    for name in (
        "memory.current",
        "memory.swap.current",
        "pids.current",
        "memory.events",
        "cpu.stat",
    ):
        p = CG / name
        scope[name] = p.read_text().strip() if p.exists() else None
    fs = os.statvfs("/var/lib")
    io = float(Path("/proc/pressure/io").read_text().split("full avg10=")[1].split()[0])
    return current, {
        "monotonic": time.monotonic(),
        "interval": elapsed,
        "cpu_busy": 100 * (1 - (d[3] + d[4]) / sum(d)),
        "mem_available": mem["MemAvailable"],
        "mem_total": mem["MemTotal"],
        "scope": scope,
        "disk_available": fs.f_bavail * fs.f_frsize,
        "disk_total": fs.f_blocks * fs.f_frsize,
        "io_full_avg10": io,
        "central_active": active,
        "central_http_status": status,
        "central_probe_ms": 1000 * (time.monotonic() - start),
    }


def reasons(s, counts, initial_oom=0):
    flags = {
        "host_cpu": s["cpu_busy"] > 10.5,
        "io_pressure": s["io_full_avg10"] > 5,
        "latency": s["central_probe_ms"] > 250,
        "scope_memory": int(s["scope"].get("memory.current") or 0) > 720000000,
    }
    for k, v in flags.items():
        counts[k] = counts.get(k, 0) + 1 if v else 0
    result = [k for k, n in counts.items() if n >= (3 if k in ("host_cpu", "io_pressure") else 2)]
    if not s["central_active"] or s["central_http_status"] != 403:
        result.append("central_health_changed")
    if s["mem_available"] < max(s["mem_total"] * 0.25, 1073741824):
        result.append("host_memory_reserve")
    if s["disk_available"] < max(s["disk_total"] * 0.2, 4294967296):
        result.append("disk_reserve")
    if int(s["scope"].get("memory.swap.current") or 0) > 0:
        result.append("scope_swap")
    if int(s["scope"].get("pids.current") or 0) > 43:
        result.append("scope_tasks")
    events = dict(l.split() for l in (s["scope"].get("memory.events") or "").splitlines())
    if int(events.get("oom", 0)) + int(events.get("oom_kill", 0)) > initial_oom:
        result.append("scope_oom")
    if s["interval"] > 2.5:
        result.append("stale_monitor")
    return result


def stop(why):
    (ROOT / "ABORT").write_text(json.dumps(why))
    # Close activation first: otherwise a queued Unix connection can reactivate
    # the collector just after it was stopped, while its caller is still dying.
    subprocess.run(["systemctl", "stop", "aa-private-collector.socket"], timeout=3, check=True)
    subprocess.run(
        ["systemctl", "stop", "aa-private-runner.service", "aa-private-collector.service"],
        timeout=10,
        check=True,
    )


def main():
    os.umask(0o077)
    previous = cpu()
    stamp = time.monotonic()
    counts = {}
    initial = dict(l.split() for l in (CG / "memory.events").read_text().splitlines())
    initial_oom = int(initial.get("oom", 0)) + int(initial.get("oom_kill", 0))
    while True:
        time.sleep(1)
        now = time.monotonic()
        try:
            previous, s = sample(previous, now - stamp)
            why = reasons(s, counts, initial_oom)
            s["abort_reasons"] = why
            with OUT.open("a") as f:
                f.write(json.dumps(s) + "\n")
            if OUT.stat().st_size > 16 * 1024 * 1024:
                why.append("monitor_log_bound")
            heartbeat = ROOT / "heartbeat.next"
            heartbeat.write_text(str(time.monotonic_ns()))
            heartbeat.chmod(0o644)
            heartbeat.replace(ROOT / "heartbeat")
            if why:
                stop(why)
                return 2
        except Exception:  # noqa: BLE001 - any monitor failure closes admission and own scopes
            stop(["monitor_failed"])
            return 3
        stamp = now


if __name__ == "__main__":
    raise SystemExit(main())
