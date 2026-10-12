"""ThreadDesk archive adapter; its identifiers and vocabulary stay source-specific."""

from __future__ import annotations

import re
from pathlib import Path

from agent_authority.file_reader import (
    MAX_FILES,
    ReadBudget,
    ReadIssue,
    Signature,
    read_directory,
    read_record,
)
from agent_authority.observations import KINDS, Diagnostic, Entry, Snapshot, Source

ID = re.compile(r"[0-9a-f]{12}\Z")
ACTORS = frozenset(
    {"human", "grok", "claude", "codex", "chatgpt", "gnom-hub-v1", "local-assistant", "system"}
)


def _read_entry(
    directory: int, name: str, thread_id: str, budget: ReadBudget
) -> tuple[Entry, Signature]:
    if not ID.fullmatch(name[:-5]):
        raise ReadIssue("invalid_filename")
    record, digest, signature = read_record(directory, name, budget)
    if not isinstance(record, dict):
        raise ReadIssue("invalid_entry")
    if record.get("id") != name[:-5] or record.get("thread_id") != thread_id:
        raise ReadIssue("entry_identity_mismatch")
    ordinal, kind, actor = record.get("ordinal"), record.get("entry_type"), record.get("actor_type")
    task = record.get("task_id")
    if (
        type(ordinal) is not int
        or not 0 <= ordinal < 2**63
        or not isinstance(kind, str)
        or kind not in KINDS
        or not isinstance(actor, str)
        or actor not in ACTORS
        or (task is not None and (not isinstance(task, str) or not task.strip() or len(task) > 300))
    ):
        raise ReadIssue("invalid_entry")
    return Entry(name[:-5], ordinal, kind, actor, task, digest), signature


def read_whiteboard(store: Path, thread_id: str) -> Snapshot:
    """Map a selected local archive to minimized observations, without authentication."""
    if not ID.fullmatch(thread_id):
        return Snapshot(
            Source("threaddesk-whiteboard", ""), (), (Diagnostic("invalid_thread_id"),), 0, 0
        )
    return read_directory(
        store.expanduser() / "whiteboard" / thread_id,
        Source("threaddesk-whiteboard", thread_id),
        lambda directory, name, budget: _read_entry(directory, name, thread_id, budget),
        max_files=MAX_FILES,
    )
