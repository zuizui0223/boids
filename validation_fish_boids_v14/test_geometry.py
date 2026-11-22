"""Synthetic-fixture checks for the frozen-geometry probability-map closure."""

import json
import math
import unittest

import numpy as np

from geometry import geometry_diagnostic


class GeometryDiagnosticTests(unittest.TestCase):
    def test_distant_agents_have_one_baseline_solution(self):
        # Negligible hearing must not create a high branch or self-coupling.
        pos = np.array([[0.0, 0.0], [1000.0, 0.0], [0.0, 1000.0]])
        found = geometry_diagnostic(pos)
        self.assertEqual(found.get("classification"), "collapsed_bounds")
        self.assertTrue(found["converged"])
        baseline = 0.057324175898868755
        np.testing.assert_allclose(found["low_fixed_point"], baseline, atol=1e-14, rtol=0)
        np.testing.assert_allclose(found["high_fixed_point"], baseline, atol=1e-14, rtol=0)
        self.assertLess(found["global_contraction_bound"], 1e-80)
        self.assertLess(found["weighted_degree_max"], 1e-80)
        self.assertLess(found["max_gap"], 1e-12)
        self.assertLessEqual(found["low_residual"], 1e-12)
        self.assertLessEqual(found["high_residual"], 1e-12)
        json.dumps(found, allow_nan=False)

    def test_zero_hearing_is_exactly_constant_in_one_iteration(self):
        # Removing hearing must remove geometry dependence and all Jacobian gain.
        pos = np.zeros((4, 2))
        found = geometry_diagnostic(pos, heard_weight=0, theta=math.log(0.2 / 0.8))
        self.assertEqual(found.get("classification"), "collapsed_bounds")
        self.assertTrue(found["converged"])
        self.assertEqual(found["iterations"], 1)
        self.assertEqual(found["low_fixed_point"], found["high_fixed_point"])
        np.testing.assert_allclose(found["low_fixed_point"], 0.2, atol=1e-15, rtol=0)
        self.assertEqual(found["low_residual"], 0.0)
        self.assertEqual(found["high_residual"], 0.0)
        self.assertEqual(found["low_spectral_radius"], 0.0)
        self.assertEqual(found["high_spectral_radius"], 0.0)
        self.assertEqual(found["global_contraction_bound"], 0.0)
        self.assertEqual(found["weighted_degree_min"], 0.0)

    def test_coincident_four_agents_recover_known_scalar_outer_roots(self):
        # With H off-diagonal one and a=2, uniform iterates obey sigmoid(-3+6q).
        found = geometry_diagnostic(np.zeros((4, 2)), heard_weight=2.0, theta=-3.0)
        self.assertEqual(found.get("classification"), "separated_fixed_points")
        self.assertTrue(found["converged"])
        lower = 0.07072018167994483
        upper = 0.9292798183200551
        np.testing.assert_allclose(found["low_fixed_point"], lower, atol=3e-12, rtol=0)
        np.testing.assert_allclose(found["high_fixed_point"], upper, atol=3e-12, rtol=0)
        self.assertAlmostEqual(found["low_mean"], lower, delta=3e-12)
        self.assertAlmostEqual(found["high_mean"], upper, delta=3e-12)
        self.assertAlmostEqual(found["max_gap"], upper - lower, delta=6e-12)
        self.assertLessEqual(found["low_residual"], 1e-12)
        self.assertLessEqual(found["high_residual"], 1e-12)
        expected_radius = 6 * lower * (1 - lower)
        self.assertAlmostEqual(found["low_spectral_radius"], expected_radius, delta=2e-11)
        self.assertAlmostEqual(found["high_spectral_radius"], expected_radius, delta=2e-11)
        self.assertEqual(found["global_contraction_bound"], 1.5)
        for key in ["weighted_degree_min", "weighted_degree_mean", "weighted_degree_max"]:
            self.assertEqual(found[key], 6.0)
        json.dumps(found, allow_nan=False)

    def test_feedback_degrees_and_global_bound_use_the_normalized_coupling(self):
        # H has rows (0,1,.5), (1,0,.5), (.5,.5,0), with rho=(1+sqrt(3))/2.
        # For N=3, a=4: A's degrees are 6,6,4 and its spectral bound is rho(H).
        pos = np.array([[0.0, 0.0], [0.0, 0.0], [5 * math.log(2), 0.0]])
        found = geometry_diagnostic(pos)
        self.assertIn(found.get("classification"), {
            "collapsed_bounds", "separated_fixed_points", "unresolved"
        })
        self.assertAlmostEqual(found["weighted_degree_min"], 4.0, delta=1e-14)
        self.assertAlmostEqual(found["weighted_degree_mean"], 16 / 3, delta=1e-14)
        self.assertAlmostEqual(found["weighted_degree_max"], 6.0, delta=1e-14)
        self.assertAlmostEqual(
            found["global_contraction_bound"], 1.3660254037844386, delta=2e-14
        )

    def test_iteration_limit_is_unresolved_even_with_a_large_gap(self):
        # A large finite-iteration gap alone cannot identify multiple fixed points.
        found = geometry_diagnostic(
            np.zeros((4, 2)), heard_weight=2.0, theta=-3.0, max_iter=1
        )
        self.assertEqual(found.get("classification"), "unresolved")
        self.assertFalse(found["converged"])
        self.assertEqual(found["iterations"], 1)
        self.assertGreater(found["max_gap"], 0.9)
        self.assertGreater(found["low_residual"], 1e-3)
        self.assertGreater(found["high_residual"], 1e-3)

    def test_returned_finite_iterates_form_nested_componentwise_brackets(self):
        # Increasing an iteration budget must tighten both enclosing sequences.
        pos = np.array([[0.0, 0.0], [0.5, 0.0], [0.0, 1.0], [1.5, 0.5]])
        previous_low = np.zeros(4)
        previous_high = np.ones(4)
        for budget in [1, 2, 3, 6, 12]:
            found = geometry_diagnostic(pos, heard_weight=2, theta=-3, max_iter=budget)
            self.assertIn(found.get("classification"), {
                "collapsed_bounds", "separated_fixed_points", "unresolved"
            })
            low = np.array(found["low_fixed_point"])
            high = np.array(found["high_fixed_point"])
            self.assertTrue(np.all(low >= previous_low))
            self.assertTrue(np.all(high <= previous_high))
            self.assertTrue(np.all(low <= high))
            self.assertTrue(np.all(low >= 0))
            self.assertTrue(np.all(high <= 1))
            previous_low, previous_high = low, high

    def test_malformed_or_nonfinite_positions_are_rejected(self):
        for pos in [
            [], [0.0, 1.0], np.empty((0, 2)), np.zeros((3, 3)),
            np.zeros((3, 1)), np.zeros((2, 2, 2)),
            [[0.0, 0.0], [math.nan, 1.0]],
            [[0.0, 0.0], [math.inf, 1.0]],
        ]:
            with self.subTest(pos=pos), self.assertRaises(ValueError):
                geometry_diagnostic(pos)

    def test_negative_or_nonfinite_hearing_is_rejected(self):
        for weight in [-0.1, math.nan, math.inf]:
            with self.subTest(weight=weight), self.assertRaises(ValueError):
                geometry_diagnostic(np.zeros((4, 2)), heard_weight=weight)

    def test_invalid_solver_controls_are_rejected(self):
        for kwargs in [
            {"theta": math.nan}, {"theta": math.inf},
            {"tol": 0}, {"tol": -1}, {"tol": math.nan}, {"tol": math.inf},
            {"max_iter": 0}, {"max_iter": -1}, {"max_iter": 1.5},
            {"max_iter": True},
        ]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                geometry_diagnostic(np.zeros((4, 2)), **kwargs)


if __name__ == "__main__":
    unittest.main()
