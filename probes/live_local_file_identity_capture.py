"""One T1-T3 capture plus T4-T7 views. Research harness, no new resource sensor."""
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

# Frozen independent I/O oracle and storage helpers, reused without modification.
from probes.local_file_identity_capture import (
    error_record, io_reference, read_view, save, write_view,
)


def native_reference(fd: int) -> dict:
    measured = os.fstat(fd)
    return {"st_dev": measured.st_dev, "st_ino": measured.st_ino,
            "regular_file": stat.S_ISREG(measured.st_mode)}


def row(run: int, kind: str, value: object) -> list[dict]:
    return [{"run": run, "kind": kind, "value": value}]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.parent != Path("/tmp"):
        raise ValueError("only_new_direct_tmp_directory")
    out.mkdir(mode=0o700, exist_ok=False)
    types = set(subprocess.check_output(
        ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True).split())
    if os.uname().sysname != "Linux" or types != {"tmpfs"}:
        save(out / "capture-status.json", {"cases_started": 0,
                                           "failure": "frozen_scope_mismatch"})
        return 1
    save(out / "system.json", {"os": "Linux", "kernel": os.uname().release,
                               "filesystem": "tmpfs", "mount_boundary": "/tmp",
                               "python": sys.version.split()[0]})
    scope = {"os": "Linux", "filesystem": "tmpfs", "same_collection_process": True,
             "live_handle_overlap_confirmed": True}
    failures = []
    started = 0
    for number in (1, 2, 3):
        folder = out / "resources" / f"T{number}"
        folder.mkdir(parents=True)
        a, b = folder / "A", folder / "B"
        journal, operations = {}, []
        stage = "create_first"
        started += 1
        try:
            with ExitStack() as stack:
                flags = os.O_RDWR | os.O_NOFOLLOW
                first = os.open(a, flags | os.O_CREAT | os.O_EXCL, 0o600)
                stack.callback(os.close, first)
                write_view(first, os.urandom(32))
                operations.append("exclusive_first_creation_returned_handle_held")
                stage = "second_reference"
                if number == 1:
                    os.rename(a, b)
                    operations.append("rename_returned_first_handle_held")
                    second = os.open(b, flags)
                elif number == 2:
                    second = os.open(b, flags | os.O_CREAT | os.O_EXCL, 0o600)
                    operations.append("exclusive_second_creation_returned")
                else:
                    shutil.copyfile(a, b)
                    operations.append("copyfile_returned")
                    second = os.open(b, flags)
                stack.callback(os.close, second)
                if number == 2:
                    write_view(second, os.urandom(32))
                stage = "paired_native_snapshot"
                for fd in (first, second):
                    fcntl.fcntl(fd, fcntl.F_GETFD)
                    if not stat.S_ISREG(os.fstat(fd).st_mode):
                        raise RuntimeError("regular_file_scope_failed_before_snapshot")
                refs = [native_reference(first), native_reference(second)]
                for fd in (first, second):
                    fcntl.fcntl(fd, fcntl.F_GETFD)
                    if not stat.S_ISREG(os.fstat(fd).st_mode):
                        raise RuntimeError("regular_file_scope_failed_after_snapshot")
                if not all(ref["regular_file"] is True for ref in refs):
                    raise RuntimeError("regular_file_scope_failed")
                save(out / "inputs" / f"T{number}.json",
                     row(number, "live_local_file_refs", {"scope": scope, "references": refs}))
                if number == 3:
                    stage = "reduced_content_views_before_reference_writes"
                    first_bytes, second_bytes = read_view(first), read_view(second)
                    save(out / "inputs" / "T5.json",
                         row(5, "content_equal", first_bytes == second_bytes))
                    save(out / "inputs" / "T6.json", row(6, "content_hash_pair", [
                        hashlib.sha256(first_bytes).hexdigest(),
                        hashlib.sha256(second_bytes).hexdigest()]))
                stage = "independent_io_reference"
                io_reference(first, second, journal)
                journal["operations"] = operations
                stage = "save_ground_truth_and_close"
                save(out / "ground-truth" / f"T{number}.json", journal)
        except Exception as exc:
            failure = {"case": f"T{number}", **error_record(
                exc, journal.get("stage", stage) if stage == "independent_io_reference" else stage)}
            failures.append(failure)
            if not (out / "inputs" / f"T{number}.json").exists():
                save(out / "inputs" / f"T{number}.json", [])
            if not (out / "ground-truth" / f"T{number}.json").exists():
                journal.update(truth="UNBEKANNT", reference_error=failure, operations=operations)
                save(out / "ground-truth" / f"T{number}.json", journal)
        finally:
            for path in (a, b):
                try:
                    path.unlink(missing_ok=True)
                except Exception as exc:
                    failures.append({"case": f"T{number}", **error_record(exc, "cleanup")})
    stage = "save_path_and_historical_controls"
    try:
        # Explicitly synthetic same relative path texts, not actual path identity.
        save(out / "inputs" / "T4.json", row(4, "path_pair", ["A", "A"]))
        baseline = Path(__file__).resolve().parents[1] / (
            "docs/observer-local-inode-reuse/2026-10-08/original/native-pairs.jsonl")
        with baseline.open() as handle:
            old = json.loads(handle.readline())
        reference = {"st_dev": old["st_dev"], "st_ino": old["st_ino"], "regular_file": True}
        historical = {**scope, "live_handle_overlap_confirmed": False}
        save(out / "inputs" / "T7.json", row(7, "live_local_file_refs",
             {"scope": historical, "references": [reference, dict(reference)]}))
    except Exception as exc:
        failures.append(error_record(exc, stage))
    remaining = [str(path.relative_to(out / "resources"))
                 for path in (out / "resources").rglob("*") if path.is_file()]
    save(out / "capture-status.json", {"cases_started": started, "failures": failures,
                                       "raw_contents_archived": False,
                                       "remaining_resource_files": remaining})
    # No GT values on stdout; stderr is kept opaque until the answer checkpoint.
    print(json.dumps({"cases_started": started, "errors": len(failures),
                      "remaining_resource_files": len(remaining)}))
    return int(bool(failures or remaining))


if __name__ == "__main__":
    raise SystemExit(main())
