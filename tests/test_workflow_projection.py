"""Workflow metadata, V11; synthetic producer records, no agent/provider execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from agent_authority.cli import main
from agent_authority.file_reader import ReadIssue
from agent_authority.workflow import (
    EVENT_SCHEMA,
    build_workflow_report,
    project_bridge_task,
    read_workflow,
)
from agent_authority.workflow_present import render_workflow_html, render_workflow_text


def event(number: int = 1, **changes: Any) -> dict[str, Any]:
    return {
        "schema_version": EVENT_SCHEMA,
        "source_tool": "kirabridge",
        "source_id": "local-run",
        "event_id": f"event-{number}",
        "ordinal": number,
        "event_type": "task.accepted",
        "timestamp": "2026-10-18T12:00:00Z",
        "project_id": "project-1",
        "workflow_id": "workflow-1",
        "task_id": "thread:task",
        "original_task_id": "thread:task",
        "bridge_task_id": "kb-task-1",
        "run_id": "run-1",
        "handoff_id": "handoff-1",
        "handoff_revision": 1,
        "source_revision": 7,
        **changes,
    }


def write(folder: Path, records: list[dict[str, Any]], name: str = "segment-1.jsonl") -> Path:
    folder.mkdir(exist_ok=True)
    path = folder / name
    path.write_text("".join(json.dumps(record) + "\n" for record in records))
    return path


def report(folder: Path) -> dict[str, Any]:
    return build_workflow_report(read_workflow(folder, "local-run", "kirabridge"))


def test_joined_claims_keep_id_and_revision_kinds_separate_and_never_upgrade_identity(
    tmp_path: Path,
):
    path = write(
        tmp_path,
        [
            event(),
            event(
                2,
                event_type="task.completed",
                source_authenticated=True,
                reported_status="turn_completed",
                request_hash="a" * 64,
                session_id="session-1",
                principal_ref="configured-chatgpt",
                operator_scope="workspace-1",
                source_hash="b" * 64,
                prompt="PRIVATE_SECRET",
                args={"token": "PRIVATE_SECRET"},
                result={"text": "PRIVATE_SECRET"},
            ),
        ],
    )
    before = path.read_bytes()
    value = report(tmp_path)
    binding = value["events"][1]["binding"]
    assert binding["original_task_id"] == "thread:task" and binding["bridge_task_id"] == "kb-task-1"
    assert binding["handoff_revision"] == 1 and binding["source_revision"] == 7
    assert binding["session_id"] != binding["run_id"]
    for output in [json.dumps(value), render_workflow_text(value), render_workflow_html(value)]:
        assert "PRIVATE_SECRET" not in output
    assert not value["source_authenticated"] and value["identity"] == value["effect"] == "UNBEKANNT"
    assert (
        not value["rights_granted"] and not value["budget_released"] and not value["stop_enforced"]
    )
    assert not value["task_completion_proven"]
    assert any(item["code"] == "workflow_identity_unverified" for item in value["warnings"])
    assert path.read_bytes() == before and list(tmp_path.iterdir()) == [path]


def test_exact_duplicate_is_counted_once_across_rotated_files_conflict_removes_both(tmp_path: Path):
    write(tmp_path, [event()])
    write(tmp_path, [event(), event(2)], "segment-2.jsonl")
    value = report(tmp_path)
    assert len(value["events"]) == 2 and value["read"]["duplicates_ignored"] == 1
    write(tmp_path, [event(source_revision=8)], "segment-3.jsonl")
    value = report(tmp_path)
    assert [item["event_id"] for item in value["events"]] == ["event-2"]
    assert "workflow_duplicate_conflict" in {item["code"] for item in value["warnings"]}
    assert not value["read"]["workflow_evidence_complete"]


def test_out_of_order_gaps_and_rotation_prefix_remain_unknown(tmp_path: Path):
    write(tmp_path, [event(3, previous_event_hash="a" * 64), event(1), event(5)])
    value = report(tmp_path)
    codes = {item["code"] for item in value["warnings"]}
    assert {"workflow_out_of_order", "workflow_sequence_gap", "workflow_prefix_unobserved"} <= codes
    assert value["read"]["coverage_of_all_activity"] == "UNBEKANNT"
    assert not value["observation_report"]["source"]["complete_observed_read"]
    assert not value["task_completion_proven"]


def test_existing_authority_envelope_is_minimized_not_authenticated_or_ordered(tmp_path: Path):
    write(
        tmp_path,
        [
            {
                "schema_version": "1",
                "source_tool": "kirabridge",
                "event_id": "legacy-1",
                "event_type": "budget.checked",
                "workflow_id": "workflow-1",
                "actor": {"key": "PRIVATE"},
                "action": "PRIVATE",
                "data_labels": ["PUBLIC"],
                "event_hash": "a" * 64,
            }
        ],
    )
    value = report(tmp_path)
    assert value["events"][0]["event_type"] == "budget.checked"
    assert "PRIVATE" not in json.dumps(value)
    assert "workflow_order_unknown" in {item["code"] for item in value["warnings"]}
    assert value["source_authenticated"] is False


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": []},
        {"schema_version": "v999"},
        {"event_type": "authority.grant"},
        {"source_tool": "tollgate"},
        {"source_id": "foreign-source"},
        {"ordinal": True},
        {"reserved_microusd": True},
        {"spent_microusd": 1.5},
        {"source_revision": -1},
        {"request_hash": "not-a-hash"},
        {"source_hash": "https://private/?token=SECRET"},
        {"operator_scope": "/private/path"},
        {"timestamp": "2026-10-18T12:00:00"},
    ],
)
def test_invalid_metadata_never_converts_to_a_positive_fact(
    tmp_path: Path, changes: dict[str, Any]
):
    write(tmp_path, [event(**changes)])
    value = report(tmp_path)
    assert not value["events"] and not value["read"]["complete_selected_read"]
    assert value["warnings"] and "SECRET" not in json.dumps(value)


def test_segment_record_and_byte_bounds_and_symlink_are_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    from agent_authority import workflow

    write(tmp_path, [event(), event(2), event(3)])
    monkeypatch.setattr(workflow, "MAX_RECORDS", 2)
    value = report(tmp_path)
    assert len(value["events"]) == 2 and not value["read"]["complete_selected_read"]
    assert "workflow_record_limit" in {item["code"] for item in value["warnings"]}
    write(tmp_path, [event(4)], "segment-2.jsonl")
    monkeypatch.setattr(workflow, "MAX_SEGMENTS", 1)
    assert "workflow_segment_limit" in {item["code"] for item in report(tmp_path)["warnings"]}
    (tmp_path / "segment-1.jsonl").write_bytes(b"x" * 65537)
    assert "entry_too_large" in {item["code"] for item in report(tmp_path)["warnings"]}
    link = tmp_path.parent / (tmp_path.name + "-link")
    link.symlink_to(tmp_path, target_is_directory=True)
    assert not report(link)["read"]["complete_selected_read"]


def test_duplicate_json_fields_and_oversized_line_are_rejected(tmp_path: Path):
    path = write(tmp_path, [])
    path.write_text('{"event_id":"a","event_id":"b"}\n')
    assert "invalid_json" in {item["code"] for item in report(tmp_path)["warnings"]}
    path.write_text(json.dumps(event(prompt="x" * 5000)) + "\n")
    assert "workflow_record_too_large" in {item["code"] for item in report(tmp_path)["warnings"]}


def test_task_projection_reuses_caller_owned_metadata_without_args_or_new_storage():
    value = project_bridge_task(
        {
            "id": "kb-task-1",
            "state": "completed",
            "updated": 1000,
            "args": {"prompt": "PRIVATE"},
            "result": {"token": "PRIVATE"},
        },
        {
            "task_id": "thread:task",
            "original_task_id": "thread:task",
            "run_id": "run-1",
            "handoff_revision": 1,
            "source_revision": 7,
            "request_hash": "a" * 64,
            "prompt": "PRIVATE",
        },
        source_id="bridge-runtime",
        event_id="audit-42",
        ordinal=42,
    )
    assert value["event_id"] == "audit-42" and value["bridge_task_id"] == "kb-task-1"
    assert value["reported_status"] == "turn_completed" and value["ordinal"] == 42
    assert "PRIVATE" not in json.dumps(value)
    with pytest.raises(ReadIssue):
        project_bridge_task(
            {"id": "x", "state": "new"}, {}, source_id="source", event_id="e", ordinal=1
        )


def test_new_cli_keeps_old_v1_entry_path_and_produces_offline_wrapper(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    write(tmp_path, [event()])
    assert (
        main(
            [
                "workflow-inspect",
                "--input",
                str(tmp_path),
                "--source-id",
                "local-run",
                "--source-tool",
                "kirabridge",
                "--format",
                "json",
            ]
        )
        == 0
    )
    value = json.loads(capsys.readouterr().out)
    assert value["schema_version"] == "agent-authority-workflow-report-v1"
    assert value["observation_report"]["schema_version"] == "agent-authority-observation-report-v1"
