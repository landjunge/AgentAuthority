"""Offline service prerequisites. No agent/model/kernel execution in these tests."""

import importlib
import multiprocessing
import os
import secrets
import sqlite3

import pytest

from research.hosted_qualification.ledger import Conflict, Invalid, Ledger

crypto = importlib.import_module("host_crypto")
create_ca, sign = crypto.create_ca, crypto.sign
NOW = 1_800_000_000_000


@pytest.fixture
def setup(tmp_path):
    private = []

    def new_key(name):
        directory = tmp_path / name
        key, public = create_ca(directory)
        private.append(key)
        return key, public

    root_a, pin_a = new_key("root-a")
    root_b, pin_b = new_key("root-b")
    agent, public = new_key("agent")
    database = tmp_path / "ledger.sqlite"
    pins = {"A": pin_a, "B": pin_b}
    ledger = Ledger(database, pins)

    def certificate(tenant="A", kid="k1", public_key=public, root=root_a, **changes):
        return sign(
            root,
            {
                "domain": "AA-QUAL-ENROLL-v1",
                "tenant": tenant,
                "kid": kid,
                "public_key": public_key,
                "issued_ms": NOW - 1000,
                "expires_ms": NOW + 86400000 - 1000,
                **changes,
            },
        )

    ledger.enroll("A", certificate(), now=NOW)

    def packet(**changes):
        body = {
            "domain": "AA-QUAL-INTAKE-v1",
            "tenant": "A",
            "kid": "k1",
            "nonce": secrets.token_hex(32),
            "idempotency_key": "event1",
            "evidence_sha256": "a" * 64,
            "issued_ms": NOW,
            "expires_ms": NOW + 60000,
        }
        body.update(changes)
        return sign(agent, body)

    yield ledger, packet, certificate, new_key, pins, database, root_b
    # Exact own synthetic private files, including after failed assertions.
    for key in private:
        key.unlink()
        key.parent.rmdir()


def worker(database, pins, packet, ready, go, result, crash=None):
    ledger = Ledger(database, pins)
    ready.put(True)
    go.wait(15)

    def checkpoint(point):
        if point == crash:
            os._exit(37)

    try:
        result.put(ledger.observe("A", packet, now=NOW, checkpoint=checkpoint)["disposition"])
    except (Invalid, Conflict, sqlite3.Error) as error:
        result.put(type(error).__name__)


def processes(database, pins, packet, count, crash=None):
    ctx = multiprocessing.get_context("spawn")
    ready, result, go = ctx.Queue(), ctx.Queue(), ctx.Event()
    children = [
        ctx.Process(target=worker, args=(database, pins, packet, ready, go, result, crash))
        for _ in range(count)
    ]
    try:
        for child in children:
            child.start()
        for _ in children:
            assert ready.get(timeout=20)
        go.set()
        values = [] if crash else [result.get(timeout=30) for _ in children]
        for child in children:
            child.join(20)
            assert child.exitcode == (37 if crash else 0)
        return values
    finally:
        for child in children:
            if child.is_alive():
                child.terminate()
                child.join(5)
        ready.close()
        result.close()


def test_parallel_workers_and_restart_record_one_finding(setup):
    _ledger, packet, _, _, pins, database, _ = setup
    p = packet()
    values = processes(database, pins, p, 8)
    assert values.count("recorded") == 1
    assert values.count("existing") == 7
    restarted = Ledger(database, pins)
    assert restarted.observe("A", p, now=NOW)["disposition"] == "existing"
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM findings").fetchone()[0] == 1
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


@pytest.mark.parametrize(
    "crash,expected", [("before_commit", "recorded"), ("after_commit", "existing")]
)
def test_real_process_exit_at_commit_boundary(setup, crash, expected):
    ledger, packet, _, _, pins, database, _ = setup
    p = packet()
    processes(database, pins, p, 1, crash)
    assert Ledger(database, pins).observe("A", p, now=NOW)["disposition"] == expected
    assert ledger.read("A", "event1")["independent_effect"] == "UNBEKANNT"


def test_nonce_replay_and_idempotency_conflict_survive_reopen(setup):
    ledger, packet, _, _, pins, database, _ = setup
    p = packet()
    ledger.observe("A", p, now=NOW)
    restarted = Ledger(database, pins)
    with pytest.raises(Conflict, match="nonce"):
        restarted.observe(
            "A", packet(nonce=p["body"]["nonce"], idempotency_key="different"), now=NOW
        )
    with pytest.raises(Conflict, match="idempotency"):
        restarted.observe("A", packet(evidence_sha256="b" * 64), now=NOW)
    assert restarted.read("A", "event1")["evidence_sha256"] == "a" * 64


def test_upload_key_cannot_enroll_itself_or_cross_tenant(setup):
    ledger, packet, certificate, _, _, _, root_b = setup
    with pytest.raises(Invalid, match="unpinned"):
        ledger.enroll("A", certificate(kid="evil", root=root_b), now=NOW)
    with pytest.raises(Invalid, match="context"):
        ledger.observe("B", packet(), now=NOW)
    with pytest.raises(Invalid, match="unregistered"):
        ledger.observe("B", packet(tenant="B"), now=NOW)
    ledger.observe("A", packet(), now=NOW)
    assert ledger.read("B", "event1") is None


