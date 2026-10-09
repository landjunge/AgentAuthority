"""Synthetic CLI records test the recorder; these are never real-agent evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)


def event(kind, value, seq, run=1):
    return {"run": run, "kind": kind, "value": value, "t_ns": seq, "event": seq}


def observation(present=True, success=True):
    return [
        event("target_initial", False, 1),
        event("tool_end", success, 2),
        event("cli_end", success, 3),
        event("target_final", present, 4),
    ]


@pytest.mark.parametrize("success", [True, False])
@pytest.mark.parametrize("present", [True, False])
def test_snapshot_is_independent_of_reported_success(success, present):
    answer = p1.infer(observation(present, success), 1)
    assert answer["verdict"] == "BELEGT"
    assert answer["target_present"] is present
    assert 2 not in answer["evidence"]


@pytest.mark.parametrize("remove", ["target_initial", "target_final", "cli_end"])
def test_missing_measurement_never_becomes_effect(remove):
    rows = [e for e in observation() if e["kind"] != remove]
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_status_only_wrong_run_and_recording_error_are_unknown():
    assert (
        p1.infer([event("tool_end", True, 1), event("cli_end", True, 2)], 1)["verdict"]
        == "UNBEKANNT"
    )
    assert p1.infer(observation(), 2)["verdict"] == "UNBEKANNT"
    assert p1.infer(observation(), 1, False)["verdict"] == "UNBEKANNT"


def test_duplicate_and_conflict_handling():
    rows = observation()
    assert p1.infer(rows + [rows[-1].copy()], 1) == p1.infer(rows, 1)
    assert p1.infer(rows + [{**rows[-1], "value": False}], 1)["verdict"] == "UNBEKANNT"
    assert p1.infer(rows + [event("target_final", False, 5)], 1)["verdict"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "patch",
    [{"kind": []}, {"value": 1}, {"run": True}, {"event": 0}, {"t_ns": -1}, {"payload": "private"}],
)
def test_malformed_evidence_is_unknown(patch):
    rows = observation()
    rows[-1] = {**rows[-1], **patch}
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_preexisting_target_or_reversed_measurement_is_unknown():
    rows = observation()
    rows[0]["value"] = True
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"
    rows = observation()
    rows[-1]["t_ns"] = 2
    assert p1.infer(rows, 1)["verdict"] == "UNBEKANNT"


def test_projection_drops_canaries_ids_and_usage():
    counts = {"invalid_records": 0, "model_completions": 0, "tool_reports": 0, "error_records": 0}
    rows = []
    raw = {
        "type": "item.completed",
        "id": "PRIVATE",
        "item": {
            "type": "command_execution",
            "exit_code": 0,
            "command": "PRIVATE",
            "aggregated_output": "PRIVATE",
            "status": "PRIVATE",
        },
        "usage": "PRIVATE",
    }
    p1.project(raw, 1, rows, counts)
    assert counts["tool_reports"] == 1
    assert set(rows[0]) == p1.FIELDS
    assert "PRIVATE" not in json.dumps(rows) + json.dumps(counts)
    raw["item"]["exit_code"] = True
    p1.project(raw, 1, rows, counts)
    assert len(rows) == 1 and counts["invalid_records"] == 1


@pytest.mark.parametrize(
    "mode,exists,code",
    [("write", True, 0), ("noop", False, 0), ("fail", False, 1), ("write_fail", True, 1)],
)
def test_real_local_tool_and_separate_reference(tmp_path, mode, exists, code):
    # Real filesystem/process test, NOT a real LLM/agent run.
    tool = tmp_path / "tool.py"
    tool.write_text(p1.TOOL)
    completed = subprocess.run([sys.executable, str(tool), mode], check=False)
    assert completed.returncode == code
    assert p1.probe(tmp_path / "target") is exists
    answer = p1.reference(tmp_path, (time.monotonic_ns(), time.monotonic_ns()))
    assert answer == {"calls": 1, "target_present": exists, "valid": True}


def test_missing_conflicting_or_late_reference_is_not_truth(tmp_path):
    cutoff = (1, 2)
    assert p1.reference(tmp_path, cutoff)["valid"] is False
    (tmp_path / "target").touch()
    receipt = tmp_path / "receipt.jsonl"
    for content in (
        '{"call": 1}\n',
        '{"call": true}\n',
        '{"call": true}\n{"created": [2, 3]}\n',
        '{"call": true}\n{"call": true}\n{"created": [1, 1]}\n',
    ):
        receipt.write_text(content)
        assert p1.reference(tmp_path, cutoff)["valid"] is False


def test_symlink_never_becomes_target_evidence(tmp_path):
    outside = tmp_path / "other"
    outside.touch()
    (tmp_path / "target").symlink_to(outside)
    assert p1.probe(tmp_path / "target") is None


def test_sensor_failure_is_missing_evidence(tmp_path, monkeypatch):
    def unavailable(self):
        raise PermissionError("PRIVATE")

    monkeypatch.setattr(Path, "lstat", unavailable)
    assert p1.probe(tmp_path / "target") is None


def test_capture_start_failure_and_reference_order(tmp_path, monkeypatch):
    original = p1.reference

    def checked_reference(root, cutoff):
        assert (tmp_path / "run" / "analysis.json").is_file()
        assert (tmp_path / "run" / "observations.json").is_file()
        return original(root, cutoff)

    monkeypatch.setattr(p1, "reference", checked_reference)
    result = p1.capture(tmp_path / "run", codex=str(tmp_path / "missing"))
    assert result["proven_agent_runs"] == 0
    assert result["agent_run"] == result["evaluation"] == "UNBEKANNT"
    assert result["target"]["verdict"] == "UNBEKANNT"
    with pytest.raises(FileExistsError):
        p1.capture(tmp_path / "run")


@pytest.mark.parametrize(
    "code",
    [
        "print('malformed')",
        "print('X' * 100000)",
        "print('[' * 1500 + ']' * 1500)",
        "import time; time.sleep(10)",
    ],
)
def test_actual_process_recording_errors_and_timeout(tmp_path, code):
    rows = []
    counts = p1.collect([sys.executable, "-c", code], "", tmp_path, 1, rows, 0.5)
    assert counts["recording_ok"] is False
    assert p1.infer(rows, 1, counts["recording_ok"])["verdict"] == "UNBEKANNT"
    assert counts["stdout_bytes"] + counts["stderr_bytes"] <= p1.MAX_STREAM + 8192


def test_capture_persists_no_raw_failure_text(tmp_path):
    fake_cli = tmp_path / "synthetic_cli"
    fake_cli.write_text(
        "#!" + sys.executable + "\nimport sys\n"
        "sys.stdin.read()\nprint('PRIVATE_RAW_CANARY')\n"
        "print('PRIVATE_RAW_CANARY', file=sys.stderr)\n"
    )
    fake_cli.chmod(0o700)
    result = p1.capture(tmp_path / "run", codex=str(fake_cli))
    assert result["agent_run"] == "UNBEKANNT"
    assert result["target"]["verdict"] == "UNBEKANNT"
    assert "PRIVATE_RAW_CANARY" not in "".join(
        path.read_text() for path in (tmp_path / "run").iterdir()
    )


@pytest.mark.parametrize("timeout", [float("nan"), float("inf"), 0, -1, 301])
def test_invalid_timeout_does_not_create_run(tmp_path, timeout):
    with pytest.raises(ValueError):
        p1.capture(tmp_path / "run", timeout=timeout)
    assert not (tmp_path / "run").exists()
