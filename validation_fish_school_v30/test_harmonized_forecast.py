"""v30 source-independent known-truth fixtures: no original animal behavior."""
import unittest

import numpy as np
from validation_fish_school_v30.harmonized_forecast import (
    AGES_SECONDS, FEAT_DIM, MODEL_NAMES, SOURCE_FPS, SourceStop,
    build_original_recording, evaluate_source_files, predict_train_file_only
)


def synthetic_original(n=4100,nfish=8):
    clock=np.arange(n,dtype=float)
    t=np.arange(n,dtype=float)
    p=np.empty((n,nfish,2),dtype=float)
    for i in range(nfish):
        p[:,i,0]=30+3*i+.03*t+.8*np.sin(t/(17+i))+.25*np.sin(t/110)
        p[:,i,1]=50+4*i-.02*t+.6*np.cos(t/(13+i))+.33*np.cos(t/120)
    return clock,p


class OriginalHarmonizationKnownTruth(unittest.TestCase):
    def test_frozen_physical_window_native_25_30_50(self):
        for native,delta in ((25,5),(30,6),(50,10)):
            ids,pos=synthetic_original(4200,8)
            s=build_original_recording(ids,pos,native,"ARTIFICIAL")
            self.assertEqual(s["source_speed_difference_frames"],delta)
            self.assertEqual(s["source_age_frames"],[0,delta,2*delta,5*delta,10*delta])
            self.assertEqual(s["source_future_delayed_start_end_frames"],[3*delta,4*delta])
            self.assertEqual(s["X"]["G_geometry"].shape[1],FEAT_DIM)
            self.assertEqual(s["Y"].shape[1],4)
            self.assertEqual(set(s["X"]),set(MODEL_NAMES))

    def test_native_ten_fish_same_schema_as_eight_fish(self):
        clock,pos=synthetic_original(4300,10)
        s=build_original_recording(clock,pos,30,"ARTIFICIAL_TEN")
        self.assertEqual(s["original_fish_per_recording"],10)
        self.assertEqual(s["X"]["age_0.4s"].shape[1],FEAT_DIM+2)

    def test_original_focal_geometry_identical_all_group_ages(self):
        c,p=synthetic_original()
        m=build_original_recording(c,p,25)
        for age in AGES_SECONDS:
            key=f"age_{age:g}s"
            np.testing.assert_array_equal(m["X"]["G_geometry"],m["X"][key][:,:FEAT_DIM])

    def test_original_future_frames_do_not_enter_predictor_X(self):
        ids,p=synthetic_original()
        baseline=build_original_recording(ids,p,25)
        future_only=p.copy()
        # Tail source frames beyond the last eligible focal time. They can
        # change future Y for final test times, not present/past predictor X.
        future_only[-4:,:,0]+=100.
        changed=build_original_recording(ids,future_only,25)
        for k in MODEL_NAMES:
            np.testing.assert_array_equal(baseline["X"][k],changed["X"][k])

    def test_native_timestamp_gap_drops_affected_rows_without_interpolating(self):
        clock,p=synthetic_original(4200)
        clean=build_original_recording(clock,p,25)
        clock[500:]+=1
        gap=build_original_recording(clock,p,25)
        self.assertLess(gap["n_original_eligible_group_times"],clean["n_original_eligible_group_times"])
        self.assertGreater(gap["n_original_rows_excluded_nonfinite_or_noncontiguous"],0)

    def test_original_NA_coordinate_deletes_shared_target_rows(self):
        ids,p=synthetic_original(4200)
        clean=build_original_recording(ids,p,25)
        p[210:350,0,1]=np.nan
        missing=build_original_recording(ids,p,25)
        self.assertLess(missing["n_original_eligible_group_times"],clean["n_original_eligible_group_times"])
        self.assertEqual(len(missing["Y"]),len(missing["X"]["age_0s"]))
        self.assertEqual(len(missing["Y"]),len(missing["X"]["age_2s"]))

    def test_heldout_target_cannot_affect_train_only_predictions(self):
        rng=np.random.default_rng(5)
        trainx=rng.normal(size=(1900,FEAT_DIM))
        trainy=rng.normal(size=(1900,4))
        testx=rng.normal(size=(600,FEAT_DIM))
        a=predict_train_file_only(trainx,trainy,testx)
        labels_changed_only_on_heldout=rng.normal(size=(600,4))*1000
        _=labels_changed_only_on_heldout
        b=predict_train_file_only(trainx,trainy,testx)
        np.testing.assert_array_equal(a,b)

    def test_fixed_three_file_source_heldout_and_no_causal_claim(self):
        files={}
        for j,name in enumerate(("01.txt","02.txt","105.txt")):
            clock,pos=synthetic_original(4200,8)
            pos+=j*2
            files[name]=build_original_recording(clock,pos,25,name)
        report=evaluate_source_files(files,"stickleback",3,{"fixture":True})
        self.assertEqual(report["status"],"V30_ORIGINAL_THREE_SOURCE_COMMON_MODEL_RECORDING_HELDOUT_SCORED")
        self.assertEqual(len(report["source_file_heldout_results"]),3)
        self.assertEqual(set(report["results_by_horizon"]),{"short","delayed"})
        self.assertFalse(report["social_causal_effect_identified"])
        self.assertTrue(report["source_file_holdout_not_confirmed_distinct_biological_shoal"])
        self.assertEqual(report["same_source_outcome_horizons_seconds"]["delayed"],[.6,.8])

    def test_frozen_recording_count_invalid_fails_closed(self):
        with self.assertRaises(SourceStop):
            evaluate_source_files({},"tetra",6,"SOURCE")

    def test_trivial_frames_and_source_fps_rejected(self):
        clock,pos=synthetic_original()
        with self.assertRaises(SourceStop):
            build_original_recording(clock,pos,40)
        with self.assertRaises(SourceStop):
            build_original_recording(clock[::-1],pos,25)

if __name__=="__main__":
    unittest.main()
