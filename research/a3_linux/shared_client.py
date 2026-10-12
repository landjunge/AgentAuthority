"""Two real Codex app-server threads in one host process; IDs are client claims."""

import hashlib
import json
import os
import select
import signal
import subprocess
import time

from client import CLIENTS, extract_job


def run_shared(expected, directory, concurrent):
    directory.mkdir(mode=0o700, parents=True)
    proc = subprocess.Popen(
        [
            CLIENTS["Codex"],
            "--disable",
            "shell_tool",
            "--disable",
            "unified_exec",
            "--disable",
            "multi_agent",
            "-c",
            'web_search="disabled"',
            "-c",
            "mcp_servers={}",
            "-c",
            "features.apps=false",
            "app-server",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        cwd=directory,
        start_new_session=True,
    )
    assert proc.stdin and proc.stdout
    records = []
    buffer = b""
    counter = 0
    deadline = time.monotonic() + 100
    jobs = [None, None]
    threads = []
    failure = None

    def send(method, params):
        nonlocal counter
        counter += 1
        proc.stdin.write(
            json.dumps({"id": counter, "method": method, "params": params}).encode() + b"\n"
        )
        proc.stdin.flush()
        return counter

    def receive():
        nonlocal buffer
        while b"\n" not in buffer:
            if time.monotonic() > deadline or not select.select([proc.stdout], [], [], 1)[0]:
                if time.monotonic() > deadline:
                    raise TimeoutError("bounded app-server")
                continue
            chunk = os.read(proc.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("app-server EOF")
            buffer += chunk
        line, buffer = buffer.split(b"\n", 1)
        item = json.loads(line)
        params = item.get("params", {})
        for index, tid in enumerate(threads):
            if params.get("threadId") == tid:
                found = extract_job(params.get("item", {}), expected[index])
                if found is not None:
                    jobs[index] = found
        records.append(
            {
                "bytes": len(line),
                "sha256": hashlib.sha256(line).hexdigest(),
                "method": item.get("method"),
                "id": item.get("id"),
                "error_code": item.get("error", {}).get("code"),
            }
        )
        return item

    def rpc(method, params):
        identifier = send(method, params)
        while True:
            item = receive()
            if item.get("id") == identifier:
                if "error" in item:
                    raise RuntimeError(
                        "app-server request rejected: " + str(item["error"].get("code"))
                    )
                return item["result"]

    def start(index):
        result = rpc(
            "thread/start",
            {
                "cwd": str(directory),
                "model": "gpt-6.1-sol",
                "approvalPolicy": "never",
                "sandbox": "read-only",
                "ephemeral": True,
                "config": {
                    "features.shell_tool": False,
                    "features.unified_exec": False,
                    "mcp_servers": {},
                },
            },
        )
        tid = result["thread"]["id"]
        threads.append(tid)
        return rpc(
            "turn/start",
            {
                "threadId": tid,
                "input": [
                    {
                        "type": "text",
                        "text": "No tools or file access. Return ONLY this synthetic execution-wrapper JSON: "
                        + json.dumps(expected[index]),
                    }
                ],
            },
        )

    def wait_turn(index):
        while True:
            item = receive()
            params = item.get("params", {})
            tid = params.get("threadId")
            for k, target in enumerate(expected):
                found = extract_job(params.get("item", {}), target)
                if found is not None and tid == threads[k]:
                    jobs[k] = found
            if item.get("method") == "turn/completed" and tid == threads[index]:
                return params.get("turn", {}).get("status")

    try:
        rpc("initialize", {"clientInfo": {"name": "a3_research", "version": "1.0"}})
        proc.stdin.write(b'{"method":"initialized"}\n')
        proc.stdin.flush()
        start(0)
        if concurrent:
            start(1)
            completed = set()
            while len(completed) != 2:
                item = receive()
                params = item.get("params", {})
                tid = params.get("threadId")
                for k in range(2):
                    if tid == threads[k]:
                        found = extract_job(params.get("item", {}), expected[k])
                        if found is not None:
                            jobs[k] = found
                        if item.get("method") == "turn/completed":
                            completed.add(k)
        else:
            wait_turn(0)
            start(1)
            wait_turn(1)
    except (ValueError, KeyError, OSError, RuntimeError, TimeoutError) as error:
        failure = type(error).__name__
    finally:
        proc.stdin.close()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=5)
    return {
        "client": "Codex",
        "client_host_pid": proc.pid,
        "threads": threads,
        "jobs": jobs,
        "concurrent": concurrent,
        "failure": failure,
        "records": records,
        "provider_identity": "UNBEKANNT",
        "model_identity": "UNBEKANNT",
        "thread_id_trust": "client_generated_not_provider_attestation",
        "signed_provider_attestation": False,
        "credentials_transferred_to_guest": False,
    }
