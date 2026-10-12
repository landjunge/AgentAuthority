"""Exactly100 locally enrolled principals, real tree handovers and counterchecks."""

import argparse
import hashlib
import json
import os
import resource
import secrets
import select
import socket
import subprocess
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from guest import digest, key, proc, receive
from lifecycle import Lifecycle
from protocol import canonical, envelope, public, verify
from starter import boot, memfd

AGENTS = {f"Agent{i:03}": 62000 + i for i in range(100)}


def initialize(vault, run_id):
    vault.mkdir(mode=0o700)
    for name in ["registrar", *AGENTS]:
        value = Ed25519PrivateKey.generate().private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
        fd = os.open(vault / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.write(fd, value)
        os.close(fd)
    return {
        "domain": "A4-SCALE-REGISTRY-v1",
        "run_id": run_id,
        "boot_hash": boot(),
        "pid_namespace": os.readlink("/proc/self/ns/pid"),
        "test_identities_only": True,
        "agents": {
            name: {"uid": uid, "public_key": public(key(vault, name))}
            for name, uid in AGENTS.items()
        },
        "registrar_public_key": public(key(vault, "registrar")),
        "worker_sha256": hashlib.sha256(
            Path(__file__).with_name("worker.py").read_bytes()
        ).hexdigest(),
        "provider_model_identity": "UNBEKANNT",
        "clock_ticks": os.sysconf("SC_CLK_TCK"),
    }


class Trial:
    def __init__(self, vault, bundle, paths, stop):
        self.vault, self.paths, self.stop = vault, paths, stop
        self.registry = bundle["registry"]["body"]
        if not verify(bundle["ca_public_key"], bundle["registry"]) or set(
            self.registry["agents"]
        ) != set(AGENTS):
            raise ValueError("registry")
        if self.registry["boot_hash"] != boot() or self.registry["pid_namespace"] != os.readlink(
            "/proc/self/ns/pid"
        ):
            raise ValueError("boot/namespace")
        if (
            self.registry["worker_sha256"]
            != hashlib.sha256(Path(__file__).with_name("worker.py").read_bytes()).hexdigest()
        ):
            raise ValueError("worker source")
        self.start = resource.getrusage(resource.RUSAGE_SELF)
        self.life = Lifecycle()
        self.child_start = resource.getrusage(resource.RUSAGE_CHILDREN)
        self.children, self.channels, self.bindings, self.oracle = {}, {}, {}, {}
        self.rows, self.nonces, self.samples = {}, set(), []
        self.signer = key(vault, "registrar")

    def launch(self):
        for index, (name, uid) in enumerate(AGENTS.items()):
            parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            parent.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            parent.settimeout(5)
            keyfd = memfd((self.vault / name).read_bytes())
            process = subprocess.Popen(
                [
                    "/usr/bin/python3",
                    "-B",
                    str(Path(__file__).with_name("worker.py")),
                    name,
                    str(keyfd),
                    str(child.fileno()),
                    self.paths[index],
                ],
                pass_fds=[keyfd, child.fileno()],
                user=uid,
                group=uid,
                extra_groups=[],
                close_fds=True,
                env={"PATH": "/usr/bin:/bin", "LANG": "C"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            child.close()
            os.close(keyfd)
            pidfd = os.pidfd_open(process.pid)
            self.children[name] = (process, pidfd)
            self.channels[name] = parent
            for _ in range(200):
                try:
                    state = self.life.state(process.pid)
                except KeyError:
                    continue
                if state["generation"] == 1:
                    break
            else:
                raise RuntimeError("missing registered exec")
            if select.select([pidfd], [], [], 0)[0]:
                raise RuntimeError("dead actor before proof")
            challenge = {
                "domain": "A4-SCALE-CHALLENGE-v1",
                "nonce": secrets.token_hex(32),
                "run_id": self.registry["run_id"],
                "boot_hash": boot(),
                "pid_namespace": self.registry["pid_namespace"],
                "instance": state,
            }
            parent.send(canonical({"challenge": challenge, "registry": self.registry}))
            message, cred = receive(parent)
            proof = message["value"]
            if (
                message["type"] != "proof"
                or not verify(self.registry["agents"][name]["public_key"], proof)
                or proof["body"]
                != {"domain": "A4-SCALE-POP-v1", "identity": name, "challenge": challenge}
                or cred != {"pid": process.pid, "uid": uid, "gid": uid}
            ):
                raise ValueError("proof binding")
            self.bindings[name] = {
                "proof": proof,
                "credentials": cred,
                "instance": state,
                "bound_ns": time.monotonic_ns(),
            }
            target = os.stat(self.paths[index], follow_symlinks=False)
            self.oracle[name] = {
                "spawn_pid": process.pid,
                "uid": uid,
                "proc_before": proc(process.pid),
                "file": {
                    "inode": target.st_ino,
                    "dev": (os.major(target.st_dev) << 20) | os.minor(target.st_dev),
                },
            }
        self.sample()
        print(
            json.dumps(
                {
                    "checkpoint": "registered",
                    "agents": len(self.bindings),
                    "bindings": self.bindings,
                    "oracle": self.oracle,
                }
            ),
            flush=True,
        )

    def sample(self):
        values = {}
        for name, (child, _) in self.children.items():
            try:
                lines = Path(f"/proc/{child.pid}/status").read_text().splitlines()
                values[name] = (
                    int(next(line.split()[1] for line in lines if line.startswith("VmRSS:"))) * 1024
                )
            except (OSError, StopIteration):
                values[name] = None
        mem = {
            line.split(":", 1)[0]: int(line.split()[1]) * 1024
            for line in Path("/proc/meminfo").read_text().splitlines()
            if line.startswith(("MemAvailable:", "MemFree:"))
        }
        self.samples.append(
            {
                "stamp_ns": time.monotonic_ns(),
                "agent_rss_bytes": values,
                "sum_rss_bytes": sum(v for v in values.values() if v is not None),
                "vm_memory": mem,
            }
        )

    def make_job(self, sender, receiver, operation="write16"):
        link = None
        if sender != "Agent000":
            parent = next(
                row
                for row in self.rows.values()
                if row["delegation"]["body"]["receiver"] == sender and row.get("done")
            )
            link = {
                "delegation_sha256": digest(parent["delegation"]),
                "acceptance_sha256": digest(parent["acceptance"]),
            }
        now = time.monotonic_ns()
        job = {"operation": operation, "file": self.oracle[receiver]["file"]}
        return {
            "domain": "A4-SCALE-DELEGATION-v1",
            "delegation_id": secrets.token_hex(32),
            "nonce": secrets.token_hex(32),
            "sender": sender,
            "receiver": receiver,
            "sender_instance": self.bindings[sender]["instance"],
            "receiver_instance": self.bindings[receiver]["instance"],
            "run_id": self.registry["run_id"],
            "boot_hash": boot(),
            "pid_namespace": self.registry["pid_namespace"],
            "issued_ns": now,
            "expires_ns": now + 5_000_000_000,
            "job": job,
            "job_digest": digest(job),
            "parent_link": link,
        }

    def actual_sender(self, name, credentials):
        binding = self.bindings[name]
        state = self.life.state(credentials["pid"])
        return (
            credentials == binding["credentials"]
            and state["start_ns"] == binding["instance"]["start_ns"]
            and state["generation"] == 1
            and not state["exit_ns"]
            and not select.select([self.children[name][1]], [], [], 0)[0]
        )

    def level(self, receivers):
        expected, done, accepted = {}, set(), set()
        released = False
        for index in receivers:
            sender, receiver = f"Agent{(index - 1) // 2:03}", f"Agent{index:03}"
            job = self.make_job(sender, receiver)
            expected[job["delegation_id"]] = job
            self.channels[sender].send(canonical({"issue": job}))
        limit = time.monotonic() + 6
        while len(done) < len(expected):
            if time.monotonic() > limit:
                raise TimeoutError("bounded frontier did not complete")
            self.life.poll()
            available = select.select(list(self.channels.values()), [], [], 0.02)[0]
            for channel in available:
                name = next(n for n, c in self.channels.items() if c is channel)
                message, cred = receive(channel)
                if not self.actual_sender(name, cred):
                    raise ValueError("changed actual sender")
                if message["type"] == "delegation":
                    value = message["value"]
                    body = value["body"]
                    identifier = body["delegation_id"]
                    if (
                        body != expected[identifier]
                        or name != body["sender"]
                        or not verify(self.registry["agents"][name]["public_key"], value)
                        or body["nonce"] in self.nonces
                    ):
                        raise ValueError("invalid/replayed delegation")
                    self.nonces.add(body["nonce"])
                    row = {
                        "delegation": value,
                        "sender_credentials": cred,
                        "received_ns": time.monotonic_ns(),
                        "forwarded_ns": time.monotonic_ns(),
                    }
                    self.rows[identifier] = row
                    self.channels[body["receiver"]].send(canonical({"receive": value}))
                elif message["type"] == "acceptance":
                    value = message["value"]
                    identifier = value["body"]["delegation_id"]
                    row = self.rows[identifier]
                    if (
                        name != row["delegation"]["body"]["receiver"]
                        or value["body"]["delegation_sha256"] != digest(row["delegation"])
                        or not verify(self.registry["agents"][name]["public_key"], value)
                    ):
                        raise ValueError("invalid acceptance")
                    row.update(
                        acceptance=value,
                        receiver_credentials=cred,
                        accepted_ns=time.monotonic_ns(),
                    )
                    accepted.add(identifier)
                elif message["type"] == "done":
                    identifier = message["delegation_id"]
                    row = self.rows[identifier]
                    if (
                        name != row["delegation"]["body"]["receiver"]
                        or message["result"] != 16
                        or identifier in done
                    ):
                        raise ValueError("invalid/duplicate completion")
                    row.update(
                        done=message, done_credentials=cred, done_received_ns=time.monotonic_ns()
                    )
                    done.add(identifier)
                else:
                    raise ValueError("unexpected message")
            if len(accepted) == len(expected) and not released:
                # All frontier recipients are waiting. Release without per-peer
                # polling so the kernel can schedule the writes concurrently.
                for identifier in expected:
                    row = self.rows[identifier]
                    row["release_ns"] = time.monotonic_ns()
                    row["receipt"] = envelope(
                        self.signer,
                        {"domain": "A4-SCALE-WITNESS-v1", "run_id": self.registry["run_id"], **row},
                    )
                    receiver = row["delegation"]["body"]["receiver"]
                    self.channels[receiver].send(
                        canonical(
                            {"go": identifier, "acceptance_sha256": digest(row["acceptance"])}
                        )
                    )
                released = True
        self.sample()
        print(
            json.dumps(
                {
                    "checkpoint": "frontier",
                    "completed": len(self.rows),
                    "rows": [self.rows[i] for i in expected],
                }
            ),
            flush=True,
        )

    def negatives(self):
        result = []
        first = list(self.rows.values())[-1]
        sender = first["delegation"]["body"]["sender"]
        self.channels[sender].send(
            canonical({"replay": first["delegation"]["body"]["delegation_id"]})
        )
        message, cred = receive(self.channels[sender])
        same = message["value"] == first["delegation"]
        replay = message["value"]["body"]["nonce"] in self.nonces
        result.append(
            {
                "case": "replay",
                "packet": message,
                "credentials": cred,
                "same_original_packet": same,
                "nonce_already_used": replay,
                "actual_sender_bound": self.actual_sender(sender, cred),
                "forwarded": False,
                "observed_ns": time.monotonic_ns(),
            }
        )
        self.channels[sender].send(canonical({"rejected": "replay"}))
        foreign = self.make_job("Agent001", "Agent098")
        self.channels["Agent099"].send(canonical({"foreign_claim": foreign}))
        message, cred = receive(self.channels["Agent099"])
        result.append(
            {
                "case": "foreign_claim",
                "packet": message,
                "credentials": cred,
                "claimed_signature_valid": verify(
                    self.registry["agents"]["Agent001"]["public_key"], message["value"]
                ),
                "actual_signature_valid": verify(
                    self.registry["agents"]["Agent099"]["public_key"], message["value"]
                ),
                "actual_sender_bound": self.actual_sender("Agent099", cred),
                "forwarded": False,
                "observed_ns": time.monotonic_ns(),
            }
        )
        self.channels["Agent099"].send(canonical({"rejected": "foreign_claim"}))
        for receiver, operation in [("Agent098", "refuse"), ("Agent099", "interrupt")]:
            sender = f"Agent{(int(receiver[-3:]) - 1) // 2:03}"
            job = self.make_job(sender, receiver, operation)
            self.channels[sender].send(canonical({"issue": job}))
            packet, sender_cred = receive(self.channels[sender])
            received = time.monotonic_ns()
            self.channels[receiver].send(canonical({"receive": packet["value"]}))
            response, receiver_cred = receive(self.channels[receiver])
            row = {
                "case": operation,
                "delegation": packet["value"],
                "response": response,
                "sender_credentials": sender_cred,
                "receiver_credentials": receiver_cred,
                "received_ns": received,
                "response_received_ns": time.monotonic_ns(),
                "released": False,
            }
            if operation == "interrupt":
                pid = self.children[receiver][0].pid
                self.oracle[receiver]["proc_after"] = proc(pid)
                self.oracle[receiver]["kernel_after"] = self.life.state(pid)
                self.children[receiver][0].terminate()
                self.children[receiver][0].wait(timeout=5)
                row["interrupted_exit"] = self.children[receiver][0].returncode
            row["receipt"] = envelope(
                self.signer, {"domain": "A4-SCALE-NEGATIVE-WITNESS-v1", **row}
            )
            result.append(row)
        for row in result[:2]:
            row["receipt"] = envelope(
                self.signer, {"domain": "A4-SCALE-NEGATIVE-WITNESS-v1", **row}
            )
        return result

    def finish(self, negatives):
        for name, (child, _) in self.children.items():
            if child.poll() is None:
                self.oracle[name]["proc_after"] = proc(child.pid)
                self.oracle[name]["kernel_after"] = self.life.state(child.pid)
                self.channels[name].send(canonical({"stop": True}))
        for name, (child, pidfd) in self.children.items():
            stdout, stderr = child.communicate(timeout=6)
            self.oracle[name].update(
                exit_code=child.returncode,
                stderr_bytes=len(stderr),
                worker_summary=json.loads(stdout) if stdout else None,
                pidfd_exited=bool(select.select([pidfd], [], [], 0)[0]),
            )
        for _ in range(5):
            self.life.poll()
        lifecycle = self.life.finish()
        self.life = None
        after = resource.getrusage(resource.RUSAGE_SELF)
        children = resource.getrusage(resource.RUSAGE_CHILDREN)
        Path(self.stop).touch(exist_ok=False)
        return {
            "agent_count": len(self.bindings),
            "bindings": self.bindings,
            "oracle": self.oracle,
            "rows": list(self.rows.values()),
            "negatives": negatives,
            "lifecycle": lifecycle,
            "memory_samples": self.samples,
            "cpu_user_seconds": after.ru_utime - self.start.ru_utime,
            "cpu_system_seconds": after.ru_stime - self.start.ru_stime,
            "rss_peak_bytes": after.ru_maxrss * 1024,
            "workers_cpu_user_seconds": children.ru_utime - self.child_start.ru_utime,
            "workers_cpu_system_seconds": children.ru_stime - self.child_start.ru_stime,
            "resource_scope": "registrar includes BCCcompile; child CPU measured after compiler before100 workers; RSS sums are snapshots",
        }

    def cleanup(self):
        for channel in self.channels.values():
            channel.close()
        for child, pidfd in self.children.values():
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
            os.close(pidfd)
        if self.life is not None:
            self.life.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "run"])
    parser.add_argument("vault", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--stop")
    args = parser.parse_args()
    if os.geteuid() != 0 or not str(args.vault).startswith("/var/tmp/a4-scale-private-"):
        raise ValueError("isolated guest root only")
    if args.command == "init":
        print(json.dumps(initialize(args.vault, args.run_id)))
    else:
        trial = Trial(
            args.vault,
            json.loads(args.certificate.read_text()),
            json.loads(args.manifest.read_text()),
            args.stop,
        )
        try:
            trial.launch()
            index = 1
            while index < 100:
                end = min(2 * index + 1, 100)
                trial.level(range(index, end))
                index = end
            negative_cases = trial.negatives()
            print(json.dumps({"result": trial.finish(negative_cases)}), flush=True)
        finally:
            trial.cleanup()
