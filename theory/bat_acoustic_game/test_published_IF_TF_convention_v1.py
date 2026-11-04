"""Synthetic verification of source-reuse IF/TF aggregate computation.

All test records below are invented; NEVER original bats.
"""
from __future__ import annotations
import math
import unittest

from published_IF_TF_convention_v1 import (
   EXPERIMENTS,MIN_CALLS_PER_ARM,MIN_CONDITIONS,
   clean_source_rows,contrast_contexts,bat_error_summary,
   bootstrap_means,leave_one_out_range,two_sided_sign_p,
   stimulus_coordinate,summarize_group,
)


def toy(bat,IF_on,TF_on,IF_off=90,TF_off=45,n=5):
    rows=[]
    for level in (50,100,200,800,1600):
        for on in ("0","1"):
            for k in range(n):
                rows.append({"ID":bat,"Experiment":"IPIlow",
                  "Condition":str(level)+"ms","Var":"toy",
                  "jammingTF":"toy45","isON":on,
                  "IF":str(IF_on if on=="1" else IF_off),
                  "TF":str(TF_on if on=="1" else TF_off)})
    return rows


def assess(rows,mode="median"):
    by,qc=clean_source_rows(rows)
    contexts,support=contrast_contexts(by,mode)
    batlevel={(i,e):bat_error_summary(d) for (i,e),d in contexts.items()}
    return summarize_group(batlevel,"IPIlow"),qc,support


class TestIFTFSourceAnalytic(unittest.TestCase):
    def test_registered_stimulus_levels(self):
        self.assertEqual(stimulus_coordinate("IPIlow","100ms"),2.0)
        self.assertEqual(stimulus_coordinate("SPLlow","-30dB"),-30.)
        self.assertIsNone(stimulus_coordinate("IPIlow","bad"))
    def test_fixed_start_wins_and_bandwidth_changes(self):
        s,q,_=assess(toy("synthetic-A",90,47))
        self.assertEqual(s["n_bats"],1)
        self.assertAlmostEqual(s["equal_bat_mean_delta_IF_khz"],0)
        self.assertAlmostEqual(s["equal_bat_mean_delta_TF_khz"],2)
        self.assertAlmostEqual(s["equal_bat_mean_delta_B_khz"],-2)
        self.assertAlmostEqual(s["equal_bat_mean_absolute_error_fixed_start_khz"],0)
        self.assertAlmostEqual(s["equal_bat_mean_absolute_error_fixed_bandwidth_khz"],2)
        self.assertEqual(s["source_bats_favor_fixed_start"],1)
    def test_fixed_bandwidth_wins(self):
        s,_,_=assess(toy("synthetic-B",92,47))
        self.assertAlmostEqual(s["equal_bat_mean_delta_B_khz"],0)
        self.assertAlmostEqual(s["equal_bat_mean_absolute_error_fixed_bandwidth_khz"],0)
        self.assertAlmostEqual(s["mean_D_bandwidth_minus_start_khz"],-2)
        self.assertEqual(s["source_bats_favor_fixed_bandwidth"],1)
    def test_intermediate_slope_gives_equal_absolute_errors(self):
        s,_,_=assess(toy("synthetic-C",91,47))
        self.assertEqual(s["source_bats_exact_or_near_ties"],1)
        self.assertAlmostEqual(s["mean_D_bandwidth_minus_start_khz"],0)
    def test_same_source_rows_mean_and_median_consistency_when_constant(self):
        rows=toy("a",90,46)
        a,_,_=assess(rows,"median")
        b,_,_=assess(rows,"mean")
        self.assertAlmostEqual(a["mean_D_bandwidth_minus_start_khz"],
                               b["mean_D_bandwidth_minus_start_khz"])
    def test_complete_case_source_rows_and_malformed_FM_exclusion(self):
        rows=toy("a",90,46)
        rows.append({"ID":"fictitious","Experiment":"IPIlow","Condition":"50ms",
            "Var":"toy","jammingTF":"toy45","isON":"0","IF":"40","TF":"41"})
        s,q,support=assess(rows)
        self.assertEqual(s["n_bats"],1)
        self.assertEqual(q["rows_excluded_by_reason"]["not_downward_FM_IF_gt_TF"],1)
        self.assertEqual(support["IPIlow"],5)
    def test_below_four_calls_arm_is_excluded(self):
        rows=toy("a",90,46,n=3)
        s,q,support=assess(rows)
        self.assertEqual(s["n_bats"],0)
        self.assertFalse(support)
    def test_three_levels_minimum(self):
        d={"50ms":{"coordinate":1.0,"delta_IF_khz":0,"delta_TF_khz":1,"delta_B_khz":-1},
           "100ms":{"coordinate":2.0,"delta_IF_khz":0,"delta_TF_khz":1,"delta_B_khz":-1}}
        self.assertIsNone(bat_error_summary(d))
        d["200ms"]={"coordinate":3.0,"delta_IF_khz":0,"delta_TF_khz":1,"delta_B_khz":-1}
        self.assertIsNotNone(bat_error_summary(d))
    def test_two_individuals_are_two_biological_units_not_100_rows(self):
        rows=toy("a",90,46)+toy("b",91,46)
        s,_,_=assess(rows)
        self.assertEqual(s["n_bats"],2)
        self.assertEqual(s["n_bat_condition_cells"],10)
    def test_no_bat_ids_in_summary(self):
        s,q,_=assess(toy("VeryDistinctOriginalIDDoNotPrint",90,47))
        self.assertNotIn("VeryDistinctOriginalIDDoNotPrint",str(s))
        self.assertNotIn("VeryDistinctOriginalIDDoNotPrint",str(q))
        self.assertTrue(s["no_raw_ID_output"])
    def test_bootstrap_reproducibility(self):
        a=bootstrap_means([1,2,3],draws=75)
        b=bootstrap_means([1,2,3],draws=75)
        self.assertEqual(a,b)
        self.assertTrue(a[0]<=a[1])
    def test_leave_one_out_exact(self):
        self.assertEqual(leave_one_out_range([1,2,3]),[1.5,2.5])
    def test_descriptive_sign_exact(self):
        self.assertAlmostEqual(two_sided_sign_p(7,0),2/2**7)
        self.assertAlmostEqual(two_sided_sign_p(3,4),1.)
    def test_source_code_primary_experiment_fixed(self):
        self.assertEqual(EXPERIMENTS,("IPIlow","IPIhigh","SPLlow"))
        self.assertEqual(MIN_CALLS_PER_ARM,4)
        self.assertEqual(MIN_CONDITIONS,3)


if __name__=="__main__":
    unittest.main()
