"""Real Codex upstream-attestation capability probe; no invented token response."""

import json
import os
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a3_linux"))
from client import extract_job
from client_run import digest_bytes, metadata


def run(directory, expected):
    directory.mkdir(mode=0o700, parents=True)
    proc = subprocess.Popen(
        [
            "/Users/landjunge/.local/bin/codex",
            "--disable",
            "shell_tool",
            "--disable",
            "unified_exec",
            "--disable",
            "multi_agent",
            "-c",
            "mcp_servers={}",
            "-c",
            "features.apps=false",
            "-c",
            'web_search="disabled"',
            "app-server",
        ],
        cwd=directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    assert proc.stdin and proc.stdout
    buffer = b""
    records = []
    counter = 0
    deadline = time.monotonic() + 90
    attestation_requests = []
    answer = None
    failure = None
    thread_id = None

    def send(value):
        proc.stdin.write(json.dumps(value).encode() + b"\n")
        proc.stdin.flush()

    def receive():
        nonlocal buffer, answer
        while b"\n" not in buffer:
            if time.monotonic() > deadline:
                raise TimeoutError("bounded provider capability trial")
            if not select.select([proc.stdout], [], [], 1)[0]:
                continue
            chunk = os.read(proc.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("app-server EOF")
            buffer += chunk
        line, buffer = buffer.split(b"\n", 1)
        value = json.loads(line)
        fields = []
        metadata(value, fields)
        records.append(
            {
                "method": value.get("method"),
                "id": value.get("id"),
                "bytes": len(line),
                "sha256": digest_bytes(line),
                "metadata": fields,
                "error_code": value.get("error", {}).get("code"),
            }
        )
        if value.get("method") == "attestation/generate":
            params = value.get("params", {})
            attestation_requests.append(
                {
                    "parameter_fields": sorted(params),
                    "token_supplied": False,
                    "direction": "server asks host for upstream token",
                }
            )
            send(
                {
                    "id": value["id"],
                    "error": {
                        "code": -32601,
                        "message": "A3.1 host has no authorized upstream attestation generator",
                    },
                }
            )
        found = extract_job(value.get("params", {}).get("item", {}), expected)
        if found:
            answer = found
        return value

    def rpc(method, params):
        nonlocal counter
        counter += 1
        identifier = counter
        send({"id": identifier, "method": method, "params": params})
        while True:
            value = receive()
            if value.get("id") == identifier and not value.get("method"):
                if "error" in value:
                    raise RuntimeError("RPC rejected " + str(value["error"].get("code")))
                return value["result"]

    try:
        rpc(
            "initialize",
            {
                "clientInfo": {"name": "a31_research", "version": "1.0"},
                "capabilities": {"requestAttestation": True},
            },
        )
        send({"method": "initialized"})
        account = rpc("account/read", {"refreshToken": False})
        account_kind = (account.get("account") or {}).get("type")
        thread = rpc(
            "thread/start",
            {
                "cwd": str(directory),
                "model": "gpt-6.1-sol",
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "ephemeral": True,
            },
        )
        thread_id = thread["thread"]["id"]
        rpc(
            "turn/start",
            {
                "threadId": thread_id,
                "input": [
                    {
                        "type": "text",
                        "text": "No tools or files. Return only this exact synthetic job JSON: "
                        + json.dumps(expected),
                    }
                ],
            },
        )
        while True:
            value = receive()
            if value.get("method") == "turn/completed":
                failure = (
                    None
                    if value["params"]["turn"]["status"] == "completed"
                    else value["params"]["turn"]["status"]
                )
                break
    except (ValueError, OSError, KeyError, RuntimeError, TimeoutError) as error:
        failure = type(error).__name__
        account_kind = None
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
    return {
        "client_pid": proc.pid,
        "requestAttestation_capability_requested": True,
        "attestation_requests": attestation_requests,
        "account_kind_claim": account_kind,
        "thread_id_claim": thread_id,
        "job": answer,
        "failure": failure,
        "records": records,
        "provider_signed_job_available": False,
        "classification": "UNBEKANNT",
        "fake_provider_token_generated": False,
    }


if __name__ == "__main__":
    import argparse
    import secrets

    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    data = run(
        args.directory,
        {
            "operation": "write16",
            "nonce": secrets.token_hex(24),
            "position": "provider-capability",
            "claimed_client": "Codex",
        },
    )
    print(json.dumps(data, indent=2))
