"""P3 checks validity and late effect on the existing P2 flow.

Synthetic rows are not a new agent run. The controlled case is a real file
created by the existing late tool. The P2 archive is only read.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
ROOT = SCRIPT.parents[1]
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)

CANARY = "SECRET-CANARY-p3"
P2_RUN = ROOT / "docs" / "p1-runs" / "2026-10-09-p2-local"
ARCHIVES = (
    "2026-10-09-attempt-03",
    "2026-10-09-attempt-04",
    "2026-10-09-p2-local",
)


def bundle(run: int = 7) -> tuple[list[dict], dict, dict]:
    observations = [
        {"run": run, "kind": "target_initial", "value": False, "t_ns": 10, "event": 1},
        {"run": run, "kind": "tool_end", "value": True, "t_ns": 15, "event": 2},
        {"run": run, "kind": "cli_end", "value": True, "t_ns": 20, "event": 3},
        {"run": run, "kind": "target_absent", "value": False, "t_ns": 25, "event": 4},
        {"run": run, "kind": "target_seen", "value": True, "t_ns": 30, "event": 5},
        {"run": run, "kind": "target_final", "value": True, "t_ns": 40, "event": 6},
    ]
    result = {
        "run": run,
        "mode": "late",
        "counts": {
            "model_completions": 1,
            "tool_reports": 1,
            "recording_ok": True,
            "cli_success": True,
        },
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "target": p1.infer(observations, run),
        "evaluation": "KORREKT",
        "scope": "local_snapshot_plus_post_end_order",
        "timing": p1.relate(observations, run),
        "timing_evaluation": "KORREKT",
    }
    reference = {
        "calls": 1,
        "target_present": True,
        "valid": True,
        "order": "NACH",
        "order_applicable": True,
        "order_valid": True,
    }
    return observations, result, reference


def test_current_evidence_recognizes_effect_after_end():
    observations, result, reference = bundle()
    reading = p1.assess(observations, result, reference, "current")
    assert reading["fehler"] == []
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["wirkung"]["target_present"] is True
    assert reading["wirkung"]["beleg"] == [1, 3, 6]
    assert reading["wirkung"]["geltung"] == "lokaler_abfragepunkt"
    assert reading["zeitbezug"]["ordnung"] == "NACH"
    assert reading["zeitbezug"]["beleg"] == [3, 4, 5]
    assert reading["ende_ist_wirkungsfreiheit"] == {
        "aussage": "NEIN",
        "grund": "end_is_an_event",
        "beleg": [],
    }
    assert reading["identitaet"]["aussage"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert reading["agent_run"] == "BELEGT"
    assert reading["bindung"] == "independent_local_effect"
    assert reading["recht_uebernommen"] is False


def test_end_alone_is_not_freedom_from_effect():
    observations = [{"run": 4, "kind": "cli_end", "value": True, "t_ns": 20, "event": 1}]
    result = {"run": 4, "counts": {"recording_ok": True}}
    reading = p1.assess(observations, result, {}, "missing")
    assert reading["fehler"] == []
    assert reading["zeitbezug"]["aussage"] == "UNBEKANNT"
    assert reading["zeitbezug"]["grund"] != "no_effect"
    assert reading["ende_ist_wirkungsfreiheit"]["aussage"] == "NEIN"
    assert reading["identitaet"] == {
        "aussage": "UNBEKANNT",
        "grund": "missing_evidence",
        "beleg": [],
    }
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"


def test_stale_and_forged_sources_do_not_become_identity():
    observations, result, reference = bundle()
    stale_rows = [dict(event) for event in observations]
    stale_rows[-1] = {**stale_rows[-1], "live": True, "released": True, "identity": CANARY}
    stale = p1.assess(stale_rows, result, reference, "stale")
    assert stale["identitaet"]["aussage"] == "UNBEKANNT"
    assert stale["identitaet"]["grund"] == "stale_source"
    assert stale["wirkung"]["grund"] == "invalid_evidence"
    assert stale["wirkung"]["geltung"] == "UNBEKANNT"
    assert stale["herkunft"]["aussage"] == "UNBEKANNT"
    assert CANARY not in json.dumps(stale)

    old_but_ordered = p1.assess(observations, result, reference, "stale")
    assert old_but_ordered["wirkung"]["aussage"] == "BELEGT"
    assert old_but_ordered["wirkung"]["geltung"] == "UNBEKANNT"
    assert old_but_ordered["identitaet"]["grund"] == "stale_source"
    assert old_but_ordered["herkunft"]["aussage"] == "UNBEKANNT"

    result["counts"]["model_completions"] = 0
    result["agent_run"] = "BELEGT"
    result["proven_agent_runs"] = 1
    forged = p1.assess(observations, result, reference, "forged")
    assert forged["agent_run"] == "UNBEKANNT"
    assert forged["identitaet"]["grund"] == "forged_source"
    assert forged["herkunft"]["aussage"] == "UNBEKANNT"
    assert forged["recht_uebernommen"] is False


def test_consistent_fd_packet_is_not_current_identity():
    observations, result, reference = bundle()
    claim = {
        "A": "DIESELBE",
        "B": CANARY,
        "C": "JA",
        "fd_set_verified": True,
        "source_authenticated": False,
        "positive_identity_authorized": True,
        "identity": CANARY,
    }
    reading = p1.assess(observations, result, reference, "forged", fd_claim=claim)
    assert reading["fd_relation"]["aussage"] == "UNBEKANNT"
    assert reading["fd_relation"]["grund"] == "unmeasured_packet_not_identity"
    assert reading["fd_relation"]["source_authenticated"] == "UNBEKANNT"
    assert reading["fd_relation"]["recht_uebernommen"] is False
    assert CANARY not in json.dumps(reading)
    assert "positive_identity_authorized" not in json.dumps(reading)

    authenticated = p1.assess(
        observations,
        result,
        reference,
        "forged",
        fd_claim={"A": "DIESELBE", "source_authenticated": True, "note": CANARY},
    )
    assert authenticated["fd_relation"]["aussage"] == "UNBEKANNT"
    assert authenticated["fd_relation"]["grund"] == "forged_authentication"
    assert authenticated["fd_relation"]["source_authenticated"] == "UNBEKANNT"
    assert CANARY not in json.dumps(authenticated)


def test_measured_fd_relation_stays_positive_without_authentication():
    measured = {
        "A": "DIESELBE",
        "B": CANARY,
        "C": "JA",
        "D": CANARY,
        "fd_set_verified": True,
        "source_authenticated": False,
        "positive_identity_authorized": True,
    }
    kept = p1.apply_fd_measurement(measured)
    assert kept["aussage"] == "DIESELBE"
    assert kept["source_authenticated"] is False
    assert kept["recht_uebernommen"] is False
    assert kept["grund"] == "local_relation_not_origin"
    assert CANARY not in json.dumps(kept)
    assert "positive_identity_authorized" not in json.dumps(kept)

    different = dict(measured)
    different["A"] = "VERSCHIEDEN"
    assert p1.apply_fd_measurement(different)["aussage"] == "VERSCHIEDEN"

    promoted = dict(measured)
    promoted["source_authenticated"] = True
    refused = p1.apply_fd_measurement(promoted)
    assert refused["aussage"] == "UNBEKANNT"
    assert refused["grund"] == "forged_authentication"
    assert refused["source_authenticated"] == "UNBEKANNT"

    consistent = dict(measured)
    consistent["fd_set_verified"] = False
    unverified = p1.apply_fd_measurement(consistent)
    assert unverified["aussage"] == "UNBEKANNT"
    assert unverified["grund"] == "verifier_not_positive"
    assert unverified["source_authenticated"] is False


def test_archived_p2_run_still_shows_late_effect_without_rewriting_it():
    before = {path.name: path.read_bytes() for path in P2_RUN.iterdir() if path.is_file()}
    observations = json.loads((P2_RUN / "observations.json").read_text(encoding="utf-8"))
    reference = json.loads((P2_RUN / "reference.json").read_text(encoding="utf-8"))
    result = json.loads((P2_RUN / "result.json").read_text(encoding="utf-8"))
    run = result["run"]
    snapshot = p1.infer(observations, run)
    timing = p1.relate(observations, run)
    assert snapshot["verdict"] == "BELEGT"
    assert snapshot["target_present"] is True
    assert snapshot["evidence"] == [1, 3, 6]
    assert timing["order"] == "NACH"
    assert timing["evidence"] == [3, 4, 5]
    assert reference["valid"] is True
    assert reference["target_present"] is True
    assert reference["order"] == "NACH"
    reading = p1.assess(observations, result, reference, "current")
    assert reading["fehler"] == []
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["zeitbezug"]["ordnung"] == "NACH"
    assert reading["identitaet"]["aussage"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert reading["agent_run"] == "BELEGT"
    assert reading["bindung"] == "independent_local_effect"
    after = {path.name: path.read_bytes() for path in P2_RUN.iterdir() if path.is_file()}
    assert after == before


def test_controlled_late_effect_is_independently_present(tmp_path):
    root = tmp_path / "late"
    measured = p1.measure_controlled_late_effect(root)
    observations = measured["observations"]
    reference = measured["reference"]
    result = measured["result"]
    target = root / "target"
    receipt = [
        json.loads(line)
        for line in (root / "receipt.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    created = next(row["created"] for row in receipt if "created" in row)
    cli_end = next(event for event in observations if event["kind"] == "cli_end")
    assert target.is_file()
    assert created[0] > cli_end["t_ns"]
    assert reference["valid"] is True
    assert reference["calls"] == 1
    assert reference["target_present"] is True
    assert reference["order"] == "NACH"
    assert reference["order_valid"] is True
    assert result["agent_run"] == "UNBEKANNT"
    assert result["proven_agent_runs"] == 0
    assert result["target"]["verdict"] == "BELEGT"
    assert result["target"]["target_present"] is True
    assert result["timing"]["order"] == "NACH"
    assert result["timing_evaluation"] == "KORREKT"
    assert result["evaluation"] == "KORREKT"
    reading = p1.assess(observations, result, reference, "current")
    assert reading["fehler"] == []
    assert reading["zeitbezug"]["ordnung"] == "NACH"
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["identitaet"]["aussage"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert "prompt" not in json.dumps(measured)
    assert CANARY not in json.dumps(measured)


def test_committed_controlled_case_matches_the_functions():
    folder = ROOT / "docs" / "p1-runs" / "2026-10-09-p3-controlled"
    observations = json.loads((folder / "observations.json").read_text(encoding="utf-8"))
    reference = json.loads((folder / "reference.json").read_text(encoding="utf-8"))
    result = json.loads((folder / "result.json").read_text(encoding="utf-8"))
    stored = json.loads((folder / "assess.json").read_text(encoding="utf-8"))
    platform_fd = json.loads((folder / "fd-platform.json").read_text(encoding="utf-8"))
    run = result["run"]
    assert p1.infer(observations, run)["evidence"] == [1, 3, 6]
    assert p1.relate(observations, run)["order"] == "NACH"
    assert reference["order"] == "NACH"
    assert reference["target_present"] is True
    assert result["agent_run"] == "UNBEKANNT"
    assert result["evaluation"] == "KORREKT"
    assert result["timing_evaluation"] == "KORREKT"
    assert p1.assess(observations, result, reference, "current") == stored
    assert stored["wirkung"]["aussage"] == "BELEGT"
    assert stored["zeitbezug"]["ordnung"] == "NACH"
    assert stored["identitaet"]["aussage"] == "UNBEKANNT"
    assert stored["fehler"] == []
    returned = platform_fd["return"]
    assert returned["A"] == "UNBEKANNT"
    assert returned["source_authenticated"] is False
    assert returned["positive_identity_authorized"] is False
    assert platform_fd["projected"] == p1.apply_fd_measurement(returned)
    assert platform_fd["projected"]["aussage"] == "UNBEKANNT"
    assert platform_fd["projected"]["source_authenticated"] is False
    assert platform_fd["projected"]["recht_uebernommen"] is False
    dumped = json.dumps(
        {"observations": observations, "reference": reference, "result": result, "assess": stored}
    )
    assert "prompt" not in dumped
    assert CANARY not in dumped


def test_older_archives_stay_byte_identical():
    root = ROOT / "docs" / "p1-runs"
    hashes = {
        name: {
            path.name: path.read_bytes()
            for path in sorted((root / name).iterdir())
            if path.is_file()
        }
        for name in ARCHIVES
    }
    observations, result, reference = bundle()
    p1.assess(observations, result, reference, "current")
    again = {
        name: {
            path.name: path.read_bytes()
            for path in sorted((root / name).iterdir())
            if path.is_file()
        }
        for name in ARCHIVES
    }
    assert again == hashes
