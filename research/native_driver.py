"""One local test driver for the available native Codex agent runtime.

Driver actions are explicitly authorised experiments, not Authority powers.
No model dialogue is received or stored. Callback meaning is frozen separately.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time

import observer_research as p


class Session:
    def __init__(self, output: Path):
        output.mkdir(parents=True, exist_ok=False)
        self.output = output
        self.temp = tempfile.TemporaryDirectory(prefix="aa-native-run-")
        self.root = Path(self.temp.name)
        self.recorder = p.Recorder()
        self.states = {}
        task = Path(__file__).parent / "agent_task.py"
        for run, mode in enumerate(p.PANEL, 1):
            work = self.root / str(run)
            work.mkdir()
            shutil.copyfile(task, work / "task.py")
            sensor = p.TargetSensor(work / "target", run, self.recorder)
            stop = threading.Event()
            watcher = threading.Thread(target=sensor.watch, args=(stop,), daemon=True)
            sensor.sample()
            watcher.start()
            self.states[run] = {"work": work, "receipt": self.root / f"receipt-{run}.jsonl",
                                "mode": mode, "sensor": sensor, "stop": stop,
                                "watcher": watcher, "end": None, "calls": 0,
                                "started": False, "timeout": False,
                                "failure": None, "stats": Counter()}

    def call(self, run: int) -> int:
        state = self.states[run]
        if state["end"] is not None:
            raise ValueError("closed_measurement_window")
        env = os.environ.copy()
        env["AA_RESEARCH_RECEIPT"] = str(state["receipt"])
        mode = "late_native" if state["mode"] == "late" else state["mode"]
        state["calls"] += 1
        try:
            result = subprocess.run([sys.executable, "task.py", mode], cwd=state["work"], env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        except subprocess.TimeoutExpired:
            state["started"] = True
            state["timeout"] = True
            state["failure"] = "tool_timeout"
            raise
        except OSError:
            state["failure"] = "tool_process_unavailable"
            raise
        state["started"] = True
        state["stats"]["tool_reports"] += 1
        state["stats"]["raw_stdout_bytes"] += len(result.stdout)
        state["stats"]["raw_stderr_bytes"] += len(result.stderr)
        state["stats"]["canary_lines_raw"] += sum(
            p.CANARY.encode() in line for line in result.stdout.splitlines() + result.stderr.splitlines())
        self.recorder.add(run, "tool_end", result.returncode == 0)
        return result.returncode

    def close(self, run: int) -> None:
        state = self.states[run]
        if state["end"] is not None:
            raise ValueError("duplicate_native_callback")
        state["end"] = time.monotonic_ns()
        self.recorder.add(run, "native_end", True, state["end"])
        state["sensor"].sample()
        state["work"].joinpath("native.closed").touch()

    def finish(self) -> None:
        time.sleep(0.5)
        captures, references = [], []
        for run, state in self.states.items():
            state["stop"].set()
            state["watcher"].join()
            state["sensor"].sample(final=True)
            reference = p.reference_at_cutoff(state["work"], state["receipt"],
                                             state["sensor"].last_interval, state["end"])
            reference["run"] = run
            reference["appearance_vs_native_end"] = reference.pop("appearance_vs_cli_end")
            references.append(reference)
            captures.append({"run": run, "scenario": state["mode"],
                             "started": state["started"], "tool_attempts": state["calls"],
                             "real_agent_observed": state["end"] is not None,
                             "timeout": state["timeout"], "failure": state["failure"],
                             "backend": "native_collaboration",
                             "completion_received": state["end"] is not None,
                             "sensor_errors": state["sensor"].errors,
                             "stats": dict(state["stats"])})
        self.output.joinpath("observations.jsonl").write_text(
            "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in self.recorder.events))
        p.write_json(self.output / "capture.json", captures)
        p.write_json(self.output / "reference.json", references)
        self.temp.cleanup()


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        try:
            request = json.loads(self.rfile.readline())
            op = request.get("op")
            session = self.server.session
            if op == "finish":
                session.finish()
                reply = {"exit": 0}
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                run = request.get("run")
                if type(run) is not int or run not in session.states:
                    raise ValueError("invalid_test_run")
                if op == "call":
                    reply = {"exit": session.call(run)}
                elif op == "close":
                    session.close(run)
                    reply = {"exit": 0}
                else:
                    raise ValueError("invalid_driver_operation")
        except (OSError, ValueError, subprocess.SubprocessError):
            reply = {"exit": 2}
        self.wfile.write(json.dumps(reply).encode() + b"\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("serve", "call", "close", "finish"))
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--run", type=int)
    args = parser.parse_args()
    endpoint = args.session / "driver.sock"
    if args.operation == "serve":
        session = Session(args.session)
        with socketserver.UnixStreamServer(str(endpoint), Handler) as server:
            server.session = session
            os.chmod(endpoint, 0o600)
            print("native research driver ready", flush=True)
            server.serve_forever(poll_interval=0.05)
        endpoint.unlink(missing_ok=True)
        return 0
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.connect(str(endpoint))
        client.sendall(json.dumps({"op": args.operation, "run": args.run}).encode() + b"\n")
        reply = json.loads(client.makefile("rb").readline())
        print(f"local fixture returned exit={reply['exit']}")
        return reply["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
