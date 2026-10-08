"""The frozen F1-F7 experiment; one run, no extra resources or replay search."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from probes.current_local_collector_responses import respond
from probes.local_evidence_validity_capture import collect_pair, release_owned
from probes.local_file_identity_capture import error_record, io_reference, save, write_view
from probes.local_inode_reuse_capture import absent, closed_fd_check, own_target_fd_links

FOLDER = Path("/tmp/aa-current-local-collector-20261008")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out != FOLDER:
        raise ValueError("only_frozen_new_private_tmp_directory")
    out.mkdir(mode=0o700, exist_ok=False)
    resources = out / "resources"
    resources.mkdir(mode=0o700)
    active, failures, cleanup_errors, io = [], [], [], {}
    book = {"native_pair_snapshots": [], "invocations": [], "releases": {},
            "replay": {}, "synthetic": {}, "closed_before_check": {}}
    stage = "system_scope"

    def packet(name: str, value: list[dict]) -> bytes:
        path = out / "inputs" / f"{name}.json"
        save(path, value)
        return path.read_bytes()

    def invoke(name: str, raw: bytes, fds: list[int] | None = None) -> None:
        entry = {"packet": name, "runtime_handles_supplied": fds is not None,
                 "native_calls": [], "answer_saved_sha256": None,
                 "native_snapshot_count_before": len(book["native_pair_snapshots"])}
        book["invocations"].append(entry)
        entry["answer_saved_sha256"] = respond(
            raw, out / "responses" / name, fds, entry["native_calls"])
        entry["native_snapshot_count_after"] = len(book["native_pair_snapshots"])

    def create_pair(label: str, same: bool) -> tuple[list[int], list[Path]]:
        flags = os.O_RDWR | os.O_NOFOLLOW
        paths = [resources / f"{label}-first"]
        first = os.open(paths[0], flags | os.O_CREAT | os.O_EXCL, 0o600)
        active.append(first)
        write_view(first, os.urandom(32))
        if same:
            second = os.open(paths[0], flags)
        else:
            paths.append(resources / f"{label}-second")
            second = os.open(paths[1], flags | os.O_CREAT | os.O_EXCL, 0o600)
        active.append(second)
        if not same:
            write_view(second, os.urandom(32))
        return [first, second], paths

    def reference_then_release(name: str, fds: list[int], paths: list[Path]) -> None:
        nonlocal stage
        stage = name + "_independent_io_reference"
        io[name] = {}
        io_reference(*fds, io[name])
        stage = name + "_complete_operational_release"
        book["releases"][name] = {}
        release_owned(fds, paths, active, book["releases"][name])

    try:
        types = set(subprocess.check_output(
            ["findmnt", "-T", str(out), "-n", "-o", "FSTYPE"], text=True).split())
        if os.uname().sysname != "Linux" or types != {"tmpfs"}:
            raise RuntimeError("frozen_linux_tmpfs_scope_mismatch")
        save(out / "system.json", {"os": "Linux", "kernel": os.uname().release,
                                   "filesystem": "tmpfs", "python": sys.version.split()[0]})
        stage = "F1_create_measure_and_current_response"
        fds, paths = create_pair("F1", True)
        raw = packet("P1", collect_pair(fds, book, "P1"))
        invoke("P1", raw, fds)
        reference_then_release("F1", fds, paths)
        stage = "F3_byte_equal_replay_without_current_handles"
        # Persist exact replay bytes, rather than reserializing a modified run.
        replay = out / "inputs" / "P3.json"
        replay.parent.mkdir(exist_ok=True)
        with replay.open("xb") as handle:
            handle.write(raw)
        replay.chmod(0o444)
        book["replay"] = {"source_packet": "P1", "replayed_packets": ["P3", "P5"],
                          "source_sha256": hashlib.sha256(raw).hexdigest(),
                          "release_before_replay_complete": book["releases"]["F1"]["complete"]}
        invoke("P3", raw)
        stage = "F5_replay_with_closed_old_descriptors"
        old = out / "inputs" / "P5.json"
        with old.open("xb") as handle:
            handle.write(raw)
        old.chmod(0o444)
        # These file operations ended with close. The observer itself performs
        # F_GETFD before allocating any findmnt pipes. No fresh flags inserted.
        invoke("P5", raw, fds)
        stage = "F4_handcrafted_without_collector"
        ref = {"st_dev": 123, "st_ino": 456, "regular_file": True}
        synthetic = [{"run": 1, "kind": "live_local_file_refs", "value": {
            "scope": {"os": "Linux", "filesystem": "tmpfs",
                      "same_collection_process": True, "live_handle_overlap_confirmed": True},
            "references": [ref, dict(ref)]}}]
        raw = packet("P4", synthetic)
        book["synthetic"] = {"packet": "P4", "source": "handcrafted_primitives",
                             "actual_resource_handles": 0}
        invoke("P4", raw)
        stage = "F2_create_measure_and_current_response"
        fds, paths = create_pair("F2", False)
        raw = packet("P2", collect_pair(fds, book, "P2"))
        invoke("P2", raw, fds)
        reference_then_release("F2", fds, paths)
        stage = "F6_prepare_then_close_immediately_before_check"
        fds, paths = create_pair("F6", True)
        raw = packet("P6", collect_pair(fds, book, "P6"))
        closed = {"close_checks": []}
        book["closed_before_check"]["F6"] = closed
        for fd in fds:
            entry = {"close_returned": False, "immediate_ebadf": False}
            closed["close_checks"].append(entry)
            os.close(fd)
            active.remove(fd)
            entry["close_returned"] = True
            closed_fd_check(fd)
            entry["immediate_ebadf"] = True
        invoke("P6", raw, fds)
        book["releases"]["F6"] = {"removed_paths": [], "complete": False}
        for path in paths:
            os.unlink(path)
            entry = {"unlink_returned": True, "path_absent": absent(path),
                     "own_target_fd_links": own_target_fd_links(path)}
            book["releases"]["F6"]["removed_paths"].append(entry)
            if not entry["path_absent"] or entry["own_target_fd_links"] != 0:
                raise RuntimeError("controlled_F6_release_not_confirmed")
        book["releases"]["F6"]["complete"] = True
        stage = "F7_create_measure_and_current_response"
        fds, paths = create_pair("F7", False)
        raw = packet("P7", collect_pair(fds, book, "P7"))
        invoke("P7", raw, fds)
        reference_then_release("F7", fds, paths)
    except Exception as exc:
        failures.append(error_record(exc, stage))
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
