"""Explicit fail-closed probes (Claude review HIGH-2). Not a frozen Phase 2 experiment rewrite."""

from lab.phase2.authority import AGENT_A
from lab.phase2.experiment03_control_flow import ImplicitFlowExperiment
from lab.phase2.workflow import REASON_ACTOR, Experiment


def test_workflow_send_unknown_receiver_is_deny_not_keyerror():
    e = Experiment(ifc=True)
    e.customer_read(AGENT_A, "C1")
    d = e.workflow_send(AGENT_A, "C1", "agent-evil")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert e.inbox[AGENT_A] == {}
    assert "C1" in e.holdings[AGENT_A]


def test_external_send_unknown_actor_is_deny_not_keyerror():
    e = Experiment(ifc=True)
    d = e.external_send("agent-x", "C1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert e.external == []


def test_experiment03_external_send_unknown_actor_is_deny_not_keyerror():
    e = ImplicitFlowExperiment(ifc=True, control_deps=True)
    d = e.external_send("agent-x", "C1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
