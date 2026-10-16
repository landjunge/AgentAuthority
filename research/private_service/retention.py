"""Durable deadlines and retryable namespace cleanup for new private test states.

No migration/deletion of historical research states. Local disk/OS-account trust;
no claim of SSD/RAM erasure, backup erasure or rollback-safe key destruction.
"""

import base64
import fcntl
import functools
import hashlib
import inspect
import json
import os
import secrets
import sqlite3
import stat
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime

from research.private_service.crypto import crypt
from research.private_service.limits import LOCK_SECONDS, remaining
from research.private_service.protocol import Problem, digest, now_ms, require, verify

REPORT_TTL = 86_400_000
MAX_REQUEST = 60_000
RETRY_CLOCK = 5_000  # extra retention only; request validity has zero clock grace
LOCKS = {}
LOCKS_GUARD = threading.Lock()


def iso(stamp):
    return (
        datetime.fromtimestamp(stamp / 1000, UTC)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
        if stamp is not None
        else None
    )


def private_dir(path):
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise OSError("UNSAFE_STORAGE")
    if path.is_symlink():
        raise OSError("UNSAFE_STORAGE")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir() or path.stat().st_uid != os.getuid():
        raise OSError("UNSAFE_STORAGE")
    path.chmod(0o700)


def write_private(path, raw):
    # No plaintext temp copy; a crash leaves at most this exact owned key file.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def guarded(fn):
    signature = inspect.signature(fn)

    @functools.wraps(fn)
    def call(self, *args, **kwargs):
        bound = signature.bind(self, *args, **kwargs).arguments
        with self.exclusive():
            self.sweep()
            try:
                result = fn(self, *args, **kwargs)
            finally:
                self.sweep()
            if fn.__name__ == "read":
                # Decryption/cleanup itself may cross the deadline. Never return
                # a materialized report whose access was blocked in that interval.
                if "report" in result[1]:
                    with self.connection() as db:
                        life = db.execute(
                            "SELECT expires,blocked FROM lifecycle WHERE tenant=? AND job_id=?",
                            (bound["tenant"], bound["jid"]),
                        ).fetchone()
                    require(
                        life is not None and life[1] is None and self.time_ms() < life[0],
                        410,
                        "REPORT_GONE",
                    )
                else:
                    result = fn(self, *args, **kwargs)
            if fn.__name__ == "mutate" and bound["path"].endswith("/receipts"):
                return 200, self.read(bound["tenant"], bound["path"].split("/")[3])[1]
            return result

    return call


