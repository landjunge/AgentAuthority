"""Exact existing tests/fixtures, privately staged on the encrypted Debian volume."""

import base64
import json
import subprocess
import zlib
from pathlib import Path

from research.debian_private.remote import bounded


def main():
    data = {}
    files = [
        Path("tests") / n
        for n in (
            "test_private_service.py",
            "test_private_service_retention.py",
            "test_private_service_security.py",
            "test_hosted_qualification.py",
            "conftest.py",
        )
    ]
    files += list(Path("lab").rglob("*.py"))
    files += [Path("docs") / "PRIVATE-SERVICE-OPENAPI-v1.json"]
    files += [
        Path("docs/private-service-20261016") / n
        for n in ("live-exchanges.json", "live-dispatch-pins.json")
    ]
    for path in files:
        data[str(path)] = base64.b64encode(path.read_bytes()).decode()
    # Actual Git objects, including original full tree hashes; no substitute
    # implementation or git shim for the pinned pre-fix reproduction.
    objects = []
    commit = subprocess.check_output(["git", "rev-parse", "09bc5f2"]).decode().strip()
    for expression in (
        commit,
        commit + "^{tree}",
        commit + ":research",
        commit + ":research/private_service",
        commit + ":research/private_service/http.py",
    ):
        oid = subprocess.check_output(["git", "rev-parse", expression]).decode().strip()
        kind = subprocess.check_output(["git", "cat-file", "-t", oid]).decode().strip()
        raw = subprocess.check_output(["git", "cat-file", kind, oid])
        packed = zlib.compress(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw)
        data[".git/objects/" + oid[:2] + "/" + oid[2:]] = base64.b64encode(packed).decode()
        objects.append(oid)
    for name, raw in {
        ".git/HEAD": commit + "\n",
        ".git/config": "[core]\nrepositoryformatversion=0\nbare=false\n",
    }.items():
        data[name] = base64.b64encode(raw.encode()).decode()
    payload = json.dumps(data)
    code = """import json,base64,pathlib,subprocess,pwd,os
try:u=pwd.getpwnam('aa-check')
except KeyError:
 subprocess.run(['useradd','--system','--user-group','--no-create-home','--home-dir','/nonexistent','--shell','/usr/sbin/nologin','aa-check'],check=True);u=pwd.getpwnam('aa-check')
root=pathlib.Path('/var/lib/aa-private/secure/qualification');root.mkdir(mode=0o700)
for name,value in json.loads(__PAYLOAD__).items():
 p=root/'code'/name;p.parent.mkdir(mode=0o700,parents=True,exist_ok=True);p.write_bytes(base64.b64decode(value));p.chmod(0o600)
(root/'tmp').mkdir(mode=0o700)
for p in [root,*root.rglob('*')]:os.chown(p,u.pw_uid,u.pw_gid)
print(json.dumps({'test_files':5,'fixture_scope':'historical synthetic regressions only, not current effect','git_objects':5,'encrypted_staging':True}))
""".replace("__PAYLOAD__", repr(payload))
    r = bounded(code.encode(), "stage-checks", 90)
    print(r.stdout.decode(), r.stderr.decode())
    raise SystemExit(r.returncode)


if __name__ == "__main__":
    main()
