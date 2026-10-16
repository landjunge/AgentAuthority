"""Fresh random-key dm-crypt epoch. No keyfile, no recovery copy, no auto restore."""

import json
import os
import pwd
import secrets
import subprocess
from pathlib import Path


def run(args, **kw):
    return subprocess.run(args, check=True, timeout=30, capture_output=True, **kw)


def main():
    os.umask(0o077)
    # This initializer must itself be inside the swap-disabled aggregate cgroup.
    assert "aa-private.slice" in Path("/proc/self/cgroup").read_text()
    assert (
        Path("/sys/fs/cgroup/aa.slice/aa-private.slice/memory.swap.max").read_text().strip() == "0"
    )
    users = ["aa-api", "aa-signer", "aa-verifier", "aa-runner", "aa-registrar"]
    for name in users:
        try:
            pwd.getpwnam(name)
        except KeyError:
            run(
                [
                    "useradd",
                    "--system",
                    "--user-group",
                    "--no-create-home",
                    "--home-dir",
                    "/nonexistent",
                    "--shell",
                    "/usr/sbin/nologin",
                    name,
                ]
            )
        else:
            raise RuntimeError("existing account must be reviewed")
    for name, number in [("aa-test-a", 61101), ("aa-test-b", 61102)]:
        try:
            pwd.getpwuid(number)
        except KeyError:
            pass
        else:
            raise RuntimeError("existing test UID")
        run(["groupadd", "--gid", str(number), name])
        run(
            [
                "useradd",
                "--uid",
                str(number),
                "--gid",
                str(number),
                "--no-create-home",
                "--home-dir",
                "/nonexistent",
                "--shell",
                "/usr/sbin/nologin",
                name,
            ]
        )
    base = Path("/var/lib/aa-private")
    base.mkdir(mode=0o700)
    image = base / "epoch.ciphertext"
    with image.open("xb") as f:
        f.truncate(256 * 1024 * 1024)
    loop = run(["losetup", "--find", "--show", str(image)]).stdout.decode().strip()
    key = secrets.token_bytes(64)
    run(
        [
            "cryptsetup",
            "open",
            "--type",
            "plain",
            "--cipher",
            "aes-xts-plain64",
            "--key-size",
            "512",
            "--key-file",
            "-",
            "--keyfile-size",
            "64",
            loop,
            "aa-private-epoch",
        ],
        input=key,
    )
    del key
    run(["mkfs.ext4", "-q", "-m", "0", "-O", "^has_journal", "/dev/mapper/aa-private-epoch"])
    mount = base / "secure"
    mount.mkdir(mode=0o700)
    run(["mount", "-o", "nodev,nosuid,noexec,noatime", "/dev/mapper/aa-private-epoch", str(mount)])
    base.chmod(0o711)
    mount.chmod(0o711)
    for name in ["api", "signer", "verifier", "runner", "registrar"]:
        p = mount / name
        p.mkdir(mode=0o700)
        user = pwd.getpwnam("aa-" + name)
        os.chown(p, user.pw_uid, user.pw_gid)
    p = mount / "collector"
    p.mkdir(mode=0o700)
    p = mount / "verdicts"
    p.mkdir(mode=0o750)
    p.chmod(0o750)
    os.chown(p, pwd.getpwnam("aa-verifier").pw_uid, pwd.getpwnam("aa-signer").pw_gid)
    runtime = Path("/run/aa-private")
    (runtime / "epoch").write_text(secrets.token_hex(16))
    record = {
        "mapping": "aa-private-epoch",
        "loop": loop,
        "ciphertext": str(image),
        "mount": str(mount),
        "size_bytes": 256 * 1024 * 1024,
        "key_backup": False,
        "on_reboot": "fail closed; kernel-only epoch key lost; no automatic new epoch",
        "plaintext_recovery": False,
        "journal": False,
    }
    Path("/var/lib/aa-private-install-20261017/storage.json").write_text(
        json.dumps(record, indent=2)
    )
    print(json.dumps(record))


if __name__ == "__main__":
    main()
