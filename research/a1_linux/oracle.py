"""Trusted artificial controller; independent spawn/proc/pidfd data, host-only output."""

import argparse
import json
import os
import select
import time

from writer import identity


def snapshot(pid):
    with open(f"/proc/{pid}/stat") as stream:
        fields = stream.read().rsplit(")", 1)[1].split()
    return {
        "pid": pid,
        "ppid": int(fields[1]),
        "start_ticks": int(fields[19]),
        "clock_ticks": os.sysconf("SC_CLK_TCK"),
    }


def spawn(path, idle=False, grandchild=False):
    ready_r, ready_w = os.pipe()
    go_r, go_w = os.pipe()
    result_r, result_w = os.pipe()
    child = os.fork()
    if child == 0:
        os.close(ready_r)
        os.close(go_w)
        os.close(result_r)
        if grandchild:
            descendant = os.fork()
            if descendant:
                os.write(ready_w, (str(descendant) + "\n").encode())
                os.close(ready_w)
                os.close(go_r)
                os.close(result_w)
                _, status = os.waitpid(descendant, 0)
                os._exit(os.waitstatus_to_exitcode(status))
        else:
            os.write(ready_w, (str(os.getpid()) + "\n").encode())
        os.close(ready_w)
        assert os.read(go_r, 1) == b"G"
        os.close(go_r)
        if idle:
            result = {"action": "idle", "result": None, "file": None}
        else:
            fd = os.open(path, os.O_WRONLY | os.O_NOFOLLOW)
            st = os.fstat(fd)
            begin = time.monotonic_ns()
            count = os.write(fd, b"0123456789ABCDEF")
            end = time.monotonic_ns()
            os.close(fd)
            result = {
                "action": "write",
                "result": count,
                "begin_ns": begin,
                "end_ns": end,
                "file": {
                    "dev": (os.major(st.st_dev) << 20) | os.minor(st.st_dev),
                    "inode": st.st_ino,
                },
            }
        os.write(result_w, json.dumps(result).encode() + b"\n")
        os.close(result_w)
        time.sleep(0.3)
        os._exit(0)
    os.close(ready_w)
    os.close(go_r)
    os.close(result_w)
    with os.fdopen(ready_r) as stream:
        actual = int(stream.readline())
    pidfd = os.pidfd_open(actual)
    before = snapshot(actual)
    os.write(go_w, b"G")
    os.close(go_w)
    with os.fdopen(result_r) as stream:
        result = json.loads(stream.readline())
    after = snapshot(actual)
    _, status = os.waitpid(child, 0)
    poll = select.poll()
    poll.register(pidfd, select.POLLIN)
    exited = bool(poll.poll(500))
    os.close(pidfd)
    result.update(
        process=before,
        process_after=after,
        stable=before == after,
        exit_status=os.waitstatus_to_exitcode(status),
        pidfd_exit_seen=exited,
        creator_child=child,
        grandchild=grandchild,
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("mode", choices=["write", "idle", "sibling", "child", "forged", "pair"])
    args = parser.parse_args()
    if not args.path.startswith("/var/tmp/a1-research-"):
        raise ValueError("artificial files only")
    controller = identity()
    rows = []
    claim = None
    if args.mode == "idle":
        rows.append(spawn(args.path, idle=True))
    elif args.mode == "sibling":
        rows.append(spawn(args.path + ".other"))
    elif args.mode == "child":
        rows.append(spawn(args.path, grandchild=True))
    elif args.mode == "pair":
        rows.append(spawn(args.path))
        rows.append(spawn(args.path))
    elif args.mode == "forged":
        rows.append(spawn(args.path, idle=True))
        claim = rows[0]["process"]["pid"]
        rows.append(spawn(args.path))
    else:
        rows.append(spawn(args.path))
    print(
        json.dumps(
            {"controller": controller, "rows": rows, "forged_claim_pid": claim}, sort_keys=True
        )
    )
