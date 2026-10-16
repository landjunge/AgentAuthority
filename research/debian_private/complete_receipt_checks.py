"""Complete revocation checks after actual receipt cleanup; no runner/action calls."""

import json
import secrets
import sqlite3
import subprocess
import time

from research.debian_private.finish_job import BASE
from research.debian_private.ipc import SECURE, guard_healthy
from research.private_service.http import call
from research.private_service.protocol import digest, now_ms, request, require, verify


def main():
    path = BASE / "completed-same-fresh-job.json"
    record = json.loads(path.read_bytes())
    require(
        record["completed"] is False
        and all(v is True for k, v in record["cleanup"].items() if k != "dispatch_pins")
        and record["cleanup"]["dispatch_pins"] == 0,
        503,
        "NOT_CLEANED",
    )
    c = json.loads((SECURE / "registrar/bootstrap/config.json").read_bytes())
    old = json.loads((BASE / "complete-service-job.json").read_bytes())
    jid = record["job_id"]
    report = json.loads((SECURE / "registrar/received-report.json").read_bytes())["report"]
    require(
        verify(c["report_public_key"], report)
        and digest(report) == record["report_sha256"]
        and report["body"]["classification"] == "BELEGT",
        503,
        "SIGNED_REPORT",
    )
    token = next(
        t["token"] for t in c["tokens"] if t["tenant"] == "test-a" and t["role"] == "client"
    )
    ap = f"/v1/jobs/{jid}/acceptances"
    signed = request(
        c["keys"]["receiver"]["private"],
        "test-a",
        "receiver",
        ap,
        old["signed_acceptance"]["body"]["payload"],
        secrets.token_hex(16),
        secrets.token_hex(32),
    )
    status, error = call("http://127.0.0.1:8765", token, "POST", ap, signed)
    require(status == 403 and error.get("code") == "KEY_REVOKED", 503, "REVOCATION_NOT_ENFORCED")
    record["cases"].append(
        {"case": "fresh-request-by-revoked-key-denied", "status": status, "code": error["code"]}
    )
    require(now_ms() >= old["signed_acceptance"]["body"]["expires_ms"], 503, "NOT_EXPIRED")
    status, error = call("http://127.0.0.1:8765", token, "POST", ap, old["signed_acceptance"])
    require(status == 410, 503, "EXPIRED_ACCEPTANCE_NOT_DENIED")
    record["cases"].append(
        {"case": "expired-exact-acceptance-denied", "status": status, "code": error.get("code")}
    )
    status, _ = call("http://127.0.0.1:8765", token, "GET", f"/v1/jobs/{jid}/report")
    require(status == 410, 503, "REPORT_STILL_AVAILABLE")
    with sqlite3.connect(SECURE / "api/service.sqlite") as db:
        require(
            db.execute("SELECT request,acceptance,report FROM jobs WHERE id=?", (jid,)).fetchone()
            == (None, None, None),
            503,
            "RETAINED_INPUT",
        )
        require(
            db.execute("SELECT count(*) FROM dispatch_pins WHERE job_id=?", (jid,)).fetchone()
            == (0,),
            503,
            "RETAINED_PIN",
        )
    guard_healthy()
    record["test_expectation_corrections"] = [
        "Original 60s job retry after intake repair expires: 410",
        "Original expired acceptance rejected before revoked-key lookup: 410; fresh revoked-key request independently checked 403",
    ]
    record["completed"] = True
    record["cleanup_end_monotonic_ns"] = time.monotonic_ns()
    path.write_text(json.dumps(record, indent=2))
    subprocess.run(["systemctl", "stop", "aa-private-handoff-expire.timer"], check=True)
    print(
        json.dumps(
            {
                "completed": True,
                "classification": "BELEGT",
                "checks": len(record["checks"]),
                "loss_counters": len(record["critical_loss_metrics"]),
                "job_id": jid,
                "action_reexecuted": False,
                "cleanup": record["cleanup"],
            }
        )
    )


if __name__ == "__main__":
    main()
