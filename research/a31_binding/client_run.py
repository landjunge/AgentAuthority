"""Fresh real CLI response channel, independently sampled signed running image."""

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a3_linux"))
from client import CLIENTS, extract_job

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import sign
from receipt import PINS, digest


def metadata(value, output):
    """Keep types/IDs/attestation-field presence, never arbitrary model/credential text."""
    if isinstance(value, dict):
        row = {}
        for key in [
            "type",
            "tool",
            "status",
            "thread_id",
            "threadId",
            "turnId",
            "session_id",
            "sessionId",
            "sender_thread_id",
            "senderThreadId",
            "receiver_thread_ids",
            "receiverThreadIds",
            "id",
        ]:
            item = value.get(key)
            if isinstance(item, (str, int, list)) and len(str(item)) < 500:
                row[key] = item
        row["attestation_fields"] = [
            k
            for k in value
            if any(s in k.lower() for s in ["attest", "signature", "proof", "digest"])
        ]
        if len(row) > 1 or row["attestation_fields"]:
            output.append(row)
        for item in value.values():
            if isinstance(item, (dict, list)):
                metadata(item, output)
    elif isinstance(value, list):
        for item in value:
            metadata(item, output)


def launch(client, job, context, directory, probe_binary, ca_file, delegation=False):
    directory.mkdir(mode=0o700, parents=True)
    schema = {
        "type": "object",
        "properties": {k: {"type": "string", "enum": [v]} for k, v in job.items()},
        "required": list(job),
        "additionalProperties": False,
    }
    schema_path = directory / "schema.json"
    schema_path.write_text(json.dumps(schema))
    prompt = "Use no tools or files. Return ONLY this exact artificial job JSON: " + json.dumps(job)
    if delegation:
        prompt = (
            "Authorized synthetic A3.1 delegation test: spawn exactly one subagent, ask it "
            "to return the exact JSON below without tools/files, wait, and return its JSON. "
            "Do nothing else: " + json.dumps(job)
        )
    executable = CLIENTS[client]
    if client == "Codex":
        args = [
            executable,
            "exec",
            "--ignore-user-config",
            "--ephemeral",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--disable",
            "shell_tool",
            "--disable",
            "unified_exec",
            "--enable" if delegation else "--disable",
            "multi_agent",
            "-c",
            'web_search="disabled"',
            "--model",
            "gpt-6.1-sol",
            "--output-schema",
            str(schema_path),
            "--cd",
            str(directory),
            prompt,
        ]
    else:
        args = [
            executable,
            "--cwd",
            str(directory),
            "--leader-socket",
            str(directory / "leader.sock"),
            "--tools",
            "",
            "--no-subagents",
            "--disable-web-search",
            "--permission-mode",
            "plan",
            "--max-turns",
            "1",
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(schema),
            "-p",
            prompt,
        ]
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("CODEX_THREAD", "CODEX_SESSION", "GROK_SESSION"))
    }
    proc = subprocess.Popen(
        args,
        cwd=directory,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    context["spawn_pid"] = proc.pid
    context["host_controller_pid"] = os.getpid()
    context["uid"] = os.getuid()
    pin = PINS[client]
    requirement = f'anchor apple generic and certificate leaf[subject.OU] = "{pin["team"]}" and identifier "{pin["identifier"]}"'
    checked = subprocess.run(
        [str(probe_binary), str(proc.pid), requirement],
        check=False,
        capture_output=True,
        timeout=30,
    )
    probe = json.loads(checked.stdout) if checked.returncode == 0 else {}
    context["process_instance"] = {
        k: probe.get(k) for k in ["pid", "start_sec", "start_usec", "boot_sec", "path"]
    }
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=100)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            stdout, stderr = proc.communicate(timeout=5)
    parsed = []
    for line in stdout.splitlines():
        try:
            parsed.append(json.loads(line))
        except ValueError:
            pass
    try:
        parsed.append(json.loads(stdout))
    except ValueError:
        pass
    answer = next((x for item in parsed if (x := extract_job(item, job)) is not None), None)
    fields = []
    for item in parsed:
        metadata(item, fields)
    issued = time.monotonic_ns()
    body = {
        "domain": "A31-LOCAL-CLIENT-JOB-v1",
        "scope": "local_host_attestation_not_provider",
        "client": client,
        "channel_id": context["channel_id"],
        "challenge": context["challenge"],
        "receipt_id": context["receipt_id"],
        "issued_ns": issued,
        "expires_ns": issued + 180_000_000_000,
        "process_probe": probe,
        "job_sha256": digest(answer) if answer else None,
        "client_binary_sha256": digest_file(executable),
        "client_exit": proc.returncode,
        "qualified_response": answer is not None and not timed_out,
        "stdout_sha256": digest_bytes(stdout),
        "metadata_sha256": digest(fields),
        "provider_attestation": False,
        "coding_thread_trust": "client_claim_only",
        "stdout_writer_limit": "exclusive owned pipe may be inherited by client descendants",
    }
    return {
        "context": context,
        "job": answer,
        "local_receipt": sign(ca_file, body),
        "client_metadata": fields,
        "process_probe_exit": checked.returncode,
        "client_exit": proc.returncode,
        "timeout": timed_out,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": digest_bytes(stdout),
        "stderr_sha256": digest_bytes(stderr),
        "provider_attestation_status": "UNBEKANNT",
        "delegation_requested": delegation,
    }


def digest_bytes(data):
    import hashlib

    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    return digest_bytes(Path(path).read_bytes())
