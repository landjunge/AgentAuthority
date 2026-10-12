"""Controlled local test agent. No provider/model/person identity is asserted."""

import argparse
import ctypes
import json
import os
import socket
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from protocol import canonical, envelope


def write(path):
    fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
    st = os.fstat(fd)
    begin = time.monotonic_ns()
    count = os.write(fd, b"0123456789ABCDEF")
    end = time.monotonic_ns()
    os.close(fd)
    return {
        "result": count,
        "begin_ns": begin,
        "end_ns": end,
        "file": {"dev": (os.major(st.st_dev) << 20) | os.minor(st.st_dev), "inode": st.st_ino},
    }


def main(args):
    if not args.path.startswith("/var/tmp/a1-research-a2-"):
        raise ValueError("artificial files only")
    if args.mode == "write-only":
        print(json.dumps({"action": write(args.path)}), flush=True)
        return
    libc = ctypes.CDLL(None)
    if libc.prctl(4, 0, 0, 0, 0) != 0 or libc.prctl(38, 1, 0, 0, 0) != 0:
        raise RuntimeError("dump/no-new-privs gate")
    os.lseek(args.keyfd, 0, os.SEEK_SET)
    key = Ed25519PrivateKey.from_private_bytes(os.read(args.keyfd, 32))
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
    conn.settimeout(8)
    conn.connect(args.socket)
    challenge = json.loads(conn.recv(8192))
    if args.mode == "child":
        child = os.fork()
        if child:
            conn.close()
            _, status = os.waitpid(child, 0)
            raise SystemExit(os.waitstatus_to_exitcode(status))
    details = {}
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
    proof = envelope(key, body)
    if args.replayfd is not None:
        os.lseek(args.replayfd, 0, os.SEEK_SET)
        proof = json.loads(os.read(args.replayfd, 8192))
    conn.send(canonical(proof))
    assert conn.recv(128) == b"GO"
    if args.mode == "hold":
        assert conn.recv(128) == b"RELEASE"
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
                "write-only",
                args.claim,
            ],
        )
    elif args.mode != "no-write":
        print(json.dumps({"action": write(args.path)}), flush=True)
    conn.close()
    os.close(args.keyfd)
    time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("socket")
    parser.add_argument("keyfd", type=int)
    parser.add_argument("mode")
    parser.add_argument("claim")
    parser.add_argument("--steal-pid", type=int)
    parser.add_argument("--steal-fd", type=int)
    parser.add_argument("--replayfd", type=int)
    main(parser.parse_args())
