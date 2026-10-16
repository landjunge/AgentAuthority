"""Real HTTP contracts, persistent races and original evidence counterexamples."""

import copy
import json
import multiprocessing
import os
import secrets
import sqlite3
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from research.private_service.demo import initialize
from research.private_service.http import call, server
from research.private_service.protocol import (
    AUDIENCE,
    SCHEMA,
    Problem,
    blob,
    blob_digest,
    canonical,
    digest,
    evidence_values,
    now_ms,
    parse,
    request,
    sign,
    verify,
)
from research.private_service.service import Service


@pytest.fixture
def api(tmp_path):
    state = tmp_path / "private"
    config, root, keys = initialize(state)
    svc = Service(state, config)
    instance = server(svc)
    thread = threading.Thread(target=instance.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{instance.server_port}"
    tokens = {t["role"]: t["token"] for t in config["tokens"]}

    def send(role, method, path, data=None):
        result = call(url, tokens.get(role, "wrong-token"), method, path, data)
        return result

    def packet(kid, path, payload, **changes):
        signed = request(
            keys[kid]["private"],
            "test-a",
            kid,
            path,
            payload,
            secrets.token_hex(16),
            secrets.token_hex(32),
        )
        if changes:
            signed = sign(keys[kid]["private"], {**signed["body"], **changes})
        return signed

    def enrollment(kid, replaces=None, signer=None):
        stamp = now_ms()
        status, challenge = send(
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
        )
        assert status == 201
        cert = sign(
            signer or root,
            {
                "schema": SCHEMA,
                "domain": "AA-ENROLL-v1",
                "tenant": "test-a",
                "audience": AUDIENCE,
                "kid": kid,
                "public_key": keys[kid]["public"],
                "role": "runner" if kid == "runner" else "actor",
                "issued_ms": stamp,
                "expires_ms": stamp + 86400000,
            },
        )
        return packet(
            kid,
            "/v1/enrollments",
            {
                "certificate": cert,
                "proof": sign(keys[kid]["private"], challenge),
                "replaces": replaces,
            },
        )

    for kid in keys:
        assert send("admin", "POST", "/v1/enrollments", enrollment(kid))[0] == 201
    yield svc, send, packet, enrollment, config, keys, url
    instance.shutdown()
    thread.join(5)
    instance.server_close()
    # Tear down only this fixture's new ephemeral payloads, including tests that
    # intentionally left a running/pending job or crashed before commit.
    with svc.exclusive():
        with svc.connection() as db:
            db.execute(
                "UPDATE lifecycle SET blocked=?,reason='test_teardown',cleanup='pending'",
                (now_ms(),),
            )
            db.execute("UPDATE jobs SET request=NULL,acceptance=NULL,report=NULL,state='unknown'")
            db.execute("DELETE FROM dispatch_pins")
        svc.sweep()
        with svc.connection() as db:
            assert db.execute(
                "SELECT count(*) FROM lifecycle WHERE cleanup!='complete'"
            ).fetchone() == (0,)
        assert not list((state / "jobs").rglob("content.key"))
    # Only exact synthetic private files created by this fixture.
    for key in [
        state / "root/ca-private.pem",
        state / "report/ca-private.pem",
        *(Path(v["private"]) for v in keys.values()),
    ]:
        key.unlink()
        key.parent.rmdir()
    (state / "config.json").unlink()


def new_job(api):
    _, send, packet, *_ = api
    signed = packet("sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"})
    status, job = send("client", "POST", "/v1/jobs", signed)
    assert status == 202, job
    return signed, job


def queue_job(api):
    signed, job = new_job(api)
    path = f"/v1/jobs/{job['job_id']}/acceptances"
    acceptance = api[2]("receiver", path, {"job_id": job["job_id"], "job_sha256": digest(signed)})
    assert api[1]("client", "POST", path, acceptance)[0] == 202
    return signed, job, acceptance


def test_http_round_trip_restart_and_exact_retry(api):
    svc, send, _, _, config, *_ = api
    signed, job = new_job(api)
    assert send("client", "POST", "/v1/jobs", signed) == (202, job)
    restarted = Service(svc.state, config)
    assert restarted.mutate("test-a", "client", "/v1/jobs", signed) == (202, job)
    assert send("reader", "GET", job["status_url"])[0] == 404
    assert send("reader", "GET", job["report_url"])[0] == 404
    assert send("missing", "GET", job["status_url"])[0] == 401
    assert send("client", "GET", job["report_url"])[1]["code"] == "REPORT_PENDING"
    assert send("runner", "POST", "/v1/jobs", signed)[0] == 403


