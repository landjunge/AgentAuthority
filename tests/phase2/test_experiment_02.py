"""Phase 2 Experiment 02. Does not modify Experiment 01 or Phase 1."""

import inspect

from lab.phase2.authority import AGENT_A, AGENT_B, CUSTOMERS
from lab.phase2.communication_gate import POLICY_INTERNAL, REASON_CROSS_WORKFLOW, CommunicationGate
from lab.phase2.gated_runtime import CHECKPOINT, REASON_REPLAY, GatedLab
from lab.phase2.labels import PUBLIC, SENSITIVE
from lab.phase2.workflow import REASON_EGRESS


def _gate_methods():
    return {n for n, _ in inspect.getmembers(CommunicationGate, predicate=inspect.isfunction)}


def test_public_transfer_through_gate_allowed():
    wf = GatedLab().workflow("wf-1")
    assert wf.public_write(AGENT_A, "P1").allow
    d = wf.request_transfer(AGENT_A, AGENT_B, "P1")
    assert d.allow is True
    assert d.policy == POLICY_INTERNAL
    assert d.message_id
    rec = wf.receive(AGENT_B, d.message_id)
    assert rec.allow is True
    assert rec.effective_label == PUBLIC


def test_sensitive_internal_transfer_allowed():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    assert d.allow is True
    assert d.effective_label == SENSITIVE


def test_sensitive_transfer_preserves_label():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    rec = wf.receive(AGENT_B, d.message_id)
    assert rec.effective_label == SENSITIVE
    assert wf.envelopes["C1"].origin == CUSTOMERS


def test_gate_does_not_receive_payload_content():
    lab = GatedLab()
    wf = lab.workflow()
    wf.customer_read(AGENT_A, "C1")
    wf.request_transfer(AGENT_A, AGENT_B, "C1")
    sig = inspect.signature(CommunicationGate.evaluate_transfer)
    assert "payload" not in sig.parameters
    for entry in lab.gate.decisions:
        assert "payload" not in entry
        assert "CUSTOMER_001" not in str(entry)
    assert "CUSTOMER_001" == wf.payloads["C1"]


def test_agent_cannot_forge_public_label():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1", label=PUBLIC, claimed_label=PUBLIC)
    assert d.effective_label == SENSITIVE
    wf.receive(AGENT_B, d.message_id)
    assert wf.envelopes["C1"].label == SENSITIVE


def test_agent_cannot_forge_provenance():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    wf.request_transfer(AGENT_A, AGENT_B, "C1", origin="public", provenance=())
    assert wf.envelopes["C1"].origin == CUSTOMERS
    assert any("customer.read" in p for p in wf.envelopes["C1"].provenance)


def test_derived_message_cannot_launder_sensitive_label():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    m = wf.derive(AGENT_A, "M1", ["C1"])
    assert m.effective_label == SENSITIVE
    d = wf.request_transfer(AGENT_A, AGENT_B, "M1", label=PUBLIC)
    assert d.effective_label == SENSITIVE


def test_receiver_cannot_rewrap_sensitive_as_public():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    wf.receive(AGENT_B, d.message_id)
    w = wf.wrap(AGENT_B, "P1", "C1", claimed_label=PUBLIC)
    assert w.effective_label == SENSITIVE


def test_direct_agent_to_agent_bypass_impossible():
    wf = GatedLab().workflow()
    assert not hasattr(wf, "workflow_send")
    assert not hasattr(wf, "deliver_direct")
    assert not hasattr(wf, "send_direct")
    wf.customer_read(AGENT_A, "C1")
    assert "C1" not in wf.holdings[AGENT_B]


def test_gate_has_no_repo_write_interface():
    assert not hasattr(CommunicationGate, "write_repo")
    assert not hasattr(CommunicationGate, "write")


def test_gate_has_no_filesystem_interface():
    assert not hasattr(CommunicationGate, "open")
    assert not hasattr(CommunicationGate, "write_file")


def test_gate_has_no_network_interface():
    assert not hasattr(CommunicationGate, "external_send")
    assert not hasattr(CommunicationGate, "connect")


def test_gate_has_no_tool_execution_interface():
    assert not hasattr(CommunicationGate, "execute")
    assert not hasattr(CommunicationGate, "run_tool")


def test_gate_has_no_payload_read_interface():
    assert not hasattr(CommunicationGate, "read_payload")
    assert "payload" not in inspect.signature(CommunicationGate.evaluate_transfer).parameters


def test_gate_cannot_mint_authority():
    assert not hasattr(CommunicationGate, "grant")
    assert not hasattr(CommunicationGate, "mint_authority")
    assert not hasattr(CommunicationGate, "delegate")
    names = _gate_methods()
    assert names <= {"__init__", "evaluate_transfer", "_record"}


