"""Controlled-clock HTTP and real namespace checks, only owned synthetic states."""

import copy
import json
import multiprocessing
import socket
import sqlite3
import struct
import tempfile
import time
from urllib.request import urlopen

import pytest
import test_private_service as contracts
from test_private_service import new_job, queue_job

from research.private_service.crypto import crypt
from research.private_service.protocol import Problem, digest, now_ms, sign, verify
from research.private_service.retention import (
    MAX_REQUEST,
    REPORT_TTL,
    RETRY_CLOCK,
    iso,
    private_dir,
)
from research.private_service.service import Service


@pytest.fixture
def api(tmp_path):
    yield from contracts.api.__wrapped__(tmp_path)


@pytest.fixture
def controlled(api, monkeypatch):
    clock = [now_ms()]
    monkeypatch.setattr(time, "time", lambda: clock[0] / 1000)
    return api, clock


def complete(api):
    signed, job, _acceptance = queue_job(api)
    assert api[0].claim()
    api[0].recover()
    status, report = api[1]("client", "GET", job["report_url"])
    assert status == 200
    return signed, job, report


def receipt(api, job, report, kid="sender", **changes):
    path = f"/v1/jobs/{job['job_id']}/receipts"
    payload = {
        "job_id": job["job_id"],
        "report_version": "1",
        "report_sha256": digest(report["report"]),
        "received_complete": True,
    }
    payload.update(changes)
    return path, api[2](kid, path, payload)


def scan_files(root, marker):
    return [
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and not p.is_symlink() and marker in p.read_bytes()
    ]


def test_receipt_signature_tenant_digest_and_complete_binding(controlled):
    api, clock = controlled
    svc, send, _, _, config, *_ = api
    _, job, report = complete(api)
    assert report["expires_at"] == iso(clock[0] + REPORT_TTL)
    assert verify(config["report_public_key"], report["report"])
    assert report["report"]["body"]["expires_at"] == report["expires_at"]
    path, packet = receipt(api, job, report)
    forged = copy.deepcopy(packet)
    forged["signature"] = "AA=="
    assert send("client", "POST", path, forged)[1]["code"] == "SIGNATURE_INVALID"
    assert send("missing", "POST", path, packet)[0] == 401
    assert send("reader", "POST", path, packet)[0] == 403
    for change in (
        {"received_complete": False},
        {"report_sha256": "0" * 64},
        {"report_version": "2"},
        {"job_id": "wrong"},
    ):
        wrong = receipt(api, job, report, **change)[1]
        assert send("client", "POST", path, wrong)[1]["code"] == "RECEIPT_MISMATCH"
    # An enrolled actor belonging to another object cannot acknowledge this one.
    from research.private_service.protocol import create_ca

    key, public = create_ca(svc.state / "outsider")
    api[5]["outsider"] = {"private": str(key), "public": public}
    assert send("admin", "POST", "/v1/enrollments", api[3]("outsider"))[0] == 201
    wrong = receipt(api, job, report, kid="outsider")[1]
    assert send("client", "POST", path, wrong)[1]["code"] == "OBJECT_FORBIDDEN"
    # Valid tenant-b signed request targets a missing object, never tenant-a data.
    with svc.connection() as db:
        db.execute(
            "INSERT INTO service_keys VALUES (?,?,?,?,?,?,NULL)",
            (
                "test-b",
                "sender",
                api[5]["sender"]["public"],
                "actor",
                clock[0],
                clock[0] + 86400000,
            ),
        )
    foreign = sign(api[5]["sender"]["private"], {**packet["body"], "tenant": "test-b"})
    with pytest.raises(Problem) as caught:
        svc.mutate("test-b", "client", path, foreign)
    assert caught.value.code == "NOT_FOUND"
    assert send("client", "GET", job["report_url"])[0] == 200
    code, value = send("client", "POST", path, packet)
    assert code == 200 and value["receipt_state"] == "confirmed"
    assert value["access_state"] == "blocked" and value["cleanup_confirmed"] is True
    assert value["cleanup_completed_at"] == iso(clock[0])
    assert value["content_key_state"] == "absent_from_owned_namespace"
    assert send("client", "GET", job["report_url"])[1]["code"] == "REPORT_GONE"
    # Exact and fresh independent confirmations are both safe and stable.
    assert send("client", "POST", path, packet) == (code, value)
    assert send("client", "POST", *receipt(api, job, report)) == (code, value)
    assert Service(svc.state, config).read("test-a", job["job_id"])[1] == value


