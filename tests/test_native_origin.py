"""Session adversaries in memory, plus separate-process kernel reception on macOS."""

import hashlib
import json
import struct
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from lab.origin import OriginReceiver
from lab.origin import receiver as core
from lab.origin.receiver import encode_message
from lab.origin.transport import Frame, Unavailable

TOKEN = bytes(range(32))
MESSAGE = b"bounded origin observation"


class SimulatedTransport:
    """Only a unit-test seam; never counted as a native process/source measurement."""

    name = "simulation-only"
    endpoint = "memory-only"

    def __init__(self, mutate=lambda packet: packet, *, token=TOKEN):
        self.frames = [Frame(b'{"kind":"hello","protocol":1}', token, 1)]
        self.mutate, self.token = mutate, token
        self.replies = []
        self.closed = False
        self.wire = None

    def receive(self, timeout_ms):
        if not self.frames:
            raise Unavailable("no_test_frame")
        return self.frames.pop(0)

    def reply(self, frame, data):
        packet = json.loads(data)
        self.replies.append(packet)
        if packet.get("kind") == "challenge":
            body = self.mutate(json.loads(encode_message(packet, MESSAGE)))
            self.wire = json.dumps(body).encode()
            self.frames.append(Frame(self.wire, self.token, 1))

    def discard(self, frame):
        pass

    def close(self):
        self.closed = True


def simulated(monkeypatch, mutate=lambda packet: packet, *, token=TOKEN):
    transport = SimulatedTransport(mutate, token=token)
    monkeypatch.setattr(core, "_transport", lambda platform: transport)
    from lab.origin import macos

    monkeypatch.setattr(macos, "sender_info", lambda token: {"pid": 10, "pid_version": 20})
    return OriginReceiver("receiver-configured-task"), transport


def test_session_consumes_once_and_hashes_same_held_bytes(monkeypatch):
    receiver, transport = simulated(monkeypatch)
    first = receiver.receive()
    assert first["source_authenticated"] is True
    assert first["message"]["sha256"] == hashlib.sha256(MESSAGE).hexdigest()
    assert first["message"]["wire_sha256"] == hashlib.sha256(transport.wire).hexdigest()
    assert first["receiver_assignment"]["task_id"] == "receiver-configured-task"
    assert first["receiver_assignment"]["task_author_authenticated"] is False
    assert first["conversation_identity"] == first["model_identity"] == "UNBEKANNT"
    transport.frames.append(Frame(transport.wire, TOKEN, 1))
    replay = receiver.receive()
    assert replay["reason"] == "replayed_local_session"
    assert replay["source_authenticated"] is False
    assert "message" not in replay


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("session", "copied-old-session", "unknown_local_session"),
        ("session", {}, "unknown_local_session"),
        ("challenge", "copied-old-challenge", "wrong_challenge"),
        ("sequence", True, "invalid_sequence"),
        ("sequence", 2, "invalid_sequence"),
        ("message", 42, "invalid_message"),
        ("message", "!", "unavailable_or_invalid_message"),
        ("source_authenticated", True, "unavailable_or_invalid_message"),
        ("actor", "Codex", "unavailable_or_invalid_message"),
        ("audit_token", list(TOKEN), "unavailable_or_invalid_message"),
    ],
)
def test_wrong_old_or_forged_fields_never_authenticate(monkeypatch, field, value, reason):
    receiver, _ = simulated(monkeypatch, lambda packet: {**packet, field: value})
    result = receiver.receive()
    assert result["status"] == "UNBEKANNT"
    assert result["reason"] == reason
    assert result["source_authenticated"] is False
    assert result["rights_inherited"] is False
    assert "sender" not in result


def test_changed_process_instance_with_same_session_is_unknown(monkeypatch):
    receiver, transport = simulated(monkeypatch)
    original = transport.reply

    def reply(frame, data):
        original(frame, data)
        if json.loads(data).get("kind") == "challenge":
            transport.frames[-1] = Frame(transport.frames[-1].data, b"x" * 32, 1)

    transport.reply = reply
    assert receiver.receive()["reason"] == "sender_instance_changed"


def test_missing_os_evidence_never_uses_labels(monkeypatch):
    receiver, _ = simulated(monkeypatch, token=b"")
    result = receiver.receive()
    assert result["reason"] == "missing_OS_message_evidence"
    assert result["source_authenticated"] is False