@pytest.mark.parametrize(
    "changes,status,code",
    [
        ({"nonce": "x"}, 422, "INVALID_FORMAT"),
        ({"tenant": "test-b"}, 403, "TENANT_MISMATCH"),
        ({"audience": "different-service"}, 422, "TARGET_MISMATCH"),
        ({"method": "GET"}, 422, "TARGET_MISMATCH"),
        ({"domain": "A4-DELEGATION-v1"}, 422, "TARGET_MISMATCH"),
        ({"issued_ms": 1, "expires_ms": 60001}, 410, "EXPIRED_OR_FUTURE"),
        ({"issued_ms": 9007199254740991, "expires_ms": 9007199254740991}, 410, "EXPIRED_OR_FUTURE"),
    ],
)
def test_signed_request_context_failures(api, changes, status, code):
    signed = api[2](
        "sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"}, **changes
    )
    result = api[1]("client", "POST", "/v1/jobs", signed)
    assert result[0] == status
    assert result[1]["code"] == code


def test_signature_replay_conflict_and_no_unexpected_fields(api):
    signed, _ = new_job(api)
    bad = copy.deepcopy(signed)
    bad["signature"] = "AA=="
    assert api[1]("client", "POST", "/v1/jobs", bad)[1]["code"] == "SIGNATURE_INVALID"
    for changes, code in (
        ({"idempotency_key": "new-id"}, "REPLAY"),
        ({"nonce": secrets.token_hex(32)}, "IDEMPOTENCY_CONFLICT"),
    ):
        changed = sign(api[5]["sender"]["private"], {**signed["body"], **changes})
        assert api[1]("client", "POST", "/v1/jobs", changed)[1]["code"] == code
    signed = api[2](
        "sender",
        "/v1/jobs",
        {"scenario": "a4-write16-v1", "receiver_kid": "receiver", "code": "ignored?"},
    )
    assert api[1]("client", "POST", "/v1/jobs", signed)[0] == 422


def test_exact_acceptance_and_source_role(api):
    signed, job = new_job(api)
    path = f"/v1/jobs/{job['job_id']}/acceptances"
    wrong = api[2]("receiver", path, {"job_id": job["job_id"], "job_sha256": "0" * 64})
    assert api[1]("client", "POST", path, wrong)[1]["code"] == "DELEGATION_MISMATCH"
    wrong = api[2]("sender", path, {"job_id": job["job_id"], "job_sha256": digest(signed)})
    assert api[1]("client", "POST", path, wrong)[1]["code"] == "OBJECT_FORBIDDEN"
    evidence_path = f"/v1/jobs/{job['job_id']}/evidence"
    assert api[1]("client", "POST", evidence_path, api[2]("sender", evidence_path, {}))[0] == 403


def test_unpinned_ca_and_possession_proof(api):
    enrollment = api[3]("receiver", signer=Path(api[5]["sender"]["private"]))
    assert api[1]("admin", "POST", "/v1/enrollments", enrollment)[1]["code"] == "TRUST_PIN_INVALID"
    enrollment = api[3]("receiver")
    enrollment["body"]["payload"]["proof"]["signature"] = "AA=="
    enrollment = sign(api[5]["receiver"]["private"], enrollment["body"])
    assert api[1]("admin", "POST", "/v1/enrollments", enrollment)[1]["code"] == "POP_INVALID"


@pytest.mark.parametrize("running", [False, True])
def test_revocation_stops_admission_and_preserves_historical_read(api, running):
    svc, send, packet, *_ = api
    _, job, acceptance = queue_job(api)
    if running:
        assert svc.claim() is not None
    revoke = packet("sender", "/v1/revocations", {"kid": "receiver"})
    assert send("admin", "POST", "/v1/revocations", revoke)[0] == 200
    assert (
        send("client", "POST", acceptance["body"]["path"], acceptance)[1]["code"] == "KEY_REVOKED"
    )
    report = send("client", "GET", job["report_url"])[1]
    assert report["report"]["body"]["classification"] == "UNBEKANNT"
    assert report["current_key_status"]["receiver"] == "revoked"
    assert verify(api[4]["report_public_key"], report["report"])
    assert svc.claim() is None


