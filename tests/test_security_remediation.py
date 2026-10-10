"""WB1098 repair controls; original catalogs, sinks and assertions stay frozen."""

from __future__ import annotations

from dataclasses import replace
import threading

import pytest

from lab import ActionRequest, Decision, Lab
from lab.fake_adapter import FakeAdapter
from lab.remediation import BOUND_APPROVAL_REQUIRED, RemediationLab
from tests.convergence.catalog import cb01_steps
from tests.convergence.fp_panel import interior_steps
from tests.realcase import catalog as realcase


def request(action="shell.exec", resource="terminal", params=None, actor="A", workflow="w"):
    return ActionRequest(actor, action, resource, params or {}, workflow)


def approved(lab, req):
    token = lab.approve(req)
    return replace(req, parameters={**req.parameters, "approval_token": token})


@pytest.mark.parametrize("case", realcase.PHASE1_CASES, ids=lambda case: case.case_id)
def test_original_rc_sinks_are_blocked_by_repair_profile(monkeypatch, case):
    monkeypatch.setattr(realcase, "Lab", RemediationLab)
    result = realcase.run_phase1_on(case)
    assert result.outcome is False
    assert result.denied_at is not None


@pytest.mark.parametrize("seed", range(20))
def test_frozen_harmless_fp_interior_still_allowed(seed):
    lab = RemediationLab()
    for req in interior_steps(seed):
        assert lab.submit(req).allow


@pytest.mark.parametrize(
    "action,resource,params",
    [
        ("file.write", ".vscode/settings.json", {"content": "INERT"}),
        ("file.write", ".cursor/mcp.json", {"content": "INERT"}),
        ("file.write", ".cursor/rules/mcp.json", {"command_hash": "BENIGN"}),
        ("mcp.start", "demo", {"command_hash": "BENIGN"}),
        ("shell.exec", "grep", {"command": "grep TODO README.md"}),
        ("repo.delete", "repo", {}),
        ("release.publish", "release", {}),
        ("file.delete", "tests/test_security.py", {}),
    ],
)
def test_legitimate_bound_consent_works_once(action, resource, params):
    lab = RemediationLab()
    req = approved(lab, request(action, resource, params))
    assert lab.submit(req).allow
    before = lab.state("w").public_view()
    assert not lab.submit(req).allow
    assert lab.state("w").public_view() == before


@pytest.mark.parametrize(
    "change",
    [
        {"actor": "other"},
        {"workflow_id": "other"},
        {"action": "mcp.start"},
        {"resource": "other"},
        {"parameters": {"command": "changed"}},
    ],
)
def test_handle_cannot_authorize_a_different_descriptor(change):
    lab = RemediationLab()
    req = approved(lab, request(params={"command": "original"}))
    token = req.parameters["approval_token"]
    if "parameters" in change:
        change = {"parameters": {**change["parameters"], "approval_token": token}}
    assert not lab.submit(replace(req, **change)).allow
    assert lab.submit(req).allow  # a rejected attempt does not consume consent


@pytest.mark.parametrize(
    "path",
    [
        "./.cursor/mcp.json",
        "x/../.cursor/mcp.json",
        ".cursor\\mcp.json",
    ],
)
def test_control_path_alias_cannot_bypass_bound_consent(path):
    lab = RemediationLab()
    assert lab.submit(request("file.read", path)).allow
    denied = lab.submit(request("file.write", path))
    assert denied.deny_reason == BOUND_APPROVAL_REQUIRED
    req = approved(lab, request("file.write", ".cursor/mcp.json"))
    assert lab.submit(replace(req, resource=path)).allow


