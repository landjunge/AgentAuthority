"""One-target coverage conformance; no writer or host completeness claim."""

from __future__ import annotations

import stat
from pathlib import Path


def describe_snapshot(present: bool | None, *, reason: str) -> dict[str, object]:
    """Describe a supplied snapshot; this does not authenticate its source."""
    if present is not None and type(present) is not bool:
        raise ValueError("invalid target snapshot")
    return {
        "target_effect": "UNBEKANNT" if present is None else "BELEGT" if present else "ABWESEND",
        "target_present": present,
        "reason": reason,
        "scope": "one_named_regular_file_at_snapshot",
        "coverage": "UNVOLLSTAENDIG",
        "all_effects_seen": False,
        "writer_identity": "UNBEKANNT",
        "logical_agent_identity": "UNBEKANNT",
        "source_authenticated": False,
        "rights_inherited": False,
    }


def measure_target(target: Path) -> dict[str, object]:
    """Sample only the named target, without reading content or sibling paths."""
    target = Path(target)
    try:
        if not stat.S_ISDIR(target.parent.stat().st_mode):
            return describe_snapshot(None, reason="directory_unavailable")
        try:
            value = target.lstat()
        except FileNotFoundError:
            return describe_snapshot(False, reason="absent_at_snapshot")
        if not stat.S_ISREG(value.st_mode):
            return describe_snapshot(None, reason="not_regular_file")
        return describe_snapshot(True, reason="present_at_snapshot")
    except OSError:
        return describe_snapshot(None, reason="observation_unavailable")