def test_deadline_uses_receiver_monotonic_clock(monkeypatch):
    receiver, _ = simulated(monkeypatch)
    # Overall receive deadline is 130; local session expires at 100.5.
    receiver._lifetime = 0.5
    clock = iter([100.0, 100.0, 100.0, 101.0, 101.0])
    monkeypatch.setattr(core.time, "monotonic", lambda: next(clock))
    assert receiver.receive(timeout_ms=30_000)["reason"] == "expired_local_session"


def test_closed_receiver_does_not_reuse_session(monkeypatch):
    receiver, transport = simulated(monkeypatch)
    receiver.close()
    assert transport.closed
    assert receiver.receive()["reason"] == "receiver_closed"


@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_unimplemented_platform_is_explicitly_unknown(monkeypatch, platform):
    monkeypatch.setattr(core.sys, "platform", platform)
    with OriginReceiver("task") as receiver:
        assert receiver.endpoint == ""
        assert receiver.receive()["source_authenticated"] is False
        assert receiver.receive()["transport"] == f"{platform}-not-implemented"


def test_duplicate_json_fields_are_not_accepted():
    with pytest.raises(ValueError, match="duplicate"):
        core._packet(b'{"kind":"hello","protocol":1,"protocol":1}')


@pytest.mark.parametrize("parser_failure", [False, True])
def test_deeply_nested_wire_returns_unknown_and_discards_once(monkeypatch, parser_failure):
    receiver, transport = simulated(monkeypatch)
    wire = b"[" * 1500 + b"0" + b"]" * 1500
    assert len(wire) < 4096
    transport.frames = [Frame(wire, TOKEN, 1)]
    discarded = []
    transport.discard = discarded.append
    if parser_failure:
        # Decoder exhaustion is simulated: local Python 3.12 parses this depth.
        def exhausted(*args, **kwargs):
            raise RecursionError("decoder exhausted")

        monkeypatch.setattr(core.json, "loads", exhausted)
    result = receiver.receive()
    assert result["reason"] == "unavailable_or_invalid_message"
    assert result["source_authenticated"] is False
    assert len(discarded) == 1
    assert transport.replies == []


@pytest.mark.parametrize("failure_kind", ["challenge", "receipt"])
def test_failed_reply_has_one_cleanup_owner(monkeypatch, failure_kind):
    receiver, transport = simulated(monkeypatch)
    discarded = []
    transport.discard = discarded.append
    original = transport.reply

    def reply(frame, data):
        is_challenge = json.loads(data).get("kind") == "challenge"
        if is_challenge == (failure_kind == "challenge"):
            # Same contract as native reply: it owns the right on failure.
            transport.discard(frame)
            raise Unavailable("send_failed")
        original(frame, data)

    transport.reply = reply
    result = receiver.receive()
    assert result["reason"] == "unavailable_or_invalid_message"
    assert result["source_authenticated"] is False
    assert len(discarded) == 1


def test_concurrent_receive_cannot_validate_same_unused_session(monkeypatch):
    receiver, transport = simulated(monkeypatch)
    from lab.origin import macos

    validating, finish = threading.Event(), threading.Event()

    def sender_info(token):
        validating.set()
        assert finish.wait(timeout=5)
        return {"pid": 10, "pid_version": 20}

    monkeypatch.setattr(macos, "sender_info", sender_info)
    with ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(receiver.receive)
        try:
            assert validating.wait(timeout=5)
            transport.frames.append(Frame(transport.wire, TOKEN, 1))
            competing = receiver.receive()
            assert competing["reason"] == "receiver_busy"
            assert competing["source_authenticated"] is False
        finally:
            finish.set()
        assert pending.result(timeout=5)["source_authenticated"] is True
    assert receiver.receive()["reason"] == "replayed_local_session"


@pytest.mark.parametrize("failure", [OSError, AttributeError])
def test_native_audit_decoder_failure_destroys_received_right(monkeypatch, failure):
    import ctypes

    from lab.origin import macos

    wire = b'{"kind":"hello","protocol":1}'
    size = (28 + len(wire) + 3) & ~3
    received = struct.pack("=7I", 18, size, 123, 456, 0, macos.MESSAGE_ID, len(wire))
    received += wire + b"\0" * (size - 28 - len(wire))
    received += struct.pack("=5I", 0, 52, 0, 0, 0) + TOKEN
    destroyed = []

    class NativeFailure:
        def mach_msg(self, buffer, *args):
            ctypes.memmove(buffer, received, len(received))
            return 0

        def mach_msg_destroy(self, buffer):
            destroyed.append(bytes(buffer))

    def unavailable(token):
        raise failure("audit decoder unavailable")

    native = object.__new__(macos.MachTransport)
    native._lib = NativeFailure()
    monkeypatch.setattr(macos, "sender_info", unavailable)
    with pytest.raises(failure):
        native._receive(456, 10)
    assert len(destroyed) == 1
    assert destroyed[0].startswith(received)


