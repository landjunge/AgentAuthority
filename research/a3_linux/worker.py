"""Artificial Linux execution adapter, explicitly NOT an authenticated provider agent."""

import argparse
import ctypes
import hashlib
import json
import os
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
from agent import write
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from protocol import canonical, envelope, verify


def main(args):
    if not args.path.startswith("/var/tmp/a1-research-a2-a3-"):
        raise ValueError("artificial A3 scope only")
    if args.mode == "write-only":
        print(json.dumps({"action": write(args.path), "adapter_only": True}), flush=True)
        return
    libc = ctypes.CDLL(None)
    if libc.prctl(4, 0, 0, 0, 0) != 0 or libc.prctl(38, 1, 0, 0, 0) != 0:
        raise RuntimeError("dump/no-new-privs gate")
    key = Ed25519PrivateKey.from_private_bytes(os.pread(args.keyfd, 32, 0))
    packet = json.loads(os.pread(args.packetfd, 65536, 0))
    if not all(verify(packet["ca_public_key"], job) for job in packet["jobs"]):
        raise ValueError("host dispatch signature")
    for index, job in enumerate(packet["jobs"]):
        conn = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        conn.settimeout(8)
        conn.connect(args.socket)
        challenge = json.loads(conn.recv(8192))
        if args.mode in ["child", "key-share"]:
            child = os.fork()
            if child:
                conn.close()
                _, status = os.waitpid(child, 0)
                raise SystemExit(os.waitstatus_to_exitcode(status))
        details = {
            "host_dispatch_sha256": hashlib.sha256(canonical(job)).hexdigest(),
            "job_nonce": job["body"]["job"]["nonce"],
            "job_index": index,
            "wrapper_not_provider_identity": True,
        }
        if args.steal_pid is not None:
            try:
                fd = os.open(f"/proc/{args.steal_pid}/fd/{args.steal_fd}", os.O_RDONLY)
                os.close(fd)
                details["foreign_key_open_errno"] = 0
            except OSError as error:
                details["foreign_key_open_errno"] = error.errno
        body = {
            "domain": "A2-TEST-POP-v1",
            "challenge": challenge,
            "claimed_identity": args.claim,
            "details": details,
        }
        conn.send(canonical(envelope(key, body)))
        if conn.recv(128) != b"GO":
            raise ValueError("broker control")
        if args.mode == "hold":
            if conn.recv(128) != b"RELEASE":
                raise ValueError("holder release")
        elif args.mode == "exec":
            os.execv(
                "/usr/bin/python3",
                [
                    "python3",
                    "-B",
                    __file__,
                    args.path,
                    args.socket,
                    str(args.keyfd),
                    str(args.packetfd),
                    "write-only",
                    args.claim,
                ],
            )
        else:
            print(
                json.dumps(
                    {
                        "action": write(args.path),
                        "dispatch_sha256": details["host_dispatch_sha256"],
                        "adapter_only": True,
                    }
                ),
                flush=True,
            )
        conn.close()
    time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("socket")
    parser.add_argument("keyfd", type=int)
    parser.add_argument("packetfd", type=int)
    parser.add_argument("mode")
    parser.add_argument("claim")
    parser.add_argument("--steal-pid", type=int)
    parser.add_argument("--steal-fd", type=int)
    main(parser.parse_args())