def test_rotation_is_atomic_and_key_id_never_reused(api):
    svc, send, _, enroll, *_ = api
    invalid = enroll("sender", replaces="receiver")
    assert send("admin", "POST", "/v1/enrollments", invalid)[1]["code"] == "KEY_ID_REUSED"
    with svc.connection() as db:
        assert db.execute("SELECT revoked FROM service_keys WHERE kid='receiver'").fetchone() == (
            None,
        )
    # Rotate to a fresh ID using a new operator-approved certificate and proof.
    from research.private_service.protocol import create_ca

    new_key, new_public = create_ca(svc.state / "next")
    api[5]["next"] = {"private": str(new_key), "public": new_public}
    valid = enroll("next", replaces="missing-predecessor")
    assert send("admin", "POST", "/v1/enrollments", valid)[1]["code"] == "KEY_UNKNOWN"
    with svc.connection() as db:
        assert db.execute("SELECT 1 FROM service_keys WHERE kid='next'").fetchone() is None
        assert db.execute("SELECT revoked FROM service_keys WHERE kid='sender'").fetchone() == (
            None,
        )
    valid["body"]["payload"]["replaces"] = "sender"
    valid = sign(new_key, valid["body"])
    assert send("admin", "POST", "/v1/enrollments", valid)[0] == 201
    with svc.connection() as db:
        assert (
            db.execute("SELECT revoked FROM service_keys WHERE kid='sender'").fetchone()[0]
            is not None
        )


def test_running_recovery_never_requeues_action(api):
    svc = api[0]
    _, job, _ = queue_job(api)
    assert svc.claim() is not None
    Service(svc.state, api[4]).recover()
    assert svc.claim() is None
    report = api[1]("client", "GET", job["report_url"])[1]["report"]
    assert report["body"]["reason"] == "WORKER_INTERRUPTED"
    assert report["body"]["classification"] == "UNBEKANNT"


def child_mutation(state, config, packet, go, result, crash=None):
    svc = Service(state, config)
    go.wait(15)
    if crash == "before_commit":
        original = svc._operation

        def abort(*args):
            original(*args)
            os._exit(37)

        svc._operation = abort
    response = svc.mutate("test-a", "client", "/v1/jobs", packet)
    if crash == "after_commit":
        os._exit(37)
    result.put(response)


@pytest.mark.parametrize("crash", [None, "before_commit", "after_commit"])
def test_process_races_and_commit_crashes(api, crash):
    svc, _, packet, _, config, *_ = api
    signed = packet("sender", "/v1/jobs", {"scenario": "a4-write16-v1", "receiver_kid": "receiver"})
    ctx = multiprocessing.get_context("spawn")
    go, results = ctx.Event(), ctx.Queue()
    processes = [
        ctx.Process(target=child_mutation, args=(svc.state, config, signed, go, results, crash))
        for _ in range(6 if crash is None else 1)
    ]
    try:
        for p in processes:
            p.start()
        go.set()
        responses = [] if crash else [results.get(timeout=30) for _ in processes]
        for p in processes:
            p.join(30)
            assert p.exitcode == (37 if crash else 0)
        response = Service(svc.state, config).mutate("test-a", "client", "/v1/jobs", signed)
        assert all(r == response for r in responses)
        with svc.connection() as db:
            assert db.execute("SELECT count(*) FROM jobs").fetchone() == (1,)
    finally:
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(5)
        results.close()


def test_http_parser_origin_limits_and_technical_failure(api, monkeypatch):
    svc, send, *_ = api
    signed, _ = new_job(api)
    monkeypatch.setattr(
        svc, "mutate", lambda *args: (_ for _ in ()).throw(sqlite3.OperationalError("secret-path"))
    )
    status, error = send("client", "POST", "/v1/jobs", signed)
    assert status == 503 and error["code"] == "SERVICE_UNAVAILABLE"
    assert "secret" not in json.dumps(error)
    url = api[6]
    token = next(t["token"] for t in api[4]["tokens"] if t["role"] == "client")
    for raw, origin, status in (
        (b'{"x":1,"x":2}', None, 400),
        (b"{}", "http://evil.invalid", 403),
        (b" " * 262145, None, 413),
    ):
        req = Request(
            url + "/v1/jobs",
            data=raw,
            headers={
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json",
                **({"Origin": origin} if origin else {}),
            },
        )
        with pytest.raises(HTTPError) as caught:
            urlopen(req, timeout=10)
        assert caught.value.code == status
        caught.value.close()


