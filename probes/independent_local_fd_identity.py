"""Independent, current-process FD-pair verification over UNIX SCM_RIGHTS.

Research-only boundary channel.  It verifies the relation of the two file
descriptors actually received by a clean verifier process.  It does not prove
that an untrusted sender supplied the originally intended resources.
"""
from __future__ import annotations

import argparse
import array
import errno
import fcntl
import hashlib
import json
import os
import secrets
import socket
import stat
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from typing import Any


PROTOCOL = "aa-independent-fd-pair-v1"
MAX_MESSAGE = 65_536
_MODULE_PATH = os.path.abspath(__file__)
_INT_BYTES = array.array("i").itemsize
_SOCKET_TYPE = getattr(socket, "SOCK_SEQPACKET", socket.SOCK_STREAM)
_LIMITS = (
    "Nur Relation der zwei tatsaechlich per SCM_RIGHTS empfangenen regulaeren "
    "FDs im Messmoment. Keine Authentisierung ihrer urspruenglich gemeinten "
    "Ressource; keine Garantie bei kompromittiertem Broker/Verifier/Kernel, "
    "FD-Neubelegung oder TOCTOU ausserhalb der Vor-/Nachmessung."
)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")


def _request_id(protocol: str, nonce: str) -> str:
    return hashlib.sha256(_canonical({"nonce": nonce, "protocol": protocol})).hexdigest()


def _unknown(
    reason: str,
    verifier: dict[str, Any] | None = None,
    *,
    fd_set_verified: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "A": "UNBEKANNT",
        "B": reason,
        "C": "NEIN",
        "D": _LIMITS,
        "source_authenticated": False,
        "fd_set_verified": fd_set_verified,
        "positive_identity_authorized": False,
    }
    if verifier is not None:
        result["verifier"] = verifier
    return result


def _packet_pairs(events: object, run: object) -> tuple[list[tuple[int, int]] | None, str]:
    if type(run) is not int or run <= 0 or not isinstance(events, list):
        return None, "invalid_packet_binding"
    candidates = []
    for row in events:
        if not isinstance(row, dict):
            return None, "invalid_packet_shape"
        if row.get("kind") != "live_local_file_refs":
            continue
        if type(row.get("run")) is not int or row["run"] <= 0:
            return None, "invalid_packet_binding"
        if row["run"] == run:
            if set(row) != {"run", "kind", "value"}:
                return None, "invalid_packet_shape"
            candidates.append(row["value"])
    if len(candidates) != 1:
        return None, "missing_unique_packet"
    value = candidates[0]
    if not isinstance(value, dict) or set(value) != {"scope", "references"}:
        return None, "invalid_packet_shape"
    scope = value["scope"]
    expected_scope = {
        "os": "Linux",
        "filesystem": "tmpfs",
        "same_collection_process": True,
        "live_handle_overlap_confirmed": True,
    }
    if not isinstance(scope, dict) or scope != expected_scope:
        return None, "invalid_packet_scope"
    refs = value["references"]
    if not isinstance(refs, list) or len(refs) != 2:
        return None, "invalid_packet_references"
    pairs = []
    for ref in refs:
        if (
            not isinstance(ref, dict)
            or set(ref) != {"st_dev", "st_ino", "regular_file"}
            or ref["regular_file"] is not True
            or type(ref["st_dev"]) is not int
            or ref["st_dev"] < 0
            or type(ref["st_ino"]) is not int
            or ref["st_ino"] <= 0
        ):
            return None, "invalid_packet_references"
        pairs.append((ref["st_dev"], ref["st_ino"]))
    return pairs, "ok"