@pytest.mark.parametrize("aborted", [False, True])
def test_get_and_aborted_transfer_never_acknowledge(controlled, aborted, capfd):
    api, _ = controlled
    _, job, report = complete(api)
    if aborted:
        # Force a TCP RST without consuming the response body.
        port = int(api[6].rsplit(":", 1)[1])
        token = next(t["token"] for t in api[4]["tokens"] if t["role"] == "client")
        sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        raw = (
            f"GET {job['report_url']} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {token}\r\n\r\n"
        ).encode()
        sock.sendall(raw)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        sock.close()
    else:
        assert api[1]("client", "GET", job["report_url"])[0] == 200
    status = api[1]("client", "GET", job["status_url"])[1]
    assert status["receipt_state"] == "unconfirmed"
    assert status["access_state"] == "available"
    assert api[1]("client", "GET", job["report_url"])[1]["report"] == report["report"]
    assert capfd.readouterr().err == ""


def test_absolute_deadline_boundary_and_overdue_restart(controlled):
    api, clock = controlled
    svc = api[0]
    _, job, report = complete(api)
    deadline = clock[0] + REPORT_TTL
    clock[0] = deadline - 1
    assert (
        Service(svc.state, api[4]).read("test-a", job["job_id"], True)[1]["expires_at"]
        == report["expires_at"]
    )
    clock[0] = deadline
    restarted = Service(svc.state, api[4])
    with pytest.raises(Problem) as caught:
        restarted.read("test-a", job["job_id"], True)
    assert caught.value.code == "REPORT_GONE"
    status = restarted.read("test-a", job["job_id"])[1]
    assert status["deletion_reason"] == "expired" and status["cleanup_confirmed"]
    assert status["expires_at"] == report["expires_at"]
    assert not svc.job_dir("test-a", job["job_id"]).exists()


def test_restart_after_service_was_down_beyond_deadline(controlled):
    api, clock = controlled
    svc = api[0]
    _, job, report = complete(api)
    clock[0] += REPORT_TTL + 1
    # No operation/timer on the stopped-service equivalent until constructor.
    restarted = Service(svc.state, api[4])
    status = restarted.read("test-a", job["job_id"])[1]
    assert status["cleanup_confirmed"] and status["expires_at"] == report["expires_at"]
    assert status["access_state"] == "blocked"


def test_cleanup_failure_is_honest_retry_does_not_extend_deadline(controlled, monkeypatch):
    api, clock = controlled
    svc = api[0]
    _, job, report = complete(api)
    remove = svc._remove_tree
    monkeypatch.setattr(
        svc, "_remove_tree", lambda p: (_ for _ in ()).throw(PermissionError("do-not-log-secret"))
    )
    path, packet = receipt(api, job, report)
    code, result = api[1]("client", "POST", path, packet)
    assert code == 200 and result["access_state"] == "blocked"
    assert result["cleanup_state"] == "failed" and not result["cleanup_confirmed"]
    assert result["cleanup_completed_at"] is None
    assert result["content_key_state"] == "present"
    assert api[1]("client", "GET", job["report_url"])[0] == 410
    clock[0] += 10
    monkeypatch.setattr(svc, "_remove_tree", remove)
    code, result = api[1]("client", "POST", path, packet)
    assert code == 200 and result["cleanup_confirmed"]
    assert result["expires_at"] == report["expires_at"]
    assert result["received_at"] == report["completed_at"]
    assert "do-not-log-secret" not in json.dumps(result)


