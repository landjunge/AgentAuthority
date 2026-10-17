"""Focused synthetic tests of replaceable server module protection boundaries."""

from __future__ import annotations

import base64
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

from agent_authority.browser_analysis import LocalReportAnalysis
from agent_authority.browser_auth import LocalAccessControl, init_synthetic
from agent_authority.browser_contracts import CONTRACT_VERSION, Problem
from agent_authority.browser_service import BrowserService, Store


class BrowserModuleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="aa-browser-modules-")
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "state"
        credentials = init_synthetic(self.path)
        self.access = LocalAccessControl(self.path)
        self.addCleanup(self.access.close)
        authorization = base64.b64encode(f"alice:{credentials['alice']}".encode()).decode()
        self.session = self.access.authenticate("Basic " + authorization)
        self.repository = Mock(contract_version=CONTRACT_VERSION)
        self.analysis = Mock(contract_version=CONTRACT_VERSION)
        self.service = BrowserService(self.access, self.repository, self.analysis)

    @staticmethod
    def envelope(**changes):
        return {
            "sourceId": "synthetic-alice",
            "jobId": "test-alice",
            "kind": "observations",
            "data": [],
            **changes,
        }

    def denied(self, status, function, *args):
        with self.assertRaises(Problem) as caught:
            function(*args)
        self.assertEqual(caught.exception.status, status)

    def test_denied_source_adapter_and_module_names_never_invoke_ports(self):
        for changes, status in (
            ({"sourceId": "synthetic-bob", "jobId": "test-bob"}, 403),
            ({"jobId": "other-job"}, 403),
            ({"kind": "private-verification"}, 403),
            ({"kind": "agent_authority.browser"}, 422),
            ({"sourceId": "file:///etc/passwd"}, 422),
        ):
            self.denied(status, self.service.save, self.session.principal, self.envelope(**changes))
        self.analysis.project.assert_not_called()
        self.repository.insert.assert_not_called()

    def test_revocation_during_analysis_prevents_commit(self):
        def project(*_args):
            self.access.revoke(self.session.token)
            return {"report": {}, "graph": {"completeRead": True}}

        self.analysis.project.side_effect = project
        self.denied(401, self.service.save, self.session.principal, self.envelope())
        self.analysis.project.assert_called_once()
        self.repository.insert.assert_not_called()
        self.denied(401, self.service.listing, self.session.principal)
        self.denied(401, self.service.get, self.session.principal, "0" * 32)
        self.repository.listing.assert_not_called()
        self.repository.get.assert_not_called()

    def test_scope_revocation_during_analysis_prevents_commit(self):
        def project(*_args):
            account = self.access._accounts["alice"]
            self.access._accounts["alice"] = replace(
                account, principal=replace(account.principal, scopes=())
            )
            return {"report": {}, "graph": {"completeRead": True}}

        self.analysis.project.side_effect = project
        self.denied(403, self.service.save, self.session.principal, self.envelope())
        self.repository.insert.assert_not_called()

    def test_auth_failure_never_falls_back_and_repository_has_no_session_secret(self):
        with patch.object(self.access, "refresh", side_effect=RuntimeError("backend unavailable")):
            with self.assertRaises(RuntimeError):
                self.service.listing(self.session.principal)
        self.repository.listing.assert_not_called()
        self.service.listing(self.session.principal)
        sent = self.repository.listing.call_args.args[0]
        self.assertEqual(sent.subject, "alice")
        self.assertEqual(sent.scopes, self.session.principal.scopes)
        self.assertIsNone(sent.session_id)
        incompatible = Mock(contract_version=CONTRACT_VERSION + 1)
        with self.assertRaises(ValueError):
            BrowserService(incompatible, self.repository, self.analysis)

    def test_analysis_slot_rejects_overlap_and_releases_after_failure(self):
        runner = LocalReportAnalysis()
        entered, release = threading.Event(), threading.Event()
        errors = []

        def project(*_args):
            entered.set()
            if not release.wait(3):
                raise AssertionError("test release timed out")
            raise ValueError("synthetic failure")

        def first():
            try:
                runner.project("source", "job", "observations", [])
            except ValueError:
                errors.append("expected failure")

        with patch.object(runner, "_project", side_effect=project):
            thread = threading.Thread(target=first)
            thread.start()
            try:
                self.assertTrue(entered.wait(3))
                self.assertEqual(runner.status()["active"], 1)
                self.denied(429, runner.project, "source", "job", "observations", [])
            finally:
                release.set()
                thread.join(4)
            self.assertFalse(thread.is_alive())
        self.assertEqual(errors, ["expected failure"])
        self.assertEqual(runner.status()["rejectedBusy"], 1)
        self.assertEqual(runner.status()["active"], 0)
        self.assertFalse(runner.status()["durableQueue"])
        self.assertEqual(
            runner.project("source", "job", "observations", [])["report"]["role"], "observer_only"
        )

    def test_store_restart_invalidates_session_and_keeps_exact_result(self):
        store = Store(self.path)
        try:
            principal = store.operator_principal("alice")
            metadata = store.save(principal, self.envelope())
            original = store.get(principal, metadata["id"])
            old_cookie = "aa_session=" + principal.session_id
        finally:
            store.close()
        restarted = Store(self.path)
        try:
            self.denied(401, restarted.access.resolve, old_cookie)
            self.assertEqual(
                restarted.get(restarted.operator_principal("alice"), metadata["id"]), original
            )
            self.denied(404, restarted.get, restarted.operator_principal("bob"), metadata["id"])
        finally:
            restarted.close()


if __name__ == "__main__":
    unittest.main()
