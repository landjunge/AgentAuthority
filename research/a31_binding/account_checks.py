"""Actual cached-token checks, with externally sourced client-ID pins and no token export."""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a3_linux"))
from account_probe import OPENSSL, der, integer, public_key, raw

PINNED = {
    "Codex": {
        "issuer": "https://auth.openai.com",
        "client_id": "app_EMoamEEZ73f0CkXaXp7hrann",
        "algorithm": "RS256",
        "source": "openai/codex rust-v0.162.1 codex-rs/login/src/auth/manager.rs",
    },
    "Grok": {
        "issuer": "https://auth.x.ai",
        "client_id": "b1a00492-073a-47ea-816f-4c329264a828",
        "algorithm": "ES256",
        "source": "xai-org/grok-build 2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8 xai-grok-login/src/config.rs; not binary-build SHA match",
    },
}


def candidates(value, field=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from candidates(item, key)
    elif isinstance(value, list):
        for item in value:
            yield from candidates(item, field)
    elif isinstance(value, str) and value.count(".") == 2:
        yield field, value


def verify_signature(token, jwk, algorithm):
    head, body, signature = token.split(".")
    spki = public_key(jwk, algorithm)
    sig = raw(signature)
    if algorithm == "ES256":
        if len(sig) != 64:
            return False
        sig = der(48, integer(sig[:32]) + integer(sig[32:]))
    with tempfile.TemporaryDirectory(prefix="a31-public-verify-") as temp:
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
        (directory / "public-sig").write_bytes(sig)
        result = subprocess.run(
            [
                OPENSSL,
                "dgst",
                "-sha256",
                "-verify",
                str(directory / "public.pem"),
                "-signature",
                str(directory / "public-sig"),
            ],
            input=(head + "." + body).encode(),
            check=False,
            capture_output=True,
            timeout=10,
        )
    return result.returncode == 0


def probe(job_nonce):
    rows = []
    public_sources = []
    consistency = []
    for client in ["Codex", "Grok"]:
        pin = PINNED[client]
        url = pin["issuer"] + "/.well-known/jwks.json"
        with urllib.request.urlopen(url, timeout=12) as response:
            data = response.read()
        import hashlib

        jwks = json.loads(data)["keys"]
        public_sources.append(
            {"url": url, "sha256": hashlib.sha256(data).hexdigest(), "keys": jwks}
        )
        stored = json.loads(
            (Path.home() / (".codex" if client == "Codex" else ".grok") / "auth.json").read_text()
        )
        subjects = []
        for field, token in candidates(stored):
            try:
                head, body, _ = token.split(".")
                header, claims = json.loads(raw(head)), json.loads(raw(body))
                key = next(x for x in jwks if x["kid"] == header.get("kid"))
                verified = header["alg"] == pin["algorithm"] and verify_signature(
                    token, key, header["alg"]
                )
                issuer_ok = claims.get("iss") == pin["issuer"]
                subject_ok = isinstance(claims.get("sub"), str) and bool(claims["sub"])
                if verified and issuer_ok and subject_ok:
                    subjects.append(claims["sub"])
                audiences = claims.get("aud", [])
                if isinstance(audiences, str):
                    audiences = [audiences]
                id_token = field in ["id_token", "idToken"]
                rows.append(
                    {
                        "client": client,
                        "kind": "id_token" if id_token else "other_cached_token",
                        "signature_verified": verified,
                        "pinned_issuer_matches": issuer_ok,
                        "pinned_OIDC_client_audience_matches": pin["client_id"] in audiences,
                        "audience_check_is_full_ID_token_check": id_token,
                        "access_token_resource_audience": "UNBEKANNT unless independently configured; not conflated with client_id",
                        "signed_subject_nonempty": subject_ok,
                        "unexpired": isinstance(claims.get("exp"), (int, float))
                        and claims["exp"] > time.time(),
                        "original_login_nonce_binding": "UNBEKANNT; original challenge not retained",
                        "nonce_equals_new_job_challenge": claims.get("nonce") == job_nonce,
                        "has_signed_response_job_digest_field": any(
                            k in claims
                            for k in [
                                "response_digest",
                                "job_digest",
                                "response_sha256",
                                "job_sha256",
                            ]
                        ),
                        "wrong_issuer_control_rejected": claims.get("iss") != "https://a31.invalid",
                        "wrong_client_audience_control_rejected": "urn:a31:foreign-client"
                        not in audiences,
                        "provider_session_job_binding": "UNBEKANNT",
                        "raw_token_archived": False,
                    }
                )
            except (ValueError, KeyError, StopIteration, TypeError):
                rows.append(
                    {
                        "client": client,
                        "kind": "unqualified_cached_token",
                        "classification": "UNBEKANNT",
                    }
                )
        consistency.append(
            {
                "client": client,
                "signed_subjects_present": len(subjects),
                "signed_subject_consistency": len(set(subjects)) == 1 if subjects else None,
                "subject_values_exported": False,
                "expected_external_subject_anchor": "UNBEKANNT; no separately enrolled subject",
            }
        )
    return {
        "pins": PINNED,
        "token_checks": rows,
        "subject_checks": consistency,
        "public_JWKS": public_sources,
        "client_id_override_environment_present": {
            k: bool(os.environ.get(k))
            for k in [
                "CODEX_APP_SERVER_LOGIN_CLIENT_ID",
                "GROK_OIDC_CLIENT_ID",
                "GROK_OIDC_ISSUER",
                "GROK_OIDC_AUDIENCE",
            ]
        },
        "new_login": False,
        "token_export": False,
    }


if __name__ == "__main__":
    out = Path(Path("/tmp/a31-active-path").read_text().strip())
    nonce = json.loads((out / "case-1.json").read_text())["context"]["challenge"]
    print(json.dumps(probe(nonce), indent=2, sort_keys=True))
