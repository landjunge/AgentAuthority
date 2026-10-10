"""Explicit local Fake-Lab repair profile, authorized by WB1098.

approve() is a trusted experiment-coordinator API. It provides no human,
cryptographic, operating-system or real external-service authorization.
"""

from __future__ import annotations

import hashlib
import json
import math
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass

from lab.models import (
    INVALID_REQUEST,
    IRREVERSIBLE_ACTIONS,
    MUTATING_ACTIONS,
    I6_IRREVERSIBLE,
    ActionRequest,
    Decision,
)
from lab.paths import canonical_path, is_security_test_path
from lab.validator import Lab, _WorkflowEntry, _emit_decision, validate_request

BOUND_APPROVAL_REQUIRED = "BOUND_APPROVAL_REQUIRED"
CONTROL_PATHS = frozenset({".vscode/settings.json", ".cursor/mcp.json", ".cursor/rules/mcp.json"})
OPAQUE_EFFECTS = frozenset({"shell.exec", "mcp.start", "cache.poison"})
MAX_APPROVALS = 64
MAX_PARAMETER_JSON = 65_536


def _snapshot(req: ActionRequest) -> ActionRequest:
    if validate_request(req) is not None:
        raise ValueError("invalid request")
    payload = json.dumps(req.parameters, sort_keys=True, allow_nan=False)
    if len(payload) > MAX_PARAMETER_JSON:
        raise ValueError("parameter limit")
    return ActionRequest(req.actor, req.action, req.resource, json.loads(payload), req.workflow_id)


def _binding(req: ActionRequest) -> tuple[str, str, str, str]:
    params = {k: v for k, v in req.parameters.items() if k != "approval_token"}
    payload = json.dumps(params, sort_keys=True, allow_nan=False, separators=(",", ":"))
    resource = canonical_path(req.resource) if req.action.startswith("file.") else req.resource
    return req.actor, req.action, resource, hashlib.sha256(payload.encode()).hexdigest()


def _requires_approval(req: ActionRequest) -> bool:
    if req.action in IRREVERSIBLE_ACTIONS or req.action in OPAQUE_EFFECTS:
        return True
    path = canonical_path(req.resource)
    if path in CONTROL_PATHS and req.action != "file.read":
        return True
    return req.action in MUTATING_ACTIONS and is_security_test_path(path)


@dataclass(frozen=True)
class _Approval:
    binding: tuple[str, str, str, str]
    expires_at: float


class RemediationLab(Lab):
    """Bound, expiring, once-only consent for the seven approved fake cases."""

    def __init__(
        self, max_tracked: int | None = None, *, clock: Callable[[], float] | None = None
    ) -> None:
        super().__init__(max_tracked=max_tracked)
        self._clock = time.monotonic if clock is None else clock

    def approve(
        self, req: ActionRequest, *, lifetime: float = 60.0, token: str | None = None
    ) -> str:
        """Trusted coordinator only. Optional token is for inert frozen fixtures."""
        req = _snapshot(req)
        if isinstance(lifetime, bool) or not math.isfinite(lifetime) or not 0 < lifetime <= 300:
            raise ValueError("lifetime must be within (0, 300]")
        if token is None:
            token = secrets.token_urlsafe(24)
        if not isinstance(token, str) or not token or len(token) > 256:
            raise ValueError("invalid local handle")
        while True:
            entry = self._admit(req.workflow_id)
            if entry is None:
                raise ValueError("workflow capacity")
            with entry.lock:
                if entry.retired:
                    continue
                now = self._clock()
                entry.approvals = {
                    key: value
                    for key, value in entry.approvals.items()
                    if isinstance(value, _Approval) and value.expires_at > now
                }
                if token in entry.approvals or len(entry.approvals) >= MAX_APPROVALS:
                    raise ValueError("handle collision or approval capacity")
                entry.approvals[token] = _Approval(_binding(req), now + lifetime)
                return token

    def submit(self, req: ActionRequest) -> Decision:
        try:
            frozen = _snapshot(req)
        except (TypeError, ValueError, RecursionError):
            decision = Decision(False, INVALID_REQUEST, [INVALID_REQUEST])
            _emit_decision(req, decision)
            return decision
        return super().submit(frozen)

    def _extra_violations(self, entry: _WorkflowEntry, req: ActionRequest) -> list[str]:
        if not _requires_approval(req):
            return []
        token = req.parameters.get("approval_token")
        grant = entry.approvals.get(token) if isinstance(token, str) else None
        if (
            isinstance(grant, _Approval)
            and grant.expires_at > self._clock()
            and grant.binding == _binding(req)
        ):
            return []
        reason = I6_IRREVERSIBLE if req.action in IRREVERSIBLE_ACTIONS else BOUND_APPROVAL_REQUIRED
        return [reason]

    def _after_allow_locked(self, entry: _WorkflowEntry, req: ActionRequest) -> None:
        if _requires_approval(req):
            entry.approvals.pop(req.parameters["approval_token"], None)
