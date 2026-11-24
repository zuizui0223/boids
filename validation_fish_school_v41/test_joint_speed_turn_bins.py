"""v41 six purely SYNTHETIC source-free known truth 2x2 speed×turn bins."""
import unittest
import numpy as np
from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v33.neighbor_panels import original_panels
from validation_fish_school_v41.joint_speed_turn_bins import (
 original_joint_speed_turn_source_moments,JOINT_CATEGORIES,ALL_CATEGORIES
)
from validation_fish_school_v41.aggregate_joint_shoal_prediction import (
 summarize_joint,CONDITIONAL_COMPARISONS,ORDERED_ENDPTS
)
from validation_fish_school_v40.source_speed_turn_strata import MODELS


def fake_original(n=5000):
    t=np.arange(n,dtype=float)
    p=np.zeros((n,8,2),dtype=float)
    for i in range(8):
        p[:,i,0]=10*i+.03*t+2*np.sin(t/(19+i*3))
        p[:,i,1]=6*i+.02*t+2*np.cos(t/(26+i*4))
    return t,p


class JointOriginalKnownTruth(unittest.TestCase):
    def test_joint_infers_no_original_future_kinematic_strata(self):
        t,p=fake_original()
        x=original_panels(t,p,"ARTIFICIAL_ONLY")
        report=original_joint_speed_turn_source_moments(x)
        self.assertEqual(set(report["stratum_sufficient_statistics"]),set(ALL_CATEGORIES))
        self.assertEqual(set(report["stratum_sufficient_statistics"]["SLOW_TLOW"]),set(MODELS))
        self.assertTrue(report["source_test_condition_assignment_never_uses_future_y"])
        self.assertTrue(report["original_XY_Y_or_individual_source_times_not_exported"])

    def test_joint_four_cells_are_exact_partition_of_all_defined_turns(self):
        t,p=fake_original()
        x=original_panels(t,p)
        r=original_joint_speed_turn_source_moments(x)
        bins=r["stratum_sufficient_statistics"]
        c=sum(bins[q]["G_geometry"]["n"] for q in JOINT_CATEGORIES)
        self.assertEqual(c,r["source_original_focal_rows"]-r["source_original_turning_undefined_rows"])
        for key in ["sx","sxx","sxy","sy","syy"]:
            np.testing.assert_allclose(
              bins["SLOW_TLOW"]["NEAR_TRUE"][key]+bins["SHIGH_TLOW"]["NEAR_TRUE"][key],
              bins["turn_low"]["NEAR_TRUE"][key],rtol=1e-9,atol=1e-3)
            np.testing.assert_allclose(
              bins["SLOW_THIGH"]["GLOBAL"][key]+bins["SHIGH_THIGH"]["GLOBAL"][key],
              bins["turn_high"]["GLOBAL"][key],rtol=1e-9,atol=1e-3)

    def test_outcome_changes_cannot_alter_focal_G_strata_counts(self):
        t,p=fake_original()
        case=original_panels(t,p)
        counts=original_joint_speed_turn_source_moments(case)["source_original_4_joint_categories_rows"]
        altered={**case,"Y":case["Y"].copy()}
        altered["Y"][:,0]*=300.
        changed=original_joint_speed_turn_source_moments(altered)["source_original_4_joint_categories_rows"]
        self.assertEqual(counts,changed)

    def test_pre_registered_primary_conditionals_and_interaction_source_free(self):
        vals={"SLOW_TLOW":{"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":98.,"NEAR_ROT1":99.},
              "SLOW_THIGH":{"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":95.,"NEAR_ROT1":99.},
              "SHIGH_TLOW":{"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":90.,"NEAR_ROT1":99.},
              "SHIGH_THIGH":{"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":84.,"NEAR_ROT1":99.}}
        folds=[]
        for i in range(1,13):
            folds.append({
             "original_biological_shoal_test_ID":str(i),
             "joint_category_file_equal_group_MSE":{
                cat:{model:{"short":mse,"delayed":mse} for model,mse in scores.items()}
                 for cat,scores in vals.items()}
            })
        d=summarize_joint(folds,{"synthetic":True})
        m=d["original_joint_speed_and_turn_predictions_by_future_horizon"]["short"]["speed_and_turn_conditional_outcomes"]
        self.assertAlmostEqual(m["TURN_EFFECT_WITHIN_LOW_SPEED"]["local_beyond_GLOBAL"]["equal_original_12_shoal_mean_relative_GAIN_difference"],.03)
        self.assertAlmostEqual(m["TURN_EFFECT_WITHIN_HIGH_SPEED"]["local_beyond_GLOBAL"]["equal_original_12_shoal_mean_relative_GAIN_difference"],.06)
        self.assertAlmostEqual(m["SPEED_EFFECT_WITHIN_LOW_TURN"]["local_beyond_GLOBAL"]["equal_original_12_shoal_mean_relative_GAIN_difference"],.08)
        self.assertAlmostEqual(m["SPEED_EFFECT_WITHIN_HIGH_TURN"]["local_beyond_GLOBAL"]["equal_original_12_shoal_mean_relative_GAIN_difference"],.11)
        self.assertAlmostEqual(m["SPEEDxTURN_DIFF_IN_DIFF"]["local_beyond_GLOBAL"]["equal_original_12_shoal_mean_relative_GAIN_difference"],.03)
        self.assertEqual(m["SPEEDxTURN_DIFF_IN_DIFF"]["local_beyond_GLOBAL"]["positive_original_shoals"],12)

    def test_original_2x2_named_cell_order_frozen(self):
        self.assertEqual(JOINT_CATEGORIES,("SLOW_TLOW","SLOW_THIGH","SHIGH_TLOW","SHIGH_THIGH"))
        self.assertEqual(len(ALL_CATEGORIES),9)
        self.assertEqual(len(CONDITIONAL_COMPARISONS),4)
        self.assertEqual(len(ORDERED_ENDPTS),5)

    def test_source_file_missing_or_nan_COHORT_STOP_on_stratum(self):
        t,p=fake_original()
        x=original_panels(t,p)
        x["X"]["G_geometry"][1500,2]=np.nan
        with self.assertRaises(SourceStop):
            original_joint_speed_turn_source_moments(x)

if __name__=="__main__":unittest.main()
