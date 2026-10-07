"""Frozen ten-run experiment runner, not an extension of the observer."""
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
import tempfile
import threading
import time

import observer_research as observer
from research.native_driver import Session as OriginalSession

COHORT = ("write", "noop", "fail", "write_fail", "late") * 2
VIEWS = {"target_present": ("run", "kind", "value"),
         "appearance_vs_native_end": ("run", "kind", "value", "t_ns")}


class StressSession(OriginalSession):
    def __init__(self, output: Path):
        # Same capture state, with the separately frozen ten-run fixture roster.
        output.mkdir(parents=True, exist_ok=False)
        self.output = output
        self.temp = tempfile.TemporaryDirectory(prefix="aa-stress-10-")
        self.root = Path(self.temp.name)
        self.recorder = observer.Recorder()
        self.states = {}
        self.control = []
        self.condition = threading.Condition()
        self.entered = set()
        self.barrier_failed = set()
        for run, mode in enumerate(COHORT, 1):
            work = self.root / str(run)
            work.mkdir()
            shutil.copyfile(Path(__file__).parent / "agent_task.py", work / "task.py")
            sensor = observer.TargetSensor(work / "target", run, self.recorder)
            stop = threading.Event()
            watcher = threading.Thread(target=sensor.watch, args=(stop,), daemon=True)
            sensor.sample()
            watcher.start()
            self.states[run] = {"work": work, "receipt": self.root / f"receipt-{run}.jsonl",
                "mode": mode, "sensor": sensor, "stop": stop, "watcher": watcher,
                "end": None, "calls": 0, "started": False, "timeout": False,
                "failure": None, "stats": Counter()}

    def note(self, run: int, kind: str, value: bool):
        with self.condition:
            self.control.append({"run": run, "kind": kind, "value": value,
                                 "t_ns": time.monotonic_ns()})

    def call(self, run: int) -> int:
        group = set(range(1, 7)) if run <= 6 else set(range(7, 11))
        self.note(run, "queued", True)
        with self.condition:
            self.entered.add(run)
            self.condition.notify_all()
            ready = self.condition.wait_for(lambda: group <= self.entered, timeout=60)
            if not ready:
                self.barrier_failed.add(run)
                self.states[run]["failure"] = "stress_barrier_timeout"
                self.states[run]["timeout"] = True
                return 2
        self.note(run, "tool", True)
        try:
            return super().call(run)
        finally:
            self.note(run, "tool", False)

    def close(self, run: int):
        super().close(run)
        self.note(run, "agent", False)

    def finish(self):
        super().finish()
        observer.write_json(self.output / "control.json", self.control)


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            request = json.loads(self.rfile.readline())
            session = self.server.session
            operation = request.get("op")
            if operation == "status":
                with session.condition:
                    reply = {"exit": 0, "run": sorted(session.entered)}
            elif operation == "finish":
                session.finish()
                reply = {"exit": 0}
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                run = request.get("run")
                if type(run) is not int or run not in session.states:
                    raise ValueError("invalid_test_run")
                if operation == "dispatch":
                    session.note(run, "agent", True)
                    reply = {"exit": 0}
                elif operation == "call":
                    reply = {"exit": session.call(run)}
                elif operation == "close":
                    session.close(run)
                    reply = {"exit": 0}
                else:
                    raise ValueError("invalid_test_operation")
        except (OSError, ValueError, subprocess.SubprocessError):
            reply = {"exit": 2}
        self.wfile.write(json.dumps(reply).encode() + b"\n")


def overlap(control: list[dict], kind: str) -> int:
    active, maximum = set(), 0
    for row in sorted((r for r in control if r["kind"] == kind), key=lambda r: r["t_ns"]):
        if row["value"]:
            active.add(row["run"])
        else:
            active.discard(row["run"])
        maximum = max(maximum, len(active))
    return maximum


def analyse(directory: Path):
    # Frozen query roster, fixed views, unchanged infer; no truth or scenario input.
    events = observer.json_lines(directory / "observations.jsonl")
    observer.check_events(events)
    predictions = []
    for run in range(1, 11):
        for question, fields in VIEWS.items():
            view = [{k: e[k] for k in fields} for e in events]
            predictions.append({"run": run, "question": question, "fields": list(fields),
                                "prediction": observer.infer(view, run, question)})
    observer.write_json(directory / "predictions.json", predictions)
    references = {r["run"]: r for r in json.loads((directory / "reference.json").read_text())}
    captures = json.loads((directory / "capture.json").read_text())
    control = json.loads((directory / "control.json").read_text())
    rows = []
    for prediction in predictions:
        truth = references.get(prediction["run"], {}).get(prediction["question"])
        rows.append({**prediction, "reference": truth,
                     "verdict": observer.judge(prediction["prediction"]["answer"], truth)})
    counts = Counter(r["verdict"] for r in rows)
    source_errors = []
    measurement_errors = []
    for capture in captures:
        run = capture["run"]
        reference = references.get(run, {})
        statuses = [e["value"] for e in events if e["run"] == run and e["kind"] == "tool_end"]
        expected = COHORT[run - 1] not in {"fail", "write_fail"}
        if (not capture["completion_received"] or capture["tool_attempts"] != 1
                or reference.get("calls") != 1 or statuses != [expected]):
            source_errors.append(run)
        if (capture["sensor_errors"] or capture["timeout"] or capture["failure"]
                or reference.get("reference_issue")):
            measurement_errors.append(run)
    started = len({r["run"] for r in control if r["kind"] == "agent" and r["value"]})
    completed = sum(r["completion_received"] for r in captures)
    tool_peak = overlap(control, "tool")
    passed = (started == completed == 10 and tool_peak >= 2 and not source_errors
              and not measurement_errors and not any(counts[k] for k in
                      ("WRONG", "UNKNOWN", "UNJUDGEABLE")) and len(rows) == 20)
    result = {"started": started, "completed": completed,
              "agent_execution_errors": source_errors, "measurement_errors": measurement_errors,
              "verdicts": dict(counts), "peak_open_agent_requests": overlap(control, "agent"),
              "peak_tool_invocations": tool_peak,
              "level_10": "BESTANDEN" if passed else "NICHT BESTANDEN", "rows": rows}
    observer.write_json(directory / "evaluation.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("serve", "dispatch", "status", "analyse"))
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--run", type=int)
    args = parser.parse_args()
    if args.operation == "analyse":
        analyse(args.session)
        return
    endpoint = args.session / "driver.sock"
    if args.operation == "serve":
        session = StressSession(args.session)
        with socketserver.ThreadingUnixStreamServer(str(endpoint), Handler) as server:
            server.session = session
            os.chmod(endpoint, 0o600)
            print("stress-10 runner ready", flush=True)
            server.serve_forever(poll_interval=0.05)
        endpoint.unlink(missing_ok=True)
    else:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.connect(str(endpoint))
            client.sendall(json.dumps({"op": args.operation, "run": args.run}).encode() + b"\n")
            print(client.makefile("rb").readline().decode().strip())


if __name__ == "__main__":
    main()
