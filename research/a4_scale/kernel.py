"""Same corrected VFS instrumentation, scoped to at most 100 held test objects."""

import argparse
import ctypes
import hashlib
import json
import os
import platform
import resource
import stat
import time
from pathlib import Path

from observer import PROGRAM, emit

from probes import attach_classic, misses, profile, program_info


def run(manifest, stop):
    from bcc import BPF

    paths = json.loads(Path(manifest).read_text())
    if os.geteuid() != 0 or len(paths) != 100 or len(set(paths)) != 100:
        raise ValueError("exactly100 artificial objects inside own research VM")
    before = resource.getrusage(resource.RUSAGE_SELF)
    fds, objects = [], []
    bpf = None
    try:
        for path in paths:
            if not path.startswith("/var/tmp/a1-research-a4-scale-"):
                raise ValueError("outside artificial scope")
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
            fds.append(fd)
            item = os.fstat(fd)
            if not stat.S_ISREG(item.st_mode):
                raise ValueError("regular held objects only")
            objects.append(
                {"inode": item.st_ino, "dev": (os.major(item.st_dev) << 20) | os.minor(item.st_dev)}
            )
        text = PROGRAM.replace(
            "BPF_PERF_OUTPUT(events);",
            "struct object { u64 inode; u32 dev; u32 pad; };\nBPF_HASH(targets, struct object, u8, 128);\nBPF_PERF_OUTPUT(events);",
        )
        text = text.replace(
            "if (ino != TARGET_INODE || dev != TARGET_DEV) return 0;",
            "struct object object = {}; object.inode = ino; object.dev = dev; if (!targets.lookup(&object)) return 0;",
        )
        bpf = BPF(text=text)
        for item in objects:
            key = bpf["targets"].Key()
            key.inode, key.dev = item["inode"], item["dev"]
            bpf["targets"][key] = ctypes.c_ubyte(1)
        entry = attach_classic(bpf, "vfs_write", "enter")
        bpf.attach_kretprobe(event="vfs_write", fn_name="leave", maxactive=128)
        boot = hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes()).hexdigest()
        counts = {"lost": 0, "bytes": 0, "records": 0}

        def callback(cpu, data, size):
            event = bpf["events"].event(data)
            row = {
                k: int(getattr(event, k))
                for k in [
                    "inode",
                    "start_ns",
                    "entry_ns",
                    "exit_ns",
                    "count",
                    "result",
                    "dev",
                    "tgid",
                    "tid",
                    "ppid",
                    "kind",
                ]
            }
            row.update(boot_hash=boot, cpu=cpu, raw_bytes=size)
            counts["records"] += 1
            counts["bytes"] += size
            emit({"record": row})

        def lost(cpu, count):
            counts["lost"] += count
            emit({"lost": count, "cpu": cpu})

        bpf["events"].open_perf_buffer(callback, page_cnt=128, lost_cb=lost)
        emit(
            {
                "ready": True,
                "ready_ns": time.monotonic_ns(),
                "kernel": platform.release(),
                "boot_hash": boot,
                "pid_namespace": os.readlink("/proc/self/ns/pid"),
                "files": objects,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "program_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "actor_or_oracle_supplied": False,
            }
        )
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline and not Path(stop).exists():
            bpf.perf_buffer_poll(timeout=50)
        stop_seen = Path(stop).exists()
        drain = time.monotonic() + 1
        while time.monotonic() < drain:
            bpf.perf_buffer_poll(timeout=50)
        snapshot = profile([entry, "r_vfs_write_bcc_" + str(os.getpid())])
        stats = {
            str(key.value): sum(int(v) for v in values) for key, values in bpf["stats"].items()
        }
        after = resource.getrusage(resource.RUSAGE_SELF)
        emit(
            {
                "summary": {
                    "stats": stats,
                    "pending": len(bpf["pending"]),
                    "perf_lost": counts["lost"],
                    "raw_bytes": counts["bytes"],
                    "records": counts["records"],
                    "classic_profile": snapshot,
                    "entry_nmissed": misses(snapshot, entry),
                    "program_info": program_info(bpf),
                    "stop_seen": stop_seen,
                    "end_ns": time.monotonic_ns(),
                    "cpu_user_seconds": after.ru_utime - before.ru_utime,
                    "cpu_system_seconds": after.ru_stime - before.ru_stime,
                    "rss_peak_bytes": after.ru_maxrss * 1024,
                    "scope": "observer including compile; not whole VM/kernel",
                }
            }
        )
    finally:
        if bpf is not None:
            bpf.cleanup()
        for fd in fds:
            os.close(fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("stop")
    args = parser.parse_args()
    run(args.manifest, args.stop)