def test_sqlite_checkpoint_failure_cannot_confirm_cleanup(controlled, monkeypatch):
    api, _ = controlled
    svc = api[0]
    _, job, report = complete(api)
    # A real reader pins old WAL frames; key removal alone is not file cleanup.
    reader = sqlite3.connect(svc.database, isolation_level=None)
    reader.execute("BEGIN")
    reader.execute("SELECT * FROM jobs").fetchall()
    # Short SQLite busy wait for this controlled failure.
    original = svc.connection
    from contextlib import contextmanager

    @contextmanager
    def short_connection():
        with original() as db:
            db.execute("PRAGMA busy_timeout=1")
            yield db

    monkeypatch.setattr(svc, "connection", short_connection)
    try:
        code, result = api[1]("client", "POST", *receipt(api, job, report))
        assert code == 200 and result["cleanup_state"] == "failed"
        assert result["cleanup_completed_at"] is None
        assert result["content_key_state"] == "absent_from_owned_namespace"
    finally:
        reader.close()
    assert svc.read("test-a", job["job_id"])[1]["cleanup_confirmed"]


def test_content_inventory_encryption_input_and_report_cleanup(controlled, monkeypatch):
    api, clock = controlled
    svc = api[0]
    signed, job, acceptance = queue_job(api)
    jid = job["job_id"]
    # No signature transport tempfiles may be made by the service.
    monkeypatch.setattr(
        tempfile,
        "TemporaryDirectory",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("tempfile")),
    )
    marker = b"OWNED-SYNTHETIC-CONTENT-20261016"
    scratch = svc.job_dir("test-a", jid) / "scratch"
    private_dir(scratch)
    intermediate = svc.seal("test-a", jid, "intermediate", marker.decode())
    (scratch / "intermediate.gcm").write_text(intermediate)
    (scratch / "intermediate.gcm").chmod(0o600)
    svc.claim()
    with svc.exclusive(), svc.connection() as db:
        db.execute("BEGIN IMMEDIATE")
        report = {
            "schema": "aa-report-v1",
            "tenant": "test-a",
            "job_id": jid,
            "classification": "UNBEKANNT",
            "issued_ms": clock[0],
            "synthetic_marker": marker.decode(),
        }
        svc.finish(db, "test-a", jid, report, "unknown", clock[0])
        db.commit()
    status = svc.read("test-a", jid)[1]
    assert status["inputs_cleanup_completed_at"] == iso(clock[0])
    assert not scratch.exists()
    assert scan_files(svc.state, marker) == []
    with svc.connection() as db:
        row = db.execute("SELECT request,acceptance,report FROM jobs WHERE id=?", (jid,)).fetchone()
        assert row[:2] == (None, None) and row[2].startswith("gcm1:")
        assert db.execute("SELECT count(*) FROM dispatch_pins").fetchone() == (0,)
        assert db.execute("PRAGMA secure_delete").fetchone() == (1,)
        assert db.execute("PRAGMA temp_store").fetchone() == (2,)
    for file in svc.state.rglob("*"):
        assert file.stat().st_mode & 0o077 == 0, file
    envelope = svc.read("test-a", jid, True)[1]
    keyfile = svc.job_dir("test-a", jid) / "content.key"
    key = keyfile.read_bytes()
    ciphertext = row[2]
    assert svc.mutate("test-a", "client", *receipt(api, job, envelope))[1]["cleanup_confirmed"]
    assert not keyfile.exists() and scan_files(svc.state, marker) == []
    assert scan_files(svc.state, key) == []
    assert scan_files(svc.state, ciphertext.encode()) == []
    # Request envelope bytes do not remain in SQLite/WAL/journal/files either.
    assert scan_files(svc.state, signed["signature"].encode()) == []
    assert scan_files(svc.state, acceptance["signature"].encode()) == []


