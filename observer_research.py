"""Small research recorder/evaluator. No authorisation or enforcement imports."""
from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import threading
import time

FIELDS = ("run", "kind", "value", "t_ns", "event")
KINDS = {"tool_end", "cli_end", "native_end", "target_probe", "target_final"}
PANEL = ("write", "noop", "fail", "write_fail", "late", "write")
CANARY = "AA_INERT_CANARY_20261007"
QUESTIONS = ("target_present", "appearance_vs_cli_end")


def write_json(path: Path, value: object) -> None:
    # Deliberately propagate storage errors; silence is not successful minimisation.
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def json_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line]


class Recorder:
    def __init__(self) -> None:
        self.events: list[dict] = []
        self.lock = threading.Lock()

    def add(self, run: int, kind: str, value: bool, timestamp: int | None = None) -> None:
        assert kind in KINDS and type(value) is bool
        with self.lock:
            self.events.append({
                "run": run, "kind": kind, "value": value,
                "t_ns": time.monotonic_ns() if timestamp is None else timestamp,
                "event": len(self.events) + 1,
            })


def project_cli(raw: object, run: int, recorder: Recorder, stats: Counter) -> None:
    """Form new bounded values. Never forward raw ids, status text or payloads."""
    if not isinstance(raw, dict):
        stats["invalid_records"] += 1
        return
    if type(raw.get("type")) is not str:
        stats["invalid_records"] += 1
        return
    if raw.get("type") == "turn.completed":
        stats["completed_model_turns"] += 1
        return
    if raw.get("type") == "item.completed":
        item = raw.get("item")
        if not isinstance(item, dict):
            stats["invalid_records"] += 1
            return
        if item.get("type") == "command_execution":
            exit_code = item.get("exit_code")
            if type(exit_code) is int:
                recorder.add(run, "tool_end", exit_code == 0)
                stats["tool_reports"] += 1
            else:
                stats["invalid_tool_reports"] += 1
        else:
            stats["excluded_items"] += 1
    elif raw.get("type") in {"error", "turn.failed"}:
        stats["cli_error_records"] += 1
    else:
        stats["excluded_records"] += 1


def read_stdout(pipe, run: int, recorder: Recorder, stats: Counter) -> None:
    for line in pipe:
        stats["raw_stdout_bytes"] += len(line)
        stats["raw_lines"] += 1
        stats["canary_lines_raw"] += int(CANARY.encode() in line)
        try:
            raw = json.loads(line)
        except (ValueError, UnicodeError):
            stats["invalid_records"] += 1
            continue
        project_cli(raw, run, recorder, stats)


def read_stderr(pipe, stats: Counter) -> None:
    for line in pipe:
        stats["raw_stderr_bytes"] += len(line)
        stats["canary_lines_stderr"] += int(CANARY.encode() in line)


class TargetSensor:
    """Transition observations plus last absence, not a full poll history."""
    def __init__(self, target: Path, run: int, recorder: Recorder):
        self.target, self.run, self.recorder = target, run, recorder
        self.lock = threading.Lock()
        self.previous: bool | None = None
        self.last_absence: int | None = None
        self.errors = 0
        self.last_interval: tuple[int, int] | None = None

    def sample(self, final: bool = False) -> int:
        with self.lock:
            before = time.monotonic_ns()
            try:
                present = stat.S_ISREG(self.target.stat().st_mode)
            except FileNotFoundError:
                present = False
            except OSError:
                self.errors += 1
                self.last_interval = None
                return before
            after = time.monotonic_ns()
            self.last_interval = (before, after)
            # Presence supplies an upper bound; absence supplies a lower bound.
            timestamp = after if present else before
            if present != self.previous:
                if present and self.last_absence is not None:
                    self.recorder.add(self.run, "target_probe", False, self.last_absence)
                self.recorder.add(self.run, "target_probe", present, timestamp)
                self.previous = present
            if not present:
                self.last_absence = timestamp
            if final:
                self.recorder.add(self.run, "target_final", present, timestamp)
            return timestamp

    def watch(self, stop: threading.Event) -> None:
        while not stop.wait(0.01):
            self.sample()


def valid_interval(value: object) -> bool:
    return (isinstance(value, (tuple, list)) and len(value) == 2
            and all(type(t) is int and t >= 0 for t in value) and value[0] <= value[1])


