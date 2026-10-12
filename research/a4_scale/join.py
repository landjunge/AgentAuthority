"""Independent OpenSSL verification of actual scale evidence, no actor-claim trust."""

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify
from protocol import canonical


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def measured_zero(values):
    return bool(values) and all(type(value) is int and value == 0 for value in values.values())


def losses(summary, life):
    stats = summary["stats"]
    values = {
        "write_entry_nmissed": summary["entry_nmissed"],
        "fork_entry_nmissed": life["fork_entry_nmissed"],
        "write_perf_lost": summary["perf_lost"],
        "pending": summary["pending"],
        "lifecycle_perf_lost": life["perf_lost"],
        "lifecycle_submit_failures": life["submit_failures"],
        "lifecycle_map_update_failures": life["map_update_failures"],
        "lifecycle_probe_read_failures": life["probe_read_failures"],
        "lifecycle_invalid_fields": life["invalid_instance_fields"],
    }
    values.update(
        {"observer_stats_" + key: stats[key] for key in ["3", "4", "5", "7", "8", "9", "10", "11"]}
    )
    selected = summary["classic_profile"]["selected"]
    returns = [v["misses"] for k, v in selected.items() if k.startswith("r_vfs_write_bcc_")]
    values["return_nmissed"] = returns[0] if len(returns) == 1 else None
    for prefix, source in [("write", summary), ("life", life)]:
        values.update(
            {
                prefix + "_" + name + "_recursion_misses": value["recursion_misses"]
                for name, value in source["program_info"].items()
            }
        )
    return values


def nonce(value):
    try:
        return len(bytes.fromhex(value)) == 32
    except (TypeError, ValueError):
        return False


def latency(values):
    ordered = sorted(values)
    return {
        "count": len(values),
        "min_ns": ordered[0],
        "median_ns": statistics.median(values),
        "mean_ns": statistics.mean(values),
        "p95_nearest_rank_ns": ordered[math.ceil(0.95 * len(values)) - 1],
        "max_ns": ordered[-1],
    }


def max_overlap(intervals):
    events = sorted([(start, 1) for start, _ in intervals] + [(end, -1) for _, end in intervals])
    active, maximum = 0, 0
    for _, delta in events:
        active += delta
        maximum = max(active, maximum)
    return maximum


