"""P4 compares the archived P2 and P3 record with the existing functions.

The German note is part of the acceptance. This module does not start a Codex
run and does not write an archive file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
ROOT = SCRIPT.parents[1]
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)

P2_RUN = ROOT / "docs" / "p1-runs" / "2026-10-09-p2-local"
P3_RUN = ROOT / "docs" / "p1-runs" / "2026-10-09-p3-controlled"
ACCEPTANCE = ROOT / "docs" / "P4-ABNAHME.md"
CHECKED_SHA = "065f45d73e7cb1d4bdb03717b157c4692cebc52a"
REFERENCE_SHA = "24a90a55702e67b0131fba7775471e34c44a2f712191da75d4388d04be5f6cb6"
P2_OBSERVATIONS_SHA = "0f49f878f5af6a78ac22ed51f950e15f2480cfd650b3f7f96ba1db35e35e0a4d"
P3_OBSERVATIONS_SHA = "ef063a8295202e3d5c864938e38e8a195ddc4bd32339249ed4978a6e08d7f356"


def _load(folder: Path, name: str):
    return json.loads((folder / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_archived_p2_infer_relate_and_bind_match_stored_json():
    observations = _load(P2_RUN, "observations.json")
    reference = _load(P2_RUN, "reference.json")
    result = _load(P2_RUN, "result.json")
    analysis = _load(P2_RUN, "analysis.json")
    binding = _load(P2_RUN, "binding.json")
    run = result["run"]
    snapshot = p1.infer(observations, run)
    timing = p1.relate(observations, run)
    assert snapshot == result["target"]
    assert timing == result["timing"]
    assert {**snapshot, "timing": timing} == analysis
    assert p1.bind(result, observations, reference) == {
        **binding,
        "agent_run": "UNBEKANNT",
        "independent_effect": "UNBEKANNT",
        "evaluation": "UNBEKANNT",
        "timing_evaluation": "UNBEKANNT",
        "reason": "agent_run_unbekannt",
    }


def test_archived_p3_assess_infer_and_relate_match_stored_json():
    observations = _load(P3_RUN, "observations.json")
    reference = _load(P3_RUN, "reference.json")
    result = _load(P3_RUN, "result.json")
    stored = _load(P3_RUN, "assess.json")
    run = result["run"]
    assert p1.infer(observations, run) == result["target"]
    assert p1.relate(observations, run) == result["timing"]
    assert p1.assess(observations, result, reference, "current") == {
        **stored,
        "wirkung": {**stored["wirkung"], "geltung": "UNBEKANNT"},
    }


def test_reference_digests_match_and_observation_digests_differ():
    p2_reference = _sha256(P2_RUN / "reference.json")
    p3_reference = _sha256(P3_RUN / "reference.json")
    p2_observations = _sha256(P2_RUN / "observations.json")
    p3_observations = _sha256(P3_RUN / "observations.json")
    assert p2_reference == p3_reference == REFERENCE_SHA
    assert p2_observations == P2_OBSERVATIONS_SHA
    assert p3_observations == P3_OBSERVATIONS_SHA
    assert p2_observations != p3_observations


def test_acceptance_note_names_the_checked_record():
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert CHECKED_SHA in text
    assert "6233001536916211328" in text
    assert "2847465012503918159" in text
    assert "UNBEKANNT" in text
    assert "RC-01" in text
    assert "OOS-021" in text
    assert "CB-01" in text
    assert "reguläre Datei" in text
    assert "Der heutige Dateizustand der archivierten Ziele ist UNBEKANNT." in text
