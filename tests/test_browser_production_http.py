"""Focused synthetic checks for the fixed HTTPS proxy transport and shared routes."""

from __future__ import annotations

import base64
import io
import json
import socket
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agent_authority.browser_auth import init_synthetic
from agent_authority.browser_http import HTTPProfile
from agent_authority.browser_service import Store
from agent_authority.browser_wsgi import BrowserWSGI


class HTTPProfileTests(unittest.TestCase):
    def test_plain_http_remains_loopback_and_https_is_explicit(self):
        for origin, prefix, secure in (
            ("http://example.test", "/", False),
            ("http://127.0.0.1:8873", "/authority/", False),
            ("http://127.0.0.1:8873", "/", True),
            ("https://example.test/path", "/", True),
            ("https://user@example.test", "/", True),
            ("https://example.test?source=arbitrary", "/", True),
            ("https://example.test", "/authority", True),
            ("https://example.test", "/../", True),
        ):
            with (
                self.subTest(origin=origin, prefix=prefix, secure=secure),
                self.assertRaises(ValueError),
            ):
                HTTPProfile(origin, prefix, secure)
        local = HTTPProfile("http://127.0.0.1:8873")
        self.assertNotIn("Secure", local.cookie("opaque", 1800))
        secure = HTTPProfile("https://example.test", "/authority/", True)
        self.assertEqual(secure.local_path("/authority/api/session"), "/api/session")
        self.assertEqual(
            secure.cookie("opaque", 1800),
            "aa_session=opaque; HttpOnly; SameSite=Strict; Path=/authority/; Max-Age=1800; Secure",
        )


class BrowserProductionHTTPTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="aa-browser-https-")
        self.addCleanup(self.temporary.cleanup)
        self.state = Path(self.temporary.name) / "state"
        self.credentials = init_synthetic(self.state)
        self.store = Store(self.state)
        self.addCleanup(self.store.close)
        self.profile = HTTPProfile("https://example.test", "/authority/", True)
        # Fixed test-only transport value; no operator credential or network use.
        self.token = "T" * 43
        self.app = BrowserWSGI(self.store, self.profile, self.token)
        self.sessions = {}

    def request(
        self, path="/authority/", method="GET", body=None, headers=None, env=None, app=None
    ):
        raw = (
            body
            if isinstance(body, bytes)
            else json.dumps(body).encode()
            if body is not None
            else b""
        )
        environ = {
            "REQUEST_METHOD": method,
            "PATH_INFO": path,
            "RAW_URI": path,
            "SCRIPT_NAME": "",
            "QUERY_STRING": "",
            "HTTP_HOST": self.profile.expected_host,
            "HTTP_X_AA_PROXY_TOKEN": self.token,
            "wsgi.input": io.BytesIO(raw),
            "wsgi.multiprocess": False,
            "wsgi.multithread": False,
            "wsgi.url_scheme": "http",  # TLS terminates at the trusted proxy.
            "gunicorn.socket": SimpleNamespace(family=socket.AF_UNIX),
        }
        if body is not None:
            environ.update(CONTENT_LENGTH=str(len(raw)), CONTENT_TYPE="application/json")
        for name, value in (headers or {}).items():
            key = name.upper().replace("-", "_")
            environ[key if key.startswith("CONTENT_") else "HTTP_" + key] = value
        environ.update(env or {})
        response = {}

        def start_response(status, response_headers):
            response.update(status=int(status.split(" ", 1)[0]), headers=dict(response_headers))

        raw_response = b"".join((app or self.app)(environ, start_response))
        content_type = response["headers"].get("Content-Type", "")
        value = (
            json.loads(raw_response)
            if content_type.startswith("application/json")
            else raw_response
        )
        return response["status"], value, response["headers"]

    def login(self, user):
        credential = base64.b64encode(f"{user}:{self.credentials[user]}".encode()).decode()
        status, value, headers = self.request(
            "/authority/api/login", "POST", {}, {"Authorization": "Basic " + credential}
        )
        self.assertEqual(status, 200)
        self.assertTrue(value["user"]["synthetic"])
        self.assertIn("Path=/authority/", headers["Set-Cookie"])
        self.assertIn("; Secure", headers["Set-Cookie"])
        self.sessions[user] = {
            "Cookie": headers["Set-Cookie"].split(";", 1)[0],
            "X-CSRF-Token": value["csrfToken"],
        }
        return self.sessions[user]

    def test_proxy_transport_and_token_precede_all_routes_and_methods(self):
        for method in ("GET", "POST", "HEAD", "DELETE"):
            for env, headers in (
                ({}, {"X-AA-Proxy-Token": ""}),
                ({}, {"X-AA-Proxy-Token": "nicht-ascii-ä"}),
                ({"gunicorn.socket": SimpleNamespace(family=socket.AF_INET)}, {}),
            ):
                with self.subTest(method=method, env=env, headers=headers):
                    status, value, _ = self.request(method=method, headers=headers, env=env)
                    self.assertEqual((status, value["code"]), (403, "PROXY_FORBIDDEN"))
        self.assertEqual(self.request(method="DELETE")[0], 405)
        self.assertEqual(self.request()[0], 200)
        loopback = BrowserWSGI(self.store, self.profile, self.token, "loopback")
        for peer, status in (("127.0.0.1", 200), ("::1", 200), ("192.0.2.1", 403), ("", 403)):
            self.assertEqual(self.request(app=loopback, env={"REMOTE_ADDR": peer})[0], status)
        for option in ("wsgi.multiprocess", "wsgi.multithread"):
            self.assertEqual(
                self.request(env={option: True})[:2],
                (
                    503,
                    {
                        "type": "urn:aa:browser:single_instance_required",
                        "status": 503,
                        "code": "SINGLE_INSTANCE_REQUIRED",
                    },
                ),
            )

    def test_fixed_origin_prefix_and_no_forwarded_header_authority(self):
        for headers, expected in (
            ({"Host": "evil.test", "X-Forwarded-Host": "example.test"}, "HOST_FORBIDDEN"),
            ({"Origin": "https://evil.test"}, "ORIGIN_FORBIDDEN"),
            ({"Origin": "null"}, "ORIGIN_FORBIDDEN"),
            ({"Sec-Fetch-Site": "cross-site"}, "ORIGIN_FORBIDDEN"),
            ({"Sec-Fetch-Site": "same-origin, same-origin"}, "ORIGIN_FORBIDDEN"),
        ):
            with self.subTest(headers=headers):
                status, value, _ = self.request(headers=headers)
                self.assertEqual((status, value["code"]), (403, expected))
        self.assertEqual(self.request(headers={"Origin": self.profile.origin})[0], 200)
        self.assertEqual(self.request(headers={"X-Forwarded-Proto": "http"})[0], 200)
        for path, env in (
            ("/", {}),
            ("/authority-other/", {}),
            ("/authority/?owner=bob", {}),
            ("/authority/%61pp.js", {}),
            ("/authority/app.js", {"RAW_URI": "/authority/%61pp.js"}),
            ("/authority/", {"SCRIPT_NAME": "/authority"}),
            ("/authority/", {"QUERY_STRING": "owner=bob"}),
        ):
            with self.subTest(path=path, env=env):
                self.assertEqual(self.request(path, env=env)[0], 404)

    def test_external_landing_navigation_is_only_the_session_free_document(self):
        navigation = {"Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document"}
        with patch.object(self.store.access, "resolve", side_effect=AssertionError("session used")):
            for site in ("same-site", "cross-site"):
                headers = {**navigation, "Sec-Fetch-Site": site}
                status, value, response_headers = self.request(headers=headers)
                self.assertEqual(status, 200)
                self.assertIn(b"<!doctype html>", value.lower())
                self.assertNotIn("Set-Cookie", response_headers)
                for path in ("/authority/app.js", "/authority/api/session", "/authority/api/demo"):
                    with self.subTest(site=site, path=path):
                        status, value, _ = self.request(path, headers=headers)
                        self.assertEqual((status, value["code"]), (403, "ORIGIN_FORBIDDEN"))
        headers = {**navigation, "Sec-Fetch-Site": "cross-site"}
        for changes in (
            {"Sec-Fetch-Mode": "cors"},
            {"Sec-Fetch-Mode": "navigate, navigate"},
            {"Sec-Fetch-Dest": "iframe"},
            {"Sec-Fetch-Dest": "empty"},
            {"Origin": "https://help-center.test"},
            {"Origin": self.profile.origin},
        ):
            with self.subTest(changes=changes):
                status, value, _ = self.request(headers={**headers, **changes})
                self.assertEqual((status, value["code"]), (403, "ORIGIN_FORBIDDEN"))
        self.assertEqual(self.request(method="POST", body={}, headers=headers)[0], 403)
        self.assertEqual(self.request(method="HEAD", headers=headers)[0], 403)
        self.assertEqual(self.request(headers={**headers, "Host": "evil.test"})[0], 403)
        self.assertEqual(self.request(headers={**headers, "X-AA-Proxy-Token": ""})[0], 403)

    def test_secure_sessions_owner_scope_csrf_and_logout(self):
        self.assertEqual(self.request("/authority/api/reports")[0], 401)
        alice, bob = self.login("alice"), self.login("bob")
        envelope = {
            "sourceId": "synthetic-alice",
            "jobId": "test-alice",
            "kind": "observations",
            "data": [],
        }
        status, metadata, _ = self.request("/authority/api/reports/import", "POST", envelope, alice)
        self.assertEqual(status, 201)
        report_path = "/authority/api/reports/" + metadata["id"]
        self.assertEqual(self.request(report_path, headers=alice)[0], 200)
        self.assertEqual(self.request(report_path, headers=bob)[0], 404)
        self.assertEqual(self.request(report_path)[0], 401)
        self.assertEqual(
            self.request("/authority/api/reports/import", "POST", envelope, bob)[0], 403
        )
        for token in ("", "wrong", "nicht-ascii-ä"):
            status, value, _ = self.request(
                "/authority/api/logout", "POST", {}, {**alice, "X-CSRF-Token": token}
            )
            self.assertEqual((status, value["code"]), (403, "CSRF_REQUIRED"))
        status, _, headers = self.request("/authority/api/logout", "POST", {}, alice)
        self.assertEqual(status, 200)
        self.assertEqual(headers["Set-Cookie"], self.profile.cookie("", 0))
        self.assertEqual(self.request(report_path, headers=alice)[0], 401)

    def test_wsgi_framing_and_ambiguous_headers_are_bounded(self):
        for headers, body, code in (
            ({"Authorization": "Basic first, Basic second"}, {}, "AMBIGUOUS_HEADERS"),
            ({"Cookie": "aa_session=first, aa_session=second"}, {}, "AMBIGUOUS_HEADERS"),
            ({"Content-Length": "2,2"}, b"{}", "INVALID_LENGTH"),
            ({"Transfer-Encoding": "chunked"}, b"{}", "INVALID_LENGTH"),
            ({"Content-Length": "3"}, b"{}", "INCOMPLETE_BODY"),
            ({"Content-Length": "8388609"}, b"{}", "INPUT_LIMIT"),
        ):
            with self.subTest(headers=headers):
                _, value, response_headers = self.request(
                    "/authority/api/login", "POST", body, headers
                )
                self.assertEqual(value["code"], code)
                self.assertNotIn(self.token, json.dumps(value))
                self.assertEqual(response_headers["Cache-Control"], "no-store")

    def test_existing_state_lease_and_restart_keep_single_instance_semantics(self):
        alice = self.login("alice")
        with self.assertRaises(ValueError):
            Store(self.state)
        self.store.close()
        restarted = Store(self.state)
        self.addCleanup(restarted.close)
        app = BrowserWSGI(restarted, self.profile, self.token)
        self.assertEqual(self.request("/authority/api/session", headers=alice, app=app)[0], 401)


if __name__ == "__main__":
    unittest.main()
