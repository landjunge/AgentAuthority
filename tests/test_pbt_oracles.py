"""PBT oracles P1–P5, P7. Frozen: docs/PBT-ORACLE-v1.md. Do not invert P5."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from lab.fake_adapter import FakeAdapter
from lab.models import KNOWN_ACTIONS, ActionRequest
from lab.paths import is_protected_path, is_security_test_path
from lab.state import empty_state, predict_next
from lab.validator import Lab

UNKNOWN_ACTIONS = (
    "file.create",
    "file.rm",
    "os.remove",
    "fs.write",
    "custom.inspect",
    "shell.exec",
    "File.write",
    "FILE.DELETE",
)
ORDINARY_PATHS = ("src/a.py", "src/app.py", "README.md", "docs/x.md")
PROTECTED_PATHS = (
    "config/security-policy.json",
    "./config/security-policy.json",
    "config/../config/security-policy.json",
)
SECURITY_PATHS = ("tests/test_security.py", "tests/security/test_policy.py")
ALL_PATHS = (
    ORDINARY_PATHS
    + PROTECTED_PATHS
    + SECURITY_PATHS
    + (
        "src/../../../../etc/passwd",
        "CONFIG/security-policy.json",
        "config/Security-Policy.json",
        "/etc/shadow",
    )
)
ACTIONS = tuple(sorted(KNOWN_ACTIONS)) + UNKNOWN_ACTIONS
PARAMS = ({}, {"approval_token": "T"}, {"to": "C"}, {"destination": "https://evil.example"})


def _freeze(stt):
    return (
        stt.workflow_id,
        stt.action_count,
        stt.files_changed,
        frozenset(stt.touched_paths),
        frozenset(stt.agents),
        stt.delegation_depth,
        frozenset(stt.network_destinations),
        tuple(stt.irreversible_effects),
        tuple(sorted(stt.actor_depth.items())),
        len(stt.provenance),
        tuple((r.seq, r.action, r.resource, r.decision) for r in stt.provenance),
    )


@given(
    action=st.sampled_from(ACTIONS),
    resource=st.sampled_from(ALL_PATHS),
    params=st.sampled_from(PARAMS),
    actor=st.sampled_from(("A", "B", "evil")),
)
def test_p1_submit_does_not_raise(action, resource, params, actor):
    lab = Lab()
    d = lab.submit(ActionRequest(actor, action, resource, dict(params), "wf-p1"))
    assert d.allow in (True, False)
    assert isinstance(d.violated_invariants, list)


@given(
    st.lists(
        st.tuples(
            st.sampled_from(ACTIONS),
            st.sampled_from(ALL_PATHS),
            st.sampled_from(PARAMS),
        ),
        min_size=1,
        max_size=12,
    )
)
def test_p2_deny_does_not_mutate_spec_fields(steps):
    lab = Lab()
    wid = "wf-p2"
    for action, resource, params in steps:
        before = _freeze(lab.state(wid))
        d = lab.submit(ActionRequest("A", action, resource, dict(params), wid))
        after = _freeze(lab.state(wid))
        if not d.allow:
            assert after == before


@given(
    action=st.sampled_from(ACTIONS),
    resource=st.sampled_from(ALL_PATHS),
    params=st.sampled_from(PARAMS),
)
def test_p3_predict_next_does_not_mutate_input(action, resource, params):
    state = empty_state("wf-p3")
    before = _freeze(state)
    predict_next(state, ActionRequest("A", action, resource, dict(params), "wf-p3"))
    assert _freeze(state) == before


@given(
    action=st.sampled_from(UNKNOWN_ACTIONS),
    resource=st.sampled_from(PROTECTED_PATHS + SECURITY_PATHS),
)
def test_p4_unknown_on_protected_is_i9(action, resource):
    d = Lab().submit(ActionRequest("A", action, resource, {}, "wf-p4"))
    assert d.allow is False
    assert "I9_UNKNOWN_ACTION_PROTECTED" in d.violated_invariants


@given(
    action=st.sampled_from(UNKNOWN_ACTIONS),
    resource=st.sampled_from(ORDINARY_PATHS),
)
def test_p5_unknown_on_ordinary_is_not_i9(action, resource):
    assert not is_protected_path(resource, "config/security-policy.json")
    assert not is_security_test_path(resource)
    d = Lab().submit(ActionRequest("A", action, resource, {}, "wf-p5"))
    assert d.deny_reason != "I9_UNKNOWN_ACTION_PROTECTED"


@given(path=st.sampled_from(ALL_PATHS))
def test_p7_adapter_deny_does_not_write_repo(path):
    ad = FakeAdapter()
    before_w = dict(ad.repo.files)
    d = ad.write("A", path, "wf-p7w", "payload")
    if not d.allow:
        assert ad.repo.files == before_w
    before_d = dict(ad.repo.files)
    d2 = ad.delete("A", path, "wf-p7d")
    if not d2.allow:
        assert ad.repo.files == before_d
