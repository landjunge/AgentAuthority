"""Focused private service checks; all accounts and observations are synthetic."""

from __future__ import annotations

import base64
import copy
from dataclasses import replace
import http.client
import json
import os
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_authority.browser import (
    MAX_BODY,
    BrowserServer,
    Store,
    init_synthetic,
)
from agent_authority.browser_analysis import LocalReportAnalysis
from agent_authority.observations import Snapshot, Source
from agent_authority.report import build_report
from agent_authority.browser_model import validate_graph


def observations(source="synthetic-alice"):
    return [
        {
            "schema_version": "agent-authority-observation-v1",
            "id": f"entry-{i}",
            "source_id": source,
            "ordinal": i,
            "kind": kind,
            "reported_actor_type": '<img src=x onerror="alert(1)">',
            "task_key": "private task claim",
        }
        for i, kind in enumerate(["task", "claimed", "result"], 1)
    ]


class BrowserServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="aa-browser-unit-")
        self.state = Path(self.temp.name) / "state"
        self.credentials = init_synthetic(self.state)
        self.store = Store(self.state)
        self.server = BrowserServer(self.store, 0)
        self.thread = threading.Thread(
            target=self.server.serve_forever, kwargs={"poll_interval": 0.01}
        )
        self.thread.start()
        self.cookies = {}
        self.csrf = {}

    def tearDown(self):
        self.server.shutdown()
        self.thread.join(5)
        self.server.server_close()
        self.store.close()
        self.temp.cleanup()

    def request(self, method, path, body=None, user=None, headers=None, raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=8)
        request_headers = {"Content-Type": "application/json"}
        if user:
            request_headers["Cookie"] = self.cookies[user]
            request_headers["X-CSRF-Token"] = self.csrf[user]
        request_headers.update(headers or {})
        encoded = (
            raw if raw is not None else json.dumps(body).encode() if body is not None else None
        )
        connection.request(method, path, body=encoded, headers=request_headers)
        response = connection.getresponse()
        data, response_headers = response.read(), dict(response.getheaders())
        status = response.status
        connection.close()
        if response_headers.get("Content-Type", "").startswith("application/json"):
            data = json.loads(data)
        return status, data, response_headers

    def login(self, username):
        auth = base64.b64encode(f"{username}:{self.credentials[username]}".encode()).decode()
        status, value, headers = self.request(
            "POST", "/api/login", {}, headers={"Authorization": f"Basic {auth}"}
        )
        self.assertEqual(status, 200)
        self.assertTrue(value["user"]["synthetic"])
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        self.cookies[username] = headers["Set-Cookie"].split(";", 1)[0]
        self.csrf[username] = value["csrfToken"]
        return value

    def upload(self, user="alice", records=None, **overrides):
        body = {
            "sourceId": f"synthetic-{user}",
            "jobId": f"test-{user}",
            "kind": "observations",
            "data": observations(f"synthetic-{user}") if records is None else records,
        }
        body.update(overrides)
        return self.request("POST", "/api/reports/import", body, user=user)

    def test_anonymous_denied_and_no_example_fallback(self):
        for path in (
            "/api/reports",
            "/api/session",
            "/api/status",
            "/api/demo",
            "/api/reports/" + "a" * 32,
        ):
            self.assertEqual(self.request("GET", path)[0], 401)
        self.login("alice")
        status, value, _ = self.request("GET", "/api/reports", user="alice")
        self.assertEqual((status, value["reports"]), (200, []))

    def test_account_source_and_job_isolation(self):
        self.login("alice")
        self.login("bob")
        status, metadata, _ = self.upload()
        self.assertEqual(status, 201)
        identifier = metadata["id"]
        status, value, _ = self.request("GET", f"/api/reports/{identifier}", user="alice")
        self.assertEqual(status, 200)
        self.assertEqual(value["metadata"]["sourceId"], "synthetic-alice")
        self.assertEqual(self.request("GET", f"/api/reports/{identifier}", user="bob")[0], 404)
        self.assertEqual(self.request("GET", "/api/reports/" + "0" * 32, user="bob")[0], 404)
        self.assertEqual(self.request("GET", "/api/reports", user="bob")[1]["reports"], [])
        self.assertEqual(self.upload("bob", sourceId="synthetic-alice", jobId="test-alice")[0], 403)
        self.assertEqual(self.upload(jobId="not-allowed")[0], 403)
        self.assertEqual(self.upload(sourceId="../../etc/passwd")[0], 422)
        self.assertEqual(self.upload(kind="shell", data="touch nope")[0], 422)

    def test_engine_semantics_provenance_and_foreign_text(self):
        self.login("alice")
        status, metadata, _ = self.upload()
        self.assertEqual(status, 201)
        _, value, _ = self.request("GET", f"/api/reports/{metadata['id']}", user="alice")
        report, graph = value["report"], value["graph"]
        self.assertEqual(report["summary"]["tasks_with_reported_association"], 1)
        self.assertEqual(report["summary"]["claims_without_later_result_in_read_entries"], 0)
        self.assertEqual(report["source"]["entries_read"], 3)
        self.assertIs(report["source"]["source_authenticated"], False)
        self.assertEqual(report["source"]["identity"], "UNBEKANNT")
        self.assertEqual(report["source"]["effect"], "UNBEKANNT")
        self.assertFalse(report["rights_inherited"])
        self.assertFalse(report["task_completion_proven"])
        self.assertEqual({node["kind"] for node in graph["nodes"]}, {"entry", "task"})
        self.assertEqual(len(graph["edges"]), 3)
        self.assertEqual(
            report["recent_entries"][0]["reported_actor_type"], '<img src=x onerror="alert(1)">'
        )
        self.assertNotIn("private task claim", json.dumps(value))
        self.assertFalse(graph["isDemo"])

    def test_browser_raw_json_preserves_duplicate_key_rejection(self):
        self.login("alice")
        report = LocalReportAnalysis.observation_report(observations(), "synthetic-alice")
        raw = json.dumps(report)
        body = {
            "sourceId": "synthetic-alice",
            "jobId": "test-alice",
            "kind": "report",
            "rawData": raw,
        }
        self.assertEqual(self.request("POST", "/api/reports/import", body, user="alice")[0], 201)
        body["rawData"] = raw.replace(
            '"role": "observer_only"', '"role": "forged", "role": "observer_only"'
        )
        self.assertEqual(self.request("POST", "/api/reports/import", body, user="alice")[0], 400)
        body["data"] = report
        self.assertEqual(self.request("POST", "/api/reports/import", body, user="alice")[0], 422)

    def test_large_ordinal_preserved_in_graph_and_exact_report_text(self):
        self.login("alice")
        records = observations()
        records[-1]["ordinal"] = 9007199254740993
        status, metadata, _ = self.upload(records=records)
        self.assertEqual(status, 201)
        graph = self.request("GET", f"/api/reports/{metadata['id']}", user="alice")[1]["graph"]
        self.assertEqual(
            json.loads(graph["reportJSON"])["recent_entries"][0]["ordinal"], 9007199254740993
        )
        selected = next(node for node in graph["nodes"] if node["id"] == "entry-3")
        self.assertEqual(
            next(f["value"] for f in selected["facts"] if f["labelKey"] == "field.ordinal"),
            "9007199254740993",
        )

    def test_empty_incomplete_and_invalid_reports_are_distinct(self):
        account = self.login("alice")
        status, metadata, _ = self.upload(records=[])
        self.assertEqual(status, 201)
        complete_id = metadata["id"]
        value = self.request("GET", f"/api/reports/{metadata['id']}", user="alice")[1]
        self.assertEqual(value["graph"]["nodes"], [])
        self.assertTrue(value["graph"]["completeRead"])
        from agent_authority.observations import Diagnostic

        report = build_report(
            Snapshot(
                Source("json-directory", "synthetic-alice"),
                (),
                (Diagnostic("source_unavailable"),),
                0,
                0,
                directory_scan_complete=False,
            )
        )
        status, metadata, _ = self.upload(kind="report", data=report)
        self.assertEqual(status, 201)
        incomplete_id = metadata["id"]
        value = self.request("GET", f"/api/reports/{metadata['id']}", user="alice")[1]
        self.assertFalse(value["graph"]["completeRead"])
        self.assertEqual(value["graph"]["warnings"], ["source_unavailable"])
        report["source"]["source_authenticated"] = True
        self.assertEqual(self.upload(kind="report", data=report)[0], 422)
        self.assertEqual(self.upload(kind="report", data={"schema": "aa-report-v1"})[0], 422)
        self.assertEqual(self.upload(kind="report", data="/etc/passwd")[0], 422)
        from agent_authority.browser_adapter import synthetic_private_response

        scope = next(s for s in account["scopes"] if s["sourceId"] == "synthetic-private-alice")
        status, metadata, _ = self.request(
            "POST",
            "/api/reports/import",
            {
                **scope,
                "kind": "private-verification",
                "data": synthetic_private_response(scope["jobId"]),
            },
            user="alice",
        )
        self.assertEqual(status, 201)
        listing = self.request("GET", "/api/reports", user="alice")[1]["reports"]
        self.assertEqual(
            {item["id"]: item["state"] for item in listing},
            {
                complete_id: "complete",
                incomplete_id: "incomplete",
                metadata["id"]: "reported-private-verification",
            },
        )

    def test_server_modules_and_state_are_not_browser_resources(self):
        self.login("alice")
        for path in (
            "/browser_auth.py",
            "/agent_authority/browser_service.py",
            "/config.json",
            "/reports.sqlite3",
            "/.instance.lock",
            "/api/modules",
        ):
            status, value, _ = self.request("GET", path, user="alice")
            self.assertEqual((status, value["code"]), (404, "NOT_FOUND"))
        document = self.request("GET", "/api/status", user="alice")[1]
        self.assertEqual(document["production"]["multiInstance"], "blocked")
        self.assertEqual(document["architecture"]["graphComputation"], "browser")
        self.assertEqual(document["processing"]["concurrencyLimit"], 1)
        self.assertFalse(document["processing"]["durableQueue"])

    def test_csrf_host_origin_and_method_boundaries(self):
        self.login("alice")
        self.assertEqual(
            self.request(
                "POST", "/api/logout", {}, user="alice", headers={"X-CSRF-Token": "wrong"}
            )[0],
            403,
        )
        self.assertEqual(
            self.request("GET", "/api/reports", user="alice", headers={"Host": "evil.example"})[0],
            403,
        )
        self.assertEqual(
            self.request(
                "GET", "/api/reports", user="alice", headers={"Origin": "https://evil.example"}
            )[0],
            403,
        )
        self.assertEqual(
            self.request(
                "GET", "/api/reports", user="alice", headers={"Sec-Fetch-Site": "cross-site"}
            )[0],
            403,
        )
        self.assertEqual(self.request("GET", "/api/reports?owner=bob", user="alice")[0], 404)
        self.assertEqual(self.request("GET", "/../../etc/passwd", user="alice")[0], 404)
        self.assertEqual(self.request("POST", "/api/demo", {}, user="alice")[0], 404)
        self.assertEqual(self.request("POST", "/api/logout", {}, user="alice")[0], 200)
        self.assertEqual(self.request("GET", "/api/reports", user="alice")[0], 401)

    def test_input_limits_duplicates_and_problems_do_not_echo(self):
        self.login("alice")
        self.assertEqual(
            self.request("POST", "/api/reports/import", user="alice", raw=b'{"data":1,"data":2}')[
                0
            ],
            400,
        )
        self.assertEqual(
            self.request("POST", "/api/reports/import", user="alice", raw=b'{"data":NaN}')[0], 400
        )
        self.assertEqual(
            self.request(
                "POST", "/api/reports/import", user="alice", raw=b"[" * 40 + b"0" + b"]" * 40
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "POST",
                "/api/reports/import",
                user="alice",
                raw=b"{}",
                headers={"Content-Length": str(MAX_BODY + 1)},
            )[0],
            413,
        )
        self.assertEqual(
            self.request(
                "POST",
                "/api/reports/import",
                user="alice",
                raw=b"{}",
                headers={"Transfer-Encoding": "chunked"},
            )[0],
            400,
        )
        self.assertEqual(
            self.request(
                "POST",
                "/api/reports/import",
                user="alice",
                raw=b"{}",
                headers={"Content-Type": "text/plain"},
            )[0],
            415,
        )
        data = observations()
        data[0]["reported_actor_type"] = "x" * 81
        status, problem, _ = self.upload(records=data)
        self.assertEqual(status, 422)
        self.assertNotIn("x" * 81, json.dumps(problem))
        self.assertNotIn(str(self.state), json.dumps(problem))
        data = observations()
        data.append(copy.deepcopy(data[0]))
        self.assertEqual(self.upload(records=data)[0], 422)

    def test_explicit_demo_status_and_csp(self):
        self.login("alice")
        status, value, _ = self.request("GET", "/api/demo", user="alice")
        self.assertEqual(status, 200)
        self.assertTrue(value["graph"]["isDemo"])
        self.assertTrue(value["metadata"]["synthetic"])
        self.assertNotIn("warningAssessments", value["graph"])
        self.assertEqual(len(value["warningAssessments"]), 6)
        validate_graph(value["graph"])
        self.assertEqual(self.request("GET", "/api/reports", user="alice")[1]["reports"], [])
        _, value, _ = self.request("GET", "/api/status", user="alice")
        self.assertEqual(value["production"]["identity"], "blocked")
        self.assertFalse(value["actions"])
        _, raw, headers = self.request("GET", "/")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertIsInstance(raw, bytes)

    def test_session_expiry_and_second_local_instance_is_blocked(self):
        self.login("alice")
        token = self.cookies["alice"].split("=", 1)[1]
        with self.assertRaises(ValueError):
            Store(self.state)
        user, csrf, _ = self.store.access._sessions[token]
        self.store.access._sessions[token] = (user, csrf, time.monotonic() - 1)
        self.assertEqual(self.request("GET", "/api/session", user="alice")[0], 401)

    def test_storage_bound_and_scope_revocation(self):
        self.login("alice")
        self.assertEqual(self.upload()[0], 201)
        identifier = self.store.listing(self.store.access.resolve(self.cookies["alice"]).principal)[
            0
        ]["id"]
        account = self.store.access._accounts["alice"]
        self.store.access._accounts["alice"] = replace(
            account, principal=replace(account.principal, scopes=())
        )
        self.assertEqual(
            self.store.listing(self.store.access.resolve(self.cookies["alice"]).principal), []
        )
        self.assertEqual(self.request("GET", f"/api/reports/{identifier}", user="alice")[0], 404)

    def test_login_rate_limit_expires_without_revealing_account_existence(self):
        authorization = "Basic " + base64.b64encode(b"nonexistent:wrong").decode()
        for _ in range(12):
            status, value, _ = self.request(
                "POST", "/api/login", {}, headers={"Authorization": authorization}
            )
            self.assertEqual((status, value["code"]), (401, "AUTH_REQUIRED"))
        self.assertEqual(
            self.request("POST", "/api/login", {}, headers={"Authorization": authorization})[0], 429
        )
        self.store.access._failed_logins = [time.monotonic() - 61]
        self.login("alice")

    def test_report_count_and_byte_quotas_are_account_scoped(self):
        self.login("alice")
        self.login("bob")
        self.assertEqual(self.upload()[0], 201)
        with patch("agent_authority.browser_repository.MAX_REPORTS", 1):
            self.assertEqual(self.upload()[0], 409)
            self.assertEqual(self.upload("bob")[0], 201)
        used = self.store.repository.db.execute(
            "SELECT SUM(length(payload)) FROM reports WHERE owner=?", ("alice",)
        ).fetchone()[0]
        with patch("agent_authority.browser_repository.MAX_ACCOUNT_BYTES", used):
            self.assertEqual(self.upload()[0], 409)
        self.assertEqual(
            len(self.store.listing(self.store.access.resolve(self.cookies["alice"]).principal)), 1
        )

    def test_database_failure_returns_fixed_error_without_private_details(self):
        self.login("alice")
        self.store.repository.db.close()
        status, value, _ = self.request("GET", "/api/reports", user="alice")
        self.assertEqual((status, value), (500, {"status": 500, "code": "INTERNAL_ERROR"}))
        self.assertNotIn(str(self.state), json.dumps(value))

    def test_private_state_permissions_and_production_config_blocked(self):
        self.assertEqual(os.stat(self.state).st_mode & 0o777, 0o700)
        self.assertEqual(os.stat(self.state / "config.json").st_mode & 0o777, 0o600)
        self.assertEqual(os.stat(self.state / "reports.sqlite3").st_mode & 0o777, 0o600)
        config = json.loads((self.state / "config.json").read_text())
        config["synthetic"] = False
        (self.state / "config.json").write_text(json.dumps(config))
        from agent_authority.browser_auth import LocalAccessControl

        with self.assertRaises(ValueError):
            LocalAccessControl(self.state)


if __name__ == "__main__":
    unittest.main()
