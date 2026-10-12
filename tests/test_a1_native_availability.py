"""Availability/unknown gates; mocks are not macOS Writer evidence."""

from __future__ import annotations

import copy
import json
import subprocess

import pytest

from scripts import a1_native_availability as a1


@pytest.fixture
def native():
    return {
        "schema": "a1-native-availability-v1",
        "euid": 501,
        "bsd": {
            "expected": 136,
            "returned": 136,
            "after_returned": 136,
            "stable": True,
            "pid": 123,
            "start_seconds": 100,
            "start_microseconds": 10,
        },
        "fd": {"expected": 1200, "returned": 1200, "same_file": True, "read_only": True},
        "mach": {"return": 0, "count": 8, "expected_count": 8, "pid": 123, "pid_version": 456},
        "auditpipe": {"opened": False, "records_read": 0},
        "es": {"result": 5, "connected": False, "subscriptions": 0, "callbacks": 0},
    }


def test_snapshots_do_not_become_writer_or_agent_and_unexecuted_is_not_zero_errors(native):
    result = a1.interpret(native)
    assert result["process_snapshot"] == result["read_only_fd_file_identity"] == "BELEGT"
    assert result["self_task_audit_snapshot"] == "BELEGT"
    assert result["writer_identity"] == result["logical_agent_identity"] == "UNBEKANNT"
    assert result["selected_writer_channel"] is None
    assert result["correct_attributions"] is result["unclear_attributions"] is None
    assert result["writer_event_count"] is result["writer_raw_event_bytes"] is None
    assert result["attribution_denominator"] == 0
    assert len(result["scenarios"]) == 6 and all(not r["executed"] for r in result["scenarios"])
    assert not result["source_authenticated_for_agent"] and not result["rights_inherited"]


@pytest.mark.parametrize(
    "block,key,value,field",
    [
        ("bsd", "after_returned", 0, "process_snapshot"),
        ("bsd", "stable", False, "process_snapshot"),
        ("bsd", "start_microseconds", 1_000_000, "process_snapshot"),
        ("fd", "returned", 0, "read_only_fd_file_identity"),
        ("fd", "same_file", False, "read_only_fd_file_identity"),
        ("mach", "pid", 999, "self_task_audit_snapshot"),
        ("mach", "count", 7, "self_task_audit_snapshot"),
    ],
)
def test_missing_or_conflicting_snapshot_is_unknown(native, block, key, value, field):
    native[block][key] = value
    result = a1.interpret(native)
    assert result[field] == result["writer_identity"] == "UNBEKANNT"


@pytest.mark.parametrize("key,value", [("result", 0), ("connected", True), ("callbacks", 1)])
def test_unexpected_es_connection_stops_before_any_writer_case(native, key, value):
    native["es"][key] = value
    result = a1.interpret(native)
    assert result == {"status": "STOP", "reason": "unexpected_ES_connection_or_callback"}


def test_readable_audit_handle_does_not_establish_record_origin_or_instance_binding(native):
    native["auditpipe"]["opened"] = True
    assert a1.interpret(native)["selected_writer_channel"] is None
    native["auditpipe"]["records_read"] = 1
    assert a1.interpret(native)["status"] == "STOP"


@pytest.mark.parametrize("change", [{"euid": 0}, {"schema": "archive"}, {"es": {}}])
def test_untrusted_schema_missing_access_result_or_root_cannot_pass(native, change):
    data = copy.deepcopy(native)
    data.update(change)
    with pytest.raises(ValueError):
        a1.interpret(data)


def test_root_and_nonmac_refuse_before_directory_creation(tmp_path, monkeypatch):
    parent = tmp_path / "unused"
    monkeypatch.setattr(a1.os, "geteuid", lambda: 0)
    with pytest.raises(ValueError, match="root"):
        a1.run(parent)
    monkeypatch.setattr(a1.os, "geteuid", lambda: 501)
    monkeypatch.setattr(a1.sys, "platform", "linux")
    with pytest.raises(ValueError, match="macOS"):
        a1.run(parent)
    assert not parent.exists()


def test_repository_existing_and_nontemporary_paths_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(a1.os, "geteuid", lambda: 501)
    monkeypatch.setattr(a1.sys, "platform", "darwin")
    for parent in (a1.ROOT / "docs" / "bad", tmp_path, a1.ROOT.parent / "foreign-fresh"):
        with pytest.raises(ValueError):
            a1._guard(parent)
    assert a1._guard(tmp_path / "fresh") == (tmp_path / "fresh").resolve()


@pytest.mark.parametrize("missing", [False, True])
def test_command_timeout_or_missing_tool_keeps_unknown_metrics_and_no_raw_text(
    monkeypatch, missing
):
    def fail(*args, **kwargs):
        if missing:
            raise FileNotFoundError(2, "not archived raw diagnostic")
        raise subprocess.TimeoutExpired(["tool"], 1, output=b"private-diagnostic-sentinel")

    monkeypatch.setattr(a1.subprocess, "run", fail)
    result, meta = a1._command(["tool"], 1)
    assert result.returncode == (127 if missing else 124)
    assert meta["cpu_seconds"] is meta["peak_rss_bytes"] is None
    assert "private-diagnostic-sentinel" not in json.dumps(meta)
    assert not meta["raw_output_saved"]
