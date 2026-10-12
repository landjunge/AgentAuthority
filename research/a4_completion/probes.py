"""Pinned BCC 0.29.1 classic attachment and explicit kernel loss snapshots."""

import os
from pathlib import Path


def attach_classic(bpf, event, function):
    from bcc import BPF
    from bcc.libbcc import lib

    event, function = event.encode(), function.encode()
    name = b"p_a4c_" + event
    program = bpf.load_func(function, BPF.KPROBE)
    # BCC libbpf.c: maxactive > 0 skips the perf-PMU path. For an ENTRY
    # create_probe_event still emits an ordinary p: event (not a return probe).
    fd = lib.bpf_attach_kprobe(program.fd, 0, name, event, 0, 1)
    if fd < 0:
        raise RuntimeError("classic tracefs attachment failed")
    bpf._add_kprobe_fd(name, function, fd)
    return name.decode() + "_bcc_" + str(os.getpid())


def profile(names):
    try:
        raw = Path("/sys/kernel/tracing/kprobe_profile").read_text()
        rows = {r[0]: r for line in raw.splitlines() if len(r := line.split()) == 3}
        selected = {
            name: {"hits": int(rows[name][1]), "misses": int(rows[name][2])} for name in names
        }
        return {"raw": raw, "selected": selected, "complete": True}
    except (OSError, KeyError, ValueError) as error:
        return {"selected": {}, "complete": False, "error": str(error)}


def program_info(bpf):
    result = {}
    for name, function in bpf.functions.items():
        label = name.decode() if isinstance(name, bytes) else str(name)
        raw = Path(f"/proc/self/fdinfo/{function.fd}").read_text()
        fields = dict(line.split(":", 1) for line in raw.splitlines() if ":" in line)
        result[label] = {
            "raw_fdinfo": raw,
            "recursion_misses": int(fields["recursion_misses"])
            if "recursion_misses" in fields
            else None,
            "prog_id": int(fields["prog_id"]),
        }
    return result


def misses(snapshot, name):
    return snapshot["selected"][name]["misses"] if snapshot["complete"] else None
