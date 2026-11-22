import unittest
import numpy as np
from validation_fish_boids_v16.run_holdout import (
    SEEDS, bootstrap_group_difference, main_contrast, _valid_trace
)
class FrozenHoldoutTests(unittest.TestCase):
    def test_seed_range_is_locked_and_independent(self):
        self.assertEqual((len(SEEDS),SEEDS[0],SEEDS[-1]),(192,3000,3191))
        self.assertTrue(set(SEEDS).isdisjoint(set(range(2000,2096))))
    def test_window_index_and_integer_algebra(self):
        n=5000
        c=np.zeros(n,dtype=float)
        p=c.copy()
        p[40:3040]=1/32
        self.assertEqual(main_contrast(p,c),1/32)
        self.assertEqual(main_contrast(p,c,5000,6000),0.)
    def test_bad_fraction_grid_is_rejected(self):
        c=np.zeros(5000,dtype=float)
        c[100]=.012
        with self.assertRaises(RuntimeError):
            _valid_trace(c,5000)
    def test_stratified_bootstrap_math(self):
        a=np.ones(8)*.08
        b=np.ones(12)*.01
        mean,ci=bootstrap_group_difference(a,b)
        self.assertAlmostEqual(mean,.07)
        self.assertTrue(np.allclose(ci,[.07,.07],atol=1e-15))
    def test_singleton_does_not_gain_fake_interval(self):
        mean,ci=bootstrap_group_difference(np.array([.1]),np.array([0,.01]))
        self.assertIsNone(ci)
        self.assertAlmostEqual(mean,.095)
    def test_empty_risk_returns_inconclusive(self):
        mean,ci=bootstrap_group_difference(np.array([]),np.array([0,.01]))
        self.assertIsNone(mean)
        self.assertIsNone(ci)
if __name__=="__main__":
    unittest.main()
