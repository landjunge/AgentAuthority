"""Admission bounds tested on real files and instrumented streaming directory scans."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from agent_authority import file_reader
from agent_authority.cli import main
from agent_authority.html_report import render_html
from agent_authority.json_source import SCHEMA, read_observations
from agent_authority.report import build_report, render_text
from agent_authority.whiteboard import read_whiteboard


def put(path, number, adapter, size=None):
    path.mkdir(parents=True, exist_ok=True)
    if adapter == "neutral":
        identifier = f"event-{number:05d}"
        record = {
            "schema_version": SCHEMA,
            "id": identifier,
            "source_id": "run",
            "ordinal": number,
            "kind": "result",
            "reported_actor_type": "test-client",
        }
    else:
        identifier = f"{number:012x}"
        record = {
            "id": identifier,
            "thread_id": "123456abcdef",
            "ordinal": number,
            "entry_type": "result",
            "actor_type": "codex",
        }
    raw = json.dumps(record).encode()
    if size is not None:
        assert len(raw) <= size
        raw = raw.ljust(size, b" ")
    target = path / f"{identifier}.json"
    target.write_bytes(raw)
    return target


def source(tmp_path, adapter):
    if adapter == "neutral":
        return tmp_path, lambda: read_observations(tmp_path, "run")
    folder = tmp_path / "whiteboard" / "123456abcdef"
    return folder, lambda: read_whiteboard(tmp_path, "123456abcdef")


@pytest.mark.parametrize("adapter", ["neutral", "threaddesk"])
def test_many_real_entries_are_capped_and_counts_are_explicit_lower_bounds(
    tmp_path, monkeypatch, adapter
):
    folder, read = source(tmp_path, adapter)
    for number in range(1, 51):
        put(folder, number, adapter)
    monkeypatch.setattr(file_reader, "MAX_DIRECTORY_ENTRIES", 5)
    monkeypatch.setattr(file_reader.os, "listdir", lambda *args: pytest.fail("unbounded listdir"))
    value = build_report(read())
    assert value["source"]["entries_read"] == 5
    assert value["source"]["directory_entries_seen"] == 6
    assert value["source"]["files_seen"] == 6
    assert value["source"]["files_seen_is_lower_bound"] is True
    assert value["source"]["complete_observed_read"] is False
    assert {w["code"] for w in value["warnings"]} == {"directory_limit"}
    assert "mindestens 6" in render_html(value)
    assert "mindestens 6" in render_text(value)


@pytest.mark.parametrize("adapter", ["neutral", "threaddesk"])
def test_non_json_entries_also_consume_directory_budget(tmp_path, monkeypatch, adapter):
    folder, read = source(tmp_path, adapter)
    folder.mkdir(parents=True, exist_ok=True)
    for number in range(30):
        (folder / f"ignored-{number}.txt").write_text("ignored")
    monkeypatch.setattr(file_reader, "MAX_DIRECTORY_ENTRIES", 5)
    value = build_report(read())
    assert value["source"]["files_seen"] == value["source"]["bytes_read"] == 0
    assert value["source"]["directory_entries_seen"] == 6
    assert value["source"]["complete_observed_read"] is False
    assert value["warnings"][0]["code"] == "directory_limit"


def test_streaming_scanner_consumes_only_cap_plus_one_and_closes_iterator(monkeypatch):
    class HugeDirectory:
        def __init__(self):
            self.count = 0
            self.closed = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.closed = True

        def __iter__(self):
            return self

        def __next__(self):
            self.count += 1
            if self.count > file_reader.MAX_DIRECTORY_ENTRIES + 1:
                pytest.fail("enumeration continued past bounded overflow probe")
            return SimpleNamespace(name=f"file-{self.count}.json")

    iterator = HugeDirectory()
    monkeypatch.setattr(file_reader.os, "scandir", lambda descriptor: iterator)
    scan = file_reader._scan_directory(0)
    assert iterator.count == file_reader.MAX_DIRECTORY_ENTRIES + 1
    assert len(scan.names) == file_reader.MAX_DIRECTORY_ENTRIES
    assert scan.complete is False
    assert iterator.closed is True


@pytest.mark.parametrize("adapter", ["neutral", "threaddesk"])
def test_total_raw_byte_budget_limits_many_individually_legal_files(tmp_path, adapter):
    folder, read = source(tmp_path, adapter)
    for number in range(1, 131):
        put(folder, number, adapter, file_reader.MAX_BYTES)
    value = build_report(read())
    assert value["source"]["bytes_read"] == file_reader.MAX_TOTAL_BYTES == 8 * 1024 * 1024
    assert value["source"]["entries_read"] == 128
    assert value["source"]["files_examined"] == 129
    assert value["source"]["files_seen"] == 130
    assert value["source"]["files_seen_is_lower_bound"] is False
    assert value["source"]["complete_observed_read"] is False
    assert value["warnings"][0]["code"] == "input_byte_limit"


def test_invalid_json_consumes_same_total_budget_as_valid_records(tmp_path, monkeypatch):
    for number in range(1, 11):
        (tmp_path / f"event-{number:05d}.json").write_bytes(b"!" * 100)
    monkeypatch.setattr(file_reader, "MAX_TOTAL_BYTES", 200)
    value = build_report(read_observations(tmp_path, "run"))
    assert value["source"]["bytes_read"] == 200
    assert value["source"]["files_examined"] == 3
    assert [w["code"] for w in value["warnings"]] == [
        "invalid_json",
        "invalid_json",
        "input_byte_limit",
    ]


def test_growing_file_can_exceed_total_budget_by_at_most_one_probe_byte(tmp_path, monkeypatch):
    path = put(tmp_path, 1, "neutral")
    size = path.stat().st_size
    monkeypatch.setattr(file_reader, "MAX_TOTAL_BYTES", size)
    original = file_reader.os.read
    changed = False

    def growing(descriptor, count):
        nonlocal changed
        if not changed:
            changed = True
            with path.open("ab") as target:
                target.write(b" " * 100)
        return original(descriptor, count)

    monkeypatch.setattr(file_reader.os, "read", growing)
    value = build_report(read_observations(tmp_path, "run"))
    assert value["source"]["bytes_read"] == size + 1
    assert value["source"]["entries_read"] == 0
    assert value["warnings"][0]["code"] == "input_byte_limit"


def test_exact_directory_and_byte_boundaries_can_still_be_complete(tmp_path, monkeypatch):
    a = put(tmp_path, 1, "neutral")
    b = put(tmp_path, 2, "neutral")
    monkeypatch.setattr(file_reader, "MAX_DIRECTORY_ENTRIES", 2)
    monkeypatch.setattr(file_reader, "MAX_TOTAL_BYTES", a.stat().st_size + b.stat().st_size)
    value = build_report(read_observations(tmp_path, "run"))
    assert value["source"]["complete_observed_read"] is True
    assert value["source"]["entries_read"] == 2
    assert value["source"]["files_seen_is_lower_bound"] is False
    assert value["source"]["bytes_read"] == file_reader.MAX_TOTAL_BYTES


def test_second_scan_is_bounded_even_when_source_grows_during_read(tmp_path, monkeypatch):
    from agent_authority import json_source

    put(tmp_path, 1, "neutral")
    original = json_source._read_entry
    visits = []
    original_scan = file_reader.os.scandir
    monkeypatch.setattr(file_reader, "MAX_DIRECTORY_ENTRIES", 3)

    def changed(directory, name, source_id, budget):
        value = original(directory, name, source_id, budget)
        for number in range(2, 30):
            put(tmp_path, number, "neutral")
        return value

    class Counted:
        def __init__(self, descriptor):
            self.iterator = original_scan(descriptor)
            self.count = 0

        def __enter__(self):
            self.iterator.__enter__()
            return self

        def __exit__(self, *args):
            visits.append(self.count)
            return self.iterator.__exit__(*args)

        def __iter__(self):
            return self

        def __next__(self):
            value = next(self.iterator)
            self.count += 1
            return value

    # Preserve the platform-support check for the wrapped function.
    monkeypatch.setattr(file_reader.os, "supports_fd", file_reader.os.supports_fd | {Counted})
    monkeypatch.setattr(file_reader.os, "scandir", Counted)
    monkeypatch.setattr(json_source, "_read_entry", changed)
    value = build_report(read_observations(tmp_path, "run"))
    assert visits == [1, 4]
    assert value["source"]["complete_observed_read"] is False
    assert {w["code"] for w in value["warnings"]} == {"source_changed", "directory_limit"}


def test_deep_json_is_rejected_without_a_parser_crash(tmp_path):
    path = put(tmp_path, 1, "neutral")
    path.write_bytes(b"[" * 2000 + b"0" + b"]" * 2000)
    value = build_report(read_observations(tmp_path, "run"))
    # This is syntactically valid JSON, but not an observation object.
    # Decoder recursion limits vary by Python/runtime; both rejection paths are valid.
    assert value["warnings"][0]["code"] in {"invalid_json", "invalid_entry"}
    assert value["source"]["entries_read"] == 0
    assert value["source"]["complete_observed_read"] is False
    assert value["source"]["bytes_read"] == 4001


def test_oversized_file_and_fifo_do_not_consume_raw_byte_budget(tmp_path):
    import os

    path = put(tmp_path, 1, "neutral")
    path.write_bytes(b"!" * (file_reader.MAX_BYTES + 1))
    os.mkfifo(tmp_path / "event-00002.json")
    value = build_report(read_observations(tmp_path, "run"))
    assert value["source"]["bytes_read"] == 0
    assert {w["code"] for w in value["warnings"]} == {"entry_too_large", "nonregular_entry"}


def test_limit_reached_is_an_incomplete_cli_result(tmp_path, monkeypatch, capsys):
    for number in range(1, 5):
        put(tmp_path, number, "neutral")
    monkeypatch.setattr(file_reader, "MAX_DIRECTORY_ENTRIES", 2)
    assert (
        main(
            [
                "inspect",
                "--source",
                "json-directory",
                "--input",
                str(tmp_path),
                "--source-id",
                "run",
                "--format",
                "json",
            ]
        )
        == 2
    )
    value = json.loads(capsys.readouterr().out)
    assert value["source"]["files_seen_is_lower_bound"] is True
    assert value["source"]["source_authenticated"] is False
