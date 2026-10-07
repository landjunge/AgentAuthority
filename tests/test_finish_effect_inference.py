"""Synthetic controls for the frozen one-write finish/effect contract."""
from copy import deepcopy
import itertools
import json
import unittest

from observer_research import infer_finish_effect


KINDS = ("write_started", "finish_return_before", "finish_return",
         "write_effect_before", "write_effect")
WRITE_KINDS = ("write_started", "write_effect_before", "write_effect")
UNKNOWN = {"A": "UNBEKANNT", "B": "UNBEKANNT", "C": "UNBEKANNT"}
AFTER = {"A": "JA", "B": "JA", "C": "JA"}
BEFORE = {"A": "NEIN", "B": "JA", "C": "JA"}
UNTIMED = {"A": "UNBEKANNT", "B": "JA", "C": "UNBEKANNT"}


def observations(finish=(10, 11), effect=(20, 21), start=1, run=1):
    times = (start, *finish, *effect)
    values = (True, True, True, False, True)
    return [{"run": run, "kind": kind, "value": value, "t_ns": timestamp}
            for kind, value, timestamp in zip(KINDS, values, times)]


class FinishEffectInferenceTests(unittest.TestCase):
    def assert_answers(self, rows, expected, run=1):
        results = {question: infer_finish_effect(rows, run, question)
                   for question in ("A", "B", "C")}
        self.assertEqual({question: result["answer"] for question, result in results.items()},
                         expected)
        for result in results.values():
            self.assertEqual(set(result), {"answer", "reason", "evidence"})
            self.assertIsInstance(result["reason"], str)
            self.assertLessEqual(len(result["reason"]), 80)
            self.assertTrue(set(result["evidence"]) <= set(KINDS))
        return results

    def test_full_bound_creation_after_finish(self):
        results = self.assert_answers(observations(), AFTER)
        self.assertEqual(results["A"]["evidence"], list(KINDS))
        self.assertEqual(results["B"]["evidence"], list(WRITE_KINDS))
        self.assertEqual(results["C"]["reason"],
                         "one_observed_write_after_finish_other_effects_unknown")

    def test_frozen_control_1_remove_both_effect_rows(self):
        rows = [row for row in observations() if row["kind"] not in
                ("write_effect_before", "write_effect")]
        self.assert_answers(rows, UNKNOWN)

    def test_frozen_control_2_remove_both_finish_rows(self):
        rows = [row for row in observations() if row["kind"] in WRITE_KINDS]
        results = self.assert_answers(rows, UNTIMED)
        self.assertEqual(results["B"]["evidence"], list(WRITE_KINDS))

    def test_frozen_control_3_remove_run_from_effect_rows(self):
        rows = observations()
        for row in rows:
            if row["kind"] in ("write_effect_before", "write_effect"):
                del row["run"]
        results = self.assert_answers(rows, UNKNOWN)
        self.assertTrue(all(result["reason"] == "unbound_observation"
                            for result in results.values()))

    def test_frozen_control_4_remove_timestamps_and_reverse(self):
        rows = [{key: value for key, value in row.items() if key != "t_ns"}
                for row in reversed(observations())]
        self.assert_answers(rows, UNTIMED)

    def test_frozen_control_5_raw_g3_allow_is_not_effect_or_finish(self):
        rows = [{"schema_version": "1", "event_type": "authority.allowed",
                 "decision": "ALLOW", "action": "file.write", "workflow_id": "same",
                 "span_id": "independent", "timestamp": "2026-10-08T00:00:00Z"}]
        results = self.assert_answers(rows, UNKNOWN)
        self.assertTrue(all(result["evidence"] == [] for result in results.values()))

    def test_frozen_control_6_reverse_reception_with_times(self):
        rows = observations()
        for question in ("A", "B", "C"):
            self.assertEqual(infer_finish_effect(rows, 1, question),
                             infer_finish_effect(list(reversed(rows)), 1, question))

    def test_all_delivery_permutations_preserve_complete_predictions(self):
        rows = observations()
        expected = {question: infer_finish_effect(rows, 1, question)
                    for question in ("A", "B", "C")}
        for permutation in itertools.permutations(rows):
            with self.subTest(order=[row["kind"] for row in permutation]):
                for question in ("A", "B", "C"):
                    self.assertEqual(infer_finish_effect(list(permutation), 1, question),
                                     expected[question])

    def test_explicit_effect_before_finish_is_nein_for_a_and_scoped_ja_for_c(self):
        results = self.assert_answers(observations(finish=(20, 21), effect=(10, 11)), BEFORE)
        self.assertEqual(results["C"]["reason"],
                         "one_observed_write_before_finish_other_effects_unknown")

    def test_equal_touching_and_overlapping_bounds_never_establish_order(self):
        cases = [((10, 20), (20, 30)), ((20, 30), (10, 20)),
                 ((10, 25), (20, 30)), ((20, 30), (10, 25)),
                 ((10, 10), (10, 10)), ((10, 30), (15, 20))]
        for finish, effect in cases:
            with self.subTest(finish=finish, effect=effect):
                self.assert_answers(observations(finish=finish, effect=effect), UNTIMED)

    def test_zero_width_intervals_and_zero_start_are_valid_when_separated(self):
        self.assert_answers(observations(finish=(0, 0), effect=(1, 1), start=0), AFTER)

    def test_missing_start_timestamp_does_not_become_new_required_field(self):
        rows = observations()
        del rows[0]["t_ns"]
        self.assert_answers(rows, AFTER)

    def test_missing_any_comparison_bound_retains_only_b(self):
        for index in range(1, 5):
            with self.subTest(kind=KINDS[index]):
                rows = observations()
                del rows[index]["t_ns"]
                self.assert_answers(rows, UNTIMED)

    def test_missing_any_required_measurement_does_not_select_a_subcase(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                rows = [row for row in observations() if row["kind"] != kind]
                self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)

    def test_identical_full_copies_collapse_without_mutating_input(self):
        rows = observations()
        delivered = rows + deepcopy(rows) + [deepcopy(rows[0])]
        original = deepcopy(delivered)
        self.assert_answers(delivered, AFTER)
        self.assertEqual(delivered, original)

    def test_distinct_same_kind_timestamps_are_not_cherry_picked(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                rows = observations()
                row = next(row for row in rows if row["kind"] == kind)
                rows.append({**row, "t_ns": row["t_ns"] + 1})
                expected = UNTIMED if kind.startswith("finish_") else UNKNOWN
                results = self.assert_answers(rows, expected)
                for question in ("A", "B", "C"):
                    self.assertEqual(results[question],
                                     infer_finish_effect(list(reversed(rows)), 1, question))

    def test_same_kind_conflicting_booleans_are_unknown(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                rows = observations()
                row = next(row for row in rows if row["kind"] == kind)
                rows.append({**row, "value": not row["value"]})
                self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)

    def test_partial_and_complete_copies_are_distinct_observations(self):
        rows = observations()
        duplicate = dict(rows[4])
        del duplicate["t_ns"]
        rows.append(duplicate)
        self.assert_answers(rows, UNKNOWN)

    def test_repeated_partial_rows_do_not_claim_duplicate_delivery_identity(self):
        for kind in WRITE_KINDS:
            with self.subTest(kind=kind):
                rows = observations()
                row = next(row for row in rows if row["kind"] == kind)
                del row["t_ns"]
                rows.append(dict(row))
                self.assert_answers(rows, UNKNOWN)

    def test_valid_other_runs_are_kept_separate(self):
        rows = observations() + observations(finish=(30, 31), effect=(10, 11), run=2)
        self.assert_answers(rows, AFTER, run=1)
        self.assert_answers(rows, BEFORE, run=2)
        self.assert_answers(rows, UNKNOWN, run=3)

    def test_malformed_kind_bound_to_other_run_does_not_poison_query(self):
        rows = observations() + [{"run": 2, "value": True, "t_ns": 10},
                                 {"run": 2, "kind": [], "value": True, "t_ns": 10}]
        self.assert_answers(rows, AFTER)

    def test_effect_rows_cannot_join_across_runs_or_matching_extra_metadata(self):
        for indices in ((3,), (4,), (3, 4), (0,)):
            with self.subTest(indices=indices):
                rows = observations()
                for index in indices:
                    rows[index]["run"] = 2
                self.assert_answers(rows, UNKNOWN)
        rows = observations()
        for row in rows:
            row["workflow_id"] = "same"
        del rows[4]["run"]
        self.assert_answers(rows, UNKNOWN)

    def test_known_kind_orphans_prevent_positive_claims_in_their_scope(self):
        for kind in KINDS:
            with self.subTest(kind=kind):
                rows = observations()
                orphan = dict(next(row for row in rows if row["kind"] == kind))
                del orphan["run"]
                rows.append(orphan)
                self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)

    def test_boolean_zero_negative_and_noninteger_run_are_never_binding(self):
        for bad_run in (True, False, 0, -1, 1.0, "1", None, [], {}):
            with self.subTest(run=bad_run):
                rows = observations()
                rows[4]["run"] = bad_run
                self.assert_answers(rows, UNKNOWN)
                self.assert_answers(observations(), UNKNOWN, run=bad_run)

    def test_present_invalid_times_are_unknown_in_each_relevant_scope(self):
        for kind in KINDS:
            for bad_time in (True, False, -1, 1.0, "1", None, [], {}):
                with self.subTest(kind=kind, time=bad_time):
                    rows = observations()
                    next(row for row in rows if row["kind"] == kind)["t_ns"] = bad_time
                    self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)

    def test_reversed_bounds_and_start_after_bounds_cannot_establish_a_or_c(self):
        cases = [observations(finish=(11, 10)), observations(effect=(21, 20)),
                 observations(start=12), observations(start=22)]
        for rows in cases:
            with self.subTest(rows=rows):
                self.assert_answers(rows, UNTIMED)

    def test_integer_values_are_not_booleans_and_missing_value_is_unknown(self):
        for kind in KINDS:
            for bad_value in (0, 1, "true", None, [], {}):
                with self.subTest(kind=kind, value=bad_value):
                    rows = observations()
                    next(row for row in rows if row["kind"] == kind)["value"] = bad_value
                    self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)
            rows = observations()
            del next(row for row in rows if row["kind"] == kind)["value"]
            self.assert_answers(rows, UNTIMED if kind.startswith("finish_") else UNKNOWN)

    def test_false_markers_and_preexisting_or_absent_target_do_not_prove_creation(self):
        for index in range(5):
            with self.subTest(kind=KINDS[index]):
                rows = observations()
                rows[index]["value"] = not rows[index]["value"]
                self.assert_answers(rows, UNTIMED if KINDS[index].startswith("finish_") else UNKNOWN)

    def test_allow_and_native_status_never_fill_missing_effect_or_finish(self):
        statuses = [{"run": 1, "kind": kind, "value": True, "t_ns": 15, "event": index}
                    for index, kind in enumerate(("native_end", "cli_end", "tool_end"), 1)]
        statuses.append({"run": 1, "decision": "ALLOW", "event_type": "authority.allowed"})
        self.assert_answers(statuses, UNKNOWN)
        writes = [row for row in observations() if row["kind"] in WRITE_KINDS]
        self.assert_answers(writes + statuses, UNTIMED)
        finishes = [row for row in observations() if row["kind"].startswith("finish_")]
        self.assert_answers(finishes + statuses, UNKNOWN)

    def test_extra_metadata_is_rejected_and_never_echoed(self):
        rows = observations()
        rows[4]["secret"] = "UNRELATED_PRIVATE_MARKER"
        results = self.assert_answers(rows, UNKNOWN)
        self.assertNotIn("UNRELATED_PRIVATE_MARKER", json.dumps(results))

    def test_malformed_inputs_return_unknown_without_historical_schema_exceptions(self):
        for rows in ([], [None], [[]], [{}], [{"kind": []}], None, {}):
            with self.subTest(rows=rows):
                self.assert_answers(rows, UNKNOWN)
        rows = observations() + [{"kind": {}, "decision": "ALLOW"}]
        self.assert_answers(rows, AFTER)

    def test_unsupported_question_is_reported_without_echoing_input(self):
        with self.assertRaisesRegex(ValueError, "^unknown_finish_effect_question$"):
            infer_finish_effect(observations(), 1, "UNRELATED_PRIVATE_MARKER")


if __name__ == "__main__":
    unittest.main()
