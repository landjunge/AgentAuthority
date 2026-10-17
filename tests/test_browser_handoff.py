"""Only the changed synthetic connection; no real Help Center identities/data."""

from __future__ import annotations

import base64
from dataclasses import replace
import http.client
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

from agent_authority.browser import BrowserServer, Store, init_synthetic
from agent_authority.browser_contracts import Principal, Problem, Scope
from agent_authority.browser_handoff import (
    SYNTHETIC_ADAPTER,
    SYNTHETIC_JOB,
    SYNTHETIC_SOURCE,
    synthetic_context,
)
from agent_authority.browser_model import validate_graph


class BrowserHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aa-handoff-test-")
        state = Path(self.temp.name) / "state"
        self.credentials = init_synthetic(state)
        config = json.loads((state / "config.json").read_text())
        config["accounts"][0]["scopes"].append(
            {
                "sourceId": SYNTHETIC_SOURCE,
                "jobId": SYNTHETIC_JOB,
                "adapters": [SYNTHETIC_ADAPTER],
            }
        )
        (state / "config.json").write_text(json.dumps(config))
        self.store = Store(state)
        self.server = BrowserServer(self.store, 0)
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.01}
        )
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(5)
        self.server.server_close()
        self.store.close()
        self.temp.cleanup()

    def request(self, path, body=None, headers=None, method="POST"):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        connection.request(
            method,
            path,
            json.dumps({} if body is None else body),
            {"Content-Type": "application/json", **(headers or {})},
        )
        response = connection.getresponse()
        status, headers, data = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return status, json.loads(data), headers

    def login(self, subject="alice"):
        authorization = base64.b64encode(
            f"{subject}:{self.credentials[subject]}".encode()
        ).decode()
        status, value, headers = self.request(
            "/api/login", headers={"Authorization": "Basic " + authorization}
        )
        self.assertEqual(status, 200)
        return {
            "Cookie": headers["Set-Cookie"].split(";", 1)[0],
            "X-CSRF-Token": value["csrfToken"],
        }

    def test_fixed_context_and_current_scope_without_storage_or_external_actions(self):
        headers = self.login()
        status, value, _ = self.request("/api/hilfezentrum/demo", headers=headers)
        self.assertEqual(status, 200)
        context, metadata = value["context"], value["metadata"]
        self.assertEqual(context["assignment"]["id"], SYNTHETIC_JOB)
        self.assertEqual(context["schema"], "hilfezentrum.authority-context.v1")
        self.assertTrue(context["case"]["synthetic"])
        self.assertFalse(context["agent_identity_verified"])
        self.assertFalse(context["handoff"]["shared_sign_in"])
        self.assertFalse(context["handoff"]["data_transferred"])
        self.assertEqual(context["handoff"]["status"], "blocked")
        self.assertEqual(metadata["adapter"], "hilfezentrum-synthetic-context")
        self.assertEqual(metadata["productionIntegration"], "blocked")
        self.assertFalse(metadata["actions"])
        self.assertFalse(metadata["grantsRights"])
        principal = self.store.access.resolve(headers["Cookie"]).principal
        self.assertEqual(self.store.listing(principal), [])
        value["context"]["case"]["synthetic"] = False
        self.assertTrue(synthetic_context(self.store, principal, {})["context"]["case"]["synthetic"])

    def test_anonymous_csrf_origin_and_foreign_account_are_checked(self):
        self.assertEqual(self.request("/api/hilfezentrum/demo")[0], 401)
        headers = self.login()
        self.assertEqual(
            self.request("/api/hilfezentrum/demo", headers={"Cookie": headers["Cookie"]})[0],
            403,
        )
        self.assertEqual(
            self.request(
                "/api/hilfezentrum/demo", headers={**headers, "Origin": "https://other.invalid"}
            )[0],
            403,
        )
        status, value, _ = self.request("/api/hilfezentrum/demo", headers=self.login("bob"))
        self.assertEqual((status, value["code"]), (404, "NOT_FOUND"))

    def test_browser_cannot_select_owner_source_job_or_transport(self):
        headers = self.login()
        for body in (
            {"owner": "bob"},
            {"assignment_id": SYNTHETIC_JOB},
            {"sourceId": SYNTHETIC_SOURCE},
            {"url": "https://other.invalid"},
            {"path": "/etc/passwd"},
            [],
        ):
            with self.subTest(body=body):
                self.assertEqual(
                    self.request("/api/hilfezentrum/demo", body=body, headers=headers)[0], 422
                )

    def test_stale_or_invented_scope_and_revocation_fail_closed(self):
        headers = self.login()
        principal = self.store.access.resolve(headers["Cookie"]).principal
        account = self.store.access._accounts["alice"]
        self.store.access._accounts["alice"] = replace(
            account,
            principal=replace(
                account.principal,
                scopes=tuple(s for s in account.principal.scopes if s.source_id != SYNTHETIC_SOURCE),
            ),
        )
        with self.assertRaises(Problem) as denied:
            synthetic_context(self.store, principal, {})
        self.assertEqual(denied.exception.status, 404)
        invented = Principal(
            "alice", (Scope(SYNTHETIC_SOURCE, SYNTHETIC_JOB, (SYNTHETIC_ADAPTER,)),)
        )
        with self.assertRaises(Problem) as denied:
            synthetic_context(self.store, invented, {})
        self.assertEqual(denied.exception.status, 401)
        self.store.access.revoke(headers["Cookie"].split("=", 1)[1])
        self.assertEqual(self.request("/api/hilfezentrum/demo", headers=headers)[0], 401)

    def test_real_context_is_blocked_after_authentication_and_csrf(self):
        self.assertEqual(self.request("/api/hilfezentrum/context")[0], 401)
        headers = self.login()
        self.assertEqual(
            self.request("/api/hilfezentrum/context", headers={"Cookie": headers["Cookie"]})[0],
            403,
        )
        status, value, _ = self.request(
            "/api/hilfezentrum/context", body={"assignment_id": SYNTHETIC_JOB}, headers=headers
        )
        self.assertEqual((status, value["code"]), (409, "HILFEZENTRUM_IDENTITY_CONTRACT_REQUIRED"))
        self.assertNotIn(SYNTHETIC_JOB, json.dumps(value))

    @unittest.skipUnless(shutil.which("node"), "Node is required for the changed browser projection")
    def test_browser_projects_context_without_verification_or_warning_claims(self):
        principal = self.store.operator_principal("alice")
        context = synthetic_context(self.store, principal, {})["context"]
        project = Path(__file__).resolve().parents[1]
        source = """
const m = require('./agent_authority/browser_static/app.js');
const context = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const graph = m.helpCenterContextGraph(context);
process.stdout.write(JSON.stringify({graph, statuses: [...m.chainStatuses(graph).values()],
  warnings: graph.nodes.map(n => m.warningAssessment(graph, n.id)),
  selectedChain: [...m.trace(graph, graph.nodes[0].id)]}));
"""
        result = subprocess.run(
            ["node", "-e", source],
            input=json.dumps(context),
            text=True,
            cwd=project,
            capture_output=True,
            timeout=5,
            check=True,
        )
        value = json.loads(result.stdout)
        graph = value["graph"]
        validate_graph(graph)
        self.assertFalse(graph["isDemo"])
        self.assertEqual(len(graph["nodes"]), 5)
        self.assertEqual(len(value["selectedChain"]), 5)
        self.assertEqual(set(value["statuses"]), {"unknown"})
        self.assertTrue(all(w["checkPerformed"] is False for w in value["warnings"]))
        self.assertFalse(any(n["kind"] == "agent" for n in graph["nodes"]))
        self.assertFalse(any(e["relation"] == "delegates" for e in graph["edges"]))
        self.assertEqual(json.loads(graph["reportJSON"]), context)


if __name__ == "__main__":
    unittest.main()
