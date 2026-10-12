from __future__ import annotations

import pytest

from scripts import c1_cohort as c1


def test_exact_binomial_reference_limits_and_symmetry():
    assert c1.exact_interval(0, 8) == pytest.approx([0, 0.3694166476])
    assert c1.exact_interval(8, 8) == pytest.approx([0.6305833524, 1])
    assert c1.exact_interval(4, 8) == pytest.approx([0.15701277, 0.84298723])


@pytest.mark.parametrize("k,n", [(True, 8), (0, 0), (-1, 8), (9, 8)])
def test_invalid_denominator_cannot_create_interval(k, n):
    with pytest.raises(ValueError):
        c1.exact_interval(k, n)


def test_missing_new_experiments_never_become_passes():
    rows = c1.additional_rows(
        {
            "capture_score": {
                "package": "PASS",
                "rows": [
                    {
                        "fall": "aktuell",
                        "ist": {"reference_valid": True, "reference_target_present": True},
                    }
                ],
            }
        }
    )
    assert sum(r["status"] == "PASS" for r in rows) == 2
    assert all(r["status"] == "UNBEKANNT" for r in rows if r["case"].startswith(("A1", "B2")))
    assert c1.p7.p1 is c1.p7.p5.p1


def test_interrupted_and_failed_launch_positions_keep_fixed_denominator():
    row = {
        "full_matrix_complete": False,
        "original_matrix_pass": False,
        "cli_started": False,
        "model_proven": False,
        "timeout": False,
    }
    partial = c1.summarize([row] * 3)
    assert partial["N_nicht_versucht"] == 5 and partial["full_matrix_interval_95"] is None
    complete = c1.summarize([row] * 8)
    assert complete["N_Startversuche"] == 8 and complete["N_gestartet"] == 0
    assert complete["N_vollstaendig"] == 0 and complete["N_abgebrochen"] == 8


def test_preregistration_refuses_repository_output():
    with pytest.raises(ValueError):
        c1.freeze(c1.ROOT / "docs" / "c1-runs" / "not-a-runtime-target")


def test_source_change_retains_failed_position_and_stops_without_retry(tmp_path, monkeypatch):
    calls = 0

    def manifest(*args):
        nonlocal calls
        calls += 1
        if calls >= 3:
            raise ValueError("source/executable changed")
        return {"order": list(range(1, 9)), "source_head": "frozen", "timeout": 1, "post_window": 1}

    def failed_prepare(*args, **kwargs):
        raise OSError("prerequisite missing")

    monkeypatch.setattr(c1, "_manifest", manifest)
    monkeypatch.setattr(c1.p7, "prepare", failed_prepare)
    summary = c1.run_cohort(tmp_path, "frozen-digest")
    assert summary["N_Startversuche"] == 1 and summary["N_nicht_versucht"] == 7
    assert summary["rows"][0]["runner_failure"] == "OSError"
    assert summary["global_stop"] == "ValueError: source/executable changed"
    assert summary["full_matrix_interval_95"] is None and summary["retries"] == 0
    assert (tmp_path / "cohort-result.json").is_file()
