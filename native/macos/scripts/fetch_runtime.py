#!/usr/bin/env python3
"""Fetch a pinned, SHA-256-verified, relocatable Intel Python runtime; no installation."""

import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/astral-sh/python-build-standalone/releases/download/20261009/cpython-3.12.15%2B20261009-x86_64-apple-darwin-install_only_stripped.tar.gz"
SHA256 = "fb3187d95334813b88940db0f1ca57b84cedfd552739c3a5771c3ea0e49988c9"
SIZE = 24751118


def main():
    cache = ROOT / ".runtime"
    cache.mkdir(exist_ok=True)
    archive = cache / "cpython-3.12.15-intel.tar.gz"
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=45) as response, archive.open("wb") as output:
            count = 0
            while chunk := response.read(1024 * 1024):
                count += len(chunk)
                if count > SIZE:
                    raise RuntimeError("Runtime archive exceeds pinned size")
                output.write(chunk)
    if archive.stat().st_size != SIZE or hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise RuntimeError("Runtime checksum mismatch; archive will not be extracted")
    destination = cache / "standalone"
    if not destination.exists():
        destination.mkdir()
        with tarfile.open(archive) as source:
            source.extractall(destination, filter="data")
    (cache / "runtime-source.json").write_text(
        json.dumps(
            {
                "url": URL,
                "sha256": SHA256,
                "bytes": SIZE,
                "target": "x86_64-apple-darwin",
                "python": "3.12.15",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(destination / "python/bin/python3.12")


if __name__ == "__main__":
    main()
