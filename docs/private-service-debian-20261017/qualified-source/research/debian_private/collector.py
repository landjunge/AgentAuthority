"""Root collector, fixed signed synthetic scenario and kernel-peer runner only."""

import ctypes
import fcntl
import hashlib
import json
import os
import secrets
import select
import signal
import subprocess
import sys
import time
from pathlib import Path

from research.debian_private.ipc import RUNTIME, SECURE, guard_healthy, serve, uid
from research.private_service.crypto import sign
from research.private_service.protocol import (
    AUDIENCE,
    blob,
    blob_digest,
    canonical,
    digest,
    fields,
    fresh,
    now_ms,
    require,
    verify,
)
from research.private_service.retention import write_private

ROOT = Path(__file__).resolve().parents[2]


def clear_inherited_capabilities():
    """Retain the collector's bounded P/E set, pass no ambient/inheritable bits."""

    class Header(ctypes.Structure):
        _fields_ = [("version", ctypes.c_uint32), ("pid", ctypes.c_int)]

    class Data(ctypes.Structure):
        _fields_ = [
            ("effective", ctypes.c_uint32),
            ("permitted", ctypes.c_uint32),
            ("inheritable", ctypes.c_uint32),
        ]

    libc = ctypes.CDLL(None, use_errno=True)
    header = Header(0x20080522, 0)
    data = (Data * 2)()
    require(libc.capget(ctypes.byref(header), data) == 0, 503, "CAPGET_FAILED")
    for word in data:
        word.inheritable = 0
    require(libc.prctl(47, 4, 0, 0, 0) == 0, 503, "AMBIENT_CLEAR_FAILED")
    require(libc.capset(ctypes.byref(header), data) == 0, 503, "CAPSET_FAILED")


def healthy():
    guard_healthy()


def validate(value):
    fields(value, "binding request acceptance")
    binding = value["binding"]
    fields(binding, "tenant job_id job_sha256 acceptance_sha256")
    jid = binding["job_id"]
    require(
        type(jid) is str and len(jid) == 32 and all(c in "0123456789abcdef" for c in jid),
        422,
        "JOB_ID",
    )
    trusted = json.loads(Path("/etc/aa-private/collector.json").read_bytes())
    require(binding["tenant"] == "test-a", 403, "TENANT")
    clock = SECURE / "collector/clock-floor"
    now = max(now_ms(), int(clock.read_text()) if clock.exists() else 0)
    clock.write_text(str(now))
    require(
        digest(value["request"]) == binding["job_sha256"]
        and digest(value["acceptance"]) == binding["acceptance_sha256"],
        403,
        "BINDING",
    )
    for kind, kid, path in [
        ("request", "sender", "/v1/jobs"),
        ("acceptance", "receiver", f"/v1/jobs/{jid}/acceptances"),
    ]:
        packet = value[kind]
        b = packet["body"]
        require(verify(trusted[kid], packet), 403, "SIGNATURE")
        fresh(b, now)
        require(
            b["kid"] == kid
            and b["tenant"] == "test-a"
            and b["audience"] == AUDIENCE
            and b["method"] == "POST"
            and b["path"] == path,
            403,
            "SCOPE",
        )
    require(
        value["request"]["body"]["payload"]
        == {"scenario": "a4-write16-v1", "receiver_kid": "receiver"},
        403,
        "SCENARIO",
    )
    require(
        value["acceptance"]["body"]["payload"]
        == {"job_id": jid, "job_sha256": binding["job_sha256"]},
        403,
        "EXACT_ACCEPTANCE",
    )
    return binding


def clean_tree(path):
    # Only our fresh, generated, encrypted job tree. Never follow a symlink.
    assert str(path).startswith("/var/tmp/a4c-private-") or str(path).startswith(
        "/var/tmp/a1-research-a4-"
    )
    if not path.exists():
        return
    for parent, dirs, files in os.walk(path, topdown=False, followlinks=False):
        for name in files:
            p = Path(parent) / name
            assert p.is_file() and not p.is_symlink() and p.stat().st_nlink == 1
            p.unlink()
        for name in dirs:
            p = Path(parent) / name
            assert not p.is_symlink()
            p.rmdir()
    path.rmdir()


