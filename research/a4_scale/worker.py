"""Controlled simulated principal, signed real messages and artificial writes."""

import ctypes
import hashlib
import json
import os
import resource
import socket
import sys
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from protocol import canonical, envelope, verify


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def run():
    name, keyfd, sockfd, path = sys.argv[1:]
    libc = ctypes.CDLL(None)
    if libc.prctl(4, 0, 0, 0, 0) or libc.prctl(38, 1, 0, 0, 0):
        raise RuntimeError("hardening")
    key = Ed25519PrivateKey.from_private_bytes(os.read(int(keyfd), 32))
    os.close(int(keyfd))
    channel = socket.socket(fileno=int(sockfd))
    channel.settimeout(90)
    context = json.loads(channel.recv(131072))
    challenge, registry = context["challenge"], context["registry"]
    channel.send(
        canonical(
            {
                "type": "proof",
                "value": envelope(
                    key, {"domain": "A4-SCALE-POP-v1", "identity": name, "challenge": challenge}
                ),
            }
        )
    )
    sent, accepted, inbound = {}, {}, None
    writes = 0
    while True:
        packet = json.loads(channel.recv(32768))
        if "stop" in packet:
            break
        if "issue" in packet or "foreign_claim" in packet:
            body = packet.get("issue", packet.get("foreign_claim"))
            if "issue" in packet:
                if body["sender"] != name or body["sender_instance"] != challenge["instance"]:
                    raise ValueError("sender instance")
                expected = (
                    None
                    if inbound is None
                    else {
                        "delegation_sha256": digest(inbound[0]),
                        "acceptance_sha256": digest(inbound[1]),
                    }
                )
                if body["parent_link"] != expected:
                    raise ValueError("multistage link")
            value = envelope(key, body)
            sent[body["delegation_id"]] = value
            channel.send(canonical({"type": "delegation", "value": value}))
        elif "replay" in packet:
            channel.send(canonical({"type": "delegation", "value": sent[packet["replay"]]}))
        elif "receive" in packet:
            delegation = packet["receive"]
            job = delegation["body"]
            now = time.monotonic_ns()
            if not (
                verify(registry["agents"][job["sender"]]["public_key"], delegation)
                and job["domain"] == "A4-SCALE-DELEGATION-v1"
                and job["receiver"] == name
                and job["receiver_instance"] == challenge["instance"]
                and job["run_id"] == registry["run_id"]
                and job["boot_hash"] == registry["boot_hash"]
                and job["pid_namespace"] == registry["pid_namespace"]
                and job["job_digest"] == digest(job["job"])
                and job["issued_ns"] <= now < job["expires_ns"]
            ):
                raise ValueError("recipient signature/scope")
            body = {
                "domain": "A4-SCALE-ACCEPT-v1",
                "identity": name,
                "instance": challenge["instance"],
                "delegation_id": job["delegation_id"],
                "delegation_sha256": digest(delegation),
                "nonce": os.urandom(32).hex(),
                "accepted_ns": now,
            }
            if job["job"]["operation"] == "refuse":
                body["domain"] = "A4-SCALE-REFUSE-v1"
                channel.send(canonical({"type": "refusal", "value": envelope(key, body)}))
            else:
                proof = envelope(key, body)
                accepted[job["delegation_id"]] = (delegation, proof)
                channel.send(canonical({"type": "acceptance", "value": proof}))
        elif "go" in packet:
            delegation, proof = accepted[packet["go"]]
            if packet["acceptance_sha256"] != digest(proof):
                raise ValueError("wrong release")
            job = delegation["body"]
            if job["job"]["operation"] != "write16":
                raise ValueError("negative job must not write")
            fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
            file = os.fstat(fd)
            obj = {
                "inode": file.st_ino,
                "dev": (os.major(file.st_dev) << 20) | os.minor(file.st_dev),
            }
            if obj != job["job"]["file"]:
                raise ValueError("wrong object")
            before = time.monotonic_ns()
            result = os.write(fd, b"A4-artificial-16")
            after = time.monotonic_ns()
            os.close(fd)
            writes += 1
            inbound = (delegation, proof)
            channel.send(
                canonical(
                    {
                        "type": "done",
                        "delegation_id": job["delegation_id"],
                        "before_ns": before,
                        "after_ns": after,
                        "result": result,
                        "pid": os.getpid(),
                        "file": obj,
                    }
                )
            )
        elif "rejected" not in packet:
            raise ValueError("unexpected control packet")
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(
        json.dumps(
            {
                "identity": name,
                "pid": os.getpid(),
                "writes": writes,
                "cpu_user_seconds": usage.ru_utime,
                "cpu_system_seconds": usage.ru_stime,
                "rss_peak_bytes": usage.ru_maxrss * 1024,
            }
        )
    )


if __name__ == "__main__":
    run()
