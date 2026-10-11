"""Receiver-assigned local sessions; no labels are used as sender evidence."""

import base64
import hashlib
import json
import math
import sys
import time
import uuid
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Self

from lab.origin.transport import Frame, Transport, Unavailable, UnsupportedTransport

MAX_MESSAGE = 2048


def _transport(platform: str) -> Transport:
    if platform == "darwin":
        from lab.origin.macos import MachTransport

        return MachTransport()
    return UnsupportedTransport(platform)


def encode_message(challenge: dict[str, Any], message: bytes, sequence: int = 1) -> bytes:
    """Client framing only; caller labels cannot provide OS evidence."""
    if type(message) is not bytes or not 0 < len(message) <= MAX_MESSAGE:
        raise ValueError("invalid message length")
    return json.dumps(
        {
            "kind": "message",
            "protocol": 1,
            "session": challenge["session"],
            "challenge": challenge["challenge"],
            "sequence": sequence,
            "message": base64.b64encode(message).decode("ascii"),
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def _packet(raw: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate field")
            result[key] = value
        return result

    data = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(data, dict) or type(data.get("protocol")) is not int or data["protocol"] != 1:
        raise ValueError("invalid protocol")
    expected = {"kind", "protocol"}
    if data.get("kind") == "message":
        expected |= {"session", "challenge", "sequence", "message"}
    elif data.get("kind") != "hello":
        raise ValueError("invalid kind")
    if set(data) != expected:
        raise ValueError("invalid fields")
    return data


@dataclass
class _Session:
    identifier: str
    challenge: str
    sender_token: bytes
    deadline: float
    consumed: bool = False


class OriginReceiver:
    """Explicit reception API, separate from Lab, submit, assess and effects.

    Task labels are receiver configuration, not authenticated human instructions.
    A local protocol session is not a Codex/Grok conversation or a model identity.
    """

    def __init__(self, task_id: str, *, lifetime_seconds: float = 30) -> None:
        if not isinstance(task_id, str) or not task_id.strip() or len(task_id) > 200:
            raise ValueError("invalid task assignment")
        if (
            type(lifetime_seconds) not in (int, float)
            or not math.isfinite(lifetime_seconds)
            or not 0 < lifetime_seconds <= 30
        ):
            raise ValueError("invalid lifetime")
        self.task_id = task_id
        self._lifetime = lifetime_seconds
        self._sessions: dict[str, _Session] = {}
        self._initial_failure: str | None = None
        self._native: Transport
        try:
            self._native = _transport(sys.platform)
        except (Unavailable, OSError, AttributeError):
            self._native = UnsupportedTransport(sys.platform)
            self._initial_failure = "native_initialization_failed"
        self._closed = False

    @property
    def endpoint(self) -> str:
        return self._native.endpoint

    def _result(self, reason: str) -> dict[str, Any]:
        return {
            "schema_version": "origin-receipt-v1",
            "status": "UNBEKANNT",
            "reason": reason,
            "transport": self._native.name,
            "source_authenticated": False,
            "source_scope": "immediate_kernel_message_sender_only",
            "author_identity": "UNBEKANNT",
            "model_identity": "UNBEKANNT",
            "conversation_identity": "UNBEKANNT",
            "receiver_assignment": {
                "task_id": self.task_id,
                "basis": "receiver_configuration",
                "task_author_authenticated": False,
            },
            "rights_inherited": False,
            "D012": "monitoring",
        }

    def _evaluate(self, frame: Frame, data: dict[str, Any]) -> dict[str, Any]:
        session_id = data["session"]
        if not isinstance(session_id, str) or session_id not in self._sessions:
            return self._result("unknown_local_session")
        session = self._sessions[session_id]
        if frame.audit_token != session.sender_token:
            return self._result("sender_instance_changed")
        if time.monotonic() >= session.deadline:
            return self._result("expired_local_session")
        if data["challenge"] != session.challenge:
            return self._result("wrong_challenge")
        if type(data["sequence"]) is not int or data["sequence"] != 1:
            return self._result("invalid_sequence")
        if session.consumed:
            return self._result("replayed_local_session")
        if not isinstance(data["message"], str):
            return self._result("invalid_message")
        message = base64.b64decode(data["message"], validate=True)
        if not 0 < len(message) <= MAX_MESSAGE:
            return self._result("invalid_message")
        from lab.origin.macos import sender_info

        sender = sender_info(frame.audit_token)
        # Consume only after complete validation. The bytes remain immutable here.
        session.consumed = True
        return {
            **self._result("kernel_sender_and_fresh_local_assignment"),
            "status": "BELEGT",
            "source_authenticated": True,
            "sender": sender,
            "audit_token_sha256": hashlib.sha256(frame.audit_token).hexdigest(),
            "receiver_session": session.identifier,
            "session_bound_to_sender": True,
            "message": {
                "sha256": hashlib.sha256(message).hexdigest(),
                "length": len(message),
                "wire_sha256": hashlib.sha256(frame.data).hexdigest(),
            },
            "freshness": "receiver_challenge_single_use_monotonic_deadline",
        }

    def receive(self, *, timeout_ms: int = 5000) -> dict[str, Any]:
        if type(timeout_ms) is not int or not 1 <= timeout_ms <= 30_000:
            raise ValueError("invalid timeout")
        if self._closed:
            return self._result("receiver_closed")
        if self._initial_failure:
            return self._result(self._initial_failure)
        frame = None
        reception_deadline = time.monotonic() + timeout_ms / 1000
        try:
            # Bounded control traffic; eight in-memory session slots, no daemon.
            for _ in range(9):
                remaining_ms = int((reception_deadline - time.monotonic()) * 1000)
                if remaining_ms <= 0:
                    return self._result("reception_timeout")
                frame = self._native.receive(min(timeout_ms, remaining_ms))
                if type(frame.audit_token) is not bytes or len(frame.audit_token) != 32:
                    result = self._result("missing_OS_message_evidence")
                else:
                    data = _packet(frame.data)
                    if data["kind"] == "hello":
                        if len(self._sessions) >= 8:
                            result = self._result("session_capacity")
                        else:
                            identifier, challenge = uuid.uuid4().hex, uuid.uuid4().hex
                            self._sessions[identifier] = _Session(
                                identifier,
                                challenge,
                                frame.audit_token,
                                time.monotonic() + self._lifetime,
                            )
                            self._native.reply(
                                frame,
                                json.dumps(
                                    {
                                        "kind": "challenge",
                                        "protocol": 1,
                                        "session": identifier,
                                        "challenge": challenge,
                                    }
                                ).encode(),
                            )
                            frame = None
                            continue
                    else:
                        result = self._evaluate(frame, data)
                self._native.reply(frame, json.dumps(result).encode())
                frame = None
                return result
            return self._result("control_traffic_limit")
        except (Unavailable, ValueError, UnicodeError, OSError, AttributeError):
            if frame is not None:
                self._native.discard(frame)
            return self._result("unavailable_or_invalid_message")

    def close(self) -> None:
        self._closed = True
        self._sessions.clear()
        self._native.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
