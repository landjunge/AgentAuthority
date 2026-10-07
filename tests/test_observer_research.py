"""Measurement correctness tests; synthetic inputs are not real-agent evidence."""
from collections import Counter
import json
from pathlib import Path

import pytest

import observer_research as p


def event(kind, value, timestamp=10, run=1, number=1):
    return {"run": run, "kind": kind, "value": value, "t_ns": timestamp, "event": number}


@pytest.mark.parametrize("code,expected", [(0, True), (7, False), (-1, False)])
def test_cli_projection_excludes_all_raw_metadata(code, expected):
    recorder, counts = p.Recorder(), Counter()
    raw = {"type": "item.completed", "source": p.CANARY, "item": {
        "type": "command_execution", "id": p.CANARY, "exit_code": code,
        "command": p.CANARY, "aggregated_output": p.CANARY,
        "actor": p.CANARY, "resource": "https://invalid.example/?api_key=" + p.CANARY,
        "reason": p.CANARY, "parameters": {"key": p.CANARY}, "label": "PUBLIC"}}
    p.project_cli(raw, 1, recorder, counts)
    assert recorder.events[0]["value"] is expected
    assert set(recorder.events[0]) == set(p.FIELDS)
    assert p.CANARY not in json.dumps(recorder.events)


@pytest.mark.parametrize("code", [None, True, "secret", {}, []])
def test_bad_exit_metadata_is_not_copied_or_inferred(code):
    recorder, counts = p.Recorder(), Counter()
    p.project_cli({"type": "item.completed", "item": {
        "type": "command_execution", "exit_code": code}}, 1, recorder, counts)
    assert not recorder.events
    assert counts["invalid_tool_reports"] == 1


@pytest.mark.parametrize("raw", [[], None, {"type": p.CANARY},
                                 {"type": "item.completed", "item": p.CANARY}])
def test_unrecognised_payload_is_not_persisted(raw):
    recorder, counts = p.Recorder(), Counter()
    p.project_cli(raw, 1, recorder, counts)
    assert not recorder.events
    assert p.CANARY not in json.dumps(counts)


def test_missing_target_is_not_negative_evidence():
    rows = [event("tool_end", True), event("cli_end", True, number=2)]
    assert p.infer(rows, 1, "target_present")["answer"] is None
    assert p.status_baseline(rows, 1, "target_present")["answer"] is True
    assert p.judge(True, False) == "WRONG"
    assert p.judge(None, False) == "UNKNOWN"


@pytest.mark.parametrize("present", [True, False])
def test_explicit_snapshot_can_state_its_bounded_presence(present):
    rows = [event("target_final", present)]
    assert p.infer(rows, 1, "target_present")["answer"] is present


def test_removing_run_does_not_restore_binding_from_order_or_event_number():
    rows = [event("target_final", True), event("target_final", False, run=2, number=2)]
    view = [{k: v for k, v in e.items() if k != "run"} for e in rows]
    assert p.infer(view, 1, "target_present")["answer"] is None
    assert p.infer(view, 2, "target_present")["answer"] is None


def test_order_uses_measured_bounds_not_delivery_order():
    rows = [event("cli_end", True, 20, number=3),
            event("target_probe", True, 10, number=2),
            event("target_probe", False, 1, number=1)]
    assert p.infer(rows, 1, "appearance_vs_cli_end")["answer"] == "before"
    view = [{k: v for k, v in e.items() if k != "t_ns"} for e in rows]
    assert p.infer(view, 1, "appearance_vs_cli_end")["answer"] is None


def test_late_reception_alone_does_not_prove_late_creation():
    rows = [event("target_probe", False, 1), event("cli_end", True, 10, number=2),
            event("target_probe", True, 20, number=3)]
    assert p.infer(rows, 1, "appearance_vs_cli_end")["answer"] is None
    rows.append(event("target_probe", False, 15, number=4))
    assert p.infer(rows, 1, "appearance_vs_cli_end")["answer"] == "after"


