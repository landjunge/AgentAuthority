"""Source-neutral, minimized observations; claims never authenticate identity or effects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}\Z")
KINDS = frozenset(
    {
        "note",
        "task",
        "claimed",
        "progress",
        "result",
        "decision",
        "problem",
        "question",
        "system",
        "plan",
        "handoff",
    }
)


@dataclass(frozen=True)
class Source:
    kind: str
    identifier: str

    def __post_init__(self) -> None:
        if not TOKEN.fullmatch(self.kind) or (
            self.identifier and not TOKEN.fullmatch(self.identifier)
        ):
            raise ValueError("invalid source reference")


@dataclass(frozen=True)
class Entry:
    identifier: str
    ordinal: int
    kind: str
    reported_actor_type: str
    task_key: str | None
    file_sha256: str

    def __post_init__(self) -> None:
        if (
            not TOKEN.fullmatch(self.identifier)
            or type(self.ordinal) is not int
            or not 0 <= self.ordinal < 2**63
            or self.kind not in KINDS
            or not isinstance(self.reported_actor_type, str)
            or not self.reported_actor_type.strip()
            or len(self.reported_actor_type) > 80
            or (
                self.task_key is not None
                and (
                    not isinstance(self.task_key, str)
                    or not self.task_key.strip()
                    or len(self.task_key) > 300
                )
            )
            or not re.fullmatch(r"[0-9a-f]{64}", self.file_sha256)
        ):
            raise ValueError("invalid observation")

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
    source: Source
    entries: tuple[Entry, ...]
    diagnostics: tuple[Diagnostic, ...]
    files_seen: int
    files_examined: int
    directory_entries_seen: int = 0
    directory_scan_complete: bool = True
    bytes_read: int = 0
