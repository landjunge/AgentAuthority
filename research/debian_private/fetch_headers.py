"""Authenticate historical matching Debian headers without changing apt sources."""

import hashlib
import lzma
import subprocess
import urllib.request
from pathlib import Path

root = Path("/var/lib/aa-private-install-20261017/headers")
root.mkdir(mode=0o700, exist_ok=True)
base = "https://snapshot.debian.org/archive/debian-security/20260807T000000Z/"


def fetch(name):
    with urllib.request.urlopen(base + name, timeout=45) as response:
        data = response.read(32 * 1024 * 1024)
        assert not response.read(1), "download bound"
        return data


release = fetch("dists/trixie-security/InRelease")
(root / "InRelease").write_bytes(release)
subprocess.run(
    [
        "gpgv",
        "--keyring",
        "/usr/share/keyrings/debian-archive-keyring.gpg",
        str(root / "InRelease"),
    ],
    check=True,
    timeout=10,
)
index_name = "main/binary-amd64/Packages.xz"
section = release.decode().split("SHA256:\n")[1].split("\nSHA512:")[0]
expected = next(
    line.split()[0]
    for line in section.splitlines()
    if len(line.split()) == 3 and line.split()[2] == index_name
)
index = fetch("dists/trixie-security/" + index_name)
assert hashlib.sha256(index).hexdigest() == expected
(root / "Packages.xz").write_bytes(index)
packages = {}
for paragraph in lzma.decompress(index).decode().split("\n\n"):
    fields = dict(
        l.split(": ", 1) for l in paragraph.splitlines() if ": " in l and not l.startswith(" ")
    )
    if fields.get("Package") in (
        "linux-headers-6.12.101+deb13-amd64",
        "linux-headers-6.12.101+deb13-common",
        "linux-kbuild-6.12.101+deb13",
    ):
        assert fields["Version"] == "6.12.101-1"
        data = fetch(fields["Filename"])
        assert (
            len(data) == int(fields["Size"])
            and hashlib.sha256(data).hexdigest() == fields["SHA256"]
        )
        p = root / Path(fields["Filename"]).name
        p.write_bytes(data)
        packages[fields["Package"]] = {"sha256": fields["SHA256"], "file": str(p)}
assert len(packages) == 3
import json

(root / "provenance.json").write_text(
    json.dumps(
        {
            "signed_index_sha256": expected,
            "historical_validity": "Archived matching headers; no current repository or security setting changed",
            "packages": packages,
        },
        indent=2,
    )
)
print(json.dumps(packages))
