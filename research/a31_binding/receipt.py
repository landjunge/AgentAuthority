"""Independent local attestor verifier; never classifies host signatures as provider proofs."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify
from protocol import canonical

PINS = {
    "Codex": {
        "team": "2DC432GLL2",
        "identifier": "codex",
        "cdhash": "e14a40abbb6e7f524291a0cc7a3d4ca83e5eff18",
        "binary_sha256": "f86b8cfd3de94dc70763d251da3ff292e94f4a53ad41b81faab3619a7bcb626c",
    },
    "Grok": {
        "team": "5Y6N3AJ54S",
        "identifier": "xai-grok-pager",
        "cdhash": "baaf319d3348a74f7644e10590efa030bcb67ffa",
        "binary_sha256": "5ff2b912da2d85cdc627595d819423751bab67fcb65870f90a0783cccba5c62a",
    },
}
INSTANCE = ["pid", "start_sec", "start_usec", "boot_sec", "path"]


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check(signed, pinned_ca, expected, job, now_ns, used, consume=True):
    """Expected channel/challenge/instance comes from separate controller state."""
    reasons = []
    try:
        body = signed["body"]
        probe = body["process_probe"]
        pin = PINS[expected["client"]]
        checks = {
            "host_signature": verify(pinned_ca, signed),
            "domain": body["domain"] == "A31-LOCAL-CLIENT-JOB-v1",
            "trust_scope": body["scope"] == "local_host_attestation_not_provider",
            "client": body["client"] == expected["client"],
            "channel": body["channel_id"] == expected["channel_id"],
            "challenge": body["challenge"] == expected["challenge"] == job["nonce"],
            "job_digest": body["job_sha256"] == digest(job),
            "instance": all(probe[k] == expected["process_instance"][k] for k in INSTANCE),
            "owned_spawn": probe["pid"] == expected["spawn_pid"]
            and probe["ppid"] == expected["host_controller_pid"]
            and probe["uid"] == expected["uid"],
            "dynamic_code_valid": probe["guest_status"]
            == probe["requirement_status"]
            == probe["validity_status"]
            == probe["signing_info_status"]
            == 0,
            "kernel_start_stable": probe["kernel_instance_stable"]
            and probe["boot_read_status"] == 0,
            "code_pin": all(probe[k] == pin[k] for k in ["team", "identifier", "cdhash"])
            and body["client_binary_sha256"] == pin["binary_sha256"],
            "time": body["issued_ns"] <= now_ns < body["expires_ns"]
            and body["expires_ns"] - body["issued_ns"] == 180_000_000_000,
            "anti_replay": body["receipt_id"] not in used,
            "job_kind": job["operation"] == "write16",
            "successful_client": body["client_exit"] == 0 and body["qualified_response"],
        }
        reasons = [name for name, value in checks.items() if not value]
        if not reasons and consume:
            used.add(body["receipt_id"])
    except (KeyError, TypeError, ValueError):
        reasons = ["malformed or incomplete evidence"]
        checks = {}
    return {
        "qualified": not reasons,
        "checks": checks,
        "reasons": reasons,
        "local_client_job_binding": "BELEGT" if not reasons else "UNBEKANNT",
        "provider_session_job_binding": "UNBEKANNT",
        "model_identity": "UNBEKANNT",
    }
