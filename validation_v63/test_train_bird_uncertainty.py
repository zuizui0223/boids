"""Synthetic known-truth v63 train-source cluster bootstrap tests; no wild evidence."""
import unittest
from copy import deepcopy
import numpy as np

from train_bird_uncertainty import (
    _blocks_by_original_2010_bird,_resample_source_blocks,
    _prepare_original_pairs,_fitted_original_pair_T,
    analyze_training_bird_uncertainty)

def toy():
    train=[]
    for i in range(8):
        for k in range(4):
            train.append({"id":f"source_{i}","polarity":1 if i<4 else -1,
                          "source_idx":k})
    test=[]
    pairs=[]
    qualified=[]
    for b in range(10):
        for k in range(2):
            i=len(test)
            test.extend([{"id":f"observed_{b}","phase":1,
                          "target_e":1.,"target_n":0.},
                         {"id":f"observed_{b}","phase":-1,
                          "target_e":0.,"target_n":1.}])
            pairs.append((i,i+1))
            if b<7:qualified.append((i,i+1))
    return train,test,pairs,qualified

def independent_known_forecast(train,test,level):
    if level!=1:raise AssertionError("v63 original phase-conditioned model only")
    if not train:raise ValueError("missing model training")
    return np.asarray([[1.,0.] if row["phase"]==1 else [0.,1.]
                       for row in test])

def source_dependent_forecast(train,test,level):
    # Known-truth: fitting source-bird composition changes the projected angle.
    sign=1 if np.mean([r["polarity"] for r in train])>=0 else -1
    pred=np.asarray([[1.,0.] if r["phase"]==1 else [0.,1.]
                     for r in test])
    return pred if sign==1 else pred[:,::-1]

class TrainingBirdBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.train,self.test,self.pairs,self.qualified=toy()

    def test_source_draw_clones_whole_birds_and_keeps_equal_slot_ids(self):
        blocks=_blocks_by_original_2010_bird(self.train,strict=False)
        selected=[0,0,1,3,3,3,7,2]
        duplicated=_resample_source_blocks(blocks,selected)
        self.assertEqual(len(duplicated),32)
        self.assertEqual(len({r["id"] for r in duplicated}),8)
        self.assertEqual([sum(r["id"]==f"v63_draw_slot_{i}" for r in duplicated)
                          for i in range(8)],[4]*8)
        self.assertTrue(all(duplicated[4*i]["polarity"]==blocks[j][0]["polarity"]
                            for i,j in enumerate(selected)))
        # The source originals are immutable and none of their identifiers
        # should be silently retained as bootstrap cluster IDs.
        self.assertEqual(len({r["id"] for r in self.train}),8)
        self.assertNotIn("source_0",{r["id"] for r in duplicated})

    def test_bootstrap_known_true_positive_and_source_qualified_separate(self):
        out=analyze_training_bird_uncertainty(
            self.train,self.test,self.pairs,self.qualified,
            independent_known_forecast,reps=40,strict=False)
        self.assertEqual(out["source_training_bootstrap_reps"],40)
        self.assertAlmostEqual(out["main_all_211_original_real_matched_pairs"][
            "original_fixed_source_T_replay"],.5)
        self.assertAlmostEqual(out["secondary_source_qualified_204_real_pairs"][
            "original_fixed_source_T_replay"],.5)
        for name in ("main_all_211_original_real_matched_pairs",
                     "secondary_source_qualified_204_real_pairs"):
            result=out[name]
            for mode in ("train_bird_only_bootstrap",
                         "joint_train_and_test_bird_bootstrap"):
                self.assertEqual(result[mode]["percentile_95"],[.5,.5])
                self.assertEqual(result[mode]["fraction_positive"],1.)
            self.assertEqual(result["leave_one_original_train_bird_out"][
                "positive_leave_one_out_models"],8)
        self.assertEqual(out["v63_primary_status"],
                         "TRAINING_AND_TEST_BIRD_POSITIVE_EXPLORATORY")
        self.assertNotIn("source_0",str(out))
        self.assertNotIn("observed_0",str(out))

    def test_heterogeneous_source_birds_change_model_and_training_interval(self):
        out=analyze_training_bird_uncertainty(
            self.train,self.test,self.pairs,self.qualified,
            source_dependent_forecast,reps=64,strict=False)
        d=out["main_all_211_original_real_matched_pairs"]
        self.assertLess(d["train_bird_only_bootstrap"]["percentile_95"][0],0)
        self.assertGreater(d["train_bird_only_bootstrap"]["percentile_95"][1],0)
        self.assertEqual(d["leave_one_original_train_bird_out"][
            "positive_leave_one_out_models"],4)
        self.assertEqual(out["v63_primary_status"],
                         "TRAINING_UNCERTAINTY_POSITIVE_NOT_ESTABLISHED")
        self.assertEqual(out,analyze_training_bird_uncertainty(
            self.train,self.test,self.pairs,self.qualified,
            source_dependent_forecast,reps=64,strict=False))

    def test_only_actual_future_headings_determine_sign_not_selection(self):
        original=analyze_training_bird_uncertainty(
            self.train,self.test,self.pairs,self.qualified,
            independent_known_forecast,reps=20,strict=False)
        other=deepcopy(self.test)
        for r in other:
            r["target_e"],r["target_n"]=(0.,1.) if r["phase"]==1 else (1.,0.)
        changed=analyze_training_bird_uncertainty(
            self.train,other,self.pairs,self.qualified,
            independent_known_forecast,reps=20,strict=False)
        self.assertEqual(original["source_bootstrap_distinct_birds"],
                         changed["source_bootstrap_distinct_birds"])
        self.assertAlmostEqual(
            changed["main_all_211_original_real_matched_pairs"][
                "original_fixed_source_T_replay"],-.5)
        self.assertEqual(changed["v63_primary_status"],
                         "TRAINING_UNCERTAINTY_POSITIVE_NOT_ESTABLISHED")

    def test_zero_or_nan_fitted_bearing_hard_stop_not_bootstrap_pruning(self):
        def bad(train,rows,level):return np.zeros((len(rows),2))
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
            analyze_training_bird_uncertainty(
                self.train,self.test,self.pairs,self.qualified,
                bad,reps=20,strict=False)
        def nan(train,rows,level):return np.full((len(rows),2),np.nan)
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
            analyze_training_bird_uncertainty(
                self.train,self.test,self.pairs,self.qualified,
                nan,reps=20,strict=False)
        def shape(train,rows,level):return np.zeros((1,2))
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
            analyze_training_bird_uncertainty(
                self.train,self.test,self.pairs,self.qualified,
                shape,reps=20,strict=False)

    def test_no_qualified_postresult_change_or_duplicate_test_pairs(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            _prepare_original_pairs(self.test,self.pairs,self.pairs+[(0,1)])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            _prepare_original_pairs(self.test,self.pairs,self.qualified+[(0,1)])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            _prepare_original_pairs(self.test,self.pairs[:1]+self.pairs[:1],
                                    self.qualified[:1])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            _resample_source_blocks(_blocks_by_original_2010_bird(self.train,
                                           strict=False),[0,1,2])

if __name__=="__main__":
    unittest.main()
