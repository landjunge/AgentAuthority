"""Prepare once, pin before trial, execute once, preserve raw failure evidence."""

import argparse
import hashlib
import json
import os
import secrets
import select
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import create_ca, sign
from protocol import canonical
from verify import evaluate

BASE = ["limactl", "shell", "--workdir=/tmp", "a1-research"]
ENV = dict(os.environ, LIMA_HOME="/Users/landjunge/.local/share/agent-authority-a1-linux-vm")
COPY = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sys.stdin.buffer.read())"


def guest(args, data=None, timeout=40):
    return subprocess.run(
        BASE + args, input=data, capture_output=True, check=True, timeout=timeout, env=ENV
    )


def dump(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def prepare(out):
    out.mkdir(parents=True, exist_ok=False)
    run_id = secrets.token_hex(16)
    scope = "/opt/a4c-" + run_id
    vault = "/var/tmp/a4c-private-" + run_id
    sources = [
        Path("research/a4_completion") / n
        for n in ["guest.py", "agent.py", "observer.py", "lifecycle.py", "probes.py"]
    ]
    sources += [Path("research/a2_linux") / n for n in ["protocol.py", "starter.py"]]
    for source in sources:
        guest(["sudo", "-n", "python3", "-c", COPY, scope + "/" + source.name], source.read_bytes())
    registry = json.loads(
        guest(
            ["sudo", "-n", "python3", "-B", scope + "/guest.py", "init", vault, "--run-id", run_id]
        ).stdout
    )
    private = Path("/tmp/a4-private-host-" + run_id)
    ca, public = create_ca(private)
    bundle = {"ca_public_key": public, "registry": sign(ca, registry)}
    certificate = scope + "/certificate.json"
    guest(["sudo", "-n", "python3", "-c", COPY, certificate], canonical(bundle))
    pins = {
        "run_id": run_id,
        "scope": scope,
        "vault": vault,
        "certificate": certificate,
        "pinned_ca_public_key": public,
        "prepared_source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "source_sha256": {str(s): hashlib.sha256(s.read_bytes()).hexdigest() for s in sources},
    }
    dump(out / "registry.json", bundle)
    dump(out / "pins.json", pins)
    return pins


def run(out):
    if (out / "attempt.json").exists():
        raise ValueError("single attempt already consumed; no retry")
    pins = json.loads((out / "pins.json").read_text())
    for source, expected in pins["source_sha256"].items():
        if hashlib.sha256(Path(source).read_bytes()).hexdigest() != expected:
            raise ValueError("prepared source changed")
    attempt = {
        "attempts": 1,
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "controlled_agent_count": 2,
    }
    dump(out / "attempt.json", attempt)
    path = "/var/tmp/a1-research-a4-" + pins["run_id"] + "/" + secrets.token_hex(16)
    setup = "import os,pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(mode=0o755);p.touch();os.chmod(p,0o666)"
    observer = None
    try:
        guest(["sudo", "-n", "python3", "-c", setup, path])
        observer = subprocess.Popen(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                pins["scope"] + "/observer.py",
                path,
                "--duration",
                "12",
            ],
            env=ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("observer readiness")
        first = observer.stdout.readline()
        if not json.loads(first).get("ready"):
            raise ValueError("observer not ready")
        trial = subprocess.run(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                pins["scope"] + "/guest.py",
                "trial",
                pins["vault"],
                "--certificate",
                pins["certificate"],
                "--path",
                path,
            ],
            env=ENV,
            check=False,
            capture_output=True,
            timeout=35,
        )
        rest, errors = observer.communicate(timeout=20)
        (out / "capture.jsonl").write_bytes(first + rest)
        (out / "trial.stdout.json").write_bytes(trial.stdout)
        (out / "trial.stderr.log").write_bytes(trial.stderr)
        (out / "observer.stderr.log").write_bytes(errors)
        dump(
            out / "process-status.json",
            {"observer_exit": observer.returncode, "trial_exit": trial.returncode},
        )
        if trial.returncode or observer.returncode:
            raise RuntimeError("actual trial failed; preserved outputs, no retry")
        result = evaluate(
            json.loads((out / "registry.json").read_text()),
            [json.loads(line) for line in (first + rest).splitlines()],
            json.loads(trial.stdout),
            pins["pinned_ca_public_key"],
        )
        dump(out / "evaluation.json", result)
        print(json.dumps(result))
    except Exception as error:
        dump(
            out / "failure.json",
            {
                "type": type(error).__name__,
                "message": str(error),
                "classification": "UNBEKANNT",
                "phase2_executed": False,
            },
        )
        raise
    finally:
        if observer is not None and observer.poll() is None:
            observer.communicate(timeout=20)
        guest(["sudo", "-n", "rm", "-rf", pins["vault"]])
        shutil.rmtree(Path("/tmp/a4-private-host-" + pins["run_id"]), ignore_errors=True)
        dump(
            out / "private-cleanup.json",
            {
                "guest_private_vault_deleted": True,
                "host_private_ca_deleted": True,
                "keys_archived": False,
            },
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
