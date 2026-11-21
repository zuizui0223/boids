"""Independent numerical checks for the deterministic mean-field audit."""

import json
import math
import unittest

from meanfield_audit import equilibria, folds, run_audit, stability


class EquilibriumTests(unittest.TestCase):
    def test_baseline_has_three_distinct_equilibria(self):
        actual = equilibria(6.0, -3.0)
        expected = [0.07072018167994483, 0.5, 0.9292798183200551]
        self.assertEqual(len(actual), len(expected))
        for found, wanted in zip(actual, expected):
            self.assertAlmostEqual(found, wanted, delta=2e-13)

    def test_small_gain_has_one_equilibrium(self):
        for gain, intercept, expected in [
            (0.0, -1.3862943611198906, 0.2),
            (2.0, -2.3972245773362196, 0.1),
            (4.0, -2.0, 0.5),
        ]:
            with self.subTest(gain=gain):
                roots = equilibria(gain, intercept)
                self.assertEqual(len(roots), 1)
                self.assertAlmostEqual(roots[0], expected, delta=2e-13)

    def test_folds_match_independently_derived_thresholds(self):
        expected = {
            "p_lower": 0.21132486540518712,
            "p_upper": 0.7886751345948129,
            "h_lower": -3.4150929106440606,
            "h_upper": -2.5849070893559394,
        }
        found = folds(6.0)
        for key, value in expected.items():
            self.assertAlmostEqual(found[key], value, delta=2e-14)
        self.assertEqual(folds(0.0), {})
        self.assertEqual(folds(4.0), {})

    def test_tangent_roots_are_returned_once(self):
        boundary = folds(6.0)
        fixtures = [
            ("h_lower", [0.04014807866379499, 0.7886751345948129]),
            ("h_upper", [0.21132486540518712, 0.9598519213362050]),
        ]
        for key, expected in fixtures:
            with self.subTest(boundary=key):
                roots = equilibria(6.0, boundary[key])
                self.assertEqual(len(roots), 2)
                for found, wanted in zip(roots, expected):
                    self.assertAlmostEqual(found, wanted, delta=3e-13)

    def test_root_count_changes_on_the_correct_side_of_each_fold(self):
        boundary = folds(6.0)
        for intercept, expected_count in [
            (boundary["h_lower"] - 1e-7, 1),
            (boundary["h_lower"] + 1e-7, 3),
            (boundary["h_upper"] - 1e-7, 3),
            (boundary["h_upper"] + 1e-7, 1),
            (-4.5, 1),
            (-1.5, 1),
        ]:
            with self.subTest(intercept=intercept):
                roots = equilibria(6.0, intercept)
                self.assertEqual(len(roots), expected_count)
                self.assertTrue(all(a < b for a, b in zip(roots, roots[1:])))
                for p in roots:
                    mapped = 1.0 / (1.0 + math.exp(-(intercept + 6.0 * p)))
                    self.assertLess(abs(p - mapped), 2e-13)

    def test_triple_critical_root_does_not_generate_duplicates(self):
        self.assertEqual(equilibria(4.0, -2.0), [0.5])
        self.assertEqual(len(equilibria(4.0, -2.0 - 1e-9)), 1)
        self.assertEqual(len(equilibria(4.0, -2.0 + 1e-9)), 1)

    def test_close_distinct_roots_are_not_merged_near_the_cusp(self):
        gain = 4.0 + 1e-12
        roots = equilibria(gain, -gain / 2.0)
        expected = [0.4999995669680510, 0.5, 0.5000004330319490]
        self.assertEqual(len(roots), 3)
        for found, wanted in zip(roots, expected):
            self.assertAlmostEqual(found, wanted, delta=3e-13)

    def test_saturated_end_of_supported_gain_range(self):
        roots = equilibria(100.0, -50.0)
        self.assertEqual(len(roots), 3)
        self.assertAlmostEqual(roots[0] / 1.9287498479639178e-22, 1.0, places=12)
        self.assertEqual(roots[1], 0.5)
        self.assertGreater(roots[2], 1.0 - 1e-14)

    def test_invalid_equilibrium_inputs_are_rejected(self):
        for gain, intercept in [
            (-1.0, 0.0), (100.01, 0.0), (math.nan, 0.0),
            (math.inf, 0.0), (6.0, math.inf), (6.0, math.nan),
        ]:
            with self.subTest(gain=gain, intercept=intercept):
                with self.assertRaises(ValueError):
                    equilibria(gain, intercept)