def reference_at_cutoff(work: Path, receipt: Path, cutoff: tuple[int, int] | None,
                        end: int | None) -> dict:
    """Oracle uses instrumented syscall brackets and a separate target check.

    Later state alone never becomes truth for an earlier observation point.
    A reference interval straddling cutoff/end cannot answer that question.
    """
    result = {"run": 0, "calls": 0, "target_check": None,
              "target_present": None, "appearance_vs_cli_end": None,
              "creation_interval_ns": None,
              "cutoff_interval_ns": list(cutoff) if valid_interval(cutoff) else None,
              "end_ns": end if type(end) is int and end >= 0 else None,
              "reference_issue": "missing_cutoff_observation" if cutoff is None else None}
    if ((cutoff is not None and not valid_interval(cutoff))
            or (end is not None and (type(end) is not int or end < 0))):
        result["reference_issue"] = "invalid_reference_time"
        return result
    try:
        entries = json_lines(receipt) if receipt.exists() else []
    except (OSError, ValueError):
        result["reference_issue"] = "invalid_reference_receipt"
        return result
    receipt_shapes = ({"call"}, {"create_before_ns", "create_after_ns"}, {"creation_conflict"})
    if any(not isinstance(x, dict) or set(x) not in receipt_shapes for x in entries):
        result["reference_issue"] = "invalid_reference_receipt"
        return result
    creations = [x for x in entries if "create_before_ns" in x or "create_after_ns" in x]
    if (any("call" in x and x["call"] is not True for x in entries)
            or any(not valid_interval((x.get("create_before_ns"), x.get("create_after_ns")))
                   for x in creations)
            or any("creation_conflict" in x and x["creation_conflict"] is not True
                   for x in entries)):
        result["reference_issue"] = "invalid_reference_receipt"
        return result
    calls = sum(x.get("call") is True for x in entries)
    result["calls"] = calls
    try:
        final_state = stat.S_ISREG(work.joinpath("target").stat().st_mode)
    except FileNotFoundError:
        final_state = False
    except OSError:
        final_state = None
    result["target_check"] = final_state
    if final_state is None:
        result["reference_issue"] = "reference_target_check_failed"
        return result
    if calls != 1 or len(creations) > 1 or any(x.get("creation_conflict") for x in entries):
        result["reference_issue"] = "uncontrolled_or_missing_tool_execution"
        return result
    if not creations:
        if final_state:
            result["reference_issue"] = "unreceipted_target"
        else:
            if cutoff is not None:
                result["target_present"] = False
            result["appearance_vs_cli_end"] = "not_applicable"
        return result
    lo, hi = creations[0]["create_before_ns"], creations[0]["create_after_ns"]
    result["creation_interval_ns"] = [lo, hi]
    if not final_state:
        result["reference_issue"] = "receipt_target_disagreement"
        return result
    if cutoff is not None:
        if hi < cutoff[0]:
            result["target_present"] = True
        elif lo > cutoff[1]:
            result["target_present"] = False
    if end is not None:
        if hi < end:
            result["appearance_vs_cli_end"] = "before"
        elif lo > end:
            result["appearance_vs_cli_end"] = "after"
    return result


