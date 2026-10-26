"""Known-truth tests for the non-identifiability of v4 vertical M1 gain."""
import unittest
import json
from pathlib import Path
import numpy as np
from altitude_error_audit import simulate_one, evaluate, transition_probabilities
from empirical_transition_benchmark import probs_from_counts


class KnownTruthAltitudeErrorTests(unittest.TestCase):
    def test_matches_frozen_observed_m0_m1_probability_definitions(self):
        c=np.arange(27,dtype=int).reshape(3,3,3)
        x0,x1=transition_probabilities(c)
        v0,v1,_=probs_from_counts(c)
        np.testing.assert_array_equal(x0,v0)
        np.testing.assert_array_equal(x1,v1)

    def test_no_memory_no_error_near_zero_gain(self):
        v=simulate_one(17,velocity_rho=0,gps_z_sigma_m=0,n_steps=500)
        self.assertLess(abs(v['heldout_M1_minus_M0_nats_per_transition']),0.015)
        self.assertLess(abs(v['observed_climb_lag1_pearson']),0.07)

    def test_gps_error_alone_creates_predictive_dependency(self):
        v=simulate_one(17,velocity_rho=0,gps_z_sigma_m=20,n_steps=500)
        self.assertGreater(v['heldout_M1_minus_M0_nats_per_transition'],0.01)
        self.assertLess(v['observed_climb_lag1_pearson'],-0.18)
        self.assertLess(abs(v['observed_climb_lag2_pearson']),0.07)
        self.assertLess(abs(v['true_climb_lag1_pearson']),0.07)
        self.assertAlmostEqual(v['theoretical_climb_lag1'],(-400/900)/(0.8**2+800/900))

    def test_true_persistence_but_noise_changes_apparent_lag(self):
        p=simulate_one(17,velocity_rho=.7,gps_z_sigma_m=0,n_steps=500)
        q=simulate_one(17,velocity_rho=.7,gps_z_sigma_m=20,n_steps=500)
        self.assertGreater(p['heldout_M1_minus_M0_nats_per_transition'],0.1)
        self.assertGreater(p['observed_climb_lag1_pearson'],0.55)
        self.assertLess(q['observed_climb_lag1_pearson'],0.08)
        self.assertGreater(q['observed_climb_lag2_pearson'],0.12)

    def test_committed_receipt_reproduces_known_truth_scores(self):
        receipt=Path(__file__).resolve().parent/'results/gps_altitude_error_known_truth_v5.json'
        expected=json.loads(receipt.read_text(encoding='utf-8'))
        replay=evaluate(n_seeds=expected['n_random_seeds'],first_seed=expected['first_seed'])
        for label in expected['scenarios']:
            x=expected['scenarios'][label]
            y=replay['scenarios'][label]
            for metric in ('heldout_M1_minus_M0_nats_per_transition',
                           'observed_climb_lag1_pearson', 'observed_climb_lag2_pearson'):
                self.assertAlmostEqual(x[metric]['mean'],y[metric]['mean'],places=8)

    def test_reproducibility_and_configuration_gate(self):
        self.assertEqual(simulate_one(222),simulate_one(222))
        with self.assertRaises(ValueError):simulate_one(1,dt_s=0)
        with self.assertRaises(ValueError):simulate_one(1,gps_z_sigma_m=-1)
        short=evaluate(n_seeds=2)
        self.assertEqual(len(short['scenarios']),6)
        self.assertEqual(short['n_random_seeds'],2)


if __name__=='__main__':unittest.main()
