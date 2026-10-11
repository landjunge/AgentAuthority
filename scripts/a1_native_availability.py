"""Bounded macOS availability diagnostics, never a Writer attribution oracle."""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = (
    "A_writes_target",
    "B_idle",
    "C_writes_other_file",
    "child_writes_target",
    "forged_PID",
    "two_sequential_writers_same_file",
)
HEADERS = (
    "usr/include/libproc.h",
    "usr/include/sys/proc_info.h",
    "usr/include/sys/event.h",
    "usr/include/bsm/audit.h",
    "usr/include/bsm/libbsm.h",
    "usr/include/mach/task_info.h",
    "usr/include/mach/message.h",
    "usr/include/EndpointSecurity/ESClient.h",
    "usr/include/EndpointSecurity/ESTypes.h",
    "usr/include/EndpointSecurity/ESMessage.h",
    "System/Library/Frameworks/CoreServices.framework/Frameworks/FSEvents.framework/Headers/FSEvents.h",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _guard(parent: Path) -> Path:
    parent = parent.resolve()
    if os.geteuid() == 0:
        raise ValueError("root probe forbidden")
    if sys.platform != "darwin":
        raise ValueError("native macOS only")
    if parent == ROOT or ROOT in parent.parents or parent.exists():
        raise ValueError("fresh external output directory required")
    temporary_roots = {Path("/tmp").resolve(), Path(tempfile.gettempdir()).resolve()}
    if not any(root in parent.parents for root in temporary_roots):
        raise ValueError("temporary output only")
    return parent


def interpret(native: dict) -> dict:
    """Diagnostic snapshots or readable handles never establish causation."""
    if native.get("schema") != "a1-native-availability-v1":
        raise ValueError("unexpected native schema")
    if type(native.get("euid")) is not int or native["euid"] == 0:
        raise ValueError("unexpected native privilege")
    es = native.get("es", {})
    if type(es.get("result")) is not int or type(es.get("connected")) is not bool:
        raise ValueError("missing ES access result")
    if es["result"] == 0 or es["connected"] or es.get("callbacks") != 0:
        return {"status": "STOP", "reason": "unexpected_ES_connection_or_callback"}
    if es.get("subscriptions") != 0 or native.get("auditpipe", {}).get("records_read") != 0:
        return {"status": "STOP", "reason": "event_observation_outside_availability_spec"}
    bsd = native.get("bsd", {})
    fd = native.get("fd", {})
    mach = native.get("mach", {})
    bsd_ok = (
        type(bsd.get("expected")) is int
        and bsd["expected"] > 0
        and bsd.get("returned") == bsd["expected"] == bsd.get("after_returned")
        and bsd.get("stable") is True
        and type(bsd.get("pid")) is int
        and bsd["pid"] > 0
        and type(bsd.get("start_seconds")) is int
        and bsd["start_seconds"] > 0
        and type(bsd.get("start_microseconds")) is int
        and 0 <= bsd["start_microseconds"] < 1_000_000
    )
    fd_ok = (
        type(fd.get("expected")) is int
        and fd["expected"] > 0
        and fd.get("returned") == fd["expected"]
        and fd.get("same_file") is True
        and fd.get("read_only") is True
    )
    mach_ok = (
        mach.get("return") == 0
        and mach.get("count") == mach.get("expected_count") == 8
        and type(mach.get("pid")) is int
        and bsd_ok
        and mach["pid"] == bsd["pid"]
        and type(mach.get("pid_version")) is int
        and mach["pid_version"] >= 0
    )
    return {
        "status": "COMPLETED",
        "process_snapshot": "BELEGT" if bsd_ok else "UNBEKANNT",
        "read_only_fd_file_identity": "BELEGT" if fd_ok else "UNBEKANNT",
        "self_task_audit_snapshot": "BELEGT" if mach_ok else "UNBEKANNT",
        "selected_writer_channel": None,
        "writer_identity": "UNBEKANNT",
        "logical_agent_identity": "UNBEKANNT",
        "durable_file_state": "UNBEKANNT",
        "reason": "no_accessible_kernel_action_to_file_actor_record",
        "auditpipe_opened": native.get("auditpipe", {}).get("opened"),
        "auditpipe_readable_is_not_yet_qualified": True,
        "source_authenticated_for_agent": False,
        "rights_inherited": False,
        "scenarios": [
            {"case": case, "executed": False, "attribution": "UNBEKANNT"} for case in SCENARIOS
        ],
        "correct_attributions": None,
        "unclear_attributions": None,
        "attribution_denominator": 0,
        "writer_event_count": None,
        "writer_raw_event_bytes": None,
    }


def _command(argv: list[str], timeout: int) -> tuple[subprocess.CompletedProcess, dict]:
    start = time.monotonic_ns()
    try:
        result = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(argv, 124, exc.stdout or b"", exc.stderr or b"")
    except OSError as exc:
        result = subprocess.CompletedProcess(argv, 127, b"", b"")
        failure = {"error_kind": type(exc).__name__, "errno": exc.errno}
    else:
        failure = {}
    if result.returncode == 124:
        failure = {"error_kind": "TimeoutExpired", "errno": None}
    data = {
        "argv": argv,
        "returncode": result.returncode,
        "stdout_bytes": len(result.stdout),
        "stderr_bytes": len(result.stderr),
        "stdout_sha256": hashlib.sha256(result.stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(result.stderr).hexdigest(),
        "elapsed_ns": time.monotonic_ns() - start,
        "cpu_seconds": None,
        "peak_rss_bytes": None,
        "raw_output_saved": False,
        "failure": failure,
    }
    return result, data


def run(parent: Path) -> dict:
    parent = _guard(parent)
    sdk = Path(subprocess.check_output(["xcrun", "--show-sdk-path"], text=True).strip())
    parent.mkdir(mode=0o700)
    artifact = parent / "availability.json"
    report = {
        "utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "host": platform.platform(),
        "python": platform.python_version(),
        "euid": os.geteuid(),
        "source_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "source_sha256": {
            "scripts/a1_native_probe.c": digest(ROOT / "scripts/a1_native_probe.c"),
            "scripts/a1_native_availability.py": digest(Path(__file__)),
        },
        "sdk": str(sdk),
        "headers_sha256": {name: digest(sdk / name) for name in HEADERS},
        "commands": [],
        "writer_hypothesis": "UNBEKANNT",
        "old_A1_result_changed": False,
    }

    def save() -> None:
        artifact.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    binary = parent / "native-probe"
    command = [
        "xcrun",
        "clang",
        "-std=c11",
        "-fblocks",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-Wno-deprecated-declarations",
        str(ROOT / "scripts/a1_native_probe.c"),
        "-lproc",
        "-lbsm",
        "-lEndpointSecurity",
        "-o",
        str(binary),
    ]
    compiled, meta = _command(command, 30)
    report["commands"].append(meta)
    if compiled.returncode != 0:
        report["status"] = "STOP"
        report["reason"] = "compile_failed"
        save()
        return report
    report["binary_sha256"] = digest(binary)
    target = parent / "empty-artificial-file"
    target.touch(exist_ok=False)
    captured, meta = _command([str(binary), str(target)], 10)
    report["commands"].append(meta)
    try:
        native = json.loads(captured.stdout)
        verdict = interpret(native)
    except (ValueError, TypeError, AttributeError):
        report["status"] = "STOP"
        report["reason"] = "native_output_unavailable"
        save()
        return report
    report["native"] = native
    report["verdict"] = verdict
    report["status"] = verdict["status"]
    if captured.returncode != 0 or verdict["status"] == "STOP":
        report["status"] = "STOP"
        report["reason"] = verdict.get("reason", "native_failure")
        save()
        return report
    for command in (
        ["/usr/bin/fs_usage", "-t", "1", str(os.getpid())],
        ["/usr/sbin/dtrace", "-l", "-n", "syscall::write:entry"],
    ):
        captured, meta = _command(command, 3)
        # Preserve bytes/hashes, but no unrestricted diagnostic/provider text.
        lowered = (captured.stdout + captured.stderr).lower()
        meta["root_or_privilege_rejection"] = b"root" in lowered or b"privilege" in lowered
        meta["executable_sha256"] = digest(Path(command[0])) if Path(command[0]).is_file() else None
        meta["writer_events_measured"] = False
        report["commands"].append(meta)
    report["raw_struct_bytes_scope"] = (
        "successful explicit output structures; not total IPC/kernel traffic; no raw memory saved"
    )
    report["native_metrics_scope"] = (
        "self-reported getrusage of this fresh native probe, CPU during calls; "
        "macOS ru_maxrss peak bytes, excludes compiler/tool/wrapper costs"
    )
    report["event_stream_resources"] = "UNBEKANNT; no Writer stream qualified or consumed"
    report["diagnostic_stdout_stderr_bytes"] = sum(
        c["stdout_bytes"] + c["stderr_bytes"] for c in report["commands"]
    )
    save()
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("parent", type=Path)
    args = parser.parse_args()
    result = run(args.parent)
    print(json.dumps({"status": result["status"], "path": str(args.parent / "availability.json")}))


if __name__ == "__main__":
    main()
