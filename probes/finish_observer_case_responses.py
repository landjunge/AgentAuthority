"""Call unchanged observer interfaces; never read the separate ground truth.

This is test bookkeeping, not a new translator, observer, or UNKNOWN fallback.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import observer_research as observer

QUESTIONS = (
    ("A", "finish() war abgeschlossen, bevor der Schreibeffekt sichtbar wurde?"),
    ("B", "Kann der Observer den später sichtbaren Effekt sicher demselben vorher gestarteten Vorgang zuordnen?"),
    ("C", "Kann der Observer unterscheiden zwischen Workflow beendet und alle daraus entstandenen Effekte beendet?"),
)


def invoke(call) -> dict:
    try:
        return {"returned": call(), "exception": None}
    except (ValueError, TypeError, KeyError) as exc:
        return {"returned": None, "exception": {"type": type(exc).__name__, "message": str(exc)}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = args.events.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line]
    result = {
        "input_sha256": hashlib.sha256(raw).hexdigest(), "input_records": len(rows),
        "input_mapping": "NONE; exact existing G3 event dictionaries",
        "schema_check": invoke(lambda: observer.check_events(rows)),
        "responses": [
            {"question": key, "question_text": text,
             "query_run_argument": 1,
             "query_run_argument_is_correlated_to_workflow": False,
             "raw_observer_result": invoke(lambda: observer.infer(rows, 1, text))}
            for key, text in QUESTIONS
        ],
        "no_answer_fabricated": True,
        "boundary": "schema/interface availability only; no detector accuracy established",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    args.out.chmod(0o444)


if __name__ == "__main__":
    main()
