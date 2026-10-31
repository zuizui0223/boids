"""Invented GPS points and model fixtures only, no original wild GPS opened."""
import datetime as dt
import json
import math
import unittest
import numpy as np
import near_heading as m

TIME=dt.datetime(2010,5,1,10,20)
LAT=m.gpsgeom.STATION_LAT
LON=m.gpsgeom.STATION_LON
class SyntheticKnownTruth(unittest.TestCase):
 def test_source_radii_and_timing_are_frozen(self):
  self.assertEqual(m.NEAR_RADIUS_KM,.2)
  self.assertEqual(m.FAR_RADIUS_MIN_KM,1.)
  self.assertEqual(m.AGE_MAX_MIN,5.)
  self.assertEqual(len(m.CONTEXT_NAMES),10)
  self.assertEqual(len(m.MODELS),4)
 def test_near_other_past_and_far_control_separate(self):
  focal=(TIME,0,LAT,LON,0)
  latest={
    1:(TIME-dt.timedelta(minutes=2),LAT+.0005,LON,1.,0.,.3),
    2:(TIME-dt.timedelta(minutes=1),LAT+.03,LON,0.,1.,.5),
    0:(TIME,LAT,LON,0.,-1.,3.)}
  ctx,n,f,ne,fa=m.source_neighbor_features(focal,latest)
  self.assertTrue(ne);self.assertTrue(fa)
  self.assertAlmostEqual(n[0],1.)
  self.assertAlmostEqual(f[1],1.)
  self.assertEqual(ctx[0],1.)
  self.assertEqual(ctx[7],1.)
  self.assertAlmostEqual(ctx[6],.3)
 def test_after_start_other_fix_rejected_even_if_co_located(self):
  focal=(TIME,0,LAT,LON,0)
  other={1:(TIME+dt.timedelta(seconds=1),LAT+.0001,LON,1.,0.,.2)}
  _,n,_,yes,_=m.source_neighbor_features(focal,other)
  self.assertFalse(yes);self.assertTrue(np.all(n==0.))
 def test_previous_other_fix_more_than_five_min_rejected(self):
  focal=(TIME,0,LAT,LON,0)
  other={1:(TIME-dt.timedelta(minutes=5,seconds=1),LAT+.0001,LON,1.,0.,.2)}
  _,n,_,yes,_=m.source_neighbor_features(focal,other)
  self.assertFalse(yes);self.assertTrue(np.all(n==0.))
 def test_near_zero_displacement_has_no_artificial_heading(self):
  focal=(TIME,0,LAT,LON,0)
  other={1:(TIME,LAT,LON,0.,0.,0.)}
  ctx,heading,_,yes,_=m.source_neighbor_features(focal,other)
  self.assertTrue(yes)
  self.assertTrue(np.allclose(heading,[0.,0.]))
  self.assertEqual(ctx[4],0.)
 def test_self_observation_never_counts_neighbor(self):
  focal=(TIME,0,LAT,LON,0)
  other={0:(TIME,LAT,LON,1.,0.,3.)}
  _,_,_,yes,_=m.source_neighbor_features(focal,other)
  self.assertFalse(yes)
 def test_same_test_rows_and_near_feature_added_after_private_history(self):
  n=5;X40=np.ones((n,70))
  cols={m.v40.MODELS[1]:np.array([0,1,2,64,68,69])}
  X,f=m.model_matrix(X40,cols,np.zeros((n,10)),np.zeros((n,2)),np.zeros((n,2)))
  self.assertEqual(X.shape,(n,84))
  self.assertEqual(len(f[m.v40.MODELS[0]]),16)
  self.assertEqual(len(f[m.v40.MODELS[1]]),18)
  self.assertEqual(len(f[m.v40.MODELS[2]]),18)
  self.assertEqual(len(f[m.v40.MODELS[3]]),20)
 def test_positive_sign_tail_and_far_gain_contrast_definition(self):
  self.assertEqual(m.CONTRASTS[0],("PRIMARY_S0_minus_S1_NEAR",0,1))
  self.assertEqual(m.CONTRASTS[-1],("descriptive_NEAR_GAIN_minus_FAR_GAIN",2,1))
  mat=np.array([[4.,3.,3.5,2.7],[3.,2.,3.1,1.9]])
  boot=np.zeros((10000,2),dtype=int)
  x=m.summary_contrasts(mat,[0,1],boot)
  self.assertGreater(x["PRIMARY_S0_minus_S1_NEAR"]["equal_bird_MSE_gain"],0)
  self.assertGreater(x["descriptive_NEAR_GAIN_minus_FAR_GAIN"]["equal_bird_MSE_gain"],0)
 def test_no_support_emits_no_social_scores(self):
  p={"start":np.array([np.datetime64("2010-01-01","us")]),"bird":np.array([0])}
  e=np.array([[2.,1.,2.2,1.2]])
  a=np.array([[float("nan")]*4])
  s=m.evaluate(p,e,a,np.array([True]),np.array([False]))
  self.assertEqual(s["status"],"NOT_ADMITTED_NEAR_BIRD_HEADING_HELDOUT_SUPPORT")
  self.assertNotIn("equal_bird_vector_MSE",json.dumps(s))
 def test_source_age_zero_is_already_observed_not_future(self):
  focal=(TIME,0,LAT,LON,0)
  x={1:(TIME,LAT+.0001,LON,0.,1.,.2)}
  _,_,_,yes,_=m.source_neighbor_features(focal,x)
  self.assertTrue(yes)
 def test_model_feature_source_contains_no_target_next_fix(self):
  import inspect
  text=inspect.getsource(m.source_neighbor_features)
  self.assertNotIn("target_future_fix",text)
  self.assertEqual(m.SIGNED_CONTRASTS if hasattr(m,"SIGNED_CONTRASTS") else m.CONTRASTS,m.CONTRASTS)
if __name__=="__main__": unittest.main()
