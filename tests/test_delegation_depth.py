"""Delegation convention: root depth 0; root→A is depth 1 (allowed);
A→B would be depth 2 and is denied by I4 (max 1).
"""

from lab.models import I4_DELEGATION_DEPTH, ActionRequest
from lab.validator import Lab


def test_delegation_depth_boundary():
    lab = Lab()
    wid = "wf-del"
    root = lab.submit(ActionRequest("root", "file.read", "README.md", {}, wid))
    assert root.allow
    assert lab.state(wid).actor_depth["root"] == 0

    to_a = lab.submit(ActionRequest("root", "delegate", "A", {"to": "A"}, wid))
    assert to_a.allow is True
    assert lab.state(wid).delegation_depth == 1
    assert lab.state(wid).actor_depth["A"] == 1

    to_b = lab.submit(ActionRequest("A", "delegate", "B", {"to": "B"}, wid))
    assert to_b.allow is False
    assert to_b.deny_reason == I4_DELEGATION_DEPTH
    assert lab.state(wid).delegation_depth == 1
    assert "B" not in lab.state(wid).actor_depth
