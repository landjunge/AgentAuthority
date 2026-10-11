"""Independent OpenSSL Ed25519 verification; no host package or privilege changes."""

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

from protocol import b64, canonical, unb64

OPENSSL = "/usr/local/opt/openssl@3/bin/openssl"
SPKI_ED25519 = bytes.fromhex("302a300506032b6570032100")


def create_ca(private_directory):
    private_directory.mkdir(mode=0o700)
    keyfile = private_directory / "ca-private.pem"
    subprocess.run(
        [OPENSSL, "genpkey", "-algorithm", "Ed25519", "-out", str(keyfile)],
        check=True,
        capture_output=True,
        timeout=10,
    )
    os.chmod(keyfile, 0o600)
    raw = subprocess.check_output(
        [OPENSSL, "pkey", "-in", str(keyfile), "-pubout", "-outform", "DER"]
    )
    if len(raw) != 44 or not raw.startswith(SPKI_ED25519):
        raise ValueError("unexpected public key format")
    return keyfile, b64(raw[-32:])


def sign(keyfile, body):
    with tempfile.TemporaryDirectory(prefix="a2-sign-") as tmp:
        payload = Path(tmp) / "public-message"
        payload.write_bytes(canonical(body))
        signature = subprocess.check_output(
            [OPENSSL, "pkeyutl", "-sign", "-rawin", "-inkey", str(keyfile), "-in", str(payload)]
        )
    return {"body": body, "signature": b64(signature)}


def verify(public_key, signed):
    try:
        key = unb64(public_key)
        if len(key) != 32:
            return False
        with tempfile.TemporaryDirectory(prefix="a2-verify-") as tmp:
            directory = Path(tmp)
            (directory / "key.der").write_bytes(SPKI_ED25519 + key)
            (directory / "message").write_bytes(canonical(signed["body"]))
            (directory / "signature").write_bytes(unb64(signed["signature"]))
            run = subprocess.run(
                [
                    OPENSSL,
                    "pkeyutl",
                    "-verify",
                    "-rawin",
                    "-pubin",
                    "-keyform",
                    "DER",
                    "-inkey",
                    str(directory / "key.der"),
                    "-in",
                    str(directory / "message"),
                    "-sigfile",
                    str(directory / "signature"),
                ],
                capture_output=True,
                timeout=10,
            )
            return run.returncode == 0
    except (ValueError, TypeError, KeyError):
        return False


def _evaluate(bundle, capture, trial, pinned_ca):
    enrollment_ok = bundle["ca_public_key"] == pinned_ca and verify(pinned_ca, bundle["enrollment"])
    registry = bundle["enrollment"]["body"]
    if set(registry["agents"]) != {"TestAlpha", "TestBeta"}:
        raise ValueError("only explicitly enrolled test identities supported")
    checks = []
    for item in trial["handshakes"]:
        receipt = item["receipt"]
        body = receipt["body"]
        actual = next(
            (
                name
                for name, principal in registry["agents"].items()
                if verify(principal["public_key"], item["proof"])
            ),
            None,
        )
        checks.append(
            {
                "starter_signature": verify(registry["starter_public_key"], receipt),
                "agent_signature_identity": actual,
                "receipt_credential_matches": actual == body["credential_identity"],
                "proof_hash_matches": hashlib.sha256(canonical(item["proof"])).hexdigest()
                == body["proof_sha256"],
                "fresh_challenge": item["proof"]["body"]["challenge"] == body["challenge"],
            }
        )
    ready = next(x for x in capture if x.get("ready"))
    summary = next(x["summary"] for x in capture if "summary" in x)
    writes = [x["record"] for x in capture if x.get("record", {}).get("kind") == 1]
    stats = summary["stats"]
    healthy = (
        summary["perf_lost"] == 0
        and summary["pending"] == 0
        and all(stats[str(k)] == 0 for k in [3, 4, 5, 7])
        and stats["0"] == stats["1"] == stats["2"] == len(writes)
        and summary["kprobe_profile"]
        and all(int(x[-1]) == 0 for x in summary["kprobe_profile"])
        and trial["lifecycle"]["perf_lost"] == trial["lifecycle"]["submit_failures"] == 0
    )
    chains = []
    for event in writes:
        candidates = []
        for item, check in zip(trial["handshakes"], checks, strict=True):
            body = item["receipt"]["body"]
            sender = body["message_sender"]
            if (
                enrollment_ok
                and healthy
                and check["starter_signature"]
                and check["receipt_credential_matches"]
                and check["proof_hash_matches"]
                and check["fresh_challenge"]
                and body["instance_bound"]
                and body["domain"] == "A2-START-BINDING-v1"
                and body["run_id"] == registry["run_id"] == body["challenge"]["run_id"]
                and body["challenge"]["file"] == ready["file"]
                and all(
                    sender[k] == body["challenge"]["instance"][k]
                    for k in ["pid", "start_ns", "generation"]
                )
                and sender["uid"] == registry["agents"][body["authenticated_identity"]]["uid"]
                and body["authenticated_identity"] == check["agent_signature_identity"]
                and body["boot_hash"] == ready["boot_hash"] == registry["boot_hash"]
                and body["pid_namespace"] == ready["pid_namespace"] == registry["pid_namespace"]
                and sender["pid"] == event["tgid"]
                and sender["start_ns"] == event["start_ns"]
                and body["attested_ns"] <= event["entry_ns"]
                and event["entry_ns"]
                <= body["challenge"]["issued_ns"] + body["challenge"]["expires_in_ns"]
                and event["result"] == event["count"] == 16
                and {k: event[k] for k in ["dev", "inode"]} == ready["file"]
            ):
                execs = [
                    x
                    for x in trial["lifecycle"]["records"]
                    if x["kind"] == 2
                    and x["pid"] == event["tgid"]
                    and x["start"] == event["start_ns"]
                    and x["stamp"] <= event["entry_ns"]
                ]
                if (
                    execs
                    and max(execs, key=lambda x: x["stamp"])["generation"] == sender["generation"]
                ):
                    candidates.append(body["authenticated_identity"])
        chains.append(
            {
                "process": {k: event[k] for k in ["tgid", "start_ns", "ppid"]},
                "independent_write": "BELEGT" if healthy else "UNBEKANNT",
                "acting_authenticated_identity": candidates[0] if len(candidates) == 1 else None,
                "identity_effect_chain": "BELEGT" if len(candidates) == 1 else "UNBEKANNT",
            }
        )
    return {
        "enrollment_signature": enrollment_ok,
        "proof_checks": checks,
        "known_loss_checks": bool(healthy),
        "chains": chains,
        "codex_authenticated": False,
        "grok_authenticated": False,
        "real_model_or_person_identity": "UNBEKANNT",
    }


def evaluate(bundle, capture, trial, pinned_ca):
    try:
        return _evaluate(bundle, capture, trial, pinned_ca)
    except (KeyError, TypeError, ValueError, StopIteration, IndexError):
        return {
            "identity_effect_chain": "UNBEKANNT",
            "chains": [],
            "reason": "malformed or incomplete evidence",
            "codex_authenticated": False,
            "grok_authenticated": False,
        }
