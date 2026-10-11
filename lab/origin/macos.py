"""Bounded inline Mach messages with the kernel's per-message audit trailer.

Uses public installed SDK interfaces. No task_for_pid, signal, entitlement,
launch-agent installation, application credentials or executable launch.
"""

import ctypes as c
import json
import struct
import uuid
from typing import Any

from lab.origin.transport import Frame, Unavailable

MAX_FRAME = 4096
MESSAGE_ID = 0x41414F52
_HEADER = struct.Struct("=6I")
_LENGTH = struct.Struct("=I")
_AUDIT_TRAILER_SIZE = 52


class _AuditToken(c.Structure):
    _fields_ = [("values", c.c_uint32 * 8)]


class MachTransport:
    name = "macos-mach-audit-trailer"

    def __init__(self, endpoint: str | None = None, *, register: bool = True) -> None:
        self.endpoint = endpoint or f"local.agent-authority.origin.{uuid.uuid4().hex}"
        if not self.endpoint.isascii() or len(self.endpoint) >= 128 or not self.endpoint:
            raise ValueError("invalid endpoint")
        self._lib = c.CDLL("/usr/lib/libSystem.B.dylib")
        self._task = c.c_uint32.in_dll(self._lib, "mach_task_self_").value
        self._bootstrap = c.c_uint32.in_dll(self._lib, "bootstrap_port").value
        signatures = {
            "mach_port_allocate": [c.c_uint32, c.c_int, c.POINTER(c.c_uint32)],
            "mach_port_insert_right": [c.c_uint32, c.c_uint32, c.c_uint32, c.c_int],
            "mach_port_destroy": [c.c_uint32, c.c_uint32],
            "mach_port_deallocate": [c.c_uint32, c.c_uint32],
            "bootstrap_register": [c.c_uint32, c.c_char_p, c.c_uint32],
            "bootstrap_look_up": [c.c_uint32, c.c_char_p, c.POINTER(c.c_uint32)],
            "mach_msg": [c.c_void_p, *([c.c_uint32] * 6)],
        }
        for name, args in signatures.items():
            function = getattr(self._lib, name)
            function.argtypes, function.restype = args, c.c_int
        self._lib.mach_msg_destroy.argtypes = [c.c_void_p]
        self._lib.mach_msg_destroy.restype = None
        self._port = self._allocate()
        self._registered = False
        self._closed = False
        try:
            self._check(self._lib.mach_port_insert_right(self._task, self._port, self._port, 20))
            if register:
                self._check(
                    self._lib.bootstrap_register(
                        self._bootstrap, self.endpoint.encode(), self._port
                    )
                )
                self._registered = True
        except Unavailable:
            self.close()
            raise

    @staticmethod
    def _check(code: int) -> None:
        if code != 0:
            raise Unavailable("native_api_failed")

    def _allocate(self) -> int:
        port = c.c_uint32()
        self._check(self._lib.mach_port_allocate(self._task, 1, c.byref(port)))
        return port.value

    def _send(self, destination: int, data: bytes, reply_port: int = 0) -> None:
        if not 0 < len(data) <= MAX_FRAME:
            raise ValueError("invalid frame length")
        size = (28 + len(data) + 3) & ~3
        bits = (19 | (21 << 8)) if reply_port else 18
        buffer = c.create_string_buffer(size)
        wire = _HEADER.pack(bits, size, destination, reply_port, 0, MESSAGE_ID)
        wire += _LENGTH.pack(len(data)) + data
        c.memmove(buffer, wire, len(wire))
        self._check(self._lib.mach_msg(buffer, 1 | 0x10, size, 0, 0, 2000, 0))

    def _receive(self, port: int, timeout_ms: int) -> Frame:
        if type(timeout_ms) is not int or not 1 <= timeout_ms <= 30_000:
            raise ValueError("invalid timeout")
        buffer = c.create_string_buffer(28 + MAX_FRAME + 256)
        # SDK: RCV_MSG | RCV_TIMEOUT | TRAILER_ELEMENTS(TRAILER_AUDIT).
        self._check(
            self._lib.mach_msg(buffer, 2 | 0x100 | (3 << 24), 0, len(buffer), port, timeout_ms, 0)
        )
        bits, size, reply, _, _, message_id = _HEADER.unpack_from(buffer.raw)
        offset = (size + 3) & ~3
        try:
            if bits & 0x80000000 or message_id != MESSAGE_ID:
                raise Unavailable("unsupported_message")
            if not 28 <= size <= 28 + MAX_FRAME or offset + _AUDIT_TRAILER_SIZE > len(buffer):
                raise Unavailable("invalid_native_size")
            length = _LENGTH.unpack_from(buffer.raw, 24)[0]
            if not 0 < length <= MAX_FRAME or ((28 + length + 3) & ~3) != size:
                raise Unavailable("invalid_native_size")
            trailer_type, trailer_size = struct.unpack_from("=2I", buffer.raw, offset)
            if trailer_type != 0 or trailer_size != _AUDIT_TRAILER_SIZE:
                raise Unavailable("missing_audit_trailer")
            token = bytes(buffer.raw[offset + 20 : offset + 52])
            if not sender_info(token)["pid"]:
                raise Unavailable("invalid_audit_sender")
            return Frame(bytes(buffer.raw[28 : 28 + length]), token, reply)
        except (Unavailable, OSError, AttributeError):
            self._lib.mach_msg_destroy(buffer)
            raise

    def receive(self, timeout_ms: int) -> Frame:
        if self._closed:
            raise Unavailable("receiver_closed")
        return self._receive(self._port, timeout_ms)

    def reply(self, frame: Frame, data: bytes) -> None:
        if not frame.reply_port:
            raise Unavailable("missing_reply_port")
        try:
            self._send(frame.reply_port, data)
        except (Unavailable, ValueError, OSError, AttributeError):
            self.discard(frame)
            raise

    def discard(self, frame: Frame) -> None:
        if frame.reply_port:
            self._lib.mach_port_deallocate(self._task, frame.reply_port)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._registered:
            self._lib.bootstrap_register(self._bootstrap, self.endpoint.encode(), 0)
        self._lib.mach_port_destroy(self._task, self._port)


