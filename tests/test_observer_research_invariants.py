"""Relevant PR19 invariants against current interfaces, without old harnesses."""

from __future__ import annotations

import importlib.util
import itertools
import json
from pathlib import Path

import pytest

from lab.fake_adapter import FakeAdapter

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
SPEC = importlib.util.spec_from_file_location("research_invariants_p1", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
p1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p1)


@pytest.mark.parametrize("fault", ["parent_is_file", "destination_is_directory"])
def test_export_io_failure_preserves_effect_decision_and_lifecycle(tmp_path, monkeypatch, fault):
    blocked = tmp_path / "blocked"
    if fault == "parent_is_file":
        blocked.write_bytes(b"")
        destination = blocked / "events.jsonl"
    else:
        blocked.mkdir()
        destination = blocked
    # Real filesystem error, rather than replacing the entire emitter with a stub.
    with pytest.raises(OSError), destination.open("a", encoding="utf-8"):
        pass
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", "1")
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(destination))

    adapter = FakeAdapter()
    original_files = dict(adapter.repo.files)
    allowed = adapter.write("a", "ordinary.py", "wf-observer-failure", "inert")
    denied = adapter.write("a", "config/security-policy.json", "wf-observer-failure", "inert")
    assert allowed.allow is True
    assert allowed.effect_committed is True
    assert adapter.repo.files == {**original_files, "ordinary.py": "inert"}
    assert denied.allow is False
    assert denied.effect_committed is False
    assert adapter.lab.finish("wf-observer-failure") is True


@pytest.mark.parametrize(
    "seen_ns,absent_ns,expected_order",
    [(5, 4, "VOR"), (13, 12, "NACH"), (11, 9, None)],
)
def test_bound_measurement_order_survives_every_delivery_permutation(
    seen_ns, absent_ns, expected_order
):
    measurements = [
        ("target_initial", False, 1),
        ("tool_end", True, 2),
        ("cli_end", True, 10),
        ("target_absent", False, absent_ns),
        ("target_seen", True, seen_ns),
        ("target_final", True, 14),
    ]
    rows = [
        {"run": 1, "kind": kind, "value": value, "t_ns": timestamp, "event": number}
        for number, (kind, value, timestamp) in enumerate(measurements, start=1)
    ]
    original = json.dumps(rows)
    snapshot = p1.infer(rows, 1)
    timing = p1.relate(rows, 1)
    assert snapshot["verdict"] == "BELEGT"
    assert snapshot["target_present"] is True
    assert timing["order"] == expected_order
    assert timing["verdict"] == ("UNBEKANNT" if expected_order is None else "BELEGT")
    for delivered in itertools.permutations(rows):
        assert p1.infer(list(delivered), 1) == snapshot
        assert p1.relate(list(delivered), 1) == timing
    assert json.dumps(rows) == original
