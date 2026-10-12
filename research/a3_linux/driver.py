"""Real-client jobs, signed bounded dispatch, isolated Linux effect measurement."""

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
from client import run_client
from host_crypto import create_ca, sign, verify
from protocol import canonical
from score import evaluate
from shared_client import run_shared

BASE = ["limactl", "shell", "--workdir=/tmp", "a1-research"]
ENV = dict(os.environ, LIMA_HOME="/Users/landjunge/.local/share/agent-authority-a1-linux-vm")
CASES = [
    "codex",
    "grok",
    "child",
    "delegation",
    "exec",
    "session-switch",
    "shared-process",
    "replay",
    "key-share",
    "takeover",
]


def guest(args, data=None, timeout=30):
    return subprocess.run(
        BASE + args, input=data, capture_output=True, check=True, timeout=timeout, env=ENV
    )


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def prepare(out):
    state = json.loads((out / "state.json").read_text())
    state["vault"] = "/var/tmp/a2-private-a3-" + state["run_id"]
    state["certificate"] = "/opt/a3/certificate-" + state["run_id"] + ".json"
    code = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sys.stdin.buffer.read())"
    for directory in ["a3_linux", "a2_linux"]:
        for source in (Path("research") / directory).glob("*.py"):
            target = ("/opt/a3/" if directory == "a3_linux" else "/opt/a2_linux/") + source.name
            guest(["sudo", "-n", "python3", "-c", code, target], source.read_bytes())
    # A3 modules resolve ../a2_linux from /opt/a3.
    enrollment = json.loads(
        guest(
            [
                "sudo",
                "-n",
                "python3",
                "-B",
                "/opt/a3/guest.py",
                "init",
                state["vault"],
                state["run_id"],
            ]
        ).stdout
    )
    ca_file, public = create_ca(out / "private-ca")
    bundle = {"ca_public_key": public, "enrollment": sign(ca_file, enrollment)}
    assert verify(public, bundle["enrollment"])
    dump(out / "enrollment.json", bundle)
    guest(["sudo", "-n", "python3", "-c", code, state["certificate"]], canonical(bundle))
    dump(out / "state.json", state)
    lock = {
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "cases": CASES,
        "attempts_each": 1,
        "ca_public_key_pin": public,
        "enrollment_sha256": hashlib.sha256(canonical(bundle)).hexdigest(),
        "source_hashes": {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path("research/a3_linux").glob("*.py")
        },
    }
    dump(out / "pre-run-lock.json", lock)