def test_changed_mcp_descriptor_requires_new_consent():
    lab = RemediationLab()
    initial = approved(
        lab,
        request(
            "file.write",
            ".cursor/rules/mcp.json",
            {
                "server": "demo",
                "command_hash": "BENIGN",
            },
        ),
    )
    assert lab.submit(initial).allow
    changed = replace(initial, parameters={**initial.parameters, "command_hash": "CHANGED"})
    assert not lab.submit(changed).allow
    assert lab.submit(approved(lab, changed)).allow
    start = approved(lab, request("mcp.start", "demo", {"command_hash": "BENIGN"}))
    assert not lab.submit(
        replace(
            start,
            parameters={
                **start.parameters,
                "command_hash": "CHANGED",
            },
        )
    ).allow
    assert lab.submit(start).allow


def test_original_rc04_command_reuse_fails_after_legitimate_first_command():
    lab = RemediationLab()
    case = next(case for case in realcase.PHASE1_CASES if case.case_id == "RC-04")
    lab.approve(case.steps[0], token="T")
    assert lab.submit(case.steps[0]).allow
    assert not lab.submit(case.steps[1]).allow
    assert lab.submit(approved(lab, case.steps[1])).allow


def test_stolen_publish_token_has_no_coordinator_grant():
    lab = RemediationLab()
    req = realcase.PHASE1_CASES[-1].steps[-1]
    assert lab.submit(req).deny_reason == "I6_IRREVERSIBLE"
    assert lab.state(req.workflow_id).irreversible_effects == []


def test_original_cb01_with_consent_only_for_first_effect_cannot_reuse():
    lab = RemediationLab()
    first, second = cb01_steps()
    lab.approve(first, token="T")
    assert lab.submit(first).allow
    assert lab.submit(second).deny_reason == "I6_IRREVERSIBLE"
    assert lab.state("cb-01").irreversible_effects == ["repo.delete"]
    assert lab.submit(approved(lab, second)).allow


def test_original_cb01_score_catches_unissued_token_at_i6(monkeypatch):
    from tests.convergence import score

    monkeypatch.setattr(score, "Lab", RemediationLab)
    kind, last = score.SCORES["CB-01"]()
    assert kind == score.CAUGHT_EXPECTED
    assert last.deny_reason == "I6_IRREVERSIBLE" and not last.allow


def test_expiry_and_finish_invalidate_old_grants():
    now = [10.0]
    lab = RemediationLab(clock=lambda: now[0])
    req = approved(lab, request())
    now[0] = 71.0
    assert not lab.submit(req).allow
    req = approved(lab, request())
    assert lab.finish("w")
    assert not lab.submit(req).allow
    assert lab.submit(approved(lab, request())).allow


def test_existing_hard_policy_is_not_overridden_by_consent():
    lab = RemediationLab()
    for action, resource in [
        ("file.write", "config/security-policy.json"),
        ("net.connect", "https://external.example"),
    ]:
        assert not lab.submit(approved(lab, request(action, resource))).allow


def test_budget_denial_does_not_consume_handle():
    lab = RemediationLab()
    req = approved(lab, request())
    for _ in range(100):
        assert lab.submit(request("file.read", "README.md")).allow
    assert lab.submit(req).deny_reason == "I1_ACTION_BUDGET"
    assert req.parameters["approval_token"] in lab._entries["w"].approvals


@pytest.mark.parametrize(
    "params",
    [
        {"command": float("nan")},
        {"command": float("inf")},
        {"command": object()},
        {"command": "x" * 70_000},
        {"approval_token": ["T"]},
    ],
)
def test_invalid_parameters_or_unissued_handle_never_mutate_workflow(params):
    lab = RemediationLab()
    assert not lab.submit(request(params=params)).allow
    assert lab.state("w").action_count == 0


def test_grant_capacity_and_handle_collision_are_bounded():
    lab = RemediationLab()
    req = request()
    lab.approve(req, token="fixture")
    with pytest.raises(ValueError):
        lab.approve(req, token="fixture")
    for _ in range(63):
        lab.approve(req)
    with pytest.raises(ValueError):
        lab.approve(req)


