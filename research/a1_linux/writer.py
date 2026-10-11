"""Artificial writer/oracle endpoint; output goes only to separate host controller."""

import argparse
import hashlib
import json
import os
import time


def identity():
    return {
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "uid": os.getuid(),
        "start_ticks": int(open("/proc/self/stat").read().rsplit(")", 1)[1].split()[19]),
        "clock_ticks": os.sysconf("SC_CLK_TCK"),
        "boot_hash": hashlib.sha256(
            open("/proc/sys/kernel/random/boot_id").read().encode()
        ).hexdigest(),
        "pid_namespace": os.readlink("/proc/self/ns/pid"),
    }


def action(path, idle):
    d = identity()
    if idle:
        d.update(action="idle", result=None, file=None)
    else:
        fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
        st = os.fstat(fd)
        begin = time.monotonic_ns()
        result = os.write(fd, b"0123456789ABCDEF")
        end = time.monotonic_ns()
        os.close(fd)
        d.update(
            action="write",
            result=result,
            begin_ns=begin,
            end_ns=end,
            file={"dev": (os.major(st.st_dev) << 20) | os.minor(st.st_dev), "inode": st.st_ino},
        )
    print(json.dumps(d, sort_keys=True), flush=True)
    time.sleep(0.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--idle", action="store_true")
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if not args.path.startswith("/var/tmp/a1-research-"):
        raise ValueError("artificial files only")
    if args.child:
        print(json.dumps({"parent": identity()}), flush=True)
        child = os.fork()
        if child == 0:
            action(args.path, False)
            os._exit(0)
        else:
            _, status = os.waitpid(child, 0)
            raise SystemExit(os.waitstatus_to_exitcode(status))
    else:
        action(args.path, args.idle)
