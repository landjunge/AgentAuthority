"""Exactly one fresh controlled Linux action; no automatic retry on any ambiguity."""

import copy
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
from research.private_service.protocol import (
    AUDIENCE,
    SCHEMA,
    digest,
    now_ms,
    request,
    require,
    sign,
    verify,
)
from research.private_service.retention import fsync_dir, write_private

RECORD = Path("/var/lib/aa-private-install-20261017/single-job.json")


def main(registration_record=None, intake_repair_seconds=0):
    require(not RECORD.exists(), 503, "SINGLE_ATTEMPT_ALREADY_STARTED")
    record = {
        "schema": "aa-debian-single-qualification-v1",
        "attempts": 1,
        "action_jobs": 0,
        "cases": [],
        "start_monotonic_ns": time.monotonic_ns(),
        "completed": False,
        "registered_identities": [],
    }

    def save():
        RECORD.write_text(json.dumps(record, indent=2))

    save()
    config = json.loads((SECURE / "registrar/bootstrap/config.json").read_bytes())
    keys = config["keys"]
    if registration_record is not None:
        require(
            registration_record == RECORD.parent / "single-job.json", 503, "REGISTRATION_RECORD"
        )
        earlier = json.loads(registration_record.read_bytes())
        require(earlier["completed"] is False and earlier["action_jobs"] == 1, 503, "PRIOR_ATTEMPT")
        certs = earlier["registered_identities"]
        require(len(certs) == 3, 503, "REGISTRATION_COUNT")
        with sqlite3.connect(SECURE / "api/service.sqlite") as db:
            prior = db.execute("SELECT state FROM jobs WHERE id=?", (earlier["job_id"],)).fetchone()
            require(prior == ("unknown",), 503, "PRIOR_NOT_CLOSED_UNKNOWN")
            cleanup = db.execute(
                "SELECT cleanup FROM lifecycle WHERE job_id=?", (earlier["job_id"],)
            ).fetchone()
            require(cleanup == ("complete",), 503, "PRIOR_NOT_CLEANED")
        for cert in certs:
            body = cert["body"]
            require(
                verify(config["root_pins"]["test-a"], cert)
                and body["public_key"] == keys[body["kid"]]["public"]
                and now_ms() < body["expires_ms"],
                503,
                "REGISTERED_CERTIFICATE",
            )
        record["registered_identities"] = certs
        record["registration_source"] = str(registration_record)
        record["prior_failed_attempt_preserved"] = True
    root = SECURE / "registrar/bootstrap/root/ca-private.pem"
    tokens = {
        role: next(
            t["token"] for t in config["tokens"] if t["tenant"] == "test-a" and t["role"] == role
        )
        for role in ("admin", "client", "runner")
    }
    tokens["foreign"] = next(t["token"] for t in config["tokens"] if t["tenant"] == "test-b")
    tokens["stranger"] = (SECURE / "registrar/foreign-reader-token").read_text()

    def send(role, method, path, data=None, expected=200, label=None):
        start = time.monotonic_ns()
        status, response = call(
            "http://127.0.0.1:8765",
            tokens.get(role, "invalid"),
            "POST" if method == "POST" else "GET",
            path,
            data,
        )
        case = {
            "case": label or path,
            "status": status,
            "code": response.get("code"),
            "duration_ns": time.monotonic_ns() - start,
        }
        record["cases"].append(case)
        save()
        require(status == expected, 503, "QUALIFICATION_HTTP_EXPECTATION")
        return response

    def packet(kid, path, payload, **kw):
        return request(
            keys[kid]["private"],
            "test-a",
            kid,
            path,
            payload,
            kw.pop("idem", secrets.token_hex(16)),
            kw.pop("nonce", secrets.token_hex(32)),
            **kw,
        )

    def wire(raw, expected, label):
        start = time.monotonic_ns()
        with socket.create_connection(("127.0.0.1", 8765), timeout=8) as channel:
            channel.sendall(raw)
            response = channel.recv(65536)
        status = int(response.split(b" ", 2)[1])
        record["cases"].append(
            {"case": label, "status": status, "duration_ns": time.monotonic_ns() - start}
        )
        save()
        require(status == expected, 503, "QUALIFICATION_WIRE_EXPECTATION")

    try:
        guard_healthy()
        for kid in () if registration_record is not None else ("sender", "receiver", "runner"):
            stamp = now_ms()
            challenge = send(
                "admin",
                "POST",
                "/v1/challenges",
                {
                    "schema": SCHEMA,
                    "kid": kid,
                    "public_key": keys[kid]["public"],
                    "idempotency_key": secrets.token_hex(16),
                    "nonce": secrets.token_hex(32),
                    "issued_ms": stamp,
                    "expires_ms": stamp + 60000,
                },
                201,
                "challenge-" + kid,
            )
            cert = sign(
                root,
                {
                    "schema": SCHEMA,
                    "domain": "AA-ENROLL-v1",
                    "tenant": "test-a",
                    "audience": AUDIENCE,
                    "kid": kid,
                    "public_key": keys[kid]["public"],
                    "role": "runner" if kid == "runner" else "actor",
                    "issued_ms": now_ms(),
                    "expires_ms": now_ms() + 86400000,
                },
            )
            record["registered_identities"].append(cert)
            payload = {
                "certificate": cert,
                "proof": sign(keys[kid]["private"], challenge),
                "replaces": None,
            }
            if kid == "sender":
                altered = copy.deepcopy(payload)
                altered["certificate"]["signature"] = "A" * 86 + "=="
                send(
                    "admin",
                    "POST",
                    "/v1/enrollments",
                    packet(kid, "/v1/enrollments", altered),
                    401,
                    "false-enrollment-root-signature",
                )
                altered = copy.deepcopy(payload)
                altered["proof"]["signature"] = "A" * 86 + "=="
                send(
                    "admin",
                    "POST",
                    "/v1/enrollments",
                    packet(kid, "/v1/enrollments", altered),
                    401,
                    "false-possession-proof",
                )
            send(
                "admin",
                "POST",
                "/v1/enrollments",
                packet(kid, "/v1/enrollments", payload),
                201,
                "registered-" + kid,
            )
        payload = {"scenario": "a4-write16-v1", "receiver_kid": "receiver"}
        forged = packet("sender", "/v1/jobs", payload)
        forged["signature"] = "A" * 86 + "=="
        send("client", "POST", "/v1/jobs", forged, 401, "bad-job-signature")
        send(
            "client",
            "POST",
            "/v1/jobs",
            packet("sender", "/v1/jobs", payload, now=now_ms() - 61000),
            410,
            "expired-request",
        )
        send(
            "client",
            "POST",
            "/v1/jobs",
            packet(
                "sender", "/v1/jobs", {"scenario": "arbitrary-shell", "receiver_kid": "receiver"}
            ),
            422,
            "arbitrary-scenario-denied",
        )
        send(
            "client",
            "POST",
            "/v1/jobs",
            packet("sender", "/v1/jobs", {**payload, "path": "/etc/passwd"}),
            422,
            "free-file-target-denied",
        )
        original = packet("sender", "/v1/jobs", payload)
        record["arrival_monotonic_ns"] = time.monotonic_ns()
        job = send("client", "POST", "/v1/jobs", original, 202, "signed-job")
        jid = job["job_id"]
        record["job_id"] = jid
        record["job_sha256"] = digest(original)
        record["signed_job"] = original
        save()
        send("client", "POST", "/v1/jobs", original, 202, "exact-retry-no-new-job")
        send(
            "client",
            "POST",
            "/v1/jobs",
            packet("sender", "/v1/jobs", payload),
            429,
            "parallel-second-job-denied",
        )
        ap = f"/v1/jobs/{jid}/acceptances"
        send(
            "client",
            "POST",
            ap,
            packet("receiver", ap, {"job_id": jid, "job_sha256": "0" * 64}),
            422,
            "nonexact-acceptance-denied",
        )
        acceptance = packet("receiver", ap, {"job_id": jid, "job_sha256": digest(original)})
        send("client", "POST", ap, acceptance, 202, "exact-signed-acceptance")
        record["accepted_monotonic_ns"] = time.monotonic_ns()
        record["acceptance_sha256"] = digest(acceptance)
        record["signed_acceptance"] = acceptance
        save()
        for role in ("foreign", "stranger"):
            send(role, "GET", f"/v1/jobs/{jid}", expected=404, label=role + "-object-denied")
            send(role, "GET", f"/v1/jobs/{jid}/report", expected=404, label=role + "-report-denied")
        for path in (
            "/.git/HEAD",
            "/config.json",
            "/service.sqlite-wal",
            "/root/ca-private.pem",
            "/../etc/passwd",
            "/v1/graph",
        ):
            send("client", "GET", path, expected=404, label="file-route-denied-" + path)
        prefix = (
            b"POST /v1/jobs HTTP/1.1\r\nHost: 127.0.0.1:8765\r\nAuthorization: Bearer "
            + tokens["client"].encode()
            + b"\r\nContent-Type: application/json\r\n"
        )
        wire(prefix + b'Content-Length: 13\r\n\r\n{"a":1,"a":2}', 400, "duplicate-json-denied")
        wire(prefix + b"Content-Length: 262145\r\n\r\n", 413, "oversize-body-denied")
        raw = b"[" * 40 + b"0" + b"]" * 40
        wire(
            prefix + b"Content-Length: " + str(len(raw)).encode() + b"\r\n\r\n" + raw,
            422,
            "parser-depth-denied",
        )
        guard_healthy()
        record["runner_start_monotonic_ns"] = time.monotonic_ns()
        record["action_jobs"] = 1
        save()
        completed = subprocess.run(
            ["systemctl", "start", "aa-private-runner.service"],
            capture_output=True,
            timeout=165,
            check=False,
        )
        record["runner_exit"] = completed.returncode
        record["runner_end_monotonic_ns"] = time.monotonic_ns()
        save()
        if completed.returncode != 0 and intake_repair_seconds:
            require(0 < intake_repair_seconds <= 70, 503, "INTAKE_REPAIR_LIMIT")
            record["intake_repair_window_open"] = True
            save()
            deadline = time.monotonic() + intake_repair_seconds
            while time.monotonic() < deadline and not (SECURE / "runner/result.json").exists():
                guard_healthy()
                time.sleep(0.2)
            record["intake_repaired_without_action_retry"] = (
                SECURE / "runner/result.json"
            ).exists()
            save()
            require(record["intake_repaired_without_action_retry"], 503, "RUNNER_FAILED_NO_RETRY")
        else:
            require(completed.returncode == 0, 503, "RUNNER_FAILED_NO_RETRY")
        result = json.loads((SECURE / "runner/result.json").read_bytes())
        require(result["job_id"] == jid, 503, "RUNNER_OBJECT")
        record["measurement"] = result
        save()
        before = send(
            "client", "GET", f"/v1/jobs/{jid}/report", label="signed-report-before-restart"
        )
        report = before["report"]
        require(verify(config["report_public_key"], report), 503, "REPORT_SIGNATURE")
        body = report["body"]
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
        record["classification"] = body["classification"]
        record["checks"] = body["checks"]
        record["critical_loss_metrics"] = body["critical_loss_metrics"]
        save()
        # Actual API process restart, same encrypted state and identity.
        subprocess.run(["systemctl", "restart", "aa-private-api.service"], check=True, timeout=8)
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1", 8765), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.1)
        after = send(
            "client", "GET", f"/v1/jobs/{jid}/report", label="report-after-real-api-restart"
        )
        require(
            after["report"] == report and verify(config["report_public_key"], after["report"]),
            503,
            "RESTART_REPORT_CHANGED",
        )
        destination = SECURE / "registrar/received-report.json"
        write_private(destination, json.dumps(after).encode())
        fsync_dir(destination.parent)
        record["recipient_copy"] = str(destination)
        record["report_sha256"] = digest(report)
        save()
        send(
            "client",
            "POST",
            "/v1/jobs",
            original,
            410 if now_ms() >= original["body"]["expires_ms"] else 202,
            "restart-exact-retry-at-actual-request-deadline",
        )
        replay = packet("sender", "/v1/jobs", payload, nonce=original["body"]["nonce"])
        send("client", "POST", "/v1/jobs", replay, 409, "restart-replay-denied")
        rp = f"/v1/jobs/{jid}/receipts"
        receipt = {
            "job_id": jid,
            "report_version": "1",
            "report_sha256": digest(report),
            "received_complete": True,
        }
        send(
            "client",
            "POST",
            rp,
            packet("sender", rp, {**receipt, "report_sha256": "0" * 64}),
            422,
            "wrong-report-digest-receipt-denied",
        )
        send(
            "client",
            "POST",
            rp,
            packet("sender", rp, {**receipt, "received_complete": False}),
            422,
            "incomplete-receipt-denied",
        )
        signed_receipt = packet("sender", rp, receipt)
        record["signed_receipt"] = signed_receipt
        ack = send("client", "POST", rp, signed_receipt, 200, "signed-full-receipt")
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
            label="report-actually-unavailable",
        )
        send("client", "POST", rp, signed_receipt, 200, "repeat-receipt-cleanup")
        # Public SQL state only; never read report content/key bytes from DB.
        with sqlite3.connect(SECURE / "api/service.sqlite") as db:
            row = db.execute(
                "SELECT request,acceptance,report FROM jobs WHERE id=?", (jid,)
            ).fetchone()
            pins = db.execute(
                "SELECT count(*) FROM dispatch_pins WHERE job_id=?", (jid,)
            ).fetchone()[0]
            lifecycle = db.execute(
                "SELECT cleanup,blocked,received,cleaned FROM lifecycle WHERE job_id=?", (jid,)
            ).fetchone()
        folder = SECURE / "api/jobs" / hashlib.sha256(b"test-a").hexdigest() / jid
        record["cleanup"] = {
            "job_fields_null": row == (None, None, None),
            "dispatch_pins": pins,
            "job_directory_absent": not folder.exists(),
            "verifier_pin_absent": not (SECURE / "verifier" / ("pin-" + jid + ".json")).exists(),
            "verdict_absent": not (SECURE / "verdicts" / (jid + ".json")).exists(),
            "lifecycle_complete": lifecycle[0] == "complete",
            "inputs_and_targets_absent": not any((SECURE / "collector/tmp").glob("a4*")),
        }
        require(
            all(v is True for k, v in record["cleanup"].items() if k != "dispatch_pins")
            and pins == 0,
            503,
            "RESIDUE_FOUND",
        )
        (SECURE / "runner/result.json").unlink()
        (SECURE / "runner/pending.json").unlink(missing_ok=True)
        # Revocation is checked before caches, without altering the saved report.
        revoke = packet("sender", "/v1/revocations", {"kid": "receiver"})
        send("admin", "POST", "/v1/revocations", revoke, label="receiver-revoked")
        send(
            "client",
            "POST",
            ap,
            acceptance,
            410 if now_ms() >= acceptance["body"]["expires_ms"] else 403,
            "revoked-exact-retry-at-actual-request-deadline",
        )
        send(
            "client",
            "POST",
            ap,
            packet("receiver", ap, acceptance["body"]["payload"]),
            403,
            "fresh-request-by-revoked-key-denied",
        )
        record["cleanup_end_monotonic_ns"] = time.monotonic_ns()
        record["completed"] = True
        save()
        print(
            json.dumps(
                {
                    "completed": True,
                    "job_id": jid,
                    "classification": body["classification"],
                    "checks": 28,
                    "loss_counters": 23,
                    "cleanup": record["cleanup"],
                }
            )
        )
    except Exception:
        record["completed"] = False
        record["failure"] = "SAFE_STOP_NO_AUTOMATIC_RERUN"
        save()
        raise
    finally:
        # This authorization is for one action, not an open-ended dispatch loop.
        (SECURE / "collector/HARDSTOP").write_text(
            "Single qualification authorization consumed. No load escalation.\n"
        )
        subprocess.run(
            [
                "systemctl",
                "stop",
                "aa-private-collector.socket",
                "aa-private-collector.service",
                "aa-private-runner.service",
            ],
            check=False,
            timeout=10,
        )


if __name__ == "__main__":
    main()
