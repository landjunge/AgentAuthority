"""Private local v1 result storage; deliberately one host, not shared infrastructure.

The state lease prevents multiple service instances from multiplying process-local
session and admission limits. The repository also serializes quota+insert in SQLite
so its storage contract holds across independent connections on this same host.
Neither boundary claims to coordinate different hosts or network filesystems.
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import sqlite3
import stat
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from agent_authority.browser_contracts import ADAPTERS, CONTRACT_VERSION, Principal, Problem
from agent_authority.observations import TOKEN

MAX_REPORTS = 50
MAX_ACCOUNT_BYTES = 64 * 1024 * 1024
MAX_OUTPUT = 24 * 1024 * 1024
SQLITE_TIMEOUT = 2.0


def _check_state(path: Path) -> None:
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
        raise ValueError("state must be a private owned directory (0700)")


def _private_descriptor(path: Path) -> int:
    """Create privately or inspect the opened inode, without following symlinks."""
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    except OSError as exc:
        raise ValueError("private regular owned state file required") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ValueError("private regular owned state file required")
    except BaseException:
        os.close(fd)
        raise
    return fd


class StateLease:
    """Fail closed when another local service owns this exact state directory.

    Keep the lock inode after close: unlinking it would let a later opener bypass
    an existing lease. This is a POSIX local-process guard, not a distributed lock.
    """

    def __init__(self, path: Path):
        self._fd: int | None = None
        _check_state(path)
        try:
            fd = _private_descriptor(path / ".instance.lock")
        except OSError as exc:
            raise ValueError("private state lease unavailable") from exc
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise ValueError("local state already in use or lease unavailable") from exc
        self._fd = fd

    def close(self) -> None:
        fd, self._fd = self._fd, None
        if fd is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


class LocalReportRepository:
    contract_version = CONTRACT_VERSION

    def __init__(self, path: Path):
        _check_state(path)
        database = path / "reports.sqlite3"
        fd = _private_descriptor(database)
        os.close(fd)
        self._lock = threading.RLock()
        self.db = sqlite3.connect(database, timeout=SQLITE_TIMEOUT, check_same_thread=False)
        try:
            self.db.execute("PRAGMA journal_mode=DELETE")
            self.db.execute("PRAGMA synchronous=FULL")
            self.db.execute("PRAGMA secure_delete=ON")
            self.db.execute(
                "CREATE TABLE IF NOT EXISTS reports (owner TEXT NOT NULL, id TEXT NOT NULL, source TEXT NOT NULL, job TEXT NOT NULL, created TEXT NOT NULL, adapter TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(owner,id))"
            )
            self.db.commit()
        except BaseException:
            self.db.close()
            raise

    def close(self) -> None:
        with self._lock:
            self.db.close()

    @staticmethod
    def _scope_filter(principal: Principal) -> tuple[str, list[str]]:
        clauses, parameters = [], []
        for scope in principal.scopes:
            adapters = tuple(adapter for adapter in scope.adapters if adapter in ADAPTERS)
            if not adapters:
                continue
            placeholders = ",".join("?" for _ in adapters)
            clauses.append(f"(source=? AND job=? AND adapter IN ({placeholders}))")
            parameters.extend((scope.source_id, scope.job_id, *adapters))
        return " OR ".join(clauses) or "0", parameters

    @staticmethod
    def _busy(exc: sqlite3.OperationalError) -> None:
        if getattr(exc, "sqlite_errorcode", 0) & 0xFF in (
            sqlite3.SQLITE_BUSY,
            sqlite3.SQLITE_LOCKED,
        ):
            raise Problem(503, "STORAGE_BUSY") from exc
        raise exc

    def listing(self, principal: Principal) -> list[dict[str, Any]]:
        allowed, parameters = self._scope_filter(principal)
        reports, used = [], 0
        with self._lock:
            try:
                rows = self.db.execute(
                    f"SELECT id,source,job,created,adapter,payload FROM reports WHERE owner=? AND ({allowed}) AND length(payload)<=? ORDER BY created DESC LIMIT ?",
                    (principal.subject, *parameters, MAX_OUTPUT, MAX_REPORTS),
                )
                # Existing result bytes remain the authority for the UI state.
                # Decode one already-scoped row at a time, with the same output
                # and account bounds; no JSON1 extension or schema migration is
                # required, and no graph projection/layout is recomputed.
                for row in rows:
                    used += len(row[5])
                    if used > MAX_ACCOUNT_BYTES:
                        raise Problem(409, "STORAGE_LIMIT")
                    metadata = json.loads(row[5]).get("metadata", {})
                    state = metadata.get("state") if isinstance(metadata, dict) else None
                    if not isinstance(state, str) or state not in (
                        "complete",
                        "incomplete",
                        "reported-private-verification",
                    ):
                        state = "unknown"
                    reports.append(
                        {
                            "id": row[0],
                            "title": f"{row[1]} / {row[2]}",
                            "sourceId": row[1],
                            "jobId": row[2],
                            "createdAt": row[3],
                            "adapter": row[4],
                            "state": state,
                        }
                    )
            except sqlite3.OperationalError as exc:
                self._busy(exc)
        return reports

    def get(self, principal: Principal, identifier: str) -> dict[str, Any]:
        allowed, parameters = self._scope_filter(principal)
        with self._lock:
            try:
                row = self.db.execute(
                    f"SELECT payload FROM reports WHERE owner=? AND id=? AND ({allowed}) AND length(payload)<=?",
                    (principal.subject, identifier, *parameters, MAX_OUTPUT),
                ).fetchone()
            except sqlite3.OperationalError as exc:
                self._busy(exc)
        if row is None:
            raise Problem(404, "NOT_FOUND")
        return json.loads(row[0])

    def insert(self, principal: Principal, payload: dict[str, Any]) -> dict[str, Any]:
        """Validate the binding before DB access; persist a detached JSON snapshot.

        The caller generates a new ID/time for each explicit import. Duplicate IDs
        are rejected, never treated as instructions to repeat or replace a result.
        """
        if not isinstance(payload, dict) or not isinstance(payload.get("metadata"), dict):
            raise Problem(422, "INVALID_REPORT")
        metadata = payload["metadata"]
        identifier, source, job, created, adapter = (
            metadata.get(key) for key in ("id", "sourceId", "jobId", "createdAt", "adapter")
        )
        if (
            not isinstance(identifier, str)
            or re.fullmatch(r"[a-f0-9]{32}", identifier) is None
            or any(
                not isinstance(value, str) or not TOKEN.fullmatch(value) for value in (source, job)
            )
            or not isinstance(adapter, str)
            or adapter not in ADAPTERS
            or not isinstance(created, str)
            or len(created) > 64
        ):
            raise Problem(422, "INVALID_REPORT")
        try:
            if datetime.fromisoformat(created).utcoffset() is None:
                raise ValueError("timezone required")
        except ValueError as exc:
            raise Problem(422, "INVALID_REPORT") from exc
        if not any(
            scope.source_id == source and scope.job_id == job and adapter in scope.adapters
            for scope in principal.scopes
        ):
            raise Problem(403, "SCOPE_FORBIDDEN")
        try:
            raw = json.dumps(
                payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False
            ).encode()
        except (TypeError, ValueError, UnicodeError, RecursionError, OverflowError) as exc:
            raise Problem(422, "INVALID_REPORT") from exc
        if len(raw) > MAX_OUTPUT:
            raise Problem(413, "OUTPUT_LIMIT")
        # Return the same detached snapshot that was actually persisted, rather
        # than exposing the caller's mutable metadata as the stored object.
        stored_metadata = json.loads(raw)["metadata"]
        if not isinstance(stored_metadata, dict) or tuple(
            stored_metadata.get(key) for key in ("id", "sourceId", "jobId", "createdAt", "adapter")
        ) != (identifier, source, job, created, adapter):
            raise Problem(422, "INVALID_REPORT")
        with self._lock:
            try:
                self.db.execute("BEGIN IMMEDIATE")
                count, used = self.db.execute(
                    "SELECT COUNT(*), COALESCE(SUM(length(payload)),0) FROM reports WHERE owner=?",
                    (principal.subject,),
                ).fetchone()
                if count >= MAX_REPORTS or used + len(raw) > MAX_ACCOUNT_BYTES:
                    raise Problem(409, "STORAGE_LIMIT")
                self.db.execute(
                    "INSERT INTO reports VALUES (?,?,?,?,?,?,?)",
                    (principal.subject, identifier, source, job, created, adapter, raw),
                )
                self.db.commit()
            except BaseException as exc:
                self.db.rollback()
                if isinstance(exc, sqlite3.IntegrityError):
                    raise Problem(409, "REPORT_EXISTS") from exc
                if isinstance(exc, sqlite3.OperationalError):
                    self._busy(exc)
                raise
        return stored_metadata
