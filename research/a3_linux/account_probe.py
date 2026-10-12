"""Verify existing account-token signatures locally; never export bearer tokens."""

import base64
import hashlib
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

OPENSSL = "/usr/local/opt/openssl@3/bin/openssl"


def raw(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def der(tag, value):
    size = len(value)
    if size < 128:
        length = bytes([size])
    else:
        data = size.to_bytes((size.bit_length() + 7) // 8, "big")
        length = bytes([128 + len(data)]) + data
    return bytes([tag]) + length + value


def integer(value):
    value = value.lstrip(b"\0") or b"\0"
    if value[0] & 128:
        value = b"\0" + value
    return der(2, value)


def public_key(jwk, algorithm):
    if algorithm == "RS256" and jwk["kty"] == "RSA":
        key = der(48, integer(raw(jwk["n"])) + integer(raw(jwk["e"])))
        return der(48, bytes.fromhex("300d06092a864886f70d0101010500") + der(3, b"\0" + key))
    if algorithm == "ES256" and jwk["kty"] == "EC" and jwk["crv"] == "P-256":
        return (
            bytes.fromhex("3059301306072a8648ce3d020106082a8648ce3d03010703420004")
            + raw(jwk["x"])
            + raw(jwk["y"])
        )
    raise ValueError("unsupported trusted key algorithm")


def token_candidates(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from token_candidates(item)
    elif isinstance(value, list):
        for item in value:
            yield from token_candidates(item)
    elif isinstance(value, str) and value.count(".") == 2:
        yield value


def probe():
    results = []
    sources = []
    for client, issuer, path in [
        ("Codex", "https://auth.openai.com", Path.home() / ".codex/auth.json"),
        ("Grok", "https://auth.x.ai", Path.home() / ".grok/auth.json"),
    ]:
        try:
            with urllib.request.urlopen(issuer + "/.well-known/jwks.json", timeout=12) as response:
                data = response.read()
            keys = json.loads(data)["keys"]
            sources.append(
                {
                    "url": issuer + "/.well-known/jwks.json",
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "public_keys": keys,
                    "bytes": len(data),
                }
            )
            credential = json.loads(path.read_text())
            candidates = list(token_candidates(credential))
            for token in candidates:
                try:
                    head, body, signature = token.split(".")
                    header, claims = json.loads(raw(head)), json.loads(raw(body))
                    if claims.get("iss") != issuer:
                        continue
                    jwk = next(key for key in keys if key.get("kid") == header.get("kid"))
                    algorithm = header["alg"]
                    spki = public_key(jwk, algorithm)
                    sig = raw(signature)
                    if algorithm == "ES256":
                        if len(sig) != 64:
                            raise ValueError("ES256 signature length")
                        sig = der(48, integer(sig[:32]) + integer(sig[32:]))
                    with tempfile.TemporaryDirectory(prefix="a3-public-verify-") as temp:
                        directory = Path(temp)
                        (directory / "public.der").write_bytes(spki)
                        subprocess.run(
                            [
                                OPENSSL,
                                "pkey",
                                "-pubin",
                                "-inform",
                                "DER",
                                "-in",
                                str(directory / "public.der"),
                                "-out",
                                str(directory / "public.pem"),
                            ],
                            check=True,
                            capture_output=True,
                            timeout=10,
                        )
                        (directory / "public-signature").write_bytes(sig)
                        checked = subprocess.run(
                            [
                                OPENSSL,
                                "dgst",
                                "-sha256",
                                "-verify",
                                str(directory / "public.pem"),
                                "-signature",
                                str(directory / "public-signature"),
                            ],
                            input=(head + "." + body).encode(),
                            check=False,
                            capture_output=True,
                            timeout=10,
                        )
                    results.append(
                        {
                            "client": client,
                            "issuer": issuer,
                            "algorithm": algorithm,
                            "signature_verified": checked.returncode == 0,
                            "unexpired": isinstance(claims.get("exp"), (int, float))
                            and claims["exp"] > time.time(),
                            "has_subject": bool(claims.get("sub")),
                            "has_auth_session": any(k in claims for k in ["sid", "session_id"]),
                            "has_logical_agent_or_model": any(
                                k in claims for k in ["agent_id", "model", "model_id"]
                            ),
                            "coding_thread_binding": "UNBEKANNT",
                            "audience_independently_pinned": False,
                            "public_proof_reproducibility": "verification code and public keys retained; bearer token deliberately withheld",
                            "token_exported": False,
                        }
                    )
                except (ValueError, KeyError, StopIteration, TypeError):
                    results.append(
                        {
                            "client": client,
                            "signature_verified": False,
                            "status": "UNBEKANNT",
                            "reason": "token/key shape cannot be qualified",
                            "token_exported": False,
                        }
                    )
            if not candidates:
                results.append(
                    {
                        "client": client,
                        "status": "UNBEKANNT",
                        "reason": "no JWT found in known auth store",
                    }
                )
        except (OSError, ValueError, KeyError) as error:
            results.append(
                {"client": client, "status": "UNBEKANNT", "error_class": type(error).__name__}
            )
    return {
        "account_token_checks": results,
        "public_jwks": sources,
        "real_agent_effect_chain": "UNBEKANNT",
        "credentials_copied_or_sent_to_guest": False,
    }


if __name__ == "__main__":
    print(json.dumps(probe(), indent=2, sort_keys=True))
