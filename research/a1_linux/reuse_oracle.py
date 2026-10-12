"""One explicit PID reuse control inside disposable guest, outside six-case denominator."""

import json
import os
import time

from oracle import spawn
from writer import identity


def main(path):
    if os.geteuid() != 0 or not path.startswith("/var/tmp/a1-research-"):
        raise ValueError("isolated guest root and artificial file required")
    controller = identity()
    first = spawn(path)
    time.sleep(0.05)
    oldpid = first["process"]["pid"]
    with open("/proc/sys/kernel/ns_last_pid", "w") as stream:
        stream.write(str(oldpid - 1))
    second = spawn(path)
    result = {
        "controller": controller,
        "rows": [first, second],
        "forged_claim_pid": None,
        "pid_reuse_requested": oldpid,
        "pid_reuse_actual": oldpid == second["process"]["pid"],
        "separate_from_six_case_denominator": True,
        "attempts": 1,
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    import sys

    main(sys.argv[1])