def _recv_request(channel: socket.socket) -> tuple[dict[str, Any], list[int]]:
    ancillary_size = socket.CMSG_SPACE(4 * _INT_BYTES)
    payload, ancillary, flags, _ = channel.recvmsg(
        MAX_MESSAGE + 1, ancillary_size, getattr(socket, "MSG_CMSG_CLOEXEC", 0)
    )
    if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC):
        raise ValueError("truncated_request")
    if not payload or len(payload) > MAX_MESSAGE:
        raise ValueError("invalid_request_size")
    try:
        request = json.loads(payload.decode("ascii"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid_request_json") from exc
    received: list[int] = []
    for level, kind, data in ancillary:
        if level != socket.SOL_SOCKET or kind != socket.SCM_RIGHTS:
            continue
        usable = len(data) - (len(data) % _INT_BYTES)
        values = array.array("i")
        values.frombytes(data[:usable])
        received.extend(values.tolist())
    return request, received


def _measure(received: list[int]) -> tuple[str, list[dict[str, Any]]]:
    before = []
    for slot, fd in enumerate(received, 1):
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        native = os.fstat(fd)
        before.append((flags, native))
        if not stat.S_ISREG(native.st_mode):
            raise ValueError(f"fd_{slot}_not_regular")
    after = []
    for slot, fd in enumerate(received, 1):
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        native = os.fstat(fd)
        after.append((flags, native))
        if not stat.S_ISREG(native.st_mode):
            raise ValueError(f"fd_{slot}_not_regular_after")
    rows = []
    for slot, ((flags_before, first), (flags_after, second)) in enumerate(
        zip(before, after), 1
    ):
        rows.append(
            {
                "slot": slot,
                "flags_before": flags_before,
                "flags_after": flags_after,
                "pair_before": [first.st_dev, first.st_ino],
                "pair_after": [second.st_dev, second.st_ino],
                "regular_before": stat.S_ISREG(first.st_mode),
                "regular_after": stat.S_ISREG(second.st_mode),
            }
        )
    if any(
        row["flags_before"] != row["flags_after"]
        or row["pair_before"] != row["pair_after"]
        for row in rows
    ):
        raise ValueError("fd_measurement_changed")
    verdict = "GLEICH" if rows[0]["pair_before"] == rows[1]["pair_before"] else "VERSCHIEDEN"
    return verdict, rows


def _verifier_main(channel_fd: int) -> int:
    channel = socket.socket(fileno=channel_fd)
    received: list[int] = []
    request: dict[str, Any] = {}
    response: dict[str, Any]
    try:
        request, received = _recv_request(channel)
        if set(request) != {"protocol", "nonce", "request_id"}:
            raise ValueError("invalid_request_shape")
        protocol = request["protocol"]
        nonce = request["nonce"]
        request_id = request["request_id"]
        if (
            protocol != PROTOCOL
            or not isinstance(nonce, str)
            or len(nonce) != 64
            or not isinstance(request_id, str)
            or request_id != _request_id(protocol, nonce)
        ):
            raise ValueError("invalid_request_binding")
        if len(received) != 2 or received[0] == received[1]:
            raise ValueError("exactly_two_received_fds_required")
        verdict, measurements = _measure(received)
        response = {
            "protocol": protocol,
            "nonce": nonce,
            "request_id": request_id,
            "status": "OK",
            "verdict": verdict,
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "executable": sys.executable,
            "syscall_origin": "clean-exec-verifier",
            "measurements": measurements,
        }
    except BaseException as exc:
        response = {
            "protocol": request.get("protocol"),
            "nonce": request.get("nonce"),
            "request_id": request.get("request_id"),
            "status": "UNBEKANNT",
            "reason": type(exc).__name__ + ":" + str(exc),
            "pid": os.getpid(),
            "ppid": os.getppid(),
            "executable": sys.executable,
            "syscall_origin": "clean-exec-verifier",
        }
    finally:
        for fd in received:
            try:
                os.close(fd)
            except OSError:
                pass
    try:
        channel.sendall(_canonical(response))
        channel.shutdown(socket.SHUT_WR)
    except OSError:
        return 3
    finally:
        channel.close()
    return 0


def _default_argv(channel_fd: int) -> list[str]:
    return [
        sys.executable,
        "-I",
        "-S",
        _MODULE_PATH,
        "--verifier-fd",
        str(channel_fd),
    ]


def _exchange(
    handles: Sequence[int],
    timeout: float,
    nonce: str,
    argv_factory: Callable[[int], Sequence[str]],
) -> dict[str, Any]:
    started = time.monotonic()
    process: subprocess.Popen[bytes] | None = None
    parent: socket.socket | None = None
    child: socket.socket | None = None
    metadata: dict[str, Any] = {"parent_pid": os.getpid()}
    try:
        parent, child = socket.socketpair(socket.AF_UNIX, _SOCKET_TYPE)
        argv = list(argv_factory(child.fileno()))
        process = subprocess.Popen(
            argv,
            close_fds=True,
            pass_fds=(child.fileno(),),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        metadata["pid"] = process.pid
        child.close()
        child = None
        request = {
            "protocol": PROTOCOL,
            "nonce": nonce,
            "request_id": _request_id(PROTOCOL, nonce),
        }
        rights = array.array("i", handles)
        sent = parent.sendmsg(
            [_canonical(request)],
            [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights.tobytes())],
        )
        if sent != len(_canonical(request)):
            raise OSError(errno.EIO, "partial_request_send")
        parent.shutdown(socket.SHUT_WR)
        chunks = []
        total = 0
        while True:
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                raise TimeoutError("verifier_timeout")
            parent.settimeout(remaining)
            chunk = parent.recv(min(8192, MAX_MESSAGE + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_MESSAGE:
                raise ValueError("response_too_large")
        remaining = timeout - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("verifier_timeout")
        return_code = process.wait(timeout=remaining)
        metadata["return_code"] = return_code
        metadata["process_reaped"] = True
        if return_code != 0:
            raise RuntimeError("verifier_nonzero_exit")
        if not chunks:
            raise ValueError("missing_verifier_response")
        try:
            response = json.loads(b"".join(chunks).decode("ascii"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid_verifier_response") from exc
        metadata["raw_response"] = response
        metadata["transport_status"] = "ok"
        return metadata
    except subprocess.TimeoutExpired as exc:
        metadata.update(transport_status="timeout", reason=type(exc).__name__)
        return metadata
    except (TimeoutError, socket.timeout) as exc:
        metadata.update(transport_status="timeout", reason=str(exc))
        return metadata
    except BaseException as exc:
        metadata.update(
            transport_status="error",
            reason=type(exc).__name__ + ":" + str(exc),
        )
        return metadata
    finally:
        if child is not None:
            child.close()
        if parent is not None:
            parent.close()
        if process is not None:
            return_code = process.poll()
            if return_code is None:
                process.kill()
                return_code = process.wait()
            else:
                process.wait()
            metadata.setdefault("return_code", return_code)
            metadata["process_reaped"] = True


def _valid_pair(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and type(value[0]) is int
        and value[0] >= 0
        and type(value[1]) is int
        and value[1] > 0
    )


def _validate_response(
    response: object,
    *,
    nonce: str,
    process_pid: int,
    parent_pid: int,
) -> tuple[list[tuple[int, int]] | None, str, dict[str, Any] | None]:
    expected_keys = {
        "protocol",
        "nonce",
        "request_id",
        "status",
        "verdict",
        "pid",
        "ppid",
        "executable",
        "syscall_origin",
        "measurements",
    }
    if not isinstance(response, dict) or set(response) != expected_keys:
        return None, "invalid_response_shape", None
    if (
        response["protocol"] != PROTOCOL
        or response["nonce"] != nonce
        or response["request_id"] != _request_id(PROTOCOL, nonce)
    ):
        return None, "response_binding_mismatch", None
    if (
        response["status"] != "OK"
        or response["verdict"] not in {"GLEICH", "VERSCHIEDEN"}
        or type(response["pid"]) is not int
        or response["pid"] != process_pid
        or response["pid"] == parent_pid
        or type(response["ppid"]) is not int
        or response["ppid"] != parent_pid
        or response["executable"] != sys.executable
        or response["syscall_origin"] != "clean-exec-verifier"
    ):
        return None, "invalid_verifier_identity", None
    rows = response["measurements"]
    if not isinstance(rows, list) or len(rows) != 2:
        return None, "invalid_measurements", None
    pairs = []
    expected_row_keys = {
        "slot",
        "flags_before",
        "flags_after",
        "pair_before",
        "pair_after",
        "regular_before",
        "regular_after",
    }
    for slot, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != expected_row_keys:
            return None, "invalid_measurements", None
        if (
            row["slot"] != slot
            or type(row["flags_before"]) is not int
            or row["flags_before"] < 0
            or type(row["flags_after"]) is not int
            or row["flags_after"] < 0
            or row["flags_before"] != row["flags_after"]
            or row["regular_before"] is not True
            or row["regular_after"] is not True
            or not _valid_pair(row["pair_before"])
            or row["pair_before"] != row["pair_after"]
        ):
            return None, "invalid_measurements", None
        pairs.append((row["pair_before"][0], row["pair_before"][1]))
    relation = "GLEICH" if pairs[0] == pairs[1] else "VERSCHIEDEN"
    if response["verdict"] != relation:
        return None, "verdict_measurement_mismatch", None
    evidence = {
        "pid": response["pid"],
        "ppid": response["ppid"],
        "parent_pid": parent_pid,
        "executable": response["executable"],
        "syscall_origin": response["syscall_origin"],
        "protocol": response["protocol"],
        "request_id": response["request_id"],
        "verdict": response["verdict"],
        "measurements": rows,
    }
    return pairs, "ok", evidence


def verify_current_fd_identity(
    events: object,
    run: object,
    observer_result: object,
    *,
    handles: Sequence[int] | None,
    timeout: float = 3.0,
) -> dict[str, Any]:
    """Reconcile packet, observer claim and a clean-process FD measurement."""
    if sys.platform != "linux":
        return _unknown("unsupported_platform")
    return _verify_current_fd_identity(
        events,
        run,
        observer_result,
        handles=handles,
        timeout=timeout,
        argv_factory=_default_argv,
    )


def _verify_current_fd_identity(
    events: object,
    run: object,
    observer_result: object,
    *,
    handles: Sequence[int] | None,
    timeout: float,
    argv_factory: Callable[[int], Sequence[str]],
) -> dict[str, Any]:
    """Testable trusted-core implementation; public entry fixes the verifier."""
    offered, packet_reason = _packet_pairs(events, run)
    if offered is None:
        return _unknown(packet_reason)
    if not isinstance(observer_result, dict) or observer_result.get("A") not in {
        "DIESELBE",
        "VERSCHIEDEN",
    }:
        return _unknown("observer_not_positive")
    if (
        handles is None
        or not isinstance(handles, Sequence)
        or isinstance(handles, (str, bytes, bytearray))
        or len(handles) != 2
        or any(type(fd) is not int or fd < 0 for fd in handles)
        or handles[0] == handles[1]
    ):
        return _unknown("invalid_fd_arguments")
    if type(timeout) not in {int, float} or isinstance(timeout, bool) or timeout <= 0:
        return _unknown("invalid_timeout")
    nonce = secrets.token_hex(32)
    transport = _exchange(handles, float(timeout), nonce, argv_factory)
    public_transport = {key: value for key, value in transport.items() if key != "raw_response"}
    if transport.get("transport_status") != "ok":
        return _unknown("verifier_transport_failed", public_transport)
    pairs, response_reason, evidence = _validate_response(
        transport.get("raw_response"),
        nonce=nonce,
        process_pid=transport["pid"],
        parent_pid=transport["parent_pid"],
    )
    if pairs is None or evidence is None:
        public_transport["validation"] = response_reason
        return _unknown("verifier_response_rejected", public_transport)
    evidence["process_reaped"] = transport.get("process_reaped") is True
    evidence["return_code"] = transport.get("return_code")
    if pairs != offered:
        return _unknown("verifier_packet_mismatch", evidence, fd_set_verified=True)
    relation = "DIESELBE" if pairs[0] == pairs[1] else "VERSCHIEDEN"
    if observer_result["A"] != relation:
        return _unknown("verifier_observer_mismatch", evidence, fd_set_verified=True)
    return {
        "A": relation,
        "B": "Verifiermessung, geordnete Packetpaare und Observer-A stimmen ueberein.",
        "C": "JA",
        "D": _LIMITS,
        "source_authenticated": False,
        "fd_set_verified": True,
        "positive_identity_authorized": True,
        "verifier": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verifier-fd", required=True, type=int)
    args = parser.parse_args()
    if args.verifier_fd < 0:
        raise ValueError("nonnegative_verifier_fd_required")
    return _verifier_main(args.verifier_fd)


if __name__ == "__main__":
    raise SystemExit(main())
