"""Targeted synthetic local-state and v1 repository boundary checks."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from agent_authority.browser_contracts import Principal, Problem, Scope
from agent_authority.browser_repository import LocalReportRepository, StateLease


def principal(subject="alice", source="source-a", job="job-a", adapters=("observations",)):
    return Principal(subject, (Scope(source, job, adapters),))


def payload(number=1, source="source-a", job="job-a", adapter="observations"):
    return {
        "metadata": {
            "id": f"{number:032x}",
            "sourceId": source,
            "jobId": job,
            "adapter": adapter,
            "createdAt": "2026-10-17T07:00:00+00:00",
        },
        "report": {"claim": "synthetic, unauthenticated"},
        "graph": {"nodes": [{"id": "entry-1"}]},
    }


class BrowserRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aa-browser-repository-")
        self.state = Path(self.temp.name) / "state"
        self.state.mkdir(mode=0o700)
        self.repository = LocalReportRepository(self.state)

    def tearDown(self):
        self.repository.close()
        self.temp.cleanup()

    def problem(self, status, code, function, *args):
        with self.assertRaises(Problem) as caught:
            function(*args)
        self.assertEqual((caught.exception.status, caught.exception.code), (status, code))

    def test_owner_source_job_and_adapter_selected_before_payload_decoding(self):
        broad = Principal(
            "alice",
            (
                Scope("source-a", "job-a", ("observations", "report")),
                Scope("source-b", "job-b", ("observations",)),
            ),
        )
        for item in (payload(), payload(2, adapter="report"), payload(3, "source-b", "job-b")):
            self.repository.insert(broad, item)
        self.repository.db.execute(
            "UPDATE reports SET payload=? WHERE id<>?", (b"not-json", f"{1:032x}")
        )
        self.repository.db.commit()
        narrow = principal()
        self.assertEqual([item["id"] for item in self.repository.listing(narrow)], [f"{1:032x}"])
        self.assertEqual(
            self.repository.get(narrow, f"{1:032x}")["metadata"]["sourceId"], "source-a"
        )
        for actor, identifier in (
            (narrow, f"{2:032x}"),
            (narrow, f"{3:032x}"),
            (principal(job="job-b"), f"{3:032x}"),
            (principal("bob"), f"{1:032x}"),
            (narrow, "0" * 32),
        ):
            self.problem(404, "NOT_FOUND", self.repository.get, actor, identifier)
        self.assertEqual(self.repository.listing(principal("bob")), [])
        self.assertEqual(self.repository.listing(Principal("alice", ())), [])

    def test_validation_and_scope_checks_precede_database_access(self):
        self.repository.close()
        self.problem(
            403, "SCOPE_FORBIDDEN", self.repository.insert, principal(job="other"), payload()
        )
        self.problem(
            403, "SCOPE_FORBIDDEN", self.repository.insert, principal(), payload(adapter="report")
        )
        self.problem(
            422, "INVALID_REPORT", self.repository.insert, principal(), payload(adapter="shell")
        )
        invalid = payload()
        invalid["metadata"]["sourceId"] = "../foreign"
        self.problem(422, "INVALID_REPORT", self.repository.insert, principal(), invalid)

    def test_listing_preserves_stored_states_without_reprojecting_after_restart(self):
        actor = principal(adapters=("observations", "report", "private-verification"))
        expected = {}
        for number, adapter, state in (
            (1, "observations", "complete"),
            (2, "report", "incomplete"),
            (3, "private-verification", "reported-private-verification"),
        ):
            item = payload(number, adapter=adapter)
            item["metadata"]["state"] = state
            self.repository.insert(actor, item)
            expected[item["metadata"]["id"]] = state
        # A legacy/missing state remains unknown; it is never inferred from the
        # graph or promoted to a stronger evidence state while listing.
        self.repository.insert(actor, payload(4))
        expected[f"{4:032x}"] = "unknown"
        self.repository.close()
        self.repository = LocalReportRepository(self.state)
        listed = self.repository.listing(actor)
        self.assertEqual({item["id"]: item["state"] for item in listed}, expected)
        self.assertTrue(all("graph" not in item and "report" not in item for item in listed))

    def test_listing_bounds_payload_decoding_by_row_and_account_bytes(self):
        self.repository.insert(principal(), payload())
        used = self.repository.db.execute("SELECT length(payload) FROM reports").fetchone()[0]
        with patch("agent_authority.browser_repository.MAX_OUTPUT", used - 1):
            self.assertEqual(self.repository.listing(principal()), [])
        with patch("agent_authority.browser_repository.MAX_ACCOUNT_BYTES", used - 1):
            self.problem(409, "STORAGE_LIMIT", self.repository.listing, principal())

    def test_stored_snapshot_and_owner_survive_close_and_reopen(self):
        item = payload()
        result = self.repository.insert(principal(), item)
        item["metadata"]["sourceId"] = "foreign"
        item["graph"]["nodes"].clear()
        result["sourceId"] = "also-foreign"
        self.repository.close()
        self.repository = LocalReportRepository(self.state)
        stored = self.repository.get(principal(), f"{1:032x}")
        self.assertEqual(stored["metadata"]["sourceId"], "source-a")
        self.assertEqual(stored["graph"]["nodes"], [{"id": "entry-1"}])
        stored["graph"]["nodes"].clear()
        self.assertEqual(len(self.repository.get(principal(), f"{1:032x}")["graph"]["nodes"]), 1)
        row = self.repository.db.execute("SELECT owner,typeof(payload) FROM reports").fetchone()
        self.assertEqual(row, ("alice", "blob"))
        self.problem(404, "NOT_FOUND", self.repository.get, principal("bob"), f"{1:032x}")
        self.assertEqual(os.stat(self.state / "reports.sqlite3").st_mode & 0o777, 0o600)

    def test_atomic_count_quota_across_two_local_connections(self):
        # Two connections on one host prove SQLite transaction behaviour only.
        for number in range(1, 50):
            self.repository.insert(principal(), payload(number))
        second = LocalReportRepository(self.state)
        self.addCleanup(second.close)
        barrier = threading.Barrier(2)

        def insert(repository, number):
            barrier.wait(timeout=3)
            try:
                repository.insert(principal(), payload(number))
                return "inserted"
            except Problem as exc:
                return exc.status, exc.code

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(insert, self.repository, 50),
                executor.submit(insert, second, 51),
            ]
            outcomes = [future.result(timeout=5) for future in futures]
        self.assertCountEqual(outcomes, ["inserted", (409, "STORAGE_LIMIT")])
        self.assertEqual(
            self.repository.db.execute(
                "SELECT COUNT(*) FROM reports WHERE owner='alice'"
            ).fetchone()[0],
            50,
        )
        # A rejected transaction releases its lock; quotas remain owner-bound.
        second.insert(principal("bob"), payload(52))
        self.assertEqual(len(second.listing(principal("bob"))), 1)

    def test_busy_writer_is_bounded_and_rejected_without_retry_or_partial_result(self):
        with patch("agent_authority.browser_repository.SQLITE_TIMEOUT", 0.01):
            second = LocalReportRepository(self.state)
        self.addCleanup(second.close)
        self.assertEqual(second.db.execute("PRAGMA busy_timeout").fetchone()[0], 10)
        self.repository.db.execute("BEGIN IMMEDIATE")
        try:
            self.problem(503, "STORAGE_BUSY", second.insert, principal(), payload())
        finally:
            self.repository.db.rollback()
        self.assertEqual(second.listing(principal()), [])
        second.insert(principal(), payload())
        self.assertEqual(len(second.listing(principal())), 1)

    def test_byte_output_and_duplicate_limits_leave_no_partial_write(self):
        self.repository.insert(principal(), payload())
        used = self.repository.db.execute("SELECT length(payload) FROM reports").fetchone()[0]
        with patch("agent_authority.browser_repository.MAX_ACCOUNT_BYTES", used):
            self.problem(409, "STORAGE_LIMIT", self.repository.insert, principal(), payload(2))
        with patch("agent_authority.browser_repository.MAX_OUTPUT", 1):
            self.problem(413, "OUTPUT_LIMIT", self.repository.insert, principal(), payload(2))
        self.problem(409, "REPORT_EXISTS", self.repository.insert, principal(), payload())
        self.repository.insert(principal(), payload(2))
        self.assertEqual(len(self.repository.listing(principal())), 2)


class StateLeaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aa-browser-lease-")
        self.state = Path(self.temp.name)
        os.chmod(self.state, 0o700)

    def tearDown(self):
        self.temp.cleanup()

    def test_second_process_denied_and_restart_releases_same_lock_inode(self):
        lease = StateLease(self.state)
        lock = self.state / ".instance.lock"
        inode = lock.stat().st_ino
        self.addCleanup(lease.close)
        with self.assertRaises(ValueError):
            StateLease(self.state)
        script = """import sys
