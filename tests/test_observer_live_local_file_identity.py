"""Synthetic parser boundary checks, not additional filesystem experiments."""
from copy import deepcopy

import pytest

from observer_research import infer_live_local_file_identity


def view():
    return [{"run": 1, "kind": "live_local_file_refs", "value": {
        "scope": {"os": "Linux", "filesystem": "tmpfs", "same_collection_process": True,
                  "live_handle_overlap_confirmed": True},
        "references": [{"st_dev": 34, "st_ino": 100, "regular_file": True},
                       {"st_dev": 34, "st_ino": 100, "regular_file": True}],
    }}]


@pytest.mark.parametrize("field,invalid", [
    ("os", "other"), ("filesystem", "other"), ("same_collection_process", False),
    ("live_handle_overlap_confirmed", False), ("live_handle_overlap_confirmed", 1),
])
def test_missing_scope_never_enables_native_identity(field, invalid):
    rows = view()
    rows[0]["value"]["scope"][field] = invalid
    # Also guard native inequality: it cannot bypass the lifetime prerequisite.
    for inode in (100, 101):
        rows[0]["value"]["references"][1]["st_ino"] = inode
        assert infer_live_local_file_identity(rows, 1)["A"] == "UNBEKANNT"
    del rows[0]["value"]["scope"][field]
    assert infer_live_local_file_identity(rows, 1)["A"] == "UNBEKANNT"


@pytest.mark.parametrize("field,invalid", [
    ("st_dev", True), ("st_dev", -1), ("st_ino", False), ("st_ino", 0),
    ("st_ino", "100"), ("regular_file", False), ("regular_file", 1),
])
def test_non_native_or_non_regular_reference_cannot_prove_identity(field, invalid):
    rows = view()
    rows[0]["value"]["references"][1][field] = invalid
    assert infer_live_local_file_identity(rows, 1)["A"] == "UNBEKANNT"
    del rows[0]["value"]["references"][1][field]
    assert infer_live_local_file_identity(rows, 1)["A"] == "UNBEKANNT"


@pytest.mark.parametrize("rows,run", [
    (None, 1), ([None], 1), ([], 1), (view(), True), (view(), 0), (view(), 2),
    ([{"kind": "live_local_file_refs", "value": {}}], 1),
    ([{"run": True, "kind": "live_local_file_refs", "value": {}}], 1),
    ([{"run": 1, "kind": [], "value": "inert_unstructured_input"}], 1),
    ([{"run": 1, "kind": "path_pair", "value": ["A", "A"]}], 1),
    ([{"run": 1, "kind": "content_equal", "value": True}], 1),
    ([{"run": 1, "kind": "content_hash_pair", "value": ["same", "same"]}], 1),
])
def test_unbound_or_wrong_evidence_is_unknown_without_echo(rows, run):
    result = infer_live_local_file_identity(rows, run)
    assert set(result) == {"A", "B", "C"}
    assert result["A"] == "UNBEKANNT"
    assert "inert_unstructured_input" not in str(result)


def test_conflicting_pair_observations_do_not_pick_a_preferred_result():
    rows = view()
    changed = deepcopy(rows[0])
    changed["value"]["references"][1]["st_ino"] = 101
    assert infer_live_local_file_identity(rows + [changed], 1)["A"] == "UNBEKANNT"


@pytest.mark.parametrize("mutate", [
    lambda r: r[0].update(path="inert_extra"),
    lambda r: r[0]["value"].update(content_hash="inert_extra"),
    lambda r: r[0]["value"]["references"].pop(),
    lambda r: r[0]["value"].update(scope=None),
])
def test_non_exact_native_shape_is_not_accepted(mutate):
    rows = view()
    mutate(rows)
    assert infer_live_local_file_identity(rows, 1)["A"] == "UNBEKANNT"
