"""Local fault-path checks; no Debian commands or network connections are executed."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "browser_service_ops", Path(__file__).parents[1] / "ops/browser_service.py"
)
ops = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ops)


class BrowserOperationsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="aa-ops-faults-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        for name in ("ROOT", "STATE", "CONFIG", "BACKUP", "SOCKET"):
            target = self.base / name
            target.mkdir()
            patcher = patch.object(ops, name, target)
            patcher.start()
            self.addCleanup(patcher.stop)
        for name in ("CADDY", "UNIT", "SLICE"):
            patcher = patch.object(ops, name, self.base / name)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.command = patch.object(ops, "run", return_value=b"").start()
        self.addCleanup(patch.stopall)
        self.subprocess = patch.object(ops.subprocess, "run").start()
        self.ready = patch.object(ops, "wait_ready").start()
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def test_partial_install_refuses_before_any_command_or_shared_write(self):
        package = self.base / "browser.pyz"
        package.write_bytes(b"synthetic package")
        with patch.object(ops.os, "getuid", return_value=0), self.assertRaises(ValueError):
            ops.install(package, ops.digest(package))
        self.command.assert_not_called()
        self.assertFalse(ops.CADDY.exists())

    def test_security_stop_latches_before_stopping_and_is_repeatable(self):
        def command(*_args):
            self.assertTrue((ops.ROOT / "SECURITY-STOP").is_file())

        self.command.side_effect = command
        ops.security_stop()
        ops.security_stop()
        self.assertEqual(self.command.call_count, 2)
        self.assertEqual((ops.ROOT / "SECURITY-STOP").stat().st_mode & 0o777, 0o600)

    def test_proxy_rollback_refuses_a_later_shared_caddy_change(self):
        ops.CADDY.write_text("foreign later change\n")
        (ops.ROOT / "activation.json").write_text(json.dumps({"caddy_after_sha256": "0" * 64}))
        with self.assertRaisesRegex(ValueError, "Caddy changed"):
            ops.rollback_proxy()
        self.assertEqual(ops.CADDY.read_text(), "foreign later change\n")
        self.command.assert_not_called()

    def releases(self):
        previous = ops.ROOT / "releases/previous"
        previous.mkdir(parents=True)
        (previous / "browser.pyz").write_bytes(b"previous synthetic release")
        source = self.base / "new.pyz"
        source.write_bytes(b"new synthetic release")
        package_hash = ops.digest(source)
        target = ops.ROOT / "releases" / package_hash[:20]
        target.mkdir()
        (target / "browser.pyz").write_bytes(source.read_bytes())
        (ops.ROOT / "current").symlink_to(previous)
        original_lstat = Path.lstat

        def fixture_owner(path):
            info = original_lstat(path)
            if path == target / "browser.pyz":
                return SimpleNamespace(st_mode=info.st_mode, st_uid=0)
            return info

        return previous, target, package_hash, fixture_owner

    def test_failed_code_start_restores_previous_release_without_clearing_a_stop(self):
        previous, _, package_hash, fixture_owner = self.releases()
        attempts = []

        def command(*args):
            if args[:2] == ("systemctl", "start"):
                attempts.append((ops.ROOT / "current").resolve())
                if len(attempts) == 1:
                    raise subprocess.CalledProcessError(1, args)

        self.command.side_effect = command
        with (
            patch.object(Path, "lstat", fixture_owner),
            self.assertRaises(subprocess.CalledProcessError),
        ):
            ops.rollback_code(package_hash)
        self.assertEqual((ops.ROOT / "current").resolve(), previous)
        self.assertEqual(len(attempts), 2)
        self.assertFalse((ops.ROOT / "SECURITY-STOP").exists())

    def test_failed_code_and_failed_restoration_latch_the_service(self):
        previous, _, package_hash, fixture_owner = self.releases()

        def command(*args):
            if args[:2] == ("systemctl", "start"):
                raise subprocess.CalledProcessError(1, args)

        self.command.side_effect = command
        with (
            patch.object(Path, "lstat", fixture_owner),
            self.assertRaises(subprocess.CalledProcessError),
        ):
            ops.rollback_code(package_hash)
        self.assertEqual((ops.ROOT / "current").resolve(), previous)
        self.assertTrue((ops.ROOT / "SECURITY-STOP").exists())
        self.subprocess.assert_any_call(
            ["systemctl", "disable", "--now", ops.NAME], capture_output=True, check=False
        )

    def test_code_switch_cannot_clear_persistent_security_stop(self):
        (ops.ROOT / "SECURITY-STOP").write_text("operator stop")
        with self.assertRaisesRegex(ValueError, "remains latched"):
            ops.rollback_code("a" * 64)
        self.command.assert_not_called()


if __name__ == "__main__":
    unittest.main()
