"""Minimized workflow claims over bounded, selected local producer segments.

No authentication, enforcement, producer execution or source modification.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

from agent_authority.file_reader import (
    MAX_TOTAL_BYTES,
    ReadBudget,
    ReadIssue,
    _constant,
    _scan_directory,
    _signature,
    _unique,
    read_bytes,
)
from agent_authority.observations import TOKEN, Diagnostic, Entry, Snapshot, Source
from agent_authority.report import build_report
from agent_authority.workflow_rules import analyze_workflow_claims

EVENT_SCHEMA = "agent-authority-workflow-event-v1"
REPORT_SCHEMA = "agent-authority-workflow-report-v1"
TOOLS = frozenset(
    {"threaddesk", "kirabridge", "tollgate", "4allpass", "gnom-hub-v1", "blockdesigner"}
)
MAX_SEGMENTS = 64
MAX_RECORDS = 10_000
MAX_RECORD_BYTES = 4096
REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,255}\Z")
HASH = re.compile(r"[0-9a-f]{64}\Z")
BINDINGS = frozenset(
    {
        "project_id",
        "workflow_id",
        "thread_id",
        "handoff_id",
        "task_id",
        "run_id",
        "attempt_id",
        "parent_task_id",
        "subtask_id",
        "return_id",
        "recipient_id",
        "source_ref",
        "artifact_ref",
        "original_task_id",
        "bridge_task_id",
        "session_id",
        "principal_ref",
        "operator_scope",
        "actor_claim",
        "consumer_id",
        "binding_event_id",
        "control_ref",
        "gate_event_id",
    }
)
HASH_FIELDS = frozenset({"request_hash", "source_hash"})
EVENT_TYPES = frozenset(
    {
        "capability.granted",
        "capability.denied",
        "capability.revoked",
        "work.started",
        "agent.invoked",
        "delegation.created",
        "tool.intent",
        "tool.result",
        "work.finished",
        "task.accepted",
        "task.started",
        "task.running",
        "task.question",
        "task.answer_recorded",
        "task.completed",
        "task.failed",
        "task.unknown",
        "task.cancelled",
        "task.delivered",
        "handoff.created",
        "handoff.bound",
        "return.received",
        "return.reviewed",
        "budget.checked",
        "budget.reserved",
        "budget.settled",
        "budget.unknown",
        "control.stop_requested",
        "control.stop_pending",
        "control.stop_effective",
        "control.abort_confirmed",
        "dispatch.attempted",
        "dispatch.unknown",
        "request.blocked",
        "consumer.frozen",
        "loop.detected",
        "access.requested",
        "access.approved",
        "access.denied",
        "access.used",
        "job.created",
        "job.started",
        "job.completed",
        "job.cancelled",
        "job.unknown",
        "design.handoff",
        "design.delivered",
    }
)
INTEGERS = frozenset(
    {
        "handoff_revision",
        "source_revision",
        "task_revision",
        "dispatch_seq",
        "barrier_seq",
        "reserved_microusd",
        "spent_microusd",
        "available_microusd",
    }
)
ENUMS = {
    "stop_state": frozenset({"requested", "pending", "effective", "abort_confirmed", "unknown"}),
    "cost_kind": frozenset({"estimated", "evidenced_final", "no_final_cost", "unknown"}),
    "reported_status": frozenset(
        {
            "accepted",
            "started",
            "running",
            "waiting_question",
            "turn_completed",
            "delivered_unverified",
            "checked",
            "accepted_by_user",
            "unknown",
            "failed",
            "cancelled",
        }
    ),
}
KIND_MAP = {
    "capability.granted": "decision",
    "capability.denied": "decision",
    "capability.revoked": "decision",
    "work.started": "claimed",
    "agent.invoked": "progress",
    "delegation.created": "handoff",
    "tool.intent": "progress",
    "tool.result": "result",
    "work.finished": "result",
    "task.accepted": "claimed",
    "task.started": "progress",
    "task.running": "progress",
    "task.question": "question",
    "task.delivered": "result",
    "task.completed": "result",
    "handoff.created": "handoff",
    "return.received": "result",
    "dispatch.attempted": "progress",
}


@dataclass(frozen=True)
class WorkflowClaim:
    event_id: str
    source_tool: str
    source_id: str
    segment_id: str
    event_type: str
    producer_ordinal: int | None
    timestamp: str | None
    binding: tuple[tuple[str, str | int], ...]
    file_sha256: str
    record_sha256: str
    entry_id: str
    event_hash: str | None = None
    previous_event_hash: str | None = None
    identity_claimed: bool = False

    def projection(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "source_tool": self.source_tool,
            "source_id": self.source_id,
            "segment_id": self.segment_id,
            "event_type": self.event_type,
            "producer_ordinal": self.producer_ordinal,
            "timestamp": self.timestamp,
            "binding": dict(self.binding),
            "entry_id": self.entry_id,
            "file_sha256": self.file_sha256,
            "record_sha256": self.record_sha256,
            "assertion_basis": "producer_report_only",
            "identity_authenticated": False,
            "effect_verified": False,
        }


def _reference(value: Any) -> str:
    if not isinstance(value, str) or not REFERENCE.fullmatch(value):
        raise ReadIssue("workflow_invalid_metadata")
    return value


def _integer(value: Any) -> int:
    if type(value) is not int or not 0 <= value < 2**63:
        raise ReadIssue("workflow_invalid_metadata")
    return value


def project_record(
    record: Any, *, source_tool: str, source_id: str, segment_id: str, file_sha256: str
) -> WorkflowClaim:
    """Whitelist only; input contents, flags and actor names cannot authenticate claims."""
    if not isinstance(record, dict):
        raise ReadIssue("workflow_invalid_record")
    schema = record.get("schema_version")
    if not isinstance(schema, str) or schema not in {EVENT_SCHEMA, "1"}:
        raise ReadIssue("workflow_unknown_schema")
    if record.get("source_tool") != source_tool or (
        schema == EVENT_SCHEMA and record.get("source_id") != source_id
    ):
        raise ReadIssue("workflow_source_mismatch")
    event_id = _reference(record.get("event_id"))
    event_type = _reference(record.get("event_type"))
    if event_type not in EVENT_TYPES:
        raise ReadIssue("workflow_unknown_event_type")
    ordinal = _integer(record["ordinal"]) if "ordinal" in record else None
    timestamp = record.get("timestamp")
    if timestamp is not None:
        if not isinstance(timestamp, str) or len(timestamp) > 40:
            raise ReadIssue("workflow_invalid_metadata")
        try:
            parsed = datetime.fromisoformat(timestamp)
            if parsed.tzinfo is None:
                raise ValueError("no timezone")
        except ValueError as exc:
            raise ReadIssue("workflow_invalid_metadata") from exc
    binding: dict[str, str | int] = {}
    for key in BINDINGS:
        if key in record:
            binding[key] = _reference(record[key])
    for key in HASH_FIELDS:
        if key in record:
            value = record[key]
            if not isinstance(value, str) or not HASH.fullmatch(value):
                raise ReadIssue("workflow_invalid_metadata")
            binding[key] = value
    for key in INTEGERS:
        if key in record:
            binding[key] = _integer(record[key])
    for key, allowed in ENUMS.items():
        if key in record:
            value = record[key]
            if not isinstance(value, str) or value not in allowed:
                raise ReadIssue("workflow_invalid_metadata")
            binding[key] = value
    # Fingerprints compare bytes/claims only; neither authenticates a producer.
    normalized = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    identity_key = json.dumps([source_tool, source_id, event_id], separators=(",", ":")).encode()
    event_hash, previous = record.get("event_hash"), record.get("previous_event_hash")
    if event_hash is not None and (
        not isinstance(event_hash, str) or not HASH.fullmatch(event_hash)
    ):
        raise ReadIssue("workflow_invalid_metadata")
    if previous is not None and (not isinstance(previous, str) or not HASH.fullmatch(previous)):
        raise ReadIssue("workflow_invalid_metadata")
    return WorkflowClaim(
        event_id,
        source_tool,
        source_id,
        segment_id,
        event_type,
        ordinal,
        timestamp,
        tuple(sorted(binding.items())),
        file_sha256,
        hashlib.sha256(normalized).hexdigest(),
        "wf-" + hashlib.sha256(identity_key).hexdigest()[:32],
        event_hash,
        previous,
        record.get("source_authenticated") is True,
    )


@dataclass(frozen=True)
class WorkflowRead:
    snapshot: Snapshot
    claims: tuple[WorkflowClaim, ...]
    diagnostics: tuple[Diagnostic, ...]
    segments_seen: int
    records_seen: int
    duplicates: int


def read_workflow(path: Path, source_id: str, source_tool: str) -> WorkflowRead:
    source = Source("workflow-jsonl", source_id if TOKEN.fullmatch(source_id) else "")
    diagnostics: list[Diagnostic] = []
    if not source.identifier or source_tool not in TOOLS:
        snapshot = Snapshot(source, (), (Diagnostic("invalid_source_id"),), 0, 0)
        return WorkflowRead(snapshot, (), (), 0, 0, 0)
    if not (os.open in os.supports_dir_fd and os.scandir in os.supports_fd):
        snapshot = Snapshot(source, (), (Diagnostic("unsupported_reader_platform"),), 0, 0)
        return WorkflowRead(snapshot, (), (), 0, 0, 0)
    try:
        directory = os.open(path.expanduser(), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        snapshot = Snapshot(
            source, (), (Diagnostic("source_unavailable"),), 0, 0, directory_scan_complete=False
        )
        return WorkflowRead(snapshot, (), (), 0, 0, 0)
    budget = ReadBudget(MAX_TOTAL_BYTES)
    claims: dict[str, WorkflowClaim] = {}
    conflicts: set[str] = set()
    signatures = {}
    seen = examined = duplicates = 0
    scan = None
    try:
        identity = os.fstat(directory)
        scan = _scan_directory(directory, ".jsonl")
        if not scan.complete:
            diagnostics.append(Diagnostic("directory_limit"))
        if scan.files_seen > MAX_SEGMENTS:
            diagnostics.append(Diagnostic("workflow_segment_limit"))
        for name in scan.names[:MAX_SEGMENTS]:
            examined += 1
            if not TOKEN.fullmatch(name[:-6]):
                diagnostics.append(Diagnostic("invalid_filename"))
                continue
            try:
                raw, fingerprint, signature = read_bytes(directory, name, budget)
                signatures[name] = signature
            except ReadIssue as exc:
                diagnostics.append(Diagnostic(str(exc)))
                if budget.exhausted:
                    break
                continue
            except OSError:
                diagnostics.append(Diagnostic("unreadable_entry"))
                continue
            for line in raw.splitlines():
                if not line.strip():
                    continue
                seen += 1
                if seen > MAX_RECORDS:
                    diagnostics.append(Diagnostic("workflow_record_limit"))
                    break
                try:
                    if len(line) > MAX_RECORD_BYTES:
                        raise ReadIssue("workflow_record_too_large")
                    record = json.loads(line, object_pairs_hook=_unique, parse_constant=_constant)
                    claim = project_record(
                        record,
                        source_tool=source_tool,
                        source_id=source_id,
                        segment_id=name[:-6],
                        file_sha256=fingerprint,
                    )
                except (ValueError, UnicodeError, RecursionError, ReadIssue) as exc:
                    diagnostics.append(
                        Diagnostic(str(exc) if isinstance(exc, ReadIssue) else "invalid_json")
                    )
                    continue
                previous = claims.get(claim.entry_id)
                if previous:
                    if previous.record_sha256 == claim.record_sha256:
                        duplicates += 1
                    else:
                        conflicts.add(claim.entry_id)
                    continue
                claims[claim.entry_id] = claim
            if seen > MAX_RECORDS:
                break
        after = _scan_directory(directory, ".jsonl")
        changed = scan != after
        for name, signature in signatures.items():
            try:
                changed |= signature != _signature(
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                )
            except OSError:
                changed = True
        current = path.expanduser().stat(follow_symlinks=False)
        changed |= (identity.st_dev, identity.st_ino) != (current.st_dev, current.st_ino)
        if changed:
            diagnostics.append(Diagnostic("source_changed"))
    except OSError:
        diagnostics.append(Diagnostic("source_unavailable"))
    finally:
        os.close(directory)
    for key in sorted(conflicts):
        diagnostics.append(Diagnostic("workflow_duplicate_conflict", key))
        claims.pop(key, None)  # neither competing version is selected as authoritative
    values = tuple(claims.values())
    entries = tuple(
        Entry(
            claim.entry_id,
            index,
            KIND_MAP.get(claim.event_type, "system"),
            claim.source_tool,
            (str(dict(claim.binding)["task_id"]) if "task_id" in dict(claim.binding) else None),
            claim.file_sha256,
        )
        for index, claim in enumerate(values, 1)
    )
    snapshot = Snapshot(
        source,
        entries,
        (),
        scan.files_seen if scan else 0,
        examined,
        scan.entries_seen if scan else 0,
        scan.complete if scan else False,
        budget.bytes_read,
    )
    return WorkflowRead(
        snapshot, values, tuple(diagnostics), scan.files_seen if scan else 0, seen, duplicates
    )


def build_workflow_report(read: WorkflowRead, limit: int = 20) -> dict[str, Any]:
    base = build_report(read.snapshot, limit)
    warnings = [
        {"code": item.code, "entry_id": item.entry_id, "classification": "missing_evidence"}
        for item in (*read.snapshot.diagnostics, *read.diagnostics)
    ]
    ordinals: dict[int, list[WorkflowClaim]] = {}
    for claim in read.claims:
        if claim.producer_ordinal is not None:
            ordinals.setdefault(claim.producer_ordinal, []).append(claim)
        if claim.identity_claimed:
            warnings.append(
                {
                    "code": "workflow_identity_unverified",
                    "entry_id": claim.entry_id,
                    "classification": "missing_evidence",
                }
            )
    if not ordinals:
        warnings.append(
            {
                "code": "workflow_order_unknown",
                "entry_id": None,
                "classification": "missing_evidence",
            }
        )
    else:
        numbers = sorted(ordinals)
        if numbers[0] > 1 or any(right != left + 1 for left, right in pairwise(numbers)):
            warnings.append(
                {
                    "code": "workflow_sequence_gap",
                    "entry_id": None,
                    "classification": "missing_evidence",
                }
            )
        if any(len(items) > 1 for items in ordinals.values()):
            warnings.append(
                {
                    "code": "workflow_ordinal_conflict",
                    "entry_id": None,
                    "classification": "structural_conflict",
                }
            )
        encountered = [c.producer_ordinal for c in read.claims if c.producer_ordinal is not None]
        if encountered != sorted(encountered):
            warnings.append(
                {
                    "code": "workflow_out_of_order",
                    "entry_id": None,
                    "classification": "missing_evidence",
                }
            )
    if read.claims and read.claims[0].previous_event_hash is not None:
        warnings.append(
            {
                "code": "workflow_prefix_unobserved",
                "entry_id": read.claims[0].entry_id,
                "classification": "missing_evidence",
            }
        )
    # An event-hash chain is merely a producer's consistency claim, never authentication.
    for previous, claim in pairwise(read.claims):
        if claim.previous_event_hash and previous.event_hash != claim.previous_event_hash:
            warnings.append(
                {
                    "code": "workflow_chain_gap",
                    "entry_id": claim.entry_id,
                    "classification": "missing_evidence",
                }
            )
    complete = base["source"]["complete_observed_read"] and not read.diagnostics
    analysis = analyze_workflow_claims(
        read.claims, limit, complete_selected_read=complete and not warnings
    )
    base["source"]["complete_observed_read"] = complete and not warnings
    return {
        "schema_version": REPORT_SCHEMA,
        "role": "observer_only",
        "source_authenticated": False,
        "identity": "UNBEKANNT",
        "effect": "UNBEKANNT",
        "observation_report": base,
        "events": [claim.projection() for claim in read.claims[-limit:]],
        "read": {
            "segments_seen": read.segments_seen,
            "records_seen": read.records_seen,
            "duplicates_ignored": read.duplicates,
            "events_omitted": max(0, len(read.claims) - limit),
            "complete_selected_read": complete,
            "workflow_evidence_complete": complete and not warnings,
            "coverage_of_all_activity": "UNBEKANNT",
        },
        "analysis": analysis,
        "warnings": warnings[:limit],
        "warnings_omitted": max(0, len(warnings) - limit),
        "rights_granted": False,
        "budget_released": False,
        "stop_enforced": False,
        "task_completion_proven": False,
    }


def project_bridge_task(
    task: dict[str, Any],
    binding: dict[str, Any],
    *,
    source_id: str,
    event_id: str,
    ordinal: int,
    source_hash: str | None = None,
) -> dict[str, Any]:
    """Called by a trusted exporter on already owned Store metadata, never its args/result.

    No Store connection or producer append is created. Existing audit sequence supplies
    event_id/ordinal; persistent mapping supplies original and Bridge task identities.
    """
    states = {
        "accepted": "task.accepted",
        "running": "task.running",
        "completed": "task.completed",
        "failed": "task.failed",
        "unknown": "task.unknown",
        "cancelled": "task.cancelled",
    }
    event_type = states.get(task.get("state", ""))
    if event_type is None:
        raise ReadIssue("workflow_unknown_event_type")
    result: dict[str, Any] = {
        "schema_version": EVENT_SCHEMA,
        "source_tool": "kirabridge",
        "source_id": _reference(source_id),
        "event_id": _reference(event_id),
        "ordinal": _integer(ordinal),
        "event_type": event_type,
    }
    for key in BINDINGS | INTEGERS | HASH_FIELDS | ENUMS.keys():
        if key in binding:
            result[key] = binding[key]
    result["bridge_task_id"] = task["id"]
    if source_hash is not None:
        result["source_hash"] = source_hash
    updated = task.get("updated")
    if isinstance(updated, (int, float)) and not isinstance(updated, bool):
        try:
            result["timestamp"] = datetime.fromtimestamp(updated, UTC).isoformat()
        except (ValueError, OverflowError, OSError) as exc:
            raise ReadIssue("workflow_invalid_metadata") from exc
    if event_type == "task.completed":
        result["reported_status"] = "turn_completed"
    # Validate/minimize the same contract before a caller exports it.
    project_record(
        result,
        source_tool="kirabridge",
        source_id=source_id,
        segment_id="export",
        file_sha256="0" * 64,
    )
    return result
