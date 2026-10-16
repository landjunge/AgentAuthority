"""Verifier/signing daemons have different UIDs, key rights and immutable pins."""

import json
import sys
import traceback
from pathlib import Path

from research.debian_private.ipc import SECURE, serve, uid
from research.private_service.boundary import report_policy, run_component
from research.private_service.protocol import canonical, digest, fields, require
from research.private_service.protocol import verify as signature
from research.private_service.retention import fsync_dir, write_private


def verify(value):
    if set(value) == {"cleanup_report"}:
        report = value["cleanup_report"]
        public = json.loads((Path("/etc/aa-private/report-public.json")).read_bytes())["public"]
        require(signature(public, report), 403, "REPORT_SIGNATURE")
        jid = report["body"]["job_id"]
        require(
            type(jid) is str and len(jid) == 32 and all(c in "0123456789abcdef" for c in jid),
            422,
            "JOB_ID",
        )
        for target in (
            SECURE / "verifier" / ("pin-" + jid + ".json"),
            SECURE / "verdicts" / (jid + ".json"),
        ):
            require(not target.is_symlink(), 503, "UNSAFE_STORAGE")
            target.unlink(missing_ok=True)
            fsync_dir(target.parent)
        return {"inputs_removed": True}
    fields(value, "payload pins expected")
    expected = value["expected"]
    jid = expected["job_id"]
    require(
        type(jid) is str and len(jid) == 32 and all(c in "0123456789abcdef" for c in jid),
        422,
        "JOB_ID",
    )
    pinned = json.loads((SECURE / "verifier" / ("pin-" + jid + ".json")).read_bytes())
    require(
        value["pins"] == pinned["pins"] and expected == pinned["expected"],
        403,
        "INDEPENDENT_PIN_MISMATCH",
    )
    result = run_component("verify", value)
    verdict = {
        "result": result,
        "expected": expected,
        "pins": value["pins"],
        "evidence_sha256": digest(value["payload"]),
    }
    target = SECURE / "verdicts" / (jid + ".json")
    if target.exists():
        require(json.loads(target.read_bytes()) == verdict, 409, "VERDICT_ALREADY_BOUND")
    else:
        write_private(target, canonical(verdict))
        target.chmod(0o640)
    return result


def report(body):
    report_policy(body)
    if "checks" in body:
        verdict = json.loads((SECURE / "verdicts" / (body["job_id"] + ".json")).read_bytes())
        result = verdict["result"]
        expected = verdict["expected"]
        pins = verdict["pins"]
        require(
            body["tenant"] == expected["tenant"]
            and body["job_sha256"] == expected["job_sha256"]
            and body["acceptance_sha256"] == expected["acceptance_sha256"]
            and body["classification"] == result["classification"]
            and body["checks"] == result["checks"]
            and body["critical_loss_metrics"] == result["loss"]
            and body["reasons"] == result["reasons"]
            and body["source"]["run_id"] == pins["run_id"]
            and body["source"]["source_sha256"] == pins["source_sha256"]
            and body["source"]["evidence_sha256"] == verdict["evidence_sha256"]
            and body["source"]["id"] == pins["source_kid"],
            403,
            "VERIFIER_RESULT_REQUIRED",
        )
    return run_component("report", body, SECURE / "signer/report.pem")


if __name__ == "__main__":
    name = sys.argv[1]
    require(name in ("signer", "verifier"), 503, "COMPONENT_FORBIDDEN")
    handler = report if name == "signer" else verify

    def diagnosed(value):
        try:
            return handler(value)
        except Exception as error:
            diagnostic = SECURE / name / "failure.json"
            require(not diagnostic.is_symlink(), 503, "UNSAFE_DIAGNOSTIC")
            diagnostic.unlink(missing_ok=True)
            write_private(
                diagnostic,
                canonical(
                    {
                        "type": type(error).__name__,
                        "code": getattr(error, "code", None),
                        "frames": [
                            {"file": Path(f.filename).name, "function": f.name, "line": f.lineno}
                            for f in traceback.extract_tb(error.__traceback__)
                        ],
                    }
                ),
            )
            raise

    serve(name, {uid("aa-api")}, diagnosed)