from pathlib import Path
from agent_authority.browser_repository import StateLease
try:
    lease = StateLease(Path(sys.argv[1]))
except ValueError:
    print('denied')
else:
    lease.close()
    raise SystemExit(2)
"""
        completed = subprocess.run(
            [sys.executable, "-B", "-c", script, str(self.state)],
            cwd=Path(__file__).resolve().parents[1],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(
            (completed.returncode, completed.stdout.strip()), (0, "denied"), completed.stderr
        )
        lease.close()
        restarted = StateLease(self.state)
        restarted.close()
        self.assertEqual(lock.stat().st_ino, inode)
        self.assertEqual(lock.stat().st_mode & 0o777, 0o600)

    def test_process_exit_releases_kernel_lease_without_deleting_lock(self):
        script = """import os, sys
from pathlib import Path
from agent_authority.browser_repository import StateLease
lease = StateLease(Path(sys.argv[1]))
os._exit(0)
"""
        completed = subprocess.run(
            [sys.executable, "-B", "-c", script, str(self.state)],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            timeout=5,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lock = self.state / ".instance.lock"
        inode = lock.stat().st_ino
        restarted = StateLease(self.state)
        restarted.close()
        self.assertEqual(lock.stat().st_ino, inode)

    def test_insecure_or_symlink_state_lock_and_database_rejected(self):
        lock = self.state / ".instance.lock"
        target = self.state / "target"
        target.write_bytes(b"")
        os.chmod(target, 0o600)
        lock.symlink_to(target)
        with self.assertRaises(ValueError):
            StateLease(self.state)
        lock.unlink()
        lock.write_bytes(b"")
        os.chmod(lock, 0o644)
        with self.assertRaises(ValueError):
            StateLease(self.state)
        database = self.state / "reports.sqlite3"
        database.symlink_to(target)
        with self.assertRaises(ValueError):
            LocalReportRepository(self.state)
        os.chmod(self.state, 0o755)
        with self.assertRaises(ValueError):
            StateLease(self.state)
        with self.assertRaises(ValueError):
            LocalReportRepository(self.state)


if __name__ == "__main__":
    unittest.main()
