"""Finish the same fresh job after intake-only repair; never claims or executes."""

import hashlib
import json
import secrets
import socket
import sqlite3
import subprocess
import time
from pathlib import Path

from research.debian_private.ipc import SECURE, guard_healthy
from research.private_service.http import call
from research.private_service.protocol import digest, request, require, verify
from research.private_service.retention import write_private

BASE = Path("/var/lib/aa-private-install-20261017")


def main(resume=False):
    destination = BASE / "completed-same-fresh-job.json"
    require(destination.exists() == resume, 503, "FINISH_STATE")
    prior = json.loads((BASE / "complete-service-job.json").read_bytes())
    config = json.loads((SECURE / "registrar/bootstrap/config.json").read_bytes())
    keys = config["keys"]
    jid = prior["job_id"]
    result = json.loads((SECURE / "runner/result.json").read_bytes())
    require(result["job_id"] == jid, 503, "WRONG_RESULT")
    record = {
        "schema": "aa-debian-completed-same-fresh-job-v1",
        "job_id": jid,
        "completed": False,
        "action_reexecuted": False,
        "initial_coordinator_failed": True,
        "intake_repaired_under_runner_uid": True,
        "measurement": result,
        "cases": [],
        "start_monotonic_ns": prior["start_monotonic_ns"],
        "finish_start_monotonic_ns": time.monotonic_ns(),
    }
    if resume:
        previous = json.loads(destination.read_bytes())
        require(
            previous["job_id"] == jid and previous["completed"] is False,
            503,
            "FINISH_ALREADY_COMPLETE",
        )
        record = previous
        record["previous_finish_expectation_error_preserved"] = True
    tokens = {
        r: next(t["token"] for t in config["tokens"] if t["tenant"] == "test-a" and t["role"] == r)
        for r in ["client", "admin"]
    }

    def save():
        destination.write_text(json.dumps(record, indent=2))

    def send(role, method, path, data=None, expected=200, label=None):
        status, response = call("http://127.0.0.1:8765", tokens[role], method, path, data)
        record["cases"].append(
            {"case": label or path, "status": status, "code": response.get("code")}
        )
        save()
        require(status == expected, 503, "FINISH_HTTP_EXPECTATION")
        return response

    def packet(kid, path, payload, **kw):
        return request(
            keys[kid]["private"],
            "test-a",
            kid,
            path,
            payload,
            secrets.token_hex(16),
            kw.get("nonce", secrets.token_hex(32)),
        )

    save()
    guard_healthy()
    before = send(
        "client", "GET", f"/v1/jobs/{jid}/report", label="fresh-signed-report-before-restart"
    )
    report = before["report"]
    body = report["body"]
    require(verify(config["report_public_key"], report), 503, "REPORT_SIGNATURE")
    require(
        body["classification"] == "BELEGT"
        and len(body["checks"]) == 28
        and all(v is True for v in body["checks"].values()),
        503,
        "CHAIN_NOT_QUALIFIED",
    )
    require(
        len(body["critical_loss_metrics"]) == 23
        and all(type(v) is int and v == 0 for v in body["critical_loss_metrics"].values()),
        503,
        "LOSS_NOT_QUALIFIED",
    )
    require(
        body["job_sha256"] == digest(prior["signed_job"])
        and body["acceptance_sha256"] == digest(prior["signed_acceptance"]),
        503,
        "BINDING",
    )
    require(body["grants_rights"] is False, 503, "RIGHTS_POLICY")
    record.update(
        classification=body["classification"],
        checks=body["checks"],
        critical_loss_metrics=body["critical_loss_metrics"],
        report_sha256=digest(report),
    )
    save()
    subprocess.run(["systemctl", "restart", "aa-private-api.service"], check=True, timeout=8)
    for _ in range(30):
        try:
            with socket.create_connection(("127.0.0.1", 8765), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    after = send(
        "client", "GET", f"/v1/jobs/{jid}/report", label="same-report-after-real-api-restart"
    )
    require(
        after["report"] == report and verify(config["report_public_key"], after["report"]),
        503,
        "RESTART_SIGNATURE",
    )
    recipient = SECURE / "registrar/received-report.json"
    if recipient.exists():
        require(
            json.loads(recipient.read_bytes())["report"] == report, 503, "RECIPIENT_COPY_CHANGED"
        )
    else:
        write_private(recipient, json.dumps(after).encode())
    original = prior["signed_job"]
    # After intake repair the original signed 60s request has expired. An exact
    # retry must obey that actual clock boundary; never extend it for a test.
    from research.private_service.protocol import now_ms

    expected_retry = 410 if now_ms() >= original["body"]["expires_ms"] else 202
    send(
        "client",
        "POST",
        "/v1/jobs",
        original,
        expected_retry,
        "restart-exact-retry-at-actual-request-deadline",
    )
    send(
        "client",
        "POST",
        "/v1/jobs",
        packet("sender", "/v1/jobs", original["body"]["payload"], nonce=original["body"]["nonce"]),
        409,
        "restart-replay-denied",
    )
    path = f"/v1/jobs/{jid}/receipts"
    receipt = {
        "job_id": jid,
        "report_version": "1",
        "report_sha256": digest(report),
        "received_complete": True,
    }
    send(
        "client",
        "POST",
        path,
        packet("sender", path, {**receipt, "report_sha256": "0" * 64}),
        422,
        "bad-report-digest-receipt-denied",
    )
    send(
        "client",
        "POST",
        path,
        packet("sender", path, {**receipt, "received_complete": False}),
        422,
        "incomplete-receipt-denied",
    )
    signed = packet("sender", path, receipt)
    ack = send("client", "POST", path, signed, label="signed-full-receipt")
    require(
        ack["cleanup_state"] == "complete" and ack["access_state"] == "blocked",
        503,
        "CLEANUP_NOT_COMPLETE",
    )
    send(
        "client",
        "GET",
        f"/v1/jobs/{jid}/report",
        expected=410,
        label="report-unavailable-after-receipt",
    )
    send("client", "POST", path, signed, label="repeat-receipt-and-cleanup")
    with sqlite3.connect(SECURE / "api/service.sqlite") as db:
        fields = db.execute(
            "SELECT request,acceptance,report FROM jobs WHERE id=?", (jid,)
        ).fetchone()
        pins = db.execute("SELECT count(*) FROM dispatch_pins WHERE job_id=?", (jid,)).fetchone()[0]
        lifecycle = db.execute(
            "SELECT cleanup,blocked,received,cleaned FROM lifecycle WHERE job_id=?", (jid,)
        ).fetchone()
    folder = SECURE / "api/jobs" / hashlib.sha256(b"test-a").hexdigest() / jid
    for p in [SECURE / "runner/pending.json", SECURE / "runner/result.json"]:
        require(not p.is_symlink(), 503, "UNSAFE_HANDOFF")
        p.unlink(missing_ok=True)
    record["cleanup"] = {
        "job_fields_null": fields == (None, None, None),
        "dispatch_pins": pins,
        "job_directory_absent": not folder.exists(),
        "verifier_pin_absent": not (SECURE / "verifier" / ("pin-" + jid + ".json")).exists(),
        "verdict_absent": not (SECURE / "verdicts" / (jid + ".json")).exists(),
        "lifecycle_complete": lifecycle[0] == "complete",
        "inputs_and_targets_absent": not any((SECURE / "collector/tmp").glob("a4*")),
        "handoff_absent": not (SECURE / "runner/pending.json").exists(),
    }
    require(
        all(v is True for k, v in record["cleanup"].items() if k != "dispatch_pins") and pins == 0,
        503,
        "RESIDUE_FOUND",
    )
    record["signed_receipt"] = signed
    record["receipt_status"] = ack
    send(
        "admin",
        "POST",
        "/v1/revocations",
        packet("sender", "/v1/revocations", {"kid": "receiver"}),
        label="receiver-revoked",
    )
    ap = f"/v1/jobs/{jid}/acceptances"
    send(
        "client",
        "POST",
        ap,
        prior["signed_acceptance"],
        410 if now_ms() >= prior["signed_acceptance"]["body"]["expires_ms"] else 403,
        "revoked-exact-cache-retry-at-actual-deadline",
    )
    send(
        "client",
        "POST",
        ap,
        packet("receiver", ap, prior["signed_acceptance"]["body"]["payload"]),
        403,
        "fresh-request-by-revoked-key-denied",
    )
    record["completed"] = True
    record["cleanup_end_monotonic_ns"] = time.monotonic_ns()
    save()
    subprocess.run(["systemctl", "stop", "aa-private-handoff-expire.timer"], check=True)
    print(
        json.dumps(
            {
                "completed": True,
                "job_id": jid,
                "classification": body["classification"],
                "checks": 28,
                "loss_counters": 23,
                "action_reexecuted": False,
                "cleanup": record["cleanup"],
            }
        )
    )


if __name__ == "__main__":
    main()
