"""AA private v1: restricted RFC8785 JSON + existing A2 Ed25519 envelopes."""

import base64
import hashlib
import json
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


def restricted(value, depth=0):
    require(depth <= 30)
    if type(value) is dict:
        for k, v in value.items():
            require(type(k) is str)
            restricted(k, depth + 1)
            restricted(v, depth + 1)
    elif type(value) is list:
        for v in value:
            restricted(v, depth + 1)
    elif type(value) is str:
        require(all(32 <= ord(c) <= 126 for c in value))
    elif type(value) is int:
        require(abs(value) <= 9007199254740991)
    else:
        require(value is None or type(value) is bool)


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 400, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result

    try:
        value = json.loads(raw, object_pairs_hook=pairs)
        restricted(value)
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
    def no_duplicates(items):
        result = {}
        for key, value in items:
            require(key not in result)
            result[key] = value
        return result

    return {
        "registry": json.loads(unblob(payload["registry"]), object_pairs_hook=no_duplicates),
        "capture": [
            json.loads(line, object_pairs_hook=no_duplicates)
            for line in unblob(payload["capture"]).splitlines()
        ],
        "trial": json.loads(unblob(payload["trial"]), object_pairs_hook=no_duplicates),
    }
