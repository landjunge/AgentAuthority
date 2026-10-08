"""Invoke only the additive observer on seven fixed inputs; never read GT."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from observer_research import infer_live_local_file_identity
from probes.local_file_identity_capture import error_record, save


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    entries = {}
    for run in range(1, 8):
        name = f"T{run}.json"
        raw = None
        try:
            raw = (args.input / name).read_bytes()
            entries[name] = {"input_sha256": hashlib.sha256(raw).hexdigest(),
                             "answers": infer_live_local_file_identity(json.loads(raw), run)}
        except (OSError, ValueError) as exc:
            entries[name] = {"input_sha256": hashlib.sha256(raw).hexdigest() if raw else None,
                             "input_error": error_record(exc, "read_fixed_input"),
                             "answers": infer_live_local_file_identity([], run)}
    answers = args.out / "before-comparison.json"
    save(answers, entries)
    save(args.out / "sealed-sha256.json", {
        "answers_sha256": hashlib.sha256(answers.read_bytes()).hexdigest(),
        "saved_before_ground_truth_comparison": True,
        "input_files": [f"T{run}.json" for run in range(1, 8)],
    })


if __name__ == "__main__":
    main()
