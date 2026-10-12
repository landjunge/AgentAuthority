"""Independent host/OpenSSL join; unknown loss metrics never pass scaling gate."""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify as signature
from protocol import canonical


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def scaling_gate(checks, loss):
    return (
        bool(checks)
        and all(value is True for value in checks.values())
        and bool(loss)
        and all(type(value) is int and value == 0 for value in loss.values())
    )


def evaluate(bundle, capture, trial, pinned_ca):
    registry = bundle["registry"]["body"]
    receipt = trial["receipt"]
    witness = receipt["body"]
    delegation, acceptance = witness["delegation"], witness["acceptance"]
    job, accept = delegation["body"], acceptance["body"]
    ready = next(row for row in capture if row.get("ready"))
    summary = next(row["summary"] for row in capture if "summary" in row)
    writes = [row["record"] for row in capture if row.get("record", {}).get("kind") == 1]
    life = trial["lifecycle"]
    checks = {
        "registry_signature_and_pin": bundle["ca_public_key"] == pinned_ca
        and signature(pinned_ca, bundle["registry"]),
        "exactly_two_test_principals": set(registry["agents"]) == {"TestA", "TestB"}
        and registry["test_identities_only"] is True,
        "separate_keys_and_uids": registry["agents"]["TestA"]["public_key"]
        != registry["agents"]["TestB"]["public_key"]
        and registry["agents"]["TestA"]["uid"] != registry["agents"]["TestB"]["uid"],
        "witness_signature": signature(registry["registrar_public_key"], receipt),
        "sender_signature": signature(registry["agents"]["TestA"]["public_key"], delegation),
        "receiver_signature": signature(registry["agents"]["TestB"]["public_key"], acceptance),
        "domain_and_scope": registry["domain"] == "A4-REGISTRY-v1"
        and witness["domain"] == "A4-TRANSPORT-WITNESS-v1"
        and job["domain"] == "A4-DELEGATION-v1"
        and accept["domain"] == "A4-ACCEPT-v1"
        and job["sender"] == "TestA"
        and job["receiver"] == accept["identity"] == "TestB"
        and job["run_id"] == witness["run_id"] == registry["run_id"]
        and job["boot_hash"] == registry["boot_hash"] == ready["boot_hash"]
        and job["pid_namespace"] == registry["pid_namespace"] == ready["pid_namespace"],
        "job_digest": job["job_digest"] == digest(job["job"])
        and job["job"]["operation"] == "write16"
        and job["job"]["file"] == ready["file"],
        "accepts_exact_delegation": accept["delegation_sha256"] == digest(delegation)
        and accept["delegation_id"] == job["delegation_id"],
        "fresh_nonce_fields": all(
            len(bytes.fromhex(value)) == 32
            for value in [job["nonce"], job["delegation_id"], accept["nonce"]]
        )
        and len({job["nonce"], job["delegation_id"], accept["nonce"]}) == 3,
        "handover_order": job["issued_ns"]
        <= witness["received_ns"]
        <= witness["forwarded_ns"]
        <= accept["accepted_ns"]
        <= witness["accepted_ns"]
        <= witness["release_ns"]
        < job["expires_ns"]
        and job["expires_ns"] - job["issued_ns"] == 5_000_000_000,
        "exactly_one_target_write": len(writes) == 1,
    }
    for name, role in [("TestA", "sender"), ("TestB", "receiver")]:
        binding = witness["bindings"][name]
        proof = binding["proof"]
        instance = job[role + "_instance"]
        cred = witness[role + "_credentials"]
        oracle = trial["oracle"][name]
        checks[name + "_proof"] = (
            signature(registry["agents"][name]["public_key"], proof)
            and proof["body"]["identity"] == name
            and proof["body"]["domain"] == "A4-POP-v1"
            and proof["body"]["challenge"]["instance"] == instance
            and proof["body"]["challenge"]["agents"] == registry["agents"]
            and proof["body"]["challenge"]["run_id"] == registry["run_id"]
            and proof["body"]["challenge"]["boot_hash"] == registry["boot_hash"]
            and proof["body"]["challenge"]["pid_namespace"] == registry["pid_namespace"]
        )
        checks[name + "_credentials"] = (
            cred
            == binding["credentials"]
            == {
                "pid": instance["pid"],
                "uid": registry["agents"][name]["uid"],
                "gid": registry["agents"][name]["uid"],
            }
            and binding["kernel_instance"]["start_ns"] == instance["start_ns"]
            and binding["kernel_instance"]["generation"] == instance["generation"] == 1
            and binding["bound_ns"] < job["issued_ns"]
        )
        ticks = oracle["proc_before"]["start_ticks"]
        checks[name + "_oracle"] = (
            oracle["spawn_pid"] == instance["pid"]
            and oracle["uid"] == cred["uid"]
            and ticks == oracle["proc_after_acceptance"]["start_ticks"]
            and instance["start_ns"] // 10_000_000 == ticks
            and oracle["kernel_after_acceptance"]["start_ns"] == instance["start_ns"]
            and oracle["kernel_after_acceptance"]["generation"] == 1
            and oracle["exit_code"] == 0
            and oracle["pidfd_exited"] is True
        )
        records = [
            r
            for r in life["records"]
            if r["pid"] == instance["pid"] and r["start"] == instance["start_ns"]
        ]
        checks[name + "_lifecycle"] = (
            [r["kind"] for r in records] == [1, 2, 3]
            and records[1]["generation"] == 1
            and records[0]["stamp"] <= records[1]["stamp"] <= binding["bound_ns"]
            and records[2]["stamp"] > witness["release_ns"]
        )
    checks["acceptance_process"] = accept["instance"] == job["receiver_instance"]
    if len(writes) == 1:
        write = writes[0]
        instance = job["receiver_instance"]
        result = trial["oracle"]["TestB"]["result"]
        checks["write_process_file_time"] = (
            write["tgid"] == instance["pid"]
            and write["start_ns"] == instance["start_ns"]
            and write["boot_hash"] == registry["boot_hash"]
            and {k: write[k] for k in ["dev", "inode"]} == ready["file"]
            and witness["release_ns"]
            <= result["before_ns"]
            <= write["entry_ns"]
            <= write["exit_ns"]
            <= result["after_ns"]
            < job["expires_ns"]
            and write["result"] == write["count"] == result["result"] == 16
            and result["pid"] == instance["pid"]
            and result["role"] == "TestB"
        )
    else:
        checks["write_process_file_time"] = False
    checks["sender_oracle_no_write"] = trial["oracle"]["TestA"]["result"] == {
        "role": "TestA",
        "delegation_sha256": digest(delegation),
        "writes": 0,
    }
    stats = summary["stats"]
    checks["count_reference_concordance"] = (
        stats["0"] == stats["1"] == stats["2"] == len(writes) == 1
    )
    profiles = summary["kprobe_profile"]
    loss = {
        "write_entry_nmissed": summary["entry_probe_nmissed"],
        "fork_entry_nmissed": life["fork_entry_nmissed"],
        "return_nmissed": sum(int(row[-1]) for row in profiles) if profiles else None,
        "write_perf_lost": summary["perf_lost"],
        "pending": summary["pending"],
        "write_submit_failures": stats["3"],
        "pending_overwrite": stats["4"],
        "pending_map_failures": stats["5"],
        "exit_submit_failures": stats["7"],
        "lifecycle_perf_lost": life["perf_lost"],
        "lifecycle_submit_failures": life["submit_failures"],
        "lifecycle_map_update_failures": life["map_update_failures"],
        "lifecycle_probe_read_failures": life["probe_read_failures"],
        "lifecycle_invalid_fields": life["invalid_instance_fields"],
        "observer_probe_read_failures": stats["9"],
        "observer_seen_update_failures": stats["8"],
        "observer_delete_failures": stats["10"],
    }
    checks["classic_profile_present"] = (
        summary["classic_profile"]["complete"] and life["classic_profile"]["complete"]
    )
    programs = {"write_" + n: p for n, p in summary["program_info"].items()}
    programs.update({"life_" + n: p for n, p in life["program_info"].items()})
    checks["program_info_present"] = (
        len(summary["program_info"]) == 3 and len(life["program_info"]) == 3
    )
    loss.update({n + "_recursion_misses": p["recursion_misses"] for n, p in programs.items()})
    passed = scaling_gate(checks, loss)
    return {
        "checks": checks,
        "critical_loss_metrics": loss,
        "observed_component_checks_pass": all(v is True for v in checks.values()),
        "phase1_classification": "BELEGT"
        if passed
        else "TEILWEISE BELEGT"
        if checks["write_process_file_time"]
        else "UNBEKANNT",
        "full_chain_gate": "BELEGT" if passed else "UNBEKANNT",
        "phase2_authorized_by_gate": passed,
        "phase2_executed": False,
        "provider_model_session_identity": "UNBEKANNT",
        "false_positive_assignments": 0 if all(v is True for v in checks.values()) else None,
        "bounded_observed_candidate_chains": 1 if all(v is True for v in checks.values()) else 0,
        "latency_ns": witness["accepted_ns"] - job["issued_ns"],
        "throughput": None,
        "kernel_vm_cpu_ram": None,
        "unresolved_metrics": [k for k, v in loss.items() if v is None],
    }