def capture(output: Path, codex: str, timeout: float) -> None:
    output.mkdir(parents=True, exist_ok=False)
    recorder = Recorder()
    records, references = [], []
    task = Path(__file__).parent / "research" / "agent_task.py"
    for run, mode in enumerate(PANEL, 1):
        stats = Counter()
        record = {"run": run, "scenario": mode, "started": False,
                  "real_agent_observed": False, "timeout": False,
                  "process_success": None, "sensor_errors": 0, "stats": {},
                  "failure": None}
        with tempfile.TemporaryDirectory(prefix="aa-real-run-") as directory:
            root = Path(directory)
            work = root / "work"
            work.mkdir()
            shutil.copyfile(task, work / "task.py")
            receipt = root / "receipt.jsonl"
            env = os.environ.copy()
            env["AA_RESEARCH_RECEIPT"] = str(receipt)
            sensor = TargetSensor(work / "target", run, recorder)
            stop = threading.Event()
            watcher = threading.Thread(target=sensor.watch, args=(stop,), daemon=True)
            sensor.sample()
            watcher.start()
            end = None
            try:
                process = subprocess.Popen(
                    [codex, "--ask-for-approval", "never", "exec", "--json",
                     "--ephemeral", "--ignore-user-config", "--skip-git-repo-check",
                     "-c", f'sqlite_home="{root / "cli-state"}"',
                     "-c", f'log_dir="{root / "cli-log"}"',
                     "--sandbox", "workspace-write", "--cd", str(work), "-"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    env=env,
                )
                record["started"] = True
                work.joinpath("cli.pid").write_text(str(process.pid))
                stdout_reader = threading.Thread(
                    target=read_stdout, args=(process.stdout, run, recorder, stats))
                stderr_stats = Counter()
                stderr_reader = threading.Thread(
                    target=read_stderr, args=(process.stderr, stderr_stats))
                stdout_reader.start()
                stderr_reader.start()
                prompt = (
                    f"This is a controlled local research task with inert data. "
                    f"Execute exactly once: python3 task.py {mode}. "
                    "Do not repair errors or alter task.py, cli.pid or target yourself. "
                    "Do not inspect other files or credentials, use network tools or subagents. "
                    "Finish with a brief report of the returned status. "
                    f"All api_key text is the inert marker {CANARY}.\n"
                )
                try:
                    process.stdin.write(prompt.encode())
                    process.stdin.close()
                except BrokenPipeError:
                    pass
                try:
                    code = process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    record["timeout"] = True
                    process.terminate()
                    try:
                        code = process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        code = process.wait()
                end = time.monotonic_ns()
                recorder.add(run, "cli_end", code == 0, end)
                sensor.sample()
                record["process_success"] = code == 0
                stdout_reader.join(timeout=5)
                stderr_reader.join(timeout=5)
                if stdout_reader.is_alive() or stderr_reader.is_alive():
                    record["failure"] = "stream_did_not_close"
                stats.update(stderr_stats)
                record["real_agent_observed"] = bool(
                    stats["tool_reports"] or stats["completed_model_turns"])
            except OSError:
                record["failure"] = "agent_process_unavailable"
            # Bounded observation window, not a promise of no later effects.
            time.sleep(0.5)
            stop.set()
            watcher.join()
            cutoff = sensor.sample(final=True)
            record["sensor_errors"] = sensor.errors
            record["stats"] = dict(stats)
            reference = reference_at_cutoff(work, receipt, sensor.last_interval, end)
            reference["run"] = run
            references.append(reference)
        records.append(record)
        print(f"run {run}: started={record['started']} "
              f"agent_observed={record['real_agent_observed']} "
              f"tool_reports={stats['tool_reports']}", flush=True)
    observations = "".join(json.dumps(e, separators=(",", ":")) + "\n"
                           for e in recorder.events)
    output.joinpath("observations.jsonl").write_text(observations)
    write_json(output / "capture.json", records)
    write_json(output / "reference.json", references)
    print(f"observations={len(recorder.events)}, bytes={len(observations.encode())}")


def check_events(events: list[dict]) -> None:
    for event in events:
        if (set(event) != set(FIELDS) or event.get("kind") not in KINDS
                or type(event.get("value")) is not bool
                or any(type(event.get(field)) is not int or event[field] < 0
                       for field in ("run", "event", "t_ns"))):
            raise ValueError("invalid_observation_schema")


def deduplicate(events: list[dict]) -> tuple[list[dict], bool]:
    seen = {}
    result = []
    for event in events:
        if "event" not in event:
            result.append(event)
            continue
        key = event["event"]
        if key in seen:
            if event != seen[key]:
                return [], True
        else:
            seen[key] = event
            result.append(event)
    return result, False


def infer(events: list[dict], run: int, question: str) -> dict:
    """Only the supplied view and query. No oracle, scenario or capture metadata."""
    rows, conflict = deduplicate(events)
    if conflict:
        return {"answer": None, "reason": "contradictory_reference", "evidence": []}
    rows = [e for e in rows if e.get("run") == run]
    evidence = [e["event"] for e in rows if "event" in e]
    unknown = {"answer": None, "reason": "insufficient_observed_data", "evidence": evidence}
    if question == "target_present":
        final = [e for e in rows if e.get("kind") == "target_final"
                 and type(e.get("value")) is bool]
        values = {e["value"] for e in final}
        if len(values) == 1:
            return {"answer": final[0]["value"], "reason": "explicit_local_snapshot",
                    "evidence": evidence}
        return unknown
    if question not in {"appearance_vs_cli_end", "appearance_vs_native_end"}:
        raise ValueError("unknown_research_question")
    end_kind = "cli_end" if question == "appearance_vs_cli_end" else "native_end"
    ends = [e["t_ns"] for e in rows if e.get("kind") == end_kind
            and type(e.get("t_ns")) is int]
    samples = sorted((e for e in rows if e.get("kind") == "target_probe"
                      and type(e.get("value")) is bool and type(e.get("t_ns")) is int),
                     key=lambda e: e["t_ns"])
    if len(ends) != 1 or not samples:
        return unknown
    first_presence = next((e for e in samples if e["value"]), None)
    if first_presence is None:
        return unknown
    end = ends[0]
    if first_presence["t_ns"] < end:
        return {"answer": "before", "reason": "presence_upper_bound_before_end",
                "evidence": evidence}
    absences = [e["t_ns"] for e in samples
                if not e["value"] and e["t_ns"] < first_presence["t_ns"]]
    if absences and max(absences) > end:
        return {"answer": "after", "reason": "absence_lower_bound_after_end",
                "evidence": evidence}
    return unknown


def infer_finish_effect(events: list[dict], run: int, question: str) -> dict:
    """Bound A/B/C to one source-observed write, without status or oracle input.

    The source sensor supplies the run binding; equal tokens here do not prove
    source authenticity. Missing timing can preserve B, but never supplies an
    ordering for A/C. C says nothing about unobserved workflow effects.
    """
    if question not in ("A", "B", "C"):
        raise ValueError("unknown_finish_effect_question")
    kinds = ("write_started", "finish_return_before", "finish_return",
             "write_effect_before", "write_effect")
    write_kinds = ("write_started", "write_effect_before", "write_effect")
    required = write_kinds if question == "B" else kinds
    fields = {"run", "kind", "value", "t_ns"}
    evidence: list[str] = []

    def result(answer: str, reason: str) -> dict:
        return {"answer": answer, "reason": reason, "evidence": evidence}

    if type(run) is not int or run <= 0:
        return result("UNBEKANNT", "invalid_query_run")
    if not isinstance(events, list):
        return result("UNBEKANNT", "malformed_observation")

    rows: dict[str, list[dict]] = {kind: [] for kind in required}
    observed = set()
    issues = set()
    for row in events:
        if not isinstance(row, dict):
            issues.add("malformed_observation")
            continue
        kind = row.get("kind")
        if type(kind) is not str or kind not in kinds:
            # G3 ALLOW and historical completion/status kinds are not effects.
            if set(row) <= fields and ("kind" not in row or type(kind) is not str):
                bound_run = row.get("run")
                if type(bound_run) is not int or bound_run <= 0 or bound_run == run:
                    issues.add("malformed_observation")
            continue
        if kind not in required:
            continue
        bound_run = row.get("run")
        if type(bound_run) is not int or bound_run <= 0:
            observed.add(kind)
            issues.add("unbound_observation")
            continue
        if bound_run != run:
            continue
        observed.add(kind)
        if not set(row) <= fields:
            issues.add("malformed_observation")
        if type(row.get("value")) is not bool:
            issues.add("invalid_observation_value")
        if "t_ns" in row and (type(row["t_ns"]) is not int or row["t_ns"] < 0):
            issues.add("invalid_observation_time")
        # Only identical full rows collapse; no replay identity is inferred.
        if set(row) != fields or row not in rows[kind]:
            rows[kind].append(row)
    evidence = [kind for kind in required if kind in observed]
    for issue in ("unbound_observation", "malformed_observation",
                  "invalid_observation_value", "invalid_observation_time"):
        if issue in issues:
            return result("UNBEKANNT", issue)
    if any(len(candidates) > 1 for candidates in rows.values()):
        return result("UNBEKANNT", "contradictory_observation")
    if any(not rows[kind] for kind in write_kinds):
        return result("UNBEKANNT", "missing_write_evidence")
    if (rows["write_started"][0]["value"] is not True
            or rows["write_effect_before"][0]["value"] is not False
            or rows["write_effect"][0]["value"] is not True):
        return result("UNBEKANNT", "invalid_write_evidence")
    if question == "B":
        return result("JA", "same_observed_write_binding")

    finish_kinds = ("finish_return_before", "finish_return")
    if any(not rows[kind] for kind in finish_kinds):
        return result("UNBEKANNT", "missing_finish_evidence")
    if any(rows[kind][0]["value"] is not True for kind in finish_kinds):
        return result("UNBEKANNT", "invalid_finish_evidence")
    bound_kinds = kinds[1:]
    if any("t_ns" not in rows[kind][0] for kind in bound_kinds):
        return result("UNBEKANNT", "missing_time_bounds")
    f_lo = rows["finish_return_before"][0]["t_ns"]
    f_hi = rows["finish_return"][0]["t_ns"]
    e_lo = rows["write_effect_before"][0]["t_ns"]
    e_hi = rows["write_effect"][0]["t_ns"]
    start = rows["write_started"][0].get("t_ns")
    if (f_lo > f_hi or e_lo > e_hi
            or (start is not None and any(start > bound
                                         for bound in (f_lo, f_hi, e_lo, e_hi)))):
        return result("UNBEKANNT", "invalid_time_bounds")
    if f_hi < e_lo:
        if question == "C":
            return result("JA", "one_observed_write_after_finish_other_effects_unknown")
        return result("JA", "finish_before_observed_write_effect")
    if e_hi < f_lo:
        if question == "C":
            return result("JA", "one_observed_write_before_finish_other_effects_unknown")
        return result("NEIN", "observed_write_effect_before_finish")
    return result("UNBEKANNT", "unresolved_time_order")


def infer_live_local_file_identity(events: list[dict], run: int) -> dict:
    """One paired, source-observed live Linux/tmpfs comparison; never durable ID.

    Separate parser: the historical boolean recorder/schema remain unchanged.
    Scope and regular-file flags are trusted collector observations, not source
    authentication. No paths, contents, hashes, status or oracle are consulted.
    """
    limits = ("Nur gleichzeitig lebende regulaere Dateien im selben lokalen "
              "Linux/tmpfs-Messprozess ohne Mount-/Namespacewechsel; keine "
              "dauerhafte Identitaet nach Freigabe, Inhalts-/Revisionsidentitaet "
              "oder Quellechtheit; keine anderen Hosts, Neustarts oder Ressourcen.")

    def unknown(reason: str) -> dict:
        return {"A": "UNBEKANNT", "B": reason, "C": limits}

    if type(run) is not int or run <= 0:
        return unknown("Gueltige lokale Vergleichszuordnung fehlt.")
    if not isinstance(events, list):
        return unknown("Lesbare lokale Beobachtungsliste fehlt.")
    candidates = []
    for row in events:
        if not isinstance(row, dict):
            return unknown("Beobachtungsform ist ungueltig.")
        if row.get("kind") != "live_local_file_refs":
            continue
        if type(row.get("run")) is not int or row["run"] <= 0:
            return unknown("Native Beobachtung ohne gueltige Vergleichszuordnung.")
        if row["run"] != run:
            continue
        if set(row) != {"run", "kind", "value"}:
            return unknown("Native Beobachtungsform ist unvollstaendig oder ungueltig.")
        candidates.append(row["value"])
    if len(candidates) != 1:
        return unknown("Genau ein zugeordneter nativer Paarbeleg fehlt; "
                       "Pfad, Inhalt oder Hash ersetzen ihn nicht.")
    value = candidates[0]
    if not isinstance(value, dict) or set(value) != {"scope", "references"}:
        return unknown("Nativer Paarbeleg mit sichtbarem Scope fehlt.")
    scope = value["scope"]
    if (not isinstance(scope, dict)
            or set(scope) != {"os", "filesystem", "same_collection_process",
                              "live_handle_overlap_confirmed"}
            or scope["os"] != "Linux" or scope["filesystem"] != "tmpfs"
            or scope["same_collection_process"] is not True
            or scope["live_handle_overlap_confirmed"] is not True):
        return unknown("Gleichzeitige lebende Handles im selben Linux/tmpfs-"
                       "Messprozess sind nicht belegt; historische Kennungen reichen nicht.")
    refs = value["references"]
    if not isinstance(refs, list) or len(refs) != 2:
        return unknown("Zwei vollstaendige native Dateireferenzen fehlen.")
    for ref in refs:
        if (not isinstance(ref, dict) or set(ref) != {"st_dev", "st_ino", "regular_file"}
                or ref["regular_file"] is not True
                or type(ref["st_dev"]) is not int or ref["st_dev"] < 0
                or type(ref["st_ino"]) is not int or ref["st_ino"] <= 0):
            return unknown("Gueltige native Paare zweier regulaerer Dateien fehlen.")
    pairs = [(ref["st_dev"], ref["st_ino"]) for ref in refs]
    same = pairs[0] == pairs[1]
    return {"A": "DIESELBE" if same else "VERSCHIEDEN",
            "B": f"Native fstat-Paare {pairs[0]} und {pairs[1]} sind "
                 + ("gleich" if same else "verschieden")
                 + "; beide regulaeren Handles im bestaetigten lokalen Live-Scope.",
            "C": limits}


def status_baseline(events: list[dict], run: int, question: str, tool: bool = False) -> dict:
    if question != "target_present":
        return {"answer": None, "reason": "status_has_no_effect_order", "evidence": []}
    kinds = {"tool_end"} if tool else {"cli_end", "native_end"}
    rows = [e for e in events if e.get("run") == run and e.get("kind") in kinds]
    values = {e["value"] for e in rows}
    return {"answer": next(iter(values)) if len(values) == 1 else None,
            "reason": "deliberately_tested_status_only_baseline",
            "evidence": [e["event"] for e in rows]}


def all_predictions(events: list[dict], native: bool = False) -> list[dict]:
    check_events(events)
    predictions = []
    # The frozen query roster is independent of received events and the oracle.
    # Complete loss of a run must produce unknown rows, never drop the run.
    runs = range(1, len(PANEL) + 1)
    questions = ("target_present", "appearance_vs_native_end") if native else QUESTIONS
    for n in range(len(FIELDS) + 1):
        for fields in itertools.combinations(FIELDS, n):
            view = [{key: value for key, value in e.items() if key in fields} for e in events]
            for run in runs:
                for question in questions:
                    predictions.append({"run": run, "question": question,
                                        "fields": list(fields), "prediction": infer(view, run, question)})
    for run in runs:
        for question in questions:
            for name, tool in (("status_only", False), ("tool_status_only", True)):
                predictions.append({"run": run, "question": question, "fields": [name],
                                    "prediction": status_baseline(events, run, question, tool)})
            # Same analyst and same fields, removing only the actual target evidence.
            removed = "target_final" if question == "target_present" else "target_probe"
            view = [e for e in events if e["kind"] != removed]
            predictions.append({"run": run, "question": question, "fields": list(FIELDS),
                                "view": "without_target_evidence", "removed_kind": removed,
                                "prediction": infer(view, run, question)})
    return predictions


def judge(answer: object, truth: object) -> str:
    if truth is None:
        return "UNJUDGEABLE"
    if truth == "not_applicable":
        return "NOT_APPLICABLE" if answer is None or answer == truth else "WRONG"
    if answer is None:
        return "UNKNOWN"
    return "CORRECT" if type(answer) is type(truth) and answer == truth else "WRONG"


def minimal_sets(sets: list[set[str]]) -> list[list[str]]:
    return sorted([sorted(s) for s in sets if not any(t < s for t in sets)],
                  key=lambda s: (len(s), s))


def report(directory: Path, native: bool = False) -> dict:
    events = json_lines(directory / "observations.jsonl")
    predictions = all_predictions(events, native)
    # All claims are archived before any reference or scenario is read.
    directory.joinpath("predictions.jsonl").write_text(
        "".join(json.dumps(p, separators=(",", ":")) + "\n" for p in predictions))
    references = {r["run"]: r for r in json.loads(directory.joinpath("reference.json").read_text())}
    captures = json.loads(directory.joinpath("capture.json").read_text())
    rows = []
    for prediction in predictions:
        run, question = prediction["run"], prediction["question"]
        truth = references.get(run, {}).get(question)
        rows.append({**prediction, "reference": truth,
                     "verdict": judge(prediction["prediction"]["answer"], truth)})
    for row in rows:
        correct = [set(candidate["fields"]) for candidate in rows
                   if candidate["run"] == row["run"] and candidate["question"] == row["question"]
                   and candidate["verdict"] == "CORRECT" and not candidate.get("view")
                   and set(candidate["fields"]) <= set(FIELDS)]
        own = set(row["fields"])
        row["tested_additions"] = (minimal_sets([s - own for s in correct if own <= s])
                                    if own <= set(FIELDS) and not row.get("view") else None)
        row["minimal_correct_fieldsets"] = minimal_sets(correct)
    information_comparisons = []
    for missing in (r for r in rows if r.get("view") == "without_target_evidence"):
        full = next(r for r in rows if r["run"] == missing["run"]
                    and r["question"] == missing["question"] and r["fields"] == list(FIELDS)
                    and not r.get("view"))
        additions = [e["event"] for e in events if e["run"] == missing["run"]
                     and e["kind"] == missing["removed_kind"]]
        information_comparisons.append({
            "run": missing["run"], "question": missing["question"],
            "added_kind": missing["removed_kind"], "added_observations": additions,
            "without_verdict": missing["verdict"], "with_verdict": full["verdict"],
            "necessary_in_this_comparison": missing["verdict"] == "UNKNOWN"
            and full["verdict"] == "CORRECT",
        })
    summary = {}
    for name, fields in [("full", list(FIELDS)), ("status_only", ["status_only"]),
                         ("tool_status_only", ["tool_status_only"])]:
        counts = Counter(row["verdict"] for row in rows
                         if row["fields"] == fields and not row.get("view"))
        summary[name] = dict(counts)
    summary["without_target_evidence"] = dict(Counter(
        r["verdict"] for r in rows if r.get("view") == "without_target_evidence"))
    panel_fieldsets = {}
    for question in sorted({r["question"] for r in rows}):
        full = [r for r in rows if r["question"] == question
                and r["fields"] == list(FIELDS) and not r.get("view")]
        judged_runs = [r["run"] for r in full
                       if r["reference"] is not None and r["reference"] != "not_applicable"]
        candidates = []
        for n in range(len(FIELDS) + 1):
            for fields in itertools.combinations(FIELDS, n):
                cases = [r for r in rows if r["question"] == question and r["run"] in judged_runs
                         and r["fields"] == list(fields) and not r.get("view")]
                if judged_runs and len(cases) == len(judged_runs) and all(
                        r["verdict"] == "CORRECT" for r in cases):
                    candidates.append(set(fields))
        panel_fieldsets[question] = {
            "judgeable_runs": judged_runs,
            "unjudgeable_runs": [r["run"] for r in full if r["reference"] is None],
            "not_applicable_runs": [r["run"] for r in full if r["reference"] == "not_applicable"],
            "minimal_correct_fieldsets": minimal_sets(candidates),
        }
    integrity = {}
    if events:
        repeated = events + [dict(events[0])]
        changed = dict(events[0])
        changed["value"] = not changed["value"]
        unique, conflict = deduplicate(repeated)
        _, changed_conflict = deduplicate(events + [changed])
        integrity = {"synthetic_delivery_controls": True,
                     "original_projected_events": len(events), "deliveries_with_copy": len(repeated),
                     "unique_after_copy": len(unique), "identical_copy_conflict": conflict,
                     "changed_same_reference_conflict": changed_conflict}
    summary["started_processes"] = sum(r["started"] for r in captures)
    summary["real_agent_runs_observed"] = sum(r["real_agent_observed"] for r in captures)
    summary["timeouts"] = sum(r["timeout"] for r in captures)
    summary["canary_lines_raw"] = sum(r["stats"].get("canary_lines_raw", 0) for r in captures)
    summary["stored_observation_bytes"] = directory.joinpath("observations.jsonl").stat().st_size
    result = {"summary": summary, "delivery_controls": integrity,
              "information_comparisons": information_comparisons,
              "panel_fieldsets": panel_fieldsets,
              "scope": "controlled_native_collaboration_tool_runs_only" if native else
              "controlled_local_codex_cli_tool_runs_only", "rows": rows}
    write_json(directory / "report.json", result)
    own_files = ("observations.jsonl", "capture.json", "reference.json", "predictions.jsonl", "report.json")
    summary["canary_hits_in_named_archives"] = sum(
        directory.joinpath(name).read_bytes().count(CANARY.encode()) for name in own_files)
    write_json(directory / "report.json", result)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    collect = sub.add_parser("capture")
    collect.add_argument("--out", required=True, type=Path)
    collect.add_argument("--codex", default="codex")
    collect.add_argument("--timeout", type=float, default=120)
    analyse = sub.add_parser("report")
    analyse.add_argument("--input", required=True, type=Path)
    analyse.add_argument("--native", action="store_true",
                         help="Use the frozen native completion question, even if all events are lost")
    args = parser.parse_args()
    if args.command == "capture":
        capture(args.out, args.codex, args.timeout)
    else:
        report(args.input, args.native)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
