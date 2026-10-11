"""Metadata-only Communication Gate. Not an agent. Experiment 02."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from lab.phase2.authority import known_actor

POLICY_INTERNAL = "INTERNAL_TRANSFER_ALLOWED"
REASON_CROSS_WORKFLOW = "CROSS_WORKFLOW_REFERENCE"
REASON_NOT_HELD = "VALUE_NOT_HELD"
REASON_NOT_FOUND = "VALUE_NOT_FOUND"
REASON_ACTOR = "UNKNOWN_ACTOR"


@dataclass(frozen=True)
class SecurityEnvelope:
    workflow_id: str
    value_id: str
    label: str
    origin: str
    derived_from: tuple[str, ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True)
class GateDecision:
    allow: bool
    reason: str | None
    sender: str
    receiver: str
    workflow_id: str
    value_id: str
    effective_label: str | None = None
    policy: str | None = None
    message_id: str | None = None


class MetadataView(Protocol):
    def get_envelope(self, workflow_id: str, value_id: str) -> SecurityEnvelope | None: ...
    def sender_holds(self, workflow_id: str, sender: str, value_id: str) -> bool: ...
    def value_in_other_workflow(self, workflow_id: str, value_id: str) -> bool: ...


class CommunicationGate:
    """Reference monitor: metadata in, ALLOW/DENY out. No payload, tools, or writes."""

    def __init__(self) -> None:
        self.decisions: list[dict[str, Any]] = []

    def evaluate_transfer(
        self,
        meta: MetadataView,
        workflow_id: str,
        sender: str,
        receiver: str,
        value_id: str,
    ) -> GateDecision:
        if not known_actor(sender) or not known_actor(receiver):
            return self._record(
                GateDecision(False, REASON_ACTOR, sender, receiver, workflow_id, value_id)
            )
        env = meta.get_envelope(workflow_id, value_id)
        if env is None:
            reason = (
                REASON_CROSS_WORKFLOW
                if meta.value_in_other_workflow(workflow_id, value_id)
                else REASON_NOT_FOUND
            )
            return self._record(
                GateDecision(False, reason, sender, receiver, workflow_id, value_id)
            )
        if not meta.sender_holds(workflow_id, sender, value_id):
            return self._record(
                GateDecision(
                    False, REASON_NOT_HELD, sender, receiver, workflow_id, value_id, env.label
                )
            )
        return self._record(
            GateDecision(
                True,
                None,
                sender,
                receiver,
                workflow_id,
                value_id,
                env.label,
                POLICY_INTERNAL,
            )
        )

    def _record(self, decision: GateDecision) -> GateDecision:
        self.decisions.append(
            {
                "decision": "ALLOW" if decision.allow else "DENY",
                "sender": decision.sender,
                "receiver": decision.receiver,
                "workflow_id": decision.workflow_id,
                "value_id": decision.value_id,
                "effective_label": decision.effective_label,
                "policy": decision.policy,
                "reason": decision.reason,
            }
        )
        return decision
