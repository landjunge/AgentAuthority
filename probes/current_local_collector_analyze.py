"""Read-only comparison AFTER the answer checkpoint; never invoked by capture."""
from __future__ import annotations

import argparse
from collections import Counter
import errno
import hashlib
import json
from pathlib import Path

from probes.local_file_identity_capture import save


def load(path: Path):
    return json.loads(path.read_text())


def complete_current(packet: list[dict], calls: list[dict]) -> bool:
    # Independently inspect actual delegated operations and their returned
    # projections. Never infer current confirmation from the observer's A/C.
    operations = ["fcntl", "fstat", "fcntl", "fstat", "uname", "run", "stat",
                  "fcntl", "fstat", "fcntl", "fstat"]
    if ([call["operation"] for call in calls] != operations
            or not all(call["attempted"] and call["returned"] for call in calls)):
        return False
    fd_checks = [calls[i] for i in (0, 2, 7, 9)]
    snapshots = [calls[i] for i in (1, 3, 8, 10)]
    if ([call["handle_index"] for call in fd_checks] != [1, 2, 1, 2]
            or not all(call["is_f_getfd"] for call in fd_checks)
            or [call["handle_index"] for call in snapshots] != [1, 2, 1, 2]
            or not all(call["regular"] for call in snapshots)):
        return False
    before = [call["native_pair"] for call in snapshots[:2]]
    after = [call["native_pair"] for call in snapshots[2:]]
    offered = [[r["st_dev"], r["st_ino"]] for r in packet[0]["value"]["references"]]
    return (calls[4]["system"] == "Linux" and calls[5]["is_fixed_findmnt"]
            and calls[5]["exit_code"] == 0 and calls[5]["filesystem_types"] == ["tmpfs"]
            and calls[6]["is_tmp_context"] and all(p[0] == calls[6]["device"] for p in before)
            and before == after == offered)


def closed_failure(calls: list[dict]) -> bool:
    return (len(calls) == 1 and calls[0]["operation"] == "fcntl"
            and calls[0]["handle_index"] == 1 and calls[0]["is_f_getfd"]
            and calls[0]["attempted"] and not calls[0]["returned"]
            and calls[0].get("error", {}).get("errno") == errno.EBADF)


def released(entry: dict) -> bool:
    return (entry["complete"]
            and len(entry["closed_handles"]) == 2
            and all(e["close_returned"] and e["closed_fd_is_ebadf"]
                    for e in entry["closed_handles"])
            and all(e["unlink_returned"] and e["path_absent"] and e["own_target_fd_links"] == 0
                    for e in entry["removed_paths"]))


