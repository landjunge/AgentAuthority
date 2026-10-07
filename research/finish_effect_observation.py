"""Opt-in passive source sensor for the existing local FakeAdapter write case.

No probe, decision, intervention or content persistence. Caller supplies trace
installation so a separate oracle can share callbacks without sharing data.
"""
from __future__ import annotations

import ast
from pathlib import Path
import threading
import time

from lab.fake_adapter import FakeAdapter
from lab.validator import Lab


class FinishEffectSensor:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self.errors = 0
        self._lock = threading.Lock()
        self._next_run = 0
        self._frames: dict = {}
        self._attempts: list[dict] = []
        self._returns: dict = {}
        self._write = FakeAdapter.write.__code__
        self._submit = Lab.submit.__code__
        self._finish = Lab.finish.__code__
        tree = ast.parse(Path(self._write.co_filename).read_text())
        node = next(n for n in ast.walk(tree)
                    if isinstance(n, ast.FunctionDef) and n.name == "write")
        assignment = next(n for n in ast.walk(node)
                          if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Subscript) and isinstance(t.value, ast.Attribute)
                                  and t.value.attr == "files" for t in n.targets))
        self._assignment_line = assignment.lineno
        self._effect_after_line = next(n.lineno for n in node.body
                                      if isinstance(n, ast.Return) and n.lineno > assignment.lineno)

    def _add(self, run: int, kind: str, value: bool, timestamp: int) -> None:
        self.events.append({"run": run, "kind": kind, "value": value, "t_ns": timestamp})

    def trace(self, frame, event: str, arg) -> None:
        # Never hold this observational lock across an original source operation.
        try:
            with self._lock:
                self._trace(frame, event, arg)
        except Exception:
            # A broken sensor never changes an original decision or effect.
            self.errors += 1

    def _trace(self, frame, event: str, arg) -> None:
        if frame in self._returns and event in {"line", "return", "exception"}:
            when = time.monotonic_ns()
            for runs in self._returns.pop(frame):
                for run in runs:
                    self._add(run, "finish_return", True, when)
        code = frame.f_code
        if code is self._write:
            local = frame.f_locals
            if event == "call":
                self._next_run += 1
                attempt = {"run": self._next_run, "lab": local["self"].lab,
                           "entry": None, "effect_pending": False}
                self._frames[frame] = attempt
                self._attempts.append(attempt)
                self._add(attempt["run"], "write_started", True, time.monotonic_ns())
            elif frame in self._frames:
                attempt = self._frames[frame]
                if event == "line" and frame.f_lineno == self._assignment_line:
                    # Lower bound before membership check and actual assignment.
                    when = time.monotonic_ns()
                    present = local["key"] in local["self"].repo.files
                    attempt["effect_pending"] = True
                    self._add(attempt["run"], "write_effect_before", present, when)
                elif (event == "line" and frame.f_lineno == self._effect_after_line
                      and attempt["effect_pending"]):
                    # Source control reached the line after the successful assignment.
                    present = local["key"] in local["self"].repo.files
                    self._add(attempt["run"], "write_effect", present, time.monotonic_ns())
                    attempt["effect_pending"] = False
                elif event == "return":
                    self._frames.pop(frame)
        elif code is self._submit and event == "return" and getattr(arg, "allow", None) is True:
            local = frame.f_locals
            caller = frame.f_back
            while caller is not None and caller not in self._frames:
                caller = caller.f_back
            if caller is not None:
                attempt = self._frames[caller]
                req = local.get("req")
                entry = local.get("entry")
                write_local = caller.f_locals
                if (entry is not None and local.get("self") is attempt["lab"]
                        and req.action == "file.write" and req.resource == write_local["key"]
                        and req.workflow_id == write_local["workflow_id"]):
                    attempt["entry"] = entry
        elif code is self._finish and event == "return" and arg is True:
            local = frame.f_locals
            entry, lab = local.get("entry"), local.get("self")
            runs = [a["run"] for a in self._attempts
                    if entry is not None and a["entry"] is entry and a["lab"] is lab]
            if runs and frame.f_back is not None:
                # This callback is before actual return, never its completion proof.
                when = time.monotonic_ns()
                for run in runs:
                    self._add(run, "finish_return_before", True, when)
                self._returns.setdefault(frame.f_back, []).append(runs)

    def close(self) -> None:
        self._frames.clear()
        self._attempts.clear()
        self._returns.clear()
