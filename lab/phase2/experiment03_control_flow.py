"""Phase 2 Experiment 03: modeled control-flow leakage. Isolated from Exp 01/02."""

from __future__ import annotations

from typing import Any

from lab.phase2.authority import (
    AGENT_A,
    AGENT_B,
    CONTROL_DECIDE,
    COPY,
    CUSTOMER_READ,
    CUSTOMERS,
    DERIVE,
    EXTERNAL,
    EXTERNAL_SEND,
    PUBLIC_WRITE,
    STATE_READ,
    STATE_WRITE,
    WORKFLOW_MSG,
    WORKFLOW_STATE,
    WRAP,
    authority_ok,
    known_actor,
)
from lab.phase2.control_dependencies import CONTROL_ORIGIN, ControlDecision
from lab.phase2.labels import PUBLIC, SENSITIVE, join_labels
from lab.phase2.values import DataValue, Phase2Decision, merge_provenance, mint_conflicts

REASON_AUTHORITY = "AUTHORITY_DENIED"
REASON_HOLDING = "VALUE_NOT_HELD"
REASON_STATE = "VALUE_NOT_IN_WORKFLOW_STATE"
REASON_EGRESS = "SENSITIVE_EXTERNAL_EGRESS"
REASON_CONTROL = "SENSITIVE_CONTROL_DEPENDENCY_EGRESS"
REASON_ACTOR = "UNKNOWN_ACTOR"
REASON_COLLISION = "VALUE_ID_COLLISION"
REASON_EMPTY = "EMPTY_TRANSFORM"