@pytest.mark.parametrize(
    "raw",
    [b'{"x":1.1}', b'{"x":"\\u00e4"}', b'{"x":NaN}', b'{"x":9007199254740992}', b'{"x":"\\n"}'],
)
def test_restricted_jcs_rejects_ambiguous_or_unsupported_values(raw):
    with pytest.raises(Problem):
        parse(raw)


def test_restricted_jcs_expected_bytes():
    assert canonical(parse(b'{"z":1,"a":[true,null,"abc"]}')) == b'{"a":[true,null,"abc"],"z":1}'


@pytest.fixture
def actual_evidence(api):
    # Regression against this session's real live artifact, never counted as new execution.
    path = Path(__file__).resolve().parents[1] / "docs/private-service-20261016/live-exchanges.json"
    transcript = json.loads(path.read_text())
    cases = {c["case"]: c for c in transcript["cases"]}
    original = cases["valid-job"]["request"]
    acceptance = cases["valid-acceptance"]["request"]
    package = cases["live-evidence"]["request"]["body"]["payload"]
    jid = transcript["job_id"]
    # Independent control-plane pin archived separately, never read from upload.
    pins = json.loads((path.parent / "live-dispatch-pins.json").read_text())
    with api[0].connection() as db:
        db.execute(
            "INSERT INTO lifecycle (tenant,job_id,retain_until) VALUES (?,?,?)",
            ("test-a", jid, now_ms() + 86500000),
        )
        db.execute(
            "INSERT INTO dispatch_pins VALUES (?,?,?)",
            ("test-a", jid, api[0].seal("test-a", jid, "pins", pins)),
        )
    row = (
        "sender",
        "receiver",
        json.dumps(original),
        json.dumps(acceptance),
        "running",
        now_ms(),
        None,
        now_ms(),
    )
    return jid, row, package


