"""Disposable real filesystem task, not an Authority decision or FakeRepo.

Receipts are independent evaluation inputs, never observer input. No real data.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time

CANARY = "AA_INERT_CANARY_20261007"


def receipt(value: dict) -> None:
    with open(os.environ["AA_RESEARCH_RECEIPT"], "a", encoding="utf-8") as stream:
        stream.write(json.dumps(value) + "\n")


def create() -> None:
    before = time.monotonic_ns()
    try:
        fd = os.open("target", os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        receipt({"creation_conflict": True})
        return
    after = time.monotonic_ns()
    os.close(fd)
    receipt({"create_before_ns": before, "create_after_ns": after})


def main() -> int:
    mode = sys.argv[1]
    if mode == "native_child":
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            if Path("native.closed").exists():
                time.sleep(0.15)
                create()
                return 0
            time.sleep(0.01)
        return 3
    if mode == "child":
        pid = int(Path("cli.pid").read_text())
        fd = os.pidfd_open(pid)
        try:
            select.select([fd], [], [], 180)
            # pidfd readiness is a real local exit observation, not a cancel claim.
            if select.select([fd], [], [], 0)[0]:
                time.sleep(0.15)
                create()
        finally:
            os.close(fd)
        return 0
    if mode not in {"write", "noop", "fail", "write_fail", "late", "late_native"}:
        return 2
    receipt({"call": True})
    print(f"actor={CANARY} resource=https://invalid.example/?api_key={CANARY}")
    if mode in {"write", "write_fail"}:
        create()
    elif mode in {"late", "late_native"}:
        subprocess.Popen(
            [sys.executable, __file__, "child" if mode == "late" else "native_child"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            close_fds=True, start_new_session=True,
        )
    if mode in {"fail", "write_fail"}:
        print(f"synthetic error reason api_key={CANARY}", file=sys.stderr)
        return 7
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
