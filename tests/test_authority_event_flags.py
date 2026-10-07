"""Explicit event-export disable values must work inside and outside pytest."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab.models import ActionRequest
from lab.validator import Lab


def set_test_context(monkeypatch, under_pytest: bool) -> None:
    if under_pytest:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "event-flag-regression (call)")
    else:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)


@pytest.mark.parametrize("under_pytest", [True, False])
@pytest.mark.parametrize("flag", ["0", "false", "off", "no", " 0 ", " FALSE ", " Off ", " NO "])
def test_explicit_disable_never_writes_events(
    tmp_path: Path, monkeypatch, under_pytest: bool, flag: str
) -> None:
    set_test_context(monkeypatch, under_pytest)
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS", flag)
    out = tmp_path / "unused-export" / "authority-events.jsonl"
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(out))

    lab = Lab()
    allowed = lab.submit(ActionRequest("A", "file.write", "src/app.py", {}, "wf-flags"))
    denied = lab.submit(
        ActionRequest("A", "file.write", "config/security-policy.json", {}, "wf-flags")
    )

    assert allowed.allow is True
    assert denied.allow is False
    assert not out.exists()
    assert not out.parent.exists()


@pytest.mark.parametrize("under_pytest", [True, False])
@pytest.mark.parametrize("flag", [None, "", "   ", "1", "unexpected-nonempty-value"])
def test_existing_export_defaults_and_nonempty_values_are_preserved(
    tmp_path: Path, monkeypatch, under_pytest: bool, flag: str | None
) -> None:
    set_test_context(monkeypatch, under_pytest)
    if flag is None:
        monkeypatch.delenv("LAB_AUTHORITY_EVENTS", raising=False)
    else:
        monkeypatch.setenv("LAB_AUTHORITY_EVENTS", flag)
    out = tmp_path / "export" / "authority-events.jsonl"
    monkeypatch.setenv("LAB_AUTHORITY_EVENTS_PATH", str(out))

    decision = Lab().submit(ActionRequest("A", "file.write", "src/app.py", {}, "wf-defaults"))

    assert decision.allow is True
    should_export = bool(flag and flag.strip()) or not under_pytest
    assert out.exists() is should_export
    if should_export:
        assert len(out.read_text(encoding="utf-8").splitlines()) == 2
    else:
        assert not out.parent.exists()
