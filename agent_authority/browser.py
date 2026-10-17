"""Private loopback browser service. Observation only; no collector or action dispatch.

Only explicit synthetic local accounts are supported until an independently agreed
production identity/source mapping exists. HTTP Basic is used solely at login;
private responses then require an expiring, server-held session.
"""

from __future__ import annotations

import argparse
import hmac
import os
import re
import signal
import socket
import sqlite3
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any

from agent_authority.browser_auth import SESSION_SECONDS, init_synthetic as init_synthetic
from agent_authority.browser_contracts import Problem
from agent_authority.browser_service import BrowserService, Store as Store, status_document
from agent_authority.browser_support import MAX_BODY, json_bytes as _json, parse_json
from agent_authority.json_source import read_observations
from agent_authority.report import build_report

STATIC = Path(__file__).with_name("browser_static")
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/strings.json": ("strings.json", "application/json; charset=utf-8"),
    "/static/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/static/style.css": ("style.css", "text/css; charset=utf-8"),
    "/static/strings.json": ("strings.json", "application/json; charset=utf-8"),
}


class BrowserServer(HTTPServer):
    allow_reuse_address = False
    request_queue_size = 8

    def __init__(self, store: BrowserService, port: int):
        self.store = store
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.expected_host = f"127.0.0.1:{self.server_port}"

    def get_request(self) -> tuple[socket.socket, Any]:
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address


