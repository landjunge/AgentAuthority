"""Synthetic error-path tests only; not the real frozen F1-F7 measurements."""
from copy import deepcopy
import errno
from types import SimpleNamespace

import pytest

import observer_research as observer


def packet():
    ref = {"st_dev": 34, "st_ino": 10, "regular_file": True}
    return [{"run": 1, "kind": "live_local_file_refs", "value": {
        "scope": {"os": "Linux", "filesystem": "tmpfs",
                  "same_collection_process": True, "live_handle_overlap_confirmed": True},
        "references": [ref, dict(ref)]}}]


def forbidden(*args, **kwargs):
    pytest.fail("native operation must not execute on this input")


def context(monkeypatch, inodes=(10, 10, 10, 10)):
    values = iter(inodes)
    monkeypatch.setattr(observer, "fcntl", SimpleNamespace(F_GETFD=observer.fcntl.F_GETFD,
                                                         fcntl=lambda *args: 0))
    monkeypatch.setattr(observer, "os", SimpleNamespace(
        fstat=lambda fd: SimpleNamespace(st_mode=0o100600, st_dev=34, st_ino=next(values)),
        uname=lambda: SimpleNamespace(sysname="Linux"),
        stat=lambda *args, **kwargs: SimpleNamespace(st_dev=34)))
    monkeypatch.setattr(observer, "subprocess", SimpleNamespace(
        run=lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="tmpfs\n"),
        TimeoutExpired=observer.subprocess.TimeoutExpired))


@pytest.mark.parametrize("handles", [None, [True, 8], [7, 7], [-1, 8]])
def test_flags_or_bad_runtime_arguments_cannot_invoke_native_checks(monkeypatch, handles):
    monkeypatch.setattr(observer.fcntl, "fcntl", forbidden)
    monkeypatch.setattr(observer.subprocess, "run", forbidden)
    result = observer.infer_current_local_file_identity(packet(), 1, handles=handles)
    assert (result["A"], result["C"]) == ("UNBEKANNT", "NEIN")


def test_closed_descriptor_is_checked_before_any_findmnt_allocation(monkeypatch):
    def closed(*args):
        raise OSError(errno.EBADF, "closed synthetic descriptor")
    monkeypatch.setattr(observer.fcntl, "fcntl", closed)
    monkeypatch.setattr(observer.os, "fstat", forbidden)
    monkeypatch.setattr(observer.subprocess, "run", forbidden)
    result = observer.infer_current_local_file_identity(packet(), 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("UNBEKANNT", "NEIN")
    assert "EBADF" in result["B"]


def test_current_pair_mismatch_cannot_be_overridden_by_claimed_flags(monkeypatch):
    context(monkeypatch, (11, 12, 11, 12))
    result = observer.infer_current_local_file_identity(packet(), 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("UNBEKANNT", "NEIN")
    assert "widersprechen" in result["B"]


def test_changed_pair_during_context_check_does_not_confirm_overlap(monkeypatch):
    context(monkeypatch, (10, 10, 10, 11))
    result = observer.infer_current_local_file_identity(packet(), 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("UNBEKANNT", "NEIN")


def test_ordered_binding_is_required_even_for_two_distinct_pairs(monkeypatch):
    context(monkeypatch, (10, 11, 10, 11))
    data = deepcopy(packet())
    data[0]["value"]["references"][0]["st_ino"] = 11
    result = observer.infer_current_local_file_identity(data, 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("UNBEKANNT", "NEIN")


def test_unavailable_mount_check_is_unjudgeable_not_confirmed(monkeypatch):
    context(monkeypatch)
    def unavailable(*args, **kwargs):
        raise FileNotFoundError(errno.ENOENT, "synthetic missing findmnt")
    monkeypatch.setattr(observer.subprocess, "run", unavailable)
    result = observer.infer_current_local_file_identity(packet(), 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("UNBEKANNT", "UNBEKANNT")


def test_descriptor_flag_zero_is_valid_and_original_packet_is_untouched(monkeypatch):
    context(monkeypatch)
    data = packet()
    before = deepcopy(data)
    result = observer.infer_current_local_file_identity(data, 1, handles=[7, 8])
    assert (result["A"], result["C"]) == ("DIESELBE", "JA")
    assert set(result) == {"A", "B", "C", "D"}
    assert data == before
