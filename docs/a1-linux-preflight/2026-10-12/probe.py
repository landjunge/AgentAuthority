"""Bounded metadata-only preflight: no subscriptions, syscalls or target files."""

import argparse
import datetime
import gzip
import hashlib
import json
import os
import platform
import resource
import shutil
import stat
import time

LIMIT = 8 * 1024 * 1024
CAPABILITIES = {
    "CAP_DAC_READ_SEARCH": 2,
    "CAP_SYS_PTRACE": 19,
    "CAP_SYS_ADMIN": 21,
    "CAP_AUDIT_WRITE": 29,
    "CAP_AUDIT_CONTROL": 30,
    "CAP_AUDIT_READ": 37,
    "CAP_PERFMON": 38,
    "CAP_BPF": 39,
    "CAP_CHECKPOINT_RESTORE": 40,
}
CONFIG_KEYS = {
    "CONFIG_AUDIT",
    "CONFIG_AUDITSYSCALL",
    "CONFIG_BPF",
    "CONFIG_BPF_SYSCALL",
    "CONFIG_BPF_EVENTS",
    "CONFIG_BPF_UNPRIV_DEFAULT_OFF",
    "CONFIG_DEBUG_INFO_BTF",
    "CONFIG_FANOTIFY",
    "CONFIG_FANOTIFY_ACCESS_PERMISSIONS",
    "CONFIG_FTRACE",
    "CONFIG_TRACEPOINTS",
    "CONFIG_PERF_EVENTS",
    "CONFIG_SECCOMP",
    "CONFIG_SECCOMP_FILTER",
    "CONFIG_SECURITY_APPARMOR",
    "CONFIG_SECURITY_SELINUX",
    "CONFIG_SECURITY_LOCKDOWN_LSM",
    "CONFIG_NAMESPACES",
    "CONFIG_USER_NS",
    "CONFIG_PID_NS",
}


