"""Source-neutral local JSON observation adapter; no source-provided trust upgrade."""

from __future__ import annotations

from pathlib import Path

from agent_authority.file_reader import (
    ReadBudget,
    ReadIssue,
    Signature,
    read_directory,
    read_record,
)
from agent_authority.observations import TOKEN, Diagnostic, Entry, Snapshot, Source

SCHEMA = "agent-authority-observation-v1"


def _read_entry(
    directory: int, name: str, source_id: str, budget: ReadBudget
) -> tuple[Entry, Signature]:
    if not TOKEN.fullmatch(name[:-5]):
        raise ReadIssue("invalid_filename")
    record, digest, signature = read_record(directory, name, budget)
    if not isinstance(record, dict) or record.get("schema_version") != SCHEMA:
        raise ReadIssue("invalid_entry")
    if record.get("id") != name[:-5] or record.get("source_id") != source_id:
        raise ReadIssue("entry_identity_mismatch")
    try:
        entry = Entry(
            record["id"],
            record["ordinal"],
            record["kind"],
            record["reported_actor_type"],
            record.get("task_key"),
            digest,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ReadIssue("invalid_entry") from exc
    return entry, signature


def read_observations(path: Path, source_id: str) -> Snapshot:
    if not TOKEN.fullmatch(source_id):
        return Snapshot(Source("json-directory", ""), (), (Diagnostic("invalid_source_id"),), 0, 0)
    return read_directory(
        path,
        Source("json-directory", source_id),
        lambda directory, name, budget: _read_entry(directory, name, source_id, budget),
    )