@pytest.mark.parametrize(
    "mutation,expected",
    [
        ("none", "BELEGT"),
        ("missing", "UNVOLLSTAENDIG"),
        ("signature", "WIDERSPRUECHLICH"),
        ("binding", "WIDERSPRUECHLICH"),
        ("duplicate", "WIDERSPRUECHLICH"),
        ("loss", "UNBEKANNT"),
        ("pin", "WIDERSPRUECHLICH"),
    ],
)
def test_original_evidence_counterexamples(api, actual_evidence, mutation, expected):
    jid, row, original = actual_evidence
    package = evidence_values(copy.deepcopy(original))
    manifest = copy.deepcopy(original["manifest"])
    if mutation == "missing":
        package["trial"] = None
        manifest["complete"] = False
    elif mutation == "signature":
        package["trial"]["receipt"]["body"]["acceptance"]["signature"] = "AA=="
    elif mutation == "binding":
        # Alter expected service job, leaving authentic A4 signatures unchanged.
        wrong = json.loads(row[2])
        wrong["body"]["nonce"] = "0" * 64
        row = (*row[:2], json.dumps(wrong), *row[3:])
    elif mutation == "duplicate":
        package["capture"].append(package["capture"][0])
    elif mutation == "loss":
        next(r["summary"] for r in package["capture"] if "summary" in r)["entry_probe_nmissed"] = (
            None
        )
    elif mutation == "pin":
        with api[0].connection() as db:
            pin = api[0].unseal(
                "test-a", jid, "pins", db.execute("SELECT context FROM dispatch_pins").fetchone()[0]
            )
            pin["pinned_ca_public_key"] = api[5]["sender"]["public"]
            db.execute(
                "UPDATE dispatch_pins SET context=?", (api[0].seal("test-a", jid, "pins", pin),)
            )
    for key in ("registry", "capture", "trial"):
        value = package[key]
        raw = (
            ("\n".join(json.dumps(r) for r in value) + "\n").encode()
            if key == "capture"
            else json.dumps(value).encode()
        )
        package[key] = None if value is None else blob(raw)
        manifest[key + "_sha256"] = blob_digest(package[key])
    package["manifest"] = manifest
    report = api[0].verify_evidence("test-a", jid, row, package, now_ms(), "runner")
    assert report["classification"] == expected
    assert report["provider_model_session"] == "UNBEKANNT"
    assert report["grants_rights"] is False
    if expected != "BELEGT":
        assert report["layers"]["independent_write"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "mode,status,code",
    [
        ("missing", 201, None),
        ("bad-digest", 422, "EVIDENCE_DIGEST_MISMATCH"),
        ("upload-trust", 403, "SOURCE_FORBIDDEN"),
        ("expired", 409, "STATE_CONFLICT"),
    ],
)
def test_evidence_http_admission_and_missing_report(api, actual_evidence, mode, status, code):
    jid, row, payload = actual_evidence
    payload = copy.deepcopy(payload)
    with api[0].connection() as db:
        db.execute(
            "INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                "test-a",
                jid,
                row[0],
                row[1],
                api[0].seal("test-a", jid, "request", json.loads(row[2])),
                api[0].seal("test-a", jid, "acceptance", json.loads(row[3])),
                "running",
                now_ms() - 180001 if mode == "expired" else now_ms(),
                None,
                now_ms(),
            ),
        )
    if mode == "missing":
        payload["trial"] = None
        payload["manifest"]["complete"] = False
        payload["manifest"]["trial_sha256"] = blob_digest(None)
    elif mode == "bad-digest":
        payload["manifest"]["capture_sha256"] = "0" * 64
    elif mode == "upload-trust":
        payload["manifest"]["source_class"] = "customer-asserted"
    path = f"/v1/jobs/{jid}/evidence"
    result = api[1]("runner", "POST", path, api[2]("runner", path, payload))
    assert result[0] == status, result
    if code:
        assert result[1]["code"] == code
    else:
        report = api[1]("client", "GET", f"/v1/jobs/{jid}/report")[1]["report"]
        assert report["body"]["classification"] == "UNVOLLSTAENDIG"
        assert verify(api[4]["report_public_key"], report)


def test_browser_and_wrong_host(api):
    with urlopen(api[6], timeout=10) as response:
        page = response.read().decode()
        assert 'type="password"' in page
        assert "no-store" in response.headers["Cache-Control"]
        assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    with urlopen(api[6] + "/inspector.js", timeout=10) as response:
        script = response.read().decode()
        assert ".textContent=" in script and "innerHTML" not in script
        assert "localStorage" not in script
    req = Request(api[6] + "/", headers={"Host": "evil.invalid"})
    with pytest.raises(HTTPError) as caught:
        urlopen(req, timeout=10)
    assert caught.value.code == 403
    caught.value.close()


def test_challenge_retry_replay_and_scope(api):
    stamp = now_ms()
    payload = {
        "schema": SCHEMA,
        "kid": "fresh",
        "public_key": api[5]["sender"]["public"],
        "idempotency_key": secrets.token_hex(16),
        "nonce": secrets.token_hex(32),
        "issued_ms": stamp,
        "expires_ms": stamp + 60000,
    }
    first = api[1]("admin", "POST", "/v1/challenges", payload)
    assert first[0] == 201
    assert api[1]("admin", "POST", "/v1/challenges", payload) == first
    assert api[1]("client", "POST", "/v1/challenges", payload)[0] == 403
    changed = {**payload, "idempotency_key": secrets.token_hex(16)}
    assert api[1]("admin", "POST", "/v1/challenges", changed)[1]["code"] == "REPLAY"
    changed = {**payload, "nonce": secrets.token_hex(32)}
    assert api[1]("admin", "POST", "/v1/challenges", changed)[1]["code"] == "IDEMPOTENCY_CONFLICT"


def test_expired_key_does_not_hide_historical_report(api):
    svc = api[0]
    _, job, _ = queue_job(api)
    svc.claim()
    svc.recover()
    with svc.connection() as db:
        db.execute("UPDATE service_keys SET expires=0 WHERE kid='sender'")
    response = api[1]("client", "GET", job["report_url"])
    assert response[0] == 200
    assert response[1]["current_key_status"]["sender"] == "expired"
    assert verify(api[4]["report_public_key"], response[1]["report"])
