"""Server-only private synthetic service operations. Invoke through with-debian-lock.py.

Install receives a reviewed zipapp; credentials/backups never leave the server.
The existing Caddy bind mount carries only a private socket, never source/state.
"""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import shutil
import socket
import stat
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path("/opt/agent-authority-browser")
STATE = Path("/var/lib/agent-authority-browser")
CONFIG = Path("/etc/agent-authority-browser")
BACKUP = Path("/var/backups/agent-authority-browser/20261017")
SOCKET = Path("/opt/4allpass/sites/.aa-transport")
CADDY = Path("/opt/4allpass/Caddyfile")
UNIT = Path("/etc/systemd/system/agent-authority-browser.service")
SLICE = Path("/etc/systemd/system/aa-browser.slice")
NAME = UNIT.name
ORIGIN = "https://v2202608211799501333.goodsrv.de"
PREFIX = "/agent-authority/"
KH_RELEASE = Path("/opt/ki-hilfezentrum-releases/601de6bbd521f0a4e783d394b5d231720c3ea808")
MARKER = "\t# agent-authority-private-20261017\n"


def run(*args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, **kwargs).stdout


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, data, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(fd, "wb") as f:
        f.write(data.encode() if isinstance(data, str) else data)
        f.flush()
        os.fsync(f.fileno())


def caddy_reload():
    run(
        "docker",
        "exec",
        "4allpass-caddy-1",
        "caddy",
        "validate",
        "--config",
        "/etc/caddy/Caddyfile",
        "--adapter",
        "caddyfile",
    )
    run(
        "docker",
        "exec",
        "4allpass-caddy-1",
        "caddy",
        "reload",
        "--config",
        "/etc/caddy/Caddyfile",
        "--adapter",
        "caddyfile",
    )


def status():
    return run(
        "systemctl",
        "show",
        NAME,
        "-p",
        "ActiveState",
        "-p",
        "SubState",
        "-p",
        "User",
        "-p",
        "Group",
        "-p",
        "Slice",
        "-p",
        "MemoryMax",
        "-p",
        "MemorySwapMax",
        "-p",
        "CPUQuotaPerSecUSec",
        "-p",
        "TasksMax",
        "-p",
        "MainPID",
        "-p",
        "NRestarts",
        text=True,
    )


def latch_security_stop():
    marker = ROOT / "SECURITY-STOP"
    if not marker.exists():
        write(
            marker, "Operator security stop: explicit operator clearance required before restart.\n"
        )


def wait_ready():
    """Private transport probe: a live anonymous401, no credentials in output/logs."""
    token = (STATE / "proxy.token").read_text().strip()
    request = (
        f"GET {PREFIX}api/session HTTP/1.0\r\nHost: {ORIGIN[8:]}\r\n"
        f"X-AA-Proxy-Token: {token}\r\n\r\n"
    ).encode("ascii")
    for _ in range(40):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(0.5)
                connection.connect(str(SOCKET / "browser.sock"))
                connection.sendall(request)
                if connection.recv(128).split(b"\r\n", 1)[0].split(b" ")[1:2] == [b"401"]:
                    return
        except OSError:
            pass
        time.sleep(0.1)
    raise RuntimeError("private application readiness failed")


