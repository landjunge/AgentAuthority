"""One current local invocation and a delegating, in-memory test journal."""
from __future__ import annotations

import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

from observer_research import infer_current_local_file_identity
from probes.local_file_identity_capture import save


def observe(events: list[dict], handles: list[int] | None, journal: list[dict]) -> dict:
    """No case, expected answer or GT input; originals always execute unchanged."""
    originals = [(fcntl, "fcntl", fcntl.fcntl), (os, "fstat", os.fstat),
                 (os, "uname", os.uname), (os, "stat", os.stat),
                 (subprocess, "run", subprocess.run)]

    def wrap(name, original):
        def delegated(*args, **kwargs):
            entry = {"operation": name, "attempted": True, "returned": False}
            if name in ("fcntl", "fstat"):
                entry["handle_index"] = (handles.index(args[0]) + 1
                                         if handles is not None and args[0] in handles else None)
            if name == "fcntl":
                entry["is_f_getfd"] = args[1] == fcntl.F_GETFD
            if name == "stat":
                entry["is_tmp_context"] = args[0] == "/tmp"
            if name == "run":
                entry["is_fixed_findmnt"] = args[0] == [
                    "findmnt", "-T", "/tmp", "-n", "-o", "FSTYPE"]
            journal.append(entry)
            try:
                result = original(*args, **kwargs)
            except Exception as exc:
                entry["error"] = {"type": type(exc).__name__,
                                  "errno": getattr(exc, "errno", None)}
                raise
            entry["returned"] = True
            if name == "fcntl":
                entry["descriptor_flags"] = result  # Zero is successful too.
            elif name == "fstat":
                entry["native_pair"] = [result.st_dev, result.st_ino]
                entry["regular"] = stat.S_ISREG(result.st_mode)
            elif name == "uname":
                entry["system"] = result.sysname
            elif name == "stat":
                entry["device"] = result.st_dev
            elif name == "run":
                entry["exit_code"] = result.returncode
                entry["filesystem_types"] = sorted(set(result.stdout.split()))
            return result
        return delegated

    try:
        for module, name, original in originals:
            setattr(module, name, wrap(name, original))
        return infer_current_local_file_identity(events, 1, handles=handles)
    finally:
        for module, name, original in originals:
            setattr(module, name, original)


def respond(raw_input: bytes, out: Path, handles: list[int] | None,
            journal: list[dict]) -> str:
    # All parsing/wrapping before the first native check is memory-only. Needed
    # for F5/F6: no file opens may reallocate their closed numeric descriptors.
    answer = observe(json.loads(raw_input), handles, journal)
    out.mkdir(parents=True, exist_ok=False)
    path = out / "answer.json"
    save(path, {"input_sha256": hashlib.sha256(raw_input).hexdigest(),
                "query_run": 1, "raw_observer_abcd": answer})
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    save(out / "sealed-sha256.json", {"answer_sha256": digest,
                                       "saved_before_ground_truth_comparison": True})
    return digest
