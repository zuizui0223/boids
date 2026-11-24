"""v28 synthetic/no-animal known-truth fixtures for target-free residual correlation."""
from __future__ import annotations
import unittest
import numpy as np
from validation_fish_school_v28 import conditional_residual as m


def fake(seed=1,n=1300):
    rng=np.random.default_rng(seed)
    g=rng.normal(size=(n,6))
    common=rng.normal(size=(n,2))
    current=g[:,:2]*2+common
    old2=g[:,:2]+.75*common+.2*rng.normal(size=(n,2))
    old1=g[:,:2]+.2*common+.6*rng.normal(size=(n,2))
    return {"geometry":g,"age_0s":current,"age_0.2s":old2,"age_1s":old1}


class ResidualizedSourceTests(unittest.TestCase):
    def test_frozen_panels_replay_same_G(self):
        p=fake()
        g=p["geometry"]
        models={"geometry":g}
        for t in m.AGES:models[f"age_{t:g}s"]=np.concatenate((g,p[f"age_{t:g}s"]),axis=1)
        out=m.source_panels(models)
        self.assertEqual(set(out),{"geometry","age_0s","age_0.2s","age_1s"})
        self.assertEqual(out["age_0s"].shape,(1300,2))
        np.testing.assert_array_equal(out["age_0s"],p["age_0s"])

    def test_wrong_original_geometry_fails(self):
        p=fake()
        g=p["geometry"]
        models={"geometry":g}
        for t in m.AGES:models[f"age_{t:g}s"]=np.concatenate((g,p[f"age_{t:g}s"]),axis=1)
        models["age_1s"]=models["age_1s"].copy()
        models["age_1s"][0,0]+=3
        with self.assertRaises(m.SourceStop):
            m.source_panels(models)

    def test_out_of_file_train_only_residual_correlation(self):
        cases={i:fake(i+1) for i in range(6)}
        out=m.assess(cases,"tetra",{"original":False})
        self.assertEqual(out["status"],"V28_ORIGINAL_TARGET_FREE_HELDOUT_CONDITIONAL_RESIDUAL_CORRELATION")
        self.assertEqual(len(out["recording_scores"]),6)
        q0=out["equal_recording_mean_conditional_residual_correlation"]
        self.assertGreater(q0["age_0.2s"],q0["age_1s"])
        self.assertFalse(out["original_fish_future_target_scores_computed"])
        self.assertFalse(out["source_fish_coordinates_redistributed"])

    def test_zero_residual_covariance_stops(self):
        with self.assertRaises(m.SourceStop):
            m.partial_vec_correlation(np.ones((1200,2)),np.ones((1200,2)))

    def test_incomplete_original_source_count_stops(self):
        with self.assertRaises(m.SourceStop):
            m.assess({0:fake()},"ayu",{})

    def test_future_temporal_shift_not_forced_to_positive(self):
        x=np.zeros((1300,2))
        y=np.arange(1300)/100
        x[:,0]=np.sin(y);x[:,1]=np.cos(y)
        self.assertGreater(m.partial_vec_correlation(x,x),.99)
        self.assertLess(m.partial_vec_correlation(x,-x),-.99)

if __name__=="__main__":unittest.main()
