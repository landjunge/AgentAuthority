"""Host-side experiment: independent pinned-key OpenSSL checks, no collector oracle input."""

import argparse
import hashlib
import json
import os
import select
import subprocess
import time
from pathlib import Path

from host_crypto import evaluate, verify

BASE = ["limactl", "shell", "--workdir=/tmp", "a1-research"]
VM_HOME = "/Users/landjunge/.local/share/agent-authority-a1-linux-vm"
CASES = ["alpha", "beta", "false-claim", "child", "exec", "reuse", "takeover", "replay"]


def main(out):
    state = json.loads((out / "local-run.json").read_text())
    bundle = json.loads((out / "enrollment.json").read_text())
    ca = bundle["ca_public_key"]
    assert verify(ca, bundle["enrollment"])
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    assert not subprocess.check_output(["git", "status", "--porcelain"])
    runs = out / "runs"
    runs.mkdir(mode=0o700)
    env = dict(os.environ, LIMA_HOME=VM_HOME)
    results = []
    lock = {
        "source_commit": source,
        "cases": CASES,
        "attempts_each": 1,
        "ca_public_key_pin": ca,
        "enrollment_sha256": hashlib.sha256((out / "enrollment.json").read_bytes()).hexdigest(),
    }
    (out / "pre-run-lock.json").write_text(json.dumps(lock, indent=2) + "\n")
    for index, case in enumerate(CASES, 1):
        path = "/var/tmp/a1-research-a2-" + state["run_id"] + "/" + os.urandom(8).hex()
        setup = "import os,pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(exist_ok=True);p.touch();os.chmod(p,0o666)"
        subprocess.run(BASE + ["python3", "-c", setup, path], env=env, check=True, timeout=15)
        observer = subprocess.Popen(
            BASE + ["sudo", "-n", "python3", "-B", "/opt/a1/observer.py", path, "--duration", "12"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert observer.stdout is not None
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("A1 collector ready")
        first = observer.stdout.readline()
        if not first:
            rest, error = observer.communicate(timeout=5)
            raise RuntimeError("A1 source qualification failed: " + str(len(error)))
        assert json.loads(first).get("ready") is True
        started = time.monotonic_ns()
        trial = subprocess.run(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                "/opt/a2/starter.py",
                "case",
                state["vault"],
                case,
                "--certificate",
                state["certificate"],
                "--path",
                path,
            ],
            env=env,
            capture_output=True,
            timeout=25,
        )
        rest, error = observer.communicate(timeout=20)
        capture = [json.loads(line) for line in (first + rest).splitlines()]
        payload = json.loads(trial.stdout) if trial.returncode == 0 else None
        result = {
            "position": index,
            "case": case,
            "source_commit": source,
            "observer_exit": observer.returncode,
            "starter_exit": trial.returncode,
            "capture": capture,
            "trial": payload,
            "capture_sha256": hashlib.sha256(first + rest).hexdigest(),
            "trial_sha256": hashlib.sha256(trial.stdout).hexdigest(),
            "starter_stderr_bytes": len(trial.stderr),
            "observer_stderr_bytes": len(error),
            "host_collection_ns": time.monotonic_ns() - started,
        }
        if observer.returncode == trial.returncode == 0:
            result["evaluation"] = evaluate(bundle, capture, payload, ca)
        else:
            result["evaluation"] = {"identity_effect_chain": "UNBEKANNT", "execution_failure": True}
            (runs / f"case-{index}-diagnostic.txt").write_bytes(trial.stderr + error)
        (runs / f"case-{index}.json").write_text(json.dumps(result, indent=2) + "\n")
        results.append({"position": index, "case": case, "evaluation": result["evaluation"]})
        print(index, case, result["evaluation"], flush=True)
    (runs / "cohort.json").write_text(
        json.dumps(
            {
                "source_commit": source,
                "cases": results,
                "test_identities_only": True,
                "retry": False,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    main(parser.parse_args().directory)
