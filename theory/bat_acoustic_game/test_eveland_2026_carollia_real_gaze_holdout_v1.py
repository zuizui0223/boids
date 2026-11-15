"""Invented HDF5 refs, kinematics and bat-level CV fixtures: no actual bats."""
import math,tempfile,unittest
from pathlib import Path
import numpy as np
import h5py

from eveland_2026_carollia_real_gaze_holdout_v1 import (
 HORIZONS,BEAM_FIT_R_MIN,LAMBDA_RIDGE,GEOM_FEATURES,
 read_source_trial,trial_rows,wrap_pi,planar_heading,weighted_ridge,predict,
 shift_sonar_within_trials,holdout,bootstrap_bat_differences
)

def make_fake_original(path):
    with h5py.File(path,"w") as h:
        root=h.create_group("RESULTS")
        for name in ("calls","beam","track"):
            group=h.create_group("_"+name+"_values")
            r=root.create_dataset(name,(1,1),dtype=h5py.ref_dtype)
            r[0,0]=group.ref
            if name=="calls":
                times=np.arange(.1,2.8,.055)
                content={"tSec":times.reshape(1,-1)}
            elif name=="beam":
                times=np.arange(.1,2.8,.055)
                content={"rel_deg":(20*np.sin(times)).reshape(1,-1),
                         "fitR":np.ones((1,len(times)))*.75}
            else:
                times=np.arange(0.,3.01,.01)
                content={"tSec":times.reshape(1,-1),
                         "pos_sm":np.stack([times,.10*times**2,.02*times],axis=0)}
            for key,value in content.items():
                d=h.create_dataset("_"+name+"_"+key,data=value)
                ref=group.create_dataset(key,(1,1),dtype=h5py.ref_dtype)
                ref[0,0]=d.ref

def fake_rows(n=7):
    a=[]
    for bat in range(n):
        for trial in range(2):
            for i in range(25):
                cue=(i%12-6)*.08
                g=np.array([1+bat*.01,0.,.2, .2,.9,0.,1.])
                a.append({"bat":"FAKE"+str(bat),"trial":"TRIAL"+str(bat)+"_"+str(trial),
                    "G":g,"S":cue,
                    "Y":.6*cue})
    return a

class TestRealBatCVMechanics(unittest.TestCase):
    def test_source_assumptions_frozen(self):
        self.assertEqual(HORIZONS,(.10,.20,.30))
        self.assertAlmostEqual(BEAM_FIT_R_MIN,.30)
        self.assertAlmostEqual(LAMBDA_RIDGE,.01)
        self.assertEqual(len(GEOM_FEATURES),7)
    def test_hdf5_matlab_v73_original_like_reference_reader(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invented.mat"
            make_fake_original(p)
            x=read_source_trial(p)
            self.assertEqual(x["track_pos"].shape[1],3)
            self.assertEqual(len(x["call_times"]),len(x["beam_deg"]))
            self.assertTrue(np.all(np.diff(x["track_times"])>0))
    def test_past_only_features_and_future_target_time(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invented.mat";make_fake_original(p)
            a=read_source_trial(p)
            for h in HORIZONS:
                rows,issues=trial_rows(a,h)
                self.assertGreater(len(rows),10)
                self.assertTrue(all(len(r["G"])==7 and np.isfinite(r["Y"]) for r in rows))
    def test_source_author_beam_fit_quality_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invented.mat";make_fake_original(p)
            a=read_source_trial(p);a["beam_fitR"][:]=.1
            rows,issues=trial_rows(a,.20)
            self.assertEqual(len(rows),0)
            self.assertGreater(issues["original_author_beam_fitR_below_0p30"],0)
    def test_trajectory_outside_time_is_rejected_without_extrapolation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invented.mat";make_fake_original(p)
            a=read_source_trial(p)
            with self.assertRaisesRegex(ValueError,"EXTRAPOLATION"):
                planar_heading(-1,a["track_times"],a["track_pos"])
    def test_angle_wrap(self):
        self.assertAlmostEqual(wrap_pi(np.pi+0.1),-np.pi+.1)
        self.assertAlmostEqual(wrap_pi(-np.pi-.1),np.pi-.1)
    def test_zero_source_motion_has_no_direction(self):
        tt=np.arange(0.,2,.01)
        xyz=np.zeros((len(tt),3))
        self.assertIsNone(planar_heading(1,tt,xyz))
    def test_ridge_no_data_from_heldout_bat(self):
        data=fake_rows()
        train=[v for v in data if v["bat"]!="FAKE6"]
        test=[v for v in data if v["bat"]=="FAKE6"]
        shift_sonar_within_trials(data)
        for features in ("G","GS","GShift"):
            fit=weighted_ridge(train,features)
            v=predict(test,fit,features)
            self.assertEqual(len(v),len(test))
            self.assertTrue(np.all(np.isfinite(v)))
    def test_source_bat_is_unit_not_calls(self):
        data=fake_rows()
        out=holdout(data)
        self.assertEqual(out["original_bat_independent_folds"],7)
        self.assertEqual(out["original_source_trials_scored"],14)
        self.assertEqual(out["original_source_calls_scored"],350)
        self.assertFalse(out["source_bat_IDs_and_individual_predictions_exported"])
        self.assertNotIn("FAKE",str(out))
    def test_informative_gaze_improves_heldout_fixture(self):
        o=holdout(fake_rows())
        self.assertLess(o["models"]["G2"]["equal_bat_mean_angular_MAE_deg"],
                        o["models"]["G1"]["equal_bat_mean_angular_MAE_deg"])
    def test_source_bat_support_stop_for_five(self):
        self.assertEqual(holdout(fake_rows(5))["status"],
                         "SOURCE_SUPPORT_STOP_FEWER_THAN_SIX_BATS")
    def test_bootstrap_bat_not_call(self):
        a=bootstrap_bat_differences([1.,-1.,.5,0.,1.])
        b=bootstrap_bat_differences([1.,-1.,.5,0.,1.])
        self.assertEqual(a,b)
        self.assertLessEqual(a[0],a[1])
if __name__=="__main__":unittest.main()
