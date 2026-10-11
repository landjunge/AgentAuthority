"""Phase 2 value-id binding. Frozen: docs/PHASE2-VALUE-ID-BINDING.md."""

from lab.phase2.authority import AGENT_A, AGENT_B
from lab.phase2.experiment03_control_flow import ImplicitFlowExperiment
from lab.phase2.gated_runtime import GatedLab
from lab.phase2.labels import SENSITIVE
from lab.phase2.workflow import (
    REASON_COLLISION,
    REASON_EGRESS,
    REASON_EMPTY,
    Experiment,
)


def test_exp01_sensitive_id_cannot_be_rebound_public():
    e = Experiment(ifc=True)
    assert e.customer_read(AGENT_A, "C1").allow
    assert e.workflow_send(AGENT_A, "C1", AGENT_B).allow
    assert e.workflow_receive(AGENT_B, "C1").allow
    before = e.catalog["C1"].label
    d = e.public_write(AGENT_A, "C1")
    assert d.allow is False
    assert d.reason == REASON_COLLISION
    assert e.catalog["C1"].label == before == SENSITIVE
    assert e.holdings[AGENT_B]["C1"].label == SENSITIVE
    egress = e.external_send(AGENT_B, "C1")
    assert egress.allow is False
    assert egress.reason == REASON_EGRESS
    assert e.external == []


def test_exp01_transfer_of_same_id_still_allows():
    e = Experiment(ifc=True)
    assert e.customer_read(AGENT_A, "C1").allow
    sent = e.workflow_send(AGENT_A, "C1", AGENT_B)
    assert sent.allow is True
    rec = e.workflow_receive(AGENT_B, "C1")
    assert rec.allow is True
    assert rec.value is not None and rec.value.label == SENSITIVE


def test_exp01_empty_derive_is_deny_not_crash():
    e = Experiment(ifc=True)
    d = e.derive(AGENT_A, "D0", [])
    assert d.allow is False
    assert d.reason == REASON_EMPTY
    assert "D0" not in e.catalog


def test_exp02_overwrite_after_transfer_does_not_declassify_in_flight():
    wf = GatedLab().workflow("wf-bind")
    assert wf.customer_read(AGENT_A, "C1").allow
    tr = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    assert tr.allow is True
    mid = tr.message_id
    rebound = wf.public_write(AGENT_A, "C1")
    assert rebound.allow is False
    assert rebound.reason == REASON_COLLISION
    assert wf.envelopes["C1"].label == SENSITIVE
    rec = wf.receive(AGENT_B, mid)
    assert rec.allow is True
    assert rec.effective_label == SENSITIVE
    egress = wf.external_send(AGENT_B, "C1")
    assert egress.allow is False
    assert egress.reason == REASON_EGRESS
    assert wf.external == []


def test_exp02_empty_derive_is_deny_not_crash():
    wf = GatedLab().workflow("wf-empty")
    d = wf.derive(AGENT_A, "D0", [])
    assert d.allow is False
    assert d.reason == REASON_EMPTY
    assert "D0" not in wf.envelopes


def test_exp03_sensitive_id_cannot_be_rebound_public():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.customer_read(AGENT_A, "C1").allow
    d = exp.public_write(AGENT_A, "C1")
    assert d.allow is False
    assert d.reason == REASON_COLLISION
    assert exp.catalog["C1"].label == SENSITIVE
    assert exp.holdings[AGENT_A]["C1"].label == SENSITIVE


def test_exp03_empty_derive_is_deny_not_crash():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    d = exp.derive(AGENT_A, "D0", [])
    assert d.allow is False
    assert d.reason == REASON_EMPTY
    assert "D0" not in exp.catalog


def test_exp03_denied_control_decide_does_not_write_decisions():
    exp = ImplicitFlowExperiment(ifc=True, control_deps=True)
    assert exp.public_write(AGENT_A, "X", "pub").allow
    assert exp.customer_read(AGENT_A, "C1").allow
    before = dict(exp.decisions)
    d = exp.control_decide(AGENT_A, "X", ["C1"])
    assert d.allow is False
    assert d.reason == REASON_COLLISION
    assert exp.decisions == before
    assert "X" not in exp.decisions
    assert exp.catalog["X"].label == "PUBLIC"
    sw = exp.state_write(AGENT_A, "S", "1", created_under="X")
    assert sw.allow is False
    assert "S" not in exp.workflow_state
    assert exp.external == []


def test_exp02_identical_remint_keeps_gate_checkpoint():
    wf = GatedLab().workflow("wf-prov")
    assert wf.customer_read(AGENT_A, "C1").allow
    tr = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    assert tr.allow is True
    checkpoint = f"{AGENT_A}->CommunicationGate->{AGENT_B}:{tr.message_id}"
    assert checkpoint in wf.envelopes["C1"].provenance
    remint = wf.customer_read(AGENT_A, "C1")
    assert remint.allow is True
    assert checkpoint in wf.envelopes["C1"].provenance
