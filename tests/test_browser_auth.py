"""Targeted synthetic checks for the server-only session and scope boundary."""

from __future__ import annotations

import base64
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from agent_authority.browser_auth import LocalAccessControl, SESSION_SECONDS, init_synthetic
from agent_authority.browser_contracts import Principal, Problem


class BrowserAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aa-browser-auth-")
        self.state = Path(self.temp.name) / "state"
        self.credentials = init_synthetic(self.state)
        self.access = LocalAccessControl(self.state)

    def tearDown(self):
        self.access.close()
        self.temp.cleanup()

    def authorization(self, subject="alice"):
        encoded = base64.b64encode(f"{subject}:{self.credentials[subject]}".encode()).decode()
        return f"Basic {encoded}"

    def problem(self, status, code, function, *args):
        with self.assertRaises(Problem) as caught:
            function(*args)
        self.assertEqual((caught.exception.status, caught.exception.code), (status, code))

    def denied_principal(self, principal):
        self.problem(401, "AUTH_REQUIRED", self.access.refresh, principal)
        self.problem(
            401,
            "AUTH_REQUIRED",
            self.access.authorize,
            principal,
            "synthetic-alice",
            "test-alice",
            "observations",
        )

    def write_config(self, mutate):
        path = self.state / "config.json"
        config = json.loads(path.read_bytes())
        mutate(config)
        path.write_text(json.dumps(config), encoding="utf-8")

    def test_login_and_resolve_bind_current_rights_to_server_session(self):
        session = self.access.authenticate(self.authorization())
        self.assertEqual(session.principal.session_id, session.token)
        self.assertNotIn(session.token, repr(session.principal))
        self.assertEqual(
            self.access.resolve(f"aa_session={session.token}").principal, session.principal
        )
        account = self.access._accounts["alice"]
        narrow = replace(account.principal, scopes=(account.principal.scopes[1],))
        self.access._accounts["alice"] = replace(account, principal=narrow)
        current = self.access.refresh(session.principal)
        self.assertEqual(current.scopes, narrow.scopes)
        self.assertEqual(current.session_id, session.token)
        self.problem(
            403,
            "SCOPE_FORBIDDEN",
            self.access.authorize,
            session.principal,
            "synthetic-alice",
            "test-alice",
            "observations",
        )

    def test_missing_or_foreign_session_context_is_denied(self):
        session = self.access.authenticate(self.authorization())
        self.denied_principal(Principal("alice", session.principal.scopes))
        self.denied_principal(replace(session.principal, session_id="unknown"))
        self.denied_principal(replace(session.principal, subject="bob"))

    def test_revoked_principal_cannot_be_reused_between_modules(self):
        session = self.access.authenticate(self.authorization())
        self.access.revoke(session.token)
        self.denied_principal(session.principal)
        self.problem(401, "AUTH_REQUIRED", self.access.resolve, f"aa_session={session.token}")

    def test_expired_principal_cannot_be_reused_between_modules(self):
        with patch("agent_authority.browser_auth.time.monotonic", return_value=100.0):
            session = self.access.authenticate(self.authorization())
        with patch(
            "agent_authority.browser_auth.time.monotonic",
            return_value=100.0 + SESSION_SECONDS,
        ):
            self.denied_principal(session.principal)
            self.problem(401, "AUTH_REQUIRED", self.access.resolve, f"aa_session={session.token}")

    def test_closed_backend_clears_context_and_cannot_issue_more_sessions(self):
        session = self.access.authenticate(self.authorization())
        self.access.close()
        self.denied_principal(session.principal)
        self.problem(401, "AUTH_REQUIRED", self.access.authenticate, self.authorization())
        self.problem(401, "AUTH_REQUIRED", self.access.for_operator, "alice")

    def test_local_operator_uses_bounded_expiring_context_and_configured_subject(self):
        self.problem(401, "AUTH_REQUIRED", self.access.for_operator, "unknown")
        with patch("agent_authority.browser_auth.time.monotonic", return_value=100.0):
            principal = self.access.for_operator("alice")
            self.assertIsNotNone(principal.session_id)
            self.assertEqual(self.access.refresh(principal), principal)
            for _ in range(127):
                self.access.for_operator("alice")
            self.problem(429, "SESSION_LIMIT", self.access.for_operator, "alice")
        with patch(
            "agent_authority.browser_auth.time.monotonic",
            return_value=100.0 + SESSION_SECONDS,
        ):
            self.denied_principal(principal)
            self.assertIsNotNone(self.access.for_operator("alice").session_id)

    def test_source_job_and_adapter_are_authorized_together(self):
        principal = self.access.authenticate(self.authorization()).principal
        self.assertEqual(
            self.access.authorize(principal, "synthetic-alice", "test-alice", "observations"),
            principal,
        )
        for source, job, adapter in (
            ("synthetic-bob", "test-bob", "observations"),
            ("synthetic-alice", "other-job", "observations"),
            ("synthetic-alice", "test-alice", "private-verification"),
            ("synthetic-alice", "test-alice", "shell"),
        ):
            self.problem(
                403, "SCOPE_FORBIDDEN", self.access.authorize, principal, source, job, adapter
            )

    def test_known_v1_configuration_preserves_only_defined_adapter_mapping(self):
        def legacy(config):
            config["schema"] = "aa-browser-synthetic-config-v1"
            for account in config["accounts"]:
                for scope in account["scopes"]:
                    del scope["adapters"]

        self.write_config(legacy)
        with_access = LocalAccessControl(self.state)
        try:
            principal = with_access.for_operator("alice")
            self.assertEqual(principal.scopes[0].adapters, ("observations", "report"))
            self.assertEqual(principal.scopes[1].adapters, ("private-verification",))
        finally:
            with_access.close()
        self.write_config(
            lambda config: config["accounts"][0]["scopes"][0].update(sourceId="custom-source")
        )
        with self.assertRaisesRegex(ValueError, "explicit v2 adapter binding"):
            LocalAccessControl(self.state)

    def test_duplicate_configured_scope_is_rejected(self):
        self.write_config(
            lambda config: config["accounts"][0]["scopes"].append(
                dict(config["accounts"][0]["scopes"][0])
            )
        )
        with self.assertRaisesRegex(ValueError, "duplicate scope"):
            LocalAccessControl(self.state)


if __name__ == "__main__":
    unittest.main()