def evaluate_case(archive: Path, n: int, invocation: dict) -> dict:
    case, name = f"F{n}", f"P{n}"
    answer_path = archive / "responses" / name / "answer.json"
    input_path = archive / "inputs" / f"{name}.json"
    packet, raw = load(input_path), load(answer_path)
    answer, calls = raw["raw_observer_abcd"], invocation["native_calls"]
    current = complete_current(packet, calls)
    technical = any(
        (not call["returned"] and call.get("error", {}).get("errno") != errno.EBADF)
        or (call["operation"] == "run" and call["returned"] and call["exit_code"] != 0)
        for call in calls)
    truth_c = "JA" if current else ("UNBEKANNT" if technical else "NEIN")
    integrity = (hashlib.sha256(answer_path.read_bytes()).hexdigest() == invocation["answer_saved_sha256"]
                 and raw["input_sha256"] == hashlib.sha256(input_path.read_bytes()).hexdigest())
    book = load(archive / "ground-truth" / "collector-lifecycle.json")
    if n in (1, 2, 7):
        reference = load(archive / "ground-truth" / f"{case}-io.json")
        truth_a = reference.get("truth", "UNBEKANNT")
        # A-GT must NEVER depend on whether the observer did its own check.
        valid_gt = (reference.get("stage") == "complete"
                    and reference.get("reference_error") is None
                    and reference.get("full_reads_verified_by_eof_probe")
                    and truth_a in ("DIESELBE", "VERSCHIEDEN"))
        check_path = current
        gt_kind = "independent_bidirectional_io_separate_from_current_check_journal"
    else:
        truth_a = "UNBEKANNT"
        gt_kind = "insufficient_current_evidence_not_resource_inequality"
        if n == 3:
            valid_gt = (not invocation["runtime_handles_supplied"]
                        and released(book["releases"]["F1"])
                        and (archive / "inputs/P1.json").read_bytes() == input_path.read_bytes())
            check_path = not calls
        elif n == 4:
            valid_gt = (not invocation["runtime_handles_supplied"]
                        and book["synthetic"]["actual_resource_handles"] == 0
                        and book["synthetic"]["source"] == "handcrafted_primitives")
            check_path = not calls
        elif n == 5:
            valid_gt = (invocation["runtime_handles_supplied"]
                        and released(book["releases"]["F1"])
                        and (archive / "inputs/P1.json").read_bytes() == input_path.read_bytes())
            check_path = closed_failure(calls)
        else:
            closed = book["closed_before_check"]["F6"]
            valid_gt = (len(closed["close_checks"]) == 2
                        and all(e["close_returned"] and e["immediate_ebadf"] for e in closed["close_checks"])
                        and book["releases"]["F6"]["complete"]
                        and all(e["unlink_returned"] and e["path_absent"] and e["own_target_fd_links"] == 0
                                for e in book["releases"]["F6"]["removed_paths"]))
            check_path = closed_failure(calls)
    judgeable = bool(valid_gt and integrity)
    a_ok, c_ok = answer["A"] == truth_a, answer["C"] == truth_c
    positive = answer["A"] in ("DIESELBE", "VERSCHIEDEN")
    bd_ok = (bool(answer["B"])
             and all(limit in answer["D"] for limit in (
                 "Linux/tmpfs", "sequenzielle Checks", "kein atomarer Lebenszeitbeweis",
                 "Keine Packetherkunft", "historische/permanente Identitaet"))
             and ((current and answer["B"].startswith("Jetzt F_GETFD/fstat")) if positive
                  else ("Keine Handles" in answer["B"] or "EBADF" in answer["B"])))
    required_c = "JA" if n in (1, 2, 7) else "NEIN"
    expected_a = {1: "DIESELBE", 2: "VERSCHIEDEN", 7: "VERSCHIEDEN"}.get(n, "UNBEKANNT")
    frozen_met = answer["A"] == expected_a and answer["C"] == required_c and check_path
    # A technical collector obstruction prevents the full required scenario;
    # still preserve independently judgeable A and factual C scores separately.
    verdict = ("UNBEURTEILBAR" if not judgeable else
               ("FALSCH" if not c_ok or (positive and (not current or not a_ok)) else
                ("UNBEURTEILBAR" if technical else
                 ("KORREKT" if a_ok and bd_ok and frozen_met else "FALSCH"))))
    return {"case": case, "packet": name, "answer": answer,
            "reference_a": truth_a, "reference_c": truth_c, "reference_kind": gt_kind,
            "native_calls": len(calls), "complete_current_confirmation": current,
            "reference_valid": bool(valid_gt), "integrity_ok": integrity,
            "a_correct": a_ok if judgeable else None, "c_correct": c_ok if judgeable else None,
            "bd_supported": bd_ok, "frozen_requirements_met": frozen_met,
            "technical_collector_obstruction": technical, "evaluation": verdict,
            "positive_without_current_check": bool(judgeable and positive and not current)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    archive = parser.parse_args().archive
    checkpoint = load(archive / "answer-checkpoint-integrity.json")
    integrity_errors = []
    for relative, digest in checkpoint["sha256"].items():
        try:
            if hashlib.sha256((archive / relative).read_bytes()).hexdigest() != digest:
                integrity_errors.append(relative)
        except OSError:
            integrity_errors.append(relative)
    book = load(archive / "ground-truth" / "collector-lifecycle.json")
    status = load(archive / "capture-status.json")
    sequence = [i["packet"] for i in book["invocations"]]
    exact_seven = (sequence == ["P1", "P3", "P5", "P4", "P2", "P6", "P7"]
                   and status["invocations_started"] == 7)
    rows, counts = [], Counter({key: 0 for key in (
        "native_check_attempted", "complete_current_confirmation", "correct_a", "false_a",
        "correct_c", "false_c", "unknown_a", "unknown_c", "positive_without_current_check",
        "unjudgeable", "frozen_requirements_not_met")})
    for n in range(1, 8):
        name = f"P{n}"
        entries = [i for i in book["invocations"] if i["packet"] == name]
        try:
            if len(entries) != 1:
                raise ValueError("missing_or_duplicated_invocation")
            row = evaluate_case(archive, n, entries[0])
        except (OSError, KeyError, TypeError, ValueError, IndexError) as exc:
            row = {"case": f"F{n}", "packet": name, "evaluation": "UNBEURTEILBAR",
                   "reason": "missing_or_partial_response_or_reference", "error_type": type(exc).__name__}
        rows.append(row)
        if "answer" in row:
            counts["native_check_attempted"] += bool(row["native_calls"])
            counts["complete_current_confirmation"] += row["complete_current_confirmation"]
            counts["correct_a"] += row["a_correct"] is True
            counts["false_a"] += row["a_correct"] is False
            counts["correct_c"] += row["c_correct"] is True
            counts["false_c"] += row["c_correct"] is False
            counts["unknown_a"] += row["answer"]["A"] == "UNBEKANNT"
            counts["unknown_c"] += row["answer"]["C"] == "UNBEKANNT"
            counts["positive_without_current_check"] += row["positive_without_current_check"]
            counts["frozen_requirements_not_met"] += not row["frozen_requirements_met"]
        counts["unjudgeable"] += row["evaluation"] == "UNBEURTEILBAR"
    failures = len(status["failures"]) + len(status["cleanup_errors"])
    # Invalid integrity/extra or missing invocations make the protocol inconclusive.
    # Cleanly evidenced false claims remain NOT SUPPORTED despite unrelated errors.
    verdict = ("INCONCLUSIVE" if integrity_errors else
               ("NOT SUPPORTED" if counts["positive_without_current_check"]
                or any(r["evaluation"] == "FALSCH" for r in rows) else
                ("INCONCLUSIVE" if not exact_seven or failures or counts["unjudgeable"] or status["remaining_resource_files"]
                 else "SUPPORTED IN THIS CASE SET")))
    result = {"verdict": verdict, "counts": dict(counts), "capture_or_cleanup_errors": failures,
              "exact_seven_in_frozen_order": exact_seven, "integrity_errors": integrity_errors,
              "cases": rows}
    save(archive / "derived" / "evaluation.json", result)
    print(json.dumps({"verdict": verdict, "counts": dict(counts)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
