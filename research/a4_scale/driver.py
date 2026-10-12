"""Gate first, pinned100-principal execution, public raw evidence and cleanup."""

import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import select
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "a2_linux"))
from host_crypto import create_ca, sign
from protocol import canonical

BASE = ["limactl", "shell", "--workdir=/tmp", "a1-research"]
ENV = dict(os.environ, LIMA_HOME="/Users/landjunge/.local/share/agent-authority-a1-linux-vm")
COPY = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sys.stdin.buffer.read())"


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def guest(args, data=None, timeout=40):
    return subprocess.run(
        BASE + args, env=ENV, input=data, capture_output=True, check=True, timeout=timeout
    )


def load(file, name):
    spec = importlib.util.spec_from_file_location(name, file)
    if spec is None or spec.loader is None:
        raise RuntimeError("missing verifier source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gate(out):
    prior = out.parent / "phase1"
    pins = json.loads((prior / "pins.json").read_text())
    result = load(ROOT / "a4_completion/verify.py", "a4_gate").evaluate(
        json.loads((prior / "registry.json").read_text()),
        [json.loads(row) for row in (prior / "capture.jsonl").read_text().splitlines()],
        json.loads((prior / "trial.stdout.json").read_text()),
        pins["pinned_ca_public_key"],
    )
    if not result["phase2_authorized_by_gate"]:
        raise ValueError("phase1 gate not independently proven")
    return result


def prepare(out):
    result = gate(out)
    out.mkdir(parents=True, exist_ok=False)
    dump(out / "entry-gate.json", result)
    run_id = secrets.token_hex(16)
    scope, vault = "/opt/a4scale-" + run_id, "/var/tmp/a4-scale-private-" + run_id
    sources = [
        (ROOT / "a4_scale" / name, name) for name in ["worker.py", "registrar.py", "kernel.py"]
    ]
    sources += [
        (ROOT / "a4_completion" / name, name)
        for name in ["observer.py", "lifecycle.py", "probes.py", "guest.py"]
    ]
    sources += [(ROOT / "a2_linux" / name, name) for name in ["protocol.py", "starter.py"]]
    for source, name in sources:
        guest(["sudo", "-n", "python3", "-c", COPY, scope + "/" + name], source.read_bytes())
    registry = json.loads(
        guest(
            [
                "sudo",
                "-n",
                "python3",
                "-B",
                scope + "/registrar.py",
                "init",
                vault,
                "--run-id",
                run_id,
            ]
        ).stdout
    )
    private = Path("/tmp/a4-scale-private-host-" + run_id)
    ca, public = create_ca(private)
    bundle = {"ca_public_key": public, "registry": sign(ca, registry)}
    guest(["sudo", "-n", "python3", "-c", COPY, scope + "/certificate.json"], canonical(bundle))
    paths = [
        "/var/tmp/a1-research-a4-scale-" + run_id + "/" + secrets.token_hex(16) for _ in range(100)
    ]
    setup = "import json,os,pathlib,sys;paths=json.loads(sys.stdin.buffer.read());pathlib.Path(paths[0]).parent.mkdir(mode=0o755);[(pathlib.Path(p).touch(exist_ok=False),os.chmod(p,0o666)) for p in paths]"
    guest(["sudo", "-n", "python3", "-c", setup], canonical(paths))
    guest(["sudo", "-n", "python3", "-c", COPY, scope + "/objects.json"], canonical(paths))
    pins = {
        "run_id": run_id,
        "scope": scope,
        "vault": vault,
        "ca_public_key": public,
        "agent_count": 100,
        "certificate": scope + "/certificate.json",
        "manifest": scope + "/objects.json",
        "stop": scope + "/stop",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "source_sha256": {
            str(source.relative_to(ROOT.parent)): hashlib.sha256(source.read_bytes()).hexdigest()
            for source, _ in sources
        },
        "positive_edges": 99,
        "positive_write_bytes": 16,
        "frontier_sizes": [2, 4, 8, 16, 32, 37],
        "job_expiry_ns": 5_000_000_000,
        "collector_max_seconds": 90,
        "negative_cases": ["replay", "foreign_claim", "refuse", "interrupt"],
    }
    dump(out / "registry.json", bundle)
    dump(out / "pins.json", pins)
    dump(out / "objects.json", paths)


def run(out):
    gate_result = gate(out)
    pins = json.loads((out / "pins.json").read_text())
    if (out / "attempt.json").exists():
        raise ValueError("attempt consumed; correction requires explicit new artifact directory")
    for source, sha in pins["source_sha256"].items():
        if hashlib.sha256(Path(source).read_bytes()).hexdigest() != sha:
            raise ValueError("unpinned runtime source")
    dump(
        out / "attempt.json",
        {
            "source_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
            "gate": gate_result["full_chain_gate"],
            "maximum_agents": 100,
        },
    )
    observer = None
    first = b""
    try:
        observer = subprocess.Popen(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                pins["scope"] + "/kernel.py",
                pins["manifest"],
                pins["stop"],
            ],
            env=ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("observer readiness")
        first = observer.stdout.readline()
        if not json.loads(first).get("ready"):
            raise ValueError("invalid ready")
        trial = subprocess.run(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                pins["scope"] + "/registrar.py",
                "run",
                pins["vault"],
                "--certificate",
                pins["certificate"],
                "--manifest",
                pins["manifest"],
                "--stop",
                pins["stop"],
            ],
            env=ENV,
            capture_output=True,
            timeout=85,
            check=False,
        )
        (out / "trial.jsonl").write_bytes(trial.stdout)
        (out / "trial.stderr.log").write_bytes(trial.stderr)
        if trial.returncode:
            guest(["sudo", "-n", "touch", pins["stop"]])
        rest, error = observer.communicate(timeout=15)
        (out / "capture.jsonl").write_bytes(first + rest)
        (out / "observer.stderr.log").write_bytes(error)
        dump(
            out / "process-status.json",
            {"registrar_exit": trial.returncode, "observer_exit": observer.returncode},
        )
        if trial.returncode or observer.returncode:
            raise RuntimeError("actual scale execution failed; raw checkpoints retained")
        result = next(
            row["result"]
            for row in [json.loads(line) for line in trial.stdout.splitlines()]
            if "result" in row
        )
        dump(out / "trial-result.json", result)
        print(
            json.dumps(
                {
                    "agents": result["agent_count"],
                    "main_jobs": len(result["rows"]),
                    "negative_cases": len(result["negatives"]),
                    "write_evaluation_pending": True,
                }
            )
        )
    except Exception as error:
        dump(
            out / "failure.json",
            {"type": type(error).__name__, "message": str(error), "classification": "UNBEKANNT"},
        )
        raise
    finally:
        if observer is not None and observer.poll() is None:
            guest(["sudo", "-n", "touch", pins["stop"]])
            rest, error = observer.communicate(timeout=15)
            (out / "capture.jsonl").write_bytes(first + rest)
            (out / "observer.stderr.log").write_bytes(error)
        guest(["sudo", "-n", "rm", "-rf", pins["vault"]])
        shutil.rmtree(Path("/tmp/a4-scale-private-host-" + pins["run_id"]), ignore_errors=True)
        dump(
            out / "private-cleanup.json",
            {"guest_vault_deleted": True, "host_ca_deleted": True, "keys_archived": False},
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run"])
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.output)
    else:
        run(args.output)
