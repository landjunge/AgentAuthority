"""One-time additive preparation; executed as root through pinned operator SSH."""

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

BASE = Path("/var/lib/aa-private-install-20261017")
assert os.geteuid() == 0
assert not BASE.exists(), "preserve previous installation record"
for p in ("/opt/aa-private", "/etc/aa-private", "/var/lib/aa-private"):
    assert not Path(p).exists(), "existing namespace must be reviewed"
BASE.mkdir(mode=0o700)
os.umask(0o077)


def cmd(args):
    return subprocess.check_output(args, timeout=15).decode()


before = {
    "time_ns": time.time_ns(),
    "packages": cmd(["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\n"]),
    "central": cmd(
        [
            "systemctl",
            "show",
            "ki-hilfezentrum.service",
            "-p",
            "MainPID",
            "-p",
            "ActiveState",
            "-p",
            "CPUUsageNSec",
            "-p",
            "MemoryCurrent",
        ]
    ),
    "listeners": cmd(["ss", "-ltn"]),
    "new_paths_previously_absent": True,
    "central_unit_sha256": hashlib.sha256(
        Path("/etc/systemd/system/ki-hilfezentrum.service").read_bytes()
    ).hexdigest(),
}
(BASE / "before.json").write_text(json.dumps(before, indent=2))
(BASE / "rollback.txt").write_text(
    "Stop only aa-private-* services and sockets, verify no users/processes/mount dependencies; keep this record. Close only aa-private dm mapping after unmount. Never reset production. Added packages recorded by before/after package diff; do not auto-remove shared dependencies. No original configuration was replaced. Ephemeral keys have no recovery copy.\n"
)
Path("/etc/systemd/system/aa-private.slice").write_text("""[Unit]
Description=Agent Authority private qualification aggregate budget
[Slice]
CPUQuota=35%
MemoryMax=768000000
MemorySwapMax=0
TasksMax=48
""")
subprocess.run(["systemctl", "daemon-reload"], check=True)
subprocess.run(["systemctl", "start", "aa-private.slice"], check=True)
print(
    json.dumps(
        {
            "backup": str(BASE),
            "new_namespace": True,
            "central_unit_sha256": before["central_unit_sha256"],
        }
    )
)
