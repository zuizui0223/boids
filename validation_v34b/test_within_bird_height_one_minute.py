"""Invented cases only; do not read any original GPS or tide data."""
import unittest
import json
import within_bird_height_one_minute as m

def datum(h,delta,n=2):
    return {"year":2010,"height_band":h,"duration":"short_5_30",
            "n_ebb":n,"n_flood":n,
            "ebb_minus_flood_speed":delta,
            "ebb_minus_flood_elapsed_minutes":0.,
            "ebb_minus_flood_water_height_m":0.}
class KnownTruth(unittest.TestCase):
    def test_no_post_result_condition_change(self):
        self.assertEqual(m.MIN_PER_BIRD_PER_REGIME,8)
        self.assertEqual(m.THRESHOLD_NAP_M,.5)
        self.assertEqual(m.MIN_SUPPORT_BIRDS,20)
        self.assertEqual(m.MIN_TOTAL_STRATA,200)
    def test_exact_one_minute_duration_rounding_tie_lower(self):
        self.assertEqual(m.one_minute_bin(5),5)
        self.assertEqual(m.one_minute_bin(10.49),10)
        self.assertEqual(m.one_minute_bin(10.50),10)
        self.assertEqual(m.one_minute_bin(10.51),11)
        self.assertEqual(m.one_minute_bin(180),180)
        with self.assertRaises(ValueError):m.one_minute_bin(181)
    def test_same_original_birds_in_both_height_regimes(self):
        d={}
        for i in range(20):
            low=[datum(-2,1. if i==0 else .2) for k in range(12)]
            high=[datum(1,-.3) for k in range(12)]
            d[f"private-bird-{i:02d}"]=low+high
        # One extreme-response bird cannot dominate equal-bird result.
        out=m.same_bird_height_contrast(d)
        self.assertEqual(out["status"],"EXPLORATORY_POSTOUTCOME_SAME_BIRD_HEIGHT_DIRECTION_AUDIT")
        self.assertEqual(out["support"]["original_v34_matched_birds_in_both_height_regimes"],20)
        self.assertAlmostEqual(out["effects"]["LOW_ebb_minus_flood"]["mean"],(1+19*.2)/20)
        self.assertAlmostEqual(out["effects"]["HIGH_ebb_minus_flood"]["mean"],-.3)
        self.assertEqual(out["birds_with_LOW_positive_and_HIGH_negative"],20)
        self.assertEqual(out,m.same_bird_height_contrast(d))
        self.assertNotIn("private-",json.dumps(out))
    def test_same_bird_height_stop_no_replacement(self):
        d={f"private-{i}":[datum(-1,.1) for k in range(10)] for i in range(50)}
        out=m.same_bird_height_contrast(d)
        self.assertEqual(out["status"],"NOT_ADMITTED_V34B_WITHIN_BIRD_HEIGHT_SUPPORT")
        self.assertFalse(out["any_new_paired_height_effect_reported"])
        self.assertNotIn("effects",out)
    def test_minute_duration_support_gate(self):
        x=m.minute_effect({},{"admitted_original_birds":0,"admitted_one_minute_matched_strata":0})
        self.assertEqual(x["status"],"NOT_ADMITTED_V34B_ONE_MINUTE_DURATION_SUPPORT")
        self.assertNotIn("matched_effects",x)
    def test_one_minute_match_strata_from_synthetic_aggregates(self):
        raw={}
        for b in range(24):
            for k in range(10):
                key=(f"private-{b}",2010,5,k,-1,10)
                raw[key]=[[2,.5,20.,-.3],[2,.3,20.,-.4]]
        matched,support=m.minute_matched_pairs(raw)
        self.assertEqual(support["admitted_original_birds"],24)
        self.assertEqual(support["admitted_one_minute_matched_strata"],240)
        out=m.minute_effect(matched,support)
        self.assertEqual(out["status"],"EXPLORATORY_POSTOUTCOME_ONE_MINUTE_DUTY_MATCHED_AUDIT")
        self.assertAlmostEqual(out["matched_effects"]["ebb_minus_flood_log1p_speed"]["mean"],.1)
        self.assertAlmostEqual(out["matched_effects"]["ebb_minus_flood_elapsed_minutes"]["mean"],0.)
        self.assertNotIn("private-",json.dumps(out))
    def test_full_frozen_receipt_comparator_is_strict(self):
        self.assertTrue(m.v34.nested_close({"x":1.0},{"x":1.0}))
        self.assertFalse(m.v34.nested_close({"x":1.0},{"x":1.1}))
if __name__=="__main__":
    unittest.main()
