"""Trusted runtime for Experiment 02. Owns labels, payloads, and transfer commit."""

from __future__ import annotations

from typing import Any

from lab.phase2.authority import (
    AGENT_A,
    AGENT_B,
    COPY,
    CUSTOMER_READ,
    CUSTOMERS,
    DERIVE,
    EXTERNAL,
    EXTERNAL_SEND,
    PUBLIC_WRITE,
    WORKFLOW_MSG,
    WRAP,
    authority_ok,
    known_actor,
)
from lab.phase2.communication_gate import (
    REASON_ACTOR,
    CommunicationGate,
    GateDecision,
    SecurityEnvelope,
)
from lab.phase2.labels import PUBLIC, SENSITIVE, join_labels
from lab.phase2.values import merge_provenance
from lab.phase2.workflow import (
    REASON_AUTHORITY,
    REASON_COLLISION,
    REASON_EGRESS,
    REASON_EMPTY,
    REASON_HOLDING,
    REASON_INBOX,
)

REASON_REPLAY = "REPLAY"
CHECKPOINT = "CommunicationGate"


class _View:
    def __init__(self, lab: GatedLab) -> None:
        self._lab = lab

    def get_envelope(self, workflow_id: str, value_id: str) -> SecurityEnvelope | None:
        wf = self._lab.workflows.get(workflow_id)
        if wf is None:
            return None
        return wf.envelopes.get(value_id)

    def sender_holds(self, workflow_id: str, sender: str, value_id: str) -> bool:
        wf = self._lab.workflows.get(workflow_id)
        if wf is None:
            return False
        bucket = wf.holdings.get(sender)
        if bucket is None:
            return False
        return value_id in bucket

    def value_in_other_workflow(self, workflow_id: str, value_id: str) -> bool:
        for wid, wf in self._lab.workflows.items():
            if wid != workflow_id and value_id in wf.envelopes:
                return True
        return False


class GatedLab:
    def __init__(self) -> None:
        self.gate = CommunicationGate()
        self.workflows: dict[str, GatedWorkflow] = {}
        self._seq = 0

    def workflow(self, workflow_id: str = "wf-1") -> GatedWorkflow:
        if workflow_id not in self.workflows:
            self.workflows[workflow_id] = GatedWorkflow(self, workflow_id)
        return self.workflows[workflow_id]

    def _next_message_id(self) -> str:
        self._seq += 1
        return f"m-{self._seq}"