def sender_info(raw_token: bytes) -> dict[str, int]:
    if type(raw_token) is not bytes or len(raw_token) != 32:
        raise Unavailable("invalid_audit_sender")
    token = _AuditToken.from_buffer_copy(raw_token)
    lib = c.CDLL("/usr/lib/libbsm.dylib")
    result: dict[str, int] = {}
    for key, name in {
        "pid": "audit_token_to_pid",
        "pid_version": "audit_token_to_pidversion",
        "uid": "audit_token_to_euid",
        "os_audit_session": "audit_token_to_asid",
    }.items():
        function = getattr(lib, name)
        function.argtypes, function.restype = [_AuditToken], c.c_uint32
        result[key] = function(token)
    if result["pid"] == 0 or result["pid_version"] == 0:
        raise Unavailable("invalid_audit_sender")
    return result


class MachClient:
    """Immediate sender. Relaying content never authenticates its original author."""

    def __init__(self, endpoint: str) -> None:
        # Private reply port; no additional namespace registration.
        self._native = MachTransport(register=False)
        destination = c.c_uint32()
        try:
            self._native._check(
                self._native._lib.bootstrap_look_up(
                    self._native._bootstrap, endpoint.encode(), c.byref(destination)
                )
            )
        except (Unavailable, UnicodeError):
            self._native.close()
            raise
        self._destination = destination.value
        self._closed = False

    def request(self, data: bytes) -> Frame:
        self._native._send(self._destination, data, self._native._port)
        return self._native.receive(5000)

    def hello(self) -> dict[str, Any]:
        frame = self.request(b'{"kind":"hello","protocol":1}')
        result = json.loads(frame.data)
        if not isinstance(result, dict):
            raise Unavailable("invalid_challenge")
        return result

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._native._lib.mach_port_deallocate(self._native._task, self._destination)
        self._native.close()
