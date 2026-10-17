"""Bounded JSON and local private-state primitives shared by server modules."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

from agent_authority.browser_contracts import Problem

MAX_BODY = 8 * 1024 * 1024


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def parse_json(raw: bytes) -> Any:
    """Bound bytes, depth and aggregate structure before applying input schemas."""
    if len(raw) > MAX_BODY:
        raise Problem(413, "INPUT_LIMIT")
    try:
        value = json.loads(raw, object_pairs_hook=_unique, parse_constant=lambda _: _bad_json())
        stack = [(value, 0)]
        count = 0
        while stack:
            item, depth = stack.pop()
            count += 1
            if depth > 30 or count > 250_000:
                raise ValueError("structure limit")
            if isinstance(item, dict):
                if any(len(key) > 256 for key in item):
                    raise ValueError("key limit")
                stack.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, list):
                stack.extend((child, depth + 1) for child in item)
            elif isinstance(item, str):
                if len(item) > MAX_BODY or any(0xD800 <= ord(c) <= 0xDFFF for c in item):
                    raise ValueError("string limit")
        return value
    except (ValueError, UnicodeError, RecursionError, OverflowError) as exc:
        raise Problem(400, "INVALID_JSON") from exc


def _bad_json() -> Any:
    raise ValueError("non-finite JSON")


def json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()


def private_file(path: Path, limit: int) -> bytes:
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ValueError("private regular owned file required")
        if info.st_size > limit:
            raise ValueError("file limit")
        raw = bytearray()
        while len(raw) <= limit:
            chunk = os.read(fd, min(8192, limit + 1 - len(raw)))
            if not chunk:
                return bytes(raw)
            raw.extend(chunk)
        raise ValueError("file limit")
    finally:
        os.close(fd)


def check_state(path: Path) -> None:
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
        raise ValueError("state must be a private owned directory (0700)")
