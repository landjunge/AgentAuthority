"""Read/verify a report without displaying bearer tokens or private keys."""

import argparse
import json
from pathlib import Path

from research.private_service.http import call
from research.private_service.protocol import require, verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["status", "report"])
    parser.add_argument("job_id")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    from research.private_service.protocol import identifier

    identifier(args.job_id)
    token = next(t["token"] for t in config["tokens"] if t["role"] == "client")
    path = f"/v1/jobs/{args.job_id}" + ("/report" if args.operation == "report" else "")
    status, value = call(args.url, token, "GET", path)
    require(status == 200, status, value.get("code", "READ_FAILED"))
    if args.operation == "report":
        require(
            verify(config["report_public_key"], value["report"]), 401, "REPORT_SIGNATURE_INVALID"
        )
        value["report_signature_verified"] = True
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
