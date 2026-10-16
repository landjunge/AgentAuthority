"""Explicit local worker; one preinstalled synthetic scenario, no arbitrary code."""

import fcntl
import hashlib
import json
import secrets
import subprocess
from pathlib import Path

from research.hosted_qualification import live_gate
from research.private_service.protocol import Problem, blob, blob_digest, canonical, request

ROOT = Path(__file__).resolve().parents[2]
LIMA_HOME = "/Users/landjunge/.local/share/agent-authority-a1-linux-vm"
LOCK = Path(LIMA_HOME) / "aa-private-service.lock"


def qualify_environment():
    # Read actual VM config before every dispatch, never provision/modify packages.
    info = subprocess.run(
        ["limactl", "list", "--json"],
        env=live_gate.driver.ENV,
        check=True,
        capture_output=True,
        timeout=10,
    )
    vm = next(
        json.loads(line)
        for line in info.stdout.splitlines()
        if json.loads(line)["name"] == "a1-research"
    )
    cfg = vm["config"]
    if vm["status"] != "Running" or cfg.get("mounts") or cfg["ssh"].get("forwardAgent"):
        raise RuntimeError("isolated running a1-research VM required; no mounts/agent forwarding")
    probes = live_gate.driver.guest(
        ["sudo", "-n", "cat", "/sys/kernel/tracing/kprobe_events"]
    ).stdout
    if probes.strip():
        raise RuntimeError("existing guest probes present; preserve active trial")
    observed = live_gate.driver.guest(["uname", "-r"]).stdout.decode().strip()
    if observed != "6.8.0-142-generic":
        raise RuntimeError("runner kernel not qualified: " + observed)


def run_once(service, deliver):
    with LOCK.open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise Problem(409, "RUNNER_BUSY") from error
        service.recover()
        qualify_environment()
        binding = service.claim()
        if binding is None:
            return {"state": "idle"}
        tenant, jid = binding["tenant"], binding["job_id"]
        output = service.state / ("evidence-" + jid)
        old_prepare = live_gate.driver.prepare
        runner_kid = service.config["runner_kid"]

        def prepare(out):
            pins = old_prepare(out)
            # This pin originates in control-plane preparation before execution.
            live_gate.driver.guest(
                [
                    "sudo",
                    "-n",
                    "python3",
                    "-c",
                    live_gate.driver.COPY,
                    pins["scope"] + "/original_guest.py",
                ],
                (ROOT / "research/a4_completion/guest.py").read_bytes(),
            )
            adapter = ROOT / "research/private_service/guest_adapter.py"
            live_gate.driver.guest(
                ["sudo", "-n", "python3", "-c", live_gate.driver.COPY, pins["scope"] + "/guest.py"],
                adapter.read_bytes(),
            )
            live_gate.driver.guest(
                [
                    "sudo",
                    "-n",
                    "python3",
                    "-c",
                    live_gate.driver.COPY,
                    pins["scope"] + "/service-binding.json",
                ],
                canonical(binding),
            )
            pins["source_sha256"]["research/private_service/guest_adapter.py"] = hashlib.sha256(
                adapter.read_bytes()
            ).hexdigest()
            pins["source_kid"] = runner_kid
            live_gate.dump(out / "pins.json", pins)
            with service.connection() as db:
                db.execute("BEGIN IMMEDIATE")
                db.execute(
                    "INSERT INTO dispatch_pins VALUES (?,?,?)", (tenant, jid, json.dumps(pins))
                )
                db.commit()
            return pins

        try:
            live_gate.driver.prepare = prepare
            # Existing lifecycle, key cleanup and conservative original evaluation.
            live_gate.run(output)
            pins = json.loads((output / "pins.json").read_text())
            package = {
                "registry": blob((output / "registry.json").read_bytes()),
                "capture": blob((output / "capture.jsonl").read_bytes()),
                "trial": blob((output / "trial.stdout.json").read_bytes()),
            }
            package["manifest"] = dict(
                schema="aa-evidence-v1",
                source_id=runner_kid,
                source_class="controlled-linux-collector",
                run_id=pins["run_id"],
                complete=True,
                **{k + "_sha256": blob_digest(v) for k, v in package.items()},
            )
            path = f"/v1/jobs/{jid}/evidence"
            signed = request(
                service.config["runner_private_key"],
                tenant,
                runner_kid,
                path,
                package,
                "evidence-" + jid,
                secrets.token_hex(32),
            )
            result = deliver(path, signed)
            if result[0] != 201:
                raise RuntimeError("evidence intake failed: " + str(result[0]))
            return {"state": "completed", "job_id": jid, "output": str(output)}
        except Exception:
            with service.connection() as db:
                db.execute("BEGIN IMMEDIATE")
                state = db.execute(
                    "SELECT state FROM jobs WHERE tenant=? AND id=?", (tenant, jid)
                ).fetchone()
                if state and state[0] == "running":
                    service._unknown(db, tenant, jid, "RUNNER_OR_INTAKE_ERROR")
                db.commit()
            raise
        finally:
            live_gate.driver.prepare = old_prepare


if __name__ == "__main__":
    import argparse

    from research.private_service.http import call
    from research.private_service.service import Service

    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    service = Service(args.state, config)
    print(
        json.dumps(
            run_once(
                service,
                lambda path, packet: call(args.url, config["runner_token"], "POST", path, packet),
            )
        )
    )