def install(package, expected):
    require(
        os.getuid() == 0 and digest(package) == expected, "root and exact package hash required"
    )
    require(
        not any(p.exists() for p in (ROOT, STATE, CONFIG, UNIT, SLICE, SOCKET, BACKUP)),
        "existing or partial private installation; refuse duplicate provisioning",
    )
    require(MARKER not in CADDY.read_text(), "private route already present")
    BACKUP.mkdir(parents=True, mode=0o700)
    shutil.copy2(CADDY, BACKUP / "Caddyfile.before")
    before = {
        "caddy_sha256": digest(CADDY),
        "other_units": {
            n: hashlib.sha256(run("systemctl", "cat", n)).hexdigest()
            for n in (
                "ki-hilfezentrum.service",
                "aa-private-verifier.service",
                "aa-private-collector.service",
                "aa-private-watchdog.service",
            )
        },
    }
    require(
        digest(BACKUP / "Caddyfile.before") == before["caddy_sha256"],
        "shared Caddy changed during backup",
    )
    write(BACKUP / "before.json", json.dumps(before, indent=2))
    try:
        pwd.getpwnam("aa-browser")
    except KeyError:
        run(
            "useradd",
            "--system",
            "--user-group",
            "--home-dir",
            str(STATE),
            "--no-create-home",
            "--shell",
            "/usr/sbin/nologin",
            "aa-browser",
        )
    else:
        raise ValueError("existing aa-browser account; operator must inspect before provisioning")
    account = pwd.getpwnam("aa-browser")
    uid = account.pw_uid
    gid = account.pw_gid
    ROOT.mkdir(mode=0o750)
    os.chown(ROOT, 0, gid)
    release = ROOT / "releases" / expected[:20]
    release.mkdir(parents=True, mode=0o750)
    for p in (ROOT / "releases", release):
        os.chown(p, 0, gid)
        p.chmod(0o750)
    shutil.copyfile(package, release / "browser.pyz")
    os.chmod(release / "browser.pyz", 0o640)
    os.chown(release / "browser.pyz", 0, gid)
    # Separate runtime, exact bytes of already qualified Gunicorn + packaging.
    runtime = ROOT / "runtime"
    venv.EnvBuilder(with_pip=False).create(runtime)
    src = KH_RELEASE / "runtime/lib/python3.13/site-packages"
    dst = runtime / "lib/python3.13/site-packages"
    dependency_hashes = {}
    for name in ("gunicorn", "gunicorn-23.0.0.dist-info", "packaging", "packaging-25.0.dist-info"):
        shutil.copytree(src / name, dst / name, ignore=shutil.ignore_patterns("__pycache__"))
        for p in (dst / name).rglob("*"):
            if p.is_file():
                dependency_hashes[str(p.relative_to(dst))] = digest(p)
    for p in [runtime, *runtime.rglob("*")]:
        if not p.is_symlink():
            os.chown(p, 0, gid)
            p.chmod(0o750 if p.is_dir() or p.stat().st_mode & 0o111 else 0o640)
    write(
        ROOT / "runtime-provenance.json",
        json.dumps({"source": str(src), "files": dependency_hashes}, indent=2),
    )
    os.symlink(release, ROOT / "current")
    CONFIG.mkdir(mode=0o700)
    STATE.mkdir(mode=0o700)
    os.chown(STATE, uid, gid)
    SOCKET.mkdir(mode=0o700)
    os.chown(SOCKET, uid, gid)
    # No secret stdout: init's one-time values are captured in memory.
    output = run(
        "runuser",
        "-u",
        "aa-browser",
        "--",
        str(runtime / "bin/python"),
        "-B",
        str(release / "browser.pyz"),
        "init-synthetic",
        "--state",
        str(STATE / "data"),
        text=True,
    )
    credentials = {
        line.split(": ", 1)[0]: line.split(": ", 1)[1]
        for line in output.splitlines()
        if line.startswith(("alice: ", "bob: "))
    }
    require(
        set(credentials) == {"alice", "bob"},
        "synthetic initialization did not return expected accounts",
    )
    config_path = STATE / "data/config.json"
    config = json.loads(config_path.read_text())
    config["accounts"][0]["scopes"].append(
        {
            "sourceId": "hilfezentrum-synthetic",
            "jobId": "30000000-0000-4000-8000-000000000001",
            "adapters": ["report"],
        }
    )
    config_path.write_text(json.dumps(config))
    os.chown(config_path, uid, gid)
    config_path.chmod(0o600)
    import secrets

    token = secrets.token_urlsafe(48)
    write(STATE / "proxy.token", token)
    os.chown(STATE / "proxy.token", uid, gid)
    write(
        CONFIG / "operator-access.json",
        json.dumps({"url": ORIGIN + PREFIX, "synthetic": True, "accounts": credentials}, indent=2),
    )
    hashes = {
        name: run(
            "docker",
            "exec",
            "-i",
            "4allpass-caddy-1",
            "caddy",
            "hash-password",
            "--algorithm",
            "bcrypt",
            "--bcrypt-cost",
            "10",
            input=(password + "\n").encode(),
        )
        .decode()
        .strip()
        for name, password in credentials.items()
    }
    content = f"""[Unit]
Description=Private synthetic Agent Authority browser (single local worker)
After=docker.service
Requires=docker.service
ConditionPathExists=!{ROOT}/SECURITY-STOP
StartLimitIntervalSec=120
StartLimitBurst=3
[Service]
User=aa-browser
Group=aa-browser
Slice=aa-browser.slice
WorkingDirectory={ROOT}/current
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONPATH={ROOT}/current/browser.pyz
Environment=AA_BROWSER_ORIGIN={ORIGIN}
Environment=AA_BROWSER_PREFIX={PREFIX}
Environment=AA_BROWSER_STATE={STATE}/data
Environment=AA_BROWSER_PROXY_TOKEN_FILE={STATE}/proxy.token
Environment=AA_BROWSER_PROXY_TRANSPORT=unix
ExecStart={runtime}/bin/python -B -m gunicorn --bind unix:{SOCKET}/browser.sock --workers 1 --threads 1 --worker-class sync --timeout 20 --graceful-timeout 10 --limit-request-line 2048 --limit-request-fields 32 --limit-request-field_size 4096 --umask 0077 --access-logfile /dev/null --error-logfile /dev/null agent_authority.browser_wsgi:create_app()
Restart=on-failure
RestartSec=3
TimeoutStopSec=20
KillMode=control-group
UMask=0077
MemoryMax=256M
MemorySwapMax=0
CPUQuota=40%
TasksMax=16
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
PrivateDevices=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
RestrictAddressFamilies=AF_UNIX
CapabilityBoundingSet=
ReadWritePaths={STATE} {SOCKET}
[Install]
WantedBy=multi-user.target
"""
    write(UNIT, content, 0o644)
    write(
        SLICE,
        """[Unit]
Description=Private Agent Authority service and exclusive laboratory runner budget
[Slice]
MemoryMax=800M
MemorySwapMax=0
CPUQuota=40%
TasksMax=32
""",
        0o644,
    )
    # Preserve the inode: Caddyfile is an existing single-file Docker bind mount.
    text = CADDY.read_text()
    anchor = "v2202608211799501333.goodsrv.de {\n"
    require(text.count(anchor) == 1, "fixed Caddy host anchor unavailable")
    block = (
        MARKER
        + f"""\thandle /agent-authority {{
\t\tredir /agent-authority/ 308
\t}}
\thandle /agent-authority/* {{
\t\tbasic_auth {{
\t\t\talice {hashes["alice"]}
\t\t\tbob {hashes["bob"]}
\t\t}}
\t\treverse_proxy unix//sites/.aa-transport/browser.sock {{
\t\t\theader_up X-AA-Proxy-Token {token}
\t\t}}
\t}}
"""
    )
    after = text.replace(anchor, anchor + block)
    after_hash = hashlib.sha256(after.encode()).hexdigest()
    require(digest(CADDY) == before["caddy_sha256"], "shared Caddy changed; refuse overwrite")
    try:
        CADDY.write_text(after)
        CADDY.chmod(0o600)
        caddy_reload()
        run("systemctl", "daemon-reload")
        run("systemctl", "enable", "--now", NAME)
        wait_ready()
        require(
            digest(CADDY) == after_hash,
            "shared Caddy changed during activation; refuse to adopt unrelated bytes",
        )
        active = {
            "package_sha256": expected,
            "release": str(release),
            "origin": ORIGIN,
            "prefix": PREFIX,
            "synthetic": True,
            "caddy_after_sha256": after_hash,
            "unit_sha256": digest(UNIT),
            "slice_sha256": digest(SLICE),
        }
        write(ROOT / "activation.json", json.dumps(active, indent=2))
        print(json.dumps(active))
        print(status())
    except BaseException:
        latch_security_stop()
        subprocess.run(["systemctl", "disable", "--now", NAME], capture_output=True, check=False)
        if digest(CADDY) == after_hash:
            CADDY.write_bytes((BACKUP / "Caddyfile.before").read_bytes())
            CADDY.chmod(stat.S_IMODE((BACKUP / "Caddyfile.before").stat().st_mode))
            caddy_reload()
        raise


