"""A4 VFS collector adaptation: reject other UIDs/cgroups before dereferencing file."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/a4_completion"))
import observer

from research.debian_private.probe_profile import profile


def main():
    observer.profile = profile
    target = sys.argv[1]
    assert target.startswith("/var/tmp/a1-research-a4-")
    relative = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
    assert relative.endswith("/aa-private-collector.service")
    cg = os.stat("/sys/fs/cgroup" + relative).st_ino
    marker = "int enter(struct pt_regs *ctx, struct file *file) {"
    guard = (
        "\n    if (bpf_get_current_cgroup_id() != "
        + str(cg)
        + "ULL || (u32)bpf_get_current_uid_gid() != 61102) return 0;\n"
    )
    assert observer.PROGRAM.count(marker) == 1
    observer.PROGRAM = observer.PROGRAM.replace(marker, marker + guard)
    observer.run(target, 12)


if __name__ == "__main__":
    main()
