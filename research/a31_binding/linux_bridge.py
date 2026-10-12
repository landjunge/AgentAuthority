"""Only two new integration effects justified by A3.1's new client-process receipt."""

import json
import secrets
import select
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a3_linux"))
from driver import BASE, ENV, guest
from score import evaluate

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from host_crypto import sign
from protocol import canonical
from receipt import check, digest


def run(out):
    state = json.loads((out / "state.json").read_text())
    ca = Path(state["ca_file"])
    vault = "/var/tmp/a2-private-a31-" + state["run_id"]
    certificate = "/opt/a31_dispatch/certificate-" + state["run_id"] + ".json"
    copy = "import pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(sys.stdin.buffer.read())"
    for name in ["guest.py", "worker.py"]:
        guest(
            ["sudo", "-n", "python3", "-c", copy, "/opt/a31_dispatch/" + name],
            (Path("research/a3_linux") / name).read_bytes(),
        )
    raw = guest(
        [
            "sudo",
            "-n",
            "python3",
            "-B",
            "/opt/a31_dispatch/guest.py",
            "init",
            vault,
            state["run_id"],
        ]
    ).stdout
    enrollment = {"ca_public_key": state["ca_public_key"], "enrollment": sign(ca, json.loads(raw))}
    (out / "linux-enrollment.json").write_text(json.dumps(enrollment, indent=2) + "\n")
    guest(["sudo", "-n", "python3", "-c", copy, certificate], canonical(enrollment))
    used = set()
    for i in [1, 2]:
        source = json.loads((out / f"case-{i}.json").read_text())
        gate_time = time.monotonic_ns()
        validity = check(
            source["local_receipt"],
            state["ca_public_key"],
            source["context"],
            source["job"],
            gate_time,
            used,
        )
        row = {
            "position": i,
            "client_receipt_sha256": digest(source["local_receipt"]),
            "entry_gate": validity,
            "entry_gate_ns": gate_time,
            "source_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip(),
        }
        if not validity["qualified"]:
            row["classification"] = "UNBEKANNT"
            row["writer_executed"] = False
            (out / f"integration-{i}.json").write_text(json.dumps(row, indent=2) + "\n")
            print(i, "not executed", validity, flush=True)
            continue
        dispatch = sign(
            ca,
            {
                "domain": "A3-HOST-DISPATCH-v1",
                "run_id": state["run_id"],
                "client": source["context"]["client"],
                "job": source["job"],
                "local_client_receipt_sha256": digest(source["local_receipt"]),
                "provider_identity": "UNBEKANNT",
                "model_identity": "UNBEKANNT",
            },
        )
        packet = {
            "ca_public_key": state["ca_public_key"],
            "jobs": [dispatch],
            "active_nonce": source["job"]["nonce"],
            "active_nonces": [source["job"]["nonce"]],
        }
        path = "/var/tmp/a1-research-a2-a3-a31-" + state["run_id"] + "/" + secrets.token_hex(8)
        setup = "import os,pathlib,sys;p=pathlib.Path(sys.argv[1]);p.parent.mkdir(exist_ok=True);p.touch();os.chmod(p,0o666)"
        guest(["python3", "-c", setup, path])
        observer = subprocess.Popen(
            BASE + ["sudo", "-n", "python3", "-B", "/opt/a1/observer.py", path, "--duration", "12"],
            env=ENV,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert observer.stdout
        if not select.select([observer.stdout], [], [], 45)[0]:
            raise TimeoutError("observer ready")
        first = observer.stdout.readline()
        assert json.loads(first).get("ready")
        trial = subprocess.run(
            BASE
            + [
                "sudo",
                "-n",
                "python3",
                "-B",
                "/opt/a31_dispatch/guest.py",
                "case",
                vault,
                "codex" if i == 1 else "grok",
                "--certificate",
                certificate,
                "--path",
                path,
                "--identity",
                "Wrapper" + source["context"]["client"],
            ],
            input=canonical(packet),
            check=False,
            capture_output=True,
            timeout=28,
            env=ENV,
        )
        rest, error = observer.communicate(timeout=20)
        capture = [json.loads(line) for line in (first + rest).splitlines()]
        payload = json.loads(trial.stdout) if trial.returncode == 0 else None
        row.update(
            dispatch_packet=packet,
            capture=capture,
            trial=payload,
            observer_exit=observer.returncode,
            adapter_exit=trial.returncode,
            stderr_bytes=len(trial.stderr) + len(error),
            writer_executed=True,
        )
        if trial.returncode == observer.returncode == 0:
            row["evaluation"] = evaluate(
                enrollment, capture, payload, packet, state["ca_public_key"]
            )
            row["all_writes_before_client_receipt_expiry"] = all(
                record["record"]["entry_ns"] >= 0
                for record in capture
                if record.get("record", {}).get("kind") == 1
            )
            row["host_collection_end_before_receipt_expiry"] = (
                time.monotonic_ns() < source["local_receipt"]["body"]["expires_ns"]
            )
        else:
            row["classification"] = "UNBEKANNT"
        (out / f"integration-{i}.json").write_text(json.dumps(row, indent=2) + "\n")
        print(
            i,
            row.get("evaluation"),
            row.get("host_collection_end_before_receipt_expiry"),
            flush=True,
        )
    guest(["sudo", "-n", "rm", "-r", vault])
    (out / "guest-key-cleanup.json").write_text(
        json.dumps({"vault_removed": True, "vault": vault}) + "\n"
    )


if __name__ == "__main__":
    run(Path(Path("/tmp/a31-active-path").read_text().strip()))
