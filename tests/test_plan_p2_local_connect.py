"""P2 binds one late local capture to the accepted P1 fields.

Synthetic rows exercise the binder. They are not the real agent run.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
ROOT = SCRIPT.parents[1]
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)

CANARY = "SECRET-CANARY-p2"
DISTINCT_TIME = 880000000000001


def bundle(run: int = 7) -> tuple[list[dict], dict, dict]:
    observations = [
        {"run": run, "kind": "target_initial", "value": False, "t_ns": DISTINCT_TIME, "event": 1},
        {"run": run, "kind": "tool_end", "value": True, "t_ns": DISTINCT_TIME + 5, "event": 2},
        {"run": run, "kind": "cli_end", "value": True, "t_ns": DISTINCT_TIME + 10, "event": 3},
        {
            "run": run,
            "kind": "target_absent",
            "value": False,
            "t_ns": DISTINCT_TIME + 15,
            "event": 4,
        },
        {"run": run, "kind": "target_seen", "value": True, "t_ns": DISTINCT_TIME + 20, "event": 5},
        {"run": run, "kind": "target_final", "value": True, "t_ns": DISTINCT_TIME + 25, "event": 6},
    ]
    snapshot = p1.infer(observations, run)
    timing = p1.relate(observations, run)
    result = {
        "run": run,
        "mode": "late",
        "requested_model": p1.MODEL,
        "counts": {
            "stdout_bytes": 1,
            "stderr_bytes": 0,
            "raw_lines": 1,
            "invalid_records": 0,
            "model_completions": 1,
            "tool_reports": 1,
            "error_records": 0,
            "started": True,
            "timeout": False,
            "recording_ok": True,
            "cli_success": True,
            "cli_exit_code": 0,
            "startup_error": "UNBEKANNT",
        },
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "target": snapshot,
        "evaluation": "KORREKT",
        "scope": "local_snapshot_plus_post_end_order",
        "timing": timing,
        "timing_evaluation": "KORREKT",
    }
    reference = {
        "calls": 1,
        "target_present": True,
        "valid": True,
        "order": "NACH",
        "order_applicable": True,
        "order_valid": True,
        "prompt": CANARY,
    }
    return observations, result, reference


def test_one_late_flow_binds_effect_without_unmapped_fields():
    observations, result, reference = bundle()
    binding = p1.bind(result, observations, reference)
    assert binding["reason"] == "agent_run_unbekannt"
    assert binding["run"] == 7
    assert binding["agent_run"] == "UNBEKANNT"
    assert binding["start"] == {"event": 1, "kind": "target_initial", "value": False}
    assert binding["tool_report"]["event"] == 2
    assert binding["end"] == {"event": 3, "kind": "cli_end", "value": True}
    assert binding["effect"]["verdict"] == "BELEGT"
    assert binding["effect"]["target_present"] is True
    assert binding["effect"]["evidence"] == [1, 3, 6]
    assert 2 not in binding["effect"]["evidence"]
    assert binding["follow_up"]["order"] == "NACH"
    assert binding["follow_up"]["evidence"] == [3, 4, 5]
    assert binding["independent_effect"] == "UNBEKANNT"
    assert binding["timing_evaluation"] == "UNBEKANNT"
    assert binding["unknown"] == {name: "UNBEKANNT" for name in p1.UNMAPPED}
    dumped = json.dumps(binding)
    assert CANARY not in dumped
    assert str(DISTINCT_TIME) not in dumped
    assert "t_ns" not in dumped


def test_forged_agent_label_and_cli_success_stay_unknown():
    observations, result, reference = bundle()
    result["counts"]["model_completions"] = 0
    result["agent_run"] = "BELEGT"
    result["proven_agent_runs"] = 1
    result["counts"]["cli_success"] = True
    binding = p1.bind(result, observations, reference)
    assert binding["agent_run"] == "UNBEKANNT"
    assert binding["reason"] == "agent_run_unbekannt"
    assert binding["effect"]["verdict"] == "BELEGT"
    assert binding["unknown"]["process_identity"] == "UNBEKANNT"
    result["counts"]["tool_reports"] = 0
    assert p1.bind(result, observations, reference)["agent_run"] == "UNBEKANNT"


def test_extra_actor_field_is_not_stored():
    observations, result, reference = bundle()
    observations[-1] = {**observations[-1], "actor": CANARY}
    binding = p1.bind(result, observations, reference)
    assert binding["reason"] == "invalid_evidence"
    assert binding["agent_run"] == "UNBEKANNT"
    assert CANARY not in json.dumps(binding)


def test_mixed_run_is_not_one_trial():
    observations, result, reference = bundle()
    observations[0] = {**observations[0], "run": 8}
    binding = p1.bind(result, observations, reference)
    assert binding["reason"] == "mixed_run"
    assert binding["agent_run"] == "UNBEKANNT"


def test_reference_disagreement_is_not_confirmed():
    observations, result, reference = bundle()
    reference["target_present"] = False
    binding = p1.bind(result, observations, reference)
    assert binding["independent_effect"] == "FALSCH"
    assert binding["reason"] == "reference_disagrees"
    assert binding["evaluation"] != "KORREKT"


def test_write_mode_is_not_the_p2_flow():
    observations, result, reference = bundle()
    result["mode"] = "write"
    binding = p1.bind(result, observations, reference)
    assert binding["reason"] == "not_the_p2_flow"
    assert binding["follow_up"] == "UNBEKANNT"


def test_connect_rejects_other_modes_without_creating_a_directory(tmp_path):
    output = tmp_path / "not-p2"
    with pytest.raises(ValueError, match="late"):
        p1.connect(output, mode="write")
    assert not output.exists()


def test_connect_writes_binding_and_leaves_observations(tmp_path, monkeypatch):
    observations, result, reference = bundle()
    output = tmp_path / "p2"

    def fake_capture(path, codex, timeout, mode, post_window, *, on_capture):
        assert mode == "late"
        path.mkdir(parents=True, exist_ok=False)
        p1.save(path / "observations.json", observations)
        p1.save(path / "reference.json", reference)
        # An arbitrary callback token is not an acquired measurement.
        on_capture(observations, result, reference, object())
        return result

    monkeypatch.setattr(p1, "capture", fake_capture)
    before = json.dumps(observations)
    binding = p1.connect(output)
    assert binding["reason"] == "agent_run_unbekannt"
    assert json.loads((output / "observations.json").read_text(encoding="utf-8")) == observations
    assert json.dumps(observations) == before
    stored = json.loads((output / "binding.json").read_text(encoding="utf-8"))
    assert stored["run"] == binding["run"]
    assert CANARY not in (output / "binding.json").read_text(encoding="utf-8")


def test_archived_runs_are_refused_and_unchanged():
    root = ROOT / "docs" / "p1-runs"
    before = {
        name: {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((root / name).iterdir())
            if path.is_file()
        }
        for name in p1.ARCHIVED_RUNS
    }
    for name in p1.ARCHIVED_RUNS:
        with pytest.raises(ValueError, match="archived"):
            p1.connect(root / name)
    after = {
        name: {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((root / name).iterdir())
            if path.is_file()
        }
        for name in p1.ARCHIVED_RUNS
    }
    assert after == before
