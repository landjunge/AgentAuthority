#!/usr/bin/env python3
"""Run opt-in native UI regressions in a logged-in graphical macOS session."""

import argparse
import json
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for lang, size in [("de", "1680x960"), ("en", "1150x730")]:
        output = args.output.resolve() / f"native-regression-{lang}.json"
        output.unlink(missing_ok=True)
        subprocess.run(
            [
                str(args.executable.resolve()),
                "--lang",
                lang,
                "--size",
                size,
                "--ui-regression-json",
                str(output),
            ],
            check=True,
            timeout=45,
        )
        report = json.loads(output.read_text(encoding="utf-8"))
        failures = [key for key, value in report["checks"].items() if value is not True]
        if not report["passed"] or failures:
            raise SystemExit(f"FAIL {lang}/{size}: {failures}")
        print(f"PASS {lang}/{size}: {report['check_count']} native UI checks")


if __name__ == "__main__":
    main()
