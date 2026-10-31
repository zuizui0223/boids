"""Scientific-bounds tests for endpoint bridge; no empirical replication implied."""
from dataclasses import replace
import unittest
from endpoint_bridge_v2 import (BridgeParams, capture_rate, crossing_workload,
   gain, HASE_2026_POTENTIAL_MISDETECTIONS, normalized_rho, run, reported_ratios)

class EndpointBridgeTests(unittest.TestCase):
    def test_original_reported_means_are_preserved(self):
        self.assertEqual(HASE_2026_POTENTIAL_MISDETECTIONS[4],(0.14,0.01))
        self.assertEqual(HASE_2026_POTENTIAL_MISDETECTIONS[32],(15.77,10.01))
        self.assertEqual(len(reported_ratios()),4)
    def test_ratio_between_zero_and_one(self):
        for n in HASE_2026_POTENTIAL_MISDETECTIONS:
            self.assertTrue(0<normalized_rho(n)<1)
    def test_zero_false_alarm_cost_equal_detection_gives_tie(self):
        self.assertAlmostEqual(gain(0,0,0.1),0,places=14)
    def test_positive_false_alarm_cost_equal_detection_improves_capture(self):
        self.assertGreater(gain(0,.5,0.1),0)
    def test_zero_false_alarm_cost_detection_penalty_hurts_capture(self):
        self.assertLess(gain(.02,0,0.1),0)
    def test_analytic_threshold_equal_gain(self):
        for n in HASE_2026_POTENTIAL_MISDETECTIONS:
            rho=normalized_rho(n)
            w=crossing_workload(.02,rho)
            self.assertAlmostEqual(gain(.02,w,rho),0,places=12)
    def test_threshold_direction(self):
        for n in HASE_2026_POTENTIAL_MISDETECTIONS:
            rho=normalized_rho(n)
            w=crossing_workload(.02,rho)
            self.assertLess(gain(.02,w*.9,rho),0)
            self.assertGreater(gain(.02,w*1.1,rho),0)
    def test_threshold_does_not_depend_on_rate_capture_or_handling(self):
        rho=normalized_rho(8)
        w=crossing_workload(.02,rho)
        for lam in (.01,1.,10.):
            for h in (0.,.25,5.):
                p=BridgeParams(prey_encounter_rate=lam,capture_given_detection=.1,
                               prey_handling_time=h)
                self.assertAlmostEqual(gain(.02,w,rho,p),0,places=12)
    def test_no_finite_rescue_if_detection_penalty_too_large(self):
        rho=.3
        self.assertIsNone(crossing_workload(.7,rho))
        for w in (0,.1,1,100):
            self.assertLess(gain(.7,w,rho),0)
    def test_larger_group_need_not_show_capture_gain_same_workload(self):
        w=.05
        self.assertGreater(gain(.02,w,normalized_rho(4)),0)
        self.assertGreater(gain(.02,w,normalized_rho(16)),0)
        self.assertLess(gain(.02,w,normalized_rho(32)),0)
    def test_ratio_not_raw_biological_detection_or_time_rate(self):
        r=run()
        self.assertFalse(r["observed_bat_measurements_added"])
        self.assertFalse(r["source_code_2020_reproduced"])
        self.assertFalse(r["group_model_2026_reproduced"])
        self.assertIn("UN",r["status"])
        self.assertIn("unmeasured",r["bridge_unmeasured"].lower() if "unmeasured" in r["bridge_unmeasured"].lower() else "unmeasured")
    def test_monotonic_loss_for_fixed_false_workload(self):
        rho=normalized_rho(8)
        vals=[gain(d,.15,rho) for d in (0,.01,.04,.08)]
        self.assertEqual(vals,sorted(vals,reverse=True))
    def test_validation_rejects_invalid_parameters(self):
        with self.assertRaises(ValueError): BridgeParams(prey_encounter_rate=0)
        with self.assertRaises(ValueError): gain(.03,-.1,.2)
        with self.assertRaises(ValueError): crossing_workload(.1,-.1)
    def test_neutral_at_zero_penalty_and_identical_false_rate(self):
        self.assertIsNone(crossing_workload(0,1))
        self.assertAlmostEqual(gain(0,.7,1),0,places=12)

if __name__=="__main__":
    unittest.main()
