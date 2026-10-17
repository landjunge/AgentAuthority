"""Server-internal v1 ports. These are Python contracts, not network services.

Only the composition root supplies implementations. Browser input never names
an implementation, database, module, path or endpoint. A future remote adapter
must preserve these ownership, revocation and atomicity guarantees explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

CONTRACT_VERSION = 1
ADAPTERS = frozenset({"observations", "report", "private-verification"})


class Problem(Exception):
    def __init__(self, status: int, code: str):
        self.status = status
        self.code = code


@dataclass(frozen=True)
class Scope:
    source_id: str
    job_id: str
    adapters: tuple[str, ...]

    def document(self) -> dict[str, Any]:
        # Preserve the existing HTTP scope shape. Adapter policy belongs to the
        # server configuration; clients submit the explicit existing kind field.
        return {"sourceId": self.source_id, "jobId": self.job_id}


@dataclass(frozen=True)
class Principal:
    subject: str
    scopes: tuple[Scope, ...]
    # Server-only authentication context; never serialize or pass to data ports.
    session_id: str | None = field(default=None, repr=False)


@dataclass(frozen=True)
class Session:
    token: str
    principal: Principal
    csrf: str


class AccessControl(Protocol):
    """Authoritative identity/session/scope lookup; deny on backend failure.

    Session records bind a subject, never a permanently cached set of rights.
    Every request resolves current rights. refresh() checks the bound session's
    subject, expiry and revocation before module access/commit; revoke()
    invalidates this session in the backend's domain. Caller-supplied scopes
    never replace current authoritative rights.
    A multi-instance implementation needs shared revocation and global limits.
    """

    contract_version: int

    def authenticate(self, authorization: str) -> Session: ...
    def resolve(self, cookie: str) -> Session: ...
    def refresh(self, principal: Principal) -> Principal: ...
    def authorize(self, principal: Principal, source: str, job: str, adapter: str) -> Principal: ...
    def revoke(self, token: str) -> None: ...
    def close(self) -> None: ...


class ReportRepository(Protocol):
    """Immutable results, scoped reads and atomic quota+insert in one authority.

    A Principal is supplied only after server-side access resolution, with its
    server-only session_id removed. Reads must
    select by BOTH owner and allowed source/job/adapter before decoding payloads.
    IDs bind stored results to that exact source/job, not to executable actions.
    Repeated explicit imports remain separate results; no retry is implied.
    """

    contract_version: int

    def listing(self, principal: Principal) -> list[dict[str, Any]]: ...
    def get(self, principal: Principal, identifier: str) -> dict[str, Any]: ...
    def insert(self, principal: Principal, payload: dict[str, Any]) -> dict[str, Any]: ...
    def close(self) -> None: ...


class ReportAnalysis(Protocol):
    """Bounded observation/projection only; no action dispatch or rendering."""

    contract_version: int

    def project(self, source: str, job: str, adapter: str, data: Any) -> dict[str, Any]: ...
    def status(self) -> dict[str, Any]: ...
