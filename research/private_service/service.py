"""Single-node private synthetic service. Resource ACLs never grant action rights."""

import json
import secrets
import sqlite3
from pathlib import Path

from research.hosted_qualification.ledger import Ledger
from research.private_service.protocol import (
    AUDIENCE,
    HEX,
    SCHEMA,
    Problem,
    digest,
    fields,
    fresh,
    identifier,
    require,
    restricted,
    verify,
)
from research.private_service.retention import (
    MAX_REQUEST,
    RETRY_CLOCK,
    Retention,
    guarded,
    private_dir,
)

LABELS = {
    "awaiting_acceptance": "Annahme ausstehend",
    "queued": "Wartet auf Testlauf",
    "running": "Testlauf wird beobachtet",
    "completed": "Pruefbericht verfuegbar",
    "unknown": "Testlauf unklar - keine automatische Wiederholung",
}
MAX_REQUEST_RECORDS = 8192
MAX_JOB_RECORDS = 4096
MAX_KEY_RECORDS = 4096  # IDs never reused; retire identity instead of pruning keys.


class Service(Retention, Ledger):
    def __init__(self, state, config, report_signer=None):
        require(not Path(state).is_symlink(), 503, "UNSAFE_STORAGE")
        self.state = Path(state).absolute()
        private_dir(self.state)
        self.database = str(self.state / "service.sqlite")
        for suffix in ("", "-wal", "-shm", "-journal"):
            require(not Path(self.database + suffix).is_symlink(), 503, "UNSAFE_STORAGE")
        # Historical states must be preserved. No implicit plaintext migration or TTL.
        with self.exclusive():
            if Path(self.database).exists():
                with sqlite3.connect(self.database) as old:
                    tables = {
                        r[0]
                        for r in old.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    }
                    require(
                        "jobs" not in tables or "lifecycle" in tables, 503, "LEGACY_STATE_PRESERVED"
                    )
                    if "service_meta" in tables:
                        require(
                            old.execute("SELECT version FROM service_meta").fetchall() == [(2,)],
                            503,
                            "SCHEMA_UNSUPPORTED",
                        )
            from research.private_service.boundary import ReportSigner
            from research.private_service.configuration import api_configuration

            self.report_signer = report_signer or ReportSigner(config["report_private_key"])
            # Only API control data survives initialization. Offline root/client/
            # runner private keys and bearer values do not belong in API config.
            self.config = api_configuration(config)
            require(
                self.config["report_public_key"] not in self.config["root_pins"].values(),
                503,
                "KEY_PURPOSE_MISMATCH",
            )
            self._initialize(self.config)
            self.sweep()

    def _initialize(self, config):
        super().__init__(self.state / "service.sqlite", config["root_pins"])
        with self.connection() as db:
            db.executescript("""
              CREATE TABLE IF NOT EXISTS service_meta (version INTEGER NOT NULL);
              INSERT INTO service_meta SELECT 2 WHERE NOT EXISTS (SELECT 1 FROM service_meta);
              CREATE TABLE IF NOT EXISTS service_keys (
                tenant TEXT, kid TEXT, public TEXT NOT NULL, role TEXT NOT NULL,
                issued INTEGER NOT NULL, expires INTEGER NOT NULL, revoked INTEGER,
                PRIMARY KEY(tenant,kid));
              CREATE TABLE IF NOT EXISTS challenges (
                tenant TEXT, id TEXT, kid TEXT, public TEXT, expires INTEGER, used INTEGER,
                PRIMARY KEY(tenant,id));
              CREATE TABLE IF NOT EXISTS requests (
                tenant TEXT, idem TEXT, nonce TEXT, digest TEXT NOT NULL,
                status INTEGER NOT NULL, response TEXT NOT NULL, stamp INTEGER NOT NULL,
                PRIMARY KEY(tenant,idem), UNIQUE(tenant,nonce));
              CREATE TABLE IF NOT EXISTS jobs (
                tenant TEXT, id TEXT, sender TEXT, receiver TEXT, request TEXT,
                acceptance TEXT, state TEXT, dispatched INTEGER, report TEXT,
                created INTEGER NOT NULL, PRIMARY KEY(tenant,id));
              CREATE TABLE IF NOT EXISTS dispatch_pins (
                tenant TEXT, job_id TEXT, context TEXT, PRIMARY KEY(tenant,job_id));
              CREATE TABLE IF NOT EXISTS audit (
                tenant TEXT, kid TEXT, event TEXT, stamp INTEGER);
            """)
            self.setup_retention(db)
            require(
                db.execute("SELECT version FROM service_meta").fetchall() == [(2,)],
                503,
                "SCHEMA_UNSUPPORTED",
            )

    def authenticate(self, token):
        entry = self.credentials(token)
        return entry["tenant"], entry["role"]

    def credentials(self, token):
        import hashlib
        import hmac

        require(type(token) is str and token.isascii(), 401, "AUTH_REQUIRED")

        for entry in self.config["tokens"]:
            if hmac.compare_digest(hashlib.sha256(token.encode()).hexdigest(), entry["sha256"]):
                return entry
        raise Problem(401, "AUTH_REQUIRED")

    def authorize_signer(self, token, kid):
        entry = self.credentials(token)
        require("*" in entry["subjects"] or kid in entry["subjects"], 403, "OBJECT_FORBIDDEN")

    def authorize_read(self, token, jid):
        entry = self.credentials(token)
        with self.connection() as db:
            row = db.execute(
                "SELECT sender,receiver FROM jobs WHERE tenant=? AND id=?", (entry["tenant"], jid)
            ).fetchone()
        require(
            row is not None
            and ("*" in entry["subjects"] or any(k in entry["subjects"] for k in row)),
            404,
            "NOT_FOUND",
        )

    def request_capacity(self, db):
        require(
            db.execute("SELECT count(*) FROM requests").fetchone()[0] < MAX_REQUEST_RECORDS,
            429,
            "REQUEST_CAPACITY",
        )

    @guarded
    def challenge(self, tenant, role, data):
        restricted(data)
        require(role == "admin", 403, "ROLE_FORBIDDEN")
        fields(data, "schema kid public_key idempotency_key nonce issued_ms expires_ms")
        require(data["schema"] == SCHEMA)
        identifier(data["kid"])
        identifier(data["idempotency_key"])
        require(type(data["nonce"]) is str and HEX.fullmatch(data["nonce"]) is not None)
        fresh(data, self.time_ms())
        require(type(data["public_key"]) is str and len(data["public_key"]) == 44)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            fresh(data, self.time_ms())
            prior = db.execute(
                "SELECT digest,status,response FROM requests WHERE tenant=? AND idem=?",
                (tenant, data["idempotency_key"]),
            ).fetchone()
            if prior:
                require(prior[0] == digest(data), 409, "IDEMPOTENCY_CONFLICT")
                return prior[1], json.loads(prior[2])
            require(
                db.execute(
                    "SELECT 1 FROM requests WHERE tenant=? AND nonce=?", (tenant, data["nonce"])
                ).fetchone()
                is None,
                409,
                "REPLAY",
            )
            self.request_capacity(db)
            require(
                db.execute(
                    "SELECT count(*) FROM challenges WHERE tenant=? AND expires>?",
                    (tenant, self.time_ms()),
                ).fetchone()[0]
                < 32,
                429,
                "CHALLENGE_LIMIT",
            )
            cid = secrets.token_hex(32)
            expires = self.time_ms() + 60000
            db.execute(
                "INSERT INTO challenges VALUES (?,?,?,?,?,0)",
                (tenant, cid, data["kid"], data["public_key"], expires),
            )
            response = {
                "schema": SCHEMA,
                "domain": "AA-POP-v1",
                "tenant": tenant,
                "audience": AUDIENCE,
                "challenge_id": cid,
                "kid": data["kid"],
                "public_key": data["public_key"],
                "expires_ms": expires,
            }
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?,?,?)",
                (
                    tenant,
                    data["idempotency_key"],
                    data["nonce"],
                    digest(data),
                    201,
                    json.dumps(response),
                    self.time_ms(),
                ),
            )
            db.execute(
                "INSERT INTO request_deadlines VALUES (?,?,?)",
                (tenant, data["idempotency_key"], data["expires_ms"] + RETRY_CLOCK),
            )
            db.commit()
        return 201, response

    def key(self, db, tenant, kid, now):
        row = db.execute(
            "SELECT public,role,issued,expires,revoked FROM service_keys WHERE tenant=? AND kid=?",
            (tenant, kid),
        ).fetchone()
        require(row is not None, 401, "KEY_UNKNOWN")
        require(row[4] is None, 403, "KEY_REVOKED")
        require(row[2] <= now < row[3], 410, "KEY_EXPIRED")
        return row

    @guarded
    def mutate(self, tenant, role, path, packet):
        restricted(packet)
        fields(packet, "body signature")
        body = packet["body"]
        fields(
            body,
            "schema domain tenant audience method path kid nonce idempotency_key issued_ms expires_ms payload",
        )
        for item in ("kid", "idempotency_key"):
            identifier(body[item])
        require(type(body["nonce"]) is str and HEX.fullmatch(body["nonce"]) is not None)
        require(body["tenant"] == tenant, 403, "TENANT_MISMATCH")
        require(
            body["schema"] == SCHEMA
            and body["domain"] == "AA-REQUEST-v1"
            and body["audience"] == AUDIENCE
            and body["method"] == "POST"
            and body["path"] == path,
            422,
            "TARGET_MISMATCH",
        )
        allowed = (
            ("admin",)
            if path in ("/v1/enrollments", "/v1/revocations")
            else (("runner",) if path.endswith("/evidence") else ("client", "admin"))
        )
        require(role in allowed, 403, "ROLE_FORBIDDEN")
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            now = self.time_ms()
            fresh(body, now)
            if path == "/v1/enrollments":
                require(role == "admin", 403, "ROLE_FORBIDDEN")
                payload = body["payload"]
                fields(payload, "certificate proof replaces")
                fields(payload["certificate"], "body signature")
                cert = payload["certificate"]["body"]
                fields(
                    cert, "schema domain tenant audience kid public_key role issued_ms expires_ms"
                )
                require(
                    cert["schema"] == SCHEMA
                    and cert["domain"] == "AA-ENROLL-v1"
                    and cert["tenant"] == tenant
                    and cert["audience"] == AUDIENCE
                    and cert["kid"] == body["kid"]
                    and cert["role"] in ("actor", "runner")
                )
                require(
                    tenant in self.root_pins
                    and verify(self.root_pins[tenant], payload["certificate"]),
                    401,
                    "TRUST_PIN_INVALID",
                )
                fresh(cert, now, 86400000)
                public = cert["public_key"]
                require(
                    public != self.config["report_public_key"]
                    and public not in self.root_pins.values(),
                    422,
                    "KEY_PURPOSE_MISMATCH",
                )
                from protocol import unb64

                try:
                    require(len(unb64(public)) == 32)
                except (ValueError, TypeError) as error:
                    raise Problem(422, "INVALID_PUBLIC_KEY") from error
            else:
                require(role in ("client", "admin", "runner"), 403, "ROLE_FORBIDDEN")
                key = self.key(db, tenant, body["kid"], now)
                public = key[0]
                require(body["issued_ms"] >= key[2], 410, "KEY_EXPIRED")
            require(verify(public, packet), 401, "SIGNATURE_INVALID")
            fresh(body, self.time_ms())
            pd = digest(packet)
            previous = db.execute(
                "SELECT digest,status,response FROM requests WHERE tenant=? AND idem=?",
                (tenant, body["idempotency_key"]),
            ).fetchone()
            if previous:
                require(previous[0] == pd, 409, "IDEMPOTENCY_CONFLICT")
                db.commit()
                return previous[1], json.loads(previous[2])
            require(
                db.execute(
                    "SELECT 1 FROM requests WHERE tenant=? AND nonce=?", (tenant, body["nonce"])
                ).fetchone()
                is None,
                409,
                "REPLAY",
            )
            self.request_capacity(db)
            result = self._operation(db, tenant, role, path, packet, now)
            # Verification/signing can take time. Do not commit a request that
            # became stale while processing; no new replay record on rollback.
            fresh(body, self.time_ms())
            db.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?,?,?)",
                (
                    tenant,
                    body["idempotency_key"],
                    body["nonce"],
                    pd,
                    result[0],
                    json.dumps(result[1]),
                    now,
                ),
            )
            epoch_end = cert["expires_ms"] if path == "/v1/enrollments" else key[3]
            db.execute(
                "INSERT INTO request_deadlines VALUES (?,?,?)",
                (
                    tenant,
                    body["idempotency_key"],
                    max(epoch_end, body["expires_ms"]) + MAX_REQUEST + RETRY_CLOCK,
                ),
            )
            db.commit()
            return result

    def _operation(self, db, tenant, role, path, packet, now):
        body, payload = packet["body"], packet["body"]["payload"]
        if path == "/v1/enrollments":
            require(
                db.execute("SELECT count(*) FROM service_keys").fetchone()[0] < MAX_KEY_RECORDS,
                429,
                "KEY_CAPACITY",
            )
            cert = payload["certificate"]["body"]
            fields(payload["proof"], "body signature")
            proof = payload["proof"]["body"]
            fields(proof, "schema domain tenant audience challenge_id kid public_key expires_ms")
            require(
                proof["schema"] == SCHEMA
                and proof["domain"] == "AA-POP-v1"
                and proof["tenant"] == tenant
                and proof["audience"] == AUDIENCE
                and proof["kid"] == cert["kid"]
                and proof["public_key"] == cert["public_key"]
            )
            identifier(proof["challenge_id"])
            row = db.execute(
                "SELECT kid,public,expires,used FROM challenges WHERE tenant=? AND id=?",
                (tenant, proof["challenge_id"]),
            ).fetchone()
            require(
                row is not None
                and row[:3] == (cert["kid"], cert["public_key"], proof["expires_ms"])
                and row[2] > now
                and row[3] == 0,
                409,
                "CHALLENGE_USED_OR_EXPIRED",
            )
            require(verify(cert["public_key"], payload["proof"]), 401, "POP_INVALID")
            require(
                db.execute(
                    "SELECT 1 FROM service_keys WHERE tenant=? AND kid=?", (tenant, cert["kid"])
                ).fetchone()
                is None,
                409,
                "KEY_ID_REUSED",
            )
            old = payload["replaces"]
            if old is not None:
                identifier(old)
                oldkey = self.key(db, tenant, old, now)
                require(oldkey[1] == cert["role"], 422, "ROTATION_ROLE_MISMATCH")
                self._revoke(db, tenant, old, now, "rotation")
            db.execute(
                "INSERT INTO service_keys VALUES (?,?,?,?,?,?,NULL)",
                (
                    tenant,
                    cert["kid"],
                    cert["public_key"],
                    cert["role"],
                    cert["issued_ms"],
                    cert["expires_ms"],
                ),
            )
            db.execute(
                "UPDATE challenges SET used=1 WHERE tenant=? AND id=?",
                (tenant, proof["challenge_id"]),
            )
            db.execute("INSERT INTO audit VALUES (?,?,?,?)", (tenant, cert["kid"], "enroll", now))
            return 201, {
                "schema": SCHEMA,
                "kid": cert["kid"],
                "state": "registered",
                "grants_rights": False,
            }
        if path == "/v1/revocations":
            require(role == "admin", 403, "ROLE_FORBIDDEN")
            fields(payload, "kid")
            identifier(payload["kid"])
            self.key(db, tenant, payload["kid"], now)
            self._revoke(db, tenant, payload["kid"], now, "revoke")
            return 200, {"schema": SCHEMA, "kid": payload["kid"], "state": "revoked"}
        if path == "/v1/jobs":
            require(
                db.execute("SELECT count(*) FROM jobs").fetchone()[0] < MAX_JOB_RECORDS,
                429,
                "JOB_CAPACITY",
            )
            require(role in ("client", "admin"), 403, "ROLE_FORBIDDEN")
            require(self.key(db, tenant, body["kid"], now)[1] == "actor", 403, "ROLE_FORBIDDEN")
            fields(payload, "scenario receiver_kid")
            require(payload["scenario"] == "a4-write16-v1", 422, "SCENARIO_UNSUPPORTED")
            identifier(payload["receiver_kid"])
            require(payload["receiver_kid"] != body["kid"])
            require(
                self.key(db, tenant, payload["receiver_kid"], now)[1] == "actor",
                403,
                "ROLE_FORBIDDEN",
            )
            require(
                db.execute(
                    "SELECT count(*) FROM jobs WHERE state IN ('awaiting_acceptance','queued','running')"
                ).fetchone()[0]
                < 16,
                429,
                "QUEUE_FULL",
            )
            jid = secrets.token_hex(16)
            db.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,NULL,'awaiting_acceptance',NULL,NULL,?)",
                (
                    tenant,
                    jid,
                    body["kid"],
                    payload["receiver_kid"],
                    self.seal(tenant, jid, "request", packet),
                    now,
                ),
            )
            epoch_end = max(
                self.key(db, tenant, k, now)[3] for k in (body["kid"], payload["receiver_kid"])
            )
            db.execute(
                "INSERT INTO lifecycle (tenant,job_id,retain_until,input_deadline) VALUES (?,?,?,?)",
                (tenant, jid, epoch_end + MAX_REQUEST + RETRY_CLOCK, body["expires_ms"]),
            )
            return 202, {
                "schema": SCHEMA,
                "job_id": jid,
                "job_sha256": digest(packet),
                "state": "awaiting_acceptance",
                "status_url": f"/v1/jobs/{jid}",
                "report_url": f"/v1/jobs/{jid}/report",
                "grants_rights": False,
            }
        parts = path.split("/")
        require(len(parts) == 5 and parts[1:3] == ["v1", "jobs"], 404, "NOT_FOUND")
        jid, operation = parts[3:]
        identifier(jid)
        row = db.execute(
            "SELECT sender,receiver,request,acceptance,state,dispatched,report,created FROM jobs WHERE tenant=? AND id=?",
            (tenant, jid),
        ).fetchone()
        require(row is not None, 404, "NOT_FOUND")
        if operation == "receipts":
            require(role in ("client", "admin"), 403, "ROLE_FORBIDDEN")
            return self.receipt(db, tenant, jid, body["kid"], payload, now)
        if operation == "cancellations":
            fields(payload, "job_id")
            require(payload["job_id"] == jid)
            require(role in ("client", "admin") and body["kid"] in row[:2], 403, "OBJECT_FORBIDDEN")
            require(row[4] in ("awaiting_acceptance", "queued", "running"), 409, "STATE_CONFLICT")
            self._unknown(db, tenant, jid, "CANCELLED_NO_RERUN")
            return 200, {
                "schema": SCHEMA,
                "job_id": jid,
                "state": "unknown",
                **self.lifecycle_status(db, tenant, jid),
            }
        require(row[2] is not None, 409, "STATE_CONFLICT")
        original = self.unseal(tenant, jid, "request", row[2])
        if operation == "acceptances":
            require(role in ("client", "admin") and body["kid"] == row[1], 403, "OBJECT_FORBIDDEN")
            fields(payload, "job_id job_sha256")
            require(
                payload == {"job_id": jid, "job_sha256": digest(original)},
                422,
                "DELEGATION_MISMATCH",
            )
            self.key(db, tenant, row[0], now)
            fresh(original["body"], now)
            require(row[4] == "awaiting_acceptance", 409, "STATE_CONFLICT")
            db.execute(
                "UPDATE jobs SET acceptance=?,state='queued' WHERE tenant=? AND id=?",
                (self.seal(tenant, jid, "acceptance", packet), tenant, jid),
            )
            db.execute(
                "UPDATE lifecycle SET input_deadline=min(input_deadline,?) WHERE tenant=? AND job_id=?",
                (body["expires_ms"], tenant, jid),
            )
            return 202, {"schema": SCHEMA, "job_id": jid, "state": "queued", "grants_rights": False}
        if operation == "evidence":
            require(
                role == "runner" and self.key(db, tenant, body["kid"], now)[1] == "runner",
                403,
                "SOURCE_FORBIDDEN",
            )
            require(row[4] == "running", 409, "STATE_CONFLICT")
            require(type(row[5]) is int and now < row[5] + 180000, 410, "EVIDENCE_WINDOW_EXPIRED")
            plain_row = (
                *row[:2],
                json.dumps(original),
                json.dumps(self.unseal(tenant, jid, "acceptance", row[3])),
                *row[4:],
            )
            report = self.verify_evidence(tenant, jid, plain_row, payload, now, body["kid"])
            for kid in row[:2]:
                self.key(db, tenant, kid, now)
            signed_report = self.finish(db, tenant, jid, report, "completed", self.time_ms())
            return 201, {
                "schema": SCHEMA,
                "job_id": jid,
                "state": "completed",
                "report_sha256": digest(signed_report),
                **self.lifecycle_status(db, tenant, jid),
            }
        raise Problem(404, "NOT_FOUND")

    def _revoke(self, db, tenant, kid, now, event):
        db.execute("UPDATE service_keys SET revoked=? WHERE tenant=? AND kid=?", (now, tenant, kid))
        db.execute("INSERT INTO audit VALUES (?,?,?,?)", (tenant, kid, event, now))
        affected = db.execute(
            "SELECT id,state FROM jobs WHERE tenant=? AND (sender=? OR receiver=?) "
            "AND state IN ('awaiting_acceptance','queued','running')",
            (tenant, kid, kid),
        ).fetchall()
        if tenant == self.config["runner_tenant"] and kid == self.config["runner_kid"]:
            affected = list(
                set(affected)
                | set(
                    db.execute(
                        "SELECT id,state FROM jobs WHERE tenant=? AND state IN ('queued','running')",
                        (tenant,),
                    ).fetchall()
                )
            )
        for jid, state in affected:
            self._unknown(
                db,
                tenant,
                jid,
                "KEY_REVOKED_DURING_RUN" if state == "running" else "KEY_REVOKED_BEFORE_RUN",
            )

    def _unknown(self, db, tenant, jid, reason):
        report = {
            "schema": "aa-report-v1",
            "domain": "AA-REPORT-v1",
            "audience": AUDIENCE,
            "signing_kid": "local-report-v1",
            "tenant": tenant,
            "job_id": jid,
            "classification": "UNBEKANNT",
            "reason": reason,
            "sources": [],
            "verifier_version": "aa-private-verifier-v1",
            "trust_catalog_version": self.config["trust_version"],
            "issued_ms": self.time_ms(),
            "scope": "controlled-a4-write16",
            "provider_model_session": "UNBEKANNT",
            "uncertainties": ["No automatic rerun", "Action may have occurred"],
            "grants_rights": False,
        }
        self.finish(db, tenant, jid, report, "unknown", self.time_ms())

    @guarded
    def read(self, tenant, jid, report=False):
        identifier(jid)
        with self.connection() as db:
            row = db.execute(
                "SELECT state,report,sender,receiver FROM jobs WHERE tenant=? AND id=?",
                (tenant, jid),
            ).fetchone()
            require(row is not None, 404, "NOT_FOUND")
            life = self.lifecycle_status(db, tenant, jid)
            keys = db.execute(
                "SELECT kid,revoked,expires FROM service_keys WHERE tenant=? AND kid IN (?,?)",
                (tenant, row[2], row[3]),
            ).fetchall()
        if report:
            require(life["access_state"] != "blocked", 410, "REPORT_GONE")
            require(row[1] is not None, 409, "REPORT_PENDING")
            return 200, {
                "schema": SCHEMA,
                "report": self.unseal(tenant, jid, "report", row[1]),
                **life,
                "current_key_status": {
                    k: "revoked"
                    if stamp is not None
                    else "expired"
                    if self.time_ms() >= expires
                    else "active"
                    for k, stamp, expires in keys
                },
            }
        return 200, {
            "schema": SCHEMA,
            "job_id": jid,
            "state": row[0],
            "label": "Berichtszugriff gesperrt; Bereinigung " + life["cleanup_state"]
            if life["access_state"] == "blocked"
            else LABELS[row[0]],
            "report_available": row[1] is not None,
            "grants_rights": False,
            **life,
        }

    @guarded
    def claim(self):
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self.key(db, self.config["runner_tenant"], self.config["runner_kid"], self.time_ms())
            row = db.execute(
                "SELECT tenant,id,sender,receiver,request,acceptance FROM jobs WHERE state='queued' AND tenant=? ORDER BY created LIMIT 1",
                (self.config["runner_tenant"],),
            ).fetchone()
            if row is None:
                return None
            tenant, jid, sender, receiver, original, acceptance = row
            try:
                for kid in (sender, receiver):
                    self.key(db, tenant, kid, self.time_ms())
                original = self.unseal(tenant, jid, "request", original)
                acceptance = self.unseal(tenant, jid, "acceptance", acceptance)
                for envelope in (original, acceptance):
                    fresh(envelope["body"], self.time_ms())
            except Problem as error:
                self._unknown(db, tenant, jid, error.code)
                db.commit()
                return None
            db.execute(
                "UPDATE jobs SET state='running',dispatched=? WHERE tenant=? AND id=?",
                (self.time_ms(), tenant, jid),
            )
            db.commit()
            return {
                "tenant": tenant,
                "job_id": jid,
                "job_sha256": digest(original),
                "acceptance_sha256": digest(acceptance),
            }

    @guarded
    def recover(self):
        # Caller MUST hold the host-wide runner lock. Never called by API startup.
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            for tenant, jid in db.execute(
                "SELECT tenant,id FROM jobs WHERE state='running'"
            ).fetchall():
                self._unknown(db, tenant, jid, "WORKER_INTERRUPTED")
            db.commit()

    def verify_evidence(self, tenant, jid, row, payload, now, source_kid):
        from research.private_service.verifier import verify_package

        return verify_package(self, tenant, jid, row, payload, now, source_kid)
