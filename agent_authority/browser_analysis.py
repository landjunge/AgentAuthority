"""Bounded local report analysis through the unchanged observation engine.

No graphics, remote rendering, dispatch, worker queue, filesystem or network
access. Busy callers are rejected; an interrupted analysis is never retried.
"""

from __future__ import annotations

import hashlib
import json
import threading
from typing import Any

from agent_authority.browser_contracts import CONTRACT_VERSION, Problem
from agent_authority.browser_support import MAX_BODY, json_bytes as _json
from agent_authority.report import build_report


class LocalReportAnalysis:
    contract_version = CONTRACT_VERSION

    def __init__(self) -> None:
        self._slot = threading.BoundedSemaphore(1)
        self._lock = threading.Lock()
        self._active = self._completed = self._failed = self._rejected = 0

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "scope": "process",
                "concurrencyLimit": 1,
                "active": self._active,
                "completed": self._completed,
                "failed": self._failed,
                "rejectedBusy": self._rejected,
                "waitingJobs": 0,
                "durableQueue": False,
                "automaticRetry": False,
            }

    def project(self, source: str, job: str, adapter: str, data: Any) -> dict[str, Any]:
        if not self._slot.acquire(blocking=False):
            with self._lock:
                self._rejected += 1
            raise Problem(429, "ANALYSIS_BUSY")
        try:
            with self._lock:
                self._active = 1
            result = self._project(source, job, adapter, data)
            with self._lock:
                self._completed += 1
            return result
        except BaseException:
            with self._lock:
                self._failed += 1
            raise
        finally:
            with self._lock:
                self._active = 0
            self._slot.release()

    def _project(self, source: str, job: str, adapter: str, data: Any) -> dict[str, Any]:
        from agent_authority.browser_model import decode_report

        try:
            if adapter == "observations":
                report = self.observation_report(data, source)
                return {"report": report, "graph": decode_report(report)}
            if adapter == "report":
                graph = decode_report(data)
                report = json.loads(graph["reportJSON"])
                if report["source"]["source_id"] != source:
                    raise ValueError("source mismatch")
                return {"report": report, "graph": graph}
            if adapter == "private-verification":
                from agent_authority.browser_adapter import adapt_private_report

                payload = adapt_private_report(data, source, job)
                payload["report"] = None
                return payload
            raise Problem(422, "UNSUPPORTED_ADAPTER")
        except Problem:
            raise
        except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
            raise Problem(422, "INVALID_REPORT") from exc

    @staticmethod
    def observation_report(data: Any, source: str) -> dict[str, Any]:
        """Use the existing bounded reader and engine, never browser-supplied paths.

        The caller provides an exact JSON array of neutral observation records.
        No temporary on-disk observation copy is needed: Entry validation and
        Snapshot/build_report are the same engine boundary as json_source.
        """
        from agent_authority.observations import Entry, Snapshot, Source

        if not isinstance(data, list) or len(data) > 10_000:
            raise ValueError("observation limit")
        entries, identifiers = [], set()
        total = 0
        for record in data:
            if (
                not isinstance(record, dict)
                or not {
                    "schema_version",
                    "id",
                    "source_id",
                    "ordinal",
                    "kind",
                    "reported_actor_type",
                }
                <= set(record)
                or set(record)
                - {
                    "schema_version",
                    "id",
                    "source_id",
                    "ordinal",
                    "kind",
                    "reported_actor_type",
                    "task_key",
                }
                or record["schema_version"] != "agent-authority-observation-v1"
                or record["source_id"] != source
            ):
                raise ValueError("invalid observation")
            raw = _json(record)
            total += len(raw)
            if len(raw) > 65536 or total > MAX_BODY:
                raise ValueError("observation byte limit")
            entry = Entry(
                record["id"],
                record["ordinal"],
                record["kind"],
                record["reported_actor_type"],
                record.get("task_key"),
                hashlib.sha256(raw).hexdigest(),
            )
            if entry.identifier in identifiers:
                raise ValueError("duplicate observation")
            identifiers.add(entry.identifier)
            entries.append(entry)
        snapshot = Snapshot(
            Source("json-directory", source),
            tuple(entries),
            (),
            len(entries),
            len(entries),
            len(entries),
            True,
            total,
        )
        report = build_report(snapshot, limit=100)
        # SHA-256 here covers the documented canonical import serialization, not
        # unknown original file bytes. Store that provenance alongside the report.
        return report