def read(path):
    """Only callers' fixed metadata paths, bounded bytes; never raw errors."""
    try:
        with open(path, "rb") as stream:
            chunks = []
            size = 0
            while size <= LIMIT:
                block = stream.read(4096)
                if not block:
                    break
                chunks.append(block)
                size += len(block)
            data = b"".join(chunks)
        if len(data) > LIMIT:
            return {"status": "UNBEKANNT", "reason": "size_limit"}
        return {
            "status": "BELEGT",
            "value": data.decode("utf-8"),
            "bytes_read": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
    except OSError as error:
        return {"status": "UNBEKANNT", "errno": error.errno}
    except UnicodeError:
        return {"status": "UNBEKANNT", "reason": "encoding"}


def metadata(path):
    try:
        item = os.stat(path)
        return {
            "status": "BELEGT",
            "mode": oct(stat.S_IMODE(item.st_mode)),
            "uid": item.st_uid,
            "gid": item.st_gid,
            "size": item.st_size,
            "readable_access_check_only": os.access(path, os.R_OK),
            "searchable_access_check_only": os.access(path, os.X_OK),
        }
    except OSError as error:
        return {"status": "UNBEKANNT", "errno": error.errno}


def namespace(path):
    try:
        return {"status": "BELEGT", "link": os.readlink(path)}
    except OSError as error:
        return {"status": "UNBEKANNT", "errno": error.errno}


def config(release):
    results = {}
    for path in ["/boot/config-" + release, "/proc/config.gz"]:
        try:
            opener = gzip.open if path.endswith(".gz") else open
            with opener(path, "rb") as stream:
                data = stream.read(LIMIT + 1)
            if len(data) > LIMIT:
                results[path] = {"status": "UNBEKANNT", "reason": "size_limit"}
                continue
            selected = {}
            for line in data.decode("utf-8").splitlines():
                key = line.split("=", 1)[0]
                if key in CONFIG_KEYS:
                    selected[key] = line.split("=", 1)[1]
                if line.startswith("# ") and line.endswith(" is not set"):
                    key = line[2:-11]
                    if key in CONFIG_KEYS:
                        selected[key] = "n"
            results[path] = {
                "status": "BELEGT",
                "bytes_read": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "selected": selected,
            }
        except OSError as error:
            results[path] = {"status": "UNBEKANNT", "errno": error.errno}
    return results


def collect(label):
    start = time.monotonic_ns()
    result = {
        "schema": "a1-linux-preflight-v1",
        "utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "environment_label": label,
        "system": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "euid": os.geteuid(),
        "egid": os.getegid(),
        "writer_experiments_executed": False,
        "event_stream_opened": False,
        "causality": "UNBEKANNT",
        "writer_events": None,
        "attribution_correct": None,
        "attribution_unclear": None,
        "event_loss": None,
        "logical_agent_identity": "UNBEKANNT",
    }
    if result["system"] != "Linux":
        result["linux_access"] = "NICHT VERFÜGBAR"
        return result
    osrelease = read("/etc/os-release")
    if osrelease["status"] == "BELEGT":
        osrelease["value"] = {
            key: value.strip('"')
            for line in osrelease["value"].splitlines()
            if "=" in line
            for key, value in [line.split("=", 1)]
            if key in {"ID", "VERSION_ID", "PRETTY_NAME", "VERSION_CODENAME"}
        }
    result["distribution"] = osrelease
    process = read("/proc/self/status")
    if process["status"] == "BELEGT":
        allowed = {
            "Uid",
            "Gid",
            "NSpid",
            "CapInh",
            "CapPrm",
            "CapEff",
            "CapBnd",
            "CapAmb",
            "NoNewPrivs",
            "Seccomp",
            "Seccomp_filters",
        }
        process["value"] = {
            line.split(":", 1)[0]: line.split(":", 1)[1].strip()
            for line in process["value"].splitlines()
            if line.split(":", 1)[0] in allowed
        }
        value = process["value"].get("CapEff")
        effective = int(value, 16) if value is not None else None
        result["selected_effective_capabilities"] = {
            name: bool(effective & (1 << bit)) if effective is not None else None
            for name, bit in CAPABILITIES.items()
        }
    result["self_status"] = process
    ownstat = read("/proc/self/stat")
    if ownstat["status"] == "BELEGT":
        ownstat["value"] = {
            "pid": os.getpid(),
            "start_ticks_since_boot": int(ownstat["value"].rsplit(")", 1)[1].split()[19]),
            "ticks_per_second": os.sysconf("SC_CLK_TCK"),
            "causal_writer_record": False,
        }
    result["self_start_snapshot"] = ownstat
    boot = read("/proc/sys/kernel/random/boot_id")
    boot.pop("value", None)
    result["boot_identity_hash"] = boot
    result["namespaces"] = {
        source: {
            kind: namespace(f"/proc/{source}/ns/{kind}")
            for kind in ["pid", "user", "mnt", "net", "cgroup"]
        }
        for source in ["self", "1"]
    }
    result["metadata_reads"] = {
        path: read(path)
        for path in [
            "/proc/self/uid_map",
            "/proc/self/gid_map",
            "/proc/self/attr/current",
            "/sys/kernel/security/lsm",
            "/sys/kernel/security/lockdown",
            "/sys/fs/selinux/enforce",
            "/sys/module/apparmor/parameters/enabled",
            "/proc/sys/kernel/unprivileged_bpf_disabled",
            "/proc/sys/kernel/perf_event_paranoid",
            "/proc/sys/kernel/yama/ptrace_scope",
            "/proc/sys/kernel/unprivileged_userns_clone",
            "/proc/sys/fs/fanotify/max_queued_events",
            "/proc/sys/fs/fanotify/max_user_groups",
            "/proc/sys/fs/fanotify/max_user_marks",
        ]
    }
    mounts = read("/proc/self/mountinfo")
    if mounts["status"] == "BELEGT":
        selected = []
        for line in mounts["value"].splitlines():
            before, after = line.split(" - ", 1)
            left, right = before.split(), after.split()
            if left[4] in [
                "/",
                "/proc",
                "/sys",
                "/sys/kernel/tracing",
                "/sys/kernel/debug",
                "/sys/kernel/security",
                "/sys/fs/bpf",
                "/sys/fs/cgroup",
            ]:
                selected.append(
                    {
                        "mountpoint": left[4],
                        "filesystem": right[0],
                        "options": left[5],
                        "super_options": right[2],
                    }
                )
        mounts["value"] = selected
    result["selected_mounts"] = mounts
    result["interface_metadata"] = {
        path: metadata(path)
        for path in [
            "/proc",
            "/sys/kernel/tracing",
            "/sys/kernel/debug/tracing",
            "/sys/fs/bpf",
            "/sys/kernel/btf/vmlinux",
            "/sys/kernel/security",
            "/usr/include/linux/fanotify.h",
            "/usr/include/linux/audit.h",
            "/usr/include/linux/bpf.h",
            "/var/log/audit",
        ]
    }
    result["tracepoint_formats"] = {}
    for root in ["/sys/kernel/tracing", "/sys/kernel/debug/tracing"]:
        for event in [
            "syscalls/sys_enter_write",
            "syscalls/sys_exit_write",
            "syscalls/sys_enter_pwrite64",
            "syscalls/sys_enter_writev",
            "sched/sched_process_fork",
            "sched/sched_process_exec",
            "sched/sched_process_exit",
        ]:
            path = root + "/events/" + event + "/format"
            fmt = read(path)
            if fmt["status"] == "BELEGT":
                fmt["value"] = [
                    line.strip()
                    for line in fmt["value"].splitlines()
                    if line.startswith(("name:", "ID:")) or "field:" in line
                ]
            result["tracepoint_formats"][path] = fmt
    result["kernel_config"] = config(result["release"])
    result["tool_paths_presence_only"] = {
        name: shutil.which(name)
        for name in [
            "python3",
            "auditctl",
            "ausearch",
            "bpftool",
            "bpftrace",
            "perf",
            "clang",
            "cc",
            "gcc",
            "getcap",
            "capsh",
        ]
    }
    result["runner_allowlist"] = {
        name: os.environ.get(name)
        for name in [
            "GITHUB_ACTIONS",
            "GITHUB_RUN_ID",
            "GITHUB_SHA",
            "RUNNER_OS",
            "RUNNER_ARCH",
            "RUNNER_ENVIRONMENT",
            "ImageOS",
            "ImageVersion",
        ]
    }
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result["diagnostic_resources"] = {
        "body_elapsed_ns": time.monotonic_ns() - start,
        "process_cpu_user_seconds": usage.ru_utime,
        "process_cpu_system_seconds": usage.ru_stime,
        "process_peak_rss_bytes_linux": usage.ru_maxrss * 1024,
        "scope": "this Python diagnostic process, not compiler/VM/monitor",
        "event_stream_cpu": None,
        "event_stream_ram": None,
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", choices=["colima-vm", "diagnostic-container", "github-actions"])
    args = parser.parse_args()
    print("A1_LINUX_PREFLIGHT_JSON_BEGIN")
    print(json.dumps(collect(args.label), sort_keys=True, indent=2, ensure_ascii=True))
    print("A1_LINUX_PREFLIGHT_JSON_END")
