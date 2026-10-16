"""Read/verify reports; confirm only a complete, verified receiver-owned file."""

import argparse
import json
import secrets
from pathlib import Path

from research.private_service.http import call
from research.private_service.protocol import digest, identifier, request, require, verify
from research.private_service.retention import fsync_dir, write_private


def confirm(config, jid, value, deliver):
    """Explicit caller assertion of full receipt, never a side effect of GET."""
    packet = value.get("report")
    require(verify(config["report_public_key"], packet), 401, "REPORT_SIGNATURE_INVALID")
    body = packet["body"]
    tenant = next(t["tenant"] for t in config["tokens"] if t["role"] == "client")
    require(body["tenant"] == tenant and body["job_id"] == jid, 422, "RECEIPT_MISMATCH")
    path = f"/v1/jobs/{jid}/receipts"
    signed = request(
        config["client_private_key"],
        tenant,
        config["client_signing_kid"],
        path,
        {
            "job_id": jid,
            "report_version": body["report_version"],
            "report_sha256": digest(packet),
            "received_complete": True,
        },
        secrets.token_hex(16),
        secrets.token_hex(32),
    )
    # A lost response can be retried with these exact bytes. No disk request cache.
    return deliver(path, signed)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["status", "report", "receive", "confirm"])
    parser.add_argument("job_id")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--output", type=Path, help="receive: new private receiver-owned file")
    parser.add_argument(
        "--report-file", type=Path, help="confirm: complete previously received file"
    )
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    identifier(args.job_id)
    token = next(t["token"] for t in config["tokens"] if t["role"] == "client")
    if args.operation == "confirm":
        require(args.report_file is not None, 422, "REPORT_FILE_REQUIRED")
        value = json.loads(args.report_file.read_bytes())
        status, value = confirm(
            config, args.job_id, value, lambda p, b: call(args.url, token, "POST", p, b)
        )
        require(status == 200, status, value.get("code", "CONFIRM_FAILED"))
    else:
        path = f"/v1/jobs/{args.job_id}" + ("" if args.operation == "status" else "/report")
        status, value = call(args.url, token, "GET", path)
        require(status == 200, status, value.get("code", "READ_FAILED"))
        if args.operation != "status":
            require(
                verify(config["report_public_key"], value["report"]),
                401,
                "REPORT_SIGNATURE_INVALID",
            )
            value["report_signature_verified"] = True
        if args.operation == "receive":
            require(args.output is not None, 422, "OUTPUT_REQUIRED")
            # Local receiver destination only, never transmitted to the service.
            write_private(args.output, (json.dumps(value, indent=2) + "\n").encode())
            fsync_dir(args.output.absolute().parent)
            value = {
                "received_complete": True,
                "server_receipt_state": "unconfirmed",
                "expires_at": value["expires_at"],
                "next": "Explicitly confirm using --report-file; receiver copy has its own lifecycle",
            }
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
