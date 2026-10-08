"""Isolated regression tests for the Run-03 source-evidence boundary prototype."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

import pytest

from probes.collector_source_boundary_analysis import (
    audit_run03,
    quarantine_unattested_claim,
)


@pytest.mark.parametrize("answer", ["DIESELBE", "VERSCHIEDEN", "UNBEKANNT"])
def test_collector_claim_never_promotes_itself_to_authenticated(answer):
    raw = {
        "A": answer,
        "C": "JA",
        "D": "claimed source authentic",
        "authenticated": True,
        "signed_by_collector": True,
    }
    before = copy.deepcopy(raw)
    result = quarantine_unattested_claim(raw)
    assert result["A"] == "UNBEKANNT"
    assert result["positive_identity_authorized"] is False
    assert result["source_authenticated"] is False
    assert result["raw_A"] == answer
    assert raw == before


@pytest.mark.parametrize("raw", [None, {"A": "DIESELBE", "C": "JA"}, {"A": "BOGUS"}])
def test_missing_or_malformed_provenance_never_confers_authority(raw):
    assert quarantine_unattested_claim(raw)["A"] == "UNBEKANNT"


def test_frozen_run03_case_matrix_and_tradeoff():
    root = Path(__file__).resolve().parents[1] / (
        "docs/observer-collector-manipulation-c1-c7-run03/2026-10-08"
    )
    report = audit_run03(root)
    assert [case["case"] for case in report["cases"]] == [
        "C1", "C2", "C3", "C4", "C5", "C6", "C7"
    ]
    assert [case["case"] for case in report["cases"] if case["raw_wrong"]] == [
        "C3", "C4", "C7"
    ]
    assert report["ground_truth_cases"] == 5
    assert report["raw_wrong"] == 3
    assert report["guarded_wrong"] == 0
    assert report["raw_positive"] == 5
    assert report["guarded_positive"] == 0
    assert report["guarded_unknown"] == 7


def test_tampered_archive_does_not_produce_normal_report(tmp_path):
    root = Path(__file__).resolve().parents[1] / (
        "docs/observer-collector-manipulation-c1-c7-run03/2026-10-08"
    )
    copy_root = tmp_path / "archive"
    shutil.copytree(root / "pre-gt", copy_root / "pre-gt")
    shutil.copytree(root / "post-gt", copy_root / "post-gt")
    target = copy_root / "pre-gt" / "responses" / "P7.json"
    row = json.loads(target.read_text())
    row["raw_observer_abcd"]["A"] = "VERSCHIEDEN"
    target.write_text(json.dumps(row))
    with pytest.raises(ValueError, match="integrity_mismatch"):
        audit_run03(copy_root)
