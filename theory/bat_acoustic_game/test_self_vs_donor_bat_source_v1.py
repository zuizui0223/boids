"""Invented data invariants for matched 4-level self/donor bat prediction."""
import unittest,math
from self_vs_donor_bat_source_v1 import (
    MODELS,COMPARE,MIN_BATS,LEVELS,fit_four,group_test
)

L=(50,100,200,800,1600)
def invented(n=7,offsets=True,slope=False):
    result={}
    for i in range(n):
        levels={}
        for j,level in enumerate(L):
            x=math.log10(level)
            a=(i*.8 if offsets else 0)
            yy=a+(x-.5)*(.4*i if slope else 0)
            levels[str(level)+"ms"]={
                "coordinate":x,
                "delta_IF_khz":yy,
                "delta_TF_khz":.1*x,
                "delta_B_khz":yy-.1*x
            }
        result[(f"FAKE_BAT_ID{i}","IPIlow")]=levels
    return result

class TestMatchedSelfDonor(unittest.TestCase):
    def test_frozen_four_source_predictors(self):
        self.assertEqual(MODELS,("self_constant","other_constant","self_linear","other_linear"))
        self.assertEqual(LEVELS,5)
        self.assertEqual(MIN_BATS,6)
        self.assertEqual(len(COMPARE),3)
    def test_same_bat_constant_learns_individual_offset(self):
        z=group_test(invented(7,offsets=True),"IPIlow")
        self.assertEqual(z["status"],"SUPPORTED_ORIGINAL_SOURCE_GROUP")
        self.assertEqual(z["biological_bat_count"],7)
        self.assertEqual(z["source_test_bat_condition_cells"],35)
        self.assertEqual(z["one_model_source_level_training_count"],4)
        self.assertEqual(z["donor_bats_compared_per_test"],6)
        self.assertAlmostEqual(z["models"]["self_constant"]["mean_bat_equal_condition_MAE_khz"],0)
        self.assertGreater(z["models"]["other_constant"]["mean_bat_equal_condition_MAE_khz"],.3)
        self.assertEqual(z["comparison"]["self_constant_minus_donor_constant"]["bats_first_model_better"],7)
    def test_identical_bats_do_not_falsely_show_personal_policy(self):
        z=group_test(invented(7,offsets=False),"IPIlow")
        self.assertAlmostEqual(z["models"]["self_constant"]["mean_bat_equal_condition_MAE_khz"],0)
        self.assertAlmostEqual(z["models"]["other_constant"]["mean_bat_equal_condition_MAE_khz"],0)
        self.assertEqual(z["comparison"]["self_constant_minus_donor_constant"]["bats_tie"],7)
    def test_bat_specific_slope_favors_self_linear(self):
        z=group_test(invented(7,offsets=True,slope=True),"IPIlow")
        self.assertLess(z["models"]["self_linear"]["mean_bat_equal_condition_MAE_khz"],1e-10)
        self.assertGreater(z["models"]["other_linear"]["mean_bat_equal_condition_MAE_khz"],.1)
    def test_single_matched_model_uses_four_not_all_five(self):
        group=invented(7)[("FAKE_BAT_ID0","IPIlow")]
        levels=list(group)
        train=[group[i] for i in levels[1:]]
        guess=fit_four(train,group[levels[0]])
        self.assertEqual(set(guess),{"constant","linear"})
    def test_less_than_four_train_conditions_stops(self):
        group=invented(7)[("FAKE_BAT_ID0","IPIlow")]
        train=list(group.values())[:3]
        with self.assertRaisesRegex(ValueError,"FOUR_SOURCE_LEVEL"):
            fit_four(train,list(group.values())[-1])
    def test_five_bats_not_six_hard_stop(self):
        z=group_test(invented(5),"IPIlow")
        self.assertEqual(z["status"],"STOP_TOO_FEW_BIOLOGICAL_SOURCE_BATS")
    def test_missing_one_donor_level_is_support_stop(self):
        q=invented(7)
        k=("FAKE_BAT_ID5","IPIlow")
        del q[k]["200ms"]
        z=group_test(q,"IPIlow")
        self.assertEqual(z["status"],"STOP_UNMATCHED_SOURCE_STIMULUS_LEVELS")
    def test_wrong_experiment_is_stop(self):
        z=group_test(invented(7),"SPLlow")
        self.assertEqual(z["status"],"STOP_TOO_FEW_BIOLOGICAL_SOURCE_BATS")
    def test_no_raw_id_export(self):
        z=group_test(invented(7),"IPIlow")
        self.assertNotIn("FAKE_BAT_ID",str(z))
        self.assertFalse(z["source_bat_IDs_in_results"])
    def test_biological_inference_only_seven_source_recipients(self):
        z=group_test(invented(7,offsets=True,slope=True),"IPIlow")
        for m in MODELS:
            self.assertEqual(z["models"][m]["biological_bats"],7)
            self.assertEqual(z["models"][m]["bat_condition_test_cells"],35)
    def test_whole_bat_ci_is_reproducible(self):
        a=group_test(invented(7,offsets=True,slope=True),"IPIlow")
        b=group_test(invented(7,offsets=True,slope=True),"IPIlow")
        self.assertEqual(a["comparison"],b["comparison"])

if __name__=="__main__":
    unittest.main()
