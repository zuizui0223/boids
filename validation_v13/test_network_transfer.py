"""v13 fail-closed tests: structural, scoring and unchanged-v12 regression."""
import unittest
from dataclasses import replace

import numpy as np
import network_transfer as v13
import emergent_preferences as v12


class TestInterventionContract(unittest.TestCase):
    def test_rewire_balanced_and_orthogonal(self):
        v13.check_partition(v13.OLD)
        v13.check_partition(v13.NEW)
        self.assertEqual(np.sum((v13.OLD == 0) & (v13.NEW == 0)), 3)
        self.assertEqual(np.sum((v13.OLD == 1) & (v13.NEW == 0)), 3)

    def test_fractions_use_prior_choice_and_exclude_self(self):
        prior = np.array([0]*6 + [1]*6)
        old = v13.social_fractions(prior, v13.OLD)
        new = v13.social_fractions(prior, v13.NEW)
        mixed = v13.social_fractions(prior, None)
        np.testing.assert_allclose(old[0], [1., 0., 0., 0.])
        np.testing.assert_allclose(new[0], [.4, .6, 0., 0.])
        np.testing.assert_allclose(mixed[0], [5/11, 6/11, 0., 0.])
        np.testing.assert_allclose(old.sum(axis=1), np.ones(v13.N))

    def test_guilds_fixed_before_day_five(self):
        for condition in v13.CONDITIONS:
            np.testing.assert_array_equal(v13.active_network(condition, 3), v13.OLD)
        self.assertIsNone(v13.active_network(v13.CONDITIONS[2], 4))
        np.testing.assert_array_equal(
            v13.active_network(v13.CONDITIONS[1], 4), v13.NEW)

    def test_reject_invalid_partition_and_network(self):
        with self.assertRaises(ValueError):
            v13.check_partition(np.zeros(v13.N, dtype=int))
        with self.assertRaises(ValueError):
            v13.simulate(replace(v13.CONDITIONS[0], network="unknown"), 7)
        with self.assertRaises(ValueError):
            v13.social_fractions(np.full(v13.N, 4), v13.OLD)

    def test_v12_unmodified_stable_without_motor(self):
        # Strong regression: new v13 code preserves its parent model exactly.
        seed = 37
        old_condition = v12.Condition(
            "exact_parent", private_learning=True, social_choice=True, boids=False)
        prior = v12.simulate(old_condition, seed)
        now = v13.simulate(v13.CONDITIONS[0], seed)
        np.testing.assert_array_equal(now["choices"], prior["choices"])
        np.testing.assert_array_equal(now["xyz"], prior["xyz"])
        np.testing.assert_array_equal(now["daily_q"], prior["daily_q"])

    def test_post_interventions_do_not_change_preperiod(self):
        seed = 91
        base = v13.simulate(v13.CONDITIONS[0], seed)
        for name in ("rewired_uniform", "mixed_uniform", "stable_gradient", "rewired_gradient"):
            cond = next(c for c in v13.CONDITIONS if c.name == name)
            alt = v13.simulate(cond, seed)
            np.testing.assert_array_equal(base["choices"][:4], alt["choices"][:4])
            np.testing.assert_array_equal(base["xyz"][:4], alt["xyz"][:4])

    def test_learning_off_means_zero_memory(self):
        c = next(c for c in v13.CONDITIONS if c.name == "rewired_no_learning")
        state = v13.simulate(c, 13)
        self.assertTrue(np.array_equal(state["daily_q"], np.zeros_like(state["daily_q"])))

    def test_deterministic_replay(self):
        a = v13.simulate(v13.CONDITIONS[1], 7)
        b = v13.simulate(v13.CONDITIONS[1], 7)
        np.testing.assert_array_equal(a["choices"], b["choices"])
        np.testing.assert_array_equal(a["xyz"], b["xyz"])


class TestForecastScoring(unittest.TestCase):
    def test_identical_agents_give_zero_group_advantage(self):
        c = np.zeros((8, 21, v13.N), int)
        own = v13.patch_scores(c, v13.OLD)
        other = v13.patch_scores(c, v13.NEW)
        self.assertAlmostEqual(own["group_vs_population"], 0., places=12)
        self.assertAlmostEqual(other["group_vs_population"], 0., places=12)
        self.assertAlmostEqual(own["group_logscore"], other["group_logscore"], places=12)

    def test_group_forecast_favors_true_future_group(self):
        # Exogenous membership, not groupings optimized on observed data.
        c = np.zeros((8, 21, v13.N), int)
        c[:, :, v13.NEW == 1] = 1
        matched = v13.patch_scores(c, v13.NEW)
        orthogonal = v13.patch_scores(c, v13.OLD)
        self.assertGreater(matched["group_logscore"] - orthogonal["group_logscore"], .40)
        self.assertGreater(matched["group_vs_population"], .40)

    def test_vertical_score_conditional_on_same_xy(self):
        p = np.zeros((8, 21, v13.N, 3))
        p[:, :, v13.NEW == 0, 2] = -12
        p[:, :, v13.NEW == 1, 2] = 12
        own = v13.height_scores(p, v13.NEW)
        other = v13.height_scores(p, v13.OLD)
        self.assertGreater(own["group_logscore"]-other["group_logscore"], .30)

    def test_no_future_leakage_into_training_counts(self):
        c = np.zeros((8, 21, v13.N), int)
        c[4:6] = 1
        altered = c.copy()
        altered[6:] = 2
        np.testing.assert_array_equal(
            v13._choice_counts(c, v13.POST_TRAIN),
            v13._choice_counts(altered, v13.POST_TRAIN))
        self.assertFalse(np.array_equal(
            v13._choice_counts(c, v13.POST_TEST),
            v13._choice_counts(altered, v13.POST_TEST)))

    def test_seed_bootstrap_uses_world_count_not_decision_count(self):
        v = np.array([2., 2., 2., 2.])
        idx = np.array([[0, 1, 2, 3], [3, 2, 1, 0]])
        result = v13.bootstrap_summary(v, idx)
        self.assertEqual(result["mean"], 2.)
        self.assertEqual(result["bootstrap_95"], [2., 2.])
        self.assertEqual(result["n_worlds"], 4)

    def test_fixed_registered_conditions(self):
        self.assertEqual(len(v13.CONDITIONS), 8)
        self.assertEqual(v13.SEED_START, 20270101)
        self.assertEqual(v13.BOOT, 5000)
        self.assertEqual((v13.POST_TRAIN.start, v13.POST_TRAIN.stop), (4, 6))
        self.assertEqual((v13.POST_TEST.start, v13.POST_TEST.stop), (6, 8))


if __name__ == "__main__":
    unittest.main()
