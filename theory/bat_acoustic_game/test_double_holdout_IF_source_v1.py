"""Invented-only source double-holdout regression tests; ZERO animal responses."""
import math
import unittest
from double_holdout_IF_source_v1 import (
    METHODS,MODELS,FORWARD_MODELS,CONDITIONAL_MODELS,
    MIN_TRAIN_BATS,MIN_TRAIN_STIMULI,
    ols_fit,predict,group_double_holdout,
)


LEVELS=(50,100,200,800,1600)
def fake_source(n=7,with_signal=True):
    out={}
    for i in range(n):
        conditions={}
        for level in LEVELS:
            x=math.log10(level)
            y=(2.+3.*x) if with_signal else (.5*i+1)
            tf=(1.1+.15*x+.05*i)
            conditions[str(level)+"ms"]={
               "coordinate":x,"delta_IF_khz":y,
               "delta_TF_khz":tf,"delta_B_khz":y-tf
            }
        out[(f"toy-{i}","IPIlow")]=conditions
    return out

class TestDoubleHoldout(unittest.TestCase):
    def test_forward_and_conditional_classes_never_confused(self):
        self.assertEqual(FORWARD_MODELS,
            ("zero","constant_training_mean","stimulus_linear"))
        self.assertEqual(CONDITIONAL_MODELS,
            ("fixed_bandwidth","trained_IF_TF_affine"))
        self.assertEqual(set(FORWARD_MODELS)|set(CONDITIONAL_MODELS),set(MODELS))
    def test_minimum_bats_and_levels(self):
        self.assertEqual(MIN_TRAIN_BATS,5)
        self.assertEqual(MIN_TRAIN_STIMULI,3)
    def test_regression_exact_line(self):
        train=[{"x":x,"y":2+3*x} for x in range(10)]
        a,b=ols_fit(train,"y","x")
        self.assertAlmostEqual(a,2)
        self.assertAlmostEqual(b,3)
    def test_regression_rejects_constant_design(self):
        with self.assertRaisesRegex(ValueError,"STOP_NO_TRAINING_VARIANCE"):
            ols_fit([{"x":1,"y":4},{"x":1,"y":5}],"y","x")
    def test_identical_training_input_predictions_all_finite(self):
        train=[{"coordinate":float(i),
                "delta_IF_khz":1.+.7*i,"delta_TF_khz":float(i)*.3}
                 for i in range(3,10)]
        test={"coordinate":11.,"delta_IF_khz":8.7,"delta_TF_khz":3.3}
        y=predict(train,test)
        self.assertEqual(set(y),set(MODELS))
        self.assertTrue(all(math.isfinite(z) for z in y.values()))
        self.assertEqual(y["zero"],0.)
        self.assertEqual(y["fixed_bandwidth"],3.3)
        self.assertAlmostEqual(y["stimulus_linear"],8.7)
    def test_true_stimulus_linear_generalizes_to_unseen_animal_and_level(self):
        result=group_double_holdout(fake_source(),"IPIlow")
        self.assertEqual(result["status"],"EVALUATED")
        self.assertEqual(result["eligible_bats"],7)
        self.assertEqual(result["n_evaluated_original_bat_condition_folds"],35)
        self.assertEqual(result["training_bats_min_max"],[6,6])
        self.assertEqual(result["training_conditions_min_max"],[4,4])
        self.assertEqual(result["training_cell_count_min_max"],[24,24])
        self.assertLess(result["models"]["stimulus_linear"]["equal_bat_MAE_khz"],1e-10)
        self.assertGreater(result["models"]["constant_training_mean"]["equal_bat_MAE_khz"],.1)
        self.assertEqual(result["comparisons"]["stimulus_linear_vs_constant"]["source_bats_for_first_model"],7)
    def test_intermediate_training_recovery_has_no_original_bat_ids(self):
        result=group_double_holdout(fake_source(),"IPIlow")
        self.assertNotIn("toy-1",str(result))
        self.assertTrue(result["no_source_ID_exported"])
        self.assertEqual(result["models"]["stimulus_linear"]["n_source_bat_condition_test_pairs"],35)
    def test_bat_support_stop_if_five(self):
        result=group_double_holdout(fake_source(n=5),"IPIlow")
        self.assertEqual(result["status"],"STOP_TOO_FEW_BIOLOGICAL_BATS")
    def test_condition_support_stop_if_three(self):
        src=fake_source()
        for k in src:src[k]={p:src[k][p] for p in list(src[k])[:3]}
        result=group_double_holdout(src,"IPIlow")
        self.assertEqual(result["status"],"STOP_TOO_FEW_SOURCE_CONDITIONS")
    def test_absent_experiment_is_stop(self):
        result=group_double_holdout(fake_source(),"IPIhigh")
        self.assertEqual(result["status"],"STOP_TOO_FEW_BIOLOGICAL_BATS")
    def test_no_stimulus_relationship_mean_only_not_identity(self):
        # Bat-specific constant signal, distinct test bats; training across
        # other bats cannot correctly guess the held-out individual's offset.
        result=group_double_holdout(fake_source(with_signal=False),"IPIlow")
        self.assertGreater(result["models"]["stimulus_linear"]["equal_bat_MAE_khz"],.01)
        self.assertEqual(result["models"]["stimulus_linear"]["information_class"],
                         "stimulus_only_forward")
    def test_source_folds_are_independent_training_bat_labels(self):
        # Algebra of group_double_holdout enforces this through counts:
        # if 7 bats, each training fold includes exactly six distinct bats.
        result=group_double_holdout(fake_source(),"IPIlow")
        self.assertEqual(result["training_bats_min_max"],[6,6])
        self.assertNotIn("raw",result)
    def test_descriptive_bootstrap_not_model_significance(self):
        r=group_double_holdout(fake_source(),"IPIlow")
        o=r["comparisons"]["stimulus_linear_vs_constant"]
        self.assertEqual(o["inference_level"],
           "DESCRIPTIVE_SOURCE_BAT_ERRORS_NOT_INDEPENDENT_EXTERNAL_REPLICATION")
        self.assertLess(o["whole_bat_bootstrap_mean_delta_95_khz"][1],0)

if __name__=="__main__":
    unittest.main()
