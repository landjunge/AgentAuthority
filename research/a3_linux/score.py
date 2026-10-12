"""Offline OpenSSL proof validation; local receipts never promote provider claims."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify
from protocol import canonical


def evaluate(bundle, capture, trial, packet, pinned_ca):
    try:
        return _evaluate(bundle, capture, trial, packet, pinned_ca)
    except (KeyError, TypeError, ValueError, StopIteration):
        return {
            "real_agent_effect_chain": "UNBEKANNT",
            "writes": [],
            "reason": "incomplete evidence",
        }


def _evaluate(bundle, capture, trial, packet, pinned_ca):
    reg = bundle["enrollment"]["body"]
    enrollment_ok = bundle["ca_public_key"] == pinned_ca and verify(pinned_ca, bundle["enrollment"])
    ready = next(row for row in capture if row.get("ready"))
    summary = next(row["summary"] for row in capture if "summary" in row)
    stats = summary["stats"]
    events = [row["record"] for row in capture if row.get("record", {}).get("kind") == 1]
    healthy = (
        summary["perf_lost"] == summary["pending"] == 0
        and all(stats[str(k)] == 0 for k in [3, 4, 5, 7])
        and stats["0"] == stats["1"] == stats["2"] == len(events)
        and bool(summary["kprobe_profile"])
        and all(int(row[-1]) == 0 for row in summary["kprobe_profile"])
        and trial["lifecycle"]["perf_lost"] == trial["lifecycle"]["submit_failures"] == 0
    )
    dispatches = {hashlib.sha256(canonical(job)).hexdigest(): job for job in packet["jobs"]}
    checks = []
    for entry in trial["handshakes"]:
        body = entry["receipt"]["body"]
        proof = entry["proof"]
        principal = next(
            (name for name, value in reg["agents"].items() if verify(value["public_key"], proof)),
            None,
        )
        dispatch = dispatches.get(proof["body"]["details"].get("host_dispatch_sha256"))
        fresh_dispatch = bool(
            dispatch
            and verify(pinned_ca, dispatch)
            and dispatch["body"]["domain"] == "A3-HOST-DISPATCH-v1"
            and dispatch["body"]["run_id"] == reg["run_id"]
            and dispatch["body"]["job"]["nonce"] in packet["active_nonces"]
            and dispatch["body"]["job"]["nonce"] == proof["body"]["details"].get("job_nonce")
        )
        checks.append(
            {
                "starter_signature": verify(reg["starter_public_key"], entry["receipt"]),
                "signature_principal": principal,
                "receipt_principal_matches": principal == body["credential_identity"],
                "proof_hash_matches": hashlib.sha256(canonical(proof)).hexdigest()
                == body["proof_sha256"],
                "fresh_challenge": proof["body"]["challenge"] == body["challenge"],
                "fresh_dispatch": fresh_dispatch,
                "dispatch_client_claim": dispatch["body"]["client"] if dispatch else None,
                "provider_authentication": "UNBEKANNT",
            }
        )
    writes = []
    for event in events:
        candidates = []
        file_ok = (
            {k: event[k] for k in ["dev", "inode"]} == ready["file"]
            and event["result"] == event["count"] == 16
            and event["entry_ns"] <= event["exit_ns"]
            and event["boot_hash"] == ready["boot_hash"] == reg["boot_hash"]
            and ready["pid_namespace"] == reg["pid_namespace"]
        )
        for index, (entry, check) in enumerate(zip(trial["handshakes"], checks, strict=True)):
            body = entry["receipt"]["body"]
            sender = body["message_sender"]
            identity = body["authenticated_identity"]
            if not (
                enrollment_ok
                and healthy
                and file_ok
                and all(
                    check[k]
                    for k in [
                        "starter_signature",
                        "receipt_principal_matches",
                        "proof_hash_matches",
                        "fresh_challenge",
                    ]
                )
                and body["instance_bound"]
                and identity == check["signature_principal"]
                and identity in reg["agents"]
                and sender["uid"] == reg["agents"][identity]["uid"]
                and body["domain"] == "A2-START-BINDING-v1"
                and body["run_id"] == body["challenge"]["run_id"] == reg["run_id"]
                and body["boot_hash"] == reg["boot_hash"]
                and body["pid_namespace"] == reg["pid_namespace"]
                and body["challenge"]["file"] == ready["file"]
                and sender["pid"] == event["tgid"]
                and sender["start_ns"] == event["start_ns"]
                and all(
                    sender[k] == body["challenge"]["instance"][k]
                    for k in ["pid", "start_ns", "generation"]
                )
                and body["attested_ns"]
                <= event["entry_ns"]
                <= body["challenge"]["issued_ns"] + body["challenge"]["expires_in_ns"]
            ):
                continue
            generations = [
                row
                for row in trial["lifecycle"]["records"]
                if row["kind"] == 2
                and row["pid"] == event["tgid"]
                and row["start"] == event["start_ns"]
                and row["stamp"] <= event["entry_ns"]
            ]
            if (
                generations
                and max(generations, key=lambda row: row["stamp"])["generation"]
                == sender["generation"]
            ):
                candidates.append((body["attested_ns"], index, identity))
        latest = max(candidates) if candidates else None
        writes.append(
            {
                "kernel_process": {k: event[k] for k in ["tgid", "start_ns", "tid", "ppid"]},
                "file": {k: event[k] for k in ["dev", "inode"]},
                "kernel_entry_ns": event["entry_ns"],
                "kernel_exit_ns": event["exit_ns"],
                "write": "BELEGT" if healthy and file_ok else "UNBEKANNT",
                "authenticated_local_wrapper": latest[2] if latest else None,
                "wrapper_effect_chain": "BELEGT" if latest else "UNBEKANNT",
                "fresh_host_dispatch": checks[latest[1]]["fresh_dispatch"] if latest else False,
                "client_claim": checks[latest[1]]["dispatch_client_claim"] if latest else None,
                "real_agent_effect_chain": "UNBEKANNT",
                "session_identity": "UNBEKANNT",
                "provider_identity": "UNBEKANNT",
                "model_identity": "UNBEKANNT",
            }
        )
    return {
        "enrollment_signature": enrollment_ok,
        "known_loss_checks": bool(healthy),
        "proof_checks": checks,
        "writes": writes,
        "real_agent_effect_chain": "UNBEKANNT",
        "partial_chain": "TEILWEISE BELEGT"
        if writes and all(row["write"] == "BELEGT" for row in writes)
        else "UNBEKANNT",
        "reason": "No externally authenticated client/session/provider credential in enrollment",
    }
