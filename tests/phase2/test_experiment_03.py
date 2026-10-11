"""Phase 2 Experiment 03. Does not modify Phase 1 or Experiments 01–02."""

from lab.models import I1_ACTION_BUDGET, ActionRequest
from lab.phase2.authority import AGENT_A, AGENT_B, CUSTOMERS
from lab.phase2.communication_gate import CommunicationGate
from lab.phase2.experiment03_control_flow import (
    REASON_AUTHORITY,
    REASON_CONTROL,
    ImplicitFlowExperiment,
)
from lab.phase2.gated_runtime import GatedLab
from lab.phase2.labels import PUBLIC, SENSITIVE
from lab.phase2.workflow import Experiment
from lab.validator import Lab


def _implicit_attack(exp: ImplicitFlowExperiment, *, created_under: str | None):
    t1 = exp.customer_read(AGENT_A, "C1")
    t2 = None
    if created_under:
        t2 = exp.control_decide(AGENT_A, created_under, ["C1"])
    t3 = exp.state_write(AGENT_A, "STATE_1", "1", created_under=created_under)
    t4 = exp.state_read(AGENT_B, "STATE_1")
    t5 = exp.external_send(AGENT_B, "STATE_1")
    return t1, t2, t3, t4, t5


def test_explicit_ifc_baseline_implicit_attack_succeeds():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=False)
    t1, _, t3, t4, t5 = _implicit_attack(exp, created_under=None)
    assert t1.allow and t3.allow and t4.allow
    assert t5.allow is True
    assert t5.authority_ok is True
    assert "STATE_1" in exp.external
    assert exp.holdings[AGENT_B]["STATE_1"].payload == "1"
    assert "C1" not in exp.holdings[AGENT_B]


def test_control_dependency_blocks_sensitive_implicit_egress():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    t1, t2, t3, t4, t5 = _implicit_attack(exp, created_under="D1")
    assert t1.allow and t2.allow and t3.allow and t4.allow
    assert t5.allow is False
    assert t5.authority_ok is True
    assert t5.flow_ok is False
    assert t5.reason == REASON_CONTROL
    assert "STATE_1" not in exp.external
    expl = t5.explanation
    assert expl["reason"] == "SENSITIVE_CONTROL_DEPENDENCY_EGRESS"
    assert expl["control_dependency"] == "D1"
    assert expl["sensitive_origin"] == CUSTOMERS
    assert expl["path"] == ["C1", "D1", "STATE_1"]
    assert "CUSTOMER_FLAG" not in str(expl)


def test_public_control_dependency_egress_allowed():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.public_write(AGENT_A, "P1", "pub").allow
    assert exp.control_decide(AGENT_A, "D2", ["P1"]).allow
    assert exp.state_write(AGENT_A, "STATE_P", "1", created_under="D2").allow
    assert exp.state_read(AGENT_B, "STATE_P").allow
    d = exp.external_send(AGENT_B, "STATE_P")
    assert d.allow is True
    assert "STATE_P" in exp.external


def test_sensitive_internal_control_use_allowed():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.customer_read(AGENT_A, "C1").allow
    assert exp.control_decide(AGENT_A, "D1", ["C1"]).allow
    assert exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1").allow
    assert exp.external == []


def test_sensitive_control_label_survives_state_write():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    w = exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    assert w.value is not None
    assert w.value.label == SENSITIVE
    assert w.value.origin == CUSTOMERS


def test_sensitive_control_label_survives_cross_agent_read():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    r = exp.state_read(AGENT_B, "STATE_1")
    assert r.value is not None
    assert r.value.label == SENSITIVE
    assert r.value.derived_from == ("D1",)


def test_new_public_value_under_sensitive_control_remains_tainted():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    w = exp.state_write(AGENT_A, "X", "1", created_under="D1", claimed_label=PUBLIC)
    assert w.value is not None and w.value.label == SENSITIVE
    exp.state_read(AGENT_B, "X")
    d = exp.external_send(AGENT_B, "X")
    assert d.allow is False
    assert "X" not in exp.external


def test_agent_b_cannot_strip_control_dependency():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    exp.state_read(AGENT_B, "STATE_1")
    w = exp.wrap(AGENT_B, "P1", "STATE_1", claimed_label=PUBLIC)
    assert w.value is not None and w.value.label == SENSITIVE
    d = exp.external_send(AGENT_B, "P1")
    assert d.allow is False
    assert "P1" not in exp.external


def test_denied_implicit_egress_does_not_mutate_external_state():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    _implicit_attack(exp, created_under="D1")
    assert exp.external == []
    assert any(a["decision"] == "DENY" for a in exp.attempts)


def test_provenance_explains_sensitive_control_origin():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    *_, t5 = _implicit_attack(exp, created_under="D1")
    expl = t5.explanation
    assert expl["decision"] == "DENY"
    assert expl["authority_ok"] is True
    assert expl["flow_ok"] is False
    assert expl["reason"] == "SENSITIVE_CONTROL_DEPENDENCY_EGRESS"
    assert expl["value_id"] == "STATE_1"
    assert expl["control_dependency"] == "D1"
    assert expl["sensitive_origin"] == CUSTOMERS
    assert expl["path"] == ["C1", "D1", "STATE_1"]
    assert "CUSTOMER_FLAG" not in str(expl)


def test_direct_agent_a_egress_still_denied_by_authority():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.public_write(AGENT_A, "H1", "hello")
    d = exp.external_send(AGENT_A, "H1")
    assert d.allow is False
    assert d.reason == REASON_AUTHORITY
    assert "H1" not in exp.external