class Handler(BaseHTTPRequestHandler):
    server: BrowserServer
    server_version = "AgentAuthorityBrowser/1"
    sys_version = ""
    protocol_version = "HTTP/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        pass

    def send_error(self, code: int, message: str | None = None, explain: str | None = None) -> None:
        self.reply(code, {"code": "HTTP_ERROR", "status": code})

    def reply(
        self,
        status: int,
        value: Any,
        content_type: str = "application/json; charset=utf-8",
        cookie: str | None = None,
    ) -> None:
        raw = value if isinstance(value, bytes) else _json(value)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        )
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Connection", "close")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass

    def boundary(self) -> None:
        if self.headers.get_all("Host", []) != [self.server.expected_host]:
            raise Problem(403, "HOST_FORBIDDEN")
        origins = self.headers.get_all("Origin", [])
        if origins and origins != [self.server.origin]:
            raise Problem(403, "ORIGIN_FORBIDDEN")
        if self.headers.get("Sec-Fetch-Site", "none") not in {"same-origin", "none"}:
            raise Problem(403, "ORIGIN_FORBIDDEN")
        for header in ("Cookie", "Authorization", "X-CSRF-Token", "Content-Type"):
            if len(self.headers.get_all(header, [])) > 1:
                raise Problem(400, "AMBIGUOUS_HEADERS")
        if "?" in self.path or "#" in self.path or len(self.path) > 200:
            raise Problem(404, "NOT_FOUND")

    def body(self) -> Any:
        lengths = self.headers.get_all("Content-Length", [])
        if (
            self.headers.get_all("Transfer-Encoding", [])
            or len(lengths) != 1
            or not re.fullmatch(r"[0-9]{1,8}", lengths[0])
        ):
            raise Problem(400, "INVALID_LENGTH")
        length = int(lengths[0])
        if not 0 < length <= MAX_BODY:
            raise Problem(413, "INPUT_LIMIT")
        if (
            self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            != "application/json"
        ):
            raise Problem(415, "JSON_REQUIRED")
        raw = self.rfile.read(length)
        if len(raw) != length:
            raise Problem(400, "INCOMPLETE_BODY")
        return parse_json(raw)

    def do_GET(self) -> None:
        self.handle_route("GET")

    def do_POST(self) -> None:
        self.handle_route("POST")

    def handle_route(self, method: str) -> None:
        try:
            self.boundary()
            if self.path in STATIC_FILES:
                if method != "GET":
                    raise Problem(405, "METHOD_NOT_ALLOWED")
                name, content_type = STATIC_FILES[self.path]
                self.reply(
                    200,
                    files("agent_authority").joinpath("browser_static", name).read_bytes(),
                    content_type,
                )
                return
            store = self.server.store
            if self.path == "/api/login":
                if method != "POST":
                    raise Problem(405, "METHOD_NOT_ALLOWED")
                if self.body() != {}:
                    raise Problem(422, "INVALID_LOGIN")
                session = store.access.authenticate(self.headers.get("Authorization", ""))
                self.reply(
                    200,
                    store.session_document(session),
                    cookie=f"aa_session={session.token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_SECONDS}",
                )
                return
            session = store.access.resolve(self.headers.get("Cookie", ""))
            principal = session.principal
            if method == "POST" and not hmac.compare_digest(
                self.headers.get("X-CSRF-Token", ""), session.csrf
            ):
                raise Problem(403, "CSRF_REQUIRED")
            if self.path == "/api/session" and method == "GET":
                self.reply(200, store.session_document(session))
            elif self.path == "/api/status" and method == "GET":
                document = status_document()
                document["processing"] = store.analysis.status()
                self.reply(200, document)
            elif self.path == "/api/reports" and method == "GET":
                self.reply(
                    200,
                    {
                        "reports": store.listing(principal),
                        "scopes": [s.document() for s in store.access.refresh(principal).scopes],
                    },
                )
            elif self.path == "/api/reports/import" and method == "POST":
                metadata = store.save(principal, self.body())
                self.reply(201, metadata)
            elif re.fullmatch(r"/api/reports/[a-f0-9]{32}", self.path) and method == "GET":
                self.reply(200, store.get(principal, self.path.rsplit("/", 1)[1]))
            elif self.path == "/api/demo" and method == "GET":
                from agent_authority.browser_model import demo_graph, warning_assessments

                graph = demo_graph()
                self.reply(
                    200,
                    {
                        "report": None,
                        "graph": graph,
                        "warningAssessments": warning_assessments(graph),
                        "metadata": {
                            "synthetic": True,
                            "adapter": "explicit-demo",
                            "sourceId": "AA-SAMPLE",
                            "jobId": "synthetic-demo",
                        },
                    },
                )
            elif self.path == "/api/logout" and method == "POST":
                if self.body() != {}:
                    raise Problem(422, "INVALID_LOGOUT")
                store.access.revoke(session.token)
                self.reply(
                    200,
                    {"loggedOut": True},
                    cookie="aa_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0",
                )
            else:
                raise Problem(404, "NOT_FOUND")
        except Problem as exc:
            self.reply(
                exc.status,
                {
                    "type": f"urn:aa:browser:{exc.code.lower()}",
                    "status": exc.status,
                    "code": exc.code,
                },
            )
        except (TimeoutError, ConnectionError):
            self.reply(408, {"status": 408, "code": "REQUEST_TIMEOUT"})
        except Exception:
            # Never echo input, local paths, credentials, DB errors or tracebacks.
            self.reply(500, {"status": 500, "code": "INTERNAL_ERROR"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Agent Authority private browser service; no live actions"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser(
        "init-synthetic", help="create new private empty state with two synthetic accounts"
    )
    init.add_argument("--state", type=Path, required=True)
    examples = commands.add_parser(
        "examples", help="write explicitly synthetic neutral/private JSON examples to new directory"
    )
    examples.add_argument("--output", type=Path, required=True)
    serve = commands.add_parser("serve", help="serve existing synthetic state on 127.0.0.1 only")
    serve.add_argument("--state", type=Path, required=True)
    serve.add_argument("--port", type=int, default=8873)
    inspect = commands.add_parser(
        "import-directory", help="operator-only existing neutral reader; no browser paths"
    )
    inspect.add_argument("--state", type=Path, required=True)
    inspect.add_argument("--user", required=True)
    inspect.add_argument("--source-id", required=True)
    inspect.add_argument("--job-id", required=True)
    inspect.add_argument("--input", type=Path, required=True)
    args = parser.parse_args(argv)
    os.umask(0o077)
    try:
        if args.command == "init-synthetic":
            credentials = init_synthetic(args.state)
            print("SYNTHETIC PRIVATE TEST ACCOUNTS ONLY; production identity is blocked.")
            for username, password in credentials.items():
                print(f"{username}: {password}")
            print("Passwords are displayed once; only salted scrypt hashes are stored.")
            return 0
        if args.command == "examples":
            from agent_authority.browser_examples import write_examples

            write_examples(args.output)
            print("Wrote explicitly SYNTHETIC examples; no live analysis or valid signature.")
            return 0
        store = Store(args.state)
        try:
            if args.command == "import-directory":
                principal = store.operator_principal(args.user)
                principal = store.access.authorize(principal, args.source_id, args.job_id, "report")
                report = build_report(read_observations(args.input, args.source_id), limit=100)
                metadata = store.save(
                    principal,
                    {
                        "sourceId": args.source_id,
                        "jobId": args.job_id,
                        "kind": "report",
                        "data": report,
                    },
                )
                print(_json(metadata).decode())
                return 0
            if not 0 <= args.port <= 65535:
                raise ValueError("invalid port")
            with BrowserServer(store, args.port) as server:

                def stop(signum: int, frame: Any) -> None:
                    threading.Thread(target=server.shutdown, daemon=True).start()

                signal.signal(signal.SIGTERM, stop)
                signal.signal(signal.SIGINT, stop)
                print(f"Agent Authority synthetic private service: {server.origin}", flush=True)
                server.serve_forever(poll_interval=0.2)
            print("Agent Authority stopped; in-memory sessions cleared.", flush=True)
        finally:
            store.close()
    except (OSError, ValueError, Problem, sqlite3.Error):
        print(
            "Cannot start/import: invalid or unavailable private state, configuration, scope or port.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
