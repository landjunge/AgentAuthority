"""Private loopback browser service. Observation only; no collector or action dispatch.

Only explicit synthetic local accounts are supported until an independently agreed
production identity/source mapping exists. HTTP Basic is used solely at login;
private responses then require an expiring, server-held session.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import signal
import socket
import sqlite3
import stat
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from importlib.resources import files
from pathlib import Path
from typing import Any

from agent_authority.json_source import read_observations
from agent_authority.observations import TOKEN
from agent_authority.report import build_report

MAX_BODY = 8 * 1024 * 1024
MAX_REPORTS = 50
MAX_ACCOUNT_BYTES = 64 * 1024 * 1024
SESSION_SECONDS = 1800
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


class Problem(Exception):
    def __init__(self, status: int, code: str):
        self.status = status
        self.code = code


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def parse_json(raw: bytes) -> Any:
    """Bound bytes, depth and aggregate structure before applying input schemas."""
    if len(raw) > MAX_BODY:
        raise Problem(413, "INPUT_LIMIT")
    try:
        value = json.loads(raw, object_pairs_hook=_unique, parse_constant=lambda _: _bad_json())
        stack = [(value, 0)]
        count = 0
        while stack:
            item, depth = stack.pop()
            count += 1
            if depth > 30 or count > 250_000:
                raise ValueError("structure limit")
            if isinstance(item, dict):
                if any(len(key) > 256 for key in item):
                    raise ValueError("key limit")
                stack.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, list):
                stack.extend((child, depth + 1) for child in item)
            elif isinstance(item, str):
                if len(item) > MAX_BODY or any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                    raise ValueError("string limit")
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Problem(400, "INVALID_JSON") from exc


def _bad_json() -> Any:
    raise ValueError("non-finite JSON")


def _json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def _private_file(path: Path, limit: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ValueError("private regular owned file required")
        if info.st_size > limit:
            raise ValueError("file limit")
        raw = bytearray()
        while len(raw) <= limit:
            chunk = os.read(fd, min(8192, limit + 1 - len(raw)))
            if not chunk:
                return bytes(raw)
            raw.extend(chunk)
        raise ValueError("file limit")
    finally:
        os.close(fd)


def _check_state(path: Path) -> None:
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
        raise ValueError("state must be a private owned directory (0700)")


def password_hash(password: str, salt: bytes) -> str:
    return hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1).hex()


def init_synthetic(path: Path) -> dict[str, str]:
    """Create a new, empty private state. Never overwrite an existing directory."""
    path.mkdir(mode=0o700)
    os.chmod(path, 0o700)
    accounts = []
    credentials = {}
    for name in ("alice", "bob"):
        password = secrets.token_urlsafe(24)
        salt = secrets.token_bytes(16)
        credentials[name] = password
        accounts.append(
            {
                "id": name,
                "synthetic": True,
                "salt": salt.hex(),
                "passwordHash": password_hash(password, salt),
                "scopes": [
                    {"sourceId": f"synthetic-{name}", "jobId": f"test-{name}"},
                    {
                        "sourceId": f"synthetic-private-{name}",
                        "jobId": hashlib.sha256(
                            f"aa-browser-synthetic-{name}".encode()
                        ).hexdigest()[:32],
                    },
                ],
            }
        )
    config = {"schema": "aa-browser-synthetic-config-v1", "synthetic": True, "accounts": accounts}
    with (path / "config.json").open("xb") as target:
        os.chmod(target.name, 0o600)
        target.write(_json(config))
    return credentials


def status_document() -> dict[str, Any]:
    return {
        "schema": "aa-browser-status-v1",
        "role": "observer_only",
        "identity": "synthetic-private-only",
        "production": {
            "identity": "blocked",
            "reason": "No agreed Help Center/OIDC audience, subject and source/job mapping",
            "collector": "blocked",
            "collectorReason": "Debian collector qualification and existing hardstop remain unchanged",
            "privateService": "blocked",
            "privateServiceReason": "No production tenant binding, report-key pin or signature verifier configured",
        },
        "capabilities": [
            "neutral-report-import",
            "neutral-observation-engine",
            "private-report-claimed-view",
            "explicit-demo",
        ],
        "actions": False,
        "grantsRights": False,
        "liveConnection": False,
        "reportRetention": "Local operator-owned synthetic state; no automated external retention contract",
    }


class Store:
    def __init__(self, path: Path):
        _check_state(path)
        config = parse_json(_private_file(path / "config.json", 65536))
        if (
            not isinstance(config, dict)
            or set(config) != {"schema", "synthetic", "accounts"}
            or config["schema"] != "aa-browser-synthetic-config-v1"
            or config["synthetic"] is not True
            or not isinstance(config["accounts"], list)
            or not 1 <= len(config["accounts"]) <= 10
        ):
            raise ValueError("only explicit synthetic configuration supported")
        self.accounts: dict[str, Any] = {}
        for account in config["accounts"]:
            if (
                not isinstance(account, dict)
                or set(account) != {"id", "synthetic", "salt", "passwordHash", "scopes"}
                or account["synthetic"] is not True
                or not isinstance(account["id"], str)
                or not TOKEN.fullmatch(account["id"])
                or account["id"] in self.accounts
                or not isinstance(account["salt"], str)
                or not re.fullmatch(r"[a-f0-9]{32}", account["salt"])
                or not isinstance(account["passwordHash"], str)
                or not re.fullmatch(r"[a-f0-9]{128}", account["passwordHash"])
                or not isinstance(account["scopes"], list)
                or not 1 <= len(account["scopes"]) <= 20
            ):
                raise ValueError("invalid synthetic account")
            for scope in account["scopes"]:
                if (
                    not isinstance(scope, dict)
                    or set(scope) != {"sourceId", "jobId"}
                    or any(not isinstance(v, str) or not TOKEN.fullmatch(v) for v in scope.values())
                ):
                    raise ValueError("invalid source/job scope")
            self.accounts[account["id"]] = account
        database = path / "reports.sqlite3"
        if database.exists() or database.is_symlink():
            info = database.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
                raise ValueError("private regular owned database required")
        self.db = sqlite3.connect(database, check_same_thread=False)
        os.chmod(database, 0o600)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA secure_delete=ON")
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS reports (owner TEXT NOT NULL, id TEXT NOT NULL, source TEXT NOT NULL, job TEXT NOT NULL, created TEXT NOT NULL, adapter TEXT NOT NULL, payload BLOB NOT NULL, PRIMARY KEY(owner,id))"
        )
        self.db.commit()
        self.sessions: dict[str, tuple[str, str, float]] = {}
        self.failed_logins: list[float] = []
        self.dummy_salt = secrets.token_bytes(16)
        self.dummy_hash = password_hash(secrets.token_urlsafe(24), self.dummy_salt)

    def close(self) -> None:
        self.sessions.clear()
        self.db.close()

    def authenticate(self, authorization: str) -> tuple[str, str]:
        now = time.monotonic()
        self.failed_logins = [t for t in self.failed_logins if now - t < 60]
        if len(self.failed_logins) >= 12:
            raise Problem(429, "LOGIN_RATE_LIMIT")
        username = password = ""
        try:
            if not authorization.startswith("Basic ") or len(authorization) > 1024:
                raise ValueError("basic required")
            decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
            username, password = decoded.split(":", 1)
            if len(username) > 128 or not 1 <= len(password) <= 256:
                raise ValueError("credential limit")
        except (ValueError, UnicodeError):
            self.failed_logins.append(now)
            raise Problem(401, "AUTH_REQUIRED") from None
        account = self.accounts.get(username)
        salt = bytes.fromhex(account["salt"]) if account else self.dummy_salt
        expected = account["passwordHash"] if account else self.dummy_hash
        candidate = password_hash(password, salt)
        if not hmac.compare_digest(expected, candidate) or account is None:
            self.failed_logins.append(now)
            raise Problem(401, "AUTH_REQUIRED")
        self.sessions = {k: v for k, v in self.sessions.items() if v[2] > now}
        if len(self.sessions) >= 128:
            raise Problem(429, "SESSION_LIMIT")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        self.sessions[token] = (username, csrf, now + SESSION_SECONDS)
        return token, username

    def session(self, cookie: str) -> tuple[str, str, str]:
        tokens = [v[11:] for v in cookie.split("; ") if v.startswith("aa_session=")]
        if len(tokens) != 1 or len(tokens[0]) > 128:
            raise Problem(401, "AUTH_REQUIRED")
        token = tokens[0]
        value = self.sessions.get(token)
        if value is None or value[2] <= time.monotonic():
            self.sessions.pop(token, None)
            raise Problem(401, "AUTH_REQUIRED")
        return token, value[0], value[1]

    def session_document(self, username: str, token: str) -> dict[str, Any]:
        return {
            "csrfToken": self.sessions[token][1],
            "user": {"id": username, "synthetic": True},
            "scopes": self.accounts[username]["scopes"],
            "production": status_document()["production"],
        }

    def _scope(self, username: str, source: str, job: str) -> None:
        if {"sourceId": source, "jobId": job} not in self.accounts[username]["scopes"]:
            raise Problem(403, "SCOPE_FORBIDDEN")

    def save(self, username: str, envelope: Any) -> dict[str, Any]:
        if not isinstance(envelope, dict) or set(envelope) not in (
            {"sourceId", "jobId", "kind", "data"},
            {"sourceId", "jobId", "kind", "rawData"},
        ):
            raise Problem(422, "INVALID_IMPORT")
        source, job, kind = envelope["sourceId"], envelope["jobId"], envelope["kind"]
        if any(not isinstance(v, str) or not TOKEN.fullmatch(v) for v in (source, job, kind)):
            raise Problem(422, "INVALID_IMPORT")
        self._scope(username, source, job)
        if "rawData" in envelope:
            if not isinstance(envelope["rawData"], str):
                raise Problem(422, "INVALID_IMPORT")
            data = parse_json(envelope["rawData"].encode("utf-8"))
        else:
            data = envelope["data"]
        from agent_authority.browser_model import decode_report

        try:
            if kind == "observations":
                report = self.observation_report(data, source)
                graph = decode_report(report)
                payload = {"report": report, "graph": graph}
            elif kind == "report":
                graph = decode_report(data)
                report = json.loads(graph["reportJSON"])
                if report["source"]["source_id"] != source:
                    raise ValueError("source mismatch")
                payload = {"report": report, "graph": graph}
            elif kind == "private-verification":
                from agent_authority.browser_adapter import adapt_private_report

                payload = adapt_private_report(data, source, job)
                payload["report"] = None
            else:
                raise Problem(422, "UNSUPPORTED_ADAPTER")
        except Problem:
            raise
        except (ValueError, TypeError, KeyError, RecursionError, OverflowError) as exc:
            raise Problem(422, "INVALID_REPORT") from exc
        created = datetime.now(timezone.utc).isoformat()
        identifier = secrets.token_hex(16)
        metadata = {
            **payload.get("metadata", {}),
            "id": identifier,
            "title": f"{source} / {job}",
            "sourceId": source,
            "jobId": job,
            "createdAt": created,
            "adapter": kind,
            "syntheticAccount": True,
            "accessIdentity": "synthetic-private-account",
            "sourceAuthentication": "UNBEKANNT",
            "productionIntegration": "blocked",
        }
        metadata["inputProvenance"] = (
            "Uploaded observations; SHA-256 covers UTF-8 json.dumps(ensure_ascii=False, separators=(',',':')) of each record; no original file bytes authenticated"
            if kind == "observations"
            else "Uploaded report statements; no source authentication, signature verification or original file recheck performed"
        )
        if kind == "private-verification":
            metadata["state"] = "reported-private-verification"
        else:
            metadata["state"] = "complete" if payload["graph"].get("completeRead") else "incomplete"
        payload["metadata"] = metadata
        raw = _json(payload)
        if len(raw) > 24 * 1024 * 1024:
            raise Problem(413, "OUTPUT_LIMIT")
        count, used = self.db.execute(
            "SELECT COUNT(*), COALESCE(SUM(length(payload)),0) FROM reports WHERE owner=?",
            (username,),
        ).fetchone()
        if count >= MAX_REPORTS or used + len(raw) > MAX_ACCOUNT_BYTES:
            raise Problem(409, "STORAGE_LIMIT")
        with self.db:
            self.db.execute(
                "INSERT INTO reports VALUES (?,?,?,?,?,?,?)",
                (username, identifier, source, job, created, kind, raw),
            )
        return metadata

    @staticmethod
    def observation_report(data: Any, source: str) -> dict[str, Any]:
        """Use the existing bounded reader and engine, never browser-supplied paths.

        The caller provides an exact JSON array of neutral observation records.
        No temporary on-disk observation copy is needed: Entry validation and
        Snapshot/build_report are the same engine boundary as json_source.
        """
        from agent_authority.observations import Entry, Snapshot, Source

        if not isinstance(data, list) or len(data) > 10_000:
            raise ValueError("observation limit")
        entries, identifiers = [], set()
        total = 0
        for record in data:
            if (
                not isinstance(record, dict)
                or not {
                    "schema_version",
                    "id",
                    "source_id",
                    "ordinal",
                    "kind",
                    "reported_actor_type",
                }
                <= set(record)
                or set(record)
                - {
                    "schema_version",
                    "id",
                    "source_id",
                    "ordinal",
                    "kind",
                    "reported_actor_type",
                    "task_key",
                }
                or record["schema_version"] != "agent-authority-observation-v1"
                or record["source_id"] != source
            ):
                raise ValueError("invalid observation")
            raw = _json(record)
            total += len(raw)
            if len(raw) > 65536 or total > MAX_BODY:
                raise ValueError("observation byte limit")
            entry = Entry(
                record["id"],
                record["ordinal"],
                record["kind"],
                record["reported_actor_type"],
                record.get("task_key"),
                hashlib.sha256(raw).hexdigest(),
            )
            if entry.identifier in identifiers:
                raise ValueError("duplicate observation")
            identifiers.add(entry.identifier)
            entries.append(entry)
        snapshot = Snapshot(
            Source("json-directory", source),
            tuple(entries),
            (),
            len(entries),
            len(entries),
            len(entries),
            True,
            total,
        )
        report = build_report(snapshot, limit=100)
        # SHA-256 here covers the documented canonical import serialization, not
        # unknown original file bytes. Store that provenance alongside the report.
        return report

    def listing(self, username: str) -> list[dict[str, Any]]:
        rows = self.db.execute(
            "SELECT id,source,job,created,adapter FROM reports WHERE owner=? ORDER BY created DESC",
            (username,),
        ).fetchall()
        return [
            {
                "id": r[0],
                "title": f"{r[1]} / {r[2]}",
                "sourceId": r[1],
                "jobId": r[2],
                "createdAt": r[3],
                "adapter": r[4],
            }
            for r in rows
            if {"sourceId": r[1], "jobId": r[2]} in self.accounts[username]["scopes"]
        ]

    def get(self, username: str, identifier: str) -> Any:
        row = self.db.execute(
            "SELECT source,job,payload FROM reports WHERE owner=? AND id=?", (username, identifier)
        ).fetchone()
        if (
            row is None
            or {"sourceId": row[0], "jobId": row[1]} not in self.accounts[username]["scopes"]
        ):
            raise Problem(404, "NOT_FOUND")
        return json.loads(row[2])


class BrowserServer(HTTPServer):
    allow_reuse_address = False
    request_queue_size = 8

    def __init__(self, store: Store, port: int):
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
                token, username = store.authenticate(self.headers.get("Authorization", ""))
                self.reply(
                    200,
                    store.session_document(username, token),
                    cookie=f"aa_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_SECONDS}",
                )
                return
            token, username, csrf = store.session(self.headers.get("Cookie", ""))
            if method == "POST" and not hmac.compare_digest(
                self.headers.get("X-CSRF-Token", ""), csrf
            ):
                raise Problem(403, "CSRF_REQUIRED")
            if self.path == "/api/session" and method == "GET":
                self.reply(200, store.session_document(username, token))
            elif self.path == "/api/status" and method == "GET":
                self.reply(200, status_document())
            elif self.path == "/api/reports" and method == "GET":
                self.reply(
                    200,
                    {
                        "reports": store.listing(username),
                        "scopes": store.accounts[username]["scopes"],
                    },
                )
            elif self.path == "/api/reports/import" and method == "POST":
                metadata = store.save(username, self.body())
                self.reply(201, metadata)
            elif re.fullmatch(r"/api/reports/[a-f0-9]{32}", self.path) and method == "GET":
                self.reply(200, store.get(username, self.path.rsplit("/", 1)[1]))
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
                store.sessions.pop(token, None)
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
                if args.user not in store.accounts:
                    raise ValueError("unknown configured user")
                store._scope(args.user, args.source_id, args.job_id)
                report = build_report(read_observations(args.input, args.source_id), limit=100)
                metadata = store.save(
                    args.user,
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