def test_missing_end_is_not_invented_from_target_sample():
    assert p.infer([event("target_probe", True)], 1,
                   "appearance_vs_cli_end")["answer"] is None


def test_identical_duplicate_is_not_second_observation_but_changed_copy_conflicts():
    row = event("target_final", True)
    rows, conflict = p.deduplicate([row, dict(row)])
    assert rows == [row] and not conflict
    changed = {**row, "value": False}
    assert p.infer([row, changed], 1, "target_present")["reason"] == "contradictory_reference"


def write_receipt(path, entries):
    path.write_text("".join(json.dumps(e) + "\n" for e in entries))


@pytest.mark.parametrize("cutoff,end,presence,order", [
    ((30, 31), 25, True, "before"),
    ((5, 6), 5, False, "after"),
    ((15, 25), 15, None, None),
])
def test_reference_uses_real_creation_interval_not_mode_name(tmp_path, cutoff, end, presence, order):
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}, {"create_before_ns": 10, "create_after_ns": 20}])
    tmp_path.joinpath("target").touch()
    result = p.reference_at_cutoff(tmp_path, receipt, cutoff, end)
    assert result["target_present"] is presence
    assert result["appearance_vs_cli_end"] == order


def test_later_target_state_does_not_prove_earlier_snapshot(tmp_path):
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}, {"create_before_ns": 50, "create_after_ns": 60}])
    tmp_path.joinpath("target").touch()
    result = p.reference_at_cutoff(tmp_path, receipt, (10, 11), 20)
    assert result["target_check"] is True
    assert result["target_present"] is False


def test_missing_tool_receipt_is_unjudgeable_even_if_snapshot_exists(tmp_path):
    tmp_path.joinpath("target").touch()
    result = p.reference_at_cutoff(tmp_path, tmp_path / "missing", (10, 11), 5)
    assert result["target_present"] is None
    assert result["reference_issue"] is not None


def test_receipt_target_disagreement_does_not_become_false_or_success(tmp_path):
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}, {"create_before_ns": 10, "create_after_ns": 20}])
    result = p.reference_at_cutoff(tmp_path, receipt, (30, 31), 25)
    assert result["target_present"] is None
    assert result["reference_issue"] == "receipt_target_disagreement"


def test_snapshot_failures_are_counted_not_silently_absent(tmp_path, monkeypatch):
    recorder = p.Recorder()
    sensor = p.TargetSensor(tmp_path / "target", 1, recorder)
    def denied(*args, **kwargs):
        raise PermissionError("synthetic")
    monkeypatch.setattr(Path, "stat", denied)
    sensor.sample(final=True)
    assert sensor.errors == 1
    assert not recorder.events


def test_all_field_subsets_are_tested_without_truth_input():
    rows = [event("target_final", True)]
    predictions = p.all_predictions(rows)
    assert len(predictions) == 6 * (32 * 2 + 6)
    assert len({tuple(row["fields"]) for row in predictions}) == 34
    assert not any("reference" in row for row in predictions)
    assert p.minimal_sets([{"run"}, {"run", "event"}]) == [["run"]]


def test_invalid_archive_metadata_is_rejected_without_echoing_value():
    with pytest.raises(ValueError, match="invalid_observation_schema"):
        p.check_events([{**event("target_final", True), "actor": p.CANARY}])


def test_report_saves_predictions_before_reference_and_scores_errors(tmp_path, monkeypatch):
    rows = [event("target_final", False), event("cli_end", True, number=2)]
    tmp_path.joinpath("observations.jsonl").write_text("\n".join(map(json.dumps, rows)))
    p.write_json(tmp_path / "reference.json", [{"run": 1, "target_present": False,
                 "appearance_vs_cli_end": "not_applicable"}])
    p.write_json(tmp_path / "capture.json", [{"started": True, "real_agent_observed": True,
                  "timeout": False, "stats": {}}])
    original = Path.read_text
    def guarded_read(path, *args, **kwargs):
        if path.name == "reference.json":
            assert tmp_path.joinpath("predictions.jsonl").exists()
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "read_text", guarded_read)
    result = p.report(tmp_path)
    assert result["summary"]["full"]["CORRECT"] == 1
    assert result["summary"]["status_only"]["WRONG"] == 1
    case = next(row for row in result["rows"] if row["question"] == "target_present"
                and row["fields"] == ["run", "kind", "value"])
    assert case["verdict"] == "CORRECT"
    assert case["minimal_correct_fieldsets"] == [["kind", "run", "value"]]


