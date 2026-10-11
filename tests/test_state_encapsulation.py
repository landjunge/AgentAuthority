"""Public Lab.state() must not be the live monitor object. docs/PHASE1-STATE-ENCAPSULATION.md."""

from lab.models import I1_ACTION_BUDGET, ActionRequest
from lab.validator import Lab


def test_mutating_public_state_cannot_reset_the_action_budget():
    lab = Lab()
    wid = "wf-encap"
    for _ in range(100):
        assert lab.submit(ActionRequest("A", "file.write", "src/a.py", {}, wid)).allow
    view = lab.state(wid)
    view.action_count = 0
    view.provenance.clear()
    d = lab.submit(ActionRequest("A", "file.write", "src/a.py", {}, wid))
    assert d.allow is False
    assert d.deny_reason == I1_ACTION_BUDGET
    live = lab.state(wid)
    assert live.action_count == 100
    assert len(live.provenance) == 100


def test_tampering_snapshot_provenance_does_not_rewrite_the_log():
    lab = Lab()
    wid = "wf-prov-copy"
    assert lab.submit(ActionRequest("A", "file.write", "src/a.py", {}, wid)).allow
    snap = lab.state(wid)
    try:
        snap.provenance[0].action = "tampered"
    except Exception:  # noqa: BLE001, S110  a frozen snapshot may raise; the live log must stay
        pass
    assert lab.state(wid).provenance[0].action == "file.write"