def test_rotation_revocation_and_old_enrollment_replay(setup):
    ledger, packet, certificate, new_key, pins, database, _ = setup
    old_packet = packet()
    new_private, new_public = new_key("rotated")
    ledger.enroll("A", certificate(kid="k2", public_key=new_public), old_kid="k1", now=NOW)
    with pytest.raises(Invalid, match="revoked"):
        Ledger(database, pins).observe("A", old_packet, now=NOW)
    with pytest.raises(Conflict):
        ledger.enroll("A", certificate(), now=NOW)
    body = packet(kid="k2")["body"]
    p = sign(new_private, body)
    assert ledger.observe("A", p, now=NOW)["disposition"] == "recorded"
    ledger.revoke("A", "k2")
    with pytest.raises(Invalid, match="revoked"):
        Ledger(database, pins).observe("A", p, now=NOW)


def test_failed_rotation_rolls_back_new_enrollment(setup):
    ledger, packet, certificate, _, _, _, _ = setup
    with pytest.raises(Invalid, match="predecessor"):
        ledger.enroll("A", certificate(kid="k2"), old_kid="missing", now=NOW)
    with pytest.raises(Invalid, match="unregistered"):
        ledger.observe("A", packet(kid="k2"), now=NOW)


@pytest.mark.parametrize(
    "changes",
    [
        {"domain": "A4-DELEGATION-v1"},
        {"issued_ms": NOW + 1},
        {"expires_ms": NOW},
        {"expires_ms": NOW + 60001},
        {"issued_ms": True},
        {"nonce": "bad"},
        {"evidence_sha256": "bad"},
        {"prompt": "SYNTHETIC-MUST-NOT-BE-STORED"},
    ],
)
def test_invalid_signed_context_does_not_consume_nonce(setup, changes):
    ledger, packet, *_ = setup
    nonce = "c" * 64
    invalid = {"nonce": nonce, **changes}
    with pytest.raises(Invalid):
        ledger.observe("A", packet(**invalid), now=NOW)
    assert ledger.observe("A", packet(nonce=nonce), now=NOW)["disposition"] == "recorded"


def test_bad_signature_does_not_consume_valid_packet(setup):
    ledger, packet, *_ = setup
    p = packet()
    p["body"]["evidence_sha256"] = "b" * 64
    with pytest.raises(Invalid, match="signature"):
        ledger.observe("A", p, now=NOW)
    p["body"]["evidence_sha256"] = "a" * 64
    assert ledger.observe("A", p, now=NOW)["disposition"] == "recorded"


def test_same_identifiers_in_distinct_tenants_do_not_share_findings(setup):
    ledger, packet, certificate, _, _, _, root_b = setup
    ledger.enroll("B", certificate(tenant="B", root=root_b), now=NOW)
    pa = packet(nonce="d" * 64)
    pb = packet(tenant="B", nonce="d" * 64, evidence_sha256="b" * 64)
    ledger.observe("A", pa, now=NOW)
    ledger.observe("B", pb, now=NOW)
    assert ledger.read("A", "event1")["evidence_sha256"] == "a" * 64
    assert ledger.read("B", "event1")["evidence_sha256"] == "b" * 64


def test_report_never_promotes_signed_digest_to_independent_effect(setup):
    ledger, packet, *_ = setup
    report = ledger.observe("A", packet(), now=NOW)["report"]
    assert report["signature_under_enrollment"] is True
    assert report["independent_effect"] == report["provider_model_session"] == "UNBEKANNT"
    assert set(report) == {
        "schema",
        "tenant",
        "id",
        "evidence_sha256",
        "signature_under_enrollment",
        "independent_effect",
        "provider_model_session",
    }


def test_logical_deletion_does_not_recreate_report_or_delete_other_tenant(setup):
    ledger, packet, _, _, pins, database, _ = setup
    p = packet()
    ledger.observe("A", p, now=NOW)
    ledger.erase_report("B", "event1")
    assert ledger.read("A", "event1") is not None
    ledger.erase_report("A", "event1")
    restarted = Ledger(database, pins)
    assert restarted.read("A", "event1") is None
    assert restarted.observe("A", p, now=NOW) == {"disposition": "deleted", "report": None}
    with sqlite3.connect(database) as db:
        assert db.execute("SELECT count(*) FROM findings WHERE report IS NULL").fetchone()[0] == 1


@pytest.mark.parametrize(
    "change",
    [
        {"issued_ms": NOW + 1},
        {"expires_ms": NOW},
        {"domain": "WRONG"},
    ],
)
def test_enrollment_time_and_domain_are_checked_even_with_valid_root_signature(setup, change):
    ledger, _, certificate, _, _, _, _ = setup
    original = certificate(kid="bad", **change)
    with pytest.raises(Invalid):
        ledger.enroll("A", original, now=NOW)
