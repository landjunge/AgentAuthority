"""AA-C02: selected synthetic source claims, no provider or secret operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agent_authority.file_reader import ReadIssue
from agent_authority.workflow import (
    EVENT_SCHEMA,
    build_workflow_report,
    project_record,
    read_workflow,
)
from agent_authority.workflow_present import render_workflow_html, render_workflow_text
from agent_authority.workflow_rules import analyze_workflow_claims


def claim(number: int, kind: str, **changes: Any):
    record = {
        "schema_version": EVENT_SCHEMA,
        "source_tool": "threaddesk",
        "source_id": "synthetic-aa",
        "event_id": f"e-{number}",
        "ordinal": number,
        "event_type": kind,
        "project_id": "project-1",
        "workflow_id": "workflow-1",
        "task_id": "td:task-1",
        "original_task_id": "td:task-1",
        "bridge_task_id": "kb-task-1",
        "handoff_id": "handoff-1",
        "run_id": "run-1",
        "recipient_id": "codex",
        "handoff_revision": 1,
        "source_revision": 7,
        "task_revision": 3,
        **changes,
    }
    return project_record(
        record,
        source_tool=record["source_tool"],
        source_id=record["source_id"],
        segment_id="segment-1",
        file_sha256="a" * 64,
    )


def analysis(*items: Any, complete: bool = True):
    return analyze_workflow_claims(tuple(items), complete_selected_read=complete)


def codes(value: dict[str, Any]):
    return {item["code"] for item in value["findings"]}


def bound_return(**changes: Any):
    return claim(1, "handoff.bound"), claim(
        2, "return.received", **{"binding_event_id": "e-1", "artifact_ref": "artifact-1", **changes}
    )


def test_matching_handoff_is_only_consistent_report_never_identity_acceptance_or_artifact_proof():
    value = analysis(*bound_return())
    assert not codes(value)
    assert value["rule_results"]["return_binding"]["compared_pairs"] == 1
    assert value["coverage_of_all_activity"] == "UNBEKANNT"
    assert not value["source_authenticated"] and not value["task_completion_proven"]
    assert not value["actual_violation_verified"] and not value["gate_authorization_proven"]


@pytest.mark.parametrize("field", ["source_revision", "handoff_revision", "task_revision"])
def test_old_revision_does_not_compare_unrelated_revision_kinds(field: str):
    old = {"source_revision": 6, "handoff_revision": 0, "task_revision": 2}[field]
    value = analysis(*bound_return(**{field: old}))
    finding = next(f for f in value["findings"] if f["code"] == "workflow_revision_stale")
    assert finding["fields"] == [field]
    assert finding["classification"] == "reported_contradiction"
    assert len(finding["evidence_refs"]) == 2
    assert not finding["identity_authenticated"] and not finding["actual_violation_verified"]


def test_future_revision_is_mismatch_not_stale_and_missing_revision_unknown():
    assert "workflow_revision_mismatch" in codes(analysis(*bound_return(source_revision=8)))
    before, returned = bound_return()
    from dataclasses import replace

    missing = replace(
        returned, binding=tuple((k, v) for k, v in returned.binding if k != "source_revision")
    )
    value = analysis(before, missing)
    assert "workflow_revision_unknown" in codes(value) and "workflow_revision_stale" not in codes(
        value
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("recipient_id", "grok"),
        ("run_id", "run-2"),
        ("task_id", "td:task-2"),
        ("bridge_task_id", "other-kb"),
        ("source_hash", "b" * 64),
    ],
)
def test_wrong_recipient_return_or_source_binding_is_reported_conflict(field: str, value: str):
    before, returned = bound_return(**{field: value})
    if field == "source_hash":
        before = claim(1, "handoff.bound", source_hash="a" * 64)
    result = analysis(before, returned)
    finding = next(f for f in result["findings"] if f["code"] == "workflow_return_binding_mismatch")
    assert field in finding["fields"]


@pytest.mark.parametrize(
    "changes",
    [
        {"project_id": "foreign"},
        {"workflow_id": "foreign"},
        {"handoff_id": "foreign"},
        {"source_id": "foreign"},
        {"source_tool": "kirabridge"},
        {"binding_event_id": "missing"},
    ],
)
def test_foreign_scope_or_missing_explicit_binding_never_joined(changes: dict[str, str]):
    result = analysis(*bound_return(**changes))
    assert "workflow_return_binding_unknown" in codes(result)
    assert "workflow_return_binding_mismatch" not in codes(result)
    assert "workflow_revision_stale" not in codes(result)


def test_implicit_binding_requires_unique_complete_ordered_slice_explicit_reference_survives_gap():
    before = claim(1, "handoff.bound")
    returned = claim(3, "return.received", artifact_ref="a")
    assert "workflow_return_binding_unknown" not in codes(analysis(before, returned))
    assert "workflow_return_binding_unknown" in codes(analysis(before, returned, complete=False))
    assert "workflow_return_binding_unknown" in codes(
        analysis(before, claim(2, "handoff.bound", run_id="run-2"), returned)
    )
    assert "workflow_return_binding_unknown" not in codes(
        analysis(
            before,
            claim(3, "return.received", binding_event_id="e-1", artifact_ref="a"),
            complete=False,
        )
    )
    assert "workflow_return_binding_unknown" in codes(analysis(claim(4, "handoff.bound"), returned))
    assert "workflow_return_binding_unknown" in codes(
        analysis(before, claim(1, "task.running", event_id="collision"), returned)
    )


@pytest.mark.parametrize(
    "kind",
    [
        "task.completed",
        "task.delivered",
        "return.received",
        "job.completed",
        "work.finished",
        "design.delivered",
    ],
)
def test_turn_or_delivery_without_artifact_is_missing_evidence_not_project_failure(kind: str):
    value = analysis(claim(1, kind))
    finding = next(f for f in value["findings"] if f["code"] == "workflow_result_artifact_missing")
    assert finding["classification"] == "missing_evidence"
    assert not value["task_completion_proven"]
    assert "workflow_result_artifact_missing" not in codes(
        analysis(claim(1, kind, artifact_ref="reported-only"))
    )


def control(number: int, kind: str, **changes: Any):
    return claim(
        number,
        kind,
        source_tool="tollgate",
        control_ref="gate-epoch-1",
        attempt_id="attempt-1",
        consumer_id="codex-lane",
        actor_claim="codex",
        request_hash="a" * 64,
        **changes,
    )


def test_reported_g02_dispatch_after_durable_barrier_is_contradiction_before_barrier_not():
    stop = control(2, "control.stop_effective", stop_state="effective", barrier_seq=7)
    gate = control(1, "budget.reserved")
    after = control(3, "dispatch.attempted", dispatch_seq=8, gate_event_id="e-1")
    value = analysis(gate, stop, after)
    assert "workflow_dispatch_after_stop" in codes(value)
    assert "workflow_control_point_missing" not in codes(value)
    assert all(not f["actual_violation_verified"] for f in value["findings"])
    before = control(3, "dispatch.attempted", dispatch_seq=6, gate_event_id="e-1")
    assert "workflow_dispatch_after_stop" not in codes(analysis(gate, stop, before))
    equal = control(3, "dispatch.attempted", dispatch_seq=7, gate_event_id="e-1")
    assert "workflow_stop_order_unknown" in codes(analysis(gate, stop, equal))


@pytest.mark.parametrize(
    "kind,state",
    [
        ("control.stop_requested", "requested"),
        ("control.stop_pending", "pending"),
        ("control.stop_effective", "unknown"),
    ],
)
def test_stop_request_pending_or_unknown_is_not_effective(kind: str, state: str):
    value = analysis(
        control(1, kind, stop_state=state, barrier_seq=1),
        control(2, "dispatch.attempted", dispatch_seq=9),
    )
    assert "workflow_dispatch_after_stop" not in codes(value)
    assert "workflow_stop_order_unknown" in codes(value)


@pytest.mark.parametrize(
    "changes",
    [
        {"control_ref": "foreign"},
        {"workflow_id": "foreign"},
        {"project_id": "foreign"},
        {"source_id": "foreign"},
    ],
)
def test_foreign_controller_sequences_never_compared(changes: dict[str, str]):
    stop = control(1, "control.stop_effective", stop_state="effective", barrier_seq=2)
    after = (
        claim(
            2,
            "dispatch.attempted",
            source_tool="tollgate",
            control_ref="gate-epoch-1",
            dispatch_seq=3,
            **changes,
        )
        if "control_ref" not in changes
        else claim(2, "dispatch.attempted", source_tool="tollgate", dispatch_seq=3, **changes)
    )
    value = analysis(stop, after)
    assert "workflow_dispatch_after_stop" not in codes(value)
    assert "workflow_stop_order_unknown" in codes(value)


def test_missing_gate_or_foreign_attempt_and_4ap_access_approved_are_not_dispatch_authorization():
    for gate in [
        control(1, "access.approved"),
        control(1, "budget.checked"),
        claim(
            1,
            "budget.reserved",
            source_tool="tollgate",
            control_ref="gate-epoch-1",
            attempt_id="foreign",
        ),
    ]:
        value = analysis(
            gate, control(2, "dispatch.attempted", dispatch_seq=2, gate_event_id="e-1")
        )
        assert "workflow_control_point_missing" in codes(value)
        assert not value["gate_authorization_proven"]
    assert not codes(analysis(claim(1, "access.approved", source_tool="4allpass")))


def test_missing_stop_sequence_unknown_and_earliest_barrier_cannot_be_hidden_by_later_barrier():
    dispatch = control(3, "dispatch.attempted", dispatch_seq=4)
    assert "workflow_stop_order_unknown" in codes(
        analysis(control(1, "control.stop_effective", stop_state="effective"), dispatch)
    )
    result = analysis(
        control(1, "control.stop_effective", stop_state="effective", barrier_seq=2),
        control(2, "control.stop_effective", stop_state="effective", barrier_seq=7),
        dispatch,
    )
    assert "workflow_dispatch_after_stop" in codes(result)


def test_stable_references_limits_and_gaps_never_become_all_clear():
    from dataclasses import replace

    item = claim(1, "task.completed")
    value = analysis(item)
    moved = analysis(replace(item, file_sha256="b" * 64))
    assert moved["findings"][0]["finding_id"] == value["findings"][0]["finding_id"]
    assert (
        moved["findings"][0]["evidence_refs"][0]["file_sha256"]
        != value["findings"][0]["evidence_refs"][0]["file_sha256"]
    )
    large = tuple(claim(i, "task.completed") for i in range(1, 102))
    bounded = analyze_workflow_claims(large, limit=2)
    assert len(bounded["findings"]) == 2 and bounded["findings_omitted"] == 99
    assert bounded["counts"]["missing_evidence"] == 101
    for invalid in [True, 0, 101]:
        with pytest.raises(ValueError):
            analyze_workflow_claims((), limit=invalid)
    with pytest.raises(ValueError):
        analyze_workflow_claims((item,) * 10001)
    empty = analysis()
    assert empty["coverage_of_all_activity"] == "UNBEKANNT"
    assert not empty["gate_authorization_proven"]


def test_adapter_strict_additions_and_real_report_path_show_evidence_without_secrets(
    tmp_path: Path,
):
    for field in ["binding_event_id", "gate_event_id", "control_ref", "consumer_id"]:
        with pytest.raises(ReadIssue):
            claim(1, "task.completed", **{field: "https://bad.invalid/?key=SECRET"})
    record = {
        "schema_version": EVENT_SCHEMA,
        "source_tool": "gnom-hub-v1",
        "source_id": "synthetic-aa",
        "event_id": "g-1",
        "ordinal": 1,
        "event_type": "work.finished",
        "project_id": "p-1",
        "workflow_id": "w-1",
        "prompt": "PRIVATE_SECRET",
        "raw_result": "PRIVATE_SECRET",
    }
    (tmp_path / "segment.jsonl").write_text(json.dumps(record) + "\n")
    value = build_workflow_report(read_workflow(tmp_path, "synthetic-aa", "gnom-hub-v1"))
    assert "workflow_result_artifact_missing" in codes(value["analysis"])
    for text in [json.dumps(value), render_workflow_text(value), render_workflow_html(value)]:
        assert "PRIVATE_SECRET" not in text
        assert "workflow_result_artifact_missing" in text or "Ergebnisbeleg" in text


@pytest.mark.parametrize(
    "field,value",
    [
        ("attempt_id", "foreign"),
        ("consumer_id", "foreign"),
        ("actor_claim", "foreign"),
        ("request_hash", "b" * 64),
        ("task_id", "foreign"),
    ],
)
def test_gate_with_foreign_g01_binding_never_becomes_matching_checkpoint(field: str, value: str):
    base = {
        "source_tool": "tollgate",
        "control_ref": "gate-epoch-1",
        "attempt_id": "attempt-1",
        "consumer_id": "codex-lane",
        "actor_claim": "codex",
        "request_hash": "a" * 64,
    }
    gate = claim(1, "budget.reserved", **{**base, field: value})
    dispatch = control(2, "dispatch.attempted", dispatch_seq=2, gate_event_id="e-1")
    result = analysis(gate, dispatch)
    assert "workflow_control_point_missing" in codes(result)
    assert not result["gate_authorization_proven"]


def test_gate_after_dispatch_or_ambiguous_ordinal_cannot_be_a_prior_checkpoint():
    result = analysis(
        control(3, "budget.reserved"),
        control(2, "dispatch.attempted", dispatch_seq=2, gate_event_id="e-3"),
    )
    assert "workflow_control_point_missing" in codes(result)
    result = analysis(
        control(1, "budget.reserved"),
        claim(1, "task.running", source_tool="tollgate", event_id="collision"),
        control(2, "dispatch.attempted", dispatch_seq=2, gate_event_id="e-1"),
    )
    assert "workflow_control_point_missing" in codes(result)
