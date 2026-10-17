"""Private loopback browser service. Observation only; no collector or action dispatch.

Only explicit synthetic local accounts are supported until an independently agreed
production identity/source mapping exists. HTTP Basic is used solely at login;
private responses then require an expiring, server-held session.
"""

from __future__ import annotations

import argparse
import os
import signal
import socket
import sqlite3
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from agent_authority.browser_auth import init_synthetic as init_synthetic
from agent_authority.browser_contracts import Problem
from agent_authority.browser_http import BrowserRoutes, HTTPProfile, response_headers
from agent_authority.browser_service import BrowserService, Store as Store
from agent_authority.browser_support import MAX_BODY as MAX_BODY, json_bytes as _json
from agent_authority.json_source import read_observations
from agent_authority.report import build_report

class BrowserServer(HTTPServer):
    allow_reuse_address = False
    request_queue_size = 8

    def __init__(self, store: BrowserService, port: int):
        self.store = store
        super().__init__(("127.0.0.1", port), Handler)
        self.origin = f"http://127.0.0.1:{self.server_port}"
        self.expected_host = f"127.0.0.1:{self.server_port}"
        self.profile = HTTPProfile(self.origin)

    def get_request(self) -> tuple[socket.socket, Any]:
        connection, address = super().get_request()
        connection.settimeout(5)
        return connection, address


class Handler(BrowserRoutes, BaseHTTPRequestHandler):
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
        for name, value in response_headers(content_type, len(raw), cookie):
            self.send_header(name, value)
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(raw)
        except (BrokenPipeError, ConnectionResetError, TimeoutError):
            pass



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
