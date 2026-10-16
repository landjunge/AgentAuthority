"""One fixed runner invocation; no shell/paths/targets supplied by API clients."""

import copy
import json
import secrets
import stat
import traceback

from research.debian_private.ipc import RUNTIME, SECURE, uid
from research.debian_private.ipc import call as ipc
from research.private_service.http import call
from research.private_service.protocol import blob, blob_digest, request, require, unblob
from research.private_service.retention import write_private


def counterexamples(evidence, binding):
    cases = []
    # Counterexamples use this fresh Debian capture. They never submit another
    # action and never sign a report; the live separated verifier still decides.
    from research.private_service.verifier import evaluate_evidence

    for mutation in (
        "missing_capture",
        "bad_registry_signature",
        "positive_loss",
        "unknown_recursion",
        "wrong_ca_pin",
    ):
        payload = copy.deepcopy(evidence["payload"])
        pins = copy.deepcopy(evidence["pin"]["body"]["pins"])
        if mutation == "missing_capture":
            payload["capture"] = None
            payload["manifest"]["complete"] = False
        elif mutation == "wrong_ca_pin":
            pins["pinned_ca_public_key"] = "A" * 43 + "="
        elif mutation == "bad_registry_signature":
            bundle = json.loads(unblob(payload["registry"]))
            bundle["registry"]["signature"] = "A" * 86 + "=="
            payload["registry"] = blob(json.dumps(bundle).encode())
        else:
            rows = [json.loads(l) for l in unblob(payload["capture"]).splitlines()]
            summary = next(r["summary"] for r in rows if "summary" in r)
            if mutation == "positive_loss":
                summary["stats"]["3"] = 1
            else:
                next(iter(summary["program_info"].values()))["recursion_misses"] = None
            payload["capture"] = blob(("\n".join(json.dumps(r) for r in rows) + "\n").encode())
        result = evaluate_evidence(payload, pins, binding["binding"])
        require(result["classification"] != "BELEGT", 503, "NEGATIVE_VERIFIER_FAILED")
        cases.append({"case": mutation, "classification": result["classification"]})
    return cases


def main():
    guard = RUNTIME / "guard-check"
    if guard.exists():
        item = guard.lstat()
        require(
            stat.S_ISREG(item.st_mode) and item.st_uid == 0 and stat.S_IMODE(item.st_mode) == 0o600,
            503,
            "GUARD_TEST_OWNER",
        )
        # Operator-only stop qualification; never claims or executes a job.
        ipc("collector", {"op": "guard-check"}, 0, seconds=60)
        raise RuntimeError("guard was not stopped")
    binding = ipc("control", {"op": "claim"}, uid("aa-api"), output=262144)
    require(binding is not None, 409, "NO_QUEUED_JOB")
    evidence = ipc("collector", binding, 0, seconds=150, output=262144)
    write_private(
        SECURE / "runner/pending.json",
        json.dumps({"binding": binding, "evidence": evidence}).encode(),
    )
    intake(binding, evidence)


def intake(binding, evidence):
    config = json.loads((SECURE / "runner/config.json").read_bytes())
    ipc("control", {"op": "pin", "pin": evidence["pin"]}, uid("aa-api"))
    jid = binding["binding"]["job_id"]
    path = f"/v1/jobs/{jid}/evidence"
    cases = counterexamples(evidence, binding)
    for mutation, expected in (
        ("source", 403),
        ("digest", 422),
        ("missing_field", 422),
        ("signature", 401),
    ):
        payload = copy.deepcopy(evidence["payload"])
        if mutation == "source":
            payload["manifest"]["source_id"] = "foreign-source"
        elif mutation == "digest":
            payload["manifest"]["capture_sha256"] = "0" * 64
        elif mutation == "missing_field":
            del payload["trial"]
        packet = request(
            SECURE / "runner/runner.pem",
            "test-a",
            "runner",
            path,
            payload,
            secrets.token_hex(16),
            secrets.token_hex(32),
        )
        if mutation == "signature":
            packet["signature"] = "A" * 86 + "=="
        status, error = call("http://127.0.0.1:8765", config["token"], "POST", path, packet)
        (SECURE / "runner/intake-status.json").unlink(missing_ok=True)
        write_private(
            SECURE / "runner/intake-status.json",
            json.dumps({"stage": mutation, "status": status, "code": error.get("code")}).encode(),
        )
        require(status == expected, 503, "NEGATIVE_INTAKE_FAILED")
        cases.append(
            {"case": "live-intake-" + mutation, "status": status, "code": error.get("code")}
        )
    packet = request(
        SECURE / "runner/runner.pem",
        "test-a",
        "runner",
        path,
        evidence["payload"],
        secrets.token_hex(16),
        secrets.token_hex(32),
    )
    status, _result = call("http://127.0.0.1:8765", config["token"], "POST", path, packet)
    (SECURE / "runner/intake-status.json").unlink(missing_ok=True)
    write_private(
        SECURE / "runner/intake-status.json",
        json.dumps({"stage": "valid", "status": status, "code": _result.get("code")}).encode(),
    )
    require(status == 201, 503, "EVIDENCE_INTAKE_FAILED")
    capture = [json.loads(l) for l in unblob(evidence["payload"]["capture"]).splitlines()]
    write_private(
        SECURE / "runner/result.json",
        json.dumps(
            {
                "job_id": jid,
                "collector_duration_ms": evidence["duration_ms"],
                "negative_cases": cases,
                "observed_write": [
                    r["record"] for r in capture if r.get("record", {}).get("kind") == 1
                ],
                "capture_sha256": blob_digest(evidence["payload"]["capture"]),
            }
        ).encode(),
    )
    print(
        json.dumps(
            {"job_id": jid, "status": status, "collector_duration_ms": evidence["duration_ms"]}
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - content-free private failure metadata
        diagnostic = SECURE / "runner/failure.json"
        require(not diagnostic.is_symlink(), 503, "UNSAFE_DIAGNOSTIC")
        diagnostic.unlink(missing_ok=True)
        write_private(
            diagnostic,
            json.dumps(
                {
                    "type": type(error).__name__,
                    "code": getattr(error, "code", None),
                    "frames": [
                        {
                            "function": f.name,
                            "line": f.lineno,
                            "file": f.filename.rsplit("/", 1)[-1],
                        }
                        for f in traceback.extract_tb(error.__traceback__)
                    ],
                }
            ).encode(),
        )
        raise SystemExit(1) from None
