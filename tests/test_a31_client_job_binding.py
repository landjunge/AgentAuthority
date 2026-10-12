"""Independent offline checks of real public receipts; no provider functions simulated."""

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/a31-session-job-runs/2026-10-12"
sys.path.insert(0, str(ROOT / "research/a31_binding"))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / "research/a31_binding" / file)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


RECEIPT = load("a31_receipt", "receipt.py")
JOIN = load("a31_join", "join.py")


@pytest.fixture()
def real_cases():
    pin = json.loads((DATA / "pre-run-lock.json").read_text())["ca_public_key_pin"]
    return [json.loads((DATA / f"case-{i}.json").read_text()) for i in [1, 2, 3, 4]], pin


def evaluate(case, pin, context=None, job=None, now=None, used=None):
    return RECEIPT.check(
        case["local_receipt"],
        pin,
        context or case["context"],
        job or case["job"],
        now if now is not None else case["local_receipt"]["body"]["issued_ns"] + 1,
        used if used is not None else set(),
    )


@pytest.mark.parametrize("index", [0, 1])
def test_real_vendor_signed_process_receipt_qualified_only_locally(real_cases, index):
    cases, pin = real_cases
    result = evaluate(cases[index], pin)
    assert result["qualified"]
    assert result["provider_session_job_binding"] == result["model_identity"] == "UNBEKANNT"


def test_public_receipt_replay_is_not_fresh(real_cases):
    cases, pin = real_cases
    used = set()
    assert evaluate(cases[0], pin, used=used)["qualified"]
    result = evaluate(cases[0], pin, used=used)
    assert result["reasons"] == ["anti_replay"] and len(used) == 1


def test_foreign_real_session_context_is_not_transferred(real_cases):
    cases, pin = real_cases
    result = evaluate(cases[1], pin, context=cases[0]["context"])
    assert result["checks"]["host_signature"]
    assert not result["checks"]["channel"] and not result["qualified"]


def test_new_real_codex_session_rejects_old_binding(real_cases):
    cases, pin = real_cases
    result = evaluate(cases[0], pin, context=cases[2]["context"])
    assert result["checks"]["host_signature"] and not result["checks"]["instance"]


def test_delegate_attempt_cannot_inherit_parent_binding(real_cases):
    cases, pin = real_cases
    result = evaluate(cases[3], pin, context=cases[0]["context"])
    assert not result["qualified"] and not result["checks"]["channel"]
    # The real CLI attempt supplied no authenticated delegate proof.
    assert result["provider_session_job_binding"] == "UNBEKANNT"


def test_manipulated_job_digest_with_valid_signature_is_rejected(real_cases):
    cases, pin = real_cases
    result = evaluate(cases[0], pin, job=dict(cases[0]["job"], position="other"))
    assert result["checks"]["host_signature"] and not result["checks"]["job_digest"]


@pytest.mark.parametrize("boundary", ["early", "expired"])
def test_receipt_time_boundaries(real_cases, boundary):
    cases, pin = real_cases
    body = cases[0]["local_receipt"]["body"]
    now = body["issued_ns"] - 1 if boundary == "early" else body["expires_ns"]
    assert evaluate(cases[0], pin, now=now)["reasons"] == ["time"]


def test_same_pid_different_kernel_start_is_unknown(real_cases):
    cases, pin = real_cases
    context = copy.deepcopy(cases[0]["context"])
    context["process_instance"]["start_usec"] += 1
    result = evaluate(cases[0], pin, context=context)
    assert result["checks"]["host_signature"] and not result["checks"]["instance"]


def test_changed_receipt_cannot_claim_provider(real_cases):
    cases, pin = real_cases
    cases[0]["local_receipt"]["body"]["scope"] = "provider_attestation"
    result = evaluate(cases[0], pin)
    assert not result["qualified"] and not result["checks"]["host_signature"]


def test_wrong_pinned_CA_is_rejected(real_cases):
    cases, _ = real_cases
    assert not evaluate(cases[0], pin="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")["qualified"]


def test_raw_transcripts_are_not_rewritten(real_cases):
    cases, pin = real_cases
    previous = copy.deepcopy(cases)
    evaluate(cases[0], pin)
    assert cases == previous


@pytest.mark.parametrize("position", [1, 2])
def test_real_two_linux_joins_disregard_invalid_time_flag(real_cases, position):
    cases, pin = real_cases
    integration = json.loads((DATA / f"integration-{position}.json").read_text())
    enrollment = json.loads((DATA / "linux-enrollment.json").read_text())
    integration["all_writes_before_client_receipt_expiry"] = False
    result = JOIN.join(cases[position - 1], integration, enrollment, pin)
    assert result["local_client_pipeline_dispatch_effect"] == "BELEGT"
    assert result["invalid_time_field_disregarded"]
    assert result["full_real_agent_session_response_effect"] == "UNBEKANNT"


def test_altered_client_thread_metadata_does_not_match_signed_receipt(real_cases):
    cases, pin = real_cases
    cases[0]["client_metadata"].append({"thread_id": "forged"})
    integration = json.loads((DATA / "integration-1.json").read_text())
    enrollment = json.loads((DATA / "linux-enrollment.json").read_text())
    result = JOIN.join(cases[0], integration, enrollment, pin)
    assert not result["checks"]["local_metadata_digest"]
    assert result["local_client_pipeline_dispatch_effect"] == "UNBEKANNT"
