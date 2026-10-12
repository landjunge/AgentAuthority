"""Product acceptance: real file reads and dishonest/incomplete archive inputs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from agent_authority.cli import main
from agent_authority.report import build_report, render_text
from agent_authority.whiteboard import read_whiteboard

THREAD = "123456abcdef"
CANARY = "PRIVATE_CANARY_DO_NOT_EXPORT"


def put(store: Path, number: int, kind: str = "result", **changes: object) -> Path:
    folder = store / "whiteboard" / THREAD
    folder.mkdir(parents=True, exist_ok=True)
    identifier = f"{number:012x}"
    record = {
        "id": identifier,
        "thread_id": THREAD,
        "ordinal": number,
        "entry_type": kind,
        "actor_type": "codex",
        "actor": CANARY,
        "task_id": CANARY,
        "run_id": CANARY,
        "actor_id": CANARY,
        "instance_id": CANARY,
        "room_id": CANARY,
        "created_at": CANARY,
        "content": CANARY,
        "metadata": {"source_authenticated": True, "effect": "BELEGT", "prompt": CANARY},
        **changes,
    }
    path = folder / (identifier + ".json")
    path.write_text(json.dumps(record))
    return path


def report(store: Path, limit: int = 20) -> dict:
    return build_report(read_whiteboard(store, THREAD), limit)


def test_historical_plan_and_handoff_are_read_without_a_field_warning(tmp_path):
    put(tmp_path, 1, "plan")
    put(tmp_path, 2, "handoff")
    value = report(tmp_path)
    text = render_text(value)
    assert value["source"]["complete_observed_read"] is True
    assert value["source"]["entries_read"] == 2
    assert value["summary"]["structural_warning_count"] == 0
    assert value["summary"]["reported_kind_counts"] == {"handoff": 1, "plan": 1}
    assert {entry["reported_kind"] for entry in value["recent_entries"]} == {"plan", "handoff"}
    assert "Übergabe gemeldet" in text
    assert CANARY not in text


def test_normal_workflow_reports_claims_and_results_without_proving_execution(tmp_path):
    put(tmp_path, 1, "task")
    put(tmp_path, 2, "claimed")
    put(tmp_path, 3, "result")
    value = report(tmp_path)
    assert value["source"]["complete_observed_read"] is True
    assert value["summary"]["reported_kind_counts"] == {"claimed": 1, "result": 1, "task": 1}
    task = value["tasks"][0]
    assert task["last_reported_kind"] == "result"
    assert task["claim_without_later_result"] is False
    assert task["evidence"][-1]["ordinal"] == 3
    assert value["task_completion_proven"] is False
    assert value["source"]["source_authenticated"] is False
    assert value["source"]["identity"] == value["source"]["effect"] == "UNBEKANNT"
    assert value["rights_inherited"] is False


def test_result_before_new_claim_does_not_hide_missing_later_result(tmp_path):
    put(tmp_path, 1, "claimed")
    put(tmp_path, 2, "result")
    put(tmp_path, 3, "claimed")
    value = report(tmp_path)
    assert value["summary"]["claims_without_later_result_in_read_entries"] == 1
    assert value["tasks"][0]["last_reported_kind"] == "claimed"
    assert "kein späterer Ergebnisbeitrag gelesen" in render_text(value)


def test_minimization_excludes_all_free_text_and_forged_authenticated_metadata(tmp_path):
    put(tmp_path, 1)
    value = report(tmp_path)
    for output in [json.dumps(value), render_text(value)]:
        assert CANARY not in output
        assert "BELEGT" not in output
    assert value["tasks"][0]["task_alias"] == "A1"
    assert value["tasks"][0]["association_basis"] == "reported_task_id_only"


def test_citation_hash_matches_the_actual_read_file_and_store_stays_unchanged(tmp_path):
    path = put(tmp_path, 1)
    original = {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    value = report(tmp_path)
    assert (
        value["recent_entries"][0]["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    )
    assert original == {str(p): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert not (tmp_path / "actors").exists()


@pytest.mark.parametrize(
    "changes",
    [
        {"ordinal": True},
        {"ordinal": -1},
        {"ordinal": 2**63},
        {"ordinal": "1"},
        {"entry_type": "ALLOW"},
        {"actor_type": ["codex"]},
        {"task_id": 123},
        {"task_id": " "},
        {"task_id": "x" * 301},
        {"id": "abcdefabcdef"},
        {"thread_id": "abcdefabcdef"},
    ],
)
def test_invalid_fields_are_not_used_for_activity_or_authority(tmp_path, changes):
    put(tmp_path, 1, **changes)
    value = report(tmp_path)
    assert value["source"]["complete_observed_read"] is False
    assert value["source"]["entries_read"] == 0
    assert value["tasks"] == []
    assert len(value["warnings"]) == 1


@pytest.mark.parametrize("raw", [b'{"id":"a","id":"b"}', b'{"x":NaN}', b"\xff", b"[]"])
def test_invalid_or_ambiguous_json_is_diagnosed_without_echo(tmp_path, raw):
    path = put(tmp_path, 1)
    path.write_bytes(raw)
    value = report(tmp_path)
    assert value["source"]["complete_observed_read"] is False
    assert value["source"]["entries_read"] == 0
    assert value["source"]["source_authenticated"] is False


def test_duplicate_ordinals_keep_all_evidence_and_do_not_choose_a_last_kind(tmp_path):
    put(tmp_path, 1, "claimed")
    put(tmp_path, 2, "result", ordinal=1)
    value = report(tmp_path)
    assert value["source"]["entries_read"] == 2
    assert value["warnings"][0]["code"] == "ordinal_collision"
    assert len(value["warnings"][0]["evidence"]) == 2
    assert value["tasks"][0]["last_reported_kind"] is None
    assert value["tasks"][0]["claim_without_later_result"] is None
    assert value["source"]["complete_observed_read"] is False


def test_display_limit_does_not_change_analysis_counts_or_hide_omissions(tmp_path):
    for number in range(1, 5):
        put(tmp_path, number, "claimed", task_id=f"task-{number}")
    limited, full = report(tmp_path, 1), report(tmp_path, 20)
    assert limited["summary"] == full["summary"]
    assert limited["summary"]["claims_without_later_result_in_read_entries"] == 4
    assert len(limited["tasks"]) == 1
    assert limited["tasks"][0]["evidence"][-1]["ordinal"] == 4
    assert limited["display"]["tasks_omitted"] == 3


def test_source_file_limit_is_explicit_not_a_complete_recent_snapshot(tmp_path, monkeypatch):
    from agent_authority import whiteboard

    put(tmp_path, 1)
    put(tmp_path, 2)
    monkeypatch.setattr(whiteboard, "MAX_FILES", 1)
    value = report(tmp_path)
    assert value["source"]["files_seen"] == 2
    assert value["source"]["files_examined"] == 1
    assert value["source"]["complete_observed_read"] is False
    assert value["warnings"][0]["code"] == "input_limit"


def test_oversized_input_is_not_read_into_the_report(tmp_path):
    path = put(tmp_path, 1)
    path.write_bytes(b"x" * 65_537)
    value = report(tmp_path)
    assert value["warnings"][0]["code"] == "entry_too_large"
    assert value["source"]["entries_read"] == 0


def test_symlinked_entry_and_fifo_are_not_followed_or_blocking(tmp_path):
    path = put(tmp_path, 1)
    private = tmp_path / "private.txt"
    private.write_text(CANARY)
    path.unlink()
    path.symlink_to(private)
    fifo = path.parent / "000000000002.json"
    os.mkfifo(fifo)
    value = report(tmp_path)
    assert value["source"]["entries_read"] == 0
    assert value["source"]["complete_observed_read"] is False
    assert {w["code"] for w in value["warnings"]} == {"unreadable_entry", "nonregular_entry"}
    assert CANARY not in json.dumps(value)


def test_symlinked_thread_is_not_followed(tmp_path):
    other = tmp_path / "other"
    put(other, 1)
    folder = tmp_path / "whiteboard"
    folder.mkdir()
    (folder / THREAD).symlink_to(other / "whiteboard" / THREAD, target_is_directory=True)
    assert report(tmp_path)["warnings"][0]["code"] == "source_unavailable"


def test_missing_store_and_invalid_thread_do_not_create_files(tmp_path):
    missing = tmp_path / "does-not-exist"
    assert report(missing)["source"]["complete_observed_read"] is False
    assert not missing.exists()
    invalid = read_whiteboard(tmp_path, "../../private")
    assert invalid.diagnostics[0].code == "invalid_thread_id"
    assert invalid.source.identifier == ""


def test_observed_file_change_and_new_entry_make_the_snapshot_incomplete(tmp_path, monkeypatch):
    from agent_authority import whiteboard

    path = put(tmp_path, 1)
    original = whiteboard._read_entry

    def changed(directory, name, thread_id):
        value = original(directory, name, thread_id)
        path.write_text(path.read_text() + " ")
        put(tmp_path, 2)
        return value

    monkeypatch.setattr(whiteboard, "_read_entry", changed)
    value = report(tmp_path)
    assert value["source"]["complete_observed_read"] is False
    assert any(w["code"] == "source_changed" for w in value["warnings"])


def test_actual_cli_formats_and_exit_status_preserve_diagnostic_scope(tmp_path, capsys):
    put(tmp_path, 1)
    args = ["inspect", "--store", str(tmp_path), "--thread", THREAD]
    assert main([*args, "--format", "json"]) == 0
    value = json.loads(capsys.readouterr().out)
    assert value["source"]["identity"] == "UNBEKANNT"
    assert main(args) == 0
    assert "Ergebnis gemeldet" in capsys.readouterr().out
    assert main(["inspect", "--store", str(tmp_path / "missing"), "--thread", THREAD]) == 2
    assert "unvollständig" in capsys.readouterr().out


def test_product_command_does_not_import_or_construct_historical_lab(tmp_path):
    put(tmp_path, 1)
    code = """
import sys
from agent_authority.cli import main
assert main(['inspect', '--store', sys.argv[1], '--thread', sys.argv[2], '--format', 'json']) == 0
assert not any(k == 'lab' or k.startswith('lab.') for k in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(tmp_path), THREAD],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["role"] == "observer_only"
