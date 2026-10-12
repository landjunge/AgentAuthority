"""Instrument-only checks, no test identities/delegations or target writer jobs."""

import argparse
import ctypes
import json
import os
import subprocess
from pathlib import Path

from lifecycle import Lifecycle


def check(mode):
    if os.geteuid() != 0 or not Path(__file__).resolve().parent.name.startswith("a4c-"):
        raise ValueError("own isolated research guest scope only")
    life = Lifecycle()
    if mode == "map-full":
        table = life.bpf["states"]
        for index in range(512):
            table[ctypes.c_uint(1_000_000 + index)] = table.Leaf()
    process = subprocess.Popen(["/bin/true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait(timeout=5)
    for _ in range(5):
        life.poll()
    result = life.finish()
    return {
        "mode": mode,
        "agent_identities": 0,
        "delegations": 0,
        "target_write_jobs": 0,
        "reference_child_pid": process.pid,
        "reference_exit": process.returncode,
        "synthetic_map_fill_entries": 512 if mode == "map-full" else 0,
        "lifecycle": result,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["healthy", "map-full"])
    args = parser.parse_args()
    print(json.dumps(check(args.mode)))
