"""Root starter/authenticator restricted to the dedicated research VM and test workers."""

import argparse
import ctypes
import fcntl
import hashlib
import json
import os
import select
import secrets
import resource
import socket
import stat
import struct
import subprocess
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from lifecycle import Lifecycle
from protocol import canonical, envelope, public, verify

AGENTS = {"TestAlpha": 61001, "TestBeta": 61002}


def boot():
    return hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes()).hexdigest()


def private(vault, name):
    return Ed25519PrivateKey.from_private_bytes((vault / name).read_bytes())


def init(vault, run_id):
    if os.geteuid() != 0 or not str(vault).startswith("/var/tmp/a2-private-"):
        raise ValueError("guest root/private research vault required")
    vault.mkdir(mode=0o700)
    registry = {}
    for name in ["starter", *AGENTS]:
        key = Ed25519PrivateKey.generate()
        data = key.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
        fd = os.open(vault / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(fd, data)
        os.close(fd)
        if name in AGENTS:
            registry[name] = {
                "uid": AGENTS[name],
                "public_key": public(key),
                "scope": "controlled_test_identity_only",
            }
    return {
        "domain": "A2-ENROLLMENT-v1",
        "run_id": run_id,
        "boot_hash": boot(),
        "pid_namespace": os.readlink("/proc/self/ns/pid"),
        "starter_public_key": public(private(vault, "starter")),
        "agents": registry,
        "agent_entry_sha256": hashlib.sha256(
            Path(__file__).with_name("agent.py").read_bytes()
        ).hexdigest(),
        "codex_authenticated": False,
        "grok_authenticated": False,
    }


def memfd(data):
    fd = os.memfd_create("a2-controlled-key", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
    os.fchmod(fd, 0o600)
    os.write(fd, data)
    os.lseek(fd, 0, os.SEEK_SET)
    seals = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL
    fcntl.fcntl(fd, fcntl.F_ADD_SEALS, seals)
    return fd


class Starter:
    def __init__(self, vault, certificate, path):
        if os.geteuid() != 0 or not path.startswith("/var/tmp/a1-research-a2-"):
            raise ValueError("isolated guest/artificial scope only")
        item = certificate.stat()
        if item.st_uid != 0 or stat.S_IMODE(item.st_mode) & 0o022:
            raise ValueError("root-controlled certificate required")
        bundle = json.loads(certificate.read_text())
        if not verify(bundle["ca_public_key"], bundle["enrollment"]):
            raise ValueError("untrusted enrollment signature")
        self.enrollment = bundle["enrollment"]["body"]
        if self.enrollment["boot_hash"] != boot() or self.enrollment[
            "pid_namespace"
        ] != os.readlink("/proc/self/ns/pid"):
            raise ValueError("old boot/namespace")
        if (
            self.enrollment["agent_entry_sha256"]
            != hashlib.sha256(Path(__file__).with_name("agent.py").read_bytes()).hexdigest()
        ):
            raise ValueError("entry source changed")
        self.vault = vault
        self.cpu_start = resource.getrusage(resource.RUSAGE_SELF)
        self.path = path
        self.signer = private(vault, "starter")
        self.life = Lifecycle()
        self.ledger = {}
        self.handshakes = []
        self.oracle = []
        self.children = []
        self.sockpath = str(Path(path).parent / (secrets.token_hex(8) + ".sock"))
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        self.server.bind(self.sockpath)
        os.chmod(self.sockpath, 0o666)
        self.server.listen(4)
        self.server.settimeout(6)

    def launch(self, identity, mode="write", claim=None, register=True, replay=None, steal=None):
        uid = self.enrollment["agents"][identity]["uid"]
        keyfd = memfd((self.vault / identity).read_bytes())
        args = [
            "/usr/bin/python3",
            "-B",
            str(Path(__file__).with_name("agent.py")),
            self.path,
            self.sockpath,
            str(keyfd),
            mode,
            claim or identity,
        ]
        fds = [keyfd]
        if replay is not None:
            replayfd = memfd(canonical(replay))
            fds.append(replayfd)
            args += ["--replayfd", str(replayfd)]
        if steal is not None:
            args += ["--steal-pid", str(steal[0]), "--steal-fd", str(steal[1])]

        def unprivileged():
            os.setgroups([])
            os.setgid(uid)
            os.setuid(uid)
            if ctypes.CDLL(None).prctl(38, 1, 0, 0, 0) != 0:
                raise RuntimeError("no-new-privs")

        child = subprocess.Popen(
            args,
            pass_fds=fds,
            close_fds=True,
            preexec_fn=unprivileged,
            env={"PATH": "/usr/bin:/bin", "LANG": "C"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        pidfd = os.pidfd_open(child.pid)
        for fd in fds:
            os.close(fd)
        state = self.life.state(child.pid)
        if not state["start_ns"]:
            raise RuntimeError("missing kernel start")
        if register:
            self.ledger[child.pid] = {
                "identity": identity,
                "instance": dict(state),
                "uid": uid,
                "pidfd": pidfd,
                "launch_ns": time.monotonic_ns(),
            }
        self.children.append((child, pidfd))
        self.oracle.append(
            {
                "spawn_pid": child.pid,
                "identity_provisioned": identity,
                "uid": uid,
                "mode": mode,
                "registered": register,
                "kernel_start_at_spawn": state,
                "key_material_archived": False,
            }
        )
        return child, keyfd

    def handshake(self):
        conn, _ = self.server.accept()
        conn.settimeout(5)
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_PASSCRED, 1)
        peer_pid, peer_uid, peer_gid = struct.unpack(
            "3i", conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
        )
        registration = self.ledger.get(peer_pid)
        challenge = {
            "domain": "A2-CHALLENGE-v1",
            "nonce": secrets.token_hex(32),
            "run_id": self.enrollment["run_id"],
            "boot_hash": boot(),
            "pid_namespace": self.enrollment["pid_namespace"],
            "instance": registration["instance"] if registration else self.life.state(peer_pid),
            "issued_ns": time.monotonic_ns(),
            "expires_in_ns": 5_000_000_000,
        }
        target = os.stat(self.path, follow_symlinks=False)
        challenge["file"] = {
            "dev": (os.major(target.st_dev) << 20) | os.minor(target.st_dev),
            "inode": target.st_ino,
        }
        conn.send(canonical(challenge))
        payload, anc, flags, _ = conn.recvmsg(8192, socket.CMSG_SPACE(12))
        credentials = [
            struct.unpack("3i", data[:12])
            for level, kind, data in anc
            if level == socket.SOL_SOCKET and kind == socket.SCM_CREDENTIALS
        ]
        if flags & (socket.MSG_TRUNC | socket.MSG_CTRUNC) or len(credentials) != 1:
            raise ValueError("credential record incomplete")
        pid, uid, gid = credentials[0]
        state = self.life.state(pid)
        proof = json.loads(payload)
        crypt_id = next(
            (
                name
                for name, principal in self.enrollment["agents"].items()
                if verify(principal["public_key"], proof)
            ),
            None,
        )
        fresh = proof.get("body", {}).get("challenge") == challenge
        domain = proof.get("body", {}).get("domain") == "A2-TEST-POP-v1"
        live = False
        if registration:
            poll = select.poll()
            poll.register(registration["pidfd"], select.POLLIN)
            live = not poll.poll(0)
        binding = bool(
            registration
            and crypt_id == registration["identity"]
            and live
            and fresh
            and domain
            and pid == peer_pid == registration["instance"]["pid"]
            and uid == peer_uid == registration["uid"]
            and state["start_ns"] == registration["instance"]["start_ns"]
            and state["generation"] == 1
            and state["generation"] == registration["instance"]["generation"]
            and state["exit_ns"] == 0
            and time.monotonic_ns() - challenge["issued_ns"] <= challenge["expires_in_ns"]
        )
        body = {
            "domain": "A2-START-BINDING-v1",
            "run_id": self.enrollment["run_id"],
            "boot_hash": boot(),
            "pid_namespace": self.enrollment["pid_namespace"],
            "connection_peer": {"pid": peer_pid, "uid": peer_uid, "gid": peer_gid},
            "message_sender": {**state, "uid": uid, "gid": gid},
            "challenge": challenge,
            "proof_sha256": hashlib.sha256(canonical(proof)).hexdigest(),
            "credential_identity": crypt_id,
            "claimed_identity": proof.get("body", {}).get("claimed_identity"),
            "authenticated_identity": crypt_id if binding else None,
            "instance_bound": binding,
            "fresh_challenge": fresh,
            "registered_identity": registration["identity"] if registration else None,
            "attested_ns": time.monotonic_ns(),
            "test_identity_only": True,
        }
        signed = envelope(self.signer, body)
        self.handshakes.append({"proof": proof, "receipt": signed})
        conn.send(b"GO")
        return conn

    def finish_child(self, child):
        stdout, stderr = child.communicate(timeout=5)
        self.life.poll()
        for row in self.oracle:
            if row["spawn_pid"] == child.pid:
                row.update(
                    exit=child.returncode,
                    stdout_records=[json.loads(line) for line in stdout.splitlines()],
                    stderr_bytes=len(stderr),
                    stderr_sha256=hashlib.sha256(stderr).hexdigest(),
                )
        return stdout

    def run(self, case):
        extra = {}
        if case in ["alpha", "beta", "false-claim", "child", "exec"]:
            identity = "TestBeta" if case == "beta" else "TestAlpha"
            mode = case if case in ["child", "exec"] else "write"
            child, _ = self.launch(identity, mode, "TestBeta" if case == "false-claim" else None)
            conn = self.handshake()
            self.finish_child(child)
            conn.close()
        elif case in ["reuse", "replay", "takeover"]:
            child, keyfd = self.launch("TestAlpha", "hold" if case == "takeover" else "no-write")
            conn = self.handshake()
            replay = self.handshakes[-1]["proof"]
            if case != "takeover":
                self.finish_child(child)
                conn.close()
            if case == "reuse":
                time.sleep(0.05)
                Path("/proc/sys/kernel/ns_last_pid").write_text(str(child.pid - 1))
                replacement, _ = self.launch("TestAlpha", register=False)
                extra["pid_reuse_actual"] = replacement.pid == child.pid
            elif case == "replay":
                replacement, _ = self.launch("TestBeta", claim="TestAlpha", replay=replay)
            else:
                replacement, _ = self.launch(
                    "TestBeta", claim="TestAlpha", steal=(child.pid, keyfd)
                )
            next_conn = self.handshake()
            self.finish_child(replacement)
            next_conn.close()
            if case == "takeover":
                conn.send(b"RELEASE")
                self.finish_child(child)
                conn.close()
        else:
            raise ValueError("case")
        lifecycle = self.life.finish()
        self.server.close()
        os.unlink(self.sockpath)
        for _, fd in self.children:
            os.close(fd)
        usage = resource.getrusage(resource.RUSAGE_SELF)
        return {
            "case": case,
            "handshakes": self.handshakes,
            "oracle": self.oracle,
            "lifecycle": lifecycle,
            "extra": extra,
            "resources": {
                "cpu_user_seconds": usage.ru_utime - self.cpu_start.ru_utime,
                "cpu_system_seconds": usage.ru_stime - self.cpu_start.ru_stime,
                "peak_rss_bytes": usage.ru_maxrss * 1024,
                "scope": "starter process including lifecycle compile; child/kernel CPU unknown",
            },
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["init", "case"])
    parser.add_argument("vault", type=Path)
    parser.add_argument("value")
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--path")
    args = parser.parse_args()
    data = (
        init(args.vault, args.value)
        if args.mode == "init"
        else Starter(args.vault, args.certificate, args.path).run(args.value)
    )
    print(json.dumps(data, sort_keys=True), flush=True)