@pytest.mark.parametrize("state", ["awaiting_acceptance", "queued", "running"])
def test_cancel_failure_or_hang_removes_inputs_and_never_requeues(controlled, state):
    api, clock = controlled
    svc = api[0]
    _, job = new_job(api) if state == "awaiting_acceptance" else queue_job(api)[:2]
    if state == "running":
        assert svc.claim()
        clock[0] += 180000
        expected_reason = "WORKER_TIMEOUT"
    else:
        path = f"/v1/jobs/{job['job_id']}/cancellations"
        packet = api[2]("sender", path, {"job_id": job["job_id"]})
        assert api[1]("client", "POST", path, packet)[0] == 200
        expected_reason = "CANCELLED_NO_RERUN"
    value = api[1]("client", "GET", job["report_url"])[1]
    assert value["report"]["body"]["reason"] == expected_reason
    assert value["inputs_cleanup_completed_at"]
    with svc.connection() as db:
        assert db.execute("SELECT request,acceptance FROM jobs").fetchone() == (None, None)
    if state != "running":
        assert svc.claim() is None


def test_waiting_timeout_is_cleaned_without_worker(controlled):
    api, clock = controlled
    _, job = new_job(api)
    clock[0] += 60000
    report = api[1]("client", "GET", job["report_url"])[1]
    assert report["report"]["body"]["reason"] == "REQUEST_EXPIRED"
    assert report["inputs_cleanup_completed_at"]


def test_replay_survives_receipt_then_expires_at_key_epoch(controlled):
    api, clock = controlled
    svc = api[0]
    signed, job, report = complete(api)
    assert api[1]("client", "POST", *receipt(api, job, report))[0] == 200
    assert api[1]("client", "POST", "/v1/jobs", signed)[1]["job_id"] == job["job_id"]
    altered = sign(api[5]["sender"]["private"], {**signed["body"], "idempotency_key": "another"})
    assert api[1]("client", "POST", "/v1/jobs", altered)[1]["code"] == "REPLAY"
    with svc.connection() as db:
        expiry = db.execute(
            "SELECT retain_until FROM request_deadlines WHERE tenant=? AND idem=?",
            ("test-a", signed["body"]["idempotency_key"]),
        ).fetchone()[0]
        key_expiry = db.execute(
            "SELECT expires FROM service_keys WHERE tenant='test-a' AND kid='sender'"
        ).fetchone()[0]
        final_expiry = max(
            db.execute("SELECT max(retain_until) FROM request_deadlines").fetchone()[0],
            db.execute("SELECT max(retain_until) FROM lifecycle").fetchone()[0],
        )
    assert expiry == key_expiry + MAX_REQUEST + RETRY_CLOCK
    clock[0] = final_expiry
    with svc.exclusive():
        svc.sweep()
    with svc.connection() as db:
        assert db.execute("SELECT count(*) FROM requests").fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)
        assert db.execute("SELECT count(*) FROM service_keys").fetchone()[0] == 3
    assert api[1]("client", "POST", "/v1/jobs", signed)[1]["code"] == "EXPIRED_OR_FUTURE"
    forged_fresh = api[2]("sender", "/v1/jobs", signed["body"]["payload"])
    assert api[1]("client", "POST", "/v1/jobs", forged_fresh)[1]["code"] == "KEY_EXPIRED"


def test_new_runner_is_fail_closed_before_vm_or_host_artifacts(controlled, monkeypatch):
    from research.private_service import runner

    api, _ = controlled
    _, job, _ = queue_job(api)
    monkeypatch.setattr(runner, "qualify_environment", lambda: pytest.fail("VM touched"))
    with pytest.raises(Problem) as caught:
        runner.run_once(api[0], lambda *args: pytest.fail("delivery"))
    assert caught.value.code == "EPHEMERAL_RUNNER_STORAGE_UNQUALIFIED"
    assert api[0].read("test-a", job["job_id"])[1]["state"] == "queued"
    assert not list(api[0].state.glob("evidence-*"))


