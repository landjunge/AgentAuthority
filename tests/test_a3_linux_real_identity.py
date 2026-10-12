"""Offline cryptographic regression on public real-run evidence, not new VM runs."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/a3-linux-runs/2026-10-12"


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "research/a3_linux" / file)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


SCORE = module("a3_score", "score.py")
CLIENT = module("a3_client", "client.py")


@pytest.fixture()
def actual_case():
    bundle = json.loads((DATA / "enrollment.json").read_text())
    case = json.loads((DATA / "case-1.json").read_text())
    return bundle, case["capture"], case["trial"], case["dispatch_packet"], bundle["ca_public_key"]


def test_actual_public_signatures_never_promote_real_identity(actual_case):
    result = SCORE.evaluate(*actual_case)
    assert result["enrollment_signature"]
    assert result["writes"][0]["authenticated_local_wrapper"] == "WrapperCodex"
    assert result["writes"][0]["fresh_host_dispatch"]
    assert result["real_agent_effect_chain"] == "UNBEKANNT"


@pytest.mark.parametrize("field,value", [("tgid", 1), ("start_ns", 1), ("inode", 1), ("result", 0)])
def test_changed_kernel_instance_or_file_cannot_bind(actual_case, field, value):
    actual_case[1][1]["record"][field] = value
    assert SCORE.evaluate(*actual_case)["writes"][0]["authenticated_local_wrapper"] is None


def test_wrong_fresh_dispatch_does_not_erase_independent_write(actual_case):
    actual_case[3]["active_nonces"] = ["wrong-new-session"]
    result = SCORE.evaluate(*actual_case)
    assert result["writes"][0]["write"] == "BELEGT"
    assert result["writes"][0]["wrapper_effect_chain"] == "BELEGT"
    assert not result["writes"][0]["fresh_host_dispatch"]
    assert result["real_agent_effect_chain"] == "UNBEKANNT"


def test_mutated_signed_client_claim_is_not_a_new_proof(actual_case):
    actual_case[3]["jobs"][0]["body"]["client"] = "Grok"
    result = SCORE.evaluate(*actual_case)
    assert not result["proof_checks"][0]["fresh_dispatch"]
    assert result["real_agent_effect_chain"] == "UNBEKANNT"


def test_changed_provider_label_cannot_authenticate_enrollment(actual_case):
    actual_case[0]["enrollment"]["body"]["codex_authenticated"] = True
    result = SCORE.evaluate(*actual_case)
    assert not result["enrollment_signature"]
    assert result["writes"][0]["authenticated_local_wrapper"] is None


def test_lifecycle_loss_unknown(actual_case):
    actual_case[2]["lifecycle"]["perf_lost"] = 1
    assert SCORE.evaluate(*actual_case)["writes"][0]["wrapper_effect_chain"] == "UNBEKANNT"


def test_exec_after_binding_invalidates_wrapper(actual_case):
    event = actual_case[1][1]["record"]
    actual_case[2]["lifecycle"]["records"].append(
        {
            "kind": 2,
            "pid": event["tgid"],
            "start": event["start_ns"],
            "stamp": event["entry_ns"] - 1,
            "generation": 2,
        }
    )
    assert SCORE.evaluate(*actual_case)["writes"][0]["authenticated_local_wrapper"] is None


def test_scoring_does_not_rewrite_raw_evidence(actual_case):
    previous = copy.deepcopy(actual_case)
    SCORE.evaluate(*actual_case)
    assert actual_case == previous


def test_client_output_is_only_exact_allowlisted_job():
    expected = {"operation": "write16", "nonce": "fresh"}
    assert CLIENT.extract_job({"text": json.dumps(expected)}, expected) == expected
    assert CLIENT.extract_job({"text": '{"operation":"shell","nonce":"fresh"}'}, expected) is None
    assert CLIENT.extract_job({"text": '{"operation":"write16","nonce":"old"}'}, expected) is None


def test_missing_evidence_stays_unknown():
    assert SCORE.evaluate({}, [], {}, {}, "bad")["real_agent_effect_chain"] == "UNBEKANNT"
