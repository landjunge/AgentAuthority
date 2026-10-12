"""Actual diagnostic artifacts and metadata failure regression; no writer retries."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/a4-completion-runs/2026-10-12"
SPEC = importlib.util.spec_from_file_location(
    "a4c_probes", ROOT / "research/a4_completion/probes.py"
)
assert SPEC and SPEC.loader
PROBES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBES)


def test_bcc_actual_funcs_registry_is_used(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda _: "prog_id: 41\nrecursion_misses: 0\n")
    result = PROBES.program_info(SimpleNamespace(funcs={b"enter": SimpleNamespace(fd=17)}))
    assert result["enter"]["recursion_misses"] == 0 and result["enter"]["prog_id"] == 41


@pytest.mark.parametrize(
    "raw", ["prog_id: 41\n", "prog_id: 41\nrecursion_misses: invalid\n", "recursion_misses: 0\n"]
)
def test_missing_invalid_metadata_is_unknown_not_zero(monkeypatch, raw):
    monkeypatch.setattr(Path, "read_text", lambda _: raw)
    result = PROBES.program_info(SimpleNamespace(funcs={"enter": SimpleNamespace(fd=17)}))
    assert result["enter"]["recursion_misses"] is None


def test_missing_bcc_registry_is_unknown():
    result = PROBES.program_info(SimpleNamespace())
    assert result["missing_program_registry"]["recursion_misses"] is None


def test_fdinfo_io_failure_does_not_destroy_collected_evidence(monkeypatch):
    def fail(_):
        raise OSError("diagnostic fixture: inaccessible fdinfo")

    monkeypatch.setattr(Path, "read_text", fail)
    result = PROBES.program_info(SimpleNamespace(funcs={"enter": SimpleNamespace(fd=17)}))
    assert result["enter"]["recursion_misses"] is None


def test_exact_probe_name_is_required(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda _: "p_entry_suffix 4 0\n")
    result = PROBES.profile(["p_entry"])
    assert not result["complete"] and PROBES.misses(result, "p_entry") is None


@pytest.mark.parametrize("miss", [0, 1, 12])
def test_real_profile_column_is_preserved(monkeypatch, miss):
    monkeypatch.setattr(Path, "read_text", lambda _: f"p_entry 42 {miss}\nother 3 99\n")
    result = PROBES.profile(["p_entry"])
    assert result["complete"] and PROBES.misses(result, "p_entry") == miss


def test_healthy_actual_lifecycle_matches_its_separate_child_reference():
    result = json.loads((DATA / "controls/healthy.json").read_text())
    life = result["lifecycle"]
    assert result["agent_identities"] == result["delegations"] == result["target_write_jobs"] == 0
    assert [row["kind"] for row in life["records"]] == [1, 2, 3]
    assert {row["pid"] for row in life["records"]} == {result["reference_child_pid"]}
    assert life["map_update_failures"] == life["fork_entry_nmissed"] == 0
    assert all(row["recursion_misses"] == 0 for row in life["program_info"].values())


def test_actual_map_exhaustion_is_detected_as_failure_not_no_effect():
    result = json.loads((DATA / "controls/map-full.json").read_text())
    assert result["synthetic_map_fill_entries"] == 512
    assert result["reference_exit"] == 0 and result["reference_child_pid"] > 0
    assert result["lifecycle"]["map_update_failures"] == 1
    assert result["lifecycle"]["records"] == []
    assert result["target_write_jobs"] == 0


def test_idle_write_probe_health_is_not_a_new_writer_proof():
    capture = [
        json.loads(row)
        for row in (DATA / "controls/write-channel-idle.jsonl").read_text().splitlines()
    ]
    summary = next(row["summary"] for row in capture if "summary" in row)
    assert summary["entry_probe_nmissed"] == 0
    assert summary["records"] == summary["stats"]["0"] == 0
    assert summary["classic_profile"]["complete"]
    assert len(summary["program_info"]) == 3


def test_failed_original_capture_cannot_inherit_later_control_metrics():
    statuses = json.loads((DATA / "phase1/process-status.json").read_text())
    assert statuses == {"observer_exit": 1, "trial_exit": 1}
    capture = [json.loads(row) for row in (DATA / "phase1/capture.jsonl").read_text().splitlines()]
    assert len([row for row in capture if row.get("record", {}).get("kind") == 1]) == 1
    assert not any("summary" in row for row in capture)
    assert (DATA / "phase1/trial.stdout.json").read_bytes() == b""
    assert b"no attribute 'functions'" in (DATA / "phase1/trial.stderr.log").read_bytes()
