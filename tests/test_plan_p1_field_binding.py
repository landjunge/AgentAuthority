"""Plan P1 binds one artificial example to the existing runner.

These rows are not a new event schema and not evidence of a real agent run.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p1_controlled_run.py"
spec = importlib.util.spec_from_file_location("p1_controlled_run", SCRIPT)
assert spec is not None and spec.loader is not None
p1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p1)

EXAMPLE = [
    {"run": 1, "kind": "target_initial", "value": False, "t_ns": 10, "event": 1},
    {"run": 1, "kind": "tool_end", "value": True, "t_ns": 15, "event": 2},
    {"run": 1, "kind": "cli_end", "value": True, "t_ns": 20, "event": 3},
    {"run": 1, "kind": "target_absent", "value": False, "t_ns": 25, "event": 4},
    {"run": 1, "kind": "target_seen", "value": True, "t_ns": 30, "event": 5},
    {"run": 1, "kind": "target_final", "value": True, "t_ns": 40, "event": 6},
]


def test_artificial_example_binds_snapshot_and_post_end_order():
    assert p1.infer(EXAMPLE, 1) == {
        "verdict": "BELEGT",
        "target_present": True,
        "reason": "local_snapshot_only",
        "evidence": [1, 3, 6],
    }
    assert p1.relate(EXAMPLE, 1) == {
        "verdict": "BELEGT",
        "order": "NACH",
        "reason": "absence_after_end_then_presence",
        "evidence": [3, 4, 5],
    }


def test_cli_failure_and_incomplete_rows_stay_unknown():
    events: list[dict] = []
    counts = {
        "stdout_bytes": 0,
        "stderr_bytes": 0,
        "raw_lines": 0,
        "invalid_records": 0,
        "model_completions": 0,
        "tool_reports": 0,
        "error_records": 0,
    }
    p1.project({"type": "error"}, 1, events, counts)
    p1.project({"type": "turn.failed"}, 1, events, counts)
    assert events == []
    assert counts["error_records"] == 2
    assert counts["model_completions"] == 0
    assert counts["tool_reports"] == 0
    assert p1.infer(
        [{"run": 1, "kind": "cli_end", "value": False, "t_ns": 20, "event": 1}],
        1,
    ) == {
        "verdict": "UNBEKANNT",
        "target_present": None,
        "reason": "missing_evidence",
        "evidence": [],
    }


def test_actor_and_origin_fields_are_not_accepted_as_known():
    row = {**EXAMPLE[-1], "actor": "claimed"}
    assert p1.infer([*EXAMPLE[:-1], row], 1)["reason"] == "invalid_evidence"
    assert "actor" not in p1.FIELDS
