"""Common transport boundary. Serialized receipts are never measurement inputs."""

from dataclasses import dataclass
from typing import Protocol


class Unavailable(Exception):
    """A bounded native reception failure, containing no message or environment."""


@dataclass(frozen=True)
class Frame:
    data: bytes
    audit_token: bytes
    reply_port: int


class Transport(Protocol):
    name: str
    endpoint: str

    def receive(self, timeout_ms: int) -> Frame: ...

    def reply(self, frame: Frame, data: bytes) -> None:
        """Take ownership of the reply right, including cleanup on failure."""
        ...

    def discard(self, frame: Frame) -> None: ...

    def close(self) -> None: ...


class UnsupportedTransport:
    """Explicit extension point, with no claimed Linux/Windows implementation."""

    endpoint = ""

    def __init__(self, platform: str) -> None:
        self.name = f"{platform}-not-implemented"

    def receive(self, timeout_ms: int) -> Frame:
        raise Unavailable("unsupported_platform")

    def reply(self, frame: Frame, data: bytes) -> None:
        raise Unavailable("unsupported_platform")

    def discard(self, frame: Frame) -> None:
        pass

    def close(self) -> None:
        pass
