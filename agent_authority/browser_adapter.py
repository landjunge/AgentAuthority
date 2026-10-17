"""Read-only display adapter for the existing private service's GET report contract.

This does not verify Ed25519, fetch URLs, dispatch collectors or turn aa-report-v1
into an observation report. Unpinned external statements remain reported facts.
The caller must authorize its source/job mapping before invoking this adapter.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
from typing import Any, cast

from agent_authority.observations import TOKEN

MAX_PRIVATE_REPORT_BYTES = 65_536
MAX_PRIVATE_REPORT_VALUES = 4_096
_ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
_JOB = re.compile(r"[0-9a-f]{32}\Z")
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_CLASSIFICATIONS = {"BELEGT", "WIDERSPRUECHLICH", "UNVOLLSTAENDIG", "UNBEKANNT"}
_LAYERS = (
    "request_signature",
    "exact_service_acceptance",
    "controlled_process_and_delegation",
    "independent_write",
)
_COMMON = {
    "schema",
    "domain",
    "audience",
    "signing_kid",
    "tenant",
    "job_id",
    "classification",
    "verifier_version",
    "trust_catalog_version",
    "issued_ms",
    "scope",
    "provider_model_session",
    "uncertainties",
    "grants_rights",
    "completed_at",
    "expires_at",
    "report_version",
}
_MEASURED = {
    "verifier_sha256",
    "normalization",
    "job_sha256",
    "acceptance_sha256",
    "source",
    "checks",
    "critical_loss_metrics",
    "reasons",
    "layers",
    "trust_basis",
}
_LIFECYCLE = {
    "completed_at",
    "expires_at",
    "report_version",
    "report_sha256",
    "receipt_state",
    "received_at",
    "access_state",
    "deletion_reason",
    "cleanup_state",
    "cleanup_completed_at",
    "cleanup_confirmed",
    "content_key_state",
    "inputs_cleanup_completed_at",
    "residual_expires_at",
    "cleanup_scope",
}


def synthetic_private_response(
    job_id: str, tenant: str = "synthetic-a", *, measured: bool = True
) -> dict[str, Any]:
    """Own GET-shape fixture, never a cryptographic, collector or live result.

    The signature consists of 64 zero bytes, deliberately no valid signature.
    This helper never starts an action or borrows external report bytes.
    """
    _require(type(job_id) is str and _JOB.fullmatch(job_id) is not None)
    _require(_identifier(tenant))
    body: dict[str, Any] = {
        "schema": "aa-report-v1",
        "domain": "AA-REPORT-v1",
        "audience": "aa-private-local-v1",
        "signing_kid": "local-report-v1",
        "tenant": tenant,
        "job_id": job_id,
        "classification": "UNBEKANNT",
        "scope": "controlled-a4-write16",
        "verifier_version": "aa-private-verifier-v1",
        "trust_catalog_version": "synthetic-v1",
        "issued_ms": 1792195200000,
        "completed_at": "2026-10-17T00:00:00.000Z",
        "expires_at": "2026-10-18T00:00:00.000Z",
        "report_version": "1",
        "provider_model_session": "UNBEKANNT",
        "grants_rights": False,
        "uncertainties": ["SYNTHETIC fixture; no actual collector or cryptographic proof"],
    }
    if measured:
        body.update(
            verifier_sha256="1" * 64,
            normalization="lifecycle records ordered by kernel monotonic stamp; none removed",
            job_sha256="2" * 64,
            acceptance_sha256="3" * 64,
            source={
                "id": "synthetic-runner",
                "trust_class": "controlled-linux-collector",
                "run_id": "synthetic-run",
                "evidence_sha256": "4" * 64,
                "source_sha256": {"synthetic/collector.py": "5" * 64},
            },
            checks={"synthetic_check_" + str(i): True for i in range(28)},
            critical_loss_metrics={"synthetic_loss_" + str(i): 0 for i in range(23)},
            reasons=["SYNTHETIC_ONLY"],
            trust_basis=["SYNTHETIC fixture"],
            layers={
                "request_signature": "BELEGT",
                "exact_service_acceptance": "BELEGT",
                "controlled_process_and_delegation": "UNBEKANNT",
                "independent_write": "UNBEKANNT",
            },
        )
    else:
        body.update(reason="WORKER_INTERRUPTED", sources=[])
    return {
        "schema": "aa-private-v1",
        "report": {"body": body, "signature": base64.b64encode(bytes(64)).decode("ascii")},
        "current_key_status": {"synthetic-sender": "active", "synthetic-receiver": "revoked"},
        "completed_at": body["completed_at"],
        "expires_at": body["expires_at"],
        "report_version": "1",
        "report_sha256": "6" * 64,
        "receipt_state": "unconfirmed",
        "received_at": None,
        "access_state": "available",
        "deletion_reason": None,
        "cleanup_state": "inputs_removed",
        "cleanup_completed_at": None,
        "cleanup_confirmed": False,
        "content_key_state": "present",
        "inputs_cleanup_completed_at": body["completed_at"],
        "residual_expires_at": None,
        "cleanup_scope": "this job's service files and SQLite namespace; no SSD/RAM/backup erasure claim",
    }


class PrivateReportError(ValueError):
    """Fixed error code, never private input, paths or arbitrary exception text."""


def _require(condition: bool, code: str = "private_report_invalid") -> None:
    if not condition:
        raise PrivateReportError(code)


def _bounded(value: Any, depth: int, remaining: list[int]) -> None:
    remaining[0] -= 1
    _require(remaining[0] >= 0 and depth <= 12, "private_report_structure_limit")
    if type(value) is dict:
        _require(len(value) <= 128, "private_report_structure_limit")
        for key, item in value.items():
            _require(type(key) is str)
            _bounded(key, depth + 1, remaining)
            _bounded(item, depth + 1, remaining)
    elif type(value) is list:
        _require(len(value) <= 128, "private_report_structure_limit")
        for item in value:
            _bounded(item, depth + 1, remaining)
    elif type(value) is str:
        _require(len(value) <= 2_048, "private_report_structure_limit")
        _require(all(32 <= ord(char) <= 126 for char in value))
    elif type(value) is int:
        _require(abs(value) <= 2**53 - 1)
    else:
        _require(value is None or type(value) is bool)


def _strings(value: Any, maximum: int = 32) -> bool:
    return type(value) is list and len(value) <= maximum and all(type(v) is str for v in value)


def _digest(value: Any) -> bool:
    return type(value) is str and _SHA.fullmatch(value) is not None


def _identifier(value: Any) -> bool:
    return type(value) is str and _ID.fullmatch(value) is not None


def _validate(data: Any, job_id: str) -> dict[str, Any]:
    _bounded(data, 0, [MAX_PRIVATE_REPORT_VALUES])
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    _require(len(raw) <= MAX_PRIVATE_REPORT_BYTES, "private_report_byte_limit")
    _require(type(data) is dict)
    _require(set(data) <= {"schema", "report", "current_key_status"} | _LIFECYCLE)
    _require({"schema", "report", "current_key_status"} <= set(data))
    _require(data["schema"] == "aa-private-v1")
    envelope = data["report"]
    _require(type(envelope) is dict and set(envelope) == {"body", "signature"})
    _require(type(envelope["signature"]) is str)
    try:
        signature = base64.b64decode(envelope["signature"], validate=True)
    except (ValueError, binascii.Error) as exc:
        raise PrivateReportError("private_report_invalid_signature_encoding") from exc
    _require(len(signature) == 64, "private_report_invalid_signature_encoding")
    body = envelope["body"]
    _require(type(body) is dict)
    _require(set(body) in (_COMMON | {"reason", "sources"}, _COMMON | _MEASURED))
    _require(body["schema"] == "aa-report-v1" and body["domain"] == "AA-REPORT-v1")
    _require(body["audience"] == "aa-private-local-v1")
    _require(body["signing_kid"] == "local-report-v1" and body["scope"] == "controlled-a4-write16")
    _require(_identifier(body["tenant"]) and body["job_id"] == job_id)
    _require(type(body["classification"]) is str and body["classification"] in _CLASSIFICATIONS)
    _require(body["grants_rights"] is False and body["provider_model_session"] == "UNBEKANNT")
    _require(type(body["issued_ms"]) is int and 0 <= body["issued_ms"] <= 2**53 - 1)
    _require(body["report_version"] == "1")
    _require(
        all(
            type(body[k]) is str and body[k]
            for k in ("verifier_version", "trust_catalog_version", "completed_at", "expires_at")
        )
    )
    _require(_strings(body["uncertainties"], 24))
    statuses = data["current_key_status"]
    _require(type(statuses) is dict and len(statuses) <= 2)
    _require(
        all(_identifier(k) and v in ("active", "expired", "revoked") for k, v in statuses.items())
    )
    for key, value in data.items():
        if key in _LIFECYCLE:
            if key in ("cleanup_confirmed",):
                _require(type(value) is bool)
            else:
                _require(value is None or type(value) is str)
    if "reason" in body:
        _require(body["classification"] == "UNBEKANNT" and body["sources"] == [])
        _require(
            type(body["reason"]) is str
            and body["reason"]
            in (
                "RUNNER_OR_INTAKE_ERROR",
                "KEY_REVOKED_DURING_RUN",
                "KEY_REVOKED_BEFORE_RUN",
                "WORKER_INTERRUPTED",
                "WORKER_TIMEOUT",
                "REQUEST_EXPIRED",
                "CANCELLED_NO_RERUN",
                "KEY_REVOKED",
                "KEY_EXPIRED",
                "EXPIRED_OR_FUTURE",
            )
        )
    else:
        _require(
            all(_digest(body[k]) for k in ("verifier_sha256", "job_sha256", "acceptance_sha256"))
        )
        _require(type(body["normalization"]) is str)
        source = body["source"]
        _require(
            type(source) is dict
            and set(source) == {"id", "trust_class", "run_id", "evidence_sha256", "source_sha256"}
        )
        _require(_identifier(source["id"]) and _identifier(source["run_id"]))
        _require(source["trust_class"] == "controlled-linux-collector")
        _require(_digest(source["evidence_sha256"]))
        _require(type(source["source_sha256"]) is dict and len(source["source_sha256"]) <= 64)
        _require(
            all(
                type(k) is str and len(k) <= 128 and _digest(v)
                for k, v in source["source_sha256"].items()
            )
        )
        checks, losses = body["checks"], body["critical_loss_metrics"]
        _require(type(checks) is dict and len(checks) <= 28)
        _require(all(type(v) is bool for v in checks.values()))
        _require(type(losses) is dict and len(losses) <= 23)
        _require(all(v is None or (type(v) is int and v >= 0) for v in losses.values()))
        layers = body["layers"]
        _require(type(layers) is dict and set(layers) == set(_LAYERS))
        _require(all(type(v) is str and v in _CLASSIFICATIONS for v in layers.values()))
        _require(_strings(body["reasons"]) and _strings(body["trust_basis"]))
        if body["classification"] == "BELEGT":
            _require(len(checks) == 28 and all(v is True for v in checks.values()))
            _require(len(losses) == 23 and all(type(v) is int and v == 0 for v in losses.values()))
    return cast(dict[str, Any], body)


def adapt_private_report(data: Any, source_id: str, job_id: str) -> dict[str, Any]:
    """Project an authorized aa-private-v1 GET response, without asserting trust.

    source_id and job_id come from operator configuration, never browser paths.
    Matching the reported job is a format check, not a tenant authorization check.
    There is intentionally no public-key argument or verification success mode.
    """
    _require(type(source_id) is str and TOKEN.fullmatch(source_id) is not None)
    _require(type(job_id) is str and _JOB.fullmatch(job_id) is not None)
    body = _validate(data, job_id)
    measured = "layers" in body
    canonical = json.dumps(data["report"], sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    envelope_digest = hashlib.sha256(canonical.encode("ascii")).hexdigest()

    def node(
        identifier: str,
        name: str,
        kind: str,
        facts: list[dict[str, Any]],
        evidence: list[str],
        *,
        localized: bool = False,
    ) -> dict[str, Any]:
        return {
            "id": identifier,
            "kind": kind,
            "name": name,
            "nameKey": localized,
            "status": "unknown",
            "group": "private-report",
            "facts": facts,
            "evidence": evidence,
        }

    def fact(label: str, value: str, *, localized: bool = False) -> dict[str, Any]:
        return {"labelKey": "browser.private." + label, "value": value, "valueKey": localized}

    nodes = [
        node(
            "private-job",
            job_id,
            "task",
            [
                fact("reportedTenant", body["tenant"]),
                fact("scope", body["scope"]),
                fact("tenantMapping", "status.unknown", localized=True),
            ],
            ["job_id:" + job_id],
        ),
        node(
            "private-report",
            "browser.private.report",
            "evidence",
            [
                fact(
                    "reportedClassification",
                    "browser.private.classification." + body["classification"],
                    localized=True,
                ),
                fact("signatureVerification", "status.unknown", localized=True),
                fact("reportedProviderSession", "status.unknown", localized=True),
                fact("reportedIssueTime", str(body["issued_ms"])),
                *[fact("reportedUncertainty", value) for value in body["uncertainties"]],
            ],
            ["envelope_sha256:" + envelope_digest],
            localized=True,
        ),
    ]
    edges = [
        {
            "from": "private-job",
            "to": "private-report",
            "relation": "reported-report",
            "status": "unknown",
            "evidence": ["job_id:" + job_id],
        }
    ]
    if measured:
        for layer in _LAYERS:
            evidence = []
            if layer == "request_signature":
                evidence = ["job_sha256:" + body["job_sha256"]]
            elif layer == "exact_service_acceptance":
                evidence = ["acceptance_sha256:" + body["acceptance_sha256"]]
            else:
                evidence = ["evidence_sha256:" + body["source"]["evidence_sha256"]]
            nodes.append(
                node(
                    "private-" + layer,
                    "browser.private.layer." + layer,
                    "evidence",
                    [
                        fact(
                            "reportedLayer",
                            "browser.private.classification." + body["layers"][layer],
                            localized=True,
                        ),
                        fact("browserVerification", "status.unknown", localized=True),
                    ],
                    evidence,
                    localized=True,
                )
            )
            edges.append(
                {
                    "from": "private-report",
                    "to": "private-" + layer,
                    "relation": "reported-layer",
                    "status": "unknown",
                    "evidence": evidence,
                }
            )
    else:
        nodes[1]["facts"].append(
            fact("reportedReason", "browser.private.reason." + body["reason"], localized=True)
        )
    # Retain the real contract name and a small subset of its statements. Never
    # export the opaque signature, arbitrary extra fields, raw A4 data or keys.
    minimized_body = {
        k: body[k]
        for k in (
            "schema",
            "domain",
            "audience",
            "tenant",
            "job_id",
            "scope",
            "classification",
            "issued_ms",
            "completed_at",
            "expires_at",
            "report_version",
            "provider_model_session",
            "grants_rights",
            "uncertainties",
        )
    }
    if measured:
        minimized_body.update(
            {k: body[k] for k in ("layers", "checks", "critical_loss_metrics", "reasons")}
        )
    else:
        minimized_body.update(reason=body["reason"], sources=[])
    return {
        "graph": {
            "schema": "agent-authority-ui-graph-v1",
            "source": source_id,
            "isDemo": False,
            "nodes": nodes,
            "edges": edges,
            "warnings": ["private_signature_unverified", "private_production_binding_blocked"],
            "omitted": 0,
        },
        "metadata": {
            "adapter": "aa-private-get-report-v1",
            "report_contract": "aa-report-v1",
            "signature_verification": "UNBEKANNT",
            "production_integration": "blocked",
            "blocking_reasons": [
                "separate_report_key_pin_and_verification_missing",
                "authenticated_tenant_job_mapping_missing",
                "collector_is_not_activated_by_this_service",
            ],
            "envelope_sha256": envelope_digest,
            "grants_rights": False,
            "synthetic_provenance": "caller_must_label_synthetic_fixture",
        },
        "privateReport": {
            "schema": "aa-private-v1",
            "report": {"body": minimized_body},
            "signature_omitted": True,
            "signature_verification": "UNBEKANNT",
            "current_key_status_reported": dict(data["current_key_status"]),
            "current_key_status_covered_by_report_signature": False,
            "lifecycle_reported": {k: data[k] for k in _LIFECYCLE if k in data},
        },
    }
