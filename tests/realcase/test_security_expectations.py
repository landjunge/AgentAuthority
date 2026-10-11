"""Security expectations. A failure is a measured miss; do not fix in this run."""

import pytest
from catalog import PHASE1_CASES, PHASE2_CASES, run_phase1_on, run_phase2


@pytest.mark.parametrize("case", PHASE1_CASES, ids=lambda case: case.case_id)
def test_phase1_monitor_blocks_forbidden_sink(case):
    result = run_phase1_on(case)
    assert result.outcome is False, (
        f"{case.case_id} reached its inert forbidden sink; "
        f"denied_at={result.denied_at!r}, reason={result.deny_reason!r}"
    )


@pytest.mark.parametrize("case", PHASE2_CASES, ids=lambda case: case.case_id)
def test_phase2_monitor_blocks_sensitive_egress(case):
    result = run_phase2(case, ifc=True)
    assert result.outcome is False, (
        f"{case.case_id} reached fake external sink; reason={result.deny_reason!r}"
    )
