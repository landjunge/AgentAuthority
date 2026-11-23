"""An update observation is a readable producer claim with no action authority."""

import json

import pytest

from agent_authority.cli import main
from agent_authority.workflow import EVENT_SCHEMA, build_workflow_report, read_workflow
from agent_authority.workflow_present import render_workflow_html, render_workflow_text

SOURCE = "a" * 40
OTHER_COMMIT = "b" * 40
ARTIFACT = "c" * 64
INSTALLED = "d" * 64


def event(number, **facts):
    return {
        "schema_version": EVENT_SCHEMA,
        "source_tool": "kirabridge",
        "source_id": "update-fixture",
        "event_id": f"event-{number}",
        "ordinal": number,
        "event_type": "update.observed",
        "update_evidence": {"update_id": "candidate-7", **facts},
    }


def report(folder, *events):
    segment = folder / "segment-1.jsonl"
    segment.write_text("".join(json.dumps(row) + "\n" for row in events))
    before = segment.read_bytes()
    value = build_workflow_report(read_workflow(folder, "update-fixture", "kirabridge"))
    assert segment.read_bytes() == before
    return value


def test_update_retains_five_claims_and_observed_drift_without_authority(tmp_path, capsys):
    row = event(
        1,
        source={"commit": SOURCE, "ref": "git-main"},
        release={"status": "published", "tag": "v1.2.3", "commit": SOURCE},
        artifact={"sha256": ARTIFACT, "ref": "bundle-asset", "commit": SOURCE},
        ci={"status": "success", "run_ref": "gha-check-1-attempt-1", "commit": OTHER_COMMIT},
        installation={
            "status": "present",
            "target_ref": "mac-test",
            "commit": OTHER_COMMIT,
            "artifact_sha256": INSTALLED,
        },
        signature="private fixture signature",
        source_authenticated=True,
    )
    value = report(tmp_path, row)
    update = value["events"][0]["update_evidence"]
    assert set(update["facts"]) == {"source", "release", "artifact", "ci", "installation"}
    for name, facts in update["facts"].items():
        assert facts == {"state": "reported", "claims": row["update_evidence"][name]}
    assert [item["fields"] for item in update["differences"]] == [
        ["source.commit", "ci.commit"],
        ["source.commit", "installation.commit"],
        ["artifact.sha256", "installation.artifact_sha256"],
    ]
    assert update["signature_verification"] == "unknown"
    assert value["identity"] == value["effect"] == "UNBEKANNT"
    assert value["source_authenticated"] is value["rights_granted"] is False
    assert value["events"][0]["effect_verified"] is False
    assert "private fixture signature" not in json.dumps(value)
    assert (
        main(
            [
                "workflow-inspect",
                "--input",
                str(tmp_path),
                "--source-id",
                "update-fixture",
                "--source-tool",
                "kirabridge",
                "--format",
                "json",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["events"][0]["update_evidence"] == update


def test_unknown_and_absent_facts_have_no_derived_result(tmp_path):
    value = report(tmp_path, event(1, ci={"status": "unknown"}, installation={"status": "unknown"}))
    update = value["events"][0]["update_evidence"]
    assert all(fact["state"] == "unknown" for fact in update["facts"].values())
    assert update["facts"]["source"]["claims"] == {}
    assert update["facts"]["ci"]["claims"] == {"status": "unknown"}
    assert update["facts"]["installation"]["claims"] == {"status": "unknown"}
    assert update["differences"] == []
    assert value["update_ci_conflicts"] == []
    assert not value["task_completion_proven"]


def test_update_does_not_count_as_a_result_for_its_reported_task(tmp_path):
    def task_event(number, event_type):
        row = event(number)
        row.pop("update_evidence")
        return {**row, "event_type": event_type, "task_id": "task-1"}

    claim = task_event(1, "task.accepted")
    update = {**event(2, source={"commit": SOURCE}), "task_id": "task-1"}
    pending = report(tmp_path, claim, update)
    assert pending["events"][1]["binding"]["task_id"] == "task-1"
    assert pending["events"][1]["update_evidence"]["facts"]["source"]["claims"]["commit"] == SOURCE
    assert pending["read"]["workflow_evidence_complete"] is True
    neutral = pending["observation_report"]
    assert neutral["summary"]["reported_kind_counts"] == {"claimed": 1, "system": 1}
    assert neutral["summary"]["claims_without_later_result_in_read_entries"] == 1
    assert neutral["tasks"][0]["last_reported_kind"] == "claimed"
    assert neutral["tasks"][0]["claim_without_later_result"] is True

    completed = report(tmp_path, claim, update, task_event(3, "task.completed"))
    neutral = completed["observation_report"]
    assert neutral["summary"]["reported_kind_counts"]["result"] == 1
    assert neutral["summary"]["claims_without_later_result_in_read_entries"] == 0
    assert neutral["tasks"][0]["last_reported_kind"] == "result"
    assert neutral["tasks"][0]["claim_without_later_result"] is False
    assert completed["task_completion_proven"] is False


def test_same_terminal_check_conflict_is_visible_without_selecting_a_winner(tmp_path):
    same_check = {"commit": SOURCE, "run_ref": "gha-check-1-attempt-1"}
    value = report(
        tmp_path,
        event(1, ci={**same_check, "status": "pending"}),
        event(2, ci={**same_check, "status": "success"}),
        event(3, ci={**same_check, "status": "failure"}),
        event(4, ci={"commit": SOURCE, "run_ref": "gha-check-1-attempt-2", "status": "failure"}),
        event(5, ci={**same_check, "commit": OTHER_COMMIT, "status": "failure"}),
    )
    assert value["update_ci_conflicts"] == [
        {
            "update_id": "candidate-7",
            "commit": SOURCE,
            "ci_run_ref": "gha-check-1-attempt-1",
            "claims": [
                {"event_id": "event-2", "status": "success"},
                {"event_id": "event-3", "status": "failure"},
            ],
            "state": "reported_conflict",
        }
    ]
    assert value["effect"] == "UNBEKANNT"
    for output in (render_workflow_text(value), render_workflow_html(value)):
        assert "Reported CI conflict" in output
        assert "success (event-2), failure (event-3)" in output


@pytest.mark.parametrize(
    "facts",
    [
        {"source": {"commit": "not-a-commit"}},
        {"artifact": {"sha256": "short"}},
        {"ci": {"status": "green"}},
        {"installation": {"target_ref": "/private/original"}},
    ],
)
def test_invalid_typed_claims_do_not_leak_source_metadata(tmp_path, facts):
    value = report(tmp_path, event(1, **facts))
    assert not value["events"] and not value["read"]["workflow_evidence_complete"]
    assert "workflow_invalid_update_evidence" in {item["code"] for item in value["warnings"]}
    assert "/private/original" not in json.dumps(value)
