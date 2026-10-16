"""Real restricted collector load/attach/counters/detach; zero actor writes."""

import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

from research.private_service.protocol import require

ROOT = Path(__file__).resolve().parents[2]


def run():
    path = Path("/var/tmp/a1-research-a4-" + secrets.token_hex(16))
    path.mkdir(mode=0o711)
    path.chmod(0o711)
    target = path / "target"
    target.touch(mode=0o600)
    os.chown(target, 61102, 61102)
    names = []
    try:
        child = subprocess.Popen(
            [
                "/usr/bin/python3",
                "-B",
                "-c",
                "import os,time;print(os.getuid(),flush=True);time.sleep(3)",
            ],
            user=61102,
            group=61102,
            extra_groups=[],
            stdout=subprocess.PIPE,
        )
        try:
            require(child.stdout.readline().strip() == b"61102", 503, "TEST_UID_NOT_READY")
            # The unchanged A4 oracle needs only the controlled child's stat.
            require(Path(f"/proc/{child.pid}/stat").is_file(), 503, "OWN_TEST_CHILD_PROC_HIDDEN")
            Path(f"/proc/{child.pid}/stat").read_text()
        finally:
            child.terminate()
            child.wait(timeout=5)
        access = []
        for actor, expected in ((61101, False), (61102, True)):
            code = (
                "import os,errno,sys,runpy\nfrom pathlib import Path\n"
                "sys.path.insert(0,'/opt/aa-private/research/a4_completion')\n"
                "runpy.run_path('/opt/aa-private/research/a4_completion/agent.py',run_name='import_only_no_action')\n"
                "assert all(int(l.split()[1],16)==0 for l in Path('/proc/self/status').read_text().splitlines() if l.startswith(('CapEff:','CapPrm:','CapAmb:','CapInh:')))\ntry:f=os.open("
                + repr(str(target))
                + ",os.O_WRONLY|os.O_NOFOLLOW);os.close(f);ok=True\nexcept OSError as e:ok=False if e.errno==errno.EACCES else None\nprint(os.getuid(),ok)\nraise SystemExit(0 if ok=="
                + repr(expected)
                + " else 1)"
            )
            p = subprocess.run(
                ["/usr/bin/python3", "-B", "-c", code],
                user=actor,
                group=actor,
                extra_groups=[],
                capture_output=True,
                timeout=5,
                check=False,
            )
            require(p.returncode == 0, 503, "TEST_UID_OR_TARGET_ISOLATION_FAILED")
            access.append({"uid": actor, "open_without_write": expected})
        observed = subprocess.run(
            [
                "/usr/bin/python3",
                "-B",
                "-m",
                "research.debian_private.collector_observer",
                str(target),
            ],
            capture_output=True,
            timeout=75,
            check=False,
        )
        if observed.returncode:
            from research.debian_private.ipc import SECURE

            (SECURE / "collector/kernel-observer-error.log").write_bytes(observed.stderr[:16000])
        require(observed.returncode == 0, 503, "RESTRICTED_OBSERVER_FAILED")
        rows = [json.loads(l) for l in observed.stdout.splitlines()]
        ready = next(r for r in rows if r.get("ready"))
        summary = next(r["summary"] for r in rows if "summary" in r)
        sys.path.insert(0, str(ROOT / "research/a4_completion"))
        import lifecycle

        from research.debian_private.probe_profile import profile

        lifecycle.profile = profile
        relative = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
        require(relative.endswith("/aa-private-collector.service"), 503, "COLLECTOR_CGROUP")
        cg = os.stat("/sys/fs/cgroup" + relative).st_ino
        marker = "int forked(struct pt_regs *ctx, struct task_struct *child) {"
        original = lifecycle.PROGRAM
        lifecycle.PROGRAM = original.replace(
            marker, marker + "\n if (bpf_get_current_cgroup_id() != " + str(cg) + "ULL) return 0;\n"
        )
        try:
            life = lifecycle.Lifecycle()
            ending = life.finish()
        finally:
            lifecycle.PROGRAM = original
        programs = {
            **summary["program_info"],
            **{"life_" + k: v for k, v in ending["program_info"].items()},
        }
        names = list(summary["classic_profile"]["selected"]) + list(
            ending["classic_profile"]["selected"]
        )
        raw = Path("/sys/kernel/tracing/kprobe_events").read_text()
        require(
            len(programs) == 6 and all(p["recursion_misses"] == 0 for p in programs.values()),
            503,
            "PROGRAM_RECURSION_UNKNOWN",
        )
        require(
            summary["classic_profile"]["complete"]
            and ending["classic_profile"]["complete"]
            and all(n not in raw for n in names),
            503,
            "PROFILE_OR_DETACH_FAILED",
        )
        require(
            all(int(v) == 0 for v in summary["stats"].values())
            and summary["perf_lost"] == 0
            and ending["perf_lost"] == 0,
            503,
            "IDLE_LOSS_OR_FOREIGN_CAPTURE",
        )
        require(summary["records"] == 0 and ending["records"] == [], 503, "FOREIGN_RECORD")
        result = {
            "kernel": ready["kernel"],
            "cgroup_id": cg,
            "uid_filter": 61102,
            "load_attach_programs": 6,
            "recursion_misses": {k: v["recursion_misses"] for k, v in programs.items()},
            "own_classic_probes_detached": True,
            "actor_writes": 0,
            "idle_foreign_records": 0,
            "scope": "real restricted service, prerequisite only",
            "uid_target_access": access,
        }
        return result
    finally:
        target.unlink()
        path.rmdir()
