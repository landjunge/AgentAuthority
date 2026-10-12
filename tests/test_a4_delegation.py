"""Offline mutations of actual A4 evidence; no extra agents/kernel experiments."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/a4-delegation-runs/2026-10-12"
SPEC = importlib.util.spec_from_file_location(
    "a4_verify", ROOT / "research/a4_delegation/verify.py"
)
assert SPEC and SPEC.loader
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


@pytest.fixture()
def evidence():
    return (
        json.loads((DATA / "registry.json").read_text()),
        [json.loads(row) for row in (DATA / "capture.jsonl").read_text().splitlines()],
        json.loads((DATA / "trial.stdout.json").read_text()),
        json.loads((DATA / "pins.json").read_text())["pinned_ca_public_key"],
    )


def test_actual_delegation_components_pass_but_unknown_losses_block_scaling(evidence):
    result = VERIFIER.evaluate(*evidence)
    assert len(result["checks"]) == 24 and all(result["checks"].values())
    assert result["false_positive_assignments"] == 0
    assert result["full_chain_gate"] == "UNBEKANNT"
    assert not result["phase2_authorized_by_gate"]
    assert result["phase1_classification"] == "TEILWEISE BELEGT"
    assert result["provider_model_session_identity"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "metric", ["write_entry_nmissed", "fork_entry_nmissed", "lifecycle_map_update_failures"]
)
def test_each_unknown_loss_independently_prevents_gate(evidence, metric):
    result = VERIFIER.evaluate(*evidence)
    loss = {key: 0 for key in result["critical_loss_metrics"]}
    assert VERIFIER.scaling_gate(result["checks"], loss)
    loss[metric] = None
    assert not VERIFIER.scaling_gate(result["checks"], loss)


@pytest.mark.parametrize("value", [False, True, "0", -1, 1, None])
def test_non_measured_zero_or_positive_loss_never_passes(evidence, value):
    result = VERIFIER.evaluate(*evidence)
    loss = {key: 0 for key in result["critical_loss_metrics"]}
    loss["write_perf_lost"] = value
    assert not VERIFIER.scaling_gate(result["checks"], loss)


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_ca",
        "false_sender",
        "false_receiver",
        "same_pid_new_start",
        "exec_change",
        "file_change",
        "missing_write",
        "duplicate_write",
        "missing_exit",
        "expired_write",
        "wrong_credentials",
    ],
)
def test_altered_real_evidence_cannot_form_complete_candidate(evidence, mutation):
    bundle, capture, trial, pin = copy.deepcopy(evidence)
    witness = trial["receipt"]["body"]
    write = next(row["record"] for row in capture if row.get("record", {}).get("kind") == 1)
    if mutation == "wrong_ca":
        pin = bundle["registry"]["body"]["agents"]["TestB"]["public_key"]
    elif mutation == "false_sender":
        witness["delegation"]["body"]["sender"] = "TestB"
    elif mutation == "false_receiver":
        witness["acceptance"]["body"]["identity"] = "TestA"
    elif mutation == "same_pid_new_start":
        write["start_ns"] += 1
    elif mutation == "exec_change":
        trial["oracle"]["TestB"]["kernel_after_acceptance"]["generation"] = 2
    elif mutation == "file_change":
        write["inode"] += 1
    elif mutation == "missing_write":
        capture = [row for row in capture if row.get("record", {}).get("kind") != 1]
    elif mutation == "duplicate_write":
        capture.append({"record": copy.deepcopy(write)})
    elif mutation == "missing_exit":
        trial["lifecycle"]["records"] = [
            row for row in trial["lifecycle"]["records"] if row["kind"] != 3
        ]
    elif mutation == "expired_write":
        write["entry_ns"] = witness["delegation"]["body"]["expires_ns"]
    elif mutation == "wrong_credentials":
        witness["receiver_credentials"]["pid"] = witness["sender_credentials"]["pid"]
    result = VERIFIER.evaluate(bundle, capture, trial, pin)
    assert not result["observed_component_checks_pass"]
    assert result["bounded_observed_candidate_chains"] == 0
    assert not result["phase2_authorized_by_gate"]
