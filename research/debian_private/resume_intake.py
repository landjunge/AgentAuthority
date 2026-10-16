"""Operator-only intake repair: no claim, collector call or action execution."""

import json

from research.debian_private.ipc import SECURE
from research.debian_private.runner import intake

if __name__ == "__main__":
    data = json.loads((SECURE / "runner/pending.json").read_bytes())
    intake(data["binding"], data["evidence"])
