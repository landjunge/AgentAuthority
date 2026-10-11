"""Any write to config/security-policy.json is denied (I3)."""

from lab.models import I3_PROTECTED_PATH, PROTECTED_PATH, ActionRequest
from lab.validator import Lab


def test_protected_path_write_denied():
    lab = Lab()
    wid = "wf-prot"
    denied = lab.submit(ActionRequest("A", "file.write", PROTECTED_PATH, {}, wid))
    assert denied.allow is False
    assert denied.deny_reason == I3_PROTECTED_PATH
    assert lab.state(wid).action_count == 0
    assert PROTECTED_PATH not in lab.state(wid).touched_paths