def test_legacy_state_and_symlink_targets_are_preserved(tmp_path):
    state = tmp_path / "historical"
    state.mkdir()
    with sqlite3.connect(state / "service.sqlite") as db:
        db.execute("CREATE TABLE jobs (report TEXT)")
        db.execute("INSERT INTO jobs VALUES (?)", ("historical evidence",))
    before = (state / "service.sqlite").read_bytes()
    with pytest.raises(Problem) as caught:
        Service(state, {})
    assert caught.value.code == "LEGACY_STATE_PRESERVED"
    assert (state / "service.sqlite").read_bytes() == before
    target = tmp_path / "foreign"
    target.mkdir()
    symlink = tmp_path / "symlink"
    symlink.symlink_to(target)
    with pytest.raises(Problem):
        Service(symlink, {})
    assert not list(target.iterdir())


def test_aes_gcm_known_vector_tamper_and_cross_object_binding():
    # NIST SP800-38D AES-256-GCM, zero key/IV, one zero block.
    raw = bytes.fromhex(
        "000000000000000000000000cea7403d4d606b6e074ec5d3baf39d18d0d1c8a799996bf0265b98b5d48ab919"
    )
    assert crypt(bytes(32), raw, b"", False) == bytes(16)
    encrypted = crypt(bytes(32), b"synthetic", b"tenant:job:report", True)
    assert crypt(bytes(32), encrypted, b"tenant:job:report", False) == b"synthetic"
    for aad, value in (
        (b"foreign:job:report", encrypted),
        (b"tenant:job:report", encrypted[:-1] + bytes([encrypted[-1] ^ 1])),
    ):
        with pytest.raises(ValueError):
            crypt(bytes(32), value, aad, False)


def race_reader(state, config, jid, gate, results):
    svc = Service(state, config)
    gate.wait(10)
    try:
        results.put(("read", svc.read("test-a", jid, True)[0]))
    except Problem as error:
        results.put(("read", error.status))


def race_receipt(state, config, packet, gate, results):
    svc = Service(state, config)
    gate.wait(10)
    value = svc.mutate("test-a", "client", packet["body"]["path"], packet)
    results.put(("receipt", value[1]["cleanup_confirmed"]))


def test_cross_process_fetch_receipt_race_is_linearized(api):
    _, job, report = complete(api)
    packet = receipt(api, job, report)[1]
    ctx = multiprocessing.get_context("spawn")
    gate, results = ctx.Event(), ctx.Queue()
    ps = [
        ctx.Process(target=race_reader, args=(api[0].state, api[4], job["job_id"], gate, results))
        for _ in range(3)
    ]
    ps.append(ctx.Process(target=race_receipt, args=(api[0].state, api[4], packet, gate, results)))
    try:
        for p in ps:
            p.start()
        gate.set()
        observed = [results.get(timeout=20) for _ in ps]
        for p in ps:
            p.join(20)
            assert p.exitcode == 0
        assert ("receipt", True) in observed
        assert all(value in (200, 410) for kind, value in observed if kind == "read")
        assert api[1]("client", "GET", job["report_url"])[0] == 410
    finally:
        for p in ps:
            if p.is_alive():
                p.terminate()
                p.join(5)
        results.close()


def test_notice_is_available_before_auth_and_reports_actual_states(api):
    with urlopen(api[6], timeout=5) as response:
        page = response.read().decode()
    assert 'lang="de"' in page and 'lang="en"' in page
    assert "24 hours of completion" in page and "65 seconds" in page
    with urlopen(api[6] + "/inspector.js", timeout=5) as response:
        script = response.read().decode()
    for field in ("expires_at", "receipt_state", "cleanup_state", "cleanup_completed_at"):
        assert field in script


