"""Finite consistency checks over minimized producer claims, never enforcement.

References locate selected evidence; neither a matching reference nor a hash proves
identity, effect, a granted capability or project acceptance.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agent_authority.workflow import WorkflowClaim

FINDINGS_SCHEMA = "agent-authority-workflow-findings-v1"
MAX_CLAIMS = 10_000
RETURN_TYPES = frozenset({"return.received", "return.reviewed"})
RESULT_TYPES = frozenset(
    {
        "task.completed",
        "task.delivered",
        "return.received",
        "job.completed",
        "work.finished",
        "design.delivered",
    }
)
REVISION_FIELDS = ("handoff_revision", "source_revision", "task_revision")
BINDING_FIELDS = (
    "task_id",
    "original_task_id",
    "bridge_task_id",
    "run_id",
    "recipient_id",
    "principal_ref",
    "operator_scope",
    "request_hash",
    "source_hash",
)


def _metadata(claim: WorkflowClaim) -> dict[str, str | int]:
    return dict(claim.binding)


def _scope(
    claim: WorkflowClaim, *, handoff: bool = False, control: bool = False
) -> tuple[Any, ...] | None:
    data = _metadata(claim)
    keys = (
        ("project_id", "workflow_id")
        + (("handoff_id",) if handoff else ())
        + (("control_ref",) if control else ())
    )
    if any(key not in data for key in keys):
        return None
    return (claim.source_tool, claim.source_id, *(data[key] for key in keys))


def _number(value: str | int) -> int:
    if type(value) is not int:
        raise ValueError("unvalidated workflow integer")
    return value


def _reference(claim: WorkflowClaim) -> dict[str, str]:
    return {
        "source_tool": claim.source_tool,
        "source_id": claim.source_id,
        "event_id": claim.event_id,
        "entry_id": claim.entry_id,
        "record_sha256": claim.record_sha256,
        "file_sha256": claim.file_sha256,
    }


class _Analysis:
    def __init__(self, limit: int) -> None:
        self.limit = limit
        self.findings: list[dict[str, Any]] = []
        self.counts: Counter[str] = Counter()
        self.rules: dict[str, Counter[str]] = defaultdict(Counter)

    def emit(
        self,
        code: str,
        rule: str,
        claim: WorkflowClaim,
        *,
        related: WorkflowClaim | None = None,
        fields: tuple[str, ...] = (),
        conflict: bool = False,
    ) -> None:
        classification = "reported_contradiction" if conflict else "missing_evidence"
        self.counts[classification] += 1
        self.rules[rule][classification] += 1
        if len(self.findings) >= self.limit:
            return
        refs = [_reference(item) for item in (claim, related) if item is not None]
        stable_refs = [
            {key: value for key, value in ref.items() if key != "file_sha256"} for ref in refs
        ]
        stable = json.dumps([code, stable_refs, fields], sort_keys=True, separators=(",", ":"))
        binding = _metadata(claim)
        self.findings.append(
            {
                "finding_id": "finding-" + hashlib.sha256(stable.encode()).hexdigest()[:32],
                "rule_id": rule,
                "code": code,
                "classification": classification,
                "severity": "warning" if conflict else "unknown",
                "entry_id": claim.entry_id,
                "evidence_refs": refs,
                "reported_scope": {
                    key: binding[key]
                    for key in (
                        "project_id",
                        "workflow_id",
                        "task_id",
                        "original_task_id",
                        "bridge_task_id",
                        "handoff_id",
                        "run_id",
                        "attempt_id",
                        "control_ref",
                    )
                    if key in binding
                },
                "assessment_scope": "producer_claim_consistency",
                "fields": list(fields),
                "identity_authenticated": False,
                "actual_violation_verified": False,
            }
        )

    def return_checks(self, claim: WorkflowClaim, bound: WorkflowClaim | None) -> None:
        if bound is None:
            self.emit("workflow_return_binding_unknown", "return_binding", claim)
            self.emit("workflow_revision_unknown", "revision", claim)
            return
        values, basis = _metadata(claim), _metadata(bound)
        revisions = tuple(key for key in REVISION_FIELDS if key in basis)
        absent = tuple(key for key in revisions if key not in values)
        if not revisions or absent:
            self.emit("workflow_revision_unknown", "revision", claim, related=bound, fields=absent)
        comparable = tuple(key for key in revisions if key in values)
        if comparable:
            self.rules["revision"]["compared_pairs"] += 1
        stale = tuple(key for key in comparable if _number(values[key]) < _number(basis[key]))
        advanced = tuple(key for key in comparable if _number(values[key]) > _number(basis[key]))
        if stale:
            self.emit(
                "workflow_revision_stale",
                "revision",
                claim,
                related=bound,
                fields=stale,
                conflict=True,
            )
        if advanced:
            self.emit(
                "workflow_revision_mismatch",
                "revision",
                claim,
                related=bound,
                fields=advanced,
                conflict=True,
            )
        required = tuple(
            sorted(
                {"task_id", "run_id", "recipient_id"}
                | {key for key in BINDING_FIELDS if key in basis}
            )
        )
        absent = tuple(key for key in required if key not in values or key not in basis)
        if absent:
            self.emit(
                "workflow_return_binding_unknown",
                "return_binding",
                claim,
                related=bound,
                fields=absent,
            )
        compared = tuple(key for key in BINDING_FIELDS if key in values and key in basis)
        if compared:
            self.rules["return_binding"]["compared_pairs"] += 1
        mismatch = tuple(key for key in compared if values[key] != basis[key])
        if mismatch:
            self.emit(
                "workflow_return_binding_mismatch",
                "return_binding",
                claim,
                related=bound,
                fields=mismatch,
                conflict=True,
            )


def analyze_workflow_claims(
    claims: tuple[WorkflowClaim, ...], limit: int = 100, *, complete_selected_read: bool = False
) -> dict[str, Any]:
    """Bounded read-only rules. Empty/clean findings are never a safety/completion proof.

    Ordinals and gate sequence numbers are meaningful only within an identical
    selected producer and explicit workflow/controller scope. Explicit event links
    are preferred; an implicit unique binding is used only for a complete slice.
    """
    if type(limit) is not int or not 1 <= limit <= 100 or len(claims) > MAX_CLAIMS:
        raise ValueError("invalid workflow analysis bound")
    if type(complete_selected_read) is not bool:
        raise ValueError("invalid read completeness")
    analysis = _Analysis(limit)
    by_event: dict[tuple[str, str, str], list[WorkflowClaim]] = defaultdict(list)
    bindings: dict[tuple[Any, ...], list[WorkflowClaim]] = defaultdict(list)
    stops: dict[tuple[Any, ...], list[WorkflowClaim]] = defaultdict(list)
    ordinal_counts = Counter((c.source_tool, c.source_id, c.producer_ordinal) for c in claims)
    for claim in claims:
        by_event[claim.source_tool, claim.source_id, claim.event_id].append(claim)
        if claim.event_type == "handoff.bound" and (key := _scope(claim, handoff=True)) is not None:
            bindings[key].append(claim)
        if (
            claim.event_type == "control.stop_effective"
            and (key := _scope(claim, control=True)) is not None
        ):
            stops[key].append(claim)
    # The earliest declared durable barrier is sufficient, not an O(n^2) scan.
    barriers: dict[tuple[Any, ...], WorkflowClaim] = {}
    for key, values in stops.items():
        unambiguous = [
            c
            for c in values
            if _metadata(c).get("stop_state") == "effective" and "barrier_seq" in _metadata(c)
        ]
        if unambiguous:
            barriers[key] = min(unambiguous, key=lambda c: _number(_metadata(c)["barrier_seq"]))

    def linked(claim: WorkflowClaim, field: str) -> WorkflowClaim | None:
        value = _metadata(claim).get(field)
        matches = by_event.get((claim.source_tool, claim.source_id, str(value)), [])
        return matches[0] if value is not None and len(matches) == 1 else None

    def ordered_pair(before: WorkflowClaim, after: WorkflowClaim) -> bool:
        return (
            before.producer_ordinal is not None
            and after.producer_ordinal is not None
            and before.producer_ordinal < after.producer_ordinal
            and ordinal_counts[before.source_tool, before.source_id, before.producer_ordinal] == 1
            and ordinal_counts[after.source_tool, after.source_id, after.producer_ordinal] == 1
        )

    for claim in claims:
        data = _metadata(claim)
        if claim.event_type in RETURN_TYPES:
            key = _scope(claim, handoff=True)
            bound = linked(claim, "binding_event_id")
            if "binding_event_id" not in data and complete_selected_read and key is not None:
                matches = bindings.get(key, [])
                bound = matches[0] if len(matches) == 1 else None
            if bound is not None and (
                bound.event_type != "handoff.bound"
                or key is None
                or _scope(bound, handoff=True) != key
                or not ordered_pair(bound, claim)
            ):
                bound = None
            analysis.return_checks(claim, bound)
        if claim.event_type in RESULT_TYPES:
            analysis.rules["artifact_evidence"]["reported_results"] += 1
            if "artifact_ref" not in data:
                analysis.emit(
                    "workflow_result_artifact_missing",
                    "artifact_evidence",
                    claim,
                    fields=("artifact_ref",),
                )
            else:
                analysis.rules["artifact_evidence"]["reported_references_only"] += 1
        if claim.event_type == "dispatch.attempted":
            key = _scope(claim, control=True)
            gate = linked(claim, "gate_event_id")
            gate_data = _metadata(gate) if gate is not None else {}
            required = ("task_id", "attempt_id", "request_hash", "consumer_id", "actor_claim")
            gate_matches = (
                gate is not None
                and gate.event_type == "budget.reserved"
                and key is not None
                and _scope(gate, control=True) == key
                and ordered_pair(gate, claim)
                and all(field in data and data[field] == gate_data.get(field) for field in required)
            )
            if not gate_matches:
                analysis.emit(
                    "workflow_control_point_missing", "control_point", claim, related=gate
                )
            else:
                analysis.rules["control_point"]["matching_reported_references"] += 1
            stop = barriers.get(key) if key is not None else None
            if stop is None or "dispatch_seq" not in data:
                analysis.emit("workflow_stop_order_unknown", "stop_order", claim)
            else:
                analysis.rules["stop_order"]["compared_pairs"] += 1
                if _number(data["dispatch_seq"]) == _number(_metadata(stop)["barrier_seq"]):
                    analysis.emit("workflow_stop_order_unknown", "stop_order", claim, related=stop)
                elif _number(data["dispatch_seq"]) > _number(_metadata(stop)["barrier_seq"]):
                    analysis.emit(
                        "workflow_dispatch_after_stop",
                        "stop_order",
                        claim,
                        related=stop,
                        fields=("dispatch_seq", "barrier_seq"),
                        conflict=True,
                    )
    total = sum(analysis.counts.values())
    return {
        "schema_version": FINDINGS_SCHEMA,
        "assessment_scope": "producer_claim_consistency",
        "findings": analysis.findings,
        "counts": dict(analysis.counts),
        "rule_results": {key: dict(value) for key, value in sorted(analysis.rules.items())},
        "findings_omitted": total - len(analysis.findings),
        "claims_examined": len(claims),
        "selected_read_complete": complete_selected_read,
        "coverage_of_all_activity": "UNBEKANNT",
        "source_authenticated": False,
        "actual_violation_verified": False,
        "task_completion_proven": False,
        "gate_authorization_proven": False,
    }
