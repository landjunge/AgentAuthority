"""Remove only this installation's finished synthetic regression/diagnostic data."""

import json
import os
import stat
import subprocess
from pathlib import Path

from research.debian_private.ipc import SECURE

BASE = Path("/var/lib/aa-private-install-20261017")


def main():
    final = json.loads((BASE / "completed-same-fresh-job.json").read_bytes())
    assert final["completed"] is True
    assert (SECURE / "collector/HARDSTOP").is_file()
    subprocess.run(
        [
            "systemctl",
            "stop",
            "aa-private-collector.socket",
            "aa-private-collector.service",
            "aa-private-runner.service",
            "aa-private-handoff-expire.timer",
        ],
        check=True,
    )
    active = subprocess.run(
        ["ps", "-u", "aa-check,aa-test-a,aa-test-b", "-o", "pid="],
        check=False,
        capture_output=True,
        text=True,
    )
    assert active.stdout.strip() == ""
    own_events = ["p_a4c_vfs_write_bcc_1097651", "r_vfs_write_bcc_1097651"]
    trace = Path("/sys/kernel/tracing/kprobe_events")
    initial = trace.read_text().splitlines()
    removed = []
    assert not Path("/proc/1097651").exists()
    for name in own_events:
        matched = [l for l in initial if l.split()[0].endswith("/" + name)]
        assert len(matched) <= 1
        if matched:
            assert matched[0].split()[1] == "vfs_write"
            fd = os.open(str(trace), os.O_WRONLY)
            try:
                os.write(fd, ("-:kprobes/" + name + "\n").encode())
            finally:
                os.close(fd)
            removed.append(name)
    assert all(n not in trace.read_text() for n in own_events)
    counts = {
        "files": 0,
        "directories": 0,
        "symlinks": 0,
        "other_test_nodes": 0,
        "logical_bytes": 0,
    }
    root = SECURE / "qualification"
    assert root.is_dir() and not root.is_symlink()
    for directory, dirs, files in os.walk(root, topdown=False, followlinks=False):
        for name in files + dirs:
            p = Path(directory) / name
            s = p.lstat()
            if stat.S_ISLNK(s.st_mode):
                counts["symlinks"] += 1
                p.unlink()
            elif stat.S_ISDIR(s.st_mode):
                counts["directories"] += 1
                p.rmdir()
            else:
                if stat.S_ISREG(s.st_mode):
                    counts["files"] += 1
                    counts["logical_bytes"] += s.st_size
                else:
                    counts["other_test_nodes"] += 1
                p.unlink()
    root.rmdir()
    counts["directories"] += 1
    names = [
        "runner/regression.json",
        "runner/regression-result.log",
        "runner/intake-repair.log",
        "runner/failure.json",
        "runner/intake-status.json",
        "runner/pending.json",
        "runner/result.json",
        "verifier/failure.json",
        "signer/failure.json",
        "collector/cap-stage.log",
        "collector/kernel-check-error.json",
        "collector/kernel-observer-error.log",
        "collector/last-failure.json",
        "registrar/received-report.json",
    ]
    for name in names:
        p = SECURE / name
        assert not p.is_symlink()
        p.unlink(missing_ok=True)
    assert list((SECURE / "verifier").iterdir()) == []
    assert list((SECURE / "verdicts").iterdir()) == []
    assert list((SECURE / "collector/tmp/compiler").iterdir()) == []
    assert not any((SECURE / "collector/tmp").glob("a4*"))
    # These fixed diagnostics have finished; no deletion of persistent core units.
    unit_names = [
        "aa-private-cap-profile.service",
        "aa-private-runner-regression.service",
        "aa-private-intake-repair.service",
    ]
    unit_archive = BASE / "retired-diagnostic-units"
    unit_archive.mkdir(mode=0o700, exist_ok=True)
    for n in unit_names:
        subprocess.run(["systemctl", "stop", n], check=True)
        p = Path("/etc/systemd/system") / n
        assert p.is_file() and not p.is_symlink()
        saved = unit_archive / n
        assert not saved.exists()
        saved.write_bytes(p.read_bytes())
        saved.chmod(0o600)
        p.unlink()
    p = Path("/opt/aa-private/research/debian_private/cap_stage.py")
    p.unlink(missing_ok=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    out = {
        "completed_job": final["job_id"],
        "regression_tree_removed": not root.exists(),
        "regression_inventory": counts,
        "retired_diagnostic_units": unit_names,
        "own_stale_probe_definitions_removed": removed,
        "probe_origin": "interrupted actor-ready-kernel-check; fixed source/probe name and dead own PID 1097651, no global tracefs flush",
        "test_uid_processes": 0,
        "raw_handoff_and_recipient_server_copy_absent": True,
        "collector_and_runner_stopped": True,
        "research_archives_and_production_data_untouched": True,
        "physical_erasure_claim": False,
    }
    (BASE / "test-cleanup.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out))


if __name__ == "__main__":
    main()
