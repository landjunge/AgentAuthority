"""Existing A2/A4 handshake/lifecycle with an added fixed cgroup predicate."""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/a4_completion"))
sys.path.append(str(ROOT / "research/a2_linux"))
import guest
import lifecycle

from research.debian_private.probe_profile import profile


def main():
    lifecycle.profile = profile
    vault, certificate, target, context = sys.argv[1:]
    relative = Path("/proc/self/cgroup").read_text().strip().split("::", 1)[1]
    assert relative.endswith("/aa-private-collector.service")
    cg = os.stat("/sys/fs/cgroup" + relative).st_ino
    marker = "int forked(struct pt_regs *ctx, struct task_struct *child) {"
    lifecycle.PROGRAM = lifecycle.PROGRAM.replace(
        marker, marker + "\n    if (bpf_get_current_cgroup_id() != " + str(cg) + "ULL) return 0;\n"
    )
    binding = json.loads(Path(context).read_bytes())
    original_digest = guest.digest

    def digest(value):
        if (
            type(value) is dict
            and set(value) == {"operation", "file"}
            and value["operation"] == "write16"
        ):
            value["service_binding"] = binding
        return original_digest(value)

    guest.digest = digest
    print(json.dumps(guest.trial(Path(vault), Path(certificate), target)))


if __name__ == "__main__":
    main()
