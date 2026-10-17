"""Single-worker HTTPS reverse-proxy entry point, independent of a server package.

Run with a production WSGI server bound only to the configured private Unix
socket (or, explicitly, loopback). One sync worker, one thread, no preload: the
Store's local lease and in-memory sessions intentionally forbid shared workers.
The proxy authenticates its transport with a private random token. That token
does not authenticate an end user; synthetic AA login remains mandatory.
"""

from __future__ import annotations

import atexit
import hmac
import os
import re
import socket
from collections.abc import Callable
from email.message import Message
from http import HTTPStatus
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from agent_authority.browser_contracts import Problem
from agent_authority.browser_http import BrowserRoutes, HTTPProfile, response_headers
from agent_authority.browser_service import Store
from agent_authority.browser_support import json_bytes, private_file


class WSGIRequest(BrowserRoutes):
    def __init__(self, app: BrowserWSGI, environ: dict[str, Any]):
        self.server = SimpleNamespace(store=app.store, profile=app.profile)
        self.environ = environ
        self.proxy_token = app.proxy_token
        self.transport = app.transport
        self.path = environ.get("RAW_URI", environ.get("PATH_INFO", ""))
        self.headers = Message()
        for name, value in environ.items():
            if name.startswith("HTTP_"):
                self.headers[name[5:].replace("_", "-")] = value
        for name in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            if name in environ:
                self.headers[name.replace("_", "-")] = environ[name]
        self.rfile = environ["wsgi.input"]

    def boundary(self) -> None:
        peer = self.environ.get("REMOTE_ADDR", "")
        if self.transport == "unix":
            local = getattr(self.environ.get("gunicorn.socket"), "family", None) == socket.AF_UNIX
        else:
            local = peer in {"127.0.0.1", "::1"}
        if not local or not hmac.compare_digest(
            self.headers.get("X-AA-Proxy-Token", "").encode("utf-8"),
            self.proxy_token.encode("ascii"),
        ):
            raise Problem(403, "PROXY_FORBIDDEN")
        if self.environ.get("wsgi.multiprocess") or self.environ.get("wsgi.multithread"):
            raise Problem(503, "SINGLE_INSTANCE_REQUIRED")
        # RAW_URI preserves encoded paths that PATH_INFO would silently decode.
        if (
            self.environ.get("SCRIPT_NAME", "")
            or self.environ.get("QUERY_STRING", "")
            or self.path != self.environ.get("PATH_INFO", "")
        ):
            raise Problem(404, "NOT_FOUND")
        # WSGI servers may join duplicate headers with commas. These fields do
        # not have legitimate comma-list syntax in this application's contract.
        for name in ("Cookie", "Authorization", "X-CSRF-Token", "Content-Type"):
            if "," in self.headers.get(name, ""):
                raise Problem(400, "AMBIGUOUS_HEADERS")
        super().boundary()

    def reply(
        self,
        status: int,
        value: Any,
        content_type: str = "application/json; charset=utf-8",
        cookie: str | None = None,
    ) -> None:
        self.raw = value if isinstance(value, bytes) else json_bytes(value)
        self.status = status
        self.response_headers = response_headers(content_type, len(self.raw), cookie)


class BrowserWSGI:
    def __init__(
        self, store: Store, profile: HTTPProfile, proxy_token: str, transport: str = "unix"
    ):
        if not profile.secure or not re.fullmatch(r"[A-Za-z0-9_-]{43,128}", proxy_token):
            raise ValueError("explicit HTTPS profile and strong proxy credential required")
        if transport not in {"unix", "loopback"}:
            raise ValueError("private proxy transport required")
        self.store = store
        self.profile = profile
        self.proxy_token = proxy_token
        self.transport = transport

    def __call__(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> list[bytes]:
        request = WSGIRequest(self, environ)
        method = environ.get("REQUEST_METHOD", "")
        request.handle_route(method)
        start_response(
            f"{request.status} {HTTPStatus(request.status).phrase}", request.response_headers
        )
        return [request.raw]

    def close(self) -> None:
        self.store.close()


def create_app() -> BrowserWSGI:
    """Fail closed unless the operator supplies every deployment boundary."""
    profile = HTTPProfile(
        os.environ["AA_BROWSER_ORIGIN"], os.environ["AA_BROWSER_PREFIX"], secure=True
    )
    token = (
        private_file(Path(os.environ["AA_BROWSER_PROXY_TOKEN_FILE"]), 256).decode("ascii").strip()
    )
    transport = os.environ["AA_BROWSER_PROXY_TRANSPORT"]
    if not re.fullmatch(r"[A-Za-z0-9_-]{43,128}", token) or transport not in {"unix", "loopback"}:
        raise ValueError("invalid private proxy configuration")
    store = Store(Path(os.environ["AA_BROWSER_STATE"]))
    app = BrowserWSGI(store, profile, token, transport)
    atexit.register(app.close)
    return app
