"""v22 offline known-truth fixtures. No original fish trajectories fetched."""
import sys,unittest,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_school_v5"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v9"))
sys.path.insert(0,str(ROOT/"validation_fish_school_v22"))
from forecast_transfer import make_trial,SourceStop
from ayu_source_gate import blobsha
from comparison import relative_other_mean,locked_panels,paired_bootstrap,make_source_panels,MODELS
from ayu import ayu_one
from tetra import tetra_one

class SourceIndependentChecks(unittest.TestCase):
    def test_other_group_rejects_own_past_replacement(self):
        now=np.array([[[1.,0.],[2.,0.],[3.,0.]]])
        past=np.array([[[4.,0.],[5.,0.],[6.,0.]]])
        cur=relative_other_mean(now,now)
        stale=relative_other_mean(past,now)
        np.testing.assert_allclose(cur[:,:,0],[[1.5,0.,-1.5]])
        np.testing.assert_allclose(stale[:,:,0],[[4.5,3.,1.5]])
        self.assertFalse(np.array_equal(stale,relative_other_mean(past,past)))

    def test_constant_other_school_cannot_fake_stale_advantage(self):
        arr=np.array([[[1.,2.],[3.,4.],[5.,6.]]])
        self.assertTrue(np.array_equal(relative_other_mean(arr,arr),
                                       relative_other_mean(arr.copy(),arr)))

    def test_source_panels_exact_same_original_global(self):
        geom=np.array([[1.,3.],[2.,4.]])
        true=np.array([[1.,0.],[0.,1.]])
        current=np.concatenate((geom,true),axis=1)
        p=locked_panels(geom,current,true,true+1)
        self.assertEqual(set(p),set(MODELS))
        np.testing.assert_array_equal(p["current"],current)
        np.testing.assert_array_equal(p["stale2s"][:,:2],geom)
        self.assertEqual(p["magnitude"].shape,(2,3))

    def test_original_global_replay_must_fail_on_modified_coefficients(self):
        g=np.ones((2,3))
        current=np.hstack((g,np.zeros((2,2))))
        with self.assertRaises(SourceStop):
            locked_panels(g,current,np.ones((2,2)),np.ones((2,2)))

    def test_whole_recording_bootstrap_not_framewise(self):
        r=paired_bootstrap(np.array([1.,-1.,2.]),np.ones(3),seed=12,n_reps=50)
        self.assertEqual(r["positive_recordings"],2)
        self.assertEqual(r["negative_recordings"],1)
        self.assertEqual(len(r["recording_differences_MSE"]),3)
        with self.assertRaises(SourceStop):
            paired_bootstrap(np.array([1.]),np.array([1.]))

    def test_unequal_target_rows_fails_before_model(self):
        good={m:np.ones((1100,2)) for m in MODELS}
        bad={m:np.ones((1100,2)) for m in MODELS}
        bad["current"]=np.ones((1000,2))
        with self.assertRaises(SourceStop):
            make_source_panels({"short":good,"delayed":bad},
                               {"short":np.ones((1100,2)),"delayed":np.ones((1100,2))},
                               {"sha":"x"},{"pins":True})

    def test_ayu_original_feature_exact_subset_and_lag(self):
        n=6200
        d=np.zeros((n,22))
        frames=np.arange(n)
        d[:,0]=frames+1
        d[:,1]=np.round(frames/30,2)
        for j in range(10):
            d[:,2+j]=10+2*j + .02*frames + .5*np.sin(frames/20+j)
            d[:,12+j]=20+3*j + .01*frames + .4*np.cos(frames/25+j)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"synthetic_ayu.txt"
            np.savetxt(path,d,fmt="%.8f")
            b=path.read_bytes()
            a=ayu_one(path,blobsha(b),len(b))
        self.assertEqual(len(a["Y"]["short"]),len(a["Y"]["delayed"]))
        self.assertTrue(a["source_checks"]["no_future_state_in_predictor"])
        self.assertEqual(a["source_checks"]["first_eligible_source_frame"],66)
        self.assertGreater(len(a["Y"]["short"]),1000)

    def test_tetra_original_feature_and_delayed_subset(self):
        n=40200
        f=np.arange(n,dtype=float)
        p=np.zeros((n,8,2),float)
        t=np.arange(n)
        for i in range(8):
            p[:,i,0]=15+i*5+.001*t+.3*np.sin(t/25+i)
            p[:,i,1]=30+i*4+.002*t+.2*np.cos(t/35+i)
        old=make_trial(f,p,0)
        result=tetra_one(f,p,old,"synthetic_sha_not_original")
        self.assertEqual(result["X"]["short"]["current"].shape[0],len(old["Y"]))
        self.assertEqual(result["X"]["delayed"]["stale2s"].shape[0],len(result["Y"]["delayed"]))
        self.assertLess(len(result["Y"]["delayed"]),len(result["Y"]["short"]))
        self.assertTrue(result["source_checks"]["no_future_trajectory_inputs"])

if __name__=="__main__":unittest.main()
