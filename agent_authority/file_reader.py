"""Read-only file mechanics shared by source adapters."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agent_authority.observations import Diagnostic, Entry, Snapshot, Source

MAX_FILES = 10_000
MAX_BYTES = 65_536
Signature = tuple[int, int, int, int, int]


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


def read_record(directory: int, name: str) -> tuple[Any, str, Signature]:
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
    return record, hashlib.sha256(raw).hexdigest(), _signature(after)


def read_directory(
    path: Path,
    source: Source,
    read_entry: Callable[[int, str], tuple[Entry, Signature]],
    max_files: int = MAX_FILES,
) -> Snapshot:
    """Read a selected directory. Completeness covers only this observed directory."""
    if (
        os.open not in os.supports_dir_fd
        or os.listdir not in os.supports_fd
        or not hasattr(os, "O_NOFOLLOW")
        or not hasattr(os, "O_DIRECTORY")
    ):
        return Snapshot(source, (), (Diagnostic("unsupported_reader_platform"),), 0, 0)
    path = path.expanduser()
    try:
        directory = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        return Snapshot(source, (), (Diagnostic("source_unavailable"),), 0, 0)
    entries: list[Entry] = []
    diagnostics: list[Diagnostic] = []
    signatures: dict[str, Signature] = {}
    examined = 0
    names: list[str] = []
    try:
        identity = os.fstat(directory)
        names = sorted(name for name in os.listdir(directory) if name.endswith(".json"))
        if len(names) > max_files:
            diagnostics.append(Diagnostic("input_limit"))
        for name in names[:max_files]:
            examined += 1
            try:
                entry, signature = read_entry(directory, name)
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
    return Snapshot(source, tuple(entries), tuple(diagnostics), len(names), examined)
