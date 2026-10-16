"""Upload only source modules; private code backups before replacing own files."""

import base64
import json
from pathlib import Path

from research.debian_private.remote import run


def main():
    selected = {}
    for name in (
        "a2_linux",
        "a4_completion",
        "hosted_qualification",
        "private_service",
        "debian_private",
    ):
        for p in (Path("research") / name).glob("*.py"):
            if name == "debian_private" and p.name in (
                "remote.py",
                "upload.py",
                "prepare_host.py",
                "fetch_headers.py",
            ):
                continue
            selected[str(p)] = base64.b64encode(p.read_bytes()).decode()
    payload = json.dumps(selected)
    code = """import base64,json,pathlib,os,time,hashlib
data=json.loads(__PAYLOAD__)
root=pathlib.Path('/opt/aa-private')
backup=pathlib.Path('/var/lib/aa-private-install-20261017/source-backups')/str(time.time_ns())
changed=[]
for name,raw in data.items():
    p=root/name;value=base64.b64decode(raw)
    if p.exists() and p.read_bytes()!=value:
        saved=backup/name;saved.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        saved.write_bytes(p.read_bytes());saved.chmod(0o600)
    if not p.exists() or p.read_bytes()!=value:
        p.parent.mkdir(mode=0o755,parents=True,exist_ok=True)
        p.write_bytes(value);p.chmod(0o644);changed.append(name)
print(json.dumps({'files':len(data),'changed':changed,'source_sha256':{n:hashlib.sha256(base64.b64decode(v)).hexdigest() for n,v in data.items()}}))
""".replace("__PAYLOAD__", repr(payload))
    result = run(code.encode(), timeout=60)
    print(result.stdout.decode(), end="")
    print(result.stderr.decode(), end="")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
