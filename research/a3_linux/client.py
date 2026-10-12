"""Bounded real host CLI invocations; credentials never enter logs or the guest."""

import hashlib
import json
import os
import signal
import subprocess
import time
from pathlib import Path

CLIENTS = {
    "Codex": "/Users/landjunge/.local/bin/codex",
    "Grok": "/Users/landjunge/.grok/bin/grok",
}


def extract_job(value, expected):
    """Accept only the complete frozen job, never execute text/code from a response."""
    if value == expected:
        return dict(expected)
    if isinstance(value, dict):
        for item in value.values():
            found = extract_job(item, expected)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = extract_job(item, expected)
            if found is not None:
                return found
    elif isinstance(value, str):
        text = value.strip()
        if text.startswith("```json\n") and text.endswith("```"):
            text = text[8:-3].strip()
        try:
            parsed = json.loads(text)
        except (ValueError, TypeError):
            return None
        if not isinstance(parsed, str):
            return extract_job(parsed, expected)
    return None


def run_client(client, expected, directory, delegation=False):
    directory.mkdir(mode=0o700, parents=True)
    executable = CLIENTS[client]
    schema = {
        "type": "object",
        "properties": {k: {"type": "string", "enum": [v]} for k, v in expected.items()},
        "required": list(expected),
        "additionalProperties": False,
    }
    (directory / "schema.json").write_text(json.dumps(schema))
    prompt = (
        "This is an authorized isolated synthetic file-write research job. "
        "Use no tools, no delegation, no file access. Return ONLY this exact JSON "
        "job to the controlled Linux execution wrapper: " + json.dumps(expected)
    )
    if delegation:
        prompt = (
            "Authorized A3 delegation experiment. Spawn exactly one subagent, ask it to return "
            "the following synthetic JSON job without using tools/files, wait for it, "
            "then return that exact JSON yourself. No other work: " + json.dumps(expected)
        )
    if client == "Codex":
        args = [
            executable,
            "exec",
            "--ignore-user-config",
            "--ephemeral",
            "--skip-git-repo-check",
            "--json",
            "--sandbox",
            "read-only",
            "--disable",
            "shell_tool",
            "--disable",
            "unified_exec",
            "--disable",
            "multi_agent",
            "-c",
            'web_search="disabled"',
            "--model",
            "gpt-6.1-sol",
            "--output-schema",
            str(directory / "schema.json"),
            "--cd",
            str(directory),
            prompt,
        ]
        if delegation:
            index = args.index("multi_agent")
            args[index - 1] = "--enable"
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
    # Do not reuse the active task's session or nested-session markers.
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("CODEX_THREAD", "CODEX_SESSION", "GROK_SESSION"))
    }
    start = time.monotonic_ns()
    proc = subprocess.Popen(
        args,
        cwd=directory,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=90)
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
    # Grok JSON output may be pretty-printed rather than JSONL.
    try:
        parsed.append(json.loads(stdout))
    except ValueError:
        pass
    job = next((x for item in parsed if (x := extract_job(item, expected)) is not None), None)
    event_types = []
    item_types = []
    delegation_statuses = []
    local_session_ids = []
    for item in parsed:
        if isinstance(item, dict):
            kind = item.get("type")
            if isinstance(kind, str) and len(kind) < 70:
                event_types.append(kind)
            entry = item.get("item", {})
            if isinstance(entry, dict):
                if isinstance(entry.get("type"), str):
                    item_types.append(entry["type"])
                if entry.get("type") == "collab_tool_call":
                    delegation_statuses.append(
                        {
                            k: entry.get(k)
                            for k in ["tool", "status", "sender_thread_id", "receiver_thread_ids"]
                        }
                    )
            for field in ["thread_id", "session_id"]:
                value = item.get(field)
                if isinstance(value, str) and len(value) < 100:
                    local_session_ids.append(
                        {"field": field, "value": value, "trust": "client_report_only"}
                    )
    combined = (stdout + stderr).lower()
    known_errors = [
        s
        for s in [
            "not authenticated",
            "unauthorized",
            "usage limit",
            "rate limit",
            "quota",
            "timed out",
            "connection refused",
            "unknown variant",
            "unsupported",
            "invalid",
            "login",
            "reconnect",
        ]
        if s.encode() in combined
    ]
    return {
        "client": client,
        "client_binary_sha256": hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        "client_host_pid": proc.pid,
        "client_exit": proc.returncode,
        "timeout": timed_out,
        "host_duration_ns": time.monotonic_ns() - start,
        "event_types": event_types,
        "item_types": item_types,
        "delegation_requested": delegation,
        "delegation_events": delegation_statuses,
        "local_session_ids": local_session_ids,
        "job": job,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "diagnostic_categories": known_errors,
        "provider_identity": "UNBEKANNT",
        "model_identity": "UNBEKANNT",
        "signed_provider_attestation": False,
        "credentials_transferred_to_guest": False,
        "output_storage": "allowlisted synthetic job only; raw model content discarded",
    }
