"""Build a portable dependency-free source package and executable zipapp.

No installation/build backend, network, native application or research runtime
is needed. Packages contain only product Python, static UI, license and browser
documentation; local state, native binaries and private evidence are excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(output: Path) -> dict[str, object]:
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=normal"], cwd=ROOT, text=True
    )
    files = sorted(
        list((ROOT / "agent_authority").glob("*.py"))
        + list((ROOT / "agent_authority" / "browser_static").glob("*"))
        + list((ROOT / "docs").glob("BROWSER-*.md"))
        + [ROOT / "LICENSE", ROOT / "scripts" / "package_browser.py"]
    )
    contents = {str(p.relative_to(ROOT)): p.read_bytes() for p in files if p.is_file()}
    contents["__main__.py"] = (
        b"from agent_authority.browser import main\nraise SystemExit(main())\n"
    )
    hashes = {name: hashlib.sha256(raw).hexdigest() for name, raw in contents.items()}
    runtime_hashes = {
        name: digest
        for name, digest in hashes.items()
        if name.startswith("agent_authority/") or name == "__main__.py"
    }
    manifest = {
        "schema": "aa-browser-package-v1",
        "sourceCommit": commit,
        "sourceClean": not bool(status),
        "python": ">=3.12; qualified target 3.13.5",
        "role": "observer_only",
        "productionIntegration": "blocked",
        "files": hashes,
        "runtimeSha256": hashlib.sha256(
            json.dumps(runtime_hashes, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    contents["PACKAGE-MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = io.BytesIO()
    archive.write(b"#!/usr/bin/env python3\n")
    with zipfile.ZipFile(archive, "a", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, raw in sorted(contents.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, raw)
    package = output / "agent-authority-browser.pyz"
    package.write_bytes(archive.getvalue())
    package.chmod(0o755)
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{digest}  {package.name}\n")
    (output / "PACKAGE-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "package": str(package),
        "sha256": digest,
        "sourceCommit": commit,
        "sourceClean": not bool(status),
        "files": len(contents),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output), indent=2))


if __name__ == "__main__":
    main()
