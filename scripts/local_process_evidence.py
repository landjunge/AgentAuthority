"""Read a macOS observer/parent snapshot; never authenticate a session or message."""

from __future__ import annotations

import argparse
import ctypes as c
import json
import os
import sys
import uuid
from datetime import UTC, datetime


class _BSDInfo(c.Structure):
    # Installed Apple SDK: proc_info.h, PROC_PIDTBSDINFO (3), MAXCOMLEN (16).
    _fields_ = (
        [
            (name, c.c_uint32)
            for name in (
                "flags",
                "status",
                "xstatus",
                "pid",
                "ppid",
                "uid",
                "gid",
                "ruid",
                "rgid",
                "svuid",
                "svgid",
                "reserved",
            )
        ]
        + [
            ("comm", c.c_char * 16),
            ("name", c.c_char * 32),
        ]
        + [
            (name, c.c_uint32)
            for name in (
                "nfiles",
                "pgid",
                "jobc",
                "tdev",
                "tpgid",
            )
        ]
        + [
            ("nice", c.c_int32),
            ("start_seconds", c.c_uint64),
            ("start_microseconds", c.c_uint64),
        ]
    )


def _boot() -> str:
    libc = c.CDLL(None, use_errno=True)
    read = libc.sysctlbyname
    read.argtypes = [c.c_char_p, c.c_void_p, c.POINTER(c.c_size_t), c.c_void_p, c.c_size_t]
    read.restype = c.c_int
    value = c.create_string_buffer(64)
    size = c.c_size_t(len(value))
    if read(b"kern.bootsessionuuid", value, c.byref(size), None, 0) != 0:
        raise OSError(c.get_errno(), "boot unavailable")
    return str(uuid.UUID(value.value.decode("ascii"))).upper()


def _process(pid: int) -> dict:
    lib = c.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    read = lib.proc_pidinfo
    read.argtypes = [c.c_int, c.c_int, c.c_uint64, c.c_void_p, c.c_int]
    read.restype = c.c_int
    value = _BSDInfo()
    if read(pid, 3, 0, c.byref(value), c.sizeof(value)) != c.sizeof(value):
        raise OSError(c.get_errno(), "process unavailable")
    # No executable/resource paths, comm, argv, environment or content projection.
    return {
        name: getattr(value, name)
        for name in (
            "pid",
            "ppid",
            "uid",
            "start_seconds",
            "start_microseconds",
        )
    }


def _signing(pid: int) -> dict:
    cf = c.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    sec = c.CDLL("/System/Library/Frameworks/Security.framework/Security")
    ptr = c.c_void_p

    def function(lib, name, result, args):
        fn = getattr(lib, name)
        fn.restype, fn.argtypes = result, args
        return fn

    number = function(cf, "CFNumberCreate", ptr, [ptr, c.c_long, ptr])
    dictionary = function(cf, "CFDictionaryCreate", ptr, [ptr, ptr, ptr, c.c_long, ptr, ptr])
    get = function(cf, "CFDictionaryGetValue", ptr, [ptr, ptr])
    string = function(cf, "CFStringGetCString", c.c_bool, [ptr, ptr, c.c_long, c.c_uint32])
    length = function(cf, "CFDataGetLength", c.c_long, [ptr])
    bytes_at = function(cf, "CFDataGetBytePtr", ptr, [ptr])
    release = function(cf, "CFRelease", None, [ptr])
    guest = function(sec, "SecCodeCopyGuestWithAttributes", c.c_int32, [ptr, ptr, c.c_uint32, ptr])
    valid = function(sec, "SecCodeCheckValidity", c.c_int32, [ptr, c.c_uint32, ptr])
    signing = function(sec, "SecCodeCopySigningInformation", c.c_int32, [ptr, c.c_uint32, ptr])

    def key(name):
        return ptr.in_dll(sec, name).value

    pid_number = c.c_int32(pid)
    value = number(None, 3, c.byref(pid_number))  # kCFNumberSInt32Type
    if not value:
        raise OSError("number unavailable")
    attrs = dictionary(
        None, (ptr * 1)(key("kSecGuestAttributePid")), (ptr * 1)(value), 1, None, None
    )
    code, info = ptr(), ptr()
    try:
        if not attrs:
            raise OSError("attributes unavailable")
        if guest(None, attrs, 0, c.byref(code)) != 0 or valid(code, 0, None) != 0:
            raise OSError("dynamic signature unavailable")
        if signing(code, 2 | 8, c.byref(info)) != 0:
            raise OSError("signing information unavailable")
        digest = get(info, key("kSecCodeInfoUnique"))
        if not digest or length(digest) != 20:
            raise ValueError("unexpected cdhash")
        team = get(info, key("kSecCodeInfoTeamIdentifier"))
        text = c.create_string_buffer(32)
        team_id = (
            text.value.decode("ascii")
            if team and string(team, text, len(text), 0x08000100)
            else None
        )
        return {"cdhash": c.string_at(bytes_at(digest), 20).hex(), "team_id": team_id}
    finally:
        for owned in (info.value, code.value, attrs, value):
            if owned:
                release(owned)


_READ_ERRORS = (OSError, ValueError, AttributeError, UnicodeError, c.ArgumentError)
_PROCESS_FIELDS = ("pid", "ppid", "uid", "start_seconds", "start_microseconds")


def _snapshot(pid: int, boot_id: str) -> dict:
    unknown = {"aussage": "UNBEKANNT", "grund": "process_unavailable", "beleg": {}}
    try:
        before = _process(pid)
        try:
            signature = _signing(pid)
        except _READ_ERRORS:
            signature = None
        after = _process(pid)
    except _READ_ERRORS:
        return unknown
    if before != after or before.get("pid") != pid:
        return {**unknown, "grund": "process_changed"}
    if (
        any(type(before.get(key)) is not int or before[key] < 0 for key in _PROCESS_FIELDS)
        or before["start_seconds"] == 0
        or before["start_microseconds"] >= 1_000_000
    ):
        return {**unknown, "grund": "invalid_process_measurement"}
    # PID + kernel start + boot are a bounded snapshot, not an IPC audit token.
    evidence = {key: before[key] for key in _PROCESS_FIELDS} | {"boot_id": boot_id}
    if signature is not None:
        evidence["codesignature"] = signature
    return {
        "aussage": "BELEGT",
        "grund": "local_process_snapshot_only",
        "beleg": evidence,
        "codesignature": "BELEGT" if signature is not None else "UNBEKANNT",
    }


def observe() -> dict:
    """Take new OS readings only; no input packet or archived receipt is accepted."""
    record = {
        "scope": "local_observer_and_parent_snapshot_only",
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "herkunft": "UNBEKANNT",
        "identitaet": "UNBEKANNT",
        "source_authenticated": False,
        "recht_uebernommen": False,
        "binding": "no_message_session_or_model_binding",
        "selection": "PID_without_message_audit_token",
        "signer_requirement": "none",
        "observer": {"aussage": "UNBEKANNT", "grund": "unsupported_platform", "beleg": {}},
        "parent": {"aussage": "UNBEKANNT", "grund": "unsupported_platform", "beleg": {}},
    }
    if sys.platform != "darwin":
        return record
    try:
        boot_id = _boot()
    except _READ_ERRORS:
        record["observer"]["grund"] = record["parent"]["grund"] = "boot_unavailable"
        return record
    record["observer"] = _snapshot(os.getpid(), boot_id)
    record["parent"] = _snapshot(os.getppid(), boot_id)
    return record


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(observe(), ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
