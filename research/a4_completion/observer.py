"""Independent guest-only VFS observer. Receives file scope, never actor/oracle."""

import argparse
import hashlib
import json
import os
import platform
import resource
import time
from pathlib import Path

from probes import attach_classic, misses, profile, program_info

PROGRAM = r"""
#include <uapi/linux/ptrace.h>
#include <linux/fs.h>
#include <linux/sched.h>

struct event {
    u64 inode, start_ns, entry_ns, exit_ns, count;
    s64 result;
    u32 dev, tgid, tid, ppid, kind;
};
BPF_HASH(pending, u64, struct event, 256);
BPF_HASH(seen, u32, u64, 256);
BPF_PERCPU_ARRAY(stats, u64, 12);
BPF_PERF_OUTPUT(events);

static void inc(u32 key) {
    u64 *v = stats.lookup(&key);
    if (v) (*v)++;
}

int enter(struct pt_regs *ctx, struct file *file) {
    struct inode *inode = NULL;
    struct super_block *sb = NULL;
    u64 ino = 0; u32 dev = 0;
    if (bpf_probe_read_kernel(&inode, sizeof(inode), &file->f_inode)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&ino, sizeof(ino), &inode->i_ino)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&sb, sizeof(sb), &inode->i_sb)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&dev, sizeof(dev), &sb->s_dev)) { inc(9); return 0; }
    if (ino != TARGET_INODE || dev != TARGET_DEV) return 0;
    inc(0);
    u64 id = bpf_get_current_pid_tgid();
    struct event e = {};
    e.inode = ino; e.dev = dev; e.tgid = id >> 32; e.tid = (u32)id;
    e.entry_ns = bpf_ktime_get_ns(); e.count = PT_REGS_PARM3(ctx); e.kind = 1;
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    struct task_struct *leader = NULL, *parent = NULL;
    if (bpf_probe_read_kernel(&leader, sizeof(leader), &task->group_leader)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&e.start_ns, sizeof(e.start_ns), &leader->start_boottime)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&parent, sizeof(parent), &leader->real_parent)) { inc(9); return 0; }
    if (bpf_probe_read_kernel(&e.ppid, sizeof(e.ppid), &parent->tgid)) { inc(9); return 0; }
    if (pending.lookup(&id)) inc(4);
    if (pending.update(&id, &e)) inc(5);
    if (seen.update(&e.tgid, &e.start_ns)) inc(8);
    return 0;
}

int leave(struct pt_regs *ctx) {
    u64 id = bpf_get_current_pid_tgid();
    struct event *e = pending.lookup(&id);
    if (!e) return 0;
    inc(1);
    e->exit_ns = bpf_ktime_get_ns(); e->result = PT_REGS_RC(ctx);
    if (events.perf_submit(ctx, e, sizeof(*e))) inc(3); else inc(2);
    if (pending.delete(&id)) inc(10);
    return 0;
}

TRACEPOINT_PROBE(sched, sched_process_exit) {
    u64 id = bpf_get_current_pid_tgid(); u32 tgid = id >> 32;
    if ((u32)id != tgid) return 0;
    u64 *start = seen.lookup(&tgid);
    if (!start) return 0;
    struct event e = {};
    e.kind = 2; e.tgid = tgid; e.tid = tgid; e.start_ns = *start;
    e.exit_ns = bpf_ktime_get_ns();
    if (events.perf_submit(args, &e, sizeof(e))) inc(7); else inc(6);
    if (seen.delete(&tgid)) inc(10);
    return 0;
}
"""


def emit(data):
    print(json.dumps(data, sort_keys=True), flush=True)


def run(path, duration):
    if platform.system() != "Linux" or os.geteuid() != 0:
        raise RuntimeError("requires explicitly authorized root inside isolated Linux VM")
    if not path.startswith("/var/tmp/a1-research-"):
        raise ValueError("scope outside artificial research directory")
    from bcc import BPF

    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    identity = os.fstat(fd)
    rawdev = (os.major(identity.st_dev) << 20) | os.minor(identity.st_dev)
    text = PROGRAM.replace("TARGET_INODE", str(identity.st_ino)).replace("TARGET_DEV", str(rawdev))
    before = resource.getrusage(resource.RUSAGE_SELF)
    boot = hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes()).hexdigest()
    bpf = BPF(text=text)
    entry_name = attach_classic(bpf, "vfs_write", "enter")
    bpf.attach_kretprobe(event="vfs_write", fn_name="leave", maxactive=128)
    lost = 0
    raw_bytes = 0
    records = 0

    def callback(cpu, data, size):
        nonlocal raw_bytes, records
        e = bpf["events"].event(data)
        record = {
            name: int(getattr(e, name))
            for name in [
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
        record.update(boot_hash=boot, cpu=cpu, raw_bytes=size)
        raw_bytes += size
        records += 1
        emit({"record": record})

    def loss(cpu, count):
        nonlocal lost
        lost += count
        emit({"lost": int(count), "cpu": cpu})

    bpf["events"].open_perf_buffer(callback, page_cnt=64, lost_cb=loss)
    ready_ns = time.monotonic_ns()
    emit(
        {
            "ready": True,
            "kernel": platform.release(),
            "boot_hash": boot,
            "pid_namespace": os.readlink("/proc/self/ns/pid"),
            "ready_ns": ready_ns,
            "file": {"dev": rawdev, "inode": identity.st_ino},
            "program_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "observer_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
    )
    end = time.monotonic() + duration
    while time.monotonic() < end:
        bpf.perf_buffer_poll(timeout=50)
    stats = {
        str(key.value): sum(int(v.value) if hasattr(v, "value") else int(v) for v in values)
        for key, values in bpf["stats"].items()
    }
    return_name = "r_vfs_write_bcc_" + str(os.getpid())
    kernel_profile = profile([entry_name, return_name])
    programs = program_info(bpf)
    after = resource.getrusage(resource.RUSAGE_SELF)
    emit(
        {
            "summary": {
                "stats": stats,
                "pending": len(bpf["pending"]),
                "perf_lost": lost,
                "records": records,
                "raw_bytes": raw_bytes,
                "kprobe_profile": [
                    [name, str(row["hits"]), str(row["misses"])]
                    for name, row in kernel_profile["selected"].items()
                ],
                "classic_profile": kernel_profile,
                "program_info": programs,
                "entry_probe_nmissed": misses(kernel_profile, entry_name),
                "entry_probe_nmissed_limit": "direct classic entry and return counters; recursion fdinfo and independent oracle also required",
                "end_ns": time.monotonic_ns(),
                "cpu_user_seconds": after.ru_utime - before.ru_utime,
                "cpu_system_seconds": after.ru_stime - before.ru_stime,
                "rss_peak_bytes": after.ru_maxrss * 1024,
                "scope": "observer process including BCC compile, not kernel/VM CPU",
                "logical_agent_identity": "UNBEKANNT",
            }
        }
    )
    bpf.cleanup()
    os.close(fd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--duration", type=float, default=6)
    args = parser.parse_args()
    if not 0 < args.duration <= 12:
        raise ValueError("duration bound")
    run(args.path, args.duration)
