"""Private synthetic Help Center connection, with no external identity exchange.

Only this fixed public-shape fixture is available. Browser requests cannot name
an owner, source, job, endpoint, path or implementation. A configured local
account needs the exact synthetic scope; that scope establishes access to this
fixture only, never an association with a real Help Center account or agent.
Graph projection and layout remain in browser_static/app.js.
"""

from __future__ import annotations

import json
from typing import Any

from agent_authority.browser_contracts import Principal, Problem
from agent_authority.browser_service import BrowserService

SYNTHETIC_SOURCE = "hilfezentrum-synthetic"
SYNTHETIC_JOB = "30000000-0000-4000-8000-000000000001"
SYNTHETIC_ADAPTER = "report"

# Pinned copy of the Help Center's examples/authority_context_synthetic.json.
# These UUID-shaped values are fixtures, not external subjects or trust anchors.
_CONTEXT_JSON = '''{
  "schema": "hilfezentrum.authority-context.v1",
  "observed_at": "2026-10-17T11:30:00+00:00",
  "source_system": "ki-hilfezentrum",
  "selected_role": "owner",
  "owner_account_id": "10000000-0000-4000-8000-000000000001",
  "participant_account_id": "10000000-0000-4000-8000-000000000002",
  "listing": {
    "id": "20000000-0000-4000-8000-000000000001",
    "lifecycle": {"state": "active", "revision": 0, "changed_at": null}
  },
  "assignment": {
    "id": "30000000-0000-4000-8000-000000000001",
    "state": "submitted",
    "revision": 3,
    "created_at": "2026-10-17T11:00:00+00:00",
    "changed_at": "2026-10-17T11:20:00+00:00"
  },
  "case": {
    "key": "40000000-0000-4000-8000-000000000001",
    "state": "open",
    "revision": 1,
    "tracked_since": "2026-10-17T11:05:00+00:00",
    "synthetic": true
  },
  "owner_accepted_assignment": false,
  "independence_verified": false,
  "external_authority": "unknown",
  "agent_identity_verified": false,
  "job_mapping": "hilfezentrum-assignment-only",
  "return_paths": {
    "de": "/?listing=20000000-0000-4000-8000-000000000001",
    "en": "/en.html?listing=20000000-0000-4000-8000-000000000001"
  },
  "handoff": {
    "status": "blocked",
    "code": "authority_identity_contract_missing",
    "shared_sign_in": false,
    "data_transferred": false
  }
}'''


def synthetic_context(
    service: BrowserService, principal: Principal, envelope: Any
) -> dict[str, Any]:
    """Authorize the fixed fixture against the current server-side account.

    The HTTP adapter must authenticate and validate CSRF/origin first. Refresh
    and authorization here also prevent trusted callers from passing stale or
    self-issued scope claims. No repository, analysis or network port is used.
    """
    principal = service.access.refresh(principal)
    if type(envelope) is not dict or envelope:
        raise Problem(422, "INVALID_SYNTHETIC_CONTEXT")
    try:
        principal = service.access.authorize(
            principal, SYNTHETIC_SOURCE, SYNTHETIC_JOB, SYNTHETIC_ADAPTER
        )
    except Problem as exc:
        if exc.status == 403:
            raise Problem(404, "NOT_FOUND") from None
        raise
    return {
        "context": json.loads(_CONTEXT_JSON),
        "metadata": {
            "adapter": "hilfezentrum-synthetic-context",
            "sourceId": SYNTHETIC_SOURCE,
            "jobId": SYNTHETIC_JOB,
            "synthetic": True,
            "syntheticAccount": True,
            "accessIdentity": "synthetic-private-account",
            "sourceAuthentication": "UNBEKANNT",
            "productionIntegration": "blocked",
            "sharedSignIn": False,
            "realContextTransferred": False,
            "actions": False,
            "grantsRights": False,
        },
    }
