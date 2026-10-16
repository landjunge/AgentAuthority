"""Offline operator projection: API receives public pins and scoped token hashes."""

import argparse
import hashlib
import json
from pathlib import Path

from research.private_service.protocol import HEX, identifier, require
from research.private_service.retention import write_private

API_FIELDS = ["root_pins", "report_public_key", "trust_version", "runner_tenant", "runner_kid"]


def api_configuration(config):
    require(type(config["tokens"]) is list and 0 < len(config["tokens"]) <= 64, 503, "CONFIG_LIMIT")
    require(
        type(config["root_pins"]) is dict and 0 < len(config["root_pins"]) <= 32,
        503,
        "CONFIG_LIMIT",
    )
    result = {key: config[key] for key in API_FIELDS}
    result["tokens"] = [
        {
            "tenant": item["tenant"],
            "role": item["role"],
            "subjects": item.get("subjects", []),
            "sha256": item.get("sha256") or hashlib.sha256(item["token"].encode()).hexdigest(),
        }
        for item in config["tokens"]
    ]
    for item in result["tokens"]:
        identifier(item["tenant"])
        require(item["tenant"] in result["root_pins"], 503, "CONFIG_TENANT")
        require(item["role"] in ("reader", "client", "runner", "admin"), 503, "CONFIG_ROLE")
        require(type(item["sha256"]) is str and HEX.fullmatch(item["sha256"]), 503, "CONFIG_TOKEN")
        require(type(item["subjects"]) is list and len(item["subjects"]) <= 64, 503, "CONFIG_LIMIT")
        for subject in item["subjects"]:
            if subject != "*":
                identifier(subject)
    require(
        len({item["sha256"] for item in result["tokens"]}) == len(result["tokens"]),
        503,
        "CONFIG_TOKEN",
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--operator-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_private(
        args.output,
        (
            json.dumps(api_configuration(json.loads(args.operator_config.read_bytes()))) + "\n"
        ).encode(),
    )