def collect(value):
    healthy()
    if value == {"op": "probe-check"}:
        from research.debian_private.kernel_check import run

        try:
            return run()
        except Exception as error:
            (SECURE / "collector/kernel-check-error.json").write_text(
                json.dumps({"type": type(error).__name__, "error": str(error)[:4096]})
            )
            raise
    if value == {"op": "guard-check"}:
        marker = RUNTIME / "guard-check"
        item = marker.lstat()
        require(item.st_uid == 0 and item.st_mode & 0o777 == 0o600, 403, "GUARD_TEST_OWNER")
        time.sleep(60)
        return {"unexpected": "guard did not stop"}
    binding = validate(value)
    require(
        not (SECURE / "collector/HARDSTOP").exists(), 503, "EPHEMERAL_RUNNER_STORAGE_UNQUALIFIED"
    )
    with (SECURE / "collector/runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        # The irreversible admission record is before any action; no retry on crash.
        consumed = SECURE / "collector" / ("consumed-" + binding["job_id"])
        write_private(consumed, b"consumed-no-automatic-rerun\n")
        return run_trial(binding)


def run_trial(binding):
    sys.path.insert(0, str(ROOT / "research/a4_completion"))
    sys.path.append(str(ROOT / "research/a2_linux"))
    import guest

    run_id = secrets.token_hex(16)
    vault = Path("/var/tmp/a4c-private-" + run_id)
    targetdir = Path("/var/tmp/a1-research-a4-" + run_id)
    targetdir.mkdir(mode=0o711)
    targetdir.chmod(0o711)
    target = targetdir / "target"
    target.touch(mode=0o600)
    os.chown(target, 61102, 61102)
    observer = None
    phase = "initialize"
    trial = None
    started = time.monotonic()
    try:
        registry = guest.initialize(vault, run_id)
        # A fresh registry CA lives only on the encrypted per-job store.
        from research.private_service.protocol import create_ca

        ca, public = create_ca(vault / "ca")
        bundle = {"ca_public_key": public, "registry": sign(ca, registry)}
        certificate = vault / "certificate.json"
        write_private(certificate, canonical(bundle))
        context = vault / "context.json"
        write_private(context, canonical(binding))
        sources = [
            ROOT / "research" / d / f
            for d, files in {
                "a4_completion": [
                    "guest.py",
                    "agent.py",
                    "observer.py",
                    "lifecycle.py",
                    "probes.py",
                    "verify.py",
                ],
                "a2_linux": ["protocol.py", "starter.py"],
                "debian_private": [
                    "collector.py",
                    "collector_observer.py",
                    "collector_trial.py",
                    "probe_profile.py",
                ],
            }.items()
            for f in files
        ]
        pins = {
            "run_id": run_id,
            "pinned_ca_public_key": public,
            "source_kid": "runner",
            "source_sha256": {
                str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources
            },
        }
        pin = {"pins": pins, "expected": binding}
        # API cannot write this verifier trust source, even if its DB is modified.
        p = SECURE / "verifier" / ("pin-" + binding["job_id"] + ".json")
        write_private(p, canonical(pin))
        os.chown(p, uid("aa-verifier"), uid("aa-verifier"))
        healthy()
        phase = "observer-start"
        observer = subprocess.Popen(
            [
                "/usr/bin/python3",
                "-B",
                "-m",
                "research.debian_private.collector_observer",
                str(target),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        require(bool(select.select([observer.stdout], [], [], 60)[0]), 503, "OBSERVER_TIMEOUT")
        first = observer.stdout.readline()
        require(json.loads(first).get("ready") is True, 503, "OBSERVER_NOT_READY")
        healthy()
        phase = "trial"
        trial = subprocess.run(
            [
                "/usr/bin/python3",
                "-B",
                "-m",
                "research.debian_private.collector_trial",
                str(vault),
                str(certificate),
                str(target),
                str(context),
            ],
            capture_output=True,
            timeout=50,
            check=False,
        )
        rest, errors = observer.communicate(timeout=25)
        phase = "capture-check"
        require(
            trial.returncode == 0 and observer.returncode == 0 and not errors and not trial.stderr,
            503,
            "CAPTURE_FAILED",
        )
        payload = {
            "registry": blob(canonical(bundle)),
            "capture": blob(first + rest),
            "trial": blob(trial.stdout),
        }
        payload["manifest"] = {
            "schema": "aa-evidence-v1",
            "source_id": "runner",
            "source_class": "controlled-linux-collector",
            "run_id": run_id,
            "complete": True,
            **{k + "_sha256": blob_digest(v) for k, v in payload.items()},
        }
        return {
            "pin": sign(SECURE / "collector/transport.pem", pin),
            "payload": payload,
            "duration_ms": int(1000 * (time.monotonic() - started)),
        }
    except Exception as error:
        # Private diagnostics: fixed synthetic children only, no raw evidence.
        (SECURE / "collector/last-failure.json").write_text(
            json.dumps(
                {
                    "phase": phase,
                    "type": type(error).__name__,
                    "code": getattr(error, "code", None),
                    "target_bytes": target.stat().st_size,
                    "trial_exit": None if trial is None else trial.returncode,
                    "trial_error": None
                    if trial is None
                    else trial.stderr.decode(errors="replace")[-2048:],
                }
            )
        )
        raise
    finally:
        if observer is not None and observer.poll() is None:
            observer.kill()
            observer.communicate(timeout=5)
        clean_tree(vault)
        clean_tree(targetdir)


if __name__ == "__main__":
    clear_inherited_capabilities()
    signal.alarm(1800)
    serve("collector", {uid("aa-runner")}, collect, output=262144)
