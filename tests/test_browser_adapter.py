"""Private-service display contract tests, entirely synthetic and with no fetch."""

from __future__ import annotations

import copy
import json

import pytest

from agent_authority.browser_adapter import (
    PrivateReportError,
    adapt_private_report,
    synthetic_private_response,
)

JOB = "0123456789abcdef" * 2


def synthetic_response(*, measured=True):
    return synthetic_private_response(JOB, measured=measured)


def test_actual_get_shape_projects_without_trusting_reported_checks_or_mutating_input():
    source = synthetic_response()
    before = copy.deepcopy(source)
    source["report"]["body"]["classification"] = "BELEGT"
    before["report"]["body"]["classification"] = "BELEGT"
    result = adapt_private_report(source, "synthetic-private-a", JOB)
    assert source == before
    graph = result["graph"]
    assert graph["schema"] == "agent-authority-ui-graph-v1"
    assert graph["isDemo"] is False  # caller labels fixture; adapter never infers provenance
    assert len(graph["nodes"]) == 6 and len(graph["edges"]) == 5
    assert {node["status"] for node in graph["nodes"]} == {"unknown"}
    assert {edge["status"] for edge in graph["edges"]} == {"unknown"}
    ids = {node["id"] for node in graph["nodes"]}
    assert all(edge["from"] in ids and edge["to"] in ids for edge in graph["edges"])
    assert result["metadata"]["production_integration"] == "blocked"
    assert result["metadata"]["signature_verification"] == "UNBEKANNT"
    assert result["privateReport"]["report"]["body"]["classification"] == "BELEGT"
    assert result["privateReport"]["signature_omitted"] is True
    assert "schema_version" not in result
    assert "agent-authority-observation-report-v1" not in json.dumps(result)
    request = next(node for node in graph["nodes"] if node["id"] == "private-request_signature")
    assert request["evidence"] == ["job_sha256:" + "2" * 64]
    acceptance = next(
        node for node in graph["nodes"] if node["id"] == "private-exact_service_acceptance"
    )
    assert acceptance["evidence"] == ["acceptance_sha256:" + "3" * 64]


def test_signed_historical_body_and_current_unsigned_status_remain_separate():
    source = synthetic_response()
    result = adapt_private_report(source, "synthetic-private-a", JOB)
    source["current_key_status"]["synthetic-sender"] = "revoked"
    changed = adapt_private_report(source, "synthetic-private-a", JOB)
    assert result["graph"] == changed["graph"]
    assert result["metadata"]["envelope_sha256"] == changed["metadata"]["envelope_sha256"]
    report = changed["privateReport"]
    assert "current_key_status_reported" not in report["report"]["body"]
    assert report["current_key_status_covered_by_report_signature"] is False
    assert report["current_key_status_reported"]["synthetic-sender"] == "revoked"


def test_interrupted_real_contract_variant_does_not_invent_missing_sources():
    result = adapt_private_report(synthetic_response(measured=False), "synthetic-private-a", JOB)
    assert len(result["graph"]["nodes"]) == 2
    body = result["privateReport"]["report"]["body"]
    assert body["sources"] == [] and body["reason"] == "WORKER_INTERRUPTED"
    assert "layers" not in body and "checks" not in body


@pytest.mark.parametrize(
    "change",
    [
        lambda value: value.update(schema="agent-authority-observation-report-v1"),
        lambda value: value["report"]["body"].update(job_id="f" * 32),
        lambda value: value["report"]["body"].update(grants_rights=True),
        lambda value: value["report"]["body"].update(provider_model_session="BELEGT"),
        lambda value: value["report"]["body"].update(classification=[]),
        lambda value: value["report"]["body"].update(issued_ms=True),
        lambda value: value["report"]["body"].update(extra="never copied"),
        lambda value: value["report"].update(signature="bad"),
        lambda value: value["current_key_status"].update(forged="verified"),
        lambda value: value["report"]["body"]["layers"].update(independent_write=[]),
        lambda value: value["report"]["body"]["checks"].update(invalid="true"),
        lambda value: value["report"]["body"]["critical_loss_metrics"].update(invalid=True),
        lambda value: value["report"]["body"]["source"].update(trust_class="customer-asserted"),
    ],
)
def test_contract_confusion_and_malformed_fields_fail_closed(change):
    source = synthetic_response()
    change(source)
    with pytest.raises(PrivateReportError, match="private_report_"):
        adapt_private_report(source, "synthetic-private-a", JOB)


@pytest.mark.parametrize(
    "source_id,job_id",
    [
        ("../private", JOB),
        ("https://untrusted.invalid", JOB),
        ("a", "x; shell"),
        ("a", "f" * 31),
    ],
)
def test_adapter_accepts_only_configured_identifiers_never_paths_urls_or_commands(
    source_id, job_id
):
    with pytest.raises(PrivateReportError):
        adapt_private_report(synthetic_response(), source_id, job_id)


def test_foreign_text_is_inert_data_and_not_an_html_renderer():
    foreign = '<img src=x onerror="alert(1)">'
    source = synthetic_response()
    source["report"]["body"]["uncertainties"] = [foreign]
    result = adapt_private_report(source, "synthetic-private-a", JOB)
    assert result["graph"]["nodes"][1]["facts"][-1]["value"] == foreign
    assert all(node["status"] == "unknown" for node in result["graph"]["nodes"])
    assert "html" not in result and "script" not in result


def test_input_budgets_reject_large_deep_and_nonfinite_data():
    source = synthetic_response()
    source["report"]["body"]["uncertainties"] = ["x" * 2049]
    with pytest.raises(PrivateReportError, match="structure_limit"):
        adapt_private_report(source, "synthetic-private-a", JOB)
    source = synthetic_response()
    source["report"]["body"]["uncertainties"] = [[[[[[[[[[[[["deep"]]]]]]]]]]]]]
    with pytest.raises(PrivateReportError, match="structure_limit"):
        adapt_private_report(source, "synthetic-private-a", JOB)
    source = synthetic_response()
    source["report"]["body"]["issued_ms"] = float("nan")
    with pytest.raises(PrivateReportError):
        adapt_private_report(source, "synthetic-private-a", JOB)


def test_no_crypto_collector_network_or_private_service_import_is_required():
    import subprocess
    import sys

    code = """
import sys
before = set(sys.modules)
from agent_authority.browser_adapter import adapt_private_report
assert not any(name.startswith(('research.', 'urllib', 'http', 'ctypes')) for name in set(sys.modules) - before)
"""
    result = subprocess.run([sys.executable, "-B", "-c", code], capture_output=True, timeout=10)
    assert result.returncode == 0, result.stderr