@pytest.mark.parametrize("lifetime", [0, -1, float("nan"), float("inf"), True, 31])
def test_invalid_lifetime_is_rejected_before_native_start(lifetime):
    with pytest.raises(ValueError, match="lifetime"):
        OriginReceiver("task", lifetime_seconds=lifetime)


MAC = pytest.mark.skipif(sys.platform != "darwin", reason="real Mach audit trailers require macOS")


@MAC
def test_native_message_and_replay_from_separate_process():
    client = """
import sys
from lab.origin.macos import MachClient
from lab.origin.receiver import encode_message
native = MachClient(sys.argv[1])
try:
    wire = encode_message(native.hello(), b'native subprocess message')
    print(native.request(wire).data.decode(), flush=True)
    print(native.request(wire).data.decode(), flush=True)
finally:
    native.close()
"""
    with OriginReceiver("native-test-task") as receiver:
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", client, receiver.endpoint],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            first, replay = receiver.receive(), receiver.receive()
            stdout, stderr = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    assert process.returncode == 0, stderr
    assert first["sender"]["pid"] == process.pid
    assert first["sender"]["pid_version"] > 0
    assert first["source_authenticated"] is True
    assert first["message"]["sha256"] == hashlib.sha256(b"native subprocess message").hexdigest()
    assert first["conversation_identity"] == "UNBEKANNT"
    assert replay["reason"] == "replayed_local_session"
    assert json.loads(stdout.splitlines()[0]) == first


@MAC
def test_native_copied_challenge_from_another_process_is_unknown():
    original_client = """
import json,sys
from lab.origin.macos import MachClient
native = MachClient(sys.argv[1])
try:
    print(json.dumps(native.hello()), flush=True)
    sys.stdin.readline()
finally:
    native.close()
"""
    relay_client = """
import json,sys
from lab.origin.macos import MachClient
from lab.origin.receiver import encode_message
native = MachClient(sys.argv[1])
try:
    wire = encode_message(json.loads(sys.argv[2]), b'copied relay message')
    print(native.request(wire).data.decode(), flush=True)
finally:
    native.close()
"""
    with OriginReceiver("relay-test") as receiver, ThreadPoolExecutor(max_workers=1) as executor:
        pending = executor.submit(receiver.receive)
        original = subprocess.Popen(
            [sys.executable, "-B", "-c", original_client, receiver.endpoint],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            challenge = original.stdout.readline().strip()
            relay = subprocess.run(
                [sys.executable, "-B", "-c", relay_client, receiver.endpoint, challenge],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            result = pending.result(timeout=10)
            assert relay.returncode == 0, relay.stderr
            assert result["reason"] == "sender_instance_changed"
            assert result["source_authenticated"] is False
            assert json.loads(relay.stdout) == result
        finally:
            original.communicate("finish\n", timeout=10)


@MAC
def test_native_endpoint_is_removed_on_close():
    from lab.origin.macos import MachClient

    receiver = OriginReceiver("cleanup-test")
    endpoint = receiver.endpoint
    receiver.close()
    with pytest.raises(Unavailable):
        MachClient(endpoint)


@MAC
def test_native_proxy_own_session_proves_only_immediate_sender():
    content = b'{"claimed_actor":"Codex","claimed_pid":1,"copied_session":"other"}'
    client = """
import sys
from lab.origin.macos import MachClient
from lab.origin.receiver import encode_message
native = MachClient(sys.argv[1])
try:
    wire = encode_message(native.hello(), sys.argv[2].encode())
    print(native.request(wire).data.decode(), flush=True)
finally:
    native.close()
"""
    with OriginReceiver("proxy-task") as receiver:
        process = subprocess.Popen(
            [sys.executable, "-B", "-c", client, receiver.endpoint, content.decode()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            result = receiver.receive()
            stdout, stderr = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    assert process.returncode == 0, stderr
    assert result["sender"]["pid"] == process.pid
    assert result["source_scope"] == "immediate_kernel_message_sender_only"
    assert result["author_identity"] == result["conversation_identity"] == "UNBEKANNT"
    assert result["model_identity"] == "UNBEKANNT"
    assert result["message"]["sha256"] == hashlib.sha256(content).hexdigest()
    assert json.loads(stdout) == result