def evaluate(bundle, capture, trial, pin):
    registry = bundle["registry"]["body"]
    agents = registry["agents"]
    ready = next(row for row in capture if row.get("ready"))
    summary = next(row["summary"] for row in capture if "summary" in row)
    life = trial["lifecycle"]
    writes = [row["record"] for row in capture if row.get("record", {}).get("kind") == 1]
    exits = [row["record"] for row in capture if row.get("record", {}).get("kind") == 2]
    expected = {f"Agent{i:03}" for i in range(100)}
    by_receiver = {row["delegation"]["body"]["receiver"]: row for row in trial["rows"]}
    loss = losses(summary, life)
    stats = summary["stats"]
    checks = {
        "registry_signature_and_pin": bundle["ca_public_key"] == pin
        and verify(pin, bundle["registry"]),
        "exactly100_test_principals": set(agents)
        == set(trial["bindings"])
        == set(trial["oracle"])
        == expected
        and registry["test_identities_only"] is True
        and trial["agent_count"] == 100,
        "distinct_keys_uids_instances": len({a["public_key"] for a in agents.values()})
        == len({a["uid"] for a in agents.values()})
        == len({b["instance"]["pid"] for b in trial["bindings"].values()})
        == len({b["instance"]["start_ns"] for b in trial["bindings"].values()})
        == 100,
        "registry_scope": registry["domain"] == "A4-SCALE-REGISTRY-v1"
        and registry["boot_hash"] == ready["boot_hash"]
        and registry["pid_namespace"] == ready["pid_namespace"]
        and registry["clock_ticks"] == 100,
        "file_reference_set": len(ready["files"])
        == len({(f["dev"], f["inode"]) for f in ready["files"]})
        == 100
        and {(f["dev"], f["inode"]) for f in ready["files"]}
        == {(o["file"]["dev"], o["file"]["inode"]) for o in trial["oracle"].values()},
        "classic_profiles_present": summary["classic_profile"]["complete"]
        and life["classic_profile"]["complete"]
        and len(summary["classic_profile"]["selected"]) == 2
        and len(life["classic_profile"]["selected"]) == 1,
        "program_metadata_present": len(summary["program_info"]) == len(life["program_info"]) == 3,
        "all_critical_losses_measured_zero": measured_zero(loss),
        "collector_stopped_after_actors": summary["stop_seen"] is True,
        "positive_reference_count": len(trial["rows"]) == len(by_receiver) == 99
        and set(by_receiver) == expected - {"Agent000"},
        "kernel_target_count": len(writes) == stats["0"] == stats["1"] == stats["2"] == 99
        and len(exits) == stats["6"] == 99,
        "no_duplicate_kernel_writes": len(
            {(e["tgid"], e["start_ns"], e["entry_ns"], e["dev"], e["inode"]) for e in writes}
        )
        == len(writes),
        "lifecycle_reference_count": len(life["records"]) == 300,
    }
    binding_checks = {}
    for name in sorted(expected):
        binding, oracle = trial["bindings"][name], trial["oracle"][name]
        instance, proof = binding["instance"], binding["proof"]
        challenge = proof["body"]["challenge"]
        records = sorted(
            [
                r
                for r in life["records"]
                if r["pid"] == instance["pid"] and r["start"] == instance["start_ns"]
            ],
            key=lambda r: r["stamp"],
        )
        cred = {"pid": instance["pid"], "uid": agents[name]["uid"], "gid": agents[name]["uid"]}
        points = {
            "proof_signature": verify(agents[name]["public_key"], proof),
            "challenge_scope": proof["body"]["domain"] == "A4-SCALE-POP-v1"
            and proof["body"]["identity"] == name
            and challenge["domain"] == "A4-SCALE-CHALLENGE-v1"
            and challenge["instance"] == instance
            and challenge["run_id"] == registry["run_id"]
            and challenge["boot_hash"] == registry["boot_hash"]
            and challenge["pid_namespace"] == registry["pid_namespace"]
            and nonce(challenge["nonce"]),
            "credentials_oracle_instance": binding["credentials"] == cred
            and oracle["spawn_pid"] == instance["pid"]
            and oracle["uid"] == cred["uid"]
            and oracle["proc_before"]["pid"] == oracle["proc_after"]["pid"] == instance["pid"]
            and oracle["proc_before"]["start_ticks"]
            == oracle["proc_after"]["start_ticks"]
            == instance["start_ns"] // 10_000_000
            and oracle["kernel_after"]["start_ns"] == instance["start_ns"]
            and oracle["kernel_after"]["generation"] == instance["generation"] == 1
            and oracle["pidfd_exited"] is True,
            "lifecycle": len(records) == 3
            and [r["kind"] for r in records] == [1, 2, 3]
            and records[1]["generation"] == records[2]["generation"] == 1
            and records[1]["uid"] == records[2]["uid"] == agents[name]["uid"]
            and records[1]["stamp"] <= binding["bound_ns"] < records[2]["stamp"],
            "exit_reference": oracle["exit_code"] == (-15 if name == "Agent099" else 0),
        }
        binding_checks[name] = points
    checks["all100_bindings_verified"] = all(all(p.values()) for p in binding_checks.values())
    checks["all_challenge_nonces_distinct"] = (
        len({b["proof"]["body"]["challenge"]["nonce"] for b in trial["bindings"].values()}) == 100
    )
    chains, chain_pass, issue_accept, issue_write, depths = [], {}, [], [], {"Agent000": 0}
    used_events = set()
    identifiers, job_nonces, acceptance_nonces = set(), set(), set()
    for row in sorted(trial["rows"], key=lambda r: r["delegation"]["body"]["issued_ns"]):
        signed, accepted = row["delegation"], row["acceptance"]
        body, accept = signed["body"], accepted["body"]
        sender, receiver = body["sender"], body["receiver"]
        receiver_instance = trial["bindings"][receiver]["instance"]
        candidates = [
            (index, event)
            for index, event in enumerate(writes)
            if event["tgid"] == receiver_instance["pid"]
            and event["start_ns"] == receiver_instance["start_ns"]
            and {k: event[k] for k in ["dev", "inode"]} == body["job"]["file"]
            and body["issued_ns"] <= event["entry_ns"] < body["expires_ns"]
        ]
        witness_fields = [
            "delegation",
            "sender_credentials",
            "received_ns",
            "forwarded_ns",
            "acceptance",
            "receiver_credentials",
            "accepted_ns",
            "release_ns",
        ]
        points = {
            "sender_signature": verify(agents[sender]["public_key"], signed),
            "recipient_signature": verify(agents[receiver]["public_key"], accepted),
            "witness_signature_and_content": verify(
                registry["registrar_public_key"], row["receipt"]
            )
            and row["receipt"]["body"]
            == {
                "domain": "A4-SCALE-WITNESS-v1",
                "run_id": registry["run_id"],
                **{key: row[key] for key in witness_fields},
            },
            "scope_and_instances": body["domain"] == "A4-SCALE-DELEGATION-v1"
            and body["run_id"] == registry["run_id"]
            and body["boot_hash"] == ready["boot_hash"]
            and body["pid_namespace"] == ready["pid_namespace"]
            and body["sender_instance"] == trial["bindings"][sender]["instance"]
            and body["receiver_instance"] == receiver_instance,
            "fresh_digest_nonce": body["job_digest"] == digest(body["job"])
            and body["job"]["operation"] == "write16"
            and nonce(body["nonce"])
            and nonce(body["delegation_id"])
            and nonce(accept["nonce"])
            and body["nonce"] not in job_nonces
            and body["delegation_id"] not in identifiers
            and accept["nonce"] not in acceptance_nonces,
            "actual_senders": row["sender_credentials"] == trial["bindings"][sender]["credentials"]
            and row["receiver_credentials"]
            == row["done_credentials"]
            == trial["bindings"][receiver]["credentials"],
            "accepts_exact_job": accept["domain"] == "A4-SCALE-ACCEPT-v1"
            and accept["identity"] == receiver
            and accept["instance"] == receiver_instance
            and accept["delegation_sha256"] == digest(signed)
            and accept["delegation_id"] == body["delegation_id"],
            "handover_time": ready["ready_ns"]
            <= body["issued_ns"]
            <= row["received_ns"]
            <= row["forwarded_ns"]
            <= accept["accepted_ns"]
            <= row["accepted_ns"]
            <= row["release_ns"]
            < body["expires_ns"]
            and body["expires_ns"] - body["issued_ns"] == 5_000_000_000,
            "one_independent_effect": len(candidates) == 1,
            "tree_parent": sender == f"Agent{(int(receiver[-3:]) - 1) // 2:03}",
        }
        if sender == "Agent000":
            points["verified_multistage_parent"] = body["parent_link"] is None
        else:
            parent = by_receiver[sender]
            points["verified_multistage_parent"] = (
                chain_pass.get(sender, False)
                and body["parent_link"]
                == {
                    "delegation_sha256": digest(parent["delegation"]),
                    "acceptance_sha256": digest(parent["acceptance"]),
                }
                and parent["done_received_ns"] <= body["issued_ns"]
            )
        if len(candidates) == 1:
            index, event = candidates[0]
            done = row["done"]
            points["write_file_return_time_reference"] = (
                event["boot_hash"] == ready["boot_hash"]
                and event["ppid"] == receiver_instance["parent"]
                and event["count"] == event["result"] == done["result"] == 16
                and body["job"]["file"] == trial["oracle"][receiver]["file"] == done["file"]
                and done["pid"] == receiver_instance["pid"]
                and done["delegation_id"] == body["delegation_id"]
                and row["release_ns"]
                <= done["before_ns"]
                <= event["entry_ns"]
                <= event["exit_ns"]
                <= done["after_ns"]
                <= row["done_received_ns"]
                and done["after_ns"] < body["expires_ns"]
            )
            points["unique_event_assignment"] = index not in used_events
            used_events.add(index)
            issue_accept.append(row["accepted_ns"] - body["issued_ns"])
            issue_write.append(event["entry_ns"] - body["issued_ns"])
        else:
            points["write_file_return_time_reference"] = points["unique_event_assignment"] = False
        valid = (
            all(points.values())
            and all(binding_checks[sender].values())
            and all(binding_checks[receiver].values())
        )
        chain_pass[receiver] = valid
        depths[receiver] = depths.get(sender, -100) + 1
        identifiers.add(body["delegation_id"])
        job_nonces.add(body["nonce"])
        acceptance_nonces.add(accept["nonce"])
        chains.append(
            {
                "delegation_id": body["delegation_id"],
                "sender": sender,
                "receiver": receiver,
                "depth": depths[receiver],
                "checks": points,
                "component_chain_verified": valid,
            }
        )
    checks["all99_positive_chains_verified"] = len(chains) == 99 and all(chain_pass.values())
    checks["all_kernel_writes_assigned_once"] = len(used_events) == len(writes) == 99
    checks["writer_exit_reference"] = len({(e["tgid"], e["start_ns"]) for e in exits}) == 99 and {
        (e["tgid"], e["start_ns"]) for e in exits
    } == {(e["tgid"], e["start_ns"]) for e in writes}
    negative_checks = []
    for row in trial["negatives"]:
        points = {
            "registrar_witness": verify(registry["registrar_public_key"], row["receipt"])
            and row["receipt"]["body"]
            == {
                "domain": "A4-SCALE-NEGATIVE-WITNESS-v1",
                **{k: v for k, v in row.items() if k != "receipt"},
            }
        }
        if row["case"] == "replay":
            signed = row["packet"]["value"]
            body = signed["body"]
            original = next(
                r
                for r in trial["rows"]
                if r["delegation"]["body"]["delegation_id"] == body["delegation_id"]
            )
            points.update(
                valid_original_signature=verify(agents[body["sender"]]["public_key"], signed),
                exact_replay=signed == original["delegation"],
                nonce_consumed=body["nonce"] in job_nonces and row["nonce_already_used"] is True,
                actual_sender=row["credentials"]
                == trial["bindings"][body["sender"]]["credentials"],
                fresh_window=body["issued_ns"] <= row["observed_ns"] < body["expires_ns"],
                no_forward=row["forwarded"] is False,
            )
        elif row["case"] == "foreign_claim":
            signed = row["packet"]["value"]
            points.update(
                actual_key_signature=verify(agents["Agent099"]["public_key"], signed),
                foreign_claim_fails=not verify(agents["Agent001"]["public_key"], signed)
                and signed["body"]["sender"] == "Agent001",
                actual_sender=row["credentials"] == trial["bindings"]["Agent099"]["credentials"],
                no_forward=row["forwarded"] is False,
            )
        else:
            signed, response = row["delegation"], row["response"]["value"]
            body, accept = signed["body"], response["body"]
            points.update(
                sender_signature=verify(agents[body["sender"]]["public_key"], signed),
                receiver_signature=verify(agents[body["receiver"]]["public_key"], response),
                response_binds_job=accept["delegation_sha256"] == digest(signed)
                and accept["delegation_id"] == body["delegation_id"]
                and accept["instance"] == trial["bindings"][body["receiver"]]["instance"],
                actual_senders=row["sender_credentials"]
                == trial["bindings"][body["sender"]]["credentials"]
                and row["receiver_credentials"]
                == trial["bindings"][body["receiver"]]["credentials"],
                no_release=row["released"] is False,
                no_new_effect=not any(
                    {k: e[k] for k in ["dev", "inode"]} == body["job"]["file"]
                    and e["entry_ns"] >= body["issued_ns"]
                    for e in writes
                ),
            )
            if row["case"] == "refuse":
                points["signed_refusal"] = (
                    accept["domain"] == "A4-SCALE-REFUSE-v1"
                    and row["response"]["type"] == "refusal"
                )
            else:
                points["accepted_then_interrupted"] = (
                    accept["domain"] == "A4-SCALE-ACCEPT-v1"
                    and row["response"]["type"] == "acceptance"
                    and row["interrupted_exit"] == trial["oracle"]["Agent099"]["exit_code"] == -15
                )
        negative_checks.append(
            {
                "case": row["case"],
                "checks": points,
                "passed": all(points.values()),
                "complete_effect_chain": False,
            }
        )
    checks["all_four_actual_negatives_verified"] = (
        {r["case"] for r in negative_checks} == {"replay", "foreign_claim", "refuse", "interrupt"}
        and len(negative_checks) == 4
        and all(r["passed"] for r in negative_checks)
    )
    passed = all(checks.values())
    start = min(r["delegation"]["body"]["issued_ns"] for r in trial["rows"])
    end = max(r["done_received_ns"] for r in trial["rows"])
    return {
        "classification": "BELEGT" if passed else "TEILWEISE BELEGT",
        "experiment_passed": passed,
        "checks": checks,
        "bindings": binding_checks,
        "chains": chains,
        "negative_checks": negative_checks,
        "critical_loss_metrics": loss,
        "agent_count": 100,
        "positive_jobs": 99,
        "full_chains_verified": 99
        if passed
        else sum(chain_pass.values())
        if measured_zero(loss)
        else None,
        "intentionally_incomplete_chains": 2,
        "rejected_message_cases": 2,
        "false_positive_assignments": 0 if passed else None,
        "missing_reference_writes": 99 - len(writes),
        "duplicated_kernel_events": len(writes)
        - len({(e["tgid"], e["start_ns"], e["entry_ns"]) for e in writes}),
        "metrics": {
            "pipeline_start_ns": start,
            "pipeline_end_ns": end,
            "pipeline_seconds": (end - start) / 1e9,
            "pipeline_jobs_per_second": 99 / ((end - start) / 1e9),
            "issue_to_acceptance": latency(issue_accept),
            "issue_to_kernel_write": latency(issue_write),
            "max_tree_depth": max(depths.values()),
            "max_inflight_delegations": max_overlap(
                [
                    (r["delegation"]["body"]["issued_ns"], r["done_received_ns"])
                    for r in trial["rows"]
                ]
            ),
            "max_overlapping_kernel_writes": max_overlap(
                [(e["entry_ns"], e["exit_ns"]) for e in writes]
            ),
            "observer_cpu_user_seconds": summary["cpu_user_seconds"],
            "observer_cpu_system_seconds": summary["cpu_system_seconds"],
            "observer_peak_rss_bytes": summary["rss_peak_bytes"],
            "registrar_cpu_user_seconds": trial["cpu_user_seconds"],
            "registrar_cpu_system_seconds": trial["cpu_system_seconds"],
            "registrar_peak_rss_bytes": trial["rss_peak_bytes"],
            "workers_cpu_user_seconds": trial["workers_cpu_user_seconds"],
            "workers_cpu_system_seconds": trial["workers_cpu_system_seconds"],
            "max_sampled_agent_rss_sum_bytes": max(
                r["sum_rss_bytes"] for r in trial["memory_samples"]
            ),
            "rss_sum_is_physical_vm_memory": False,
            "observer_raw_callback_bytes": summary["raw_bytes"],
            "lifecycle_raw_callback_bytes": life["callback_raw_bytes"],
            "whole_vm_kernel_cpu_overhead": None,
            "actual_pid_reuse": None,
        },
        "provider_model_session_identity": "UNBEKANNT",
        "trust": [
            "host CA",
            "root registrar/reference",
            "Linux kernel",
            "pinned controlled test code",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    pins = json.loads((args.output / "pins.json").read_text())
    result = evaluate(
        json.loads((args.output / "registry.json").read_text()),
        [json.loads(r) for r in (args.output / "capture.jsonl").read_text().splitlines()],
        json.loads((args.output / "trial-result.json").read_text()),
        pins["ca_public_key"],
    )
    (args.output / "independent-join.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(
        json.dumps(
            {
                "passed": result["experiment_passed"],
                "failed_checks": [k for k, v in result["checks"].items() if not v],
                "metrics": result["metrics"],
            }
        )
    )
