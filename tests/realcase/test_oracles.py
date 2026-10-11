"""The red-before-green equivalent for the experiment: monitor-off must leak."""

import pytest
from catalog import PHASE1_CASES, PHASE2_CASES, run_phase1_off, run_phase2


@pytest.mark.parametrize("case", PHASE1_CASES, ids=lambda case: case.case_id)
def test_phase1_monitor_off_reaches_forbidden_sink(case):
    result = run_phase1_off(case)
    assert result.outcome is True


@pytest.mark.parametrize("case", PHASE2_CASES, ids=lambda case: case.case_id)
def test_phase2_monitor_off_reaches_forbidden_sink(case):
    result = run_phase2(case, ifc=False)
    assert result.outcome is True
