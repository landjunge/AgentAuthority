"""Emit the frozen case matrix as JSON after both oracle and monitor runs."""

from __future__ import annotations

import json

from catalog import PHASE1_CASES, PHASE2_CASES, run_phase1_off, run_phase1_on, run_phase2


def main() -> None:
    rows: list[dict] = []
    for case in PHASE1_CASES:
        off = run_phase1_off(case)
        on = run_phase1_on(case)
        classification = (
            "INVALID" if not off.outcome else "MISSED" if on.outcome else "CAUGHT-OTHER"
        )
        rows.append(
            {
                "id": case.case_id,
                "title": case.title,
                "evidence_type": case.evidence_type,
                "mapping": case.mapping,
                "oracle_off_outcome": off.outcome,
                "monitor_on_outcome": on.outcome,
                "deny_reason": on.deny_reason,
                "classification": classification,
                "source": case.source_url,
            }
        )
    for case in PHASE2_CASES:
        off = run_phase2(case, ifc=False)
        on = run_phase2(case, ifc=True)
        classification = (
            "INVALID"
            if not off.outcome
            else "MISSED"
            if on.outcome
            else "CAUGHT-EXPECTED"
            if on.deny_reason == "SENSITIVE_EXTERNAL_EGRESS"
            else "CAUGHT-OTHER"
        )
        rows.append(
            {
                "id": case.case_id,
                "title": case.title,
                "evidence_type": case.evidence_type,
                "mapping": case.mapping,
                "oracle_off_outcome": off.outcome,
                "monitor_on_outcome": on.outcome,
                "deny_reason": on.deny_reason,
                "classification": classification,
                "source": case.source_url,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
