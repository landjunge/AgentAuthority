"""One frozen three-case local-file study; never a general resource sensor."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")
    path.chmod(0o444)


def read_view(fd: int) -> bytes:
    # Controlled files have 32, 64 or 96 bytes; fixed offsets avoid shared offsets.
    value = os.pread(fd, 256, 0)
    if len(value) not in (32, 64, 96) or os.pread(fd, 1, len(value)) != b"":
        raise RuntimeError(f"unexpected_or_short_reference_read:length={len(value)}")
    return value


def write_view(fd: int, value: bytes) -> int:
    written = os.pwrite(fd, value, 0)
    if written != len(value):
        raise RuntimeError(f"short_reference_write:returned={written},requested={len(value)}")
    try:
        os.ftruncate(fd, len(value))
    except OSError as exc:
        exc.add_note(f"pwrite_returned={written};ftruncate_requested={len(value)}")
        raise
    return written


def identity(fd: int) -> dict:
    value = os.fstat(fd)
    return {"st_dev": value.st_dev, "st_ino": value.st_ino,
            "regular_file": stat.S_ISREG(value.st_mode)}


def io_reference(first: int, second: int, journal: dict) -> dict:
    """No fstat, inode comparison, case label or expected relation here."""
    journal.update(truth="UNBEKANNT", checks={}, read_lengths=[[], [], []],
                   successful_write_lengths=[], offset=0)
    journal["stage"] = "initial_first_read"
    a0 = read_view(first)
    journal["read_lengths"][0].append(len(a0))
    journal["stage"] = "initial_second_read"
    b0 = read_view(second)
    journal["read_lengths"][0].append(len(b0))
    marker_a = os.urandom(64)
    if len(a0) == 64 or len(b0) == 64:
        raise RuntimeError("reference_marker_not_distinct")
    journal["stage"] = "first_marker_write_and_truncate"
    wa = write_view(first, marker_a)
    journal["successful_write_lengths"].append(wa)
    journal["stage"] = "first_own_read"
    a1 = read_view(first)
    journal["read_lengths"][1].append(len(a1))
    checks = journal["checks"]
    checks["own_a_write_visible"] = a1 == marker_a
    journal["stage"] = "first_cross_read"
    b1 = read_view(second)
    journal["read_lengths"][1].append(len(b1))
    checks["cross_b_matches_a_marker"] = b1 == marker_a
    checks["cross_b_unchanged_from_its_baseline"] = b1 == b0
    # These actual post-direction-1 views are direction-2's fresh baselines.
    marker_b = os.urandom(96)
    if len(a1) == 96 or len(b1) == 96:
        raise RuntimeError("reference_marker_not_distinct")
    journal["stage"] = "second_marker_write_and_truncate"
    wb = write_view(second, marker_b)
    journal["successful_write_lengths"].append(wb)
    journal["stage"] = "second_cross_read"
    a2 = read_view(first)
    journal["read_lengths"][2].append(len(a2))
    checks["cross_a_matches_b_marker"] = a2 == marker_b
    checks["cross_a_unchanged_from_its_fresh_baseline"] = a2 == a1
    journal["stage"] = "second_own_read"
    b2 = read_view(second)
    journal["read_lengths"][2].append(len(b2))
    checks["own_b_write_visible"] = b2 == marker_b
    own = checks["own_a_write_visible"] and checks["own_b_write_visible"]
    same = checks["cross_b_matches_a_marker"] and checks["cross_a_matches_b_marker"]
    different = (checks["cross_b_unchanged_from_its_baseline"]
                 and checks["cross_a_unchanged_from_its_fresh_baseline"])
    truth = "DIESELBE" if own and same else (
        "VERSCHIEDEN" if own and different else "UNBEKANNT")
    journal.update(truth=truth, stage="complete", full_reads_verified_by_eof_probe=True,
                   reference_error=None)
    return journal


def error_record(exc: Exception, stage: str) -> dict:
    return {"stage": stage, "type": type(exc).__name__, "message": str(exc),
            "errno": getattr(exc, "errno", None), "notes": getattr(exc, "__notes__", [])}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out.parent != Path("/tmp").resolve():
        raise ValueError("only_new_direct_tmp_directory")
    out.mkdir(mode=0o700, exist_ok=False)
    kinds = set(subprocess.check_output(
        ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True).split())
    if os.uname().sysname != "Linux" or kinds != {"tmpfs"}:
        save(out / "capture-status.json", {"cases_started": 0, "errors": 1,
                                           "failure": "frozen_system_scope_mismatch"})
        return
    save(out / "system.json", {"os": "Linux", "kernel": os.uname().release,
                               "filesystem": "tmpfs", "mount_boundary": "/tmp",
                               "python": sys.version.split()[0]})
    errors = 0
    for number in (1, 2, 3):
        folder = out / "resources" / f"L{number}"
        folder.mkdir(parents=True)
        a, b = folder / "A", folder / "B"
        steps = []
        journal, failures = {}, []
        stage = "create_and_measure_first_reference"
        try:
            with ExitStack() as stack:
                flags = os.O_RDWR | os.O_NOFOLLOW
                first = os.open(a, flags | os.O_CREAT | os.O_EXCL, 0o600)
                stack.callback(os.close, first)
                payload = os.urandom(32)
                write_view(first, payload)
                before = identity(first)
                steps.append("created_A_and_kept_first_handle_open")
                stage = "case_operation_and_second_reference"
                if number == 1:
                    os.rename(a, b)
                    steps.append("rename_A_to_B_returned")
                    second = os.open(b, flags)
                    stack.callback(os.close, second)
                elif number == 2:
                    os.unlink(a)
                    steps.append("unlink_A_returned_first_handle_retained")
                    second = os.open(a, flags | os.O_CREAT | os.O_EXCL, 0o600)
                    stack.callback(os.close, second)
                    write_view(second, payload)
                    steps.append("exclusive_new_A_creation_returned")
                else:
                    shutil.copyfile(a, b)
                    steps.append("copy_A_to_B_returned")
                    second = os.open(b, flags)
                    stack.callback(os.close, second)
                after = identity(second)
                stage = "confirm_overlap_and_save_inputs"
                fcntl.fcntl(first, fcntl.F_GETFD)
                fcntl.fcntl(second, fcntl.F_GETFD)
                source = {"scope": {"os": "Linux", "filesystem": "tmpfs",
                                    "same_collection_process": True,
                                    "live_handle_overlap_confirmed": True},
                          "references": [before, after]}
                # No operation history or expected answer in the primary channel.
                save(out / "observations" / f"P{number}.json", source)
                if number == 2:
                    save(out / "controls" / "path_only.json", {"path_texts": [a.name, a.name]})
                if number == 3:
                    initial_a, initial_b = read_view(first), read_view(second)
                    save(out / "controls" / "content_only.json",
                         {"content_equal": initial_a == initial_b})
                    save(out / "controls" / "hash_only.json", {"content_sha256": [
                        hashlib.sha256(initial_a).hexdigest(), hashlib.sha256(initial_b).hexdigest()]})
                stage = "independent_io_reference"
                reference = io_reference(first, second, journal)
                reference["operations"] = steps
                stage = "save_reference_and_close_handles"
                save(out / "ground-truth" / f"L{number}.json", reference)
        except Exception as exc:
            failure = error_record(exc, journal.get("stage", stage)
                                   if stage == "independent_io_reference" else stage)
            failures.append(failure)
            # A partial original recording remains; never repair/rerun the case.
            obs = out / "observations" / f"P{number}.json"
            if not obs.exists():
                save(obs, {})
            gt = out / "ground-truth" / f"L{number}.json"
            if not gt.exists():
                journal.update(truth="UNBEKANNT", reference_error=failure, operations=steps)
                save(gt, journal)
        finally:
            for path in (a, b):
                try:
                    if path.exists():
                        path.unlink()
                except Exception as exc:
                    failures.append(error_record(exc, "remove_temporary_" + path.name))
            if failures:
                errors += 1
                save(out / "errors" / f"L{number}.json", {"failures": failures})
    remaining = list((out / "resources").rglob("*"))
    save(out / "capture-status.json", {"cases_started": 3, "errors": errors,
                                       "raw_contents_archived": False,
                                       "temporary_data_files_removed": not any(
                                           path.is_file() for path in remaining)})
    print(json.dumps({"cases_started": 3, "errors": errors}))


if __name__ == "__main__":
    main()
