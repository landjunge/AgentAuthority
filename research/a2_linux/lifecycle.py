"""Additive kernel fork/start/exec/exit metadata for trusted starter descendants."""

import os

PROGRAM = r"""
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>
struct state { u64 start, exec_ns, exit_ns; u32 execs, parent; };
struct record { u64 start, stamp; u32 pid, parent, kind, generation, uid; };
BPF_HASH(states, u32, struct state, 128);
BPF_PERCPU_ARRAY(failures, u64, 1);
BPF_PERF_OUTPUT(events);
static void send(void *ctx, u32 pid, struct state *s, u32 kind) {
    struct record r = {};
    r.pid = pid; r.parent = s->parent; r.start = s->start;
    r.stamp = bpf_ktime_get_ns(); r.kind = kind; r.generation = s->execs;
    r.uid = (u32)bpf_get_current_uid_gid();
    if (events.perf_submit(ctx, &r, sizeof(r))) {
        u32 k=0; u64 *v=failures.lookup(&k); if(v) (*v)++;
    }
}
int forked(struct pt_regs *ctx, struct task_struct *child) {
    u32 parent = bpf_get_current_pid_tgid() >> 32;
    if (parent != STARTER_PID && !states.lookup(&parent)) return 0;
    u32 pid=0; struct state s={}; s.parent=parent;
    bpf_probe_read_kernel(&pid, sizeof(pid), &child->tgid);
    bpf_probe_read_kernel(&s.start, sizeof(s.start), &child->start_boottime);
    if (!s.start || !pid) return 0;
    states.update(&pid, &s); send(ctx,pid,&s,1); return 0;
}
TRACEPOINT_PROBE(sched, sched_process_exec) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    struct state *s=states.lookup(&pid); if(!s) return 0;
    s->execs++; s->exec_ns=bpf_ktime_get_ns(); send(args,pid,s,2); return 0;
}
TRACEPOINT_PROBE(sched, sched_process_exit) {
    u64 id=bpf_get_current_pid_tgid(); u32 pid=id>>32;
    if ((u32)id != pid) return 0;
    struct state *s=states.lookup(&pid); if(!s) return 0;
    s->exit_ns=bpf_ktime_get_ns(); send(args,pid,s,3); return 0;
}
"""


class Lifecycle:
    def __init__(self):
        from bcc import BPF

        self.bpf = BPF(text=PROGRAM.replace("STARTER_PID", str(os.getpid())))
        self.bpf.attach_kprobe(event="wake_up_new_task", fn_name="forked")
        self.records = []
        self.lost = 0
        self.raw_bytes = 0
        self.bpf["events"].open_perf_buffer(self._event, lost_cb=self._lost, page_cnt=64)

    def _event(self, cpu, data, size):
        event = self.bpf["events"].event(data)
        self.records.append(
            {
                name: int(getattr(event, name))
                for name in ["start", "stamp", "pid", "parent", "kind", "generation", "uid"]
            }
        )
        self.raw_bytes += size

    def _lost(self, cpu, count):
        self.lost += count

    def poll(self):
        self.bpf.perf_buffer_poll(timeout=10)

    def state(self, pid):
        import ctypes

        self.poll()
        s = self.bpf["states"][ctypes.c_uint(pid)]
        return {
            "pid": pid,
            "start_ns": int(s.start),
            "generation": int(s.execs),
            "exec_ns": int(s.exec_ns),
            "exit_ns": int(s.exit_ns),
            "parent": int(s.parent),
        }

    def finish(self):
        self.poll()
        failures = sum(int(v) for _, values in self.bpf["failures"].items() for v in values)
        result = {
            "records": self.records,
            "perf_lost": self.lost,
            "submit_failures": failures,
            "callback_raw_bytes": self.raw_bytes,
            "fork_entry_nmissed": None,
            "scope": "starter descendants; missing fork/exec means unknown binding",
        }
        self.bpf.cleanup()
        return result
