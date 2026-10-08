"""One fixed, sequential /tmp inode-reuse study; no product/resource sensor."""
from __future__ import annotations

import argparse
import errno
import fcntl
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

MAX_NEW_LIFETIMES = 10_000
FOLDER = Path("/tmp/aa-local-inode-reuse-20261008")


def save(path: Path, value: dict | list, *, lines: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        if lines:
            for row in value:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
        else:
            json.dump(value, handle, indent=2)
            handle.write("\n")
    path.chmod(0o444)


def failure(exc: Exception, stage: str) -> dict:
    return {"stage": stage, "type": type(exc).__name__, "message": str(exc),
            "errno": getattr(exc, "errno", None)}


def closed_fd_check(fd: int) -> None:
    # Call immediately after close, before anything can allocate another FD.
    try:
        fcntl.fcntl(fd, fcntl.F_GETFD)
    except OSError as exc:
        if exc.errno == errno.EBADF:
            return
        raise
    raise RuntimeError("closed_descriptor_still_valid")


def own_target_fd_links(path: Path) -> int:
    target = str(path)
    matches = 0
    # Never open/fstat a proc FD target; never persist other FD target paths.
    with os.scandir("/proc/self/fd") as entries:
        for entry in entries:
            link = os.readlink(entry.path)
            if link in (target, target + " (deleted)"):
                matches += 1
    return matches


def absent(path: Path) -> bool:
    try:
        os.lstat(path)
    except FileNotFoundError:
        return True
    return False


def release(fd: int, path: Path, journal: dict) -> None:
    """Operational lifecycle evidence; no native identity comparison."""
    journal["stage"] = "close"
    journal["close_attempted"] = True
    os.close(fd)
    journal["close_returned"] = True
    journal["stage"] = "immediate_closed_descriptor_check"
    closed_fd_check(fd)
    journal["closed_fd_is_ebadf"] = True
    journal["stage"] = "unlink"
    os.unlink(path)
    journal["unlink_returned"] = True
    journal["stage"] = "confirm_path_absence"
    journal["path_absent_after_unlink"] = absent(path)
    if not journal["path_absent_after_unlink"]:
        raise RuntimeError("test_path_still_present_after_unlink")
    journal["stage"] = "own_target_fd_link_scan"
    journal["own_target_fd_links_after_release"] = own_target_fd_links(path)
    if journal["own_target_fd_links_after_release"] != 0:
        raise RuntimeError("own_test_resource_handle_still_present")
    journal["release_complete"] = True
    journal["stage"] = "complete"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out != FOLDER:
        raise ValueError("only_the_frozen_private_tmp_folder")
    try:
        out.mkdir(mode=0o700, exist_ok=False)
    except Exception as exc:
        print(json.dumps({"measurement_error": failure(exc, "exclusive_private_folder"),
                          "new_lifetimes_created": 0}), file=sys.stderr)
        raise SystemExit(1)
    path = out / "resources" / "file"
    pairs, lifetimes, errors, cleanup_errors = [], [], [], []
    active_fd, journal = None, {}
    system = {"os": os.uname().sysname, "kernel": os.uname().release,
              "python": sys.version.split()[0], "filesystem": None}
    hit_attempt, stop_reason, stage = None, "measurement_error", "private_resource_folder"
    cleanup = {}
    try:
        path.parent.mkdir(mode=0o700)
        stage = "system_scope"
        kinds = set(subprocess.check_output(
            ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True).split())
        system["filesystem"] = "tmpfs" if kinds == {"tmpfs"} else sorted(kinds)
        if system["os"] != "Linux" or kinds != {"tmpfs"}:
            raise RuntimeError("frozen_linux_tmpfs_scope_mismatch")
        previous_release = None
        for attempt in range(MAX_NEW_LIFETIMES + 1):
            journal = {"attempt": attempt,
                       "previous_release_confirmed_before_create": previous_release,
                       "exclusive_create_returned": False, "release_complete": False,
                       "stage": "exclusive_create"}
            lifetimes.append(journal)
            if attempt and previous_release is not True:
                raise RuntimeError("previous_release_not_confirmed")
            active_fd = os.open(path, os.O_RDONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            journal["exclusive_create_returned"] = True
            journal["stage"] = "native_fstat"
            native = os.fstat(active_fd)
            journal["regular_file"] = stat.S_ISREG(native.st_mode)
            if not journal["regular_file"]:
                raise RuntimeError("not_a_regular_test_file")
            pairs.append({"st_dev": native.st_dev, "st_ino": native.st_ino})
            match = attempt > 0 and pairs[-1] == pairs[0]
            if match:
                hit_attempt = attempt
            release(active_fd, path, journal)
            active_fd = None
            previous_release = journal["release_complete"]
            if match:
                stop_reason = "first_native_pair_recurrence"
                break
        else:
            stop_reason = "maximum_reached_without_native_pair_recurrence"
    except Exception as exc:
        entry = failure(exc, journal.get("stage", stage))
        errors.append(entry)
        if journal:
            journal["error"] = entry
    finally:
        # Cleanup does not turn a failed lifecycle into a successful reference.
        if active_fd is not None and not journal.get("close_attempted", False):
            try:
                os.close(active_fd)
                closed_fd_check(active_fd)
                cleanup["remaining_owned_descriptor_closed_and_ebadf"] = True
            except Exception as exc:
                cleanup_errors.append(failure(exc, "cleanup_owned_descriptor"))
        elif active_fd is not None:
            cleanup["prior_close_attempt_not_retried"] = True
        try:
            if not absent(path):
                os.unlink(path)
                cleanup["remaining_test_path_unlinked"] = True
            cleanup["test_file_absent"] = absent(path)
            cleanup["own_target_fd_links_after_final_cleanup"] = own_target_fd_links(path)
        except Exception as exc:
            cleanup_errors.append(failure(exc, "cleanup_path_or_fd_scan"))
    status = {"maximum_new_lifetimes": MAX_NEW_LIFETIMES,
              "baseline_created": bool(lifetimes and lifetimes[0]["exclusive_create_returned"]),
              "new_lifetimes_created": sum(row["exclusive_create_returned"]
                                           for row in lifetimes if row["attempt"] > 0),
              "new_native_pairs_recorded": max(0, len(pairs) - 1),
              "native_match_attempt": hit_attempt, "stop_reason": stop_reason,
              "measurement_errors": errors, "cleanup_errors": cleanup_errors,
              "cleanup": cleanup, "raw_contents_archived": False}
    # No artifact files were created and no payloads read/written in the loop.
    artifacts = [
        ("original/native-pairs.jsonl", pairs, True),
        ("original/identity-scope.json", {"os": system["os"],
          "filesystem": system["filesystem"], "maximum_new_lifetimes": MAX_NEW_LIFETIMES}, False),
        ("ground-truth/lifetimes.jsonl", lifetimes, True),
        ("system.json", system, False), ("capture-status.json", status, False)]
    for name, value, lines in artifacts:
        try:
            save(out / name, value, lines=lines)
        except Exception as exc:
            # Preserve actual in-memory originals without retrying the failed save.
            print(json.dumps({"archive_error": failure(exc, "archive_" + name),
                              "original_native_pairs": pairs,
                              "ground_truth_lifetimes": lifetimes,
                              "capture_status": status}), file=sys.stderr)
            raise SystemExit(1)
    print(json.dumps({"new_lifetimes_created": status["new_lifetimes_created"],
                      "measurement_errors": len(errors), "cleanup_errors": len(cleanup_errors)}))


if __name__ == "__main__":
    main()
