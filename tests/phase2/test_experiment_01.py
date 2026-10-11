"""Phase 2 Experiment 01. Does not modify Phase 1 tests."""

from lab.phase2.authority import AGENT_A, AGENT_B, CUSTOMERS
from lab.phase2.labels import PUBLIC, SENSITIVE
from lab.phase2.workflow import REASON_AUTHORITY, REASON_EGRESS, Experiment


def _attack(exp: Experiment) -> tuple:
    t1 = exp.customer_read(AGENT_A, "C1")
    t2 = exp.workflow_send(AGENT_A, "C1", AGENT_B)
    t3 = exp.workflow_receive(AGENT_B, "C1")
    t4 = exp.external_send(AGENT_B, "C1")
    return t1, t2, t3, t4


def test_authority_only_composition_attack_succeeds():
    exp = Experiment(ifc=False)
    t1, t2, t3, t4 = _attack(exp)
    assert t1.allow and t2.allow and t3.allow
    assert t4.allow is True
    assert t4.authority_ok is True
    assert "C1" in exp.external


def test_ifc_blocks_sensitive_composition_attack():
    exp = Experiment(ifc=True)
    t1, t2, t3, t4 = _attack(exp)
    assert t1.allow and t2.allow and t3.allow
    assert t4.allow is False
    assert t4.authority_ok is True
    assert t4.flow_ok is False
    assert t4.reason == REASON_EGRESS
    assert "C1" not in exp.external
    expl = t4.explanation
    assert expl["decision"] == "DENY"
    assert expl["authority_ok"] is True
    assert expl["flow_ok"] is False
    assert expl["reason"] == "SENSITIVE_EXTERNAL_EGRESS"
    assert expl["value_id"] == "C1"
    assert expl["sensitive_origin"] == CUSTOMERS
    assert expl["path"] == ["C1"]
    assert "CUSTOMER_001" not in str(expl)


def test_public_egress_allowed():
    for ifc in (False, True):
        exp = Experiment(ifc=ifc)
        w = exp.public_write(AGENT_B, "H1", "hello world")
        d = exp.external_send(AGENT_B, "H1")
        assert w.allow and d.allow, ifc
        assert "H1" in exp.external


def test_sensitive_internal_use_allowed():
    exp = Experiment(ifc=True)
    assert exp.customer_read(AGENT_A, "C1").allow
    assert exp.derive(AGENT_A, "D1", ["C1"]).allow
    assert exp.external == []


def test_sensitive_label_survives_transfer():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    exp.workflow_send(AGENT_A, "C1", AGENT_B)
    rec = exp.workflow_receive(AGENT_B, "C1")
    assert rec.value is not None
    assert rec.value.label == SENSITIVE
    assert rec.value.origin == CUSTOMERS


def test_sensitive_label_survives_copy():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    c = exp.copy(AGENT_A, "C1", "C1copy")
    assert c.value is not None and c.value.label == SENSITIVE


def test_sensitive_label_survives_derived_value():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    d = exp.derive(AGENT_A, "D1", ["C1"])
    assert d.value is not None and d.value.label == SENSITIVE


def test_mixed_public_sensitive_becomes_sensitive():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    exp.public_write(AGENT_A, "P0")
    m = exp.derive(AGENT_A, "M1", ["C1", "P0"])
    assert m.value is not None and m.value.label == SENSITIVE


def test_agent_b_cannot_strip_label():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    exp.workflow_send(AGENT_A, "C1", AGENT_B)
    exp.workflow_receive(AGENT_B, "C1")
    w = exp.wrap(AGENT_B, "P1", "C1", claimed_label=PUBLIC)
    assert w.value is not None and w.value.label == SENSITIVE
    d = exp.external_send(AGENT_B, "P1")
    assert d.allow is False and d.reason == REASON_EGRESS


def test_denied_egress_does_not_mutate_external_state():
    exp = Experiment(ifc=True)
    snap = list(exp.external)
    _attack(exp)
    assert exp.external == snap == []


def test_provenance_contains_original_sensitive_origin():
    exp = Experiment(ifc=True)
    _attack(exp)
    d = exp.attempts[-1]
    assert d["sensitive_origin"] == CUSTOMERS
    assert d["path"][0] == "C1"


def test_direct_agent_a_egress_denied_by_authority():
    exp = Experiment(ifc=True)
    exp.customer_read(AGENT_A, "C1")
    d = exp.external_send(AGENT_A, "C1")
    assert d.allow is False
    assert d.authority_ok is False
    assert d.reason == REASON_AUTHORITY
    assert exp.external == []


def test_agent_b_public_egress_allowed_by_authority_and_flow():
    exp = Experiment(ifc=True)
    exp.public_write(AGENT_B, "H1")
    d = exp.external_send(AGENT_B, "H1")
    assert d.allow is True
    assert d.authority_ok is True
    assert d.flow_ok is True


def test_cross_agent_attack_requires_global_workflow_context():
    src = Experiment(ifc=True)
    src.customer_read(AGENT_A, "C1")
    other = Experiment(ifc=True)
    d = other.external_send(AGENT_B, "C1")
    assert d.allow is False
    assert "C1" not in other.external
    src.workflow_send(AGENT_A, "C1", AGENT_B)
    rec = src.workflow_receive(AGENT_B, "C1")
    assert rec.value is not None and rec.value.label == SENSITIVE


def test_legitimate_multi_agent_workflow_completes():
    exp = Experiment(ifc=True)
    assert exp.public_write(AGENT_A, "H1", "hello world").allow
    assert exp.workflow_send(AGENT_A, "H1", AGENT_B).allow
    assert exp.workflow_receive(AGENT_B, "H1").allow
    d = exp.external_send(AGENT_B, "H1")
    assert d.allow is True
    assert "H1" in exp.external


def test_wrapper_laundering_multi_hop_blocked():
    exp = Experiment(ifc=True)
    assert exp.customer_read(AGENT_A, "C1").allow
    assert exp.derive(AGENT_A, "D1", ["C1"]).allow
    assert exp.derive(AGENT_A, "D2", ["D1"]).allow
    assert exp.workflow_send(AGENT_A, "D2", AGENT_B).allow
    assert exp.workflow_receive(AGENT_B, "D2").allow
    wrap = exp.wrap(AGENT_B, "P1", "D2", claimed_label=PUBLIC)
    assert wrap.value is not None and wrap.value.label == SENSITIVE
    d = exp.external_send(AGENT_B, "P1")
    assert d.allow is False
    assert d.authority_ok is True
    assert d.flow_ok is False
    assert d.explanation["path"] == ["C1", "D1", "D2", "P1"]
    assert d.explanation["sensitive_origin"] == CUSTOMERS
    assert "CUSTOMER_001" not in str(d.explanation)
    assert exp.external == []


def test_payload_string_is_not_inspected():
    """PUBLIC value whose payload happens to equal CUSTOMER_001 is not DLP-matched."""
    exp = Experiment(ifc=True)
    exp.public_write(AGENT_B, "X1", payload="CUSTOMER_001")
    d = exp.external_send(AGENT_B, "X1")
    assert d.allow is True
    assert "X1" in exp.external


def test_b_cannot_read_customers():
    d = Experiment(ifc=True).customer_read(AGENT_B, "C1")
    assert d.allow is False and d.reason == REASON_AUTHORITY


def test_honesty_not_removing_b_network():
    exp = Experiment(ifc=True)
    exp.public_write(AGENT_B, "H1")
    assert exp.external_send(AGENT_B, "H1").allow is True


def test_honesty_not_preventing_a_read():
    assert Experiment(ifc=True).customer_read(AGENT_A, "C1").allow is True
