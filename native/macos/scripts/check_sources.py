#!/usr/bin/env python3
"""Catalog completeness, UI key coverage, UTF-8 and NOTIFY-only collector checks."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads(
    (ROOT / "Sources/AuthorityCore/Resources/Strings.json").read_text(encoding="utf-8")
)
errors = []
for key, pair in catalog.items():
    if set(pair) != {"de", "en"} or not all(pair.values()):
        errors.append("Incomplete key: " + key)
    if set(re.findall(r"\{\w+\}", pair["de"])) != set(re.findall(r"\{\w+\}", pair["en"])):
        errors.append("Placeholder mismatch: " + key)
for path in (ROOT / "Sources").rglob("*.swift"):
    text = path.read_text(encoding="utf-8")
    for key in re.findall(r'(?:L|label|button)\("([a-zA-Z0-9_.]+)"', text):
        if key.endswith("."):
            continue
        if key not in catalog:
            errors.append(f"Unknown UI key: {key} ({path.name})")
    # Owned prose in controls must use the catalog; raw data/IDs and symbols are allowed.
    for text_literal in re.findall(
        r'(?:messageText|informativeText|placeholderString|toolTip)\s*=\s*"([^"]+)"', text
    ):
        if re.search(r"[A-Za-z]{3}.*\s+[A-Za-z]{3}", text_literal):
            errors.append(f"Hardcoded UI prose: {path.name}: {text_literal}")
for path in ROOT.rglob("*"):
    if any(part.startswith(".") or part == "build" for part in path.relative_to(ROOT).parts):
        continue
    if path.is_file() and path.suffix in {".swift", ".py", ".json", ".c", ".m", ".h", ".md"}:
        text = path.read_text(encoding="utf-8")
        if "\ufffd" in text or "\ufeff" in text:
            errors.append("Invalid text marker: " + str(path))
collector = (ROOT / "Collector/main.m").read_text()
if "ES_EVENT_TYPE_AUTH_" in collector or "es_respond_" in collector:
    errors.append("Collector must never implement authorization")
if "xpc_connection_set_peer_code_signing_requirement" not in collector:
    errors.append("Collector peer authentication missing")
if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {len(catalog)} DE/EN keys, UI references, UTF-8, NOTIFY-only collector.")
