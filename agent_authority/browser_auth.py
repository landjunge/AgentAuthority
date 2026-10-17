"""Synthetic, process-local implementation of the server access-control port.

Not SSO, not distributed identity. Passwords/scopes come only from operator
configuration. Sessions hold subjects; rights are resolved on every use.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
import threading
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from agent_authority.browser_contracts import (
    ADAPTERS,
    CONTRACT_VERSION,
    Principal,
    Problem,
    Scope,
    Session,
)
from agent_authority.browser_support import check_state, json_bytes, parse_json, private_file
from agent_authority.observations import TOKEN

SESSION_SECONDS = 1800


def password_hash(password: str, salt: bytes) -> str:
    return hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1).hex()


def init_synthetic(path: Path) -> dict[str, str]:
    """New private state only; explicit adapter bindings in configuration v2."""
    path.mkdir(mode=0o700)
    os.chmod(path, 0o700)
    accounts = []
    credentials = {}
    for name in ("alice", "bob"):
        password, salt = secrets.token_urlsafe(24), secrets.token_bytes(16)
        credentials[name] = password
        accounts.append(
            {
                "id": name,
                "synthetic": True,
                "salt": salt.hex(),
                "passwordHash": password_hash(password, salt),
                "scopes": [
                    {
                        "sourceId": f"synthetic-{name}",
                        "jobId": f"test-{name}",
                        "adapters": ["observations", "report"],
                    },
                    {
                        "sourceId": f"synthetic-private-{name}",
                        "jobId": hashlib.sha256(
                            f"aa-browser-synthetic-{name}".encode()
                        ).hexdigest()[:32],
                        "adapters": ["private-verification"],
                    },
                ],
            }
        )
    config = {"schema": "aa-browser-synthetic-config-v2", "synthetic": True, "accounts": accounts}
    with (path / "config.json").open("xb") as target:
        os.chmod(target.name, 0o600)
        target.write(json_bytes(config))
    return credentials


@dataclass(frozen=True)
class Account:
    principal: Principal
    salt: bytes
    password_hash: str


def _scope(data: Any, subject: str, legacy: bool) -> Scope:
    expected = {"sourceId", "jobId"} if legacy else {"sourceId", "jobId", "adapters"}
    if (
        not isinstance(data, dict)
        or set(data) != expected
        or any(
            not isinstance(data[k], str) or not TOKEN.fullmatch(data[k])
            for k in ("sourceId", "jobId")
        )
    ):
        raise ValueError("invalid source/job scope")
    if legacy:
        # Only the two exact pairs created by v1 init have an unambiguous adapter
        # contract. Do not guess the meaning of custom legacy source names.
        pair = data["sourceId"], data["jobId"]
        private_job = hashlib.sha256(f"aa-browser-synthetic-{subject}".encode()).hexdigest()[:32]
        if pair == (f"synthetic-{subject}", f"test-{subject}"):
            adapters = ["observations", "report"]
        elif pair == (f"synthetic-private-{subject}", private_job):
            adapters = ["private-verification"]
        else:
            raise ValueError("legacy scope needs explicit v2 adapter binding")
    else:
        adapters = data["adapters"]
    if (
        not isinstance(adapters, list)
        or not 1 <= len(adapters) <= len(ADAPTERS)
        or any(not isinstance(a, str) or a not in ADAPTERS for a in adapters)
        or len(set(adapters)) != len(adapters)
    ):
        raise ValueError("invalid adapter binding")
    return Scope(data["sourceId"], data["jobId"], tuple(adapters))


class LocalAccessControl:
    contract_version = CONTRACT_VERSION

    def __init__(self, path: Path):
        check_state(path)
        config = parse_json(private_file(path / "config.json", 65536))
        if (
            not isinstance(config, dict)
            or set(config) != {"schema", "synthetic", "accounts"}
            or config["schema"]
            not in ("aa-browser-synthetic-config-v1", "aa-browser-synthetic-config-v2")
            or config["synthetic"] is not True
            or not isinstance(config["accounts"], list)
            or not 1 <= len(config["accounts"]) <= 10
        ):
            raise ValueError("only explicit synthetic configuration supported")
        legacy = config["schema"] == "aa-browser-synthetic-config-v1"
        self._accounts: dict[str, Account] = {}
        for data in config["accounts"]:
            if (
                not isinstance(data, dict)
                or set(data) != {"id", "synthetic", "salt", "passwordHash", "scopes"}
                or data["synthetic"] is not True
                or not isinstance(data["id"], str)
                or not TOKEN.fullmatch(data["id"])
                or data["id"] in self._accounts
                or not isinstance(data["salt"], str)
                or not re.fullmatch(r"[a-f0-9]{32}", data["salt"])
                or not isinstance(data["passwordHash"], str)
                or not re.fullmatch(r"[a-f0-9]{128}", data["passwordHash"])
                or not isinstance(data["scopes"], list)
                or not 1 <= len(data["scopes"]) <= 20
            ):
                raise ValueError("invalid synthetic account")
            scopes = tuple(_scope(s, data["id"], legacy) for s in data["scopes"])
            if len({(s.source_id, s.job_id) for s in scopes}) != len(scopes):
                raise ValueError("duplicate scope")
            self._accounts[data["id"]] = Account(
                Principal(data["id"], scopes), bytes.fromhex(data["salt"]), data["passwordHash"]
            )
        self._sessions: dict[str, tuple[str, str, float]] = {}
        self._failed_logins: list[float] = []
        self._dummy_salt = secrets.token_bytes(16)
        self._dummy_hash = password_hash(secrets.token_urlsafe(24), self._dummy_salt)
        self._lock = threading.RLock()
        self._closed = False

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._sessions.clear()

    def refresh(self, principal: Principal) -> Principal:
        with self._lock:
            token = principal.session_id
            if self._closed or not isinstance(token, str):
                raise Problem(401, "AUTH_REQUIRED")
            session = self._sessions.get(token)
            if session is None or session[2] <= time.monotonic():
                self._sessions.pop(token, None)
                raise Problem(401, "AUTH_REQUIRED")
            if session[0] != principal.subject:
                raise Problem(401, "AUTH_REQUIRED")
            account = self._accounts.get(principal.subject)
            if account is None:
                raise Problem(401, "AUTH_REQUIRED")
            return replace(account.principal, session_id=token)

    def _issue_session(self, account: Account, now: float) -> Session:
        """Called under the access-control lock by fixed local entry points."""
        if self._closed:
            raise Problem(401, "AUTH_REQUIRED")
        self._sessions = {k: v for k, v in self._sessions.items() if v[2] > now}
        if len(self._sessions) >= 128:
            raise Problem(429, "SESSION_LIMIT")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        self._sessions[token] = (account.principal.subject, csrf, now + SESSION_SECONDS)
        return Session(token, replace(account.principal, session_id=token), csrf)

    def for_operator(self, subject: str) -> Principal:
        """Trusted local CLI bootstrap only; never an API or AccessControl port.

        The operator already controls this process and its private configuration.
        Use the same bounded, expiring session checks as browser authentication.
        """
        with self._lock:
            account = self._accounts.get(subject)
            if account is None or self._closed:
                raise Problem(401, "AUTH_REQUIRED")
            return self._issue_session(account, time.monotonic()).principal

    def authorize(self, principal: Principal, source: str, job: str, adapter: str) -> Principal:
        principal = self.refresh(principal)
        if not any(
            s.source_id == source and s.job_id == job and adapter in s.adapters
            for s in principal.scopes
        ):
            raise Problem(403, "SCOPE_FORBIDDEN")
        return principal

    def authenticate(self, authorization: str) -> Session:
        with self._lock:
            if self._closed:
                raise Problem(401, "AUTH_REQUIRED")
            now = time.monotonic()
            self._failed_logins = [t for t in self._failed_logins if now - t < 60]
            if len(self._failed_logins) >= 12:
                raise Problem(429, "LOGIN_RATE_LIMIT")
            try:
                if not authorization.startswith("Basic ") or len(authorization) > 1024:
                    raise ValueError("basic required")
                decoded = base64.b64decode(authorization[6:], validate=True).decode("utf-8")
                username, password = decoded.split(":", 1)
                if len(username) > 128 or not 1 <= len(password) <= 256:
                    raise ValueError("credential limit")
            except (ValueError, UnicodeError):
                self._failed_logins.append(now)
                raise Problem(401, "AUTH_REQUIRED") from None
            account = self._accounts.get(username)
            salt = account.salt if account else self._dummy_salt
            expected = account.password_hash if account else self._dummy_hash
            candidate = password_hash(password, salt)
            if not hmac.compare_digest(expected, candidate) or account is None:
                self._failed_logins.append(now)
                raise Problem(401, "AUTH_REQUIRED")
            return self._issue_session(account, now)

    def resolve(self, cookie: str) -> Session:
        with self._lock:
            tokens = [v[11:] for v in cookie.split("; ") if v.startswith("aa_session=")]
            if len(tokens) != 1 or len(tokens[0]) > 128:
                raise Problem(401, "AUTH_REQUIRED")
            token = tokens[0]
            value = self._sessions.get(token)
            if value is None or value[2] <= time.monotonic():
                self._sessions.pop(token, None)
                raise Problem(401, "AUTH_REQUIRED")
            return Session(token, self.refresh(Principal(value[0], (), token)), value[1])

    def revoke(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)
