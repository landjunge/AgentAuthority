"""Synthetic regressions for the three pre-freeze review findings, not F cases."""
import errno
import hashlib
import json
import sys

from probes import current_local_collector_analyze as analysis
from probes.local_file_identity_capture import save
from tests.test_observer_current_local_collector import packet


def synthetic_archive(tmp_path, io, validity="NEIN"):
    save(tmp_path / "inputs/P1.json", packet())
    input_hash = hashlib.sha256((tmp_path / "inputs/P1.json").read_bytes()).hexdigest()
    save(tmp_path / "responses/P1/answer.json", {
        "input_sha256": input_hash, "raw_observer_abcd": {
            "A": "UNBEKANNT", "B": "Keine Handles", "C": validity,
            "D": "Linux/tmpfs; sequenzielle Checks; kein atomarer Lebenszeitbeweis; "
                 "Keine Packetherkunft; historische/permanente Identitaet"}})
    answer_hash = hashlib.sha256((tmp_path / "responses/P1/answer.json").read_bytes()).hexdigest()
    save(tmp_path / "ground-truth/collector-lifecycle.json", {})
    save(tmp_path / "ground-truth/F1-io.json", io)
    return {"packet": "P1", "native_calls": [], "runtime_handles_supplied": True,
            "answer_saved_sha256": answer_hash}


def test_missing_observer_check_cannot_hide_known_io_truth(tmp_path):
    invocation = synthetic_archive(tmp_path, {
        "truth": "DIESELBE", "stage": "complete", "reference_error": None,
        "full_reads_verified_by_eof_probe": True})
    row = analysis.evaluate_case(tmp_path, 1, invocation)
    assert row["reference_valid"] is True
    assert row["a_correct"] is False
    assert row["reference_c"] == "NEIN" and row["c_correct"] is True
    assert row["frozen_requirements_met"] is False
    assert row["evaluation"] == "FALSCH"


def test_partial_io_remains_unjudgeable_without_release_key(tmp_path):
    invocation = synthetic_archive(tmp_path, {"truth": "UNBEKANNT", "stage": "first_write"})
    row = analysis.evaluate_case(tmp_path, 1, invocation)
    assert row["evaluation"] == "UNBEURTEILBAR"
    assert row["a_correct"] is None


def test_false_confirmation_cannot_hide_behind_technical_failure(tmp_path):
    invocation = synthetic_archive(tmp_path, {
        "truth": "DIESELBE", "stage": "complete", "reference_error": None,
        "full_reads_verified_by_eof_probe": True}, validity="JA")
    invocation["native_calls"] = [{"operation": "run", "attempted": True,
                                   "returned": False, "error": {"errno": errno.ENOENT}}]
    row = analysis.evaluate_case(tmp_path, 1, invocation)
    assert row["technical_collector_obstruction"] is True
    assert row["reference_c"] == "UNBEKANNT" and row["c_correct"] is False
    assert row["evaluation"] == "FALSCH"


def test_duplicates_or_missing_invocations_cannot_pass_case_set(tmp_path, monkeypatch):
    save(tmp_path / "answer-checkpoint-integrity.json", {"sha256": {}})
    save(tmp_path / "ground-truth/collector-lifecycle.json", {
        "invocations": [{"packet": "P1"}, {"packet": "P1"}]})
    save(tmp_path / "capture-status.json", {"invocations_started": 2, "failures": [],
                                           "cleanup_errors": [], "remaining_resource_files": []})
    monkeypatch.setattr(sys, "argv", ["analyze", "--archive", str(tmp_path)])
    assert analysis.main() == 0
    result = json.loads((tmp_path / "derived/evaluation.json").read_text())
    assert result["exact_seven_in_frozen_order"] is False
    assert result["counts"]["unjudgeable"] == 7
    assert result["verdict"] == "INCONCLUSIVE"
