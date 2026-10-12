"""Mutations of the actual100-agent archive; no new agents or kernel writes."""

import copy
import functools
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/a4-final-runs/2026-10-12"
SPEC = importlib.util.spec_from_file_location("a4_scale_join", ROOT / "research/a4_scale/join.py")
assert SPEC and SPEC.loader
JOIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(JOIN)


@pytest.fixture(scope="module", autouse=True)
def signature_cache():
    original = JOIN.verify

    @functools.lru_cache(maxsize=4096)
    def cached(public, serialized):
        return original(public, json.loads(serialized))

    # Cache only exact public-key/envelope pairs; modified signed content causes
    # a fresh independent OpenSSL verification. No boolean signature stubs.
    JOIN.verify = lambda public, signed: cached(public, json.dumps(signed, sort_keys=True))
    yield
    JOIN.verify = original


@pytest.fixture(scope="module")
def archive():
    out = DATA / "phase2"
    return (
        json.loads((out / "registry.json").read_text()),
        [json.loads(row) for row in (out / "capture.jsonl").read_text().splitlines()],
        json.loads((out / "trial-result.json").read_text()),
        json.loads((out / "pins.json").read_text())["ca_public_key"],
    )


def test_actual_fresh_gate_has_no_unknown_critical_metrics():
    gate = json.loads((DATA / "phase1/evaluation.json").read_text())
    assert gate["full_chain_gate"] == "BELEGT" and gate["phase2_authorized_by_gate"]
    assert len(gate["checks"]) == 26 and all(gate["checks"].values())
    assert len(gate["critical_loss_metrics"]) == 23
    assert JOIN.measured_zero(gate["critical_loss_metrics"])


def test_actual100_agent_experiment_matches_independent_archive(archive):
    result = JOIN.evaluate(*archive)
    saved = json.loads((DATA / "phase2/independent-join.json").read_text())
    assert result == saved
    assert result["experiment_passed"] and result["full_chains_verified"] == 99
    assert len(result["bindings"]) == 100 and result["false_positive_assignments"] == 0
    assert result["metrics"]["max_tree_depth"] == 6
    assert result["metrics"]["max_inflight_delegations"] == 37
    assert result["metrics"]["max_overlapping_kernel_writes"] == 2
    assert result["provider_model_session_identity"] == "UNBEKANNT"


@pytest.mark.parametrize("value", [None, False, True, "0", -1, 1])
def test_unknown_or_noninteger_loss_never_passes(value):
    assert not JOIN.measured_zero({"write_entry": value})


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_ca",
        "wrong_start",
        "missing_write",
        "duplicate_write",
        "missing_exit",
        "lost_event",
        "unknown_entry",
        "map_failure",
        "wrong_parent",
        "wrong_uid",
        "expired_write",
        "replay_forwarded",
        "foreign_forwarded",
        "refusal_released",
        "wrong_root_witness",
    ],
)
def test_modified_actual_evidence_is_not_a_successful_scale_result(archive, mutation):
    bundle, capture, trial, pin = copy.deepcopy(archive)
    write = next(row["record"] for row in capture if row.get("record", {}).get("kind") == 1)
    summary = next(row["summary"] for row in capture if "summary" in row)
    if mutation == "wrong_ca":
        pin = bundle["registry"]["body"]["agents"]["Agent099"]["public_key"]
    elif mutation == "wrong_start":
        write["start_ns"] += 1
    elif mutation == "missing_write":
        capture = [row for row in capture if row.get("record") is not write]
    elif mutation == "duplicate_write":
        capture.append({"record": copy.deepcopy(write)})
    elif mutation == "missing_exit":
        trial["lifecycle"]["records"] = [
            row for row in trial["lifecycle"]["records"] if row["kind"] != 3
        ]
    elif mutation == "lost_event":
        summary["perf_lost"] = 1
    elif mutation == "unknown_entry":
        summary["entry_nmissed"] = None
    elif mutation == "map_failure":
        trial["lifecycle"]["map_update_failures"] = 1
    elif mutation == "wrong_parent":
        row = next(
            row for row in trial["rows"] if row["delegation"]["body"]["parent_link"] is not None
        )
        row["delegation"]["body"]["parent_link"]["delegation_sha256"] = "0" * 64
    elif mutation == "wrong_uid":
        trial["rows"][0]["sender_credentials"]["uid"] += 1
    elif mutation == "expired_write":
        row = next(
            row
            for row in trial["rows"]
            if row["delegation"]["body"]["receiver_instance"]["pid"] == write["tgid"]
        )
        write["entry_ns"] = row["delegation"]["body"]["expires_ns"]
    elif mutation == "replay_forwarded":
        next(row for row in trial["negatives"] if row["case"] == "replay")["forwarded"] = True
    elif mutation == "foreign_forwarded":
        next(row for row in trial["negatives"] if row["case"] == "foreign_claim")["forwarded"] = (
            True
        )
    elif mutation == "refusal_released":
        next(row for row in trial["negatives"] if row["case"] == "refuse")["released"] = True
    elif mutation == "wrong_root_witness":
        trial["rows"][0]["receipt"]["body"]["run_id"] = "foreign"
    result = JOIN.evaluate(bundle, capture, trial, pin)
    assert not result["experiment_passed"] and result["full_chains_verified"] is None
    assert result["false_positive_assignments"] is None


def test_four_real_negative_cases_cannot_be_counted_as_full_effect_chains(archive):
    result = JOIN.evaluate(*archive)
    assert len(result["negative_checks"]) == 4
    assert all(
        row["passed"] and not row["complete_effect_chain"] for row in result["negative_checks"]
    )
    assert result["intentionally_incomplete_chains"] == result["rejected_message_cases"] == 2


def test_rss_sum_is_never_claimed_as_whole_vm_memory(archive):
    result = JOIN.evaluate(*archive)
    assert not result["metrics"]["rss_sum_is_physical_vm_memory"]
    assert result["metrics"]["whole_vm_kernel_cpu_overhead"] is None
    assert result["metrics"]["actual_pid_reuse"] is None