def test_effect_is_once_only_bound_to_decision_request_and_owner():
    lab = Lab()
    req = request("file.write", "src/a.py")
    decision = lab.submit(req)
    effects = []
    assert not Lab().commit_effect(req, decision, lambda: effects.append("other lab"))
    forged = Decision(True, None, [])
    forged._effect_ticket = decision._effect_ticket
    assert not lab.commit_effect(req, forged, lambda: effects.append("forged"))
    assert not lab.commit_effect(
        replace(req, resource="src/b.py"), decision, lambda: effects.append("changed")
    )
    assert lab.commit_effect(req, decision, lambda: effects.append("actual"))
    assert not lab.commit_effect(req, decision, lambda: effects.append("replay"))
    assert effects == ["actual"] and decision.effect_committed is True
    assert not Lab().commit_effect(req, decision, lambda: effects.append("foreign retry"))
    assert decision.effect_committed is True


def test_finish_and_generation_reuse_cancel_old_effect_ticket():
    lab = Lab()
    req = request("file.write", "src/a.py")
    old = lab.submit(req)
    assert lab.finish("w")
    fresh = lab.submit(req)
    effects = []
    assert not lab.commit_effect(req, old, lambda: effects.append("old"))
    assert old.effect_committed is False
    assert lab.commit_effect(req, fresh, lambda: effects.append("fresh"))
    assert effects == ["fresh"]


def test_adapter_deny_and_success_have_accurate_effect_status():
    adapter = FakeAdapter()
    before = dict(adapter.repo.files)
    denied = adapter.write("A", "config/security-policy.json", "w", "INERT")
    assert not denied.allow and denied.effect_committed is False
    assert adapter.repo.files == before
    allowed = adapter.write("A", "src/a.py", "w", "INERT")
    assert allowed.allow and allowed.effect_committed is True
    assert adapter.repo.files == {**before, "src/a.py": "INERT"}


def test_bound_control_write_commits_and_does_not_leak_approval():
    lab = RemediationLab()
    adapter = FakeAdapter(lab)
    req = request("file.write", ".cursor/mcp.json", {"content": "INERT"})
    token = lab.approve(req)
    decision = adapter.write("A", req.resource, "w", "INERT", approval_token=token)
    assert decision.allow and decision.effect_committed is True
    assert adapter.repo.files[req.resource] == "INERT"
    assert token not in repr(decision)
    assert token not in repr(lab.state("w").public_view())
    assert token not in repr(lab.state("w").provenance)


def test_callback_exception_is_not_replayed_as_a_second_effect():
    lab = Lab()
    req = request("file.write", "src/a.py")
    decision = lab.submit(req)

    def fail():
        raise ValueError("inert callback failed")

    with pytest.raises(ValueError):
        lab.commit_effect(req, decision, fail)
    assert decision.effect_committed is False
    effects = []
    assert not lab.commit_effect(req, decision, lambda: effects.append("retry"))
    assert effects == []


def test_finish_waits_for_started_effect_and_other_workflows_progress():
    lab = Lab()
    req = request("file.write", "src/a.py")
    decision = lab.submit(req)
    started = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    errors = []
    effects = []

    def effect():
        started.set()
        assert release.wait(5)
        effects.append("before finish")

    def commit():
        try:
            assert lab.commit_effect(req, decision, effect)
        except BaseException as error:
            errors.append(error)

    def finish():
        try:
            assert lab.finish("w")
            finished.set()
        except BaseException as error:
            errors.append(error)

    worker = threading.Thread(target=commit)
    worker.start()
    assert started.wait(5)
    finisher = threading.Thread(target=finish)
    finisher.start()
    try:
        assert lab.submit(request("file.read", "README.md", workflow="independent")).allow
        assert not finished.is_set()
    finally:
        release.set()
        worker.join(10)
        finisher.join(10)
    assert not worker.is_alive() and not finisher.is_alive()
    assert errors == [] and finished.is_set() and effects == ["before finish"]