def test_no_reference_and_no_effect_are_different_outcomes():
    assert p.judge(False, None) == "UNJUDGEABLE"
    assert p.judge(None, "not_applicable") == "NOT_APPLICABLE"
    assert p.judge(False, False) == "CORRECT"


def test_failed_agent_start_does_not_become_a_real_run(tmp_path, monkeypatch):
    monkeypatch.setattr(p, "PANEL", ("write",))
    output = tmp_path / "out"
    p.capture(output, str(tmp_path / "nonexistent-codex"), 1)
    result = p.report(output)
    assert result["summary"]["real_agent_runs_observed"] == 0
    assert result["summary"]["full"] == {"UNJUDGEABLE": 2}


def test_storage_failure_propagates(tmp_path):
    with pytest.raises(OSError):
        p.write_json(tmp_path / "missing" / "output.json", {"safe": True})


def test_missing_entire_run_remains_in_native_query_roster():
    rows = p.all_predictions([], native=True)
    assert {r["run"] for r in rows} == set(range(1, 7))
    assert {r["question"] for r in rows} == {"target_present", "appearance_vs_native_end"}
    assert all(r["prediction"]["answer"] is None for r in rows)


def test_positive_order_claim_with_no_effect_is_wrong():
    assert p.judge("after", "not_applicable") == "WRONG"
    assert p.judge("before", "not_applicable") == "WRONG"


def test_tool_success_and_agent_completion_are_separate():
    rows = [event("tool_end", False), event("native_end", True, number=2)]
    assert p.status_baseline(rows, 1, "target_present")["answer"] is True
    assert p.status_baseline(rows, 1, "target_present", tool=True)["answer"] is False


def test_failed_final_sample_cannot_reuse_old_cutoff(tmp_path, monkeypatch):
    sensor = p.TargetSensor(tmp_path / "target", 1, p.Recorder())
    sensor.sample()
    assert sensor.last_interval is not None
    original = Path.stat
    def denied_target(path, *args, **kwargs):
        if path.name == "target":
            raise PermissionError("synthetic")
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "stat", denied_target)
    sensor.sample(final=True)
    assert sensor.last_interval is None
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}])
    reference = p.reference_at_cutoff(tmp_path, receipt, sensor.last_interval, 10)
    assert reference["target_present"] is None
    assert reference["target_check"] is None
    assert reference["reference_issue"] == "reference_target_check_failed"


def test_missing_cutoff_keeps_presence_unknown_with_valid_later_check(tmp_path):
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}])
    reference = p.reference_at_cutoff(tmp_path, receipt, None, 10)
    assert reference["target_check"] is False
    assert reference["target_present"] is None
    assert reference["reference_issue"] == "missing_cutoff_observation"


def test_native_fixture_and_completion_have_actual_separate_observations(tmp_path, monkeypatch):
    from research.native_driver import Session
    monkeypatch.setattr(p, "PANEL", ("write_fail",))
    session = Session(tmp_path / "run")
    try:
        assert session.call(1) == 7
        assert not any(e["kind"] == "native_end" for e in session.recorder.events)
        session.states[1]["sensor"].sample()
        session.close(1)
        with pytest.raises(ValueError, match="duplicate_native_callback"):
            session.close(1)
        session.finish()
        result = p.report(tmp_path / "run", native=True)
        assert result["summary"]["full"] == {"CORRECT": 2}
        assert result["summary"]["tool_status_only"]["WRONG"] == 1
        assert result["summary"]["without_target_evidence"] == {"UNKNOWN": 2}
        assert all(r["tested_additions"] is None for r in result["rows"]
                   if r.get("view") == "without_target_evidence")
        assert all(c["necessary_in_this_comparison"] for c in result["information_comparisons"])
        assert result["panel_fieldsets"]["target_present"]["minimal_correct_fieldsets"] == [
            ["kind", "run", "value"]]
    finally:
        for state in session.states.values():
            state["stop"].set()
            state["watcher"].join()
        session.temp.cleanup()


