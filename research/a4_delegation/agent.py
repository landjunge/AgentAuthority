"""Exactly two controlled test principals; no external AI identity claims."""

import ctypes
import hashlib
import json
import os
import socket
import sys
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from protocol import canonical, envelope, verify


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def run():
    role, keyfd, sockfd, path = sys.argv[1:]
    libc = ctypes.CDLL(None)
    if libc.prctl(4, 0, 0, 0, 0) or libc.prctl(38, 1, 0, 0, 0):
        raise RuntimeError("process hardening failed")
    key = Ed25519PrivateKey.from_private_bytes(os.read(int(keyfd), 32))
    os.close(int(keyfd))
    channel = socket.socket(fileno=int(sockfd))
    channel.settimeout(5)
    context = json.loads(channel.recv(16384))
    proof = envelope(key, {"domain": "A4-POP-v1", "identity": role, "challenge": context})
    channel.send(canonical(proof))
    packet = json.loads(channel.recv(16384))
    if role == "TestA":
        delegation = envelope(key, packet)
        channel.send(canonical(delegation))
        acknowledgement = json.loads(channel.recv(16384))
        if acknowledgement != {"accepted": digest(delegation)}:
            raise ValueError("unexpected handover acknowledgement")
        print(json.dumps({"role": role, "delegation_sha256": digest(delegation), "writes": 0}))
    else:
        delegation = packet["delegation"]
        job = delegation["body"]
        if not verify(context["agents"]["TestA"]["public_key"], delegation):
            raise ValueError("invalid sender signature")
        now = time.monotonic_ns()
        if not (
            job["domain"] == "A4-DELEGATION-v1"
            and job["sender"] == "TestA"
            and job["receiver"] == role
            and job["receiver_instance"] == context["instance"]
            and job["run_id"] == context["run_id"]
            and job["boot_hash"] == context["boot_hash"]
            and job["pid_namespace"] == context["pid_namespace"]
            and job["issued_ns"] <= now < job["expires_ns"]
            and job["job_digest"] == digest(job["job"])
        ):
            raise ValueError("delegation scope mismatch")
        acceptance = envelope(
            key,
            {
                "domain": "A4-ACCEPT-v1",
                "delegation_sha256": digest(delegation),
                "delegation_id": job["delegation_id"],
                "identity": role,
                "instance": context["instance"],
                "nonce": os.urandom(32).hex(),
                "accepted_ns": now,
            },
        )
        channel.send(canonical(acceptance))
        go = json.loads(channel.recv(16384))
        if go != {"go": digest(acceptance)}:
            raise ValueError("unexpected execution release")
        fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
        before = time.monotonic_ns()
        result = os.write(fd, b"A4-artificial-16")
        after = time.monotonic_ns()
        os.close(fd)
        print(
            json.dumps(
                {
                    "role": role,
                    "pid": os.getpid(),
                    "result": result,
                    "before_ns": before,
                    "after_ns": after,
                }
            )
        )
    channel.close()


if __name__ == "__main__":
    run()