class ImplicitFlowExperiment:
    """ifc: Experiment 01 FlowOK. control_deps: inherit taint via created_under."""

    def __init__(self, *, ifc: bool, control_deps: bool, workflow_id: str = "wf-03") -> None:
        self.ifc = ifc
        self.control_deps = control_deps
        self.workflow_id = workflow_id
        self.holdings: dict[str, dict[str, DataValue]] = {AGENT_A: {}, AGENT_B: {}}
        self.catalog: dict[str, DataValue] = {}
        self.workflow_state: dict[str, DataValue] = {}
        self.decisions: dict[str, ControlDecision] = {}
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
            payload="CUSTOMER_FLAG",
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

    def control_decide(self, actor: str, decision_id: str, depends_on: list[str]) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, CONTROL_DECIDE, WORKFLOW_STATE)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        inputs: list[DataValue] = []
        for src in depends_on:
            held = self.holdings[actor].get(src)
            if held is None:
                return self._deny(auth, True, REASON_HOLDING)
            inputs.append(held)
        label = join_labels([v.label for v in inputs])
        origin = next(
            (v.origin for v in inputs if v.label == SENSITIVE),
            CONTROL_ORIGIN,
        )
        value = DataValue(
            value_id=decision_id,
            label=label,
            origin=origin if label == SENSITIVE else CONTROL_ORIGIN,
            derived_from=tuple(depends_on),
            provenance=(f"{actor}:{CONTROL_DECIDE}:{decision_id}",),
            payload="",
        )
        if mint_conflicts(self.catalog.get(decision_id), value):
            return self._deny(auth, True, REASON_COLLISION)
        rec = ControlDecision(decision_id, tuple(depends_on), label, origin)
        committed = self._commit_hold(actor, value, auth)
        if committed.allow:
            self.decisions[decision_id] = rec
        return committed

    def state_write(
        self,
        actor: str,
        value_id: str,
        payload: str,
        created_under: str | None = None,
        claimed_label: str | None = None,
    ) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, STATE_WRITE, WORKFLOW_STATE)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        derived: tuple[str, ...] = ()
        label = PUBLIC
        origin = WORKFLOW_STATE
        if self.control_deps and created_under:
            rec = self.decisions.get(created_under)
            if rec is None:
                return self._deny(auth, True, REASON_HOLDING)
            derived = (created_under,)
            label = rec.label
            origin = rec.origin if rec.label == SENSITIVE else WORKFLOW_STATE
        _ = claimed_label  # ignored — no declassification
        value = DataValue(
            value_id=value_id,
            label=label,
            origin=origin,
            derived_from=derived,
            provenance=(f"{actor}:{STATE_WRITE}:{value_id}",),
            payload=payload,
        )
        if mint_conflicts(self.catalog.get(value_id), value):
            return self._deny(auth, True, REASON_COLLISION)
        self.workflow_state[value_id] = value
        return self._commit_hold(actor, value, auth)

    def state_read(self, actor: str, value_id: str) -> Phase2Decision:
        if not known_actor(actor):
            return self._deny(False, True, REASON_ACTOR)
        auth = authority_ok(actor, STATE_READ, WORKFLOW_STATE)
        if not auth:
            return self._deny(auth, True, REASON_AUTHORITY)
        incoming = self.workflow_state.get(value_id)
        if incoming is None:
            return self._deny(auth, True, REASON_STATE)
        received = DataValue(
            value_id=incoming.value_id,
            label=incoming.label,
            origin=incoming.origin,
            derived_from=incoming.derived_from,
            provenance=incoming.provenance + (f"{actor}:{STATE_READ}",),
            payload=incoming.payload,
        )
        return self._commit_hold(actor, value=received, auth=auth)

    def copy(self, actor: str, src_id: str, dst_id: str) -> Phase2Decision:
        return self._transform(actor, COPY, dst_id, (src_id,))

    def derive(self, actor: str, dst_id: str, from_ids: list[str]) -> Phase2Decision:
        return self._transform(actor, DERIVE, dst_id, tuple(from_ids))

    def wrap(
        self, actor: str, dst_id: str, src_id: str, claimed_label: str = PUBLIC
    ) -> Phase2Decision:
        _ = claimed_label
        return self._transform(actor, WRAP, dst_id, (src_id,))

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
        reason = REASON_CONTROL if self._has_control_dep(held) else REASON_EGRESS
        explanation["reason"] = reason
        explanation["decision"] = "DENY"
        return Phase2Decision(False, True, False, reason, explanation, held)

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
            payload=inputs[0].payload if inputs else "derived",
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

    def _has_control_dep(self, value: DataValue) -> bool:
        seen: set[str] = set()
        stack = [value.value_id]
        while stack:
            vid = stack.pop()
            if vid in seen:
                continue
            seen.add(vid)
            if vid in self.decisions:
                return True
            node = self.catalog.get(vid)
            if node is None:
                continue
            stack.extend(node.derived_from)
        return False

    def _path(self, value: DataValue) -> list[str]:
        for parent in value.derived_from:
            node = self.catalog.get(parent)
            if node and self._depends_on_sensitive(node):
                return self._path(node) + [value.value_id]
        return [value.value_id]

    def _control_id(self, value: DataValue) -> str | None:
        seen: set[str] = set()
        stack = [value.value_id]
        while stack:
            vid = stack.pop()
            if vid in seen:
                continue
            seen.add(vid)
            if vid in self.decisions:
                return vid
            node = self.catalog.get(vid)
            if node:
                stack.extend(node.derived_from)
        return None

    def _explain(self, value: DataValue, auth: bool, flow_ok: bool) -> dict[str, Any]:
        origin, path = None, []
        if self._depends_on_sensitive(value):
            origin = CUSTOMERS
            path = self._path(value)
        reason = None
        if not (auth and flow_ok):
            if not auth:
                reason = REASON_AUTHORITY
            elif self._has_control_dep(value):
                reason = REASON_CONTROL
            else:
                reason = REASON_EGRESS
        return {
            "decision": "ALLOW" if (auth and flow_ok) else "DENY",
            "authority_ok": auth,
            "flow_ok": flow_ok,
            "reason": reason,
            "value_id": value.value_id,
            "control_dependency": self._control_id(value),
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
