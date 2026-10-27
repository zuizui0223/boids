"""Known-truth algebraic identified-set and transfer limits."""
import unittest
from identified_set_forecast import (ALPHAS,D0_M,CALIBRATED_EFFECTIVE_COEFFICIENT,
    gamma_on_identified_set,effective_steering,experiment,simulate_pair_distance)

class TestStructuralTransfer(unittest.TestCase):
    def test_all_coefficients_indistinguishable_at_calibration_distance(self):
        for a in ALPHAS:
            self.assertAlmostEqual(effective_steering(a,gamma_on_identified_set(a),D0_M),
                                   CALIBRATED_EFFECTIVE_COEFFICIENT,places=13)
    def test_parameter_identified_set_is_not_a_single_point(self):
        self.assertGreater(len(set(gamma_on_identified_set(a) for a in ALPHAS)),1)
    def test_new_contexts_break_one_step_equivalence(self):
        v=[effective_steering(a,gamma_on_identified_set(a),25.) for a in ALPHAS]
        self.assertGreater(max(v)-min(v),0.001)
    def test_same_context_simulation_is_deterministic(self):
        a=simulate_pair_distance(15.,ALPHAS[1]);b=simulate_pair_distance(15.,ALPHAS[1])
        self.assertEqual(a,b)
    def test_longer_horizon_spatial_pattern_not_unique(self):
        d=experiment()['worlds']
        self.assertGreater(d['25.0']['endpoint_forecast_width_m'],4.0)
        self.assertGreater(d['25.0']['endpoint_forecast_width_m'],d['10.0']['endpoint_forecast_width_m'])
    def test_trajectory_does_not_infer_ecological_niche(self):
        x=experiment()
        self.assertEqual(x['evidence_status'],'MATHEMATICAL_KNOWN_TRUTH_ONLY_NOT_WILD_ANIMAL_DATA')
        self.assertNotIn('niche_distribution',x)

if __name__=='__main__':unittest.main()
