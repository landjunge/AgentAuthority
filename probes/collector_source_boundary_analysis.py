"""Isolated research: fail-closed treatment of unauthenticated collector claims.

This is a *policy simulation*, NOT a detector of compromised sources.
The caller must not treat a collector's self-reported provenance, C=JA,
matching fstat values, or the SHA-256 manifest as source authentication.
The frozen Run 03 observer and all archived measurements stay unchanged.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


VALID = {"DIESELBE", "VERSCHIEDEN", "UNBEKANNT"}
GTS = (1, 2, 3, 4, 7)


def quarantine_unattested_claim(raw: object) -> dict[str, Any]:
    """No independent authentication channel is supplied: positive claims are held.

    Intentionally does not accept a bool or a token supplied by the collector
    as 'proof'. A trust anchor outside the attacker's control remains future work.
    """
    claimed = raw.get("A") if isinstance(raw, dict) else None
    if claimed not in VALID:
        claimed = None
    return {
        "A": "UNBEKANNT",
        "raw_A": claimed,
        "reason": "Quellenherkunft nicht unabhaengig belegt",
        "source_authenticated": False,
        "positive_identity_authorized": False,
    }


def _verified_manifest(folder: Path, manifest_name: str) -> None:
    manifest = json.loads((folder / manifest_name).read_text(encoding="utf-8"))
    if manifest.get("algorithm") != "sha256" or not isinstance(manifest.get("files"), dict):
        raise ValueError("invalid_manifest")
    for name, expected in manifest["files"].items():
        path = (folder / name).resolve()
        try:
            path.relative_to(folder.resolve())
        except ValueError as exc:
            raise ValueError("external_manifest_file") from exc
        if not path.is_file():
            raise ValueError("missing_manifest_file")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("integrity_mismatch")


def audit_run03(root: Path) -> dict[str, Any]:
    """Read frozen evidence: guard is evaluated BEFORE the separate I/O reference."""
    pre, post = root / "pre-gt", root / "post-gt"
    _verified_manifest(pre, "pre-gt-manifest.json")
    _verified_manifest(post, "post-gt-manifest.json")
    cases = []
    for number in range(1, 8):
        raw = json.loads((pre / "responses" / f"P{number}.json").read_text())[
            "raw_observer_abcd"
        ]
        guarded = quarantine_unattested_claim(raw)
        # Deliberately AFTER guard calculation; not an input to guard.
        gt = None
        if number in GTS:
            gt = json.loads(
                (post / "ground-truth" / f"C{number}.json").read_text()
            )["truth"]
            if gt not in ("DIESELBE", "VERSCHIEDEN"):
                raise ValueError("missing_independent_ground_truth")
        cases.append({
            "case": f"C{number}",
            "raw_A": raw["A"],
            "raw_C": raw["C"],
            "guarded_A": guarded["A"],
            "ground_truth": gt,
            "raw_wrong": gt is not None and raw["A"] in (
                "DIESELBE", "VERSCHIEDEN"
            ) and raw["A"] != gt,
            "guarded_wrong": gt is not None and guarded["A"] in (
                "DIESELBE", "VERSCHIEDEN"
            ) and guarded["A"] != gt,
        })
    return {
        "status": "RESEARCH_ONLY_NOT_AUTHENTICATION",
        "cases": cases,
        "ground_truth_cases": len(GTS),
        "raw_wrong": sum(case["raw_wrong"] for case in cases),
        "guarded_wrong": sum(case["guarded_wrong"] for case in cases),
        "raw_positive": sum(case["raw_A"] in ("DIESELBE", "VERSCHIEDEN") for case in cases),
        "guarded_positive": sum(case["guarded_A"] in ("DIESELBE", "VERSCHIEDEN") for case in cases),
        "guarded_unknown": sum(case["guarded_A"] == "UNBEKANNT" for case in cases),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_run03(args.archive), ensure_ascii=False, indent=2))