def test_agent_b_normal_public_egress_allowed():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.public_write(AGENT_B, "H1", "hello-world").allow
    d = exp.external_send(AGENT_B, "H1")
    assert d.allow is True
    assert "H1" in exp.external


def test_literal_sensitive_string_with_public_provenance_is_allowed():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.public_write(AGENT_B, "L1", "CUSTOMER_FLAG").allow
    d = exp.external_send(AGENT_B, "L1")
    assert d.allow is True
    assert "L1" in exp.external


def test_same_output_value_can_be_public_or_sensitive_by_provenance():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.public_write(AGENT_A, "P1", "1")
    exp.control_decide(AGENT_A, "Dpub", ["P1"])
    exp.state_write(AGENT_A, "X", "1", created_under="Dpub")
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "Y", "1", created_under="D1")
    exp.state_read(AGENT_B, "X")
    exp.state_read(AGENT_B, "Y")
    assert exp.holdings[AGENT_B]["X"].payload == exp.holdings[AGENT_B]["Y"].payload == "1"
    assert exp.external_send(AGENT_B, "X").allow is True
    assert exp.external_send(AGENT_B, "Y").allow is False
    assert "X" in exp.external and "Y" not in exp.external


def test_multi_step_control_dependency_survives():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    exp.control_decide(AGENT_A, "D2", ["STATE_1"])
    exp.state_write(AGENT_A, "STATE_2", "1", created_under="D2")
    exp.state_read(AGENT_B, "STATE_2")
    d = exp.external_send(AGENT_B, "STATE_2")
    assert d.allow is False
    assert d.explanation["path"] == ["C1", "D1", "STATE_1", "D2", "STATE_2"]
    assert "STATE_2" not in exp.external


def test_cross_agent_attack_requires_shared_workflow_context():
    a = ImplicitFlowExperiment(ifc=True, control_deps=True, workflow_id="wf-a")
    b = ImplicitFlowExperiment(ifc=True, control_deps=True, workflow_id="wf-b")
    a.customer_read(AGENT_A, "C1")
    a.control_decide(AGENT_A, "D1", ["C1"])
    a.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    r = b.state_read(AGENT_B, "STATE_1")
    assert r.allow is False
    d = b.external_send(AGENT_B, "STATE_1")
    assert d.allow is False
    assert b.external == []


def test_legitimate_multi_agent_workflow_completes():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.public_write(AGENT_A, "P1", "ok").allow
    assert exp.control_decide(AGENT_A, "D2", ["P1"]).allow
    assert exp.state_write(AGENT_A, "STATE_P", "1", created_under="D2").allow
    assert exp.state_read(AGENT_B, "STATE_P").allow
    assert exp.external_send(AGENT_B, "STATE_P").allow
    assert "STATE_P" in exp.external


def test_phase1_regression_suite_unchanged():
    lab = Lab()
    for i in range(100):
        assert lab.submit(ActionRequest("A", "file.read", f"r{i}", {}, "p1")).allow
    d = lab.submit(ActionRequest("A", "file.read", "rX", {}, "p1"))
    assert d.allow is False and d.deny_reason == I1_ACTION_BUDGET


def test_phase2_experiment01_suite_unchanged():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    exp.workflow_send(AGENT_A, "C1", AGENT_B)
    exp.workflow_receive(AGENT_B, "C1")
    d = exp.external_send(AGENT_B, "C1")
    assert d.allow is False
    assert exp.external == []


def test_phase2_experiment02_communication_gate_suite_unchanged():
    wf = GatedLab().workflow("wf-reg")
    assert wf.public_write(AGENT_A, "P1").allow
    d = wf.request_transfer(AGENT_A, AGENT_B, "P1")
    assert d.allow is True
    rec = wf.receive(AGENT_B, d.message_id)
    assert rec.allow is True
    assert CommunicationGate is not None


def test_adversarial_copy_preserves_control_taint():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "STATE_1", "1", created_under="D1")
    exp.state_read(AGENT_B, "STATE_1")
    exp.copy(AGENT_B, "STATE_1", "SCOPY")
    assert exp.external_send(AGENT_B, "SCOPY").allow is False


def test_adversarial_three_step_control_chain():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.customer_read(AGENT_A, "C1")
    exp.control_decide(AGENT_A, "D1", ["C1"])
    exp.state_write(AGENT_A, "S1", "1", created_under="D1")
    exp.control_decide(AGENT_A, "D2", ["S1"])
    exp.state_write(AGENT_A, "S2", "1", created_under="D2")
    exp.control_decide(AGENT_A, "D3", ["S2"])
    exp.state_write(AGENT_A, "S3", "1", created_under="D3")
    exp.state_read(AGENT_B, "S3")
    d = exp.external_send(AGENT_B, "S3")
    assert d.allow is False
    assert "C1" in d.explanation["path"]


def test_agent_a_cannot_state_read():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    exp.public_write(AGENT_A, "P1", "x")
    exp.control_decide(AGENT_A, "D2", ["P1"])
    exp.state_write(AGENT_A, "STATE_P", "1", created_under="D2")
    d = exp.state_read(AGENT_A, "STATE_P")
    assert d.allow is False
    assert d.reason == REASON_AUTHORITY


def test_agent_b_cannot_customer_read():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    d = exp.customer_read(AGENT_B, "C1")
    assert d.allow is False
    assert d.reason == REASON_AUTHORITY
