"""Offline qualification of intake integrity, never an action/permission service.

No HTTP, caller authentication, sandbox, production CA or generic A4 verifier.
Tenant context and root pins must come from the future authenticated control plane.
Uses existing Ed25519 canonicalization/OpenSSL; SQLite qualifies one local disk only.
"""

import hashlib
import json
import re
import sqlite3
import sys
import time
from contextlib import contextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify
from protocol import canonical

ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")


class Invalid(ValueError):
    pass


class Conflict(ValueError):
    pass


def check_fields(body, fields):
    if type(body) is not dict or set(body) != set(fields.split()):
        raise Invalid("unexpected fields")


def identifier(value):
    if type(value) is not str or not ID.fullmatch(value):
        raise Invalid("invalid identifier")


def window(body, now, maximum):
    if any(type(body.get(k)) is not int for k in ("issued_ms", "expires_ms")):
        raise Invalid("invalid time")
    if not body["issued_ms"] <= now < body["expires_ms"] <= body["issued_ms"] + maximum:
        raise Invalid("expired/future/oversized window")


class Ledger:
    def __init__(self, database, root_pins):
        self.database = str(database)
        self.root_pins = dict(root_pins)  # operator-configured, never taken from intake
        with self.connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS keys (
                    tenant TEXT, kid TEXT, public TEXT NOT NULL,
                    issued INTEGER NOT NULL, expires INTEGER NOT NULL,
                    active INTEGER NOT NULL, PRIMARY KEY(tenant,kid));
                CREATE TABLE IF NOT EXISTS findings (
                    tenant TEXT, idem TEXT, nonce TEXT NOT NULL,
                    packet_digest TEXT NOT NULL, report TEXT,
                    PRIMARY KEY(tenant,idem), UNIQUE(tenant,nonce));
            """)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.database, timeout=15, isolation_level=None)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            yield db
        finally:
            db.close()  # rolls back any unfinished transaction, including failures

    def enroll(self, tenant, certificate, old_kid=None, now=None):
        """Control-plane-only method; external upload has no route to this method."""
        live_clock = now is None
        now = int(time.time() * 1000) if live_clock else now
        identifier(tenant)
        check_fields(certificate, "body signature")
        body = certificate["body"]
        check_fields(body, "domain tenant kid public_key issued_ms expires_ms")
        identifier(body["kid"])
        if body["domain"] != "AA-QUAL-ENROLL-v1" or body["tenant"] != tenant:
            raise Invalid("enrollment context")
        if tenant not in self.root_pins or not verify(self.root_pins[tenant], certificate):
            raise Invalid("unpinned enrollment signer")
        window(body, now, 86_400_000)
        # verify() also checks key size; reject malformed enrolled public keys now.
        from protocol import unb64

        if len(unb64(body["public_key"])) != 32:
            raise Invalid("public key length")
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            window(body, int(time.time() * 1000) if live_clock else now, 86_400_000)
            try:
                db.execute(
                    "INSERT INTO keys VALUES (?,?,?,?,?,1)",
                    (
                        tenant,
                        body["kid"],
                        body["public_key"],
                        body["issued_ms"],
                        body["expires_ms"],
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise Conflict("key id never reused, including after revocation") from error
            if old_kid is not None:
                updated = db.execute(
                    "UPDATE keys SET active=0 WHERE tenant=? AND kid=? AND active=1",
                    (tenant, old_kid),
                )
                if updated.rowcount != 1:
                    raise Invalid("rotation predecessor unavailable")
            db.commit()

    def revoke(self, tenant, kid):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE keys SET active=0 WHERE tenant=? AND kid=?", (tenant, kid))
            db.commit()

    def observe(self, tenant, packet, now=None, checkpoint=lambda point: None):
        """Record only intake integrity. Never infer an effect from a signature.

        checkpoint is an offline crash-injection hook, absent from a network API.
        The signed digest names evidence bytes; this prototype does not ingest them.
        """
        live_clock = now is None
        now = int(time.time() * 1000) if live_clock else now
        identifier(tenant)
        check_fields(packet, "body signature")
        body = packet["body"]
        check_fields(
            body, "domain tenant kid nonce idempotency_key evidence_sha256 issued_ms expires_ms"
        )
        for key in ("kid", "idempotency_key"):
            identifier(body[key])
        if body["domain"] != "AA-QUAL-INTAKE-v1" or body["tenant"] != tenant:
            raise Invalid("intake context")
        for key in ("nonce", "evidence_sha256"):
            if type(body[key]) is not str or not HEX.fullmatch(body[key]):
                raise Invalid("digest/nonce format")
        window(body, now, 60_000)
        with self.connection() as db:
            row = db.execute(
                "SELECT public FROM keys WHERE tenant=? AND kid=?", (tenant, body["kid"])
            ).fetchone()
        if row is None or not verify(row[0], packet):
            raise Invalid("unregistered key or bad signature")
        packet_digest = hashlib.sha256(canonical(packet)).hexdigest()
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            now = int(time.time() * 1000) if live_clock else now
            window(body, now, 60_000)
            key = db.execute(
                "SELECT public,issued,expires,active FROM keys WHERE tenant=? AND kid=?",
                (tenant, body["kid"]),
            ).fetchone()
            # Recheck revocation and enrollment inside the same write transaction.
            if (
                key is None
                or key[0] != row[0]
                or not key[3]
                or not key[1] <= body["issued_ms"] <= now < key[2]
            ):
                raise Invalid("key revoked or outside enrollment")
            previous = db.execute(
                "SELECT packet_digest,report FROM findings WHERE tenant=? AND idem=?",
                (tenant, body["idempotency_key"]),
            ).fetchone()
            if previous:
                if previous[0] != packet_digest:
                    raise Conflict("idempotency key reused for different bytes")
                db.commit()
                return {
                    "disposition": "existing" if previous[1] else "deleted",
                    "report": json.loads(previous[1]) if previous[1] else None,
                }
            report = {
                "schema": "aa-intake-qualification-v1",
                "tenant": tenant,
                "id": body["idempotency_key"],
                "evidence_sha256": body["evidence_sha256"],
                "signature_under_enrollment": True,
                "independent_effect": "UNBEKANNT",
                "provider_model_session": "UNBEKANNT",
            }
            try:
                db.execute(
                    "INSERT INTO findings VALUES (?,?,?,?,?)",
                    (
                        tenant,
                        body["idempotency_key"],
                        body["nonce"],
                        packet_digest,
                        json.dumps(report, sort_keys=True),
                    ),
                )
            except sqlite3.IntegrityError as error:
                raise Conflict("nonce already recorded") from error
            checkpoint("before_commit")
            db.commit()
            checkpoint("after_commit")
            return {"disposition": "recorded", "report": report}

    def read(self, tenant, idem):
        with self.connection() as db:
            row = db.execute(
                "SELECT report FROM findings WHERE tenant=? AND idem=?", (tenant, idem)
            ).fetchone()
        return json.loads(row[0]) if row and row[0] else None

    def erase_report(self, tenant, idem):
        """Logical report deletion; keep replay tombstone. No physical erase claim.

        WAL, backups and restored copies require a separate retention mechanism.
        This prototype deliberately has no tombstone expiry/backup implementation.
        """
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("UPDATE findings SET report=NULL WHERE tenant=? AND idem=?", (tenant, idem))
            db.commit()
