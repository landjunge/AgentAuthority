"""Bounded read-only projection of local ThreadDesk archive records."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ID = re.compile(r"[0-9a-f]{12}\Z")
KINDS = frozenset(
    {"note", "task", "claimed", "progress", "result", "decision", "problem", "question", "system"}
)
ACTORS = frozenset(
    {"human", "grok", "claude", "codex", "chatgpt", "gnom-hub-v1", "local-assistant", "system"}
)
MAX_FILES = 10_000
MAX_BYTES = 65_536
Signature = tuple[int, int, int, int, int]


@dataclass(frozen=True)
class Entry:
    identifier: str
    ordinal: int
    kind: str
    reported_actor_type: str
    task_key: str | None
    file_sha256: str

    def reference(self) -> dict[str, Any]:
        return {
            "entry_id": self.identifier,
            "ordinal": self.ordinal,
            "file_sha256": self.file_sha256,
        }


@dataclass(frozen=True)
class Diagnostic:
    code: str
    entry_id: str | None = None


@dataclass(frozen=True)
class Snapshot:
    thread_id: str
    entries: tuple[Entry, ...]
    diagnostics: tuple[Diagnostic, ...]
    files_seen: int
    files_examined: int


class ReadIssue(Exception):
    """A fixed diagnostic code; never includes source contents or OS error text."""


def _signature(value: os.stat_result) -> Signature:
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise ValueError("non-finite JSON value")


def _read_entry(directory: int, name: str, thread_id: str) -> tuple[Entry, Signature]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW, dir_fd=directory)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise ReadIssue("nonregular_entry")
        if before.st_size > MAX_BYTES:
            raise ReadIssue("entry_too_large")
        raw = bytearray()
        while len(raw) <= MAX_BYTES:
            chunk = os.read(descriptor, min(8192, MAX_BYTES + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        if len(raw) > MAX_BYTES:
            raise ReadIssue("entry_too_large")
        after = os.fstat(descriptor)
        if _signature(before) != _signature(after):
            raise ReadIssue("source_changed")
    finally:
        os.close(descriptor)
    try:
        record = json.loads(raw, object_pairs_hook=_unique, parse_constant=_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ReadIssue("invalid_json") from exc
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
    return Entry(
        name[:-5], ordinal, kind, actor, task, hashlib.sha256(raw).hexdigest()
    ), _signature(after)


def read_whiteboard(store: Path, thread_id: str) -> Snapshot:
    """Read a selected archive. Completeness covers only this observed directory."""
    if not ID.fullmatch(thread_id):
        return Snapshot("", (), (Diagnostic("invalid_thread_id"),), 0, 0)
    if (
        os.open not in os.supports_dir_fd
        or os.listdir not in os.supports_fd
        or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
    ):
        return Snapshot(thread_id, (), (Diagnostic("unsupported_reader_platform"),), 0, 0)
    path = store.expanduser() / "whiteboard" / thread_id
    try:
        directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        return Snapshot(thread_id, (), (Diagnostic("source_unavailable"),), 0, 0)
    entries: list[Entry] = []
    diagnostics: list[Diagnostic] = []
    signatures: dict[str, Signature] = {}
    examined = 0
    names: list[str] = []
    try:
        identity = os.fstat(directory)
        names = sorted(name for name in os.listdir(directory) if name.endswith(".json"))
        if len(names) > MAX_FILES:
            diagnostics.append(Diagnostic("input_limit"))
        for name in names[:MAX_FILES]:
            examined += 1
            if not ID.fullmatch(name[:-5]):
                diagnostics.append(Diagnostic("invalid_filename"))
                continue
            try:
                entry, signature = _read_entry(directory, name, thread_id)
            except ReadIssue as exc:
                diagnostics.append(Diagnostic(str(exc), name[:-5]))
            except OSError:
                diagnostics.append(Diagnostic("unreadable_entry", name[:-5]))
            else:
                entries.append(entry)
                signatures[name] = signature
        changed = names != sorted(name for name in os.listdir(directory) if name.endswith(".json"))
        for name, signature in signatures.items():
            try:
                changed |= signature != _signature(
                    os.stat(name, dir_fd=directory, follow_symlinks=False)
                )
            except OSError:
                changed = True
        try:
            current = path.stat(follow_symlinks=False)
            changed |= (identity.st_dev, identity.st_ino) != (current.st_dev, current.st_ino)
        except OSError:
            changed = True
        if changed:
            diagnostics.append(Diagnostic("source_changed"))
    except OSError:
        diagnostics.append(Diagnostic("source_unavailable"))
    finally:
        os.close(directory)
    return Snapshot(thread_id, tuple(entries), tuple(diagnostics), len(names), examined)
