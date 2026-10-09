"""P6 ingress countercontrols. Invented counters are not an agent execution."""

from __future__ import annotations

import importlib.util
import json
import os
import stat
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
spec = importlib.util.spec_from_file_location("p6_observer", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)
CANARY = "SYNTHETIC-P6-METADATA-MARKER"


def invented_bundle():
    rows = [
        {"run": 7, "kind": kind, "value": value, "t_ns": stamp, "event": i}
        for i, (kind, value, stamp) in enumerate(
            [
                ("target_initial", False, 10),
                ("tool_end", True, 15),
                ("cli_end", True, 20),
                ("target_absent", False, 25),
                ("target_seen", True, 30),
                ("target_final", True, 40),
            ],
            1,
        )
    ]
    result = {
        "run": 7,
        "mode": "late",
        "counts": {"model_completions": 1, "tool_reports": 1, "recording_ok": True},
        "proven_agent_runs": 1,
        "agent_run": "BELEGT",
        "target": p1.infer(rows, 7),
        "timing": p1.relate(rows, 7),
        "evaluation": "KORREKT",
        "timing_evaluation": "KORREKT",
        "scope": "local_snapshot_plus_post_end_order",
    }
    reference = {
        "calls": 1,
        "target_present": True,
        "valid": True,
        "order": "NACH",
        "order_applicable": True,
        "order_valid": True,
    }
    return rows, result, reference


@pytest.mark.parametrize("evidence_class", ["forged", "stale", "missing"])
def test_invented_complete_bundle_does_not_prove_agent(evidence_class):
    rows, result, reference = invented_bundle()
    reading = p1.assess(rows, result, reference, evidence_class)
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["bindung"] != "independent_local_effect"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"


def test_omitted_class_does_not_promote_archive_to_current():
    reading = p1.assess(*invented_bundle())
    assert reading["evidence_class"] == "stale"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["agent_run"] == "UNBEKANNT"
    # Historical row consistency and chronology are still available.
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["zeitbezug"]["ordnung"] == "NACH"


@pytest.mark.parametrize("invalid_class", [{"current": CANARY}, [CANARY], None, 1, True])
def test_invalid_class_returns_bounded_unknown(invalid_class):
    reading = p1.assess(*invented_bundle(), evidence_class=invalid_class)
    assert reading["evidence_class"] == "forged"
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["wirkung"]["geltung"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert CANARY not in json.dumps(reading)


def test_local_effect_remains_usable_without_model_or_origin(tmp_path):
    measured = p1.measure_controlled_late_effect(tmp_path / "local")
    reading = p1.assess(
        measured["observations"], measured["result"], measured["reference"], "current"
    )
    target = tmp_path / "local" / "target"
    assert stat.S_ISREG(target.lstat().st_mode) and target.stat().st_size == 0
    assert reading["wirkung"]["aussage"] == "BELEGT"
    assert reading["zeitbezug"]["ordnung"] == "NACH"
    assert reading["agent_run"] == "UNBEKANNT"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"


def test_held_fd_relation_remains_useful_and_untrusted_ingress_stays_unknown(tmp_path):
    first = os.open(tmp_path / "a", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
    handles = [first]
    try:
        handles.append(os.dup(first))
        handles.append(os.open(tmp_path / "b", os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600))
        before = [os.fstat(fd) for fd in handles]
        after = [os.fstat(fd) for fd in handles]
        pairs_before = [(s.st_dev, s.st_ino) for s in before]
        pairs_after = [(s.st_dev, s.st_ino) for s in after]
        assert all(stat.S_ISREG(s.st_mode) for s in before + after)
        assert pairs_before == pairs_after
        assert pairs_before[0] == pairs_before[1]
        assert pairs_before[0] != pairs_before[2]
        for index, expected in [(1, "DIESELBE"), (2, "VERSCHIEDEN")]:
            packet = {
                "A": "DIESELBE" if pairs_before[0] == pairs_before[index] else "VERSCHIEDEN",
                "C": "JA",
                "fd_set_verified": True,
                "source_authenticated": False,
            }
            # Projection only: actual fstat is above, not established by JSON.
            projected = p1.apply_fd_measurement(packet)
            assert projected["aussage"] == expected
            assert projected["source_authenticated"] is False
            reading = p1.assess(*invented_bundle(), fd_claim=packet)
            assert reading["fd_relation"]["aussage"] == "UNBEKANNT"
            assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    finally:
        for fd in handles:
            os.close(fd)


def test_explicit_current_is_still_a_caller_contract_not_authentication():
    reading = p1.assess(*invented_bundle(), evidence_class="current")
    # This deliberately exposes the remaining internal precondition. The P6
    # patch does not authenticate acquisition, bind(), or the FD projection.
    assert reading["agent_run"] == "BELEGT"
    assert reading["wirkung"]["geltung"] == "lokaler_abfragepunkt"
    assert reading["herkunft"]["aussage"] == "UNBEKANNT"
    assert reading["recht_uebernommen"] is False
