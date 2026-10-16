"""Operator-only fixed SSH transport. Never carries credentials in argv/output."""

import argparse
import subprocess
from pathlib import Path

SSH = [
    "ssh",
    "-T",
    "-o",
    "BatchMode=yes",
    "-o",
    "StrictHostKeyChecking=yes",
    "-o",
    "UpdateHostKeys=no",
    "-o",
    "ForwardAgent=no",
    "-o",
    "ClearAllForwardings=yes",
    "-o",
    "ConnectTimeout=8",
    "netcup-daniel",
]


def run(source, timeout=60):
    return subprocess.run(
        SSH + ["sudo -n python3 -B -"],
        input=source,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def bounded(source, name, timeout=180):
    assert name.replace("-", "").isalnum()
    command = (
        "sudo -n systemd-run --unit=aa-private-"
        + name
        + " --slice=aa-private.slice --property=MemorySwapMax=0 --property=LimitCORE=0"
        " --property=RuntimeMaxSec=" + str(timeout - 5) + " --wait --pipe /usr/bin/python3 -B -"
    )
    return subprocess.run(
        SSH + [command], input=source, capture_output=True, timeout=timeout, check=False
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    r = run(a.source.read_bytes(), a.timeout)
    if a.output:
        with a.output.open("xb") as f:
            f.write(r.stdout)
    else:
        print(r.stdout.decode(), end="")
    print(r.stderr.decode(), end="")
    raise SystemExit(r.returncode)
