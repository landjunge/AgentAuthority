"""Fixed local budgets. OS account/sandbox separation still requires a target host."""

import os
import resource
import sys
import time
from contextvars import ContextVar

from research.private_service.protocol import require

MAX_BYTES = 262144
MAX_CHILD_INPUT = 524288
MAX_CHILD_OUTPUT = 65536
HTTP_SECONDS = 5.0
CHILD_SECONDS = 2.0
LOCK_SECONDS = 1.0
MEMORY_BYTES = 512 * 1024 * 1024
DEADLINE = ContextVar("aa_request_deadline", default=None)


def remaining(maximum=CHILD_SECONDS):
    deadline = DEADLINE.get()
    left = maximum if deadline is None else min(maximum, deadline - time.monotonic())
    require(left > 0, 503, "REQUEST_TIMEOUT")
    return left


def unprivileged():
    require(os.geteuid() != 0 and os.getuid() != 0, 503, "PRIVILEGED_API_FORBIDDEN")
    if sys.platform.startswith("linux"):
        # Effective AND latent capabilities must not enter the public process.
        with open("/proc/self/status", encoding="ascii") as status:
            for line in status:
                if line.startswith(("CapInh:", "CapPrm:", "CapEff:", "CapAmb:")):
                    require(int(line.split()[1], 16) == 0, 503, "PRIVILEGED_API_FORBIDDEN")


def process_limits(child=False):
    """Applied only to our CLI/children, never the caller's test/editor process.

    Darwin rejects a finite DATA limit on this host; no hard RSS claim there.
    Linux AS is a hard virtual-address limit. CPU is a process-lifetime budget.
    """
    unprivileged()
    for kind, value in (
        (resource.RLIMIT_CORE, 0),
        (resource.RLIMIT_NOFILE, 64),
        (resource.RLIMIT_CPU, 2 if child else 120),
        (resource.RLIMIT_FSIZE, 0 if child else 32 * 1024 * 1024),
    ):
        _, hard = resource.getrlimit(kind)
        value = value if hard == resource.RLIM_INFINITY else min(value, hard)
        resource.setrlimit(kind, (value, value))
    if sys.platform.startswith("linux"):
        _, hard = resource.getrlimit(resource.RLIMIT_AS)
        value = MEMORY_BYTES if hard == resource.RLIM_INFINITY else min(MEMORY_BYTES, hard)
        resource.setrlimit(resource.RLIMIT_AS, (value, value))
