"""Bounded AF_UNIX messages with kernel peer credentials; fixed private endpoints."""

import json
import os
import pwd
import socket
import stat
import struct
import time
from pathlib import Path

from research.private_service.limits import MAX_CHILD_INPUT, MAX_CHILD_OUTPUT, remaining
from research.private_service.protocol import parse, require

RUNTIME = Path("/run/aa-private")
SECURE = Path("/var/lib/aa-private/secure")


def guard_healthy():
    p = RUNTIME / "heartbeat"
    item = p.lstat()
    require(
        item.st_uid == 0 and stat.S_ISREG(item.st_mode) and item.st_mode & 0o022 == 0,
        503,
        "HOST_GUARD_CLOSED",
    )
    age = time.monotonic_ns() - int(p.read_text())
    require(not (RUNTIME / "ABORT").exists() and 0 <= age < 2500000000, 503, "HOST_GUARD_CLOSED")


def uid(name):
    return pwd.getpwnam(name).pw_uid


def peer(channel):
    return struct.unpack("3i", channel.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))[1]


def receive(channel, maximum, seconds=2):
    deadline = time.monotonic() + seconds

    def take(n):
        result = bytearray()
        while len(result) < n:
            left = deadline - time.monotonic()
            require(left > 0, 503, "IPC_TIMEOUT")
            channel.settimeout(left)
            chunk = channel.recv(n - len(result))
            require(bool(chunk), 503, "IPC_TRUNCATED")
            result.extend(chunk)
        return bytes(result)

    size = struct.unpack("!I", take(4))[0]
    require(0 < size <= maximum, 413, "IPC_LIMIT")
    return parse(take(size))


def send(channel, value, maximum):
    raw = json.dumps(value, allow_nan=False).encode()
    require(len(raw) <= maximum, 413, "IPC_LIMIT")
    channel.sendall(struct.pack("!I", len(raw)) + raw)


def call(name, value, expected_uid, seconds=2, output=MAX_CHILD_OUTPUT):
    path = RUNTIME / (name + ".sock")
    item = path.lstat()
    require(stat.S_ISSOCK(item.st_mode) and item.st_uid in (0, expected_uid), 503, "IPC_PATH")
    require(RUNTIME.stat().st_uid == 0 and RUNTIME.stat().st_mode & 0o022 == 0, 503, "IPC_PATH")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
        channel.settimeout(seconds)
        channel.connect(str(path))
        # The listener is created by systemd/PID1, then inherited by a dedicated
        # service UID. SO_PEERCRED on this side therefore authenticates PID1/root.
        # The server authenticates the actual connecting UID on its accepted FD.
        require(peer(channel) == 0, 503, "IPC_PEER")
        send(channel, value, MAX_CHILD_INPUT)
        result = receive(channel, output, seconds=seconds)
        require(result.get("ok") is True, 503, "IPC_COMPONENT_FAILED")
        return result["value"]


def component(operation, value):
    require(operation in ("verify", "report"), 503, "COMPONENT_FORBIDDEN")
    name = "verifier" if operation == "verify" else "signer"
    return call(name, value, uid("aa-" + name), seconds=remaining())


def serve(name, allowed, handler, output=MAX_CHILD_OUTPUT):
    # systemd owns the listener and its immutable socket ACL; never unlink paths.
    require(int(os.environ.get("LISTEN_FDS", "0")) == 1, 503, "SOCKET_ACTIVATION_REQUIRED")
    with socket.socket(fileno=3) as listener:
        while True:
            channel, _ = listener.accept()
            with channel:
                channel.settimeout(2 if name in ("signer", "verifier", "control") else 150)
                try:
                    require(peer(channel) in allowed, 403, "IPC_PEER")
                    data = receive(channel, MAX_CHILD_INPUT)
                    value = handler(data)
                    send(channel, {"ok": True, "value": value}, output)
                except Exception:  # noqa: BLE001 - fixed error frame; never payload/exception text
                    try:
                        send(channel, {"ok": False}, 128)
                    except OSError:
                        pass
