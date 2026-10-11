"""v0.3 I7: deleting security-test artifacts needs an approval token."""

from lab.models import I7_SECURITY_TEST_DELETE, ActionRequest
from lab.validator import Lab


def test_security_test_delete_without_token_denied():
    lab = Lab()
    wid = "wf-i7"
    for path in ("tests/test_security.py", "tests/security/test_policy.py"):
        before = lab.state(wid).snapshot()
        d = lab.submit(ActionRequest("A", "file.delete", path, {}, wid))
        assert d.allow is False, path
        assert d.deny_reason == I7_SECURITY_TEST_DELETE
        assert lab.state(wid).action_count == before.action_count
        assert lab.state(wid).provenance == before.provenance


def test_security_test_delete_with_token_allowed():
    lab = Lab()
    d = lab.submit(
        ActionRequest(
            "A",
            "file.delete",
            "tests/test_security.py",
            {"approval_token": "APPROVE-DEL"},
            "wf-i7-ok",
        )
    )
    assert d.allow is True
    rec = lab.state("wf-i7-ok").provenance[-1]
    assert rec.action == "file.delete"
    assert "APPROVE-DEL" not in str(rec)


def test_non_security_delete_does_not_need_token():
    lab = Lab()
    d = lab.submit(ActionRequest("A", "file.delete", "src/app.py", {}, "wf-i7-other"))
    assert d.allow is True