def main(out):
    state = json.loads((out / "state.json").read_text())
    bundle = json.loads((out / "enrollment.json").read_text())
    lock = json.loads((out / "pre-run-lock.json").read_text())
    assert (
        subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        == lock["source_commit"]
    )
    assert not subprocess.check_output(["git", "status", "--porcelain"])
    assert all(
        hashlib.sha256(Path(p).read_bytes()).hexdigest() == value
        for p, value in lock["source_hashes"].items()
    )
    ca_file = out / "private-ca/ca-private.pem"
    runs = out / "runs"
    runs.mkdir(mode=0o700)
    first_dispatch = None
    cohort = []
    for position, case in enumerate(CASES, 1):
        client = "Grok" if position in [2, 10] else "Codex"
        expected = {
            "operation": "write16",
            "nonce": secrets.token_hex(16),
            "position": str(position),
            "claimed_client": client,
        }
        if position in [1, 2]:
            result = json.loads((out / f"client-{position}.json").read_text())
            expected = result["job"] if result["job"] else expected
            clients = [result]
            jobs = [result["job"]]
        elif case in ["session-switch", "shared-process"]:
            second = dict(expected, nonce=secrets.token_hex(16))
            shared = run_shared(
                [expected, second], out / f"client-{position}", case == "shared-process"
            )
            clients = [shared]
            jobs = shared["jobs"]
        else:
            result = run_client(
                client, expected, out / f"client-{position}", delegation=case == "delegation"
            )
            clients = [result]
            jobs = [result["job"]]
        if any(job is None for job in jobs):
            blocked = {
                "position": position,
                "case": case,
                "clients": clients,
                "classification": "UNBEKANNT",
                "blocker": "real client did not produce qualified job",
                "writer_executed": False,
            }
            dump(runs / f"case-{position}.json", blocked)
            cohort.append(blocked)
            print(position, case, "BLOCKED: real client qualification", flush=True)
            continue
        dispatches = [
            sign(
                ca_file,
                {
                    "domain": "A3-HOST-DISPATCH-v1",
                    "run_id": state["run_id"],
                    "client": client,
                    "job": job,
                    "client_evidence_sha256": hashlib.sha256(canonical(clients)).hexdigest(),
                    "provider_identity": "UNBEKANNT",
                    "model_identity": "UNBEKANNT",
                    "signer_scope": "trusted local controller, not provider",
                },
            )
            for job in jobs
        ]
        active = [job["nonce"] for job in jobs]
        if case == "replay":
            if first_dispatch is None:
                raise RuntimeError("no earlier public real-client dispatch available")
            dispatches = [first_dispatch]
        if first_dispatch is None:
            first_dispatch = dispatches[0]
        packet = {
            "jobs": dispatches,
            "active_nonce": active[0],
            "active_nonces": active,
            "ca_public_key": bundle["ca_public_key"],
        }
        path = "/var/tmp/a1-research-a2-a3-" + state["run_id"] + "/" + secrets.token_hex(8)
        setup = "import os,pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(exist_ok=True);os.chmod(p.parent,0o755);p.touch();os.chmod(p,0o666)"
        guest(["python3", "-c", setup, path])
        observer = subprocess.Popen(
            BASE + ["sudo", "-n", "python3", "-B", "/opt/a1/observer.py", path, "--duration", "12"],
            env=ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert observer.stdout is not None
        if not select.select([observer.stdout], [], [], 45)[0]:
            observer.terminate()
            raise TimeoutError("observer ready")
        first = observer.stdout.readline()
        if not first or not json.loads(first).get("ready"):
            raise RuntimeError("observer qualification")
        trial = subprocess.run(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                "/opt/a3/guest.py",
                "case",
                state["vault"],
                case,
                "--certificate",
                state["certificate"],
                "--path",
                path,
                "--identity",
                "Wrapper" + client,
            ],
            check=False,
            input=canonical(packet),
            capture_output=True,
            timeout=28,
            env=ENV,
        )
        rest, error = observer.communicate(timeout=20)
        capture = [json.loads(line) for line in (first + rest).splitlines()]
        payload = json.loads(trial.stdout) if trial.returncode == 0 else None
        result = {
            "position": position,
            "case": case,
            "clients": clients,
            "dispatch_packet": packet,
            "capture": capture,
            "trial": payload,
            "observer_exit": observer.returncode,
            "adapter_exit": trial.returncode,
            "source_commit": lock["source_commit"],
            "capture_sha256": hashlib.sha256(first + rest).hexdigest(),
            "trial_sha256": hashlib.sha256(trial.stdout).hexdigest(),
            "adapter_stderr_bytes": len(trial.stderr),
            "observer_stderr_bytes": len(error),
        }
        if trial.returncode == observer.returncode == 0:
            result["evaluation"] = evaluate(
                bundle, capture, payload, packet, bundle["ca_public_key"]
            )
        else:
            result["evaluation"] = {
                "real_agent_effect_chain": "UNBEKANNT",
                "execution_failure": True,
            }
            # Controlled Python/compile diagnostic only; never CLI/provider transcripts.
            (runs / f"case-{position}-diagnostic.txt").write_bytes(trial.stderr + error)
        dump(runs / f"case-{position}.json", result)
        cohort.append({"position": position, "case": case, "evaluation": result["evaluation"]})
        print(position, case, json.dumps(result["evaluation"]), flush=True)
    dump(
        runs / "cohort.json",
        {
            "cases": cohort,
            "source_commit": lock["source_commit"],
            "retry": False,
            "provider_authenticated_cases": 0,
        },
    )
    guest(["sudo", "-n", "rm", "-r", state["vault"]])
    shutil.rmtree(out / "private-ca")
    dump(
        out / "private-key-cleanup.json",
        {"guest_vault_removed": True, "host_ca_removed": True, "secure_RAM_erasure": "UNBEKANNT"},
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["prepare", "run"])
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    (prepare if args.mode == "prepare" else main)(args.directory)
