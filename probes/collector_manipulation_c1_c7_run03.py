"""Independent C1-C7 Run-03 capture; one process, one invocation per packet.

The process stops after sealing observer inputs, raw ABCD responses and wrapper
journals.  It retains every owned descriptor until an external checkpoint
authorization file appears.  Only then does it run the separate I/O reference.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
from types import SimpleNamespace
import sys
import time
from typing import Callable

import hypothesis
import pytest

from observer_research import infer_current_local_file_identity
from probes.local_file_identity_capture import io_reference, write_view


FOLDER = Path("/tmp/aa-collector-manipulation-c1-c7-run03-20261008")
SYNTHETIC_INODE = 424242


@dataclass
class CaseState:
    number: int
    handles: list[int]
    paths: list[Path]
    actual_pairs: list[tuple[int, int]]
    offered_pairs: list[tuple[int, int]]
    packet: list[dict]
    journal: list[dict]


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    path.chmod(0o444)


def save_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(value)
    path.chmod(0o444)


def error_record(exc: BaseException, stage: str) -> dict:
    return {
        "stage": stage,
        "type": type(exc).__name__,
        "message": str(exc),
        "errno": getattr(exc, "errno", None),
        "notes": getattr(exc, "__notes__", []),
    }


def pair_from_result(value: object) -> tuple[int, int]:
    return (value.st_dev, value.st_ino)  # type: ignore[attr-defined]


def regular_result(pair: tuple[int, int]) -> SimpleNamespace:
    return SimpleNamespace(st_mode=stat.S_IFREG | 0o600, st_dev=pair[0], st_ino=pair[1])


def make_packet(
    number: int,
    actual: list[tuple[int, int]],
    device: int,
) -> tuple[list[dict], list[tuple[int, int]]]:
    if number in (1, 2, 5, 6):
        offered = list(actual)
    elif number == 3:
        offered = [actual[0], actual[0]]
    elif number == 4:
        replacement = (actual[0][0], actual[0][1] + 1)
        if replacement[1] <= 0 or replacement == actual[0]:
            raise ValueError("invalid_frozen_replacement_inode")
        offered = [actual[0], replacement]
    elif number == 7:
        offered = [(device, SYNTHETIC_INODE), (device, SYNTHETIC_INODE)]
    else:
        raise ValueError("case_out_of_frozen_range")
    references = [
        {"st_dev": pair[0], "st_ino": pair[1], "regular_file": True}
        for pair in offered
    ]
    if number == 6:
        del references[1]["regular_file"]
    packet = [{
        "run": 1,
        "kind": "live_local_file_refs",
        "value": {
            "scope": {
                "os": "Linux",
                "filesystem": "tmpfs",
                "same_collection_process": True,
                "live_handle_overlap_confirmed": True,
            },
            "references": references,
        },
    }]
    return packet, offered


def _project_fstat(
    number: int,
    handle_index: int,
    fstat_ordinal: int,
    offered: list[tuple[int, int]],
    original: Callable[[int], object],
    fd: int,
) -> tuple[object, str]:
    if number in (3, 4, 7):
        return regular_result(offered[handle_index - 1]), "manipulated"
    if number == 5 and fstat_ordinal == 4 and handle_index == 2:
        return regular_result((offered[1][0], offered[1][1] + 1)), "manipulated"
    return original(fd), "delegated"


def invoke_with_wrappers(
    packet: list[dict],
    handles: list[int],
    number: int,
    offered: list[tuple[int, int]],
    journal: list[dict],
    observer: Callable[..., dict] = infer_current_local_file_identity,
) -> tuple[dict, bool]:
    """Install only the five contracted call-local wrappers and always restore."""
    originals = {
        "fcntl": fcntl.fcntl,
        "fstat": os.fstat,
        "uname": os.uname,
        "run": subprocess.run,
        "stat": os.stat,
    }
    fstat_ordinal = 0
    sequence = 0

    def entry(name: str) -> dict:
        nonlocal sequence
        sequence += 1
        row = {"sequence": sequence, "operation": name, "attempted": True, "returned": False}
        journal.append(row)
        return row

    def handle_index(fd: int) -> int | None:
        return handles.index(fd) + 1 if fd in handles else None

    def wrapped_fcntl(fd: int, command: int, *args: object) -> object:
        row = entry("fcntl")
        row.update(handle_index=handle_index(fd), is_f_getfd=command == fcntl.F_GETFD)
        try:
            if number == 7:
                result, source = 0, "manipulated"
            else:
                result, source = originals["fcntl"](fd, command, *args), "delegated"
        except BaseException as exc:
            row["error"] = error_record(exc, "wrapped_fcntl")
            raise
        row.update(returned=True, source=source, descriptor_flags=result)
        return result

    def wrapped_fstat(fd: int) -> object:
        nonlocal fstat_ordinal
        row = entry("fstat")
        fstat_ordinal += 1
        index = handle_index(fd)
        row.update(handle_index=index, fstat_ordinal=fstat_ordinal)
        try:
            if index is None:
                result, source = originals["fstat"](fd), "delegated"
            else:
                result, source = _project_fstat(
                    number, index, fstat_ordinal, offered, originals["fstat"], fd
                )
        except BaseException as exc:
            row["error"] = error_record(exc, "wrapped_fstat")
            raise
        row.update(
            returned=True,
            source=source,
            native_pair=list(pair_from_result(result)),
            regular=stat.S_ISREG(result.st_mode),  # type: ignore[attr-defined]
        )
        return result

    def wrapped_uname() -> object:
        row = entry("uname")
        try:
            if number == 7:
                result, source = SimpleNamespace(sysname="Linux"), "manipulated"
            else:
                result, source = originals["uname"](), "delegated"
        except BaseException as exc:
            row["error"] = error_record(exc, "wrapped_uname")
            raise
        row.update(returned=True, source=source, system=result.sysname)
        return result

    def wrapped_run(*args: object, **kwargs: object) -> object:
        row = entry("run")
        row["is_fixed_findmnt"] = bool(args and args[0] == [
            "findmnt", "-T", "/tmp", "-n", "-o", "FSTYPE"
        ])
        try:
            if number == 7:
                result, source = SimpleNamespace(returncode=0, stdout="tmpfs\n"), "manipulated"
            else:
                result, source = originals["run"](*args, **kwargs), "delegated"
        except BaseException as exc:
            row["error"] = error_record(exc, "wrapped_run")
            raise
        row.update(
            returned=True,
            source=source,
            exit_code=result.returncode,
            filesystem_types=sorted(set(result.stdout.split())),
        )
        return result

    def wrapped_stat(path: object, *args: object, **kwargs: object) -> object:
        row = entry("stat")
        row["is_tmp_context"] = path == "/tmp"
        try:
            if number == 7:
                result, source = SimpleNamespace(st_dev=offered[0][0]), "manipulated"
            else:
                result, source = originals["stat"](path, *args, **kwargs), "delegated"
        except BaseException as exc:
            row["error"] = error_record(exc, "wrapped_stat")
            raise
        row.update(returned=True, source=source, device=result.st_dev)
        return result

    try:
        fcntl.fcntl = wrapped_fcntl
        os.fstat = wrapped_fstat
        os.uname = wrapped_uname
        subprocess.run = wrapped_run
        os.stat = wrapped_stat
        answer = observer(packet, 1, handles=handles)
    finally:
        fcntl.fcntl = originals["fcntl"]
        os.fstat = originals["fstat"]
        os.uname = originals["uname"]
        subprocess.run = originals["run"]
        os.stat = originals["stat"]
    restored = (
        fcntl.fcntl is originals["fcntl"]
        and os.fstat is originals["fstat"]
        and os.uname is originals["uname"]
        and subprocess.run is originals["run"]
        and os.stat is originals["stat"]
    )
    return answer, restored


def seal_tree(root: Path, manifest: Path) -> dict[str, str]:
    hashes = {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != manifest
    }
    save_json(manifest, {"algorithm": "sha256", "files": hashes})
    return hashes


def verify_system_gate(out: Path) -> dict:
    filesystem_types = sorted(set(subprocess.check_output(
        ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True
    ).split()))
    result = {
        "os": os.uname().sysname,
        "kernel": os.uname().release,
        "machine": os.uname().machine,
        "python": sys.version.split()[0],
        "pytest": pytest.__version__,
        "hypothesis": hypothesis.__version__,
        "filesystem_types": filesystem_types,
        "tmp_device": os.stat("/tmp").st_dev,
        "network_mode_required": "none",
    }
    if (
        result["os"] != "Linux"
        or sys.version_info[:2] != (3, 12)
        or filesystem_types != ["tmpfs"]
        or tuple(int(value) for value in pytest.__version__.split(".")[:1]) < (8,)
        or tuple(int(value) for value in hypothesis.__version__.split(".")[:2]) < (6, 100)
    ):
        raise RuntimeError("run02_system_gate_failed")
    return result


def create_case(resources: Path, number: int, device: int, active: list[int]) -> CaseState:
    folder = resources / f"C{number}"
    folder.mkdir(mode=0o700, parents=True)
    same = number in (1, 4, 5, 6)
    flags = os.O_RDWR | os.O_NOFOLLOW
    first_path = folder / "first"
    first = os.open(first_path, flags | os.O_CREAT | os.O_EXCL, 0o600)
    active.append(first)
    write_view(first, os.urandom(32))
    paths = [first_path]
    if same:
        second = os.open(first_path, flags)
    else:
        second_path = folder / "second"
        second = os.open(second_path, flags | os.O_CREAT | os.O_EXCL, 0o600)
        paths.append(second_path)
        write_view(second, os.urandom(32))
    active.append(second)
    handles = [first, second]
    if handles[0] == handles[1]:
        raise RuntimeError("numeric_descriptor_arguments_not_distinct")
    actual = [pair_from_result(os.fstat(fd)) for fd in handles]
    if any(pair[0] != device or pair[1] <= 0 for pair in actual):
        raise RuntimeError("owned_file_outside_frozen_tmp_device")
    packet, offered = make_packet(number, actual, device)
    return CaseState(number, handles, paths, actual, offered, packet, [])


def analyze_c5(journal: list[dict], restored: bool) -> dict:
    fstats = [row for row in journal if row["operation"] == "fstat" and row["returned"]]
    deltas = []
    if len(fstats) == 4:
        for before, after in zip(fstats[:2], fstats[2:]):
            deltas.append(before["native_pair"] != after["native_pair"])
    return {
        "fstat_returns": len(fstats),
        "per_handle_pre_post_changed": deltas,
        "changed_projection_count": sum(deltas),
        "only_final_handle_2_manipulated": bool(
            len(fstats) == 4
            and [row["source"] for row in fstats] == [
                "delegated", "delegated", "delegated", "manipulated"
            ]
        ),
        "wrappers_restored": restored,
    }


def cleanup(states: list[CaseState], active: list[int]) -> list[dict]:
    errors = []
    for fd in list(active):
        try:
            os.close(fd)
            active.remove(fd)
        except BaseException as exc:
            errors.append(error_record(exc, "cleanup_handle"))
    for state in states:
        for path in state.paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
            except BaseException as exc:
                errors.append(error_record(exc, "cleanup_path"))
    return errors


def capture(out: Path, wait_seconds: int) -> int:
    if out.resolve() != FOLDER:
        raise ValueError("only_frozen_run02_directory")
    out.mkdir(mode=0o700, exist_ok=False)
    pre = out / "pre-gt"
    resources = out / "resources"
    resources.mkdir(mode=0o700)
    active: list[int] = []
    states: list[CaseState] = []
    restorations: dict[int, bool] = {}
    stage = "system_gate"
    try:
        system = verify_system_gate(out)
        save_json(pre / "system.json", system)
        device = system["tmp_device"]
        stage = "create_owned_cases"
        for number in range(1, 8):
            states.append(create_case(resources, number, device, active))
        for state in states:
            stage = f"P{state.number}_single_observer_invocation"
            save_json(pre / "inputs" / f"P{state.number}.json", state.packet)
            answer, restored = invoke_with_wrappers(
                state.packet,
                state.handles,
                state.number,
                state.offered_pairs,
                state.journal,
            )
            restorations[state.number] = restored
            save_json(pre / "responses" / f"P{state.number}.json", {
                "packet": f"P{state.number}",
                "query_run": 1,
                "raw_observer_abcd": answer,
            })
            save_json(pre / "journals" / f"P{state.number}.json", {
                "packet": f"P{state.number}",
                "calls": state.journal,
                "wrappers_restored": restored,
            })
        status = {
            "sequence": [f"P{state.number}" for state in states],
            "observer_invocations": len(states),
            "all_wrappers_restored": all(restorations.values()),
            "ground_truth_started": False,
            "handles_retained": len(active),
            "failures": [],
        }
        save_json(pre / "capture-status.json", status)
        seal_tree(pre, pre / "pre-gt-manifest.json")
        save_json(pre / "checkpoint-ready.json", {
            "ready": True,
            "ground_truth_started": False,
            "authorization_file": "continue-after-remote-checkpoint",
        })
        print(
            json.dumps({"checkpoint_ready": True, "observer_invocations": len(states)}),
            flush=True,
        )
    except BaseException as exc:
        save_json(pre / "capture-failure.json", error_record(exc, stage))
        cleanup(states, active)
        raise

    authorization = out / "continue-after-remote-checkpoint"
    deadline = time.monotonic() + wait_seconds
    while not authorization.exists():
        if time.monotonic() >= deadline:
            save_json(out / "post-gt" / "timeout.json", {
                "ground_truth_started": False,
                "reason": "remote_checkpoint_authorization_timeout",
            })
            cleanup(states, active)
            return 2
        time.sleep(0.2)

    post = out / "post-gt"
    gt_errors = []
    try:
        for number in (1, 2, 3, 4, 7):
            state = states[number - 1]
            journal: dict = {}
            try:
                io_reference(state.handles[0], state.handles[1], journal)
            except BaseException as exc:
                failure = error_record(exc, journal.get("stage", "io_reference"))
                journal.update(truth="UNBEKANNT", reference_error=failure)
                gt_errors.append({"case": f"C{number}", **failure})
            save_json(post / "ground-truth" / f"C{number}.json", journal)
        save_json(post / "controls" / "C5.json", analyze_c5(states[4].journal, restorations[5]))
        save_json(post / "controls" / "C6.json", {
            "second_reference_keys": sorted(states[5].packet[0]["value"]["references"][1]),
            "regular_file_missing": (
                "regular_file" not in states[5].packet[0]["value"]["references"][1]
            ),
            "native_calls": len(states[5].journal),
            "wrappers_restored": restorations[6],
        })
    finally:
        cleanup_errors = cleanup(states, active)
    remaining_files = sorted(
        str(path.relative_to(resources)) for path in resources.rglob("*") if path.is_file()
    )
    save_json(post / "completion-status.json", {
        "ground_truth_started_after_authorization": True,
        "io_cases": ["C1", "C2", "C3", "C4", "C7"],
        "ground_truth_errors": gt_errors,
        "cleanup_errors": cleanup_errors,
        "remaining_resource_files": remaining_files,
        "active_handles_after_cleanup": len(active),
        "raw_contents_archived": False,
    })
    seal_tree(post, post / "post-gt-manifest.json")
    print(json.dumps({
        "ground_truth_complete": not gt_errors,
        "ground_truth_errors": len(gt_errors),
        "cleanup_errors": len(cleanup_errors),
    }), flush=True)
    return int(bool(gt_errors or cleanup_errors or remaining_files or active))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--wait-seconds", type=int, default=7200)
    args = parser.parse_args()
    if args.wait_seconds <= 0:
        raise ValueError("positive_wait_required")
    return capture(args.out, args.wait_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