def test_value_id_payload_substitution_blocked():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    wf.public_write(AGENT_A, "P1", "hello world")
    d = wf.request_transfer(AGENT_A, AGENT_B, "P1")
    wf.receive(AGENT_B, d.message_id)
    assert wf.payloads["P1"] == "hello world"
    assert wf.payloads["C1"] == "CUSTOMER_001"
    assert wf.envelopes["P1"].label == PUBLIC
    assert wf.envelopes["C1"].label == SENSITIVE
    assert not hasattr(wf, "rebind_payload")
    assert not hasattr(wf, "set_payload")


def test_cross_workflow_reference_blocked():
    lab = GatedLab()
    w1 = lab.workflow("W1")
    w2 = lab.workflow("W2")
    w1.customer_read(AGENT_A, "C1")
    w2.public_write(AGENT_B, "P1")
    d = w2.request_transfer(AGENT_A, AGENT_B, "C1")
    assert d.allow is False
    assert d.reason == REASON_CROSS_WORKFLOW
    assert "C1" not in w2.holdings[AGENT_B]


def test_replayed_message_blocked():
    wf = GatedLab().workflow()
    wf.public_write(AGENT_A, "P1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "P1")
    assert wf.receive(AGENT_B, d.message_id).allow is True
    replay = wf.receive(AGENT_B, d.message_id)
    assert replay.allow is False
    assert replay.reason == REASON_REPLAY


def test_successful_transfer_records_checkpoint():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    assert any(CHECKPOINT in p for p in wf.envelopes["C1"].provenance)
    assert d.message_id in "".join(wf.envelopes["C1"].provenance)


def test_gate_does_not_replace_original_origin():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    wf.request_transfer(AGENT_A, AGENT_B, "C1")
    assert wf.envelopes["C1"].origin == CUSTOMERS
    assert CHECKPOINT not in wf.envelopes["C1"].origin


def test_sensitive_data_received_by_b_still_blocked_at_external_egress():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "C1")
    wf.receive(AGENT_B, d.message_id)
    eg = wf.external_send(AGENT_B, "C1")
    assert eg.allow is False
    assert eg.reason == REASON_EGRESS
    assert wf.external == []


def test_public_data_received_by_b_can_egress():
    wf = GatedLab().workflow()
    wf.public_write(AGENT_A, "H1")
    d = wf.request_transfer(AGENT_A, AGENT_B, "H1")
    wf.receive(AGENT_B, d.message_id)
    eg = wf.external_send(AGENT_B, "H1")
    assert eg.allow is True
    assert "H1" in wf.external


def test_denied_transfer_does_not_mutate_receiver_state():
    wf = GatedLab().workflow()
    snap_h = {a: set(v) for a, v in wf.holdings.items()}
    snap_i = {a: dict(v) for a, v in wf.inbox.items()}
    d = wf.request_transfer(AGENT_A, AGENT_B, "missing")
    assert d.allow is False
    assert wf.holdings == snap_h
    assert wf.inbox == snap_i


def test_denied_transfer_does_not_mutate_payload_state():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    payloads = dict(wf.payloads)
    wf.request_transfer(AGENT_A, AGENT_B, "nope")
    assert wf.payloads == payloads


def test_legitimate_multi_message_workflow_completes():
    wf = GatedLab().workflow()
    wf.public_write(AGENT_A, "H1")
    wf.public_write(AGENT_B, "H2")
    d1 = wf.request_transfer(AGENT_A, AGENT_B, "H1")
    d2 = wf.request_transfer(AGENT_B, AGENT_A, "H2")
    assert wf.receive(AGENT_B, d1.message_id).allow
    assert wf.receive(AGENT_A, d2.message_id).allow
    assert wf.external_send(AGENT_B, "H1").allow


def test_wrapper_composition_through_gate_blocked_at_egress():
    wf = GatedLab().workflow()
    wf.customer_read(AGENT_A, "C1")
    wf.derive(AGENT_A, "D1", ["C1"])
    d = wf.request_transfer(AGENT_A, AGENT_B, "D1")
    wf.receive(AGENT_B, d.message_id)
    wf.derive(AGENT_B, "D2", ["D1"])
    wf.wrap(AGENT_B, "P1", "D2", claimed_label=PUBLIC)
    eg = wf.external_send(AGENT_B, "P1")
    assert eg.allow is False
    assert wf.attempts[-1]["path"] == ["C1", "D1", "D2", "P1"]
    assert wf.attempts[-1]["sensitive_origin"] == CUSTOMERS
    assert "CUSTOMER_001" not in str(wf.attempts[-1])
    assert wf.external == []


def test_public_payload_equal_to_customer_string_is_not_dlp():
    wf = GatedLab().workflow()
    wf.public_write(AGENT_B, "X1", payload="CUSTOMER_001")
    assert wf.envelopes["X1"].label == PUBLIC
    assert wf.external_send(AGENT_B, "X1").allow is True


def test_b_to_a_public_allowed():
    wf = GatedLab().workflow()
    wf.public_write(AGENT_B, "H1")
    d = wf.request_transfer(AGENT_B, AGENT_A, "H1")
    assert d.allow is True
    assert wf.receive(AGENT_A, d.message_id).allow
