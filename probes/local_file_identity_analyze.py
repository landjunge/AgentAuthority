"""Separate fixed-study analysis; no Ground Truth reader or resource operations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def analyze(data: dict) -> dict:
    limits = ("Nur gleichzeitig lebende regulaere lokale Dateien im selben Linux/tmpfs-"
              "Messprozess; keine Pfad-/Inhalts-/Revisionsidentitaet, Persistenz nach "
              "Handlefreigabe, Quellechtheit, Neustarts, fremde Maschinen oder Netzwerke.")
    unknown = {"A": "UNBEKANNT", "B": "Tragfaehige native Identitaet oder lokaler "
               "Lebendigkeitsscope fehlt; Pfad/Inhalt/Hash ersetzen sie nicht.", "C": limits}
    if not isinstance(data, dict) or set(data) != {"scope", "references"}:
        return unknown
    scope = data["scope"]
    if (not isinstance(scope, dict)
            or set(scope) != {"os", "filesystem", "same_collection_process", "live_handle_overlap_confirmed"}
            or scope["os"] != "Linux" or scope["filesystem"] != "tmpfs"
            or scope["same_collection_process"] is not True
            or scope["live_handle_overlap_confirmed"] is not True):
        return unknown
    rows = data["references"]
    if not isinstance(rows, list) or len(rows) != 2:
        return unknown
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"st_dev", "st_ino", "regular_file"}
                or row["regular_file"] is not True
                or type(row["st_dev"]) is not int or row["st_dev"] < 0
                or type(row["st_ino"]) is not int or row["st_ino"] <= 0):
            return unknown
    pairs = [(row["st_dev"], row["st_ino"]) for row in rows]
    same = pairs[0] == pairs[1]
    return {"A": "DIESELBE" if same else "VERSCHIEDEN",
            "B": f"Native fstat-Paare {pairs[0]} und {pairs[1]} sind "
                 + ("gleich" if same else "verschieden")
                 + "; beide regulaeren Dateien gleichzeitig offen im selben lokalen Scope.",
            "C": limits}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    entries = {}
    # These are the sole analyst input files; never enumerate/read Ground Truth.
    for name in ("observations/P1.json", "observations/P2.json", "observations/P3.json",
                 "controls/path_only.json", "controls/content_only.json", "controls/hash_only.json"):
        path = args.input / name
        raw = None
        try:
            raw = path.read_bytes()
            entries[name] = {"input_sha256": hashlib.sha256(raw).hexdigest(),
                             "answers": analyze(json.loads(raw))}
        except (OSError, ValueError) as exc:
            entries[name] = {"input_sha256": hashlib.sha256(raw).hexdigest()
                             if raw is not None else None, "answers": analyze({}),
                             "input_error": {"type": type(exc).__name__, "message": str(exc),
                                             "errno": getattr(exc, "errno", None)}}
    args.out.mkdir(parents=True, exist_ok=False)
    path = args.out / "before-comparison.json"
    with path.open("x") as handle:
        json.dump(entries, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    path.chmod(0o444)
    seal = args.out / "sealed-sha256.json"
    with seal.open("x") as handle:
        json.dump({"answers_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "saved_before_ground_truth_comparison": True}, handle, indent=2)
        handle.write("\n")
    seal.chmod(0o444)


if __name__ == "__main__":
    main()
