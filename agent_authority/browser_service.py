"""Server-side orchestration; access checks precede each data/analysis port.

Store is the explicit local composition, not a multi-server storage backend.
BrowserService can use other v1 implementations supplied by trusted server code.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent_authority.browser_analysis import LocalReportAnalysis
from agent_authority.browser_auth import LocalAccessControl
from agent_authority.browser_contracts import (
    ADAPTERS,
    CONTRACT_VERSION,
    AccessControl,
    Principal,
    Problem,
    ReportAnalysis,
    ReportRepository,
    Session,
)
from agent_authority.browser_repository import LocalReportRepository, StateLease
from agent_authority.browser_support import parse_json
from agent_authority.observations import TOKEN


def status_document() -> dict[str, Any]:
    return {
        "schema": "aa-browser-status-v1",
        "role": "observer_only",
        "identity": "synthetic-private-only",
        "production": {
            "identity": "blocked",
            "reason": "No agreed Help Center/OIDC audience, subject and source/job mapping",
            "collector": "blocked",
            "collectorReason": "Debian collector qualification and existing hardstop remain unchanged",
            "privateService": "blocked",
            "privateServiceReason": "No production tenant binding, report-key pin or signature verifier configured",
            "multiInstance": "blocked",
            "multiInstanceReason": "Shared authoritative identity/revocation, data, quotas and admission are not configured",
            "helpcenterHandoff": "blocked",
            "helpcenterHandoffReason": "No agreed audience/subject/tenant/owner/source/job/revocation contract; private fixture access does not establish Help Center identity",
        },
        "capabilities": [
            "neutral-report-import",
            "neutral-observation-engine",
            "private-report-claimed-view",
            "explicit-demo",
            "synthetic-helpcenter-context",
        ],
        "actions": False,
        "grantsRights": False,
        "liveConnection": False,
        "reportRetention": "Local operator-owned synthetic state; no automated external retention contract",
        "architecture": {
            "contractVersion": CONTRACT_VERSION,
            "graphComputation": "browser",
            "profile": "single-instance-local-synthetic",
            "authState": "process-memory; configuration read at startup",
            "reportState": "local-sqlite",
            "stateLease": "exclusive-local-process-lock; not a distributed lease",
            "httpConcurrency": 1,
            "socketBacklog": 8,
            "durableQueue": False,
            "globalAdmission": "not-implemented; multi-instance-blocked",
        },
    }


class BrowserService:
    def __init__(
        self, access: AccessControl, repository: ReportRepository, analysis: ReportAnalysis
    ):
        if any(c.contract_version != CONTRACT_VERSION for c in (access, repository, analysis)):
            raise ValueError("incompatible server contract")
        self.access, self.repository, self.analysis = access, repository, analysis

    def session_document(self, session: Session) -> dict[str, Any]:
        principal = self.access.refresh(session.principal)
        return {
            "csrfToken": session.csrf,
            "user": {"id": principal.subject, "synthetic": self.identity_metadata(principal)["syntheticAccount"],
                     "agentIdentityVerified": False},
            "scopes": [s.document() for s in principal.scopes],
            "production": {**status_document()["production"], **({'identity': 'helpcenter-account-only', 'helpcenterHandoff': 'configured-account-only'} if hasattr(self.access, 'exchange') else {})},
        }

    def identity_metadata(self, principal):
        if hasattr(self.access, 'identity_metadata'):
            return self.access.identity_metadata(principal)
        return {'syntheticAccount': True, 'accessIdentity': 'synthetic-private-account'}

    def listing(self, principal: Principal) -> list[dict[str, Any]]:
        current = self.access.refresh(principal)
        return self.repository.listing(Principal(current.subject, current.scopes))

    def get(self, principal: Principal, identifier: str) -> dict[str, Any]:
        current = self.access.refresh(principal)
        return self.repository.get(Principal(current.subject, current.scopes), identifier)

    def save(self, principal: Principal, envelope: Any) -> dict[str, Any]:
        if not isinstance(envelope, dict) or set(envelope) not in (
            {"sourceId", "jobId", "kind", "data"},
            {"sourceId", "jobId", "kind", "rawData"},
        ):
            raise Problem(422, "INVALID_IMPORT")
        source, job, kind = envelope["sourceId"], envelope["jobId"], envelope["kind"]
        if any(not isinstance(v, str) or not TOKEN.fullmatch(v) for v in (source, job, kind)):
            raise Problem(422, "INVALID_IMPORT")
        if kind not in ADAPTERS:
            raise Problem(422, "UNSUPPORTED_ADAPTER")
        principal = self.access.authorize(principal, source, job, kind)
        if "rawData" in envelope:
            if not isinstance(envelope["rawData"], str):
                raise Problem(422, "INVALID_IMPORT")
            data = parse_json(envelope["rawData"].encode("utf-8"))
        else:
            data = envelope["data"]
        payload = self.analysis.project(source, job, kind, data)
        metadata = {
            **payload.get("metadata", {}),
            "id": secrets.token_hex(16),
            "title": f"{source} / {job}",
            "sourceId": source,
            "jobId": job,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "adapter": kind,
            **self.identity_metadata(principal),
            "sourceAuthentication": "UNBEKANNT",
            "productionIntegration": "blocked",
        }
        metadata["inputProvenance"] = (
            "Uploaded observations; SHA-256 covers UTF-8 json.dumps(ensure_ascii=False, separators=(',',':')) of each record; no original file bytes authenticated"
            if kind == "observations"
            else "Uploaded report statements; no source authentication, signature verification or original file recheck performed"
        )
        metadata["state"] = (
            "reported-private-verification"
            if kind == "private-verification"
            else "complete"
            if payload["graph"].get("completeRead")
            else "incomplete"
        )
        payload["metadata"] = metadata
        # Re-resolve after analysis: an adapter cannot preserve stale privileges
        # across a future independently implemented authorization backend.
        principal = self.access.authorize(principal, source, job, kind)
        return self.repository.insert(Principal(principal.subject, principal.scopes), payload)


class Store(BrowserService):
    """One local state, one process; failures release the lease and fail closed."""

    def __init__(self, path: Path):
        self._lease = StateLease(path)
        access = repository = None
        try:
            access = LocalAccessControl(path)
            self._local_access = access
            repository = LocalReportRepository(path)
            super().__init__(access, repository, LocalReportAnalysis())
        except BaseException:
            if repository is not None:
                repository.close()
            if access is not None:
                access.close()
            self._lease.close()
            raise

    def operator_principal(self, subject: str) -> Principal:
        """Local CLI only; never exposed by HTTP or the replaceable auth port."""
        return self._local_access.for_operator(subject)

    def close(self) -> None:
        try:
            self.access.close()
        finally:
            try:
                self.repository.close()
            finally:
                self._lease.close()
