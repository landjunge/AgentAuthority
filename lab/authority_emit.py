"""G3: emit Authority Event Envelope. Never a ThreadDesk DB. Never changes ALLOW/DENY."""

from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from lab.models import ActionRequest, Decision

SOURCE = "agent-authority-lab"


def enabled() -> bool:
    raw = (os.environ.get("LAB_AUTHORITY_EVENTS") or "").strip().lower()
    if not raw:
        return not bool(os.environ.get("PYTEST_CURRENT_TEST"))
    return raw not in ("0", "false", "off", "no")


def events_path() -> Path:
    override = (os.environ.get("LAB_AUTHORITY_EVENTS_PATH") or "").strip()
    if override:
        return Path(override).expanduser()
    return Path.cwd() / "data" / "authority-events.jsonl"


def _iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(event: dict[str, Any]) -> bytes:
    body = {k: v for k, v in event.items() if k != "event_hash"}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def _hash(event: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(event)).hexdigest()


def _last_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    last = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                last = json.loads(line).get("event_hash")
            except json.JSONDecodeError:
                continue
    return str(last) if last else None


def _append(event_type: str, req: ActionRequest, decision: Decision) -> dict[str, Any] | None:
    path = events_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    wf = req.workflow_id
    event: dict[str, Any] = {
        "schema_version": "1",
        "event_id": uuid.uuid4().hex[:16],
        "timestamp": _iso(),
        "trace_id": wf,
        "span_id": uuid.uuid4().hex[:8],
        "workflow_id": wf,
        "project_id": "agent-authority-lab",
        "source_tool": SOURCE,
        "event_type": event_type,
        "actor": {"agent_id": req.actor, "role": "lab-agent"},
        "action": req.action,
        "resource": req.resource,
        "decision": "ALLOW" if decision.allow else "DENY",
        "reason_code": decision.deny_reason,
        "previous_event_hash": _last_hash(path),
        "data_labels": ["PUBLIC"],
    }
    event["event_hash"] = _hash(event)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=True) + "\n")
    return event


def emit_decision(req: ActionRequest, decision: Decision) -> None:
    """Side channel only. Must not raise into Lab.submit."""
    if not enabled():
        return
    try:
        _append("authority.requested", req, decision)
        kind = "authority.allowed" if decision.allow else "authority.denied"
        _append(kind, req, decision)
    except Exception:  # noqa: BLE001  fail-open: emit must not raise into submit
        return
