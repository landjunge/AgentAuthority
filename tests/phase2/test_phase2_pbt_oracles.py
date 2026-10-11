"""PBT oracle P6: unknown actor is DENY, never a crash. docs/PBT-ORACLE-v1.md."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from lab.phase2.authority import AGENT_A
from lab.phase2.experiment03_control_flow import ImplicitFlowExperiment
from lab.phase2.gated_runtime import GatedLab
from lab.phase2.workflow import REASON_ACTOR, Experiment

UNKNOWN_ACTORS = ("agent-evil", "agent-x", "AGENT-A", "")


@given(actor=st.sampled_from(UNKNOWN_ACTORS))
def test_p6_experiment_send_to_unknown_is_deny(actor):
    e = Experiment(ifc=True)
    e.customer_read(AGENT_A, "C1")
    d = e.workflow_send(AGENT_A, "C1", actor)
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert "C1" in e.holdings[AGENT_A]


@given(actor=st.sampled_from(UNKNOWN_ACTORS))
def test_p6_experiment_external_send_unknown_is_deny(actor):
    e = Experiment(ifc=True)
    d = e.external_send(actor, "C1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert e.external == []


@given(actor=st.sampled_from(UNKNOWN_ACTORS))
def test_p6_experiment03_external_send_unknown_is_deny(actor):
    e = ImplicitFlowExperiment(ifc=True, control_deps=True)
    d = e.external_send(actor, "C1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert e.external == []


@given(actor=st.sampled_from(UNKNOWN_ACTORS))
def test_p6_gated_external_send_unknown_is_deny(actor):
    wf = GatedLab().workflow("wf-p6")
    d = wf.external_send(actor, "C1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
    assert wf.external == []


@given(actor=st.sampled_from(UNKNOWN_ACTORS))
def test_p6_gated_receive_unknown_is_deny(actor):
    wf = GatedLab().workflow("wf-p6r")
    d = wf.receive(actor, "m-1")
    assert d.allow is False
    assert d.reason == REASON_ACTOR
