"""A3 additive adapter using the unchanged A2 starter and kernel lifecycle source."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "a2_linux"))
import starter as a2
from protocol import canonical, verify

a2.AGENTS = {"WrapperCodex": 61011, "WrapperGrok": 61012}


class Adapter(a2.Starter):
    def __init__(self, vault, certificate, path, packet):
        super().__init__(vault, certificate, path)
        self.packet = packet
        expected = self.enrollment["a3_worker_sha256"]
        if (
            hashlib.sha256(Path(__file__).with_name("worker.py").read_bytes()).hexdigest()
            != expected
        ):
            raise ValueError("A3 worker pin changed")
        self.active_nonce = packet["active_nonce"]
        self.ca_public_key = packet["ca_public_key"]
        bundle = json.loads(certificate.read_text())
        if self.ca_public_key != bundle["ca_public_key"]:
            raise ValueError("dispatch CA differs from enrolled CA")
        for job in packet["jobs"]:
            if (
                not verify(self.ca_public_key, job)
                or job["body"]["domain"] != "A3-HOST-DISPATCH-v1"
            ):
                raise ValueError("dispatch signature/domain")

    def launch(self, identity, mode="write", claim=None, register=True, steal=None):
        uid = self.enrollment["agents"][identity]["uid"]
        keyfd = a2.memfd((self.vault / identity).read_bytes())
        packetfd = a2.memfd(canonical(self.packet))
        args = [
            "/usr/bin/python3",
            "-B",
            str(Path(__file__).with_name("worker.py")),
            self.path,
            self.sockpath,
            str(keyfd),
            str(packetfd),
            mode,
            claim or identity,
        ]
        if steal:
            args += ["--steal-pid", str(steal[0]), "--steal-fd", str(steal[1])]

        child = subprocess.Popen(
            args,
            pass_fds=[keyfd, packetfd],
            close_fds=True,
            user=uid,
            group=uid,
            extra_groups=[],
            env={"PATH": "/usr/bin:/bin", "LANG": "C"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        pidfd = os.pidfd_open(child.pid)
        os.close(keyfd)
        os.close(packetfd)
        state = self.life.state(child.pid)
        if not state["start_ns"]:
            raise RuntimeError("missing exact kernel start")
        if register:
            self.ledger[child.pid] = {
                "identity": identity,
                "instance": dict(state),
                "uid": uid,
                "pidfd": pidfd,
                "launch_ns": a2.time.monotonic_ns(),
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

    def execute(self, case, identity):
        if case == "takeover":
            holder, fd = self.launch("WrapperCodex", "hold")
            held = self.handshake()
            writer, _ = self.launch("WrapperGrok", claim="WrapperCodex", steal=(holder.pid, fd))
            conn = self.handshake()
            self.finish_child(writer)
            conn.close()
            held.send(b"RELEASE")
            self.finish_child(holder)
            held.close()
        else:
            mode = case if case in ["child", "exec", "key-share"] else "write"
            child, _ = self.launch(identity, mode)
            for _ in self.packet["jobs"]:
                conn = self.handshake()
                conn.close()
            self.finish_child(child)
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
            "active_nonce": self.active_nonce,
            "resources": {
                "cpu_user_seconds": usage.ru_utime - self.cpu_start.ru_utime,
                "cpu_system_seconds": usage.ru_stime - self.cpu_start.ru_stime,
                "peak_rss_bytes": usage.ru_maxrss * 1024,
                "scope": "root adapter including lifecycle compile; kernel/children unknown",
            },
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["init", "case"])
    parser.add_argument("vault", type=Path)
    parser.add_argument("value")
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--path")
    parser.add_argument("--identity")
    args = parser.parse_args()
    if args.mode == "init":
        data = a2.init(args.vault, args.value)
        data["a3_worker_sha256"] = hashlib.sha256(
            Path(__file__).with_name("worker.py").read_bytes()
        ).hexdigest()
        data["domain"] = "A3-WRAPPER-ENROLLMENT-v1"
        for principal in data["agents"].values():
            principal["scope"] = "local_execution_wrapper_only_not_real_agent_provider_or_model"
    else:
        packet = json.load(sys.stdin)
        data = Adapter(args.vault, args.certificate, args.path, packet).execute(
            args.value, args.identity
        )
    print(json.dumps(data, sort_keys=True), flush=True)
