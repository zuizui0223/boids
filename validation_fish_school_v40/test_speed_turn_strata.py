"""v40 known-truth source-independent speed/turn outcome-blind splits."""
import json,unittest
import numpy as np
from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v33.neighbor_panels import original_panels
from validation_fish_school_v40.source_speed_turn_strata import (
 source_trial_stratified_moments,stable_two_half_masks,pure_source_now_own_motion,
 MODELS,CATEGORIES
)
from validation_fish_school_v40.aggregate_speed_turn_original_shoals import (
 restored_source_file,summarize,REFERENCE_V33
)
from validation_fish_school_v40.author_group_speed_turn_shard import to_safe_json_moments

def fake_fish_data(n=4800):
    f=np.arange(n,dtype=float)
    p=np.zeros((n,8,2),dtype=float)
    for j in range(8):
        p[:,j,0]=10*j+.03*f+2*np.sin(f/(19+j*3))
        p[:,j,1]=7*j+.02*f+2*np.cos(f/(26+j*4))
    return f,p

class SpeedTurnNoFutureLeak(unittest.TestCase):
    def test_original_v33_source_full_and_two_half_moments(self):
        f,p=fake_fish_data()
        src=original_panels(f,p,"SYNTHETIC_ONLY")
        r=source_trial_stratified_moments(src)
        self.assertEqual(set(r["moments"]),set(CATEGORIES))
        self.assertEqual(set(r["moments"]["ALL"]),set(MODELS))
        self.assertEqual(r["n_speed_low_fish_frame_rows"]+r["n_speed_high_fish_frame_rows"],
                         r["n_original_focal_fish_frame_rows"])
        self.assertEqual(r["n_turn_low_fish_frame_rows"]+r["n_turn_high_fish_frame_rows"],
                         r["n_original_turn_well_defined_rows"])
        self.assertTrue(r["original_focal_velocity_future_Y_or_XY_NOT_exported"])

    def test_source_sample_moment_json_sorted_key_roundtrip(self):
        f,p=fake_fish_data()
        source=source_trial_stratified_moments(original_panels(f,p))
        recorded={
           "stratum_source_moment_sufficient_statistics_only":json.loads(
                json.dumps(to_safe_json_moments(source["moments"]),sort_keys=True))
        }
        out=restored_source_file(recorded)
        self.assertEqual(out["ALL"]["NEAR_TRUE"]["n"],source["n_original_focal_fish_frame_rows"])
        self.assertEqual(out["speed_low"]["GLOBAL"]["sxy"].shape,(16,4))

    def test_own_velocity_speed_is_original_G_not_future_Y(self):
        f,p=fake_fish_data()
        x=original_panels(f,p)["X"]["G_geometry"]
        speed,turn,ok=pure_source_now_own_motion(x)
        np.testing.assert_allclose(speed,x[:,8])
        self.assertEqual(len(turn),len(x))
        self.assertTrue(ok.any())

    def test_stable_rank_half_split_with_ties_is_exact_and_no_drop(self):
        v=np.array([1.,1.,1.,3.,3.,3.,5.])
        low,high=stable_two_half_masks(np.tile(v,500),np.ones(3500,dtype=bool))
        self.assertEqual(low.sum(),1750)
        self.assertEqual(high.sum(),1750)
        self.assertFalse(np.any(low & high))

    def test_original_no_prev_heading_turn_rows_marked_invalid(self):
        g=np.zeros((3000,14),dtype=float)
        g[:,2]=1
        g[:,4]=0
        v,turn,defined=pure_source_now_own_motion(g)
        self.assertFalse(defined.any())
        with self.assertRaises(SourceStop):
            stable_two_half_masks(turn,defined)

    def test_future_coordinate_change_outside_frozen_source_cohort_does_not_change_present_own_kinematics(self):
        f,p=fake_fish_data()
        base=original_panels(f,p)
        speed,turn,ok=pure_source_now_own_motion(base["X"]["G_geometry"])
        p[-4:,:,0]+=10000
        after=original_panels(f,p)
        s2,t2,o2=pure_source_now_own_motion(after["X"]["G_geometry"])
        np.testing.assert_array_equal(speed,s2)
        np.testing.assert_array_equal(turn,t2)
        np.testing.assert_array_equal(ok,o2)

    def test_hypothetical_source_groups_matched_v33_baseline_and_opposite_turn_direction(self):
        folds=[]
        for i in range(1,13):
            ms={}
            for cat in CATEGORIES:
                ms[cat]={}
                for model in MODELS:
                    ms[cat][model]={}
                    for h in ("short","delayed"):
                        if cat=="ALL":
                            mse=REFERENCE_V33[h][model]
                        elif cat.endswith("_low"):
                            mse={"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":90.,"NEAR_ROT1":99.}[model]
                        elif cat=="speed_high":
                            mse={"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":80.,"NEAR_ROT1":99.}[model]
                        else:
                            mse={"G_geometry":105.,"GLOBAL":100.,"NEAR_TRUE":97.,"NEAR_ROT1":99.}[model]
                        ms[cat][model][h]=mse
            folds.append({"original_test_group_ID":str(i),"source_category_MSE":ms})
        out=summarize(folds,{"synthetic":True})
        m=out["source_original_12_shoal_MODERATION_results"]["short"]["source_original_pairwise_SPEED_AND_TURN_MODERATIONS"]
        self.assertAlmostEqual(m["speed"]["local_beyond_GLOBAL"]["equal_12_original_shoal_mean_modulation_relative_GLOBAL_MSE"],.1)
        self.assertAlmostEqual(m["turn"]["local_beyond_GLOBAL"]["equal_12_original_shoal_mean_modulation_relative_GLOBAL_MSE"],-.07)
        self.assertEqual(m["speed"]["local_beyond_GLOBAL"]["positive_original_groups"],12)
        self.assertEqual(m["turn"]["local_beyond_GLOBAL"]["negative_original_groups"],12)

    def test_frozen_source_scientific_panels_do_not_change(self):
        self.assertEqual(MODELS,("G_geometry","GLOBAL","NEAR_TRUE","NEAR_ROT1"))
        self.assertEqual(CATEGORIES,("ALL","speed_low","speed_high","turn_low","turn_high"))
        self.assertNotIn("FAR_TRUE",MODELS)

if __name__=="__main__":unittest.main()
