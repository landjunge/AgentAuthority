"""Adapt A4 two-principal verifier without changing historical research contracts."""

import copy
import hashlib
import json
import types
from pathlib import Path

from research.hosted_qualification.live_gate import driver
from research.private_service.crypto import verify
from research.private_service.protocol import blob_digest, digest, evidence_values, fields, require

# Retain the historical evaluator bytecode and rules, replace only its disk-based
# OpenSSL transport with EVP verification in memory. No mutation of old modules.
evaluate = types.FunctionType(
    driver.evaluate.__code__, {**driver.evaluate.__globals__, "signature": verify}
)


def verify_package(service, tenant, jid, row, payload, now, source_kid):
    fields(payload, "manifest registry capture trial")
    manifest = payload["manifest"]
    fields(
        manifest,
        "schema source_id source_class run_id registry_sha256 capture_sha256 trial_sha256 complete",
    )
    require(type(manifest["complete"]) is bool)
    with service.connection() as db:
        saved = db.execute(
            "SELECT context FROM dispatch_pins WHERE tenant=? AND job_id=?", (tenant, jid)
        ).fetchone()
    require(saved is not None, 409, "DISPATCH_PIN_MISSING")
    pins = service.unseal(tenant, jid, "pins", saved[0])
    require(
        source_kid == pins["source_kid"]
        and manifest["source_id"] == source_kid
        and manifest["source_class"] == "controlled-linux-collector",
        403,
        "SOURCE_FORBIDDEN",
    )
    require(
        manifest["schema"] == "aa-evidence-v1" and manifest["run_id"] == pins["run_id"],
        422,
        "EVIDENCE_TARGET_MISMATCH",
    )
    for key in ("registry", "capture", "trial"):
        require(
            manifest[key + "_sha256"] == blob_digest(payload[key]), 422, "EVIDENCE_DIGEST_MISMATCH"
        )
    expected = {
        "tenant": tenant,
        "job_id": jid,
        "job_sha256": digest(json.loads(row[2])),
        "acceptance_sha256": digest(json.loads(row[3])),
    }
    evidence_sha256 = digest(payload)
    checks, loss = {}, {}
    classification = "UNBEKANNT"
    reasons = []
    if manifest["complete"] is not True or any(
        payload[k] is None for k in ("registry", "capture", "trial")
    ):
        classification = "UNVOLLSTAENDIG"
        reasons.append("MISSING_EVIDENCE")
    else:
        try:
            payload = evidence_values(payload)
            require(type(payload["capture"]) is list)
            capture = payload["capture"]
            closed = (
                sum(bool(r.get("ready")) for r in capture) == 1
                and sum("summary" in r for r in capture) == 1
            )
            # perf buffers deliver across CPUs; use kernel monotonic stamps,
            # preserving all records and preserving raw bytes and their digests.
            normalized_trial = copy.deepcopy(payload["trial"])
            normalized_trial["lifecycle"]["records"].sort(key=lambda r: r["stamp"])
            result = evaluate(
                payload["registry"], capture, normalized_trial, pins["pinned_ca_public_key"]
            )
            checks = result["checks"]
            loss = result["critical_loss_metrics"]
            checks["one_closed_capture"] = closed
            checks["service_request_and_acceptance_binding"] = (
                payload["trial"]["receipt"]["body"]["delegation"]["body"]["job"]["service_binding"]
                == expected
            )
            if not all(v is True for v in checks.values()):
                classification = "WIDERSPRUECHLICH"
                reasons.append("CHAIN_CHECK_FAILED")
            elif not all(type(v) is int and v == 0 for v in loss.values()):
                reasons.append("LOSS_UNKNOWN_OR_POSITIVE")
            else:
                classification = "BELEGT"
        except (KeyError, ValueError, TypeError, StopIteration, IndexError):
            classification = "UNVOLLSTAENDIG"
            reasons.append("MALFORMED_OR_MISSING_CHAIN")
    positive = classification == "BELEGT"
    return {
        "schema": "aa-report-v1",
        "domain": "AA-REPORT-v1",
        "audience": "aa-private-local-v1",
        "signing_kid": "local-report-v1",
        "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "normalization": "lifecycle records ordered by kernel monotonic stamp; none removed",
        "tenant": tenant,
        "job_id": jid,
        "issued_ms": now,
        "classification": classification,
        "scope": "controlled-a4-write16",
        "job_sha256": expected["job_sha256"],
        "acceptance_sha256": expected["acceptance_sha256"],
        "verifier_version": "aa-private-verifier-v1",
        "trust_catalog_version": service.config["trust_version"],
        "source": {
            "id": source_kid,
            "trust_class": "controlled-linux-collector",
            "run_id": pins["run_id"],
            "evidence_sha256": evidence_sha256,
            "source_sha256": pins["source_sha256"],
        },
        "checks": checks,
        "critical_loss_metrics": loss,
        "reasons": reasons,
        "layers": {
            "request_signature": "BELEGT",
            "exact_service_acceptance": "BELEGT",
            "controlled_process_and_delegation": "BELEGT" if positive else "UNBEKANNT",
            "independent_write": "BELEGT" if positive else "UNBEKANNT",
        },
        "trust_basis": [
            "Operator enrollment root",
            "Pinned runner channel",
            "Research host root and kernel",
            "SCM_CREDENTIALS, pidfd and lifecycle",
            "Independent bounded VFS collector",
        ],
        "uncertainties": [
            "No provider/model session proof",
            "No arbitrary code or external effect proof",
            "Compromised host/root/CA excluded",
            "Signature covers report bytes, not universal safety",
        ],
        "provider_model_session": "UNBEKANNT",
        "grants_rights": False,
    }
