"""Neutral contract acceptance, including a second real file adapter and import boundaries."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys

import pytest

from agent_authority.cli import main
from agent_authority.html_report import render_html
from agent_authority.json_source import SCHEMA, read_observations
from agent_authority.observations import Entry, Snapshot, Source
from agent_authority.report import build_report, render_text
from agent_authority.whiteboard import read_whiteboard


def put(folder, **changes):
    folder.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": SCHEMA,
        "id": "event-1",
        "source_id": "local-run",
        "ordinal": 1,
        "kind": "result",
        "reported_actor_type": "independent-client",
        "task_key": "PRIVATE_TASK",
        "content": "PRIVATE_CONTENT",
        "metadata": {"source_authenticated": True, "effect": "BELEGT"},
        **changes,
    }
    path = folder / "event-1.json"
    path.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return path


def test_neutral_contract_and_all_renderers_work_without_any_adapter_import():
    code = """
import sys
from agent_authority.observations import Entry, Snapshot, Source
from agent_authority.report import build_report, render_text
from agent_authority.html_report import render_html
s = Snapshot(Source('independent-source', 'run-42'),
             (Entry('event-1', 1, 'result', 'other-client', None, 'a'*64),), (), 1, 1)
r = build_report(s)
assert r['schema_version'] == 'agent-authority-observation-report-v1'
assert r['source']['source_id'] == 'run-42'
assert r['source']['identity'] == r['source']['effect'] == 'UNBEKANNT'
assert 'thread_id' not in r['source']
assert 'ThreadDesk' not in render_text(r) + render_html(r)
assert not any(k in sys.modules for k in ('agent_authority.whiteboard',
           'agent_authority.json_source', 'agent_authority.file_reader', 'lab'))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", code], capture_output=True, text=True, timeout=10, check=False
    )
    assert result.returncode == 0, result.stderr


def test_neutral_files_are_read_minimized_and_never_authenticate_claims(tmp_path):
    path = put(tmp_path)
    before = path.read_bytes()
    value = build_report(read_observations(tmp_path, "local-run"))
    assert value["source"]["complete_observed_read"] is True
    assert value["source"]["kind"] == "json-directory"
    assert value["recent_entries"][0]["reported_actor_type"] == "independent-client"
    assert value["recent_entries"][0]["file_sha256"] == hashlib.sha256(before).hexdigest()
    for output in [json.dumps(value), render_text(value), render_html(value)]:
        assert "PRIVATE" not in output
        assert "BELEGT" not in output
        assert "ThreadDesk" not in output
    assert value["source"]["source_authenticated"] is False
    assert value["task_completion_proven"] is value["rights_inherited"] is False
    assert path.read_bytes() == before
    assert list(tmp_path.iterdir()) == [path]


def test_both_adapters_produce_identical_analysis_for_equivalent_claims(tmp_path):
    neutral = tmp_path / "neutral"
    put(neutral, id="event-1", reported_actor_type="codex")
    td = tmp_path / "store" / "whiteboard" / "123456abcdef"
    td.mkdir(parents=True)
    (td / "000000000001.json").write_text(
        json.dumps(
            {
                "id": "000000000001",
                "thread_id": "123456abcdef",
                "ordinal": 1,
                "entry_type": "result",
                "actor_type": "codex",
                "task_id": "PRIVATE_TASK",
            }
        )
    )
    a = build_report(read_observations(neutral, "local-run"))
    b = build_report(read_whiteboard(tmp_path / "store", "123456abcdef"))
    assert a["schema_version"] == b["schema_version"]
    assert a["summary"] == b["summary"]
    assert a["tasks"][0]["last_reported_kind"] == b["tasks"][0]["last_reported_kind"]
    assert a["source"]["scope"] == b["source"]["scope"] == "selected_local_observations"
    assert a["source"]["kind"] != b["source"]["kind"]


@pytest.mark.parametrize(
    "changes",
    [
        {"schema_version": "forged"},
        {"id": "different"},
        {"source_id": "other"},
        {"ordinal": True},
        {"ordinal": -1},
        {"kind": ["result"]},
        {"kind": "ALLOW"},
        {"reported_actor_type": ""},
        {"reported_actor_type": "x" * 81},
        {"reported_actor_type": ["codex"]},
        {"task_key": "x" * 301},
    ],
)
def test_invalid_neutral_contracts_remain_incomplete(tmp_path, changes):
    put(tmp_path, **changes)
    value = build_report(read_observations(tmp_path, "local-run"))
    assert value["source"]["complete_observed_read"] is False
    assert value["source"]["entries_read"] == 0
    assert value["warnings"]


@pytest.mark.parametrize("format", ["text", "json", "html"])
def test_neutral_cli_needs_no_threaddesk_store(tmp_path, capsys, format):
    put(tmp_path, reported_actor_type="client-ä")
    assert (
        main(
            [
                "inspect",
                "--source",
                "json-directory",
                "--input",
                str(tmp_path),
                "--source-id",
                "local-run",
                "--format",
                format,
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "ThreadDesk" not in output
    if format in {"json", "html"}:
        assert "client-ä" in output


@pytest.mark.parametrize("extra", [[], ["--thread", "123456abcdef"], ["--store", "/tmp"]])
def test_cli_rejects_missing_or_mixed_adapter_arguments(tmp_path, extra):
    args = ["inspect", "--source", "json-directory", *extra]
    if extra:
        args += ["--input", str(tmp_path), "--source-id", "local-run"]
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2


def test_neutral_invalid_source_and_symlink_remain_diagnosed(tmp_path):
    put(tmp_path)
    assert read_observations(tmp_path, "../private").diagnostics[0].code == "invalid_source_id"
    link = tmp_path.parent / (tmp_path.name + "-link")
    link.symlink_to(tmp_path, target_is_directory=True)
    assert read_observations(link, "local-run").diagnostics[0].code == "source_unavailable"


def test_snapshot_is_frozen_and_rejects_authority_as_observation_kind():
    from dataclasses import FrozenInstanceError

    snapshot = Snapshot(Source("local", "run"), (), (), 0, 0)
    with pytest.raises(FrozenInstanceError):
        snapshot.files_seen = 1
    with pytest.raises(ValueError):
        Entry("event-1", 1, "ALLOW", "client", None, "a" * 64)
