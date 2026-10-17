"""Shared HTTP routes and explicit transport profiles for the browser module.

The HTTPS profile assumes a separately authenticated local reverse proxy. It
never derives authority, TLS state or identity from forwarded request headers.
"""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from agent_authority.browser_auth import SESSION_SECONDS
from agent_authority.browser_contracts import Problem
from agent_authority.browser_service import status_document
from agent_authority.browser_support import MAX_BODY, parse_json


def response_headers(
    content_type: str, length: int, cookie: str | None = None
) -> list[tuple[str, str]]:
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(length)),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
        ("Referrer-Policy", "no-referrer"),
        ("Cross-Origin-Resource-Policy", "same-origin"),
        (
            "Content-Security-Policy",
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'",
        ),
        ("Permissions-Policy", "camera=(), microphone=(), geolocation=()"),
    ]
    if cookie:
        headers.append(("Set-Cookie", cookie))
    return headers


@dataclass(frozen=True)
class HTTPProfile:
    origin: str
    prefix: str = "/"
    secure: bool = False

    def __post_init__(self) -> None:
        parsed = urlsplit(self.origin)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path
            or parsed.query
            or parsed.fragment
            or self.origin != f"{parsed.scheme}://{parsed.netloc}"
            or not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?(?::[0-9]{1,5})?", parsed.netloc)
            or not re.fullmatch(r"/(?:[a-z][a-z0-9-]*/)*", self.prefix)
        ):
            raise ValueError("invalid fixed HTTP profile")
        try:
            _ = parsed.port
        except ValueError:
            raise ValueError("invalid fixed HTTP profile") from None
        if self.secure:
            if parsed.scheme != "https":
                raise ValueError("HTTPS required")
        elif parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or self.prefix != "/":
            raise ValueError("plain HTTP is restricted to local loopback")

    @property
    def expected_host(self) -> str:
        return urlsplit(self.origin).netloc

    def local_path(self, path: str) -> str:
        if (
            not path.startswith(self.prefix)
            or "?" in path
            or "#" in path
            or "%" in path
            or "\\" in path
            or len(path) > 200
        ):
            raise Problem(404, "NOT_FOUND")
        return "/" + path[len(self.prefix) :]

    def cookie(self, token: str, max_age: int) -> str:
        secure = "; Secure" if self.secure else ""
        return (
            f"aa_session={token}; HttpOnly; SameSite=Strict; Path={self.prefix}; "
            f"Max-Age={max_age}{secure}"
        )


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


class BrowserRoutes:
    def boundary(self) -> None:
        if self.headers.get_all("Host", []) != [self.server.profile.expected_host]:
            raise Problem(403, "HOST_FORBIDDEN")
        origins = self.headers.get_all("Origin", [])
        if origins and origins != [self.server.profile.origin]:
            raise Problem(403, "ORIGIN_FORBIDDEN")
        local_path = self.server.profile.local_path(self.path)
        fetch_sites = self.headers.get_all("Sec-Fetch-Site", [])
        # The Help Center may navigate to this separate origin. Only the public
        # document shell can accept that top-level transition; no session is
        # resolved here, and its subsequent API requests must be same-origin.
        external_landing = (
            self.request_method == "GET"
            and local_path == "/"
            and not origins
            and fetch_sites in (["same-site"], ["cross-site"])
            and self.headers.get_all("Sec-Fetch-Mode", []) == ["navigate"]
            and self.headers.get_all("Sec-Fetch-Dest", []) == ["document"]
        )
        if fetch_sites not in ([], ["same-origin"], ["none"]) and not external_landing:
            raise Problem(403, "ORIGIN_FORBIDDEN")
        for header in ("Cookie", "Authorization", "X-CSRF-Token", "Content-Type"):
            if len(self.headers.get_all(header, [])) > 1:
                raise Problem(400, "AMBIGUOUS_HEADERS")
        self.path = local_path

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
            self.request_method = method
            self.boundary()
            if method not in {"GET", "POST"}:
                raise Problem(405, "METHOD_NOT_ALLOWED")
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
                    cookie=self.server.profile.cookie(session.token, SESSION_SECONDS),
                )
                return
            session = store.access.resolve(self.headers.get("Cookie", ""))
            principal = session.principal
            if method == "POST" and not hmac.compare_digest(
                self.headers.get("X-CSRF-Token", "").encode("utf-8"), session.csrf.encode("ascii")
            ):
                raise Problem(403, "CSRF_REQUIRED")
            if self.path == "/api/hilfezentrum/demo" and method == "POST":
                from agent_authority.browser_handoff import synthetic_context

                self.reply(200, synthetic_context(store, principal, self.body()))
            elif self.path == "/api/hilfezentrum/context" and method == "POST":
                self.body()
                raise Problem(409, "HILFEZENTRUM_IDENTITY_CONTRACT_REQUIRED")
            elif self.path == "/api/session" and method == "GET":
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
                    cookie=self.server.profile.cookie("", 0),
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
        except Exception:  # noqa: BLE001 - the HTTP boundary must redact backend failures.
            # Never echo input, local paths, credentials, DB errors or tracebacks.
            self.reply(500, {"status": 500, "code": "INTERNAL_ERROR"})
