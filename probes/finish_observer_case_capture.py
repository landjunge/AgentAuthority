"""Test-only passive tracing of the unchanged finish/late-effect probe.

No trace record is an observer event. All checkpoints are a private oracle.
Load explicitly with pytest -p probes.finish_observer_case_capture.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import threading

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE = str(ROOT / "probes/test_finish_adapter_effect_atomicity_probe.py")
VALIDATOR = str(ROOT / "lab/validator.py")
NODE = "test_no_adapter_effect_occurs_after_finish_returns"
records: list[dict] = []
reports: list[dict] = []
record_lock = threading.Lock()
output: Path


def save(path: Path, value: object) -> None:
    with path.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    path.chmod(0o444)


def export_snapshot() -> dict:
    path = output / "original/authority-events.jsonl"
    data = path.read_bytes() if path.exists() else b""
    return {"bytes": len(data), "lines": len(data.splitlines()),
            "sha256": hashlib.sha256(data).hexdigest()}


def append(record: dict) -> None:
    with record_lock:
        records.append(record)


def trace(frame, event, arg):
    filename, name = frame.f_code.co_filename, frame.f_code.co_name
    if filename == VALIDATOR and name == "finish":
        if event == "return":
            append({"checkpoint": "actual_finish_return", "returned_value": arg,
                    "workflow_id": frame.f_locals["workflow_id"]})
        return trace
    if filename != PROBE:
        return None
    local = frame.f_locals
    if name == "submit_then_pause":
        if event == "call":
            req = local["req"]
            append({"checkpoint": "actual_submitted_request", "actor": req.actor,
                    "action": req.action, "resource": req.resource,
                    "workflow_id": req.workflow_id})
        elif event == "line" and frame.f_lineno == 31:
            append({"checkpoint": "allow_assertion_passed_before_pause",
                    "allow": local["decision"].allow})
        elif event == "line" and frame.f_lineno == 33:
            append({"checkpoint": "release_wait_succeeded_before_adapter_resumes"})
    elif name == NODE and event == "line":
        if frame.f_lineno in (47, 48, 50, 58):
            adapter, workflow = local["adapter"], local["workflow_id"]
            entry = adapter.lab._entries.get(workflow)
            label = {47: "authorized_wait_succeeded_before_finish_call",
                     48: "caller_passed_finish_true_assertion",
                     50: "absence_assertion_passed_before_release",
                     58: "worker_join_and_result_assertions_passed"}[frame.f_lineno]
            append({"checkpoint": label, "probe_line": frame.f_lineno,
                    "target_present": local["path"] in adapter.repo.files,
                    "authorized_set": local["authorized"].is_set(),
                    "release_set": local["release_effect"].is_set(),
                    "worker_alive": local["worker"].is_alive(),
                    "worker_errors": [type(e).__name__ for e in local["errors"]],
                    "returned_decisions": [d.allow for d in local["result"]],
                    "live_workflow_registered": entry is not None,
                    "live_provenance_count": len(entry.state.provenance) if entry else None,
                    "original_export_snapshot": export_snapshot()})
    if event == "exception":
        append({"checkpoint": "original_probe_exception", "function": name,
                "probe_line": frame.f_lineno, "exception_type": arg[0].__name__})
    return trace


def pytest_configure(config):
    global output
    output = Path(os.environ["AA_FINISH_CASE_OUT"]).resolve()
    if Path(os.environ["LAB_AUTHORITY_EVENTS_PATH"]).resolve() != output / "original/authority-events.jsonl":
        raise RuntimeError("export_path_does_not_match_frozen_contract")
    output.mkdir(parents=True, exist_ok=False)
    (output / "original").mkdir()
    (output / "ground-truth").mkdir()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    if str(item.path) != PROBE or item.name != NODE:
        raise RuntimeError("only_the_frozen_original_probe_is_authorized")
    old_main, old_thread = sys.gettrace(), threading.gettrace()
    sys.settrace(trace)
    threading.settrace(trace)
    try:
        yield
    finally:
        sys.settrace(old_main)
        threading.settrace(old_thread)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    reports.append({"when": report.when, "outcome": report.outcome,
                    "exception_type": call.excinfo.type.__name__ if call.excinfo else None})


def pytest_sessionfinish(session, exitstatus):
    save(output / "ground-truth/checkpoints.json",
         {"checkpoints": records, "pytest_reports": reports, "pytest_exit_code": int(exitstatus),
          "instrumentation": "passive_trace_only; no_mutation_or_synthetic_observer_events"})
    path = output / "original/authority-events.jsonl"
    if path.exists():
        path.chmod(0o444)
