"""One unchanged-observer invocation; pure requested-format mapping, no oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from observer_research import infer_live_local_file_identity
from probes.local_file_identity_capture import save


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    raw_input = args.input.read_bytes()
    # The filename, case, provenance, lifecycle and expected answers are not
    # supplied to the observer. Replay deliberately keeps its original run=1.
    original = infer_live_local_file_identity(json.loads(raw_input), 1)
    answer = {
        "input_sha256": hashlib.sha256(raw_input).hexdigest(), "query_run": 1,
        "raw_observer_abc": original,
        "requested_abcd": {"A": original["A"], "B": original["B"],
                           "C": "UNBEKANNT", "D": original["C"]},
        "validity_output_present": False,
        "validity_output_note": "Der unveraenderte Observer liefert keine gesonderte "
                                "aktuelle Gueltigkeitsantwort. C=UNBEKANNT ist nur "
                                "die Kennzeichnung dieser fehlenden Ausgabe, keine "
                                "neue Ableitung oder erkannte Ungueltigkeit.",
    }
    path = args.out / "answer.json"
    save(path, answer)
    save(args.out / "sealed-sha256.json", {
        "answer_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "saved_before_ground_truth_comparison": True,
    })


if __name__ == "__main__":
    main()
