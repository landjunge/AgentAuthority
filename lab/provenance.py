from __future__ import annotations

from datetime import UTC, datetime

from lab.models import ActionRequest, ProvenanceRecord, WorkflowState


def utc_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def record(
    *,
    req: ActionRequest,
    before: WorkflowState,
    after: WorkflowState,
    decision: str,
) -> ProvenanceRecord:
    """Build a provenance row for a committed ALLOW.

    Never copies parameters (approval tokens / fake secrets stay out).
    """
    return ProvenanceRecord(
        workflow_id=req.workflow_id,
        actor=req.actor,
        action=req.action,
        resource=req.resource,
        decision=decision,
        state_before=before.public_view(),
        state_after=after.public_view(),
        timestamp=utc_timestamp(),
        seq=len(before.provenance) + 1,
    )
