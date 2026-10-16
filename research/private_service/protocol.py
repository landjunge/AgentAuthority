"""AA private v1: restricted RFC8785 JSON + existing A2 Ed25519 envelopes."""

import base64
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import create_ca
from protocol import canonical

from research.private_service.crypto import sign, verify

__all__ = ["canonical", "create_ca", "sign", "verify"]

ID = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
AUDIENCE = "aa-private-local-v1"
SCHEMA = "aa-private-v1"


class Problem(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(code)


def require(condition, status=422, code="INVALID_FORMAT"):
    if not condition:
        raise Problem(status, code)


def fields(value, names):
    require(type(value) is dict and set(value) == set(names.split()))


def identifier(value):
    require(type(value) is str and ID.fullmatch(value) is not None)


MAX_NODES = 20000
MAX_STRING = 196608


def restricted(value, depth=0, budget=None, legacy=False):
    budget = [MAX_NODES] if budget is None else budget
    budget[0] -= 1
    require(budget[0] >= 0, 422, "STRUCTURE_LIMIT")
    require(depth <= 30)
    if type(value) is dict:
        require(len(value) <= 128, 422, "STRUCTURE_LIMIT")
        for k, v in value.items():
            require(type(k) is str)
            restricted(k, depth + 1, budget, legacy)
            restricted(v, depth + 1, budget, legacy)
    elif type(value) is list:
        require(len(value) <= 4096, 422, "STRUCTURE_LIMIT")
        for v in value:
            restricted(v, depth + 1, budget, legacy)
    elif type(value) is str:
        require(len(value) <= MAX_STRING, 422, "STRUCTURE_LIMIT")
        require(legacy or all(32 <= ord(c) <= 126 for c in value))
    elif type(value) is int:
        require(legacy or abs(value) <= 9007199254740991)
    elif type(value) is float and legacy:
        require(math.isfinite(value))
    else:
        require(value is None or type(value) is bool)


def parse(raw, legacy=False):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 400, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=pairs)
        restricted(value, legacy=legacy)
        return value
    except (ValueError, TypeError, RecursionError, UnicodeError) as error:
        raise Problem(400, "INVALID_JSON") from error


def digest(value):
    restricted(value)
    return hashlib.sha256(canonical(value)).hexdigest()


def now_ms():
    return int(time.time() * 1000)


def fresh(body, now, maximum=60000):
    require(all(type(body.get(k)) is int for k in ("issued_ms", "expires_ms")))
    require(
        body["issued_ms"] <= now < body["expires_ms"] <= body["issued_ms"] + maximum,
        410,
        "EXPIRED_OR_FUTURE",
    )


def request(key, tenant, kid, path, payload, idem, nonce, now=None):
    stamp = now_ms() if now is None else now
    return sign(
        key,
        {
            "schema": SCHEMA,
            "domain": "AA-REQUEST-v1",
            "tenant": tenant,
            "audience": AUDIENCE,
            "method": "POST",
            "path": path,
            "kid": kid,
            "nonce": nonce,
            "idempotency_key": idem,
            "issued_ms": stamp,
            "expires_ms": stamp + 60000,
            "payload": payload,
        },
    )


def blob(raw):
    return base64.b64encode(raw).decode("ascii")


def unblob(value):
    require(type(value) is str)
    try:
        return base64.b64decode(value, validate=True)
    except ValueError as error:
        raise Problem(422, "EVIDENCE_ENCODING_INVALID") from error


def blob_digest(value):
    return hashlib.sha256(unblob(value) if value is not None else b"").hexdigest()


def evidence_values(payload):
    # These are opaque legacy A4 measurement bytes, outside the new JCS schema.
    # Hash the exact bytes; never re-canonicalize legacy floats/raw diagnostics.
    raw = {k: unblob(payload[k]) for k in ("registry", "capture", "trial")}
    require(sum(map(len, raw.values())) <= 196608, 413, "EVIDENCE_BYTE_LIMIT")
    lines = raw["capture"].splitlines()
    require(len(lines) <= 4096, 422, "STRUCTURE_LIMIT")
    result = {
        "registry": parse(raw["registry"], legacy=True),
        "capture": [parse(line, legacy=True) for line in lines],
        "trial": parse(raw["trial"], legacy=True),
    }
    restricted(result, legacy=True)
    return result
