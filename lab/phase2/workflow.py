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
    WORKFLOW_RECEIVE,
    WORKFLOW_SEND,
    WRAP,
    authority_ok,
    known_actor,
)
from lab.phase2.labels import PUBLIC, SENSITIVE, join_labels
from lab.phase2.values import DataValue, Phase2Decision, merge_provenance, mint_conflicts

REASON_AUTHORITY = "AUTHORITY_DENIED"
REASON_HOLDING = "VALUE_NOT_HELD"
REASON_INBOX = "VALUE_NOT_IN_INBOX"
REASON_EGRESS = "SENSITIVE_EXTERNAL_EGRESS"
REASON_ACTOR = "UNKNOWN_ACTOR"
REASON_COLLISION = "VALUE_ID_COLLISION"
REASON_EMPTY = "EMPTY_TRANSFORM"


class Experiment:
    """One fake workflow. `ifc=False` is authority-only; `ifc=True` enforces FlowOK."""

    def __init__(self, *, ifc: bool) -> None:
        self.ifc = ifc
        self.holdings: dict[str, dict[str, DataValue]] = {AGENT_A: {}, AGENT_B: {}}
        self.inbox: dict[str, dict[str, DataValue]] = {AGENT_A: {}, AGENT_B: {}}
        self.catalog: dict[str, DataValue] = {}
        self.external: list[str] = []
        self.attempts: list[dict[str, Any]] = []

    def customer_read(self, actor: str, value_id: str = "C1") -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, CUSTOMER_READ, CUSTOMERS)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        value = DataValue(
            value_id=value_id,
            label=SENSITIVE,
            origin=CUSTOMERS,
            provenance=(f"{actor}:{CUSTOMER_READ}:{CUSTOMERS}",),
            payload="CUSTOMER_001",
        )
        return self._commit_hold(actor, value, auth)

    def public_write(
        self, actor: str, value_id: str, payload: str = "hello world"
    ) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, PUBLIC_WRITE, WORKFLOW_MSG)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        value = DataValue(
            value_id=value_id,
            label=PUBLIC,
            origin=WORKFLOW_MSG,
            provenance=(f"{actor}:{PUBLIC_WRITE}:{WORKFLOW_MSG}",),
            payload=payload,
        )
        return self._commit_hold(actor, value, auth)

    def copy(self, actor: str, src_id: str, dst_id: str) -> Phase2Decision:
        return self._transform(actor, COPY, dst_id, (src_id,))

    def derive(self, actor: str, dst_id: str, from_ids: list[str]) -> Phase2Decision:
        return self._transform(actor, DERIVE, dst_id, tuple(from_ids))

    def wrap(
        self, actor: str, dst_id: str, src_id: str, claimed_label: str = PUBLIC
    ) -> Phase2Decision:
        # claimed_label is ignored. Wrapping does not declassify.
        _ = claimed_label
        return self._transform(actor, WRAP, dst_id, (src_id,))

    def workflow_send(self, actor: str, value_id: str, to_actor: str) -> Phase2Decision:
        if not known_actor(actor) or not known_actor(to_actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, WORKFLOW_SEND, WORKFLOW_MSG)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        held = self.holdings[actor].get(value_id)
        if held is None:
            return self._deny(auth, True, REASON_HOLDING)
        transferred = DataValue(
            value_id=held.value_id,
            label=held.label,
            origin=held.origin,
            derived_from=held.derived_from,
            provenance=held.provenance + (f"{actor}:{WORKFLOW_SEND}:{to_actor}",),
            payload=held.payload,
        )
        if mint_conflicts(self.catalog.get(value_id), transferred):
            return self._deny(auth, True, REASON_COLLISION)
        self.catalog[transferred.value_id] = transferred
        self.inbox[to_actor][value_id] = transferred
        self.holdings[actor][value_id] = transferred
        return Phase2Decision(True, auth, True, None, value=transferred)

    def workflow_receive(self, actor: str, value_id: str) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, WORKFLOW_RECEIVE, WORKFLOW_MSG)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        incoming = self.inbox[actor].get(value_id)
        if incoming is None:
            return self._deny(auth, True, REASON_INBOX)
        received = DataValue(
            value_id=incoming.value_id,
            label=incoming.label,
            origin=incoming.origin,
            derived_from=incoming.derived_from,
            provenance=incoming.provenance + (f"{actor}:{WORKFLOW_RECEIVE}",),
            payload=incoming.payload,
        )
        if mint_conflicts(self.catalog.get(value_id), received):
            return self._deny(auth, True, REASON_COLLISION)
        self.catalog[value_id] = received
        self.holdings[actor][value_id] = received
        del self.inbox[actor][value_id]
        return Phase2Decision(True, auth, True, None, value=received)

    def external_send(self, actor: str, value_id: str) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, EXTERNAL_SEND, EXTERNAL)
        held = self.holdings[actor].get(value_id)
        if held is None:
            return self._deny(auth, True, REASON_HOLDING)
        sensitive = self._depends_on_sensitive(held)
        flow_ok = True if not self.ifc else (not sensitive)
        explanation = self._explain(held, auth, flow_ok)
        self.attempts.append(explanation)
        if auth and flow_ok:
            self.external.append(value_id)
            return Phase2Decision(True, True, True, None, explanation, held)
        if not auth:
            return Phase2Decision(False, False, flow_ok, REASON_AUTHORITY, explanation, held)
        return Phase2Decision(False, True, False, REASON_EGRESS, explanation, held)

    def _transform(
        self, actor: str, action: str, dst_id: str, from_ids: tuple[str, ...]
    ) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, action, WORKFLOW_MSG)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        if not from_ids:
            return self._deny(auth, True, REASON_EMPTY)
        inputs: list[DataValue] = []
        for src in from_ids:
            held = self.holdings[actor].get(src)
            if held is None:
                return self._deny(auth, True, REASON_HOLDING)
            inputs.append(held)
        label = join_labels([v.label for v in inputs])
        origin = next(
            (v.origin for v in inputs if v.label == SENSITIVE),
            inputs[0].origin if inputs else WORKFLOW_MSG,
        )
        value = DataValue(
            value_id=dst_id,
            label=label,
            origin=origin,
            derived_from=from_ids,
            provenance=tuple(e for v in inputs for e in v.provenance)
            + (f"{actor}:{action}:{dst_id}",),
            payload="derived",
        )
        return self._commit_hold(actor, value, auth)

    def _depends_on_sensitive(self, value: DataValue) -> bool:
        if value.label == SENSITIVE or value.origin == CUSTOMERS:
            return True
        seen: set[str] = set()
        stack = [value.value_id]
        while stack:
            vid = stack.pop()
            if vid in seen:
                continue
            seen.add(vid)
            node = self.catalog.get(vid)
            if node is None:
                continue
            if node.label == SENSITIVE or node.origin == CUSTOMERS:
                return True
            stack.extend(node.derived_from)
        return False

    def _path(self, value: DataValue) -> list[str]:
        for parent in value.derived_from:
            node = self.catalog.get(parent)
            if node and self._depends_on_sensitive(node):
                return self._path(node) + [value.value_id]
        return [value.value_id]

    def _explain(self, value: DataValue, auth: bool, flow_ok: bool) -> dict[str, Any]:
        origin, path = None, []
        if self._depends_on_sensitive(value):
            origin = CUSTOMERS
            path = self._path(value)
        return {
            "decision": "ALLOW" if (auth and flow_ok) else "DENY",
            "authority_ok": auth,
            "flow_ok": flow_ok,
            "reason": None
            if (auth and flow_ok)
            else (REASON_AUTHORITY if not auth else REASON_EGRESS),
            "value_id": value.value_id,
            "sensitive_origin": origin,
            "path": path,
        }

    def _commit_hold(self, actor: str, value: DataValue, auth: bool) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        existing = self.catalog.get(value.value_id)
        if mint_conflicts(existing, value):
            return self._deny(auth, True, REASON_COLLISION)
        if existing is not None:
            value = DataValue(
                value_id=value.value_id,
                label=value.label,
                origin=value.origin,
                derived_from=value.derived_from,
                provenance=merge_provenance(existing.provenance, value.provenance),
                payload=value.payload,
            )
        self.catalog[value.value_id] = value
        self.holdings[actor][value.value_id] = value
        return Phase2Decision(True, auth, True, None, value=value)

    def _deny(self, auth: bool, flow_ok: bool, reason: str) -> Phase2Decision:
        return Phase2Decision(False, auth, flow_ok, reason)
