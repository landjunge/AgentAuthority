"""Fixed local study analyst; reads only native pairs and identity scope."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def analyze(scope: dict, pairs: list) -> dict:
    answer = {"A": "UNBEKANNT", "B": "UNBEKANNT",
              "evidence": "Gueltige Ausgangs-/Neumessung oder lokaler Scope fehlen.",
              "C": "Keine dauerhafte Eindeutigkeit oder Unmoeglichkeit von Wiederverwendung; "
                   "keine allgemeine Rate, andere Dateisysteme, Hosts, Neustarts, Cloud- oder "
                   "Netzwerkressourcen, kryptografische Quellechtheit oder zukuenftige ID-Loesung."}
    if (not isinstance(scope, dict) or scope != {"os": "Linux", "filesystem": "tmpfs",
                                               "maximum_new_lifetimes": 10000}
            or type(scope.get("maximum_new_lifetimes")) is not int
            or not isinstance(pairs, list) or not 2 <= len(pairs) <= 10001):
        return answer
    for pair in pairs:
        if (not isinstance(pair, dict) or set(pair) != {"st_dev", "st_ino"}
                or type(pair["st_dev"]) is not int or pair["st_dev"] < 0
                or type(pair["st_ino"]) is not int or pair["st_ino"] <= 0):
            return answer
    old = pairs[0]
    hit = next((number for number, pair in enumerate(pairs[1:], 1) if pair == old), None)
    selected = pairs[hit] if hit is not None else pairs[-1]
    answer["A"] = "UNBEKANNT" if hit is not None else "NEIN"
    answer["B"] = "NEIN" if hit is None and len(pairs) == 10001 else "UNBEKANNT"
    answer["evidence"] = (
        f"Ausgangspaar {old}, ausgewaehltes neues Paar {selected}; "
        f"{len(pairs)-1} neue native Messpaare. "
        + (f"Paarrekurrenz an Position {hit}; getrennte Lebenszeiten sind im Input nicht belegt."
           if hit is not None else
           "Paarungleichheit verneint nur die Identitaet der beiden Messreferenzen. "
           + ("Keine Ausgangspaarrekurrenz in der vollstaendigen eingefrorenen 10000er-Liste."
              if len(pairs) == 10001 else "Die eingefrorene native Liste ist unvollstaendig."))
        + " Kein Beleg fuer dauerhafte Eindeutigkeit, Fortbestand anderswo oder physische Freigabe.")
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw_files, input_errors = {}, []
    for name in ("original/native-pairs.jsonl", "original/identity-scope.json"):
        try:
            raw_files[name] = (args.input / name).read_bytes()
        except OSError as exc:
            input_errors.append({"file": name, "type": type(exc).__name__,
                                 "message": str(exc), "errno": exc.errno})
    try:
        scope = json.loads(raw_files["original/identity-scope.json"])
        pairs = [json.loads(line) for line in raw_files["original/native-pairs.jsonl"].splitlines()]
        answers = analyze(scope, pairs) if not input_errors else analyze({}, [])
    except (ValueError, KeyError) as exc:
        input_errors.append({"type": type(exc).__name__, "message": str(exc)})
        answers = analyze({}, [])
    result = {"input_files_sha256": {name: hashlib.sha256(raw).hexdigest()
                                     for name, raw in raw_files.items()},
              "input_errors": input_errors, "answers": answers}
    args.out.mkdir(parents=True, exist_ok=False)
    path = args.out / "before-comparison.json"
    with path.open("x") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
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
