"""Trusted research registrar/transport witness, isolated guest root only."""

import argparse
import hashlib
import json
import os
import resource
import secrets
import select
import socket
import struct
import subprocess
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from lifecycle import Lifecycle
from protocol import canonical, envelope, public, verify
from starter import boot, memfd

AGENTS = {"TestA": 61101, "TestB": 61102}


def key(vault, name):
    return Ed25519PrivateKey.from_private_bytes((vault / name).read_bytes())


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


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
        "domain": "A4-REGISTRY-v1",
        "run_id": run_id,
        "boot_hash": boot(),
        "pid_namespace": os.readlink("/proc/self/ns/pid"),
        "agents": {
            name: {"uid": uid, "public_key": public(key(vault, name))}
            for name, uid in AGENTS.items()
        },
        "registrar_public_key": public(key(vault, "registrar")),
        "agent_sha256": hashlib.sha256(
            Path(__file__).with_name("agent.py").read_bytes()
        ).hexdigest(),
        "test_identities_only": True,
        "provider_identity": "UNBEKANNT",
    }


def receive(channel):
    payload, ancillary, flags, _ = channel.recvmsg(32768, socket.CMSG_SPACE(12))
    credentials = [
        struct.unpack("3i", data[:12])
        for level, kind, data in ancillary
        if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS
    ]
    if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC) or len(credentials) != 1:
        raise ValueError("missing/truncated sender credentials")
    return json.loads(payload), dict(zip(["pid", "uid", "gid"], credentials[0], strict=True))


def proc(pid):
    # /proc stat comm may contain spaces/parentheses; split after closing comm.
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return {"pid": pid, "start_ticks": int(fields[19]), "state": fields[0]}


