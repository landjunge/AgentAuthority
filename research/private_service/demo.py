"""Reproducible private service exercise, optionally one real independent VM write.

Creates only synthetic identities. Secret state stays in the operator-selected
0700 directory. Public transcripts are separately exportable and contain no tokens.
"""

import argparse
import copy
import json
import os
import secrets
import threading
from pathlib import Path

from research.private_service.http import call, server
from research.private_service.protocol import (
    AUDIENCE,
    SCHEMA,
    create_ca,
    digest,
    now_ms,
    request,
    sign,
    verify,
)
from research.private_service.service import Service


def initialize(state):
    state.mkdir(mode=0o700, parents=True, exist_ok=False)
    root, pin = create_ca(state / "root")
    report, report_pin = create_ca(state / "report")
    keys = {}
    for kid in ("sender", "receiver", "runner"):
        key, public = create_ca(state / kid)
        keys[kid] = {"private": str(key), "public": public}
    config = {
        "root_pins": {"test-a": pin, "test-b": pin},
        "report_private_key": str(report),
        "report_public_key": report_pin,
        "trust_version": "local-test-catalog-v1",
        "runner_tenant": "test-a",
        "runner_kid": "runner",
        "runner_private_key": keys["runner"]["private"],
        "tokens": [],
    }
    for tenant, role in (
        ("test-a", "admin"),
        ("test-a", "client"),
        ("test-a", "runner"),
        ("test-b", "reader"),
    ):
        config["tokens"].append({"tenant": tenant, "role": role, "token": secrets.token_hex(32)})
    config["runner_token"] = next(t["token"] for t in config["tokens"] if t["role"] == "runner")
    config_path = state / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    os.chmod(config_path, 0o600)
    return config, root, keys


def exercise(state, live=False):
    config, root, keys = initialize(state)
    service = Service(state, config)
    http = server(service)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{http.server_port}"
    tokens = {t["role"]: t["token"] for t in config["tokens"]}
    transcript = []

    def send(role, method, path, data=None, expected=None, label=None):
        status, response = call(url, tokens.get(role, "invalid"), method, path, data)
        transcript.append(
            {
                "case": label or path,
                "method": method,
                "path": path,
                "auth_role": role,
                "request": data,
                "status": status,
                "response": response,
            }
        )
        if expected is not None:
            assert status == expected, (path, status, response)
        return response

    def signed(kid, path, payload, **kwargs):
        return request(
            keys[kid]["private"],
            "test-a",
            kid,
            path,
            payload,
            kwargs.pop("idem", secrets.token_hex(16)),
            kwargs.pop("nonce", secrets.token_hex(32)),
            **kwargs,
        )

    try:
        for kid in keys:
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
                    "issued_ms": now_ms(),
                    "expires_ms": now_ms() + 60000,
                },
                201,
            )
            now = now_ms()
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
                    "issued_ms": now,
                    "expires_ms": now + 86400000,
                },
            )
            packet = signed(
                kid,
                "/v1/enrollments",
                {
                    "certificate": cert,
                    "proof": sign(keys[kid]["private"], challenge),
                    "replaces": None,
                },
            )
            send("admin", "POST", "/v1/enrollments", packet, 201)
        job_packet = signed(
            "sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"}
        )
        job = send("client", "POST", "/v1/jobs", job_packet, 202, "valid-job")
        jid = job["job_id"]
        send("client", "POST", "/v1/jobs", job_packet, 202, "identical-retry")
        altered = copy.deepcopy(job_packet)
        altered["body"]["nonce"] = secrets.token_hex(32)
        send("client", "POST", "/v1/jobs", altered, 401, "invalid-signature")
        replay = signed(
            "sender", "/v1/jobs", job_packet["body"]["payload"], nonce=job_packet["body"]["nonce"]
        )
        send("client", "POST", "/v1/jobs", replay, 409, "replay-new-idem")
        conflict = signed(
            "sender",
            "/v1/jobs",
            job_packet["body"]["payload"],
            idem=job_packet["body"]["idempotency_key"],
        )
        send("client", "POST", "/v1/jobs", conflict, 409, "idempotency-conflict")
        expired = signed("sender", "/v1/jobs", job_packet["body"]["payload"], now=now_ms() - 61000)
        send("client", "POST", "/v1/jobs", expired, 410, "expired")
        send("missing", "GET", f"/v1/jobs/{jid}", expected=401, label="missing-auth")
        send("reader", "GET", f"/v1/jobs/{jid}", expected=404, label="foreign-tenant-object")
        send("reader", "GET", f"/v1/jobs/{jid}/report", expected=404, label="foreign-tenant-report")
        send("client", "GET", f"/v1/jobs/{jid}/report", expected=409, label="report-pending")
        accept_path = f"/v1/jobs/{jid}/acceptances"
        wrong_accept = signed("receiver", accept_path, {"job_id": jid, "job_sha256": "0" * 64})
        send("client", "POST", accept_path, wrong_accept, 422, "wrong-exact-acceptance")
        acceptance = signed(
            "receiver", accept_path, {"job_id": jid, "job_sha256": digest(job_packet)}
        )
        send("client", "POST", accept_path, acceptance, 202, "valid-acceptance")
        if live:
            from research.private_service.runner import run_once

            result = run_once(
                service,
                lambda path, packet: (
                    201,
                    send("runner", "POST", path, packet, 201, "live-evidence"),
                ),
            )
            assert result["state"] == "completed"
            report = send(
                "client", "GET", f"/v1/jobs/{jid}/report", expected=200, label="live-report"
            )
            assert verify(config["report_public_key"], report["report"])
            assert report["report"]["body"]["classification"] == "BELEGT"
            assert all(v is True for v in report["report"]["body"]["checks"].values())
        else:
            service.claim()
            service.recover()
        send("client", "GET", f"/v1/jobs/{jid}", expected=200, label="final-status")
        # Revocation does not rewrite a historical signed report.
        revoke = signed("sender", "/v1/revocations", {"kid": "receiver"})
        send("admin", "POST", "/v1/revocations", revoke, 200, "revoke-receiver")
        retry = signed("receiver", accept_path, acceptance["body"]["payload"])
        send("client", "POST", accept_path, retry, 403, "revoked-key")
        send(
            "client",
            "GET",
            f"/v1/jobs/{jid}/report",
            expected=200,
            label="historical-after-revocation",
        )
        service = Service(state, config)
        send("client", "POST", "/v1/jobs", job_packet, 202, "retry-after-restart")
        return {
            "schema": "aa-private-exercise-v1",
            "live": live,
            "job_id": jid,
            "report_public_key": config["report_public_key"],
            "root_public_key": config["root_pins"]["test-a"],
            "public_keys": {k: v["public"] for k, v in keys.items()},
            "cases": transcript,
        }
    except Exception:
        (state / "exchanges-failure.json").write_text(
            json.dumps({"cases": transcript}, indent=2) + "\n"
        )
        raise
    finally:
        http.shutdown()
        thread.join(5)
        http.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    result = exercise(args.state.resolve(), args.live)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps({"live": args.live, "cases": len(result["cases"]), "job_id": result["job_id"]})
    )
