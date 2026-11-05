"""Invented data only: scientific equations and holdout exclusions.

All fake source IDs and counts here are synthetic; tests do not open
external published PNAS supplementary or original bats.
"""
import math,unittest
import numpy as np
from molossus_2024_source_capture_LOBO_v1 import (
  COLS,DENSITY_BINS,admit_rows,density_bin,
  predictor_values,poisson_deviance_per_exposure,model_rates,score_source_test,
  evaluate_source,bootstrap_bat_mean
)

def invented_rows(n=10,rows_per_bat=16):
    groups=[]
    for bat in range(n):
        for i in range(rows_per_bat):
            E=2+(i%3)
            c_density=[0,2,10,25,40,70,95,130][i%8]
            # chosen as integer counts; strict source physical constraints
            attempts=int(round(E*(2.0+(.03*c_density))))
            fraction=max(.05,.88-.005*c_density)
            successes=min(attempts,int(round(attempts*fraction)))
            groups.append({"bat":"TEST-BAT-"+str(bat),
                "E":E,"A":attempts,"Y":successes,"C":c_density*E,
                "commute":0,"disrupt":0,"density":float(c_density),
                "z":math.log1p(float(c_density))/math.log1p(100)})
    return groups

class TestPNASOriginalBatCaptureMath(unittest.TestCase):
    def test_source_literal_columns(self):
        self.assertEqual(COLS,("bat","sec_group","numel_5swindows",
            "sum_attacks","sum_success","sum_cons","sum_commute","sum_disrupt"))
    def test_bin_bounds_source_published_prior(self):
        self.assertEqual([density_bin(x) for x in (0,1,25,26,75,76,100)],
             ["zero","positive_to_25","positive_to_25","25_to_75",
              "25_to_75","above_75","above_75"])
    def test_source_rows_validate_positive_exposure(self):
        row=[["PSEUDO_A"+str(j),str(i),2,1,1,10,0,0]
             for j in range(8) for i in range(9)]
        groups,meta=admit_rows(row)
        self.assertEqual(meta["source_individual_bat_ID_count"],8)
        self.assertEqual(meta["sum_five_second_exposures"],144)
        self.assertEqual(groups[0]["density"],5)
        self.assertNotIn("PSEUDO_A",str(meta))
    def test_counts_exceeding_source_attacks_fail_closed(self):
        bad=[["PSEUDO",str(i),2,1,2,5,0,0] for i in range(8)]
        with self.assertRaisesRegex(ValueError,"STOP_SUCCESS_EXCEEDS_ATTACK"):
            admit_rows(bad)
    def test_zero_exposure_fails(self):
        bad=[["PSEUDO",str(i),0,0,0,0,0,0] for i in range(8)]
        with self.assertRaisesRegex(ValueError,"STOP_NONPOSITIVE_GROUP_EXPOSURE"):
            admit_rows(bad)
    def test_poisson_deviance_self_consistency(self):
        self.assertAlmostEqual(poisson_deviance_per_exposure([0,2,4],[.01,2,4],3),
                              2*.01/3,places=10)
        self.assertAlmostEqual(poisson_deviance_per_exposure([1,2],[1,2],2),0,places=12)
    def test_model_predicted_capture_is_attempts_times_success_fraction(self):
        rows=invented_rows(9,12)
        rates=model_rates(rows,rows[:6])
        self.assertEqual(set(rates),
         {"M0","M1","M2","source_predicted_attack_rate",
          "source_predicted_attack_success_fraction"})
        self.assertTrue(np.allclose(rates["M2"],
             rates["source_predicted_attack_rate"]*
             rates["source_predicted_attack_success_fraction"]))
        self.assertTrue(np.all(np.isfinite(rates["M1"])))
    def test_all_models_report_per_exposure_score(self):
        rows=invented_rows(9,12)
        rates=model_rates(rows,rows[:8])
        s=score_source_test(rows[:8],rates)
        self.assertTrue(all(s[m]["capture_deviance_per_5s"]>=-1e-8 for m in ("M0","M1","M2")))
        self.assertIsNotNone(s["success_stage_negloglik_per_original_attack"])
    def test_leave_one_bat_out_purely_synthetic(self):
        rows=invented_rows(10,16)
        r=evaluate_source(rows)
        self.assertEqual(r["original_bat_independent_fold_count"],10)
        self.assertEqual(set(r["source_model_scores"]),{"M0","M1","M2"})
        self.assertEqual(set(r["paired_bat_comparisons"]),{"M1_minus_M0","M2_minus_M0","M2_minus_M1"})
        self.assertTrue(r["no_original_bat_IDs_exported"])
        self.assertNotIn("TEST-BAT",str(r))
    def test_source_bat_count_hard_stop(self):
        with self.assertRaisesRegex(ValueError,"STOP_FEWER_THAN_SEVEN_SOURCE_TRAIN_BATS"):
            evaluate_source(invented_rows(7,10))
    def test_source_bootstrap_deterministic(self):
        a=bootstrap_bat_mean([-.5,.1,.2,0,1])
        b=bootstrap_bat_mean([-.5,.1,.2,0,1])
        self.assertEqual(a,b)
        self.assertLessEqual(a[0],a[1])

if __name__=="__main__":
    unittest.main()
