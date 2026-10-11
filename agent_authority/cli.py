"""Installable local observer; no store constructors or lab enforcement imports."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from agent_authority import __version__
from agent_authority.html_report import render_html
from agent_authority.report import build_report, render_text
from agent_authority.whiteboard import read_whiteboard


def _limit(value: str) -> int:
    number = int(value)
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError("Die Anzeigegrenze muss zwischen 1 und 100 liegen.")
    return number


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-authority",
        description="Agent Authority: lokale Beiträge beobachten und einordnen.",
    )
    parser.add_argument(
        "--version", action="version", version=f"Agent Authority {__version__} (observer preview)"
    )
    actions = parser.add_subparsers(dest="command", required=True)
    inspect = actions.add_parser("inspect", help="ThreadDesk-Whiteboard nur lesend auswerten.")
    inspect.add_argument(
        "--thread", required=True, help="ThreadDesk-Thread-ID (zwölf kleine Hexzeichen)."
    )
    inspect.add_argument(
        "--store", type=Path, default=Path.home() / ".threaddesk", help="Lokaler ThreadDesk-Store."
    )
    inspect.add_argument(
        "--format", choices=["text", "json", "html"], default="text", help="Berichtsformat."
    )
    inspect.add_argument(
        "--limit",
        type=_limit,
        default=20,
        help="Höchstens 1–100 Anzeigezeilen je Kategorie; Analyse bleibt vollständig.",
    )
    args = parser.parse_args(argv)
    report = build_report(read_whiteboard(args.store, args.thread), args.limit)
    if args.format == "html":
        output = render_html(report)
    elif args.format == "json":
        output = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        output = render_text(report)
    print(output)
    return 0 if report["source"]["complete_observed_read"] else 2
