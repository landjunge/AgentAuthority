"""Explicit, generated synthetic inputs for manual browser operation only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def write_examples(output: Path) -> None:
    from agent_authority.browser_adapter import synthetic_private_response

    output.mkdir(mode=0o700)
    for name in ("alice", "bob"):
        records = [
            {
                "schema_version": "agent-authority-observation-v1",
                "id": f"synthetic-entry-{i}",
                "source_id": f"synthetic-{name}",
                "ordinal": i,
                "kind": kind,
                "reported_actor_type": "SYNTHETIC test agent",
                "task_key": "SYNTHETIC example task",
            }
            for i, kind in enumerate(("task", "claimed", "progress", "result"), 1)
        ]
        job = hashlib.sha256(f"aa-browser-synthetic-{name}".encode()).hexdigest()[:32]
        examples = {
            f"SYNTHETIC-{name}-observations.json": records,
            f"SYNTHETIC-{name}-private-report.json": synthetic_private_response(job),
        }
        for filename, data in examples.items():
            with (output / filename).open("x", encoding="utf-8") as target:
                target.write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
