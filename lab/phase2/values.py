from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataValue:
    value_id: str
    label: str
    origin: str
    derived_from: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    # Fake-world only. Never read by FlowOK / explanations.
    payload: str = ""


def merge_provenance(existing: tuple[str, ...], incoming: tuple[str, ...]) -> tuple[str, ...]:
    extra = tuple(p for p in incoming if p not in existing)
    return existing + extra


def mint_conflicts(existing: DataValue | None, incoming: DataValue) -> bool:
    """True if `incoming` would rebind an id to a different security identity."""
    if existing is None:
        return False
    return (
        existing.label != incoming.label
        or existing.origin != incoming.origin
        or existing.derived_from != incoming.derived_from
        or existing.payload != incoming.payload
    )


@dataclass
class Phase2Decision:
    allow: bool
    authority_ok: bool
    flow_ok: bool
    reason: str | None
    explanation: dict[str, Any] | None = None
    value: DataValue | None = None
