"""Offline scorer safety checks. Fixtures are not kernel/Writer evidence."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "a1_linux_score", Path(__file__).resolve().parents[1] / "research/a1_linux/score.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    identity = {"dev": 3, "inode": 9}
    process = {"pid": 42, "ppid": 7, "clock_ticks": 100, "start_ticks": 100}
    oracle = {
        "controller": {"boot_hash": "boot", "pid_namespace": "ns"},
        "rows": [
            {
                "file": identity,
                "action": "write",
                "result": 16,
                "process": process,
                "process_after": process,
                "stable": True,
                "pidfd_exit_seen": True,
                "exit_status": 0,
                "begin_ns": 20,
                "end_ns": 50,
            }
        ],
        "forged_claim_pid": 999,
    }
    capture = [
        {
            "ready": True,
            "boot_hash": "boot",
            "pid_namespace": "ns",
            "ready_ns": 10,
            "file": identity,
        },
        {
            "record": {
                "kind": 1,
                "dev": 3,
                "inode": 9,
                "tgid": 42,
                "ppid": 7,
                "start_ns": 1_000_000_000,
                "boot_hash": "boot",
                "count": 16,
                "result": 16,
                "entry_ns": 30,
                "exit_ns": 40,
            }
        },
        {
            "summary": {
                "perf_lost": 0,
                "pending": 0,
                "stats": {str(k): int(k < 3) for k in range(8)},
                "kprobe_profile": [["p_vfs_write", "1", "0"], ["r_vfs_write", "1", "0"]],
                "end_ns": 60,
            }
        },
    ]
    return capture, oracle


def test_valid_fixture_only_process_and_action():
    capture, oracle = fixture()
    result = MODULE.evaluate(capture, oracle)
    assert result["evidence"] == "BELEGT"
    assert result["correct"] == 1
    assert result["logical_agent_identity"] == "UNBEKANNT"


@pytest.mark.parametrize(
    "field,value", [("perf_lost", 1), ("pending", 1), ("kprobe_profile", None)]
)
def test_loss_or_unknown_coverage_no_positive(field, value):
    capture, oracle = fixture()
    capture[-1]["summary"][field] = value
    assert MODULE.evaluate(capture, oracle)["evidence"] == "UNBEKANNT"


@pytest.mark.parametrize("key", ["3", "4", "5", "7"])
def test_kernel_drop_or_collision_no_positive(key):
    capture, oracle = fixture()
    capture[-1]["summary"]["stats"][key] = 1
    assert MODULE.evaluate(capture, oracle)["evidence"] == "UNBEKANNT"


def test_kernel_profile_missed_no_positive():
    capture, oracle = fixture()
    capture[-1]["summary"]["kprobe_profile"][1][-1] = "1"
    assert MODULE.evaluate(capture, oracle)["evidence"] == "UNBEKANNT"


def test_pid_reuse_different_start_not_joined():
    capture, oracle = fixture()
    capture[1]["record"]["start_ns"] = 2_000_000_000
    result = MODULE.evaluate(capture, oracle)
    assert result["evidence"] != "BELEGT" and result["correct"] == 0


@pytest.mark.parametrize("field,value", [("inode", 10), ("tgid", 999), ("result", 0)])
def test_file_actor_or_return_mismatch_not_joined(field, value):
    capture, oracle = fixture()
    capture[1]["record"][field] = value
    assert MODULE.evaluate(capture, oracle)["evidence"] != "BELEGT"


def test_missing_start_unknown():
    capture, oracle = fixture()
    capture[1]["record"]["start_ns"] = 0
    assert MODULE.evaluate(capture, oracle)["evidence"] == "UNBEKANNT"


def test_foreign_boot_no_pid_join():
    capture, oracle = fixture()
    oracle["controller"]["boot_hash"] = "other"
    assert MODULE.evaluate(capture, oracle)["evidence"] == "UNBEKANNT"


def test_malformed_evidence_unknown():
    assert MODULE.evaluate([{"ready": True}, {"summary": {}}], {})["evidence"] == "UNBEKANNT"


def test_wrong_time_not_joined():
    capture, oracle = fixture()
    capture[1]["record"]["exit_ns"] = 100
    assert MODULE.evaluate(capture, oracle)["evidence"] != "BELEGT"
