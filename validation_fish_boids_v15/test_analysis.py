"""Hand-derived checks for the independent v15 factorial and arrival algebra."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("analysis.py")
        cls.module = None
        if path.exists():
            spec = importlib.util.spec_from_file_location("v15_analysis_test_target", path)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)

    def api(self, name):
        self.assertIsNotNone(self.module, "v15 analysis is not implemented")
        self.assertTrue(hasattr(self.module, name), f"v15 {name} is not implemented")
        return getattr(self.module, name)

    def test_additive_fixture_respects_X4_V2_C1_mask_order(self):
        # Baseline 10, X=3, V=5, C=7; a bit-order swap breaks this fixture.
        result = self.api("decompose")([[10, 17, 15, 22, 13, 20, 18, 25]])
        for term, expected in {"X": 3, "V": 5, "C": 7,
                               "XV": 0, "XC": 0, "VC": 0, "XVC": 0}.items():
            np.testing.assert_array_equal(result["mobius"][term], [expected])
        np.testing.assert_array_equal(result["total"], [15])
        np.testing.assert_array_equal(result["insertion_X"], [3])
        np.testing.assert_array_equal(result["deletion_X"], [3])
        np.testing.assert_array_equal(result["shapley_X_minus_C"], [-4])
        for term, expected in {"X": 3, "V": 5, "C": 7}.items():
            np.testing.assert_array_equal(result["shapley"][term], [expected])

    def test_pairwise_interactions_are_split_between_their_own_components(self):
        # Only XV=12, XC=-6, VC=4. X deletion=10-4, not X insertion=0.
        result = self.api("decompose")([[0, 0, 0, 4, 0, -6, 12, 10]])
        for term, expected in {"X": 0, "V": 0, "C": 0,
                               "XV": 12, "XC": -6, "VC": 4, "XVC": 0}.items():
            np.testing.assert_array_equal(result["mobius"][term], [expected])
        for term, expected in {"X": 3, "V": 8, "C": -1}.items():
            np.testing.assert_array_equal(result["shapley"][term], [expected])
        np.testing.assert_array_equal(result["total"], [10])
        np.testing.assert_array_equal(result["insertion_X"], [0])
        np.testing.assert_array_equal(result["deletion_X"], [6])
        np.testing.assert_array_equal(result["shapley_X_minus_C"], [4])

    def test_three_way_interaction_has_no_lower_order_terms(self):
        result = self.api("decompose")([[2, 2, 2, 2, 2, 2, 2, 11]])
        for term in ("X", "V", "C", "XV", "XC", "VC"):
            np.testing.assert_array_equal(result["mobius"][term], [0])
        np.testing.assert_array_equal(result["mobius"]["XVC"], [9])
        for term in ("X", "V", "C"):
            np.testing.assert_array_equal(result["shapley"][term], [3])
        np.testing.assert_array_equal(result["total"], [9])
        np.testing.assert_array_equal(result["insertion_X"], [0])
        np.testing.assert_array_equal(result["deletion_X"], [9])

    def test_all_seven_terms_and_shapley_close_within_each_seed(self):
        # Rows have known terms (2,3,5,7,11,13,17) and pure XVC=9.
        values = np.array([[10, 15, 13, 31, 12, 28, 22, 68],
                           [2, 2, 2, 2, 2, 2, 2, 11]], dtype=float)
        original = values.copy()
        result = self.api("decompose")(values)
        expected_terms = {"X": [2, 0], "V": [3, 0], "C": [5, 0],
                          "XV": [7, 0], "XC": [11, 0], "VC": [13, 0],
                          "XVC": [17, 9]}
        self.assertEqual(set(result["mobius"]), set(expected_terms))
        self.assertEqual(set(result["shapley"]), {"X", "V", "C"})
        for term, expected in expected_terms.items():
            np.testing.assert_array_equal(result["mobius"][term], expected)
        np.testing.assert_allclose(result["shapley"]["X"], [50 / 3, 3])
        np.testing.assert_allclose(result["shapley"]["V"], [56 / 3, 3])
        np.testing.assert_allclose(result["shapley"]["C"], [68 / 3, 3])
        np.testing.assert_array_equal(result["total"], [58, 9])
        np.testing.assert_array_equal(result["deletion_X"], [37, 9])
        np.testing.assert_allclose(sum(result["mobius"].values()), [58, 9], atol=1e-14)
        np.testing.assert_allclose(sum(result["shapley"].values()), [58, 9], atol=1e-14)
        np.testing.assert_array_equal(values, original)

    def test_cancelling_signed_terms_are_retained_when_total_is_zero(self):
        result = self.api("decompose")([[0, -8, 0, -8, 8, 0, 8, 0]])
        np.testing.assert_array_equal(result["total"], [0])
        np.testing.assert_array_equal(result["shapley"]["X"], [8])
        np.testing.assert_array_equal(result["shapley"]["C"], [-8])
        np.testing.assert_array_equal(result["shapley_X_minus_C"], [16])

    def test_empty_factorial_preserves_every_per_seed_output_shape(self):
        result = self.api("decompose")(np.empty((0, 8)))
        for name in ("total", "insertion_X", "deletion_X", "shapley_X_minus_C"):
            self.assertEqual(result[name].shape, (0,))
        self.assertEqual(set(result["mobius"]), {"X", "V", "C", "XV", "XC", "VC", "XVC"})
        for group in ("mobius", "shapley"):
            for value in result[group].values():
                self.assertEqual(value.shape, (0,))

    def test_malformed_factorial_cannot_silently_drop_seed_rows_or_corners(self):
        decompose = self.api("decompose")
        invalid = [np.zeros(8), np.zeros((2, 7)), np.zeros((2, 9)),
                   np.zeros((1, 8, 1)), [[0] * 8, [0] * 7],
                   [[np.nan] + [0] * 7], [[np.inf] + [0] * 7]]
        for values in invalid:
            with self.subTest(values=values), self.assertRaises(ValueError):
                decompose(values)

    def test_count_decomposition_preserves_exact_zero_primary_interactions(self):
        # Additive integer increments X=106, V=143, C=-82; every interaction is 0.
        counts = np.array([[89037, 88955, 89180, 89098,
                            89143, 89061, 89286, 89204]], dtype=np.int64)
        result = self.api("decompose_counts")(counts, 96000)
        for term in ("XV", "XC", "VC", "XVC"):
            np.testing.assert_array_equal(result["mobius"][term], [0.0])
        for term, expected in {"X": 106 / 96000, "V": 143 / 96000,
                               "C": -82 / 96000}.items():
            np.testing.assert_array_equal(result["mobius"][term], [expected])
            np.testing.assert_array_equal(result["shapley"][term], [expected])
        np.testing.assert_array_equal(result["total"], [167 / 96000])
        np.testing.assert_array_equal(result["insertion_X"], [106 / 96000])
        np.testing.assert_array_equal(result["deletion_X"], [106 / 96000])
        np.testing.assert_array_equal(result["shapley_X_minus_C"], [188 / 96000])

    def test_count_shapley_cancellations_happen_before_any_division(self):
        counts = np.array([
            [100, 100, 100, 100, 101, 101, 97, 100],
            [100, 100, 100, 103, 101, 103, 102, 108],
            [10, 15, 13, 31, 12, 28, 22, 68],
        ])
        result = self.api("decompose_counts")(counts, 96000)
        # Row 1: X=1, XV=-4, XVC=3 gives phi_X=1-2+1=0.
        # Row 2: terms (1,0,0,1,2,3,1) give phi_X=phi_C=17/6.
        # Row 3: terms (2,3,5,7,11,13,17) exercise all seven coefficients.
        np.testing.assert_array_equal(result["shapley"]["X"],
                                      [0, 17 / 576000, 100 / 576000])
        np.testing.assert_array_equal(result["shapley"]["V"],
                                      [-1 / 96000, 14 / 576000, 112 / 576000])
        np.testing.assert_array_equal(result["shapley"]["C"],
                                      [1 / 96000, 17 / 576000, 136 / 576000])
        np.testing.assert_array_equal(result["shapley_X_minus_C"],
                                      [-1 / 96000, 0, -6 / 96000])
        np.testing.assert_array_equal(result["total"], [0, 8 / 96000, 58 / 96000])
        np.testing.assert_allclose(sum(result["shapley"].values()), result["total"],
                                   rtol=0, atol=1e-18)
        np.testing.assert_allclose(sum(result["mobius"].values()), result["total"],
                                   rtol=0, atol=1e-18)

    def test_count_decomposition_never_coerces_integers_to_float_before_subtraction(self):
        # Above 2**53, float coercion would erase some one-count differences.
        base = 2 ** 53
        counts = np.array([[base, base + 7, base + 5, base + 12,
                            base + 3, base + 10, base + 8, base + 15]], dtype=np.int64)
        original = counts.copy()
        result = self.api("decompose_counts")(counts, 96000)
        for term, expected in {"X": 3 / 96000, "V": 5 / 96000,
                               "C": 7 / 96000}.items():
            np.testing.assert_array_equal(result["shapley"][term], [expected])
        for term in ("XV", "XC", "VC", "XVC"):
            np.testing.assert_array_equal(result["mobius"][term], [0])
        np.testing.assert_array_equal(result["total"], [15 / 96000])
        np.testing.assert_array_equal(counts, original)

    def test_count_decomposition_empty_cohort_preserves_all_output_shapes(self):
        result = self.api("decompose_counts")(np.empty((0, 8), dtype=np.int64), 96000)
        self.assertEqual(set(result), {"total", "insertion_X", "deletion_X", "mobius",
                                       "shapley", "shapley_X_minus_C"})
        for name in ("total", "insertion_X", "deletion_X", "shapley_X_minus_C"):
            self.assertEqual(result[name].shape, (0,))
        for group in ("mobius", "shapley"):
            for value in result[group].values():
                self.assertEqual(value.shape, (0,))
                self.assertEqual(value.dtype, np.dtype(float))

    def test_count_decomposition_rejects_fractional_nonfinite_or_overflow_risk_inputs(self):
        decompose = self.api("decompose_counts")
        invalid = [np.zeros(8, dtype=int), np.zeros((1, 7), dtype=int),
                   [[0] * 8, [0] * 7], [[.5] + [0] * 7],
                   [[np.nan] + [0] * 7], [[np.inf] + [0] * 7],
                   np.ones((1, 8), dtype=complex), np.ones((1, 8), dtype=bool),
                   np.full((1, 8), np.iinfo(np.int64).max, dtype=np.int64),
                   np.full((1, 8), np.iinfo(np.int64).min, dtype=np.int64),
                   np.full((1, 8), np.iinfo(np.uint64).max, dtype=np.uint64)]
        for counts in invalid:
            with self.subTest(counts=counts), self.assertRaises(ValueError):
                decompose(counts, 96000)

    def test_count_decomposition_requires_a_positive_integer_denominator(self):
        decompose = self.api("decompose_counts")
        for denominator in (0, -1, 1.5, True, np.nan, np.inf):
            with self.subTest(denominator=denominator), self.assertRaises(ValueError):
                decompose(np.zeros((1, 8), dtype=int), denominator)

    def test_bootstrap_matrix_reuses_whole_seed_rows_deterministically(self):
        bootstrap = self.api("bootstrap_indices")
        indices = bootstrap(4, replicates=31)
        self.assertEqual(indices.shape, (31, 4))
        self.assertTrue(np.issubdtype(indices.dtype, np.integer))
        self.assertTrue(np.all((indices >= 0) & (indices < 4)))
        np.testing.assert_array_equal(indices, bootstrap(4, replicates=31, seed=2026112205))
        self.assertFalse(np.array_equal(indices, bootstrap(4, replicates=31, seed=42)))
        # Each selected row keeps both columns paired with one seed identity.
        paired = np.array([[1, 101], [2, 102], [3, 103], [4, 104]])[indices]
        np.testing.assert_array_equal(paired[:, :, 1] - paired[:, :, 0], np.full((31, 4), 100))

    def test_bootstrap_empty_and_singleton_cohorts_remain_well_shaped(self):
        bootstrap = self.api("bootstrap_indices")
        self.assertEqual(bootstrap(0).shape, (10000, 0))
        np.testing.assert_array_equal(bootstrap(1, replicates=4), np.zeros((4, 1), dtype=int))

    def test_bootstrap_rejects_invalid_population_or_replicate_counts(self):
        bootstrap = self.api("bootstrap_indices")
        for n, replicates, seed in [(-1, 10, 1), (2.5, 10, 1), (True, 10, 1),
                                    (2, 0, 1), (2, -1, 1), (2, 2.5, 1),
                                    (2, True, 1), (2, 10, -1), (2, 10, 1.5)]:
            with self.subTest(n=n, replicates=replicates, seed=seed), self.assertRaises(ValueError):
                bootstrap(n, replicates, seed)

    def test_summary_uses_supplied_paired_indices_and_known_percentiles(self):
        summarize = self.api("summarize")
        indices = np.array([[0, 0], [1, 1], [0, 1], [1, 0]])
        original = indices.copy()
        # Seed differences 2,4 give bootstrap means 2,4,3,3.
        result = summarize([2, 4], indices)
        self.assertEqual(result["n"], 2)
        self.assertEqual(result["mean"], 3)
        self.assertEqual(result["median"], 3)
        np.testing.assert_allclose(result["ci95"], [2.075, 3.925])
        self.assertEqual((result["positive"], result["negative"], result["zero"]), (2, 0, 0))
        # The same draws applied to the arms produce known, covarying intervals.
        np.testing.assert_allclose(summarize([10, 20], indices)["ci95"], [10.375, 19.625])
        np.testing.assert_allclose(summarize([12, 24], indices)["ci95"], [12.45, 23.55])
        np.testing.assert_array_equal(indices, original)

    def test_summary_concentration_uses_positive_mass_and_stable_tie_order(self):
        result = self.api("summarize")([-10, 2, 1, 1, 0], np.array([[0, 1, 2, 3, 4]]))
        self.assertEqual(result["mean"], -1.2)
        self.assertEqual(result["median"], 1)
        self.assertEqual((result["positive"], result["negative"], result["zero"]), (3, 1, 1))
        self.assertEqual(result["positive_concentration"], {
            "positive_total": 4.0, "top_two_indices": [1, 2],
            "top_two_share": .75, "largest_share": .5})

    def test_zero_and_negative_only_cohorts_have_no_positive_concentration_share(self):
        summarize = self.api("summarize")
        for values in ([0, 0, 0], [-2, -1, 0]):
            with self.subTest(values=values):
                result = summarize(values, np.array([[0, 1, 2]]))
                self.assertEqual(result["positive_concentration"], {
                    "positive_total": 0.0, "top_two_indices": [],
                    "top_two_share": None, "largest_share": None})

    def test_empty_summary_has_null_estimates_and_interval(self):
        result = self.api("summarize")([], np.empty((4, 0), dtype=int))
        self.assertEqual(result, {
            "n": 0, "mean": None, "median": None, "ci95": None,
            "positive": 0, "negative": 0, "zero": 0,
            "positive_concentration": {"positive_total": 0.0, "top_two_indices": [],
                                       "top_two_share": None, "largest_share": None}})

    def test_singleton_summary_is_descriptive_without_interval(self):
        result = self.api("summarize")([5], np.zeros((10, 1), dtype=int))
        self.assertEqual(result["n"], 1)
        self.assertEqual(result["mean"], 5)
        self.assertEqual(result["median"], 5)
        self.assertIsNone(result["ci95"])
        self.assertEqual(result["positive_concentration"], {
            "positive_total": 5.0, "top_two_indices": [0],
            "top_two_share": 1.0, "largest_share": 1.0})

    def test_summary_rejects_unpaired_or_invalid_indices_and_nonfinite_values(self):
        summarize = self.api("summarize")
        invalid = [([1, 2], np.array([[0]])), ([1, 2], np.array([0, 1])),
                   ([1, 2], np.array([[0, 2]])), ([1, 2], np.array([[-1, 1]])),
                   ([1, 2], np.array([[0.0, 1.0]])),
                   ([1, 2], np.empty((0, 2), dtype=int)),
                   ([1, np.nan], np.array([[0, 1]])),
                   ([1, np.inf], np.array([[0, 1]])),
                   ([[1, 2]], np.array([[0, 1]]))]
        for values, indices in invalid:
            with self.subTest(values=values, indices=indices), self.assertRaises(ValueError):
                summarize(values, indices)

    def test_arrival_uses_continuation_offset_and_first_completed_window(self):
        result = self.api("arrival_record")([0, 0, 1, 1, 1], start_step=1040, window=2, threshold=1)
        self.assertEqual(result, {"confirmation_step": 1044, "event_observed": True,
                                  "censored": False, "restricted_latency": 4})

    def test_already_high_arrival_has_a_full_window_measurement_floor(self):
        result = self.api("arrival_record")(np.ones(200))
        self.assertEqual(result, {"confirmation_step": 1240, "event_observed": True,
                                  "censored": False, "restricted_latency": 200})

    def test_exact_final_window_event_is_observed_at_6000(self):
        # Exactly 180*32=5760 calls in the final 200 samples: mean .90.
        values = np.zeros(4960)
        values[-180:] = 1
        result = self.api("arrival_record")(values)
        self.assertEqual(result, {"confirmation_step": 6000, "event_observed": True,
                                  "censored": False, "restricted_latency": 4960})

    def test_one_call_below_final_window_boundary_is_censored_at_same_latency(self):
        values = np.zeros(4960)
        values[-180:] = 1
        values[-1] = 31 / 32  # Final total 5759, below the required 5760.
        result = self.api("arrival_record")(values)
        self.assertEqual(result, {"confirmation_step": None, "event_observed": False,
                                  "censored": True, "restricted_latency": 4960})

    def test_prespecified_thresholds_use_exact_integer_call_totals(self):
        arrival = self.api("arrival_record")
        for threshold, high_samples in [(.8, 160), (.9, 180), (.95, 190)]:
            with self.subTest(threshold=threshold):
                values = np.zeros(200)
                values[:high_samples] = 1
                result = arrival(values, threshold=threshold)
                self.assertEqual(result["confirmation_step"], 1240)
                self.assertTrue(result["event_observed"])
                values[0] = 31 / 32
                self.assertTrue(arrival(values, threshold=threshold)["censored"])

    def test_noninteger_required_call_threshold_rounds_up_without_float_ties(self):
        arrival = self.api("arrival_record")
        # .9*3*2=5.4, so five calls fail and six calls qualify.
        self.assertTrue(arrival([1, 2 / 3], start_step=7, window=2, n=3)["censored"])
        self.assertEqual(arrival([1, 1], start_step=7, window=2, n=3)["confirmation_step"], 9)
        # .14 is an exact decimal threshold; 14 of 100 calls must qualify.
        self.assertTrue(arrival([14 / 100], start_step=0, window=1,
                                threshold=.14, n=100)["event_observed"])

    def test_arrival_rejects_impossible_call_fractions_even_near_grid(self):
        arrival = self.api("arrival_record")
        for values in ([.9], [np.nextafter(.5, 1)], [-1 / 32], [33 / 32],
                       [np.nan], [np.inf], [[0]], []):
            with self.subTest(values=values), self.assertRaises(ValueError):
                arrival(values, window=1)

    def test_arrival_rejects_invalid_window_offset_threshold_and_fish_count(self):
        arrival = self.api("arrival_record")
        invalid = [{"start_step": -1}, {"start_step": False}, {"start_step": 1.5},
                   {"window": 0}, {"window": 3}, {"window": False}, {"window": 1.5},
                   {"threshold": -.1}, {"threshold": 1.1}, {"threshold": np.nan},
                   {"threshold": True}, {"n": 0}, {"n": 2.5}, {"n": True}]
        for kwargs in invalid:
            args = {"window": 1, **kwargs}
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                arrival([0, 1], **args)


if __name__ == "__main__":
    unittest.main()
