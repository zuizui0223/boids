"""Annual colony-patch component gating tests, distinct from Boids."""
import unittest
import numpy as np
from breeding_patch_bridge import PatchDesign,weights,effective_components,one_world

class BreedingGateTests(unittest.TestCase):
    def setUp(self):self.d=PatchDesign(null_replicates=199)

    def test_no_habitat_diff_preserves_probabilities(self):
        q=weights(self.d,.85,False)
        for row in q:np.testing.assert_allclose(row,q[0],atol=1e-12)

    def test_no_mobility_preserves_probabilities(self):
        q=weights(self.d,0,True)
        for row in q:np.testing.assert_allclose(row,q[0],atol=1e-12)

    def test_heterogeneous_filter_changes_expected_composition(self):
        q=weights(self.d,.85,True)
        self.assertGreater(q[-1,0],q[0,0])
        self.assertLess(q[-1,-1],q[0,-1])
        self.assertLess(float(effective_components(q[-1])),float(effective_components(q[0])))

    def test_count_null_calibration_bounds(self):
        o=one_world(self.d,.85,True,seed=17)
        self.assertTrue(0<o['null_lower_tail_p']<=1)
        self.assertEqual(sum(o['observed_patch_counts'][-1]),self.d.population_totals[-1])

if __name__=='__main__':unittest.main()
