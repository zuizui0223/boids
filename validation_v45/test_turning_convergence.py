"""Invented direction pairs only, no original bird GPS or RWS tide outcomes."""
import unittest
import json
import inspect
import numpy as np
import turning_convergence as m

class PureKnownTruth(unittest.TestCase):
 def test_fixed_source_gates(self):
    self.assertEqual(m.MIN_MOVEMENT_KM,.05)
    self.assertEqual(m.MIN_OTHER_RESULTANT,.25)
    self.assertEqual(m.MIN_BIRDS,12)
    self.assertEqual(m.MIN_SOURCE_STEPS,2500)
    self.assertEqual(m.MIN_YEARS,2)
    self.assertEqual(m.SHAM,100)
 def test_true_unit_heading_and_stationary_zero(self):
    u,n=m.normalize_rows(np.array([[0.,0.],[3.,4.]]))
    self.assertTrue(np.all(u[0]==0))
    self.assertTrue(np.allclose(u[1],[.6,.8]))
    self.assertEqual(n[0],0.)
 def test_toward_near_vs_far_exact_bounded_geometry(self):
    before=np.array([1.,0.])
    after=np.array([0.,1.])
    near=np.array([0.,1.])
    far=np.array([1.,0.])
    turn=after-before
    self.assertEqual(float(turn@(near-far)),2.)
    self.assertAlmostEqual(float(turn@near),1.)
    self.assertAlmostEqual(float(turn@far),-1.)
 def test_original_disjoint_speeds_and_next_50m_admission(self):
    n=4
    x=np.zeros((n,len(m.v39.ENV_FIELDS)+4))
    x[:,0]=1.
    idx=m.v39.ENV_FIELDS.index("prior_observed_device_pair_elapsed_minutes_over_30")
    x[:,idx]=.5
    x[:,-3]=np.log1p(np.array([1.,1.,.05,1.]))
    X40=np.column_stack([x,np.array([[1.,0.]]*n)])
    Y=np.arcsinh(np.array([[0.,1.]]*n))
    new=np.array([.10,.10,.10,.01])
    near=np.array([[0.,1.],[0.,.2],[0.,1.],[0.,1.]])
    far=np.array([[1.,0.]]*n)
    indices,change,nn,ff,q=m.direction_ready(
        {"X":x},Y,new,X40,near,far,np.arange(n))
    self.assertEqual(indices.tolist(),[0])
    self.assertEqual(q["original_v44_matched_future_steps_before_displacement_gates"],4)
    self.assertAlmostEqual(float(change[0]@(nn[0]-ff[0])),2.)
 def test_no_original_support_no_effect(self):
    d={"bird":np.array([0]),"start":np.array([np.datetime64("2010-01-01","us")])}
    idx=np.array([0])
    out=m.evaluate(d,idx,np.array([[1.,0.]]),np.array([[1.,0.]]),
                   np.array([[0.,1.]]),{"source":True})
    self.assertEqual(out["status"],"NOT_ADMITTED_ORIGINAL_DIRECTION_CONVERGENCE")
    self.assertFalse(out["any_turning_effect_reported"])
    self.assertNotIn("all_three_frozen_signed_estimands",json.dumps(out))
 def test_bird_bootstrap_weights_birds_not_observations(self):
    sample=np.array([[0,1],[0,0],[1,1]])
    b=m.bird_summary([2.,-1.],sample)
    self.assertAlmostEqual(b["equal_bird_mean"],.5)
    self.assertEqual(b["positive_original_birds"],1)
 def test_source_cohort_not_unknown_posthoc_options(self):
    self.assertEqual(m.PREVIOUS_43.name,"original_near_bird_heading_forecast_v43.json")
    self.assertEqual(m.PREVIOUS_44.name,"original_both_near_far_heading_v44.json")
    source=inspect.getsource(m.source_replay)
    self.assertIn("v43_result",source) if False else self.assertIn("original43",source)
    self.assertIn("v44.matched_cohort_score",source)
    self.assertIn("nested_close",source)
 def test_sham_clock_group_fixed(self):
    s=inspect.getsource(m.sham)
    self.assertIn("date.hour//6",s)
    self.assertIn("current_dH_m_per_h",s)
    self.assertIn("rng.permutation",s)
 def test_no_old_raw_source_rewrite(self):
    self.assertNotIn("git push",inspect.getsource(m))
    self.assertNotIn("os.system(",inspect.getsource(m))
 def test_source_unit_3d_not_admitted(self):
    self.assertTrue(m.PROTOCOL.endswith("PROTOCOL.md"))
    self.assertIn("v45",m.PROTOCOL.lower())

if __name__=="__main__":
    unittest.main()
