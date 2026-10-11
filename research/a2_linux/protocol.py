"""Canonical public transcripts; private key bytes never returned or archived."""

import base64
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def b64(value):
    return base64.b64encode(value).decode()


def unb64(value):
    return base64.b64decode(value, validate=True)


def public(key):
    from cryptography.hazmat.primitives import serialization

    return b64(
        key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    )


def envelope(key, body):
    return {"body": body, "signature": b64(key.sign(canonical(body)))}


def verify(public_key, signed):
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    try:
        Ed25519PublicKey.from_public_bytes(unb64(public_key)).verify(
            unb64(signed["signature"]), canonical(signed["body"])
        )
        return True
    except (InvalidSignature, ValueError, TypeError, KeyError):
        return False