class Retention:
    @contextmanager
    def exclusive(self):
        name = str(self.state)
        with LOCKS_GUARD:
            lock, local = LOCKS.setdefault(name, (threading.RLock(), threading.local()))
        require(lock.acquire(timeout=remaining(LOCK_SECONDS)), 503, "STORAGE_BUSY")
        try:
            if getattr(local, "depth", 0):
                local.depth += 1
                try:
                    yield
                finally:
                    local.depth -= 1
                return
            fd = os.open(
                self.state / ".lifecycle.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600
            )
            try:
                deadline = time.monotonic() + remaining(LOCK_SECONDS)
                while True:
                    try:
                        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError:
                        require(time.monotonic() < deadline, 503, "STORAGE_BUSY")
                        time.sleep(min(0.01, max(0, deadline - time.monotonic())))
                local.depth = 1
                yield
            finally:
                local.depth = 0
                os.close(fd)
        finally:
            lock.release()

    @contextmanager
    def connection(self):
        for suffix in ("", "-wal", "-shm", "-journal"):
            path = self.state / ("service.sqlite" + suffix)
            require(not path.is_symlink(), 503, "UNSAFE_STORAGE")
        db = sqlite3.connect(self.database, timeout=remaining(0.5), isolation_level=None)
        try:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA secure_delete=ON")
            db.execute("PRAGMA temp_store=MEMORY")
            for suffix in ("", "-wal", "-shm", "-journal"):
                path = self.state / ("service.sqlite" + suffix)
                if path.exists():
                    if path.is_symlink():
                        raise OSError("UNSAFE_STORAGE")
                    path.chmod(0o600)
            yield db
        finally:
            db.close()

    def setup_retention(self, db):
        db.executescript("""
          CREATE TABLE IF NOT EXISTS lifecycle (
            tenant TEXT, job_id TEXT, completed INTEGER, expires INTEGER,
            report_digest TEXT, received INTEGER, blocked INTEGER, reason TEXT,
            cleanup TEXT NOT NULL DEFAULT 'not_due', cleaned INTEGER,
            inputs_cleaned INTEGER, retain_until INTEGER NOT NULL, input_deadline INTEGER,
            PRIMARY KEY(tenant,job_id));
          CREATE TABLE IF NOT EXISTS request_deadlines (
            tenant TEXT, idem TEXT, retain_until INTEGER NOT NULL,
            PRIMARY KEY(tenant,idem));
          CREATE TABLE IF NOT EXISTS clock_state (id INTEGER PRIMARY KEY CHECK(id=1), floor INTEGER NOT NULL);
          INSERT OR IGNORE INTO clock_state VALUES (1,0);
        """)
        private_dir(self.state / "jobs")

    def job_dir(self, tenant, jid):
        # Only generated server IDs, no caller path segments, no symlink traversal.
        require(len(jid) == 32 and all(c in "0123456789abcdef" for c in jid))
        parent = self.state / "jobs" / hashlib.sha256(tenant.encode()).hexdigest()
        for path in (self.state / "jobs", parent, parent / jid):
            if path.is_symlink():
                raise OSError("UNSAFE_STORAGE")
        return parent / jid

    def seal(self, tenant, jid, field, value):
        folder = self.job_dir(tenant, jid)
        private_dir(folder.parent)
        private_dir(folder)
        keyfile = folder / "content.key"
        if not keyfile.exists():
            write_private(keyfile, secrets.token_bytes(32))
            fsync_dir(folder)
        fd = os.open(keyfile, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as source:
            key = source.read()
        aad = f"aa-storage-v1:{tenant}:{jid}:{field}".encode()
        return (
            "gcm1:" + base64.b64encode(crypt(key, json.dumps(value).encode(), aad, True)).decode()
        )

    def unseal(self, tenant, jid, field, value):
        require(type(value) is str and value.startswith("gcm1:"), 503, "STORAGE_INVALID")
        fd = os.open(self.job_dir(tenant, jid) / "content.key", os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as source:
            key = source.read()
        aad = f"aa-storage-v1:{tenant}:{jid}:{field}".encode()
        try:
            return json.loads(crypt(key, base64.b64decode(value[5:], validate=True), aad, False))
        except ValueError as error:
            raise Problem(503, "STORAGE_INVALID") from error

    def finish(self, db, tenant, jid, report, state, now):
        expires = now + REPORT_TTL
        report.update(completed_at=iso(now), expires_at=iso(expires), report_version="1")
        signed = self.report_signer(report)
        require(
            signed.get("body") == report and verify(self.config["report_public_key"], signed),
            503,
            "REPORT_SIGNING_FAILED",
        )
        db.execute(
            "UPDATE jobs SET state=?,report=?,request=NULL,acceptance=NULL WHERE tenant=? AND id=?",
            (state, self.seal(tenant, jid, "report", signed), tenant, jid),
        )
        db.execute("DELETE FROM dispatch_pins WHERE tenant=? AND job_id=?", (tenant, jid))
        db.execute(
            "UPDATE lifecycle SET completed=?,expires=?,report_digest=?,cleanup='inputs_pending',"
            "retain_until=max(retain_until,?) WHERE tenant=? AND job_id=?",
            (now, expires, digest(signed), expires + MAX_REQUEST + RETRY_CLOCK, tenant, jid),
        )
        return signed

    def receipt(self, db, tenant, jid, kid, payload, now):
        from research.private_service.protocol import fields

        fields(payload, "job_id report_version report_sha256 received_complete")
        require(
            payload["job_id"] == jid
            and payload["report_version"] == "1"
            and payload["received_complete"] is True,
            422,
            "RECEIPT_MISMATCH",
        )
        row = db.execute(
            "SELECT sender,receiver FROM jobs WHERE tenant=? AND id=?", (tenant, jid)
        ).fetchone()
        require(row is not None, 404, "NOT_FOUND")
        require(kid in row, 403, "OBJECT_FORBIDDEN")
        life = db.execute(
            "SELECT report_digest,completed,blocked,reason FROM lifecycle WHERE tenant=? AND job_id=?",
            (tenant, jid),
        ).fetchone()
        require(life is not None and life[1] is not None, 409, "REPORT_PENDING")
        require(payload["report_sha256"] == life[0], 422, "RECEIPT_MISMATCH")
        require(life[2] is None or life[3] == "receipt", 410, "REPORT_GONE")
        db.execute(
            "UPDATE lifecycle SET received=coalesce(received,?),blocked=coalesce(blocked,?),"
            "reason='receipt',cleanup=CASE WHEN cleanup='complete' THEN cleanup ELSE 'pending' END "
            "WHERE tenant=? AND job_id=?",
            (now, now, tenant, jid),
        )
        db.execute("UPDATE jobs SET report=NULL WHERE tenant=? AND id=?", (tenant, jid))
        return 200, {"schema": "aa-private-v1", "job_id": jid, "receipt": "accepted"}

    def _remove_tree(self, path):
        # Never follow symlinks, and never target paths outside the generated job tree.
        if path.is_symlink():
            raise OSError("UNSAFE_STORAGE")
        if not path.exists():
            return
        for entry in path.iterdir():
            mode = entry.lstat().st_mode
            if stat.S_ISDIR(mode):
                self._remove_tree(entry)
            elif stat.S_ISREG(mode):
                entry.unlink()
            else:
                raise OSError("UNSAFE_STORAGE")
        path.rmdir()
        fsync_dir(path.parent)

    def _clean(self, tenant, jid, blocked):
        folder = self.job_dir(tenant, jid)
        # Only owned per-job files; guest cleanup may keep this pending separately.
        if blocked:
            self._remove_tree(folder)
        else:
            self._remove_tree(folder / "scratch")
        with self.connection() as db:
            busy, frames, checkpointed = db.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            if busy or frames != checkpointed:
                raise OSError("CHECKPOINT_PENDING")
        if blocked and folder.exists():
            raise OSError("FILES_REMAIN")
        if not blocked and (folder / "scratch").exists():
            raise OSError("FILES_REMAIN")

    def sweep(self):
        """Call under exclusive lock, at startup, each operation and HTTP idle tick."""
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            self.clock_floor = max(
                now_ms(), db.execute("SELECT floor FROM clock_state WHERE id=1").fetchone()[0]
            )
            now = self.clock_floor
            db.execute("UPDATE clock_state SET floor=? WHERE id=1", (now,))
            # Stalled execution: no redispatch; deadline anchored at durable dispatch.
            stale = db.execute(
                "SELECT j.tenant,j.id,j.state FROM jobs j JOIN lifecycle l "
                "ON l.tenant=j.tenant AND l.job_id=j.id WHERE "
                "(j.state IN ('awaiting_acceptance','queued') AND coalesce(l.input_deadline,j.created+60000)<=?) OR "
                "(j.state='running' AND j.dispatched+180000<=?)",
                (now, now),
            ).fetchall()
            for tenant, jid, state in stale:
                self._unknown(
                    db, tenant, jid, "WORKER_TIMEOUT" if state == "running" else "REQUEST_EXPIRED"
                )
            db.execute(
                "UPDATE lifecycle SET blocked=expires,reason='expired',cleanup='pending' "
                "WHERE blocked IS NULL AND expires<=?",
                (now,),
            )
            db.execute(
                "UPDATE jobs SET report=NULL,request=NULL,acceptance=NULL WHERE EXISTS "
                "(SELECT 1 FROM lifecycle l WHERE l.tenant=jobs.tenant AND l.job_id=jobs.id AND l.blocked IS NOT NULL)"
            )
            pending = db.execute(
                "SELECT tenant,job_id,blocked FROM lifecycle WHERE cleanup IN "
                "('pending','failed','inputs_pending','inputs_failed')"
            ).fetchall()
            db.execute(
                "DELETE FROM requests WHERE EXISTS (SELECT 1 FROM request_deadlines d WHERE "
                "d.tenant=requests.tenant AND d.idem=requests.idem AND d.retain_until<=?)",
                (now,),
            )
            db.execute("DELETE FROM request_deadlines WHERE retain_until<=?", (now,))
            db.execute("DELETE FROM challenges WHERE expires<=?", (now,))
            db.execute(
                "DELETE FROM audit WHERE EXISTS (SELECT 1 FROM service_keys k WHERE "
                "k.tenant=audit.tenant AND k.kid=audit.kid AND k.expires+?<=?)",
                (MAX_REQUEST + RETRY_CLOCK, now),
            )
            db.commit()
        self.clean_orphans()

        for tenant, jid, blocked in pending:
            try:
                self._clean(tenant, jid, blocked is not None)
            except (OSError, sqlite3.Error):
                with self.connection() as db:
                    db.execute(
                        "UPDATE lifecycle SET cleanup=? WHERE tenant=? AND job_id=?",
                        ("failed" if blocked is not None else "inputs_failed", tenant, jid),
                    )
            else:
                confirmed_at = self.time_ms()
                with self.connection() as db:
                    db.execute(
                        "UPDATE lifecycle SET cleanup=?,cleaned=?,inputs_cleaned=coalesce(inputs_cleaned,?) "
                        "WHERE tenant=? AND job_id=?",
                        (
                            "complete" if blocked is not None else "not_due",
                            confirmed_at if blocked is not None else None,
                            confirmed_at,
                            tenant,
                            jid,
                        ),
                    )
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            done = db.execute(
                "SELECT tenant,job_id FROM lifecycle WHERE cleanup='complete' AND retain_until<=?",
                (now,),
            ).fetchall()
            for tenant, jid in done:
                db.execute("DELETE FROM jobs WHERE tenant=? AND id=?", (tenant, jid))
                db.execute("DELETE FROM lifecycle WHERE tenant=? AND job_id=?", (tenant, jid))
            db.commit()

    def time_ms(self):
        # A backwards wall-clock adjustment cannot reopen expired requests/reports
        # after pruning. A disk/snapshot rollback still needs an external epoch.
        return max(now_ms(), self.clock_floor)

    def clean_orphans(self):
        # A process crash before SQLite commit can leave only an owned key dir.
        root = self.state / "jobs"
        with self.connection() as db:
            owned = {
                (hashlib.sha256(t.encode()).hexdigest(), jid)
                for t, jid in db.execute("SELECT tenant,job_id FROM lifecycle")
            }
        for tenant_dir in root.iterdir():
            if (
                tenant_dir.is_symlink()
                or not tenant_dir.is_dir()
                or len(tenant_dir.name) != 64
                or any(c not in "0123456789abcdef" for c in tenant_dir.name)
            ):
                raise OSError("UNSAFE_STORAGE")
            for folder in tenant_dir.iterdir():
                if len(folder.name) != 32 or any(c not in "0123456789abcdef" for c in folder.name):
                    raise OSError("UNSAFE_STORAGE")
                if (tenant_dir.name, folder.name) not in owned:
                    self._remove_tree(folder)

    def lifecycle_status(self, db, tenant, jid):
        row = db.execute(
            "SELECT completed,expires,report_digest,received,blocked,reason,cleanup,cleaned,inputs_cleaned,retain_until FROM lifecycle WHERE tenant=? AND job_id=?",
            (tenant, jid),
        ).fetchone()
        require(row is not None, 503, "LIFECYCLE_MISSING")
        return {
            "completed_at": iso(row[0]),
            "expires_at": iso(row[1]),
            "report_version": "1" if row[0] is not None else None,
            "report_sha256": row[2],
            "receipt_state": "confirmed" if row[3] is not None else "unconfirmed",
            "received_at": iso(row[3]),
            "access_state": "blocked"
            if row[4] is not None
            else "available"
            if row[0] is not None
            else "pending",
            "deletion_reason": row[5],
            "cleanup_state": row[6],
            "cleanup_completed_at": iso(row[7]),
            "cleanup_confirmed": row[6] == "complete" and row[7] is not None,
            "content_key_state": "present"
            if (self.job_dir(tenant, jid) / "content.key").exists()
            else "absent_from_owned_namespace",
            "inputs_cleanup_completed_at": iso(row[8]),
            "residual_expires_at": iso(row[9]),
            "cleanup_scope": "this job's service files and SQLite namespace; no SSD/RAM/backup erasure claim",
        }
