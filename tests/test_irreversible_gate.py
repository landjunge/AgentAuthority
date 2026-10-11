"""repo.delete / release.publish without approval_token → I6 deny."""

from lab.models import I6_IRREVERSIBLE, ActionRequest
from lab.validator import Lab


def test_irreversible_without_token_denied():
    lab = Lab()
    wid = "wf-irr"
    for action in ("repo.delete", "release.publish"):
        before = lab.state(wid).snapshot()
        d = lab.submit(ActionRequest("A", action, action, {}, wid))
        assert d.allow is False
        assert d.deny_reason == I6_IRREVERSIBLE
        after = lab.state(wid)
        assert after.action_count == before.action_count
        assert after.irreversible_effects == before.irreversible_effects
        assert after.provenance == before.provenance
    assert lab.state(wid).irreversible_effects == []


def test_irreversible_with_token_allowed():
    lab = Lab()
    wid = "wf-irr-token"
    token = "APPROVE-TOKEN-XYZ"
    d = lab.submit(ActionRequest("A", "repo.delete", "repo", {"approval_token": token}, wid))
    assert d.allow is True
    st = lab.state(wid)
    assert "repo.delete" in st.irreversible_effects
    rec = st.provenance[-1]
    assert rec.action == "repo.delete"
    assert rec.decision == "ALLOW"
    assert rec.state_after["action_count"] == 1
    assert token not in str(rec)
    assert "approval_token" not in rec.state_after
