"""Frozen V1-V7 validity study. No observer changes, trust repairs or reuse search."""
from __future__ import annotations

import argparse
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

from probes.local_file_identity_capture import error_record, io_reference, save, write_view
from probes.local_inode_reuse_capture import absent, closed_fd_check, own_target_fd_links


def check_handles(fds: list[int], checks: dict) -> None:
    checks.update(valid_descriptors=[], regular_files=[])
    for fd in fds:
        fcntl.fcntl(fd, fcntl.F_GETFD)
        checks["valid_descriptors"].append(True)
        regular = stat.S_ISREG(os.fstat(fd).st_mode)
        checks["regular_files"].append(regular)
        if not regular:
            raise RuntimeError("controlled_regular_file_check_failed")


def collect_pair(fds: list[int], book: dict, packet: str) -> list[dict]:
    entry = {"packet": packet, "before": {}, "after": {}, "complete": False}
    book["native_pair_snapshots"].append(entry)
    check_handles(fds, entry["before"])
    refs = []
    for fd in fds:
        measured = os.fstat(fd)
        refs.append({"st_dev": measured.st_dev, "st_ino": measured.st_ino,
                     "regular_file": stat.S_ISREG(measured.st_mode)})
    check_handles(fds, entry["after"])
    entry["complete"] = True
    return [{"run": 1, "kind": "live_local_file_refs", "value": {
        "scope": {"os": "Linux", "filesystem": "tmpfs", "same_collection_process": True,
                  "live_handle_overlap_confirmed": True}, "references": refs}}]


def invoke(out: Path, packet: str, book: dict, fds: list[int] | None = None) -> None:
    entry = {"packet": packet, "before": {}, "after": {},
             "live_checked_for_invocation": fds is not None,
             "native_snapshot_count_before": len(book["native_pair_snapshots"]),
             "native_snapshot_count_after": None, "answer_saved_sha256": None}
    book["invocations"].append(entry)
    if fds is not None:
        check_handles(fds, entry["before"])
    command = [sys.executable, "-m", "probes.local_evidence_validity_responses",
               "--input", str(out / "inputs" / f"{packet}.json"),
               "--out", str(out / "responses" / packet)]
    # Resource descriptors are non-inheritable; no lifecycle data or oracle is
    # passed. The parent continuously retains both handles across the child.
    process = subprocess.run(command, close_fds=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=20)
    entry.update(process_exit=process.returncode, stdout_bytes=len(process.stdout),
                 stderr_bytes=len(process.stderr))
    streams = out / "response-processes"
    streams.mkdir(exist_ok=True)
    (streams / f"{packet}.stdout.log").write_bytes(process.stdout)
    (streams / f"{packet}.stderr.log").write_bytes(process.stderr)
    if fds is not None:
        check_handles(fds, entry["after"])
    if process.returncode:
        raise RuntimeError("observer_response_process_failed")
    # Read only opaque bytes here, not answer semantics and never a GT comparison.
    answer = out / "responses" / packet / "answer.json"
    entry["answer_saved_sha256"] = hashlib.sha256(answer.read_bytes()).hexdigest()
    entry["native_snapshot_count_after"] = len(book["native_pair_snapshots"])