class StabilityTests(unittest.TestCase):
    def test_outer_equilibrium_uses_full_two_state_eigenvalues(self):
        result = stability(0.07072018167994483)
        self.assertEqual(result["classification"], "stable")
        for actual, expected in zip(
            result["eigenvalues"], [0.7897590533516358, -0.008321378185434908]
        ):
            self.assertAlmostEqual(actual, expected, delta=2e-13)
        self.assertAlmostEqual(result["spectral_radius"], 0.7897590533516358)
        self.assertTrue(all(value > 0 for value in result["jury"].values()))

    def test_middle_equilibrium_is_unstable_in_full_map(self):
        result = stability(0.5)
        self.assertEqual(result["classification"], "unstable")
        self.assertAlmostEqual(result["eigenvalues"][0], 1.1713430220938281)
        self.assertAlmostEqual(result["eigenvalues"][1], -0.0213430220938281)
        self.assertLess(result["jury"]["one_minus_trace_plus_det"], 0)

    def test_saddle_node_is_nonhyperbolic(self):
        result = stability(0.21132486540518712)
        self.assertEqual(result["classification"], "nonhyperbolic")
        self.assertAlmostEqual(result["eigenvalues"][0], 1.0)
        self.assertAlmostEqual(result["eigenvalues"][1], -1.0 / 60.0)

    def test_pure_delay_can_make_middle_root_a_repeller(self):
        result = stability(0.5, alpha=0, k=1, beta=6, eta=0)
        self.assertEqual(result["classification"], "unstable")
        self.assertGreater(result["eigenvalues"][0], 1)
        self.assertLess(result["eigenvalues"][1], -1)
        critical = stability(0.5, alpha=0, k=1, beta=4, eta=0)
        self.assertEqual(critical["classification"], "nonhyperbolic")
        self.assertEqual(critical["eigenvalues"], [1.0, -1.0])

    def test_stability_checks_the_supported_model_domain(self):
        for kwargs in [
            {"alpha": 1}, {"alpha": -0.1}, {"k": -1},
            {"beta": -1}, {"eta": -1}, {"eta": math.inf},
        ]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                stability(0.5, **kwargs)
        for p in [-0.01, 1.01, math.nan]:
            with self.subTest(p=p), self.assertRaises(ValueError):
                stability(p)


class SweepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = run_audit()

    def test_sweeps_converge_in_the_full_two_state_map(self):
        audit = self.audit
        self.assertTrue(audit["checks"]["all_sweep_points_converged"])
        tol = audit["sweeps"]["settle_tolerance"]
        for direction in ["increasing", "decreasing"]:
            rows = audit["sweeps"][direction]
            self.assertGreaterEqual(len(rows), 150)
            for row in rows:
                g, p, theta = row["g"], row["p"], row["theta"]
                mapped_g = 0.65 * g + 0.35 * p
                mapped_p = 1.0 / (1.0 + math.exp(-(theta + 4.0 * g + 2.0 * p)))
                residual = max(abs(mapped_g - g), abs(mapped_p - p))
                self.assertTrue(row["converged"])
                self.assertLessEqual(residual, 1.01 * tol)

    def test_continuation_exhibits_different_branches_at_same_theta(self):
        up = min(self.audit["sweeps"]["increasing"], key=lambda r: abs(r["theta"] + 3))
        down = min(self.audit["sweeps"]["decreasing"], key=lambda r: abs(r["theta"] + 3))
        self.assertAlmostEqual(up["theta"], -3)
        self.assertAlmostEqual(down["theta"], -3)
        self.assertAlmostEqual(up["p"], 0.07072018167994483, delta=2e-8)
        self.assertAlmostEqual(down["p"], 0.9292798183200551, delta=2e-8)

    def test_sweep_jumps_bracket_the_analytic_folds(self):
        inc = self.audit["checks"]["increasing_jump"]
        dec = self.audit["checks"]["decreasing_jump"]
        self.assertLessEqual(inc["from_theta"], -2.5849070893559394)
        self.assertGreaterEqual(inc["to_theta"], -2.5849070893559394)
        self.assertGreater(inc["delta_p"], 0.5)
        self.assertGreaterEqual(dec["from_theta"], -3.4150929106440606)
        self.assertLessEqual(dec["to_theta"], -3.4150929106440606)
        self.assertLess(dec["delta_p"], -0.5)

    def test_audit_can_be_serialized_as_strict_json(self):
        self.assertTrue(self.audit["checks"]["bistability_at_baseline"])
        self.assertEqual(len(self.audit["roots"]), 3)
        self.assertLess(self.audit["checks"]["roots_residual_max"], 2e-13)
        json.dumps(self.audit, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
