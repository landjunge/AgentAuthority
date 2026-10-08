"""Synthetic helper tests only; these are not C1-C7 Run-02 measurements."""
from __future__ import annotations

import fcntl
import os
import subprocess

import pytest

from probes import collector_manipulation_c1_c7_run02 as run02


ACTUAL_SAME = [(55, 100), (55, 100)]
ACTUAL_DIFFERENT = [(55, 100), (55, 200)]


@pytest.mark.parametrize("number", range(1, 8))
def test_frozen_packet_profiles_are_deterministic(number):
    actual = ACTUAL_DIFFERENT if number in (2, 3, 7) else ACTUAL_SAME
    packet, offered = run02.make_packet(number, actual, 55)
    refs = packet[0]["value"]["references"]
    assert packet[0]["run"] == 1
    assert packet[0]["kind"] == "live_local_file_refs"
    if number == 3:
        assert offered == [ACTUAL_DIFFERENT[0], ACTUAL_DIFFERENT[0]]
    elif number == 4:
        assert offered == [(55, 100), (55, 101)]
    elif number == 7:
        assert offered == [(55, run02.SYNTHETIC_INODE)] * 2
    else:
        assert offered == actual
    if number == 6:
        assert set(refs[1]) == {"st_dev", "st_ino"}
    else:
        assert refs[1]["regular_file"] is True


def test_c5_changes_only_final_second_fstat_projection():
    calls = []

    def delegated(fd):
        calls.append(fd)
        return run02.regular_result((55, 100))

    rows = [
        run02._project_fstat(5, index, ordinal, ACTUAL_SAME, delegated, 70 + index)
        for ordinal, index in enumerate((1, 2, 1, 2), 1)
    ]
    assert [source for _, source in rows] == [
        "delegated", "delegated", "delegated", "manipulated"
    ]
    assert [run02.pair_from_result(value) for value, _ in rows] == [
        (55, 100), (55, 100), (55, 100), (55, 101)
    ]
    assert calls == [71, 72, 71]


def test_c7_controls_all_five_interfaces_and_restores_originals():
    packet, offered = run02.make_packet(7, ACTUAL_DIFFERENT, 55)
    originals = (fcntl.fcntl, os.fstat, os.uname, subprocess.run, os.stat)
    observed = {}

    def fake_observer(events, run, *, handles):
        observed["flags"] = [fcntl.fcntl(fd, fcntl.F_GETFD) for fd in handles]
        observed["before"] = [run02.pair_from_result(os.fstat(fd)) for fd in handles]
        observed["system"] = os.uname().sysname
        mounted = subprocess.run(
            ["findmnt", "-T", "/tmp", "-n", "-o", "FSTYPE"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        observed["mount"] = (mounted.returncode, mounted.stdout)
        observed["device"] = os.stat("/tmp").st_dev
        observed["after"] = [run02.pair_from_result(os.fstat(fd)) for fd in handles]
        return {"A": "DIESELBE", "B": "synthetic", "C": "JA", "D": "limit"}

    journal = []
    answer, restored = run02.invoke_with_wrappers(
        packet, [70, 71], 7, offered, journal, observer=fake_observer
    )
    assert answer["A"] == "DIESELBE"
    assert restored
    assert (fcntl.fcntl, os.fstat, os.uname, subprocess.run, os.stat) == originals
    assert observed == {
        "flags": [0, 0],
        "before": [(55, run02.SYNTHETIC_INODE)] * 2,
        "system": "Linux",
        "mount": (0, "tmpfs\n"),
        "device": 55,
        "after": [(55, run02.SYNTHETIC_INODE)] * 2,
    }
    assert [row["operation"] for row in journal] == [
        "fcntl", "fcntl", "fstat", "fstat", "uname", "run", "stat", "fstat", "fstat"
    ]
    assert all(row["source"] == "manipulated" for row in journal)


def test_c7_real_observer_sees_one_internally_consistent_false_source():
    packet, offered = run02.make_packet(7, ACTUAL_DIFFERENT, 55)
    journal = []
    answer, restored = run02.invoke_with_wrappers(
        packet, [70, 71], 7, offered, journal
    )
    assert (answer["A"], answer["C"]) == ("DIESELBE", "JA")
    assert "Keine Packetherkunft" in answer["D"]
    assert restored
    assert [row["operation"] for row in journal] == [
        "fcntl", "fstat", "fcntl", "fstat", "uname", "run", "stat",
        "fcntl", "fstat", "fcntl", "fstat",
    ]
    assert all(row["source"] == "manipulated" for row in journal)


def test_wrappers_restore_when_observer_raises():
    packet, offered = run02.make_packet(7, ACTUAL_DIFFERENT, 55)
    originals = (fcntl.fcntl, os.fstat, os.uname, subprocess.run, os.stat)

    def fail(*args, **kwargs):
        os.fstat(70)
        raise RuntimeError("synthetic observer failure")

    with pytest.raises(RuntimeError, match="synthetic observer failure"):
        run02.invoke_with_wrappers(packet, [70, 71], 7, offered, [], observer=fail)
    assert (fcntl.fcntl, os.fstat, os.uname, subprocess.run, os.stat) == originals


def test_c6_real_parser_rejects_before_any_native_call_and_restores():
    packet, offered = run02.make_packet(6, ACTUAL_SAME, 55)
    journal = []
    answer, restored = run02.invoke_with_wrappers(packet, [70, 71], 6, offered, journal)
    assert (answer["A"], answer["C"]) == ("UNBEKANNT", "NEIN")
    assert journal == []
    assert restored


def test_c5_control_requires_one_visible_delta_and_restoration():
    journal = []
    for ordinal, (index, pair, source) in enumerate([
        (1, (55, 100), "delegated"),
        (2, (55, 100), "delegated"),
        (1, (55, 100), "delegated"),
        (2, (55, 101), "manipulated"),
    ], 1):
        journal.append({
            "operation": "fstat",
            "returned": True,
            "fstat_ordinal": ordinal,
            "handle_index": index,
            "native_pair": list(pair),
            "source": source,
        })
    control = run02.analyze_c5(journal, True)
    assert control["per_handle_pre_post_changed"] == [False, True]
    assert control["changed_projection_count"] == 1
    assert control["only_final_handle_2_manipulated"]
    assert control["wrappers_restored"]