def trial(vault, certificate, path):
    if not str(path).startswith("/var/tmp/a1-research-a4-"):
        raise ValueError("artificial scope required")
    bundle = json.loads(certificate.read_text())
    if not verify(bundle["ca_public_key"], bundle["registry"]):
        raise ValueError("registry signature")
    registry = bundle["registry"]["body"]
    if registry["boot_hash"] != boot() or registry["pid_namespace"] != os.readlink(
        "/proc/self/ns/pid"
    ):
        raise ValueError("stale namespace/boot")
    if (
        registry["agent_sha256"]
        != hashlib.sha256(Path(__file__).with_name("agent.py").read_bytes()).hexdigest()
    ):
        raise ValueError("worker source changed")
    start_cpu = resource.getrusage(resource.RUSAGE_SELF)
    life = Lifecycle()
    children, channels, states, oracle, bindings = {}, {}, {}, {}, {}
    try:
        for name, uid in AGENTS.items():
            parent, child = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            parent.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
            parent.settimeout(5)
            keyfd = memfd((vault / name).read_bytes())
            process = subprocess.Popen(
                [
                    "/usr/bin/python3",
                    "-B",
                    str(Path(__file__).with_name("agent.py")),
                    name,
                    str(keyfd),
                    str(child.fileno()),
                    str(path),
                ],
                pass_fds=[keyfd, child.fileno()],
                close_fds=True,
                user=uid,
                group=uid,
                extra_groups=[],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={"PATH": "/usr/bin:/bin", "LANG": "C"},
            )
            child.close()
            os.close(keyfd)
            pidfd = os.pidfd_open(process.pid)
            children[name] = (process, pidfd)
            channels[name] = parent
            for _ in range(200):
                state = life.state(process.pid)
                if state["generation"] == 1:
                    break
                time.sleep(0.002)
            if state["generation"] != 1 or select.select([pidfd], [], [], 0)[0]:
                raise ValueError("process instance unavailable")
            states[name] = state
            oracle[name] = {"spawn_pid": process.pid, "uid": uid, "proc_before": proc(process.pid)}
            challenge = {
                "domain": "A4-CHALLENGE-v1",
                "nonce": secrets.token_hex(32),
                "run_id": registry["run_id"],
                "boot_hash": boot(),
                "pid_namespace": registry["pid_namespace"],
                "instance": state,
                "agents": registry["agents"],
            }
            parent.send(canonical(challenge))
            proof, cred = receive(parent)
            if (
                not verify(registry["agents"][name]["public_key"], proof)
                or proof["body"]
                != {"domain": "A4-POP-v1", "identity": name, "challenge": challenge}
                or cred != {"pid": process.pid, "uid": uid, "gid": uid}
            ):
                raise ValueError("credential binding failed")
            bindings[name] = {
                "proof": proof,
                "credentials": cred,
                "kernel_instance": life.state(process.pid),
                "bound_ns": time.monotonic_ns(),
            }
        target = os.stat(path, follow_symlinks=False)
        file = {
            "dev": (os.major(target.st_dev) << 20) | os.minor(target.st_dev),
            "inode": target.st_ino,
        }
        issued = time.monotonic_ns()
        job = {"operation": "write16", "file": file}
        body = {
            "domain": "A4-DELEGATION-v1",
            "delegation_id": secrets.token_hex(32),
            "nonce": secrets.token_hex(32),
            "run_id": registry["run_id"],
            "boot_hash": boot(),
            "pid_namespace": registry["pid_namespace"],
            "sender": "TestA",
            "receiver": "TestB",
            "sender_instance": states["TestA"],
            "receiver_instance": states["TestB"],
            "job": job,
            "job_digest": digest(job),
            "issued_ns": issued,
            "expires_ns": issued + 5_000_000_000,
        }
        channels["TestA"].send(canonical(body))
        delegation, sender = receive(channels["TestA"])
        received = time.monotonic_ns()
        if delegation["body"] != body or not verify(
            registry["agents"]["TestA"]["public_key"], delegation
        ):
            raise ValueError("sender delegation invalid")
        forwarded = time.monotonic_ns()
        channels["TestB"].send(canonical({"delegation": delegation}))
        acceptance, receiver = receive(channels["TestB"])
        accepted = time.monotonic_ns()
        if not verify(registry["agents"]["TestB"]["public_key"], acceptance):
            raise ValueError("acceptance invalid")
        receipt_body = {
            "domain": "A4-TRANSPORT-WITNESS-v1",
            "run_id": registry["run_id"],
            "bindings": bindings,
            "delegation": delegation,
            "acceptance": acceptance,
            "sender_credentials": sender,
            "receiver_credentials": receiver,
            "received_ns": received,
            "forwarded_ns": forwarded,
            "accepted_ns": accepted,
            "release_ns": time.monotonic_ns(),
        }
        receipt = envelope(key(vault, "registrar"), receipt_body)
        for name in AGENTS:
            oracle[name]["proc_after_acceptance"] = proc(children[name][0].pid)
            oracle[name]["kernel_after_acceptance"] = life.state(children[name][0].pid)
        channels["TestB"].send(canonical({"go": digest(acceptance)}))
        channels["TestA"].send(canonical({"accepted": digest(delegation)}))
        for name, (process, pidfd) in children.items():
            stdout, stderr = process.communicate(timeout=6)
            oracle[name].update(
                exit_code=process.returncode,
                stderr_bytes=len(stderr),
                result=json.loads(stdout),
                pidfd_exited=bool(select.select([pidfd], [], [], 0)[0]),
            )
        time.sleep(0.1)
        lifecycle = life.finish()
        life = None
        end_cpu = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "receipt": receipt,
            "oracle": oracle,
            "lifecycle": lifecycle,
            "cpu_user_seconds": end_cpu.ru_utime - start_cpu.ru_utime,
            "cpu_system_seconds": end_cpu.ru_stime - start_cpu.ru_stime,
            "rss_peak_bytes": end_cpu.ru_maxrss * 1024,
            "resource_scope": "registrar including BCC compile; excludes children/kernel/VM",
        }
    finally:
        for channel in channels.values():
            channel.close()
        for process, pidfd in children.values():
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            os.close(pidfd)
        if life is not None:
            life.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "trial"])
    parser.add_argument("vault", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--path", type=Path)
    args = parser.parse_args()
    if os.geteuid() != 0 or not str(args.vault).startswith("/var/tmp/a4-private-"):
        raise ValueError("isolated guest root required")
    result = (
        initialize(args.vault, args.run_id)
        if args.command == "init"
        else trial(args.vault, args.certificate, args.path)
    )
    print(json.dumps(result))