def test_client_only_confirms_verified_complete_file(api, tmp_path):
    from research.private_service.client import confirm

    _, job, report = complete(api)
    destination = tmp_path / "received.json"
    from research.private_service.retention import write_private

    write_private(destination, json.dumps(report).encode())
    try:
        value = json.loads(destination.read_bytes())
        wrong = copy.deepcopy(value)
        wrong["report"]["signature"] = "AA=="
        with pytest.raises(Problem):
            confirm(api[4], job["job_id"], wrong, lambda *a: pytest.fail("posted bad file"))
        with pytest.raises(Problem):
            confirm(api[4], "different-job", value, lambda *a: pytest.fail("posted foreign file"))
        result = confirm(
            api[4],
            job["job_id"],
            value,
            lambda path, packet: api[1]("client", "POST", path, packet),
        )
        assert result[0] == 200 and result[1]["cleanup_confirmed"]
        assert destination.exists()  # Receiver copy is explicitly outside service scope.
    finally:
        destination.unlink()


def test_cleanup_retries_after_restart(controlled, monkeypatch):
    api, _ = controlled
    svc = api[0]
    _, job, report = complete(api)
    monkeypatch.setattr(svc, "_clean", lambda *a: (_ for _ in ()).throw(OSError("fault")))
    result = api[1]("client", "POST", *receipt(api, job, report))[1]
    assert result["cleanup_state"] == "failed"
    restarted = Service(svc.state, api[4])
    status = restarted.read("test-a", job["job_id"])[1]
    assert status["cleanup_confirmed"] and status["receipt_state"] == "confirmed"


def test_privacy_notice_api_precedes_submission(api):
    with urlopen(api[6] + "/v1/privacy", timeout=5) as response:
        value = json.loads(response.read())
        assert response.headers["Cache-Control"] == "no-store"
    assert value["report_max_age_seconds"] == 86400
    assert value["de"] and value["en"] and "5000ms" in value["replay_retention"]


def test_orphan_key_and_encrypted_scratch_removed_on_restart(api):
    svc = api[0]
    jid = "e" * 32
    # Emulate a process killed after files were fsynced but before DB commit.
    value = svc.seal("test-a", jid, "request", {"synthetic": "orphan-only"})
    folder = svc.job_dir("test-a", jid)
    (folder / "orphan.gcm").write_text(value)
    (folder / "orphan.gcm").chmod(0o600)
    Service(svc.state, api[4])
    assert not folder.exists()


def test_idle_service_sweeps_expiry_without_download(controlled):
    api, clock = controlled
    svc = api[0]
    _, job, _ = complete(api)
    clock[0] += REPORT_TTL
    # Invoke the real HTTPServer idle hook deterministically, no wall-clock sleep.
    from research.private_service.http import server

    http = server(svc)
    try:
        http.service_actions()
        with svc.connection() as db:
            row = db.execute(
                "SELECT blocked,cleanup,cleaned FROM lifecycle WHERE job_id=?", (job["job_id"],)
            ).fetchone()
        assert row[0] == clock[0] and row[1] == "complete" and row[2] == clock[0]
    finally:
        http.server_close()


def test_clock_rollback_after_pruning_cannot_reexecute_old_request(controlled):
    api, clock = controlled
    svc = api[0]
    signed, job, report = complete(api)
    api[1]("client", "POST", *receipt(api, job, report))
    original_time = clock[0]
    clock[0] += REPORT_TTL + 100000
    Service(svc.state, api[4])
    clock[0] = original_time
    restarted = Service(svc.state, api[4])
    with pytest.raises(Problem) as caught:
        restarted.mutate("test-a", "client", "/v1/jobs", signed)
    assert caught.value.code == "EXPIRED_OR_FUTURE"
    with restarted.connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone() == (0,)


def test_current_openapi_matches_actual_lifecycle_fields(api):
    from pathlib import Path

    schemas = json.loads(
        (Path(__file__).resolve().parents[1] / "docs/PRIVATE-SERVICE-OPENAPI-v1.json").read_text()
    )["components"]["schemas"]
    _, job, report = complete(api)
    status = api[1]("client", "GET", job["status_url"])[1]
    for name, value in (("Status", status), ("ReportResponse", report)):
        assert set(value) == set(schemas[name]["properties"])
        assert set(schemas[name]["required"]) <= set(value)


