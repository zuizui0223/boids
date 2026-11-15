"""Invented bats only; all original source outcomes remain outside test fixtures."""
import unittest
from molossus_withinbat_highdensity_v1 import (
    exact_lower_tail, mantel_haenszel_or, observed_bat_contrast,
    flight_third, run_time_stratification
)

def fake_rows():
    rows=[]
    for i in range(4):
        bat="TEST_BAT_"+str(i)
        for k in range(20):
            d=80 if k%2 else 35
            rows.append({"bat":bat,"sec":k,"E":1,"density":d,"A":1,
                         "Y":1 if d==35 else 0})
    return rows

class TestWithinBatHighDensity(unittest.TestCase):
    def test_exact_one_bat_example(self):
        t=[{"high_attacks":2,"high_success":0,
            "ref_attacks":2,"ref_success":2}]
        self.assertAlmostEqual(exact_lower_tail(t),1/6,places=13)
    def test_exact_two_bat_convolution(self):
        t=[{"high_attacks":2,"high_success":0,
            "ref_attacks":2,"ref_success":2}]*2
        self.assertAlmostEqual(exact_lower_tail(t),1/36,places=13)
    def test_mh_odds_ratio_one_and_zero(self):
        t=[{"high_attacks":2,"high_success":1,
            "ref_attacks":2,"ref_success":1}]
        self.assertAlmostEqual(mantel_haenszel_or(t),1)
        t[0]["high_success"]=0;t[0]["ref_success"]=2
        self.assertAlmostEqual(mantel_haenszel_or(t),0)
    def test_bat_not_five_second_window_is_primary_unit(self):
        out=observed_bat_contrast(fake_rows(), "moderate")
        self.assertEqual(out["eligible_bats"],4)
        self.assertEqual(out["high_attacks_eligible"],40)
        self.assertEqual(out["reference_attacks_eligible"],40)
        self.assertEqual(out["bat_mean_high_minus_reference_success_fraction"],-1)
        self.assertNotIn("TEST_BAT",str(out))
    def test_no_time_bin_leakage(self):
        self.assertEqual(flight_third(0,0,11),0)
        self.assertEqual(flight_third(3,0,9),1)
        self.assertEqual(flight_third(6,0,9),2)
        self.assertEqual(flight_third(9,0,9),2)
    def test_time_strata_support_on_fake_bats(self):
        out=run_time_stratification(fake_rows())
        self.assertEqual(out["source_bats_with_time_matched_high_and_moderate_attacks"],4)
        self.assertEqual(out["support_status"],"SUPPORTED")
        self.assertLess(out["conditional_exact_lower_tail"],.01)
    def test_all_zeros_are_not_treated_as_negative_success(self):
        rows=[{"bat":"AA","sec":0,"E":1,"density":90,"A":0,"Y":0},
              {"bat":"AA","sec":1,"E":1,"density":30,"A":1,"Y":1}]
        out=observed_bat_contrast(rows,"moderate")
        self.assertEqual(out["eligible_bats"],0)
        self.assertIsNone(out["conditional_exact_lower_tail"])
if __name__=="__main__":unittest.main()
