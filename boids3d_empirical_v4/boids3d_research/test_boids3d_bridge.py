import unittest
import numpy as np

from boids3d_bridge import (Rules, neighbors, step, simulate,
                            centered_height_histories, heldout_shape_gain,
                            permutation_calibration, mean_horizontal_overlap)


class TestBoids3dBridge(unittest.TestCase):
    def test_neighborhoods(self):
        pos = np.array([[0., 0., 50.], [4., 0., 50.],
                        [100., 0., 50.], [103., 0., 50.]])
        rules = Rules(neighbor_radius=5.0, topological_k=2)
        metr = neighbors(pos, "metric", rules)
        topo = neighbors(pos, "topological", rules)
        self.assertTrue(metr[0, 1]); self.assertFalse(metr[0, 2])
        self.assertFalse(np.diag(metr).any())
        self.assertFalse(np.diag(topo).any())
        np.testing.assert_equal(topo.sum(axis=1), [2, 2, 2, 2])
        with self.assertRaises(ValueError):
            neighbors(pos, "not_a_rule", rules)

    def test_fixed_seed(self):
        a, g = simulate(model="boids_personal", method="metric", seed=7,
                        n=5, nights=2, steps=210, burn=40, thin=5)
        b, h = simulate(model="boids_personal", method="metric", seed=7,
                        n=5, nights=2, steps=210, burn=40, thin=5)
        np.testing.assert_array_equal(a, b)
        np.testing.assert_array_equal(g, h)
        self.assertTrue(np.isfinite(a).all())
        self.assertTrue((a[..., 2] >= 5).all())
        self.assertTrue((a[..., 2] <= 200).all())
        self.assertEqual(a.shape, (2, 5, 34, 3))

    def test_wind_only_shifts_ground(self):
        rules = Rules(noise_sd=0, dt=.5)
        p = np.array([[0., 0., 95.], [30., 0., 95.]])
        v = np.array([[7., 0., 0.], [7., 0., 0.]])
        rng = np.random.default_rng(10)
        q, w = step(p, v, 0., np.array([.17, .17]), rng,
                    model="independent_shared", method="metric", rules=rules)
        self.assertTrue((q[:, 0] - p[:, 0] > .5 * w[:, 0]).all())

    def test_gain_swap_changes_trajectories(self):
        a, _ = simulate(model="boids_personal", method="topological", seed=17,
                        n=5, nights=3, steps=190, burn=40)
        b, _ = simulate(model="boids_personal", method="topological", seed=17,
                        n=5, nights=3, steps=190, burn=40,
                        swap_personal_between_nights=True)
        self.assertFalse(np.array_equal(a, b))

    def test_calibration_repeatable(self):
        traces, _ = simulate(model="boids_personal", method="topological",
                             seed=17, n=5, nights=3, steps=400, burn=80)
        hist = centered_height_histories(traces)
        score = heldout_shape_gain(hist)
        report = permutation_calibration(hist, reps=9)
        self.assertAlmostEqual(report["raw_gain_nats_per_fix"], score)
        self.assertGreaterEqual(report["permutation_p_one_sided"], .1)
        self.assertLessEqual(report["permutation_p_one_sided"], 1)
        self.assertTrue(0 <= mean_horizontal_overlap(traces) <= 1)


if __name__ == "__main__":
    unittest.main()