def release_owned(fds: list[int], paths: list[Path], active: list[int], journal: dict) -> None:
    journal.update(closed_handles=[], removed_paths=[], complete=False)
    for fd in fds:
        entry = {"close_returned": False, "closed_fd_is_ebadf": False}
        journal["closed_handles"].append(entry)
        journal["stage"] = "close_then_immediate_ebadf"
        os.close(fd)
        active.remove(fd)
        entry["close_returned"] = True
        closed_fd_check(fd)
        entry["closed_fd_is_ebadf"] = True
    for path in paths:
        entry = {"unlink_returned": False, "path_absent": False, "own_target_fd_links": None}
        journal["removed_paths"].append(entry)
        journal["stage"] = "unlink_then_absence_and_own_link_check"
        os.unlink(path)
        entry["unlink_returned"] = True
        entry["path_absent"] = absent(path)
        entry["own_target_fd_links"] = own_target_fd_links(path)
        if not entry["path_absent"] or entry["own_target_fd_links"] != 0:
            raise RuntimeError("controlled_release_not_confirmed")
    journal.update(complete=True, stage="complete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    out = parser.parse_args().out.resolve()
    if out != Path("/tmp/aa-local-evidence-validity-20261008"):
        raise ValueError("only_frozen_new_private_tmp_directory")
    out.mkdir(mode=0o700, exist_ok=False)
    resources = out / "resources"
    resources.mkdir(mode=0o700)
    active, failures, cleanup_errors = [], [], []
    book = {"native_pair_snapshots": [], "invocations": [], "releases": {},
            "replay": {}, "synthetic": {}}
    stage = "system_scope"
    io = {}
    try:
        types = set(subprocess.check_output(
            ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True).split())
        if os.uname().sysname != "Linux" or types != {"tmpfs"}:
            raise RuntimeError("frozen_linux_tmpfs_scope_mismatch")
        save(out / "system.json", {"os": "Linux", "kernel": os.uname().release,
                                   "filesystem": "tmpfs", "python": sys.version.split()[0]})
        flags = os.O_RDWR | os.O_NOFOLLOW
        stage = "V1_create_and_open_twice"
        same = resources / "same"
        first = os.open(same, flags | os.O_CREAT | os.O_EXCL, 0o600)
        active.append(first)
        write_view(first, os.urandom(32))
        second = os.open(same, flags)
        active.append(second)
        fds = [first, second]
        stage = "V1_native_snapshot"
        source = collect_pair(fds, book, "P1")
        save(out / "inputs" / "P1.json", source)
        stage = "V1_live_response"
        invoke(out, "P1", book, fds)
        for packet in ("P4", "P6", "P7"):
            stage = packet + "_reduced_live_view_and_response"
            reduced = deepcopy(source)
            if packet == "P4":
                del reduced[0]["value"]["scope"]["same_collection_process"]
                del reduced[0]["value"]["scope"]["live_handle_overlap_confirmed"]
            elif packet == "P6":
                del reduced[0]["value"]["references"][0]["st_dev"]
            else:
                del reduced[0]["value"]["references"][1]["regular_file"]
            save(out / "inputs" / f"{packet}.json", reduced)
            invoke(out, packet, book, fds)
        stage = "V1_independent_io_reference"
        io["V1"] = {}
        io_reference(first, second, io["V1"])
        stage = "V1_complete_operational_release"
        book["releases"]["V1"] = {}
        release_owned(fds, [same], active, book["releases"]["V1"])
        stage = "V3_unchanged_replay_after_release"
        old_path = out / "inputs" / "P1.json"
        replay_path = out / "inputs" / "P3.json"
        shutil.copyfile(old_path, replay_path)
        replay_path.chmod(0o444)
        book["replay"] = {"old_packet": "P1", "replayed_packet": "P3",
                          "old_sha256": hashlib.sha256(old_path.read_bytes()).hexdigest(),
                          "replay_sha256": hashlib.sha256(replay_path.read_bytes()).hexdigest(),
                          "original_query_run": 1, "replay_query_run": 1,
                          "prior_release_complete": book["releases"]["V1"]["complete"]}
        invoke(out, "P3", book)
        stage = "V2_create_two_files"
        a, b = resources / "first", resources / "second"
        first = os.open(a, flags | os.O_CREAT | os.O_EXCL, 0o600)
        active.append(first)
        write_view(first, os.urandom(32))
        second = os.open(b, flags | os.O_CREAT | os.O_EXCL, 0o600)
        active.append(second)
        write_view(second, os.urandom(32))
        fds = [first, second]
        stage = "V2_native_snapshot_and_live_response"
        save(out / "inputs" / "P2.json", collect_pair(fds, book, "P2"))
        invoke(out, "P2", book, fds)
        stage = "V2_independent_io_reference"
        io["V2"] = {}
        io_reference(first, second, io["V2"])
        stage = "V2_complete_operational_release"
        book["releases"]["V2"] = {}
        release_owned(fds, [a, b], active, book["releases"]["V2"])
        stage = "V5_synthetic_unchecked_claim"
        # Independently hand-built primitives: no native measurement or copied
        # earlier live record. Provenance stays only in the separate GT journal.
        ref = {"st_dev": 123, "st_ino": 456, "regular_file": True}
        synthetic = [{"run": 1, "kind": "live_local_file_refs", "value": {
            "scope": {"os": "Linux", "filesystem": "tmpfs", "same_collection_process": True,
                      "live_handle_overlap_confirmed": True},
            "references": [ref, dict(ref)]}}]
        save(out / "inputs" / "P5.json", synthetic)
        book["synthetic"] = {"packet": "P5", "source": "handcrafted_unchecked_primitives",
                             "native_collector_called_for_packet": False,
                             "actual_resource_handles_for_packet": 0}
        invoke(out, "P5", book)
    except Exception as exc:
        reference_stage = io.get("V1" if stage.startswith("V1") else "V2", {}).get("stage", stage)
        failures.append(error_record(exc, reference_stage if "io_reference" in stage else stage))
    finally:
        for fd in list(active):
            try:
                os.close(fd)
                active.remove(fd)
            except Exception as exc:
                cleanup_errors.append(error_record(exc, "cleanup_handle"))
        for path in resources.iterdir():
            try:
                path.unlink()
            except Exception as exc:
                cleanup_errors.append(error_record(exc, "cleanup_resource_file"))
    # Originals include partial records on failure; never rerun or replace them.
    save(out / "ground-truth" / "collector-lifecycle.json", book)
    for name, reference in io.items():
        save(out / "ground-truth" / f"{name}-io.json", reference)
    remaining = [p.name for p in resources.iterdir() if p.is_file()]
    save(out / "capture-status.json", {"invocations_started": len(book["invocations"]),
                                       "failures": failures, "cleanup_errors": cleanup_errors,
                                       "remaining_resource_files": remaining,
                                       "raw_contents_archived": False})
    print(json.dumps({"invocations_started": len(book["invocations"]),
                      "errors": len(failures), "cleanup_errors": len(cleanup_errors),
                      "remaining_resource_files": len(remaining)}))
    return int(bool(failures or cleanup_errors or remaining))


if __name__ == "__main__":
    raise SystemExit(main())