def security_stop():
    # Leave the route authenticated but return no application data.
    latch_security_stop()
    run("systemctl", "disable", "--now", NAME)
    print(
        "security stop: persistently latched, disabled/inactive; authentication gate and private state retained"
    )


def rollback_proxy():
    active = json.loads((ROOT / "activation.json").read_text())
    require(digest(CADDY) == active["caddy_after_sha256"], "Caddy changed; refuse overwrite")
    before = json.loads((BACKUP / "before.json").read_text())
    require(
        digest(BACKUP / "Caddyfile.before") == before["caddy_sha256"], "Caddy backup hash mismatch"
    )
    security_stop()
    CADDY.write_bytes((BACKUP / "Caddyfile.before").read_bytes())
    CADDY.chmod(stat.S_IMODE((BACKUP / "Caddyfile.before").stat().st_mode))
    caddy_reload()
    print("private route removed; own service disabled; state, releases and backups retained")


def rollback_code(package_hash):
    require(
        len(package_hash) == 64 and all(c in "0123456789abcdef" for c in package_hash),
        "exact lowercase package hash required",
    )
    require(
        not (ROOT / "SECURITY-STOP").exists(),
        "security stop remains latched; code switch cannot clear it",
    )
    target = ROOT / "releases" / package_hash[:20]
    info = (target / "browser.pyz").lstat()
    require(
        stat.S_ISREG(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022,
        "root-owned immutable release package required",
    )
    require(digest(target / "browser.pyz") == package_hash, "release package hash mismatch")
    previous = (ROOT / "current").resolve(strict=True)
    new = ROOT / "current.next"
    require(not os.path.lexists(new), "unfinished previous code switch; inspect before retry")
    run("systemctl", "stop", NAME)
    try:
        os.symlink(target, new)
        os.replace(new, ROOT / "current")
        run("systemctl", "start", NAME)
        wait_ready()
    except BaseException:
        subprocess.run(["systemctl", "stop", NAME], capture_output=True, check=False)
        if new.is_symlink():
            new.unlink()
        os.symlink(previous, new)
        os.replace(new, ROOT / "current")
        try:
            run("systemctl", "start", NAME)
            wait_ready()
        except BaseException:  # noqa: BLE001 - restoration failure must leave the persistent stop latched.
            latch_security_stop()
            subprocess.run(
                ["systemctl", "disable", "--now", NAME], capture_output=True, check=False
            )
        raise
    print("pinned code switched; state retained; sessions revoked by stop")


if __name__ == "__main__":
    os.umask(0o077)
    require(os.geteuid() == 0, "server operations require root")
    action = sys.argv[1]
    if action == "install":
        install(Path(sys.argv[2]), sys.argv[3])
    elif action == "status":
        print(status())
    elif action == "security-stop":
        security_stop()
    elif action == "rollback-proxy":
        rollback_proxy()
    elif action == "rollback-code":
        rollback_code(sys.argv[2])
    else:
        raise SystemExit("unknown operation")