class GatedWorkflow:
    def __init__(self, lab: GatedLab, workflow_id: str) -> None:
        self.lab = lab
        self.workflow_id = workflow_id
        self.envelopes: dict[str, SecurityEnvelope] = {}
        self.payloads: dict[str, str] = {}
        self.holdings: dict[str, set[str]] = {AGENT_A: set(), AGENT_B: set()}
        self.inbox: dict[str, dict[str, str]] = {AGENT_A: {}, AGENT_B: {}}
        self.consumed: set[str] = set()
        self.external: list[str] = []
        self.attempts: list[dict[str, Any]] = []

    def customer_read(self, actor: str, value_id: str = "C1") -> GateDecision:
        if not known_actor(actor):
            return GateDecision(False, REASON_ACTOR, actor, actor, self.workflow_id, value_id)
        if not authority_ok(actor, CUSTOMER_READ, CUSTOMERS):
            return GateDecision(False, REASON_AUTHORITY, actor, actor, self.workflow_id, value_id)
        env = SecurityEnvelope(
            self.workflow_id, value_id, SENSITIVE, CUSTOMERS, (), (f"{actor}:{CUSTOMER_READ}",)
        )
        if not self._put(actor, env, "CUSTOMER_001"):
            return GateDecision(False, REASON_COLLISION, actor, actor, self.workflow_id, value_id)
        return GateDecision(True, None, actor, actor, self.workflow_id, value_id, SENSITIVE)

    def public_write(self, actor: str, value_id: str, payload: str = "hello world") -> GateDecision:
        if not known_actor(actor):
            return GateDecision(False, REASON_ACTOR, actor, actor, self.workflow_id, value_id)
        if not authority_ok(actor, PUBLIC_WRITE, WORKFLOW_MSG):
            return GateDecision(False, REASON_AUTHORITY, actor, actor, self.workflow_id, value_id)
        env = SecurityEnvelope(
            self.workflow_id, value_id, PUBLIC, WORKFLOW_MSG, (), (f"{actor}:{PUBLIC_WRITE}",)
        )
        if not self._put(actor, env, payload):
            return GateDecision(False, REASON_COLLISION, actor, actor, self.workflow_id, value_id)
        return GateDecision(True, None, actor, actor, self.workflow_id, value_id, PUBLIC)

    def copy(self, actor: str, src_id: str, dst_id: str) -> GateDecision:
        return self._transform(actor, COPY, dst_id, (src_id,))

    def derive(self, actor: str, dst_id: str, from_ids: list[str]) -> GateDecision:
        return self._transform(actor, DERIVE, dst_id, tuple(from_ids))

    def wrap(
        self, actor: str, dst_id: str, src_id: str, claimed_label: str = PUBLIC
    ) -> GateDecision:
        _ = claimed_label
        return self._transform(actor, WRAP, dst_id, (src_id,))

    def request_transfer(
        self, sender: str, receiver: str, value_id: str, **claimed: object
    ) -> GateDecision:
        _ = claimed
        if not known_actor(sender) or not known_actor(receiver):
            return GateDecision(False, REASON_ACTOR, sender, receiver, self.workflow_id, value_id)
        raw = self.lab.gate.evaluate_transfer(
            _View(self.lab), self.workflow_id, sender, receiver, value_id
        )
        if not raw.allow:
            return raw
        if receiver not in self.inbox:
            return GateDecision(False, REASON_ACTOR, sender, receiver, self.workflow_id, value_id)
        message_id = self.lab._next_message_id()
        env = self.envelopes[value_id]
        checkpoint = env.provenance + (f"{sender}->{CHECKPOINT}->{receiver}:{message_id}",)
        updated = SecurityEnvelope(
            env.workflow_id, env.value_id, env.label, env.origin, env.derived_from, checkpoint
        )
        if (
            updated.label != env.label
            or updated.origin != env.origin
            or updated.derived_from != env.derived_from
        ):
            return GateDecision(
                False, REASON_COLLISION, sender, receiver, self.workflow_id, value_id
            )
        self.envelopes[value_id] = updated
        self.inbox[receiver][message_id] = value_id
        return GateDecision(
            True,
            None,
            sender,
            receiver,
            self.workflow_id,
            value_id,
            raw.effective_label,
            raw.policy,
            message_id,
        )

    def receive(self, actor: str, message_id: str) -> GateDecision:
        if not known_actor(actor):
            return GateDecision(False, REASON_ACTOR, actor, actor, self.workflow_id, "")
        if message_id in self.consumed:
            return GateDecision(False, REASON_REPLAY, actor, actor, self.workflow_id, "")
        value_id = self.inbox[actor].get(message_id)
        if value_id is None:
            return GateDecision(False, REASON_INBOX, actor, actor, self.workflow_id, "")
        self.consumed.add(message_id)
        del self.inbox[actor][message_id]
        self.holdings[actor].add(value_id)
        env = self.envelopes[value_id]
        return GateDecision(
            True, None, actor, actor, self.workflow_id, value_id, env.label, message_id=message_id
        )

    def external_send(self, actor: str, value_id: str) -> GateDecision:
        if not known_actor(actor):
            return GateDecision(False, REASON_ACTOR, actor, actor, self.workflow_id, value_id)
        auth = authority_ok(actor, EXTERNAL_SEND, EXTERNAL)
        if value_id not in self.holdings[actor]:
            return GateDecision(False, REASON_HOLDING, actor, actor, self.workflow_id, value_id)
        env = self.envelopes[value_id]
        sensitive = self._depends_on_sensitive(env)
        flow_ok = not sensitive
        reason = None if (auth and flow_ok) else (REASON_AUTHORITY if not auth else REASON_EGRESS)
        expl: dict[str, Any] = {
            "decision": "ALLOW" if (auth and flow_ok) else "DENY",
            "authority_ok": auth,
            "flow_ok": flow_ok,
            "reason": reason,
            "value_id": value_id,
            "sensitive_origin": CUSTOMERS if sensitive else None,
            "path": self._path(env) if sensitive else [],
        }
        self.attempts.append(expl)
        if auth and flow_ok:
            self.external.append(value_id)
            return GateDecision(True, None, actor, actor, self.workflow_id, value_id, env.label)
        return GateDecision(
            False,
            reason,
            actor,
            actor,
            self.workflow_id,
            value_id,
            env.label,
        )

    def _transform(
        self, actor: str, action: str, dst_id: str, from_ids: tuple[str, ...]
    ) -> GateDecision:
        if not known_actor(actor):
            return GateDecision(False, REASON_ACTOR, actor, actor, self.workflow_id, dst_id)
        if not authority_ok(actor, action, WORKFLOW_MSG):
            return GateDecision(False, REASON_AUTHORITY, actor, actor, self.workflow_id, dst_id)
        if not from_ids:
            return GateDecision(False, REASON_EMPTY, actor, actor, self.workflow_id, dst_id)
        inputs = []
        for src in from_ids:
            if src not in self.holdings[actor]:
                return GateDecision(False, REASON_HOLDING, actor, actor, self.workflow_id, dst_id)
            inputs.append(self.envelopes[src])
        label = join_labels([e.label for e in inputs])
        origin = next((e.origin for e in inputs if e.label == SENSITIVE), inputs[0].origin)
        env = SecurityEnvelope(
            self.workflow_id,
            dst_id,
            label,
            origin,
            from_ids,
            tuple(p for e in inputs for p in e.provenance) + (f"{actor}:{action}:{dst_id}",),
        )
        if not self._put(actor, env, "derived"):
            return GateDecision(False, REASON_COLLISION, actor, actor, self.workflow_id, dst_id)
        return GateDecision(True, None, actor, actor, self.workflow_id, dst_id, label)

    def _put(self, actor: str, env: SecurityEnvelope, payload: str) -> bool:
        if actor not in self.holdings:
            return False
        existing = self.envelopes.get(env.value_id)
        if existing is not None:
            old_payload = self.payloads.get(env.value_id)
            if (
                existing.label != env.label
                or existing.origin != env.origin
                or existing.derived_from != env.derived_from
                or old_payload != payload
            ):
                return False
            env = SecurityEnvelope(
                env.workflow_id,
                env.value_id,
                env.label,
                env.origin,
                env.derived_from,
                merge_provenance(existing.provenance, env.provenance),
            )
        self.envelopes[env.value_id] = env
        self.payloads[env.value_id] = payload
        self.holdings[actor].add(env.value_id)
        return True

    def _depends_on_sensitive(self, env: SecurityEnvelope) -> bool:
        if env.label == SENSITIVE or env.origin == CUSTOMERS:
            return True
        seen: set[str] = set()
        stack = [env.value_id]
        while stack:
            vid = stack.pop()
            if vid in seen:
                continue
            seen.add(vid)
            node = self.envelopes.get(vid)
            if node is None:
                continue
            if node.label == SENSITIVE or node.origin == CUSTOMERS:
                return True
            stack.extend(node.derived_from)
        return False

    def _path(self, env: SecurityEnvelope) -> list[str]:
        for parent in env.derived_from:
            node = self.envelopes.get(parent)
            if node and self._depends_on_sensitive(node):
                return self._path(node) + [env.value_id]
        return [env.value_id]
