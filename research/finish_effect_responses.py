"""Save case answers and frozen input controls before reading any oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from observer_research import infer_finish_effect


def responses(events: list[dict], run: int) -> dict:
    return {q: infer_finish_effect(events, run, q) for q in ("A", "B", "C")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--g3", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = args.events.read_bytes()
    events = [json.loads(line) for line in raw.splitlines() if line]
    starts = {e["run"] for e in events if e.get("kind") == "write_started"}
    # This contract executes one original write; never infer missing start binding.
    run = next(iter(starts)) if len(starts) == 1 else 0
    g3 = [json.loads(line) for line in args.g3.read_text().splitlines() if line]
    views = {
        "without_effect": [e for e in events if not e["kind"].startswith("write_effect")],
        "without_finish": [e for e in events if not e["kind"].startswith("finish_return")],
        "without_effect_binding": [{k: v for k, v in e.items()
                                    if k != "run" or not e["kind"].startswith("write_effect")}
                                   for e in events],
        "without_times_reversed": [{k: v for k, v in e.items() if k != "t_ns"}
                                    for e in reversed(events)],
        "allow_only": [e for e in g3 if e.get("event_type") == "authority.allowed"],
        "delivery_reversed": list(reversed(events)),
    }
    result = {"input_sha256": hashlib.sha256(raw).hexdigest(), "run": run,
              "answers": responses(events, run),
              "controls": {name: {"input": view, "answers": responses(view, run)}
                           for name, view in views.items()},
              "scope": "one_observed_fake_write_attempt; other_effects_unknown"}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    args.out.chmod(0o444)
    seal = args.out.with_name("sealed-response-sha256.json")
    with seal.open("x") as handle:
        json.dump({"sha256": hashlib.sha256(args.out.read_bytes()).hexdigest(),
                   "sealed_before_ground_truth_read": True}, handle, indent=2)
        handle.write("\n")
    seal.chmod(0o444)


if __name__ == "__main__":
    main()
