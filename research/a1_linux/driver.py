"""Host controller: separate SSH channels, Oracle retained on host only, no retries."""

import argparse
import datetime
import hashlib
import json
import os
import select
import secrets
import subprocess
import time
from pathlib import Path

from score import evaluate

VM_HOME = "/Users/landjunge/.local/share/agent-authority-a1-linux-vm"
BASE = ["limactl", "shell", "--workdir=/tmp", "a1-research"]
MODES = ["write", "idle", "sibling", "child", "forged", "pair"]


def run(directory):
    if directory.exists():
        raise ValueError("fresh output only")
    directory.mkdir(mode=0o700)
    env = dict(os.environ, LIMA_HOME=VM_HOME)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain"]):
        raise ValueError("committed clean source required")
    result = {
        "source_commit": head,
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cases": [],
        "logical_agent_identity": "UNBEKANNT",
        "retries": 0,
    }
    for position, mode in enumerate(MODES, 1):
        path = "/var/tmp/a1-research-" + directory.name + "/" + secrets.token_hex(8)
        setup = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(exist_ok=True);p.touch();pathlib.Path(str(p)+'.other').touch()"
        subprocess.run(BASE + ["python3", "-c", setup, path], env=env, check=True, timeout=15)
        observer = subprocess.Popen(
            BASE + ["sudo", "-n", "/usr/bin/python3", "-B", "/opt/a1/observer.py", path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert observer.stdout is not None
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("collector ready")
        first = observer.stdout.readline()
        if not first:
            _, error = observer.communicate(timeout=10)
            (directory / f"L{position}-observer-failure.txt").write_bytes(error)
            raise RuntimeError("observer failed before ready")
        ready = json.loads(first)
        if ready.get("ready") is not True:
            raise RuntimeError("collector handshake")
        capture_start = time.monotonic_ns()
        truth = subprocess.run(
            BASE + ["/usr/bin/python3", "-B", "/opt/a1/oracle.py", path, mode],
            env=env,
            capture_output=True,
            timeout=10,
        )
        rest, error = observer.communicate(timeout=15)
        capture = [json.loads(line) for line in (first + rest).decode().splitlines()]
        oracle = json.loads(truth.stdout) if truth.returncode == 0 else None
        record = {
            "position": position,
            "target_path": path,
            "mode": mode,
            "observer_exit": observer.returncode,
            "oracle_exit": truth.returncode,
            "observer_stderr_bytes": len(error),
            "observer_stderr_sha256": hashlib.sha256(error).hexdigest(),
            "oracle_stderr_bytes": len(truth.stderr),
            "host_collection_ns": time.monotonic_ns() - capture_start,
            "capture": capture,
            "oracle": oracle,
            "capture_sha256": hashlib.sha256(first + rest).hexdigest(),
            "oracle_sha256": hashlib.sha256(truth.stdout).hexdigest(),
        }
        if observer.returncode == truth.returncode == 0:
            record["evaluation"] = evaluate(capture, oracle)
        else:
            record["evaluation"] = {"evidence": "UNBEKANNT", "reason": "execution failure"}
        (directory / f"L{position}.json").write_text(json.dumps(record, indent=2) + "\n")
        result["cases"].append({"position": position, "mode": mode, **record["evaluation"]})
        print(position, mode, record["evaluation"], flush=True)
    result["ended_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (directory / "cohort.json").write_text(json.dumps(result, indent=2) + "\n")


def run_reuse(directory):
    env = dict(os.environ, LIMA_HOME=VM_HOME)
    path = "/var/tmp/a1-research-" + directory.name + "/" + secrets.token_hex(8)
    setup = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(exist_ok=True);p.touch()"
    subprocess.run(BASE + ["python3", "-c", setup, path], env=env, check=True, timeout=15)
    observer = subprocess.Popen(
        BASE + ["sudo", "-n", "/usr/bin/python3", "-B", "/opt/a1/observer.py", path],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert observer.stdout is not None
    if not select.select([observer.stdout], [], [], 45)[0]:
        raise TimeoutError("reuse collector ready")
    first = observer.stdout.readline()
    assert json.loads(first).get("ready") is True
    truth = subprocess.run(
        BASE + ["sudo", "-n", "/usr/bin/python3", "-B", "/opt/a1/reuse_oracle.py", path],
        env=env,
        capture_output=True,
        timeout=10,
    )
    rest, error = observer.communicate(timeout=15)
    oracle = json.loads(truth.stdout) if truth.returncode == 0 else None
    capture = [json.loads(line) for line in (first + rest).decode().splitlines()]
    result = {
        "separate_control": "PID_REUSE",
        "target_path": path,
        "observer_exit": observer.returncode,
        "oracle_exit": truth.returncode,
        "oracle": oracle,
        "capture": capture,
        "observer_stderr_bytes": len(error),
        "capture_sha256": hashlib.sha256(first + rest).hexdigest(),
        "oracle_sha256": hashlib.sha256(truth.stdout).hexdigest(),
    }
    if observer.returncode == truth.returncode == 0:
        result["evaluation"] = evaluate(capture, oracle)
    else:
        result["evaluation"] = {"evidence": "UNBEKANNT", "reason": "control execution failed"}
    (directory / "pid-reuse-control.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PID_REUSE", result["evaluation"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--reuse-control", action="store_true")
    args = parser.parse_args()
    run(args.directory)
    if args.reuse_control:
        run_reuse(args.directory)
