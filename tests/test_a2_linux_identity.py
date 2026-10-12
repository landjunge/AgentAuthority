"""Real OpenSSL signature checks and offline negative joins, not VM evidence."""

import copy
import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parents[1] / "research/a2_linux"
SPEC = importlib.util.spec_from_file_location("a2_protocol", DIR / "protocol.py")
assert SPEC and SPEC.loader
PROTOCOL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROTOCOL)
PREVIOUS = sys.modules.get("protocol")
sys.modules["protocol"] = PROTOCOL
try:
    SPEC2 = importlib.util.spec_from_file_location("a2_host_crypto", DIR / "host_crypto.py")
    assert SPEC2 and SPEC2.loader
    HOST = importlib.util.module_from_spec(SPEC2)
    SPEC2.loader.exec_module(HOST)
finally:
    if PREVIOUS is None:
        del sys.modules["protocol"]
    else:
        sys.modules["protocol"] = PREVIOUS


@pytest.fixture()
def signed_case(tmp_path):
    ca, ca_pub = HOST.create_ca(tmp_path / "ca")
    issuer, issuer_pub = HOST.create_ca(tmp_path / "issuer")
    alpha, alpha_pub = HOST.create_ca(tmp_path / "alpha")
    _beta, beta_pub = HOST.create_ca(tmp_path / "beta")
    instance = {"pid": 8, "start_ns": 50, "generation": 1}
    file = {"dev": 3, "inode": 4}
    challenge = {
        "run_id": "run",
        "instance": instance,
        "file": file,
        "nonce": "fresh",
        "issued_ns": 100,
        "expires_in_ns": 500,
    }
    proof = HOST.sign(alpha, {"challenge": challenge, "claimed_identity": "TestAlpha"})
    receipt = {
        "domain": "A2-START-BINDING-v1",
        "run_id": "run",
        "challenge": challenge,
        "message_sender": {**instance, "uid": 61001},
        "boot_hash": "boot",
        "pid_namespace": "ns",
        "credential_identity": "TestAlpha",
        "proof_sha256": hashlib.sha256(PROTOCOL.canonical(proof)).hexdigest(),
        "instance_bound": True,
        "authenticated_identity": "TestAlpha",
        "attested_ns": 150,
    }
    registry = {
        "run_id": "run",
        "starter_public_key": issuer_pub,
        "boot_hash": "boot",
        "pid_namespace": "ns",
        "agents": {
            "TestAlpha": {"public_key": alpha_pub, "uid": 61001},
            "TestBeta": {"public_key": beta_pub, "uid": 61002},
        },
    }
    bundle = {"ca_public_key": ca_pub, "enrollment": HOST.sign(ca, registry)}
    trial = {
        "handshakes": [{"proof": proof, "receipt": HOST.sign(issuer, receipt)}],
        "lifecycle": {
            "perf_lost": 0,
            "submit_failures": 0,
            "records": [{"kind": 2, "pid": 8, "start": 50, "stamp": 80, "generation": 1}],
        },
    }
    capture = [
        {"ready": True, "boot_hash": "boot", "pid_namespace": "ns", "file": file},
        {
            "record": {
                "kind": 1,
                "tgid": 8,
                "start_ns": 50,
                "ppid": 7,
                "entry_ns": 200,
                "result": 16,
                "count": 16,
                **file,
            }
        },
        {
            "summary": {
                "stats": {str(k): int(k < 3) for k in range(8)},
                "perf_lost": 0,
                "pending": 0,
                "kprobe_profile": [["r_vfs_write", "1", "0"]],
            }
        },
    ]
    return bundle, capture, trial, ca_pub


def test_independent_signatures_and_exact_chain(signed_case):
    result = HOST.evaluate(*signed_case)
    assert result["chains"][0]["acting_authenticated_identity"] == "TestAlpha"
    assert not result["codex_authenticated"] and not result["grok_authenticated"]


def test_mutated_enrollment_rejected(signed_case):
    bundle, capture, trial, ca = signed_case
    bundle["enrollment"]["body"]["agents"]["TestAlpha"]["uid"] = 61002
    result = HOST.evaluate(bundle, capture, trial, ca)
    assert not result["enrollment_signature"]
    assert result["chains"][0]["acting_authenticated_identity"] is None


@pytest.mark.parametrize(
    "field,value", [("tgid", 9), ("start_ns", 51), ("inode", 5), ("result", 0), ("entry_ns", 700)]
)
def test_actor_instance_file_return_expiry_mismatch(signed_case, field, value):
    bundle, capture, trial, ca = signed_case
    capture[1]["record"][field] = value
    assert (
        HOST.evaluate(bundle, capture, trial, ca)["chains"][0]["acting_authenticated_identity"]
        is None
    )


def test_exec_generation_invalidates_previous_binding(signed_case):
    bundle, capture, trial, ca = signed_case
    trial["lifecycle"]["records"].append(
        {"kind": 2, "pid": 8, "start": 50, "stamp": 180, "generation": 2}
    )
    assert (
        HOST.evaluate(bundle, capture, trial, ca)["chains"][0]["acting_authenticated_identity"]
        is None
    )


def test_signature_alteration_cannot_authenticate(signed_case):
    bundle, capture, trial, ca = signed_case
    trial["handshakes"][0]["proof"]["body"]["claimed_identity"] = "TestBeta"
    assert (
        HOST.evaluate(bundle, capture, trial, ca)["chains"][0]["acting_authenticated_identity"]
        is None
    )


def test_wrong_ca_pin_no_chain(signed_case):
    bundle, capture, trial, _ = signed_case
    assert (
        HOST.evaluate(bundle, capture, trial, PROTOCOL.b64(bytes(32)))["chains"][0][
            "acting_authenticated_identity"
        ]
        is None
    )


def test_lifecycle_loss_unknown(signed_case):
    bundle, capture, trial, ca = signed_case
    trial["lifecycle"]["perf_lost"] = 1
    assert (
        HOST.evaluate(bundle, capture, trial, ca)["chains"][0]["identity_effect_chain"]
        == "UNBEKANNT"
    )


def test_public_copy_not_signature(signed_case):
    bundle, capture, trial, ca = signed_case
    trial["handshakes"][0]["receipt"]["signature"] = PROTOCOL.b64(bytes(64))
    assert (
        HOST.evaluate(bundle, capture, trial, ca)["chains"][0]["acting_authenticated_identity"]
        is None
    )


def test_incomplete_evidence_conservative():
    assert HOST.evaluate({}, [], {}, "x")["identity_effect_chain"] == "UNBEKANNT"


def test_proof_message_is_not_silently_modified(signed_case):
    before = copy.deepcopy(signed_case)
    HOST.evaluate(*signed_case)
    assert before == signed_case