@pytest.mark.parametrize("failure,started,timeout", [("timeout", True, True), ("start", False, False)])
def test_native_failed_tool_attempt_is_visible(tmp_path, monkeypatch, failure, started, timeout):
    import subprocess
    from research import native_driver
    monkeypatch.setattr(p, "PANEL", ("write",))
    session = native_driver.Session(tmp_path / "run")
    def fail(*args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired("synthetic", 10)
        raise OSError("synthetic")
    monkeypatch.setattr(native_driver.subprocess, "run", fail)
    try:
        with pytest.raises((OSError, subprocess.TimeoutExpired)):
            session.call(1)
        session.finish()
        capture = json.loads((tmp_path / "run" / "capture.json").read_text())[0]
        assert capture["tool_attempts"] == 1
        assert capture["started"] is started and capture["timeout"] is timeout
        assert capture["failure"] is not None
        assert capture["real_agent_observed"] is False
        assert not any(e["kind"] == "tool_end" for e in session.recorder.events)
    finally:
        for state in session.states.values():
            state["stop"].set()
            state["watcher"].join()
        session.temp.cleanup()


@pytest.mark.parametrize("record_type", [[], {}, None, True, 7])
def test_invalid_cli_record_type_cannot_kill_reader(record_type):
    counts, recorder = Counter(), p.Recorder()
    p.project_cli({"type": record_type, "reason": p.CANARY}, 1, recorder, counts)
    assert counts["invalid_records"] == 1
    assert not recorder.events
    assert p.CANARY not in json.dumps(counts)


@pytest.mark.parametrize("entry", [
    {"create_before_ns": 50, "create_after_ns": 10},
    {"create_before_ns": 10},
    {"create_before_ns": p.CANARY, "create_after_ns": 20},
    {"create_before_ns": True, "create_after_ns": 20},
    {"create_before_ns": -1, "create_after_ns": 20},
    {"call": p.CANARY}, {"creation_conflict": p.CANARY}, [], None,
])
def test_invalid_receipt_cannot_produce_safe_truth_or_copy_values(tmp_path, entry):
    receipt = tmp_path / "receipt.jsonl"
    write_receipt(receipt, [{"call": True}, entry])
    tmp_path.joinpath("target").touch()
    result = p.reference_at_cutoff(tmp_path, receipt, (30, 31), 25)
    assert result["target_present"] is None
    assert result["appearance_vs_cli_end"] is None
    assert result["reference_issue"] == "invalid_reference_receipt"
    assert p.CANARY not in json.dumps(result)


def test_partial_receipt_is_explicitly_unjudgeable(tmp_path):
    receipt = tmp_path / "receipt.jsonl"
    receipt.write_text('{"call":true}\n{"create_before_ns":')
    result = p.reference_at_cutoff(tmp_path, receipt, (30, 31), 25)
    assert p.judge(True, result["target_present"]) == "UNJUDGEABLE"
    assert result["reference_issue"] == "invalid_reference_receipt"


@pytest.mark.parametrize("cutoff,end", [((31, 30), 25), ((p.CANARY, 30), 25),
                                       ((30, 31), p.CANARY), ((30, 31), True)])
def test_bad_reference_clock_bounds_are_not_truth(tmp_path, cutoff, end):
    result = p.reference_at_cutoff(tmp_path, tmp_path / "receipt", cutoff, end)
    assert result["target_present"] is None and result["appearance_vs_cli_end"] is None
    assert result["reference_issue"] == "invalid_reference_time"
    assert p.CANARY not in json.dumps(result)
