"""Public receipt-to-dispatch-to-kernel join; disregards the preserved invalid time field."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a3_linux"))
from score import evaluate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import verify
from receipt import check, digest


def join(source, integration, enrollment, pinned_ca):
    local = check(
        source["local_receipt"],
        pinned_ca,
        source["context"],
        source["job"],
        integration["entry_gate_ns"],
        set(),
        consume=False,
    )
    packet = integration["dispatch_packet"]
    dispatch = packet["jobs"][0]
    body = dispatch["body"]
    checks = {
        "local_receipt": local["qualified"],
        "local_metadata_digest": source["local_receipt"]["body"]["metadata_sha256"]
        == digest(source["client_metadata"]),
        "dispatch_signature": verify(pinned_ca, dispatch),
        "signed_receipt_link": body["local_client_receipt_sha256"]
        == digest(source["local_receipt"])
        == integration["client_receipt_sha256"],
        "concrete_job": body["job"] == source["job"],
        "client_pipeline": body["client"] == source["context"]["client"],
        "fresh_entry_gate": integration["entry_gate"]["qualified"],
        "bounded_host_collection": integration["host_collection_end_before_receipt_expiry"] is True,
        "clean_exits": integration["observer_exit"] == integration["adapter_exit"] == 0,
    }
    measured = evaluate(enrollment, integration["capture"], integration["trial"], packet, pinned_ca)
    checks["independent_writer_binding"] = bool(measured["writes"]) and all(
        row["write"] == row["wrapper_effect_chain"] == "BELEGT"
        and row["fresh_host_dispatch"]
        and row["authenticated_local_wrapper"] == "Wrapper" + body["client"]
        for row in measured["writes"]
    )
    return {
        "checks": checks,
        "local_client_pipeline_dispatch_effect": "BELEGT" if all(checks.values()) else "UNBEKANNT",
        "full_real_agent_session_response_effect": "UNBEKANNT",
        "independent_reply_bytes_root_process_writer": "UNBEKANNT; inherited stdout possible",
        "continuous_host_exec_generation": "UNBEKANNT; runtime image sampled once",
        "invalid_time_field_disregarded": True,
        "host_collection_end_timestamp_ns": None,
        "provider_model_identity": "UNBEKANNT",
        "kernel": measured,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    root = args.directory
    enrollment = json.loads((root / "linux-enrollment.json").read_text())
    pin = json.loads((root / "pre-run-lock.json").read_text())["ca_public_key_pin"]
    rows = []
    for i in [1, 2]:
        rows.append(
            {
                "position": i,
                "verification": join(
                    json.loads((root / f"case-{i}.json").read_text()),
                    json.loads((root / f"integration-{i}.json").read_text()),
                    enrollment,
                    pin,
                ),
            }
        )
    print(json.dumps({"integrations": rows}, indent=2))