def test_expiry_during_report_materialization_blocks_response(controlled, monkeypatch):
    api, clock = controlled
    svc = api[0]
    _, job, _ = complete(api)
    clock[0] += REPORT_TTL - 1
    unseal = svc.unseal

    def delayed(*args):
        value = unseal(*args)
        clock[0] += 2
        return value

    monkeypatch.setattr(svc, "unseal", delayed)
    with pytest.raises(Problem) as caught:
        svc.read(tenant="test-a", jid=job["job_id"], report=True)
    assert caught.value.code == "REPORT_GONE"
    assert svc.read("test-a", job["job_id"])[1]["cleanup_confirmed"]


def test_malformed_http_does_not_echo_secret_or_write_error_logs(api, capfd):
    port = int(api[6].rsplit(":", 1)[1])
    marker = b"SYNTHETIC-SECRET-IN-MALFORMED-REQUEST"
    with socket.create_connection(("127.0.0.1", port), timeout=5) as sock:
        sock.sendall(b"GET /" + marker + b" HTTP/9.9\r\nHost: invalid\r\n\r\n")
        raw = b""
        while chunk := sock.recv(8192):
            raw += chunk
    assert marker not in raw
    assert capfd.readouterr().err == ""


def test_waiting_cleanup_uses_actual_request_expiry(controlled):
    api, clock = controlled
    signed = api[2](
        "sender",
        "/v1/jobs",
        {"scenario": "a4-write16-v1", "receiver_kid": "receiver"},
        issued_ms=clock[0],
        expires_ms=clock[0] + 100,
    )
    code, job = api[1]("client", "POST", "/v1/jobs", signed)
    assert code == 202
    clock[0] += 100
    value = api[1]("client", "GET", job["report_url"])[1]
    assert value["report"]["body"]["reason"] == "REQUEST_EXPIRED"
    assert value["inputs_cleanup_completed_at"] == iso(clock[0])


def test_positive_archived_evidence_http_report_then_receipt(api):
    # Regression on preserved synthetic evidence, explicitly no fresh VM effect.
    jid, row, payload = contracts.actual_evidence.__wrapped__(api)
    svc = api[0]
    with svc.connection() as db:
        db.execute(
            "INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                "test-a",
                jid,
                row[0],
                row[1],
                svc.seal("test-a", jid, "request", json.loads(row[2])),
                svc.seal("test-a", jid, "acceptance", json.loads(row[3])),
                "running",
                now_ms(),
                None,
                now_ms(),
            ),
        )
    path = f"/v1/jobs/{jid}/evidence"
    code, _result = api[1]("runner", "POST", path, api[2]("runner", path, payload))
    assert code == 201
    code, value = api[1]("client", "GET", f"/v1/jobs/{jid}/report")
    assert code == 200 and value["report"]["body"]["classification"] == "BELEGT"
    assert verify(api[4]["report_public_key"], value["report"])
    assert value["inputs_cleanup_completed_at"]
    code, status = api[1]("client", "POST", *receipt(api, {"job_id": jid}, value))
    assert code == 200 and status["cleanup_confirmed"]
    assert api[1]("client", "GET", f"/v1/jobs/{jid}/report")[0] == 410


def test_cleanup_completion_timestamp_is_measured_after_filesystem_work(controlled, monkeypatch):
    api, clock = controlled
    svc = api[0]
    _, job, report = complete(api)
    before = clock[0]
    clean = svc._clean

    def delayed(*args):
        clean(*args)
        clock[0] += 5000

    monkeypatch.setattr(svc, "_clean", delayed)
    result = api[1]("client", "POST", *receipt(api, job, report))[1]
    assert result["received_at"] == iso(before)
    assert result["cleanup_completed_at"] == iso(before + 5000)
    assert result["cleanup_confirmed"]
