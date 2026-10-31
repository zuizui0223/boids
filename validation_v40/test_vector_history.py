"""Invented original GPS/tide known-truth only, not source movement opened."""
import datetime as dt
import json
import math
import unittest

import numpy as np
import vector_history as m

class PureSourceFreeKnownTruth(unittest.TestCase):
 def test_spherical_geodesic_east_north_and_zero_distance(self):
    e,n,d,s,c=m.spherical_east_north(53.,6.,53.,6.)
    self.assertEqual((e,n,d,s,c),(0.,0.,0.,0.,0.))
    e,n,d,s,c=m.spherical_east_north(53.,6.,53.,6.1)
    self.assertGreater(e,0.)
    # The initial great-circle bearing along a latitude circle has a small\n    # north component, even if the two endpoints have identical latitude.\n    self.assertLess(abs(n),d*.001)
    self.assertAlmostEqual(e,d,places=5)
    e,n,d,s,c=m.spherical_east_north(53.,6.,53.1,6.)
    self.assertGreater(n,0.)
    self.assertAlmostEqual(e,0.,places=5)
    self.assertAlmostEqual(n,d,places=5)
 def test_preserve_four_distinct_original_fixes_and_source_horizon(self):
    self.assertEqual(m.last.four_original_fix_indices(2),(0,1,2,3))
    self.assertEqual(m.last.MIN_FUTURE_PAIR_MIN,5)
    self.assertEqual(m.last.MAX_FUTURE_PAIR_MIN,30)
    self.assertEqual(m.last.EMBARGO_DAYS,7)
 def test_vector_asinh_and_sinh_roundtrip(self):
    v=np.array([-10.,0.,20.])
    self.assertTrue(np.allclose(np.sinh(np.arcsinh(v)),v))
 def test_angle_loss_zero_for_parallel_true_prediction(self):
    y=np.arcsinh(np.array([[2.,0.],[0.,-3.]]))
    loss=m.angular_loss(y,y,np.array([.1,.1]))
    self.assertTrue(np.allclose(loss,0,atol=1e-12))
 def test_angle_loss_2_for_opposite_and_neutral_for_small_pred_speed(self):
    truth=np.arcsinh(np.array([[1.,0.],[1.,0.]]))
    pred=np.arcsinh(np.array([[-1.,0.],[.001,0.]]))
    a=m.angular_loss(truth,pred,np.array([.2,.2]))
    self.assertAlmostEqual(a[0],2.)
    self.assertAlmostEqual(a[1],1.)
 def test_stationary_or_short_future_step_excluded_angular_only(self):
    truth=np.arcsinh(np.array([[1.,0.],[1.,0.]]))
    a=m.angular_loss(truth,truth,np.array([0.,.049]))
    self.assertTrue(np.isnan(a).all())
 def test_prescribed_four_models_and_prior_heading_beyond_prior_speed(self):
    self.assertEqual(len(m.MODELS),4)
    self.assertEqual(m.CONTRASTS[0],("PRIMARY_V0_minus_V1",0,1))
    self.assertEqual(m.NUM_VECTORS,2)
    self.assertEqual(m.RIDGE_ALPHA,25)
    self.assertEqual(m.ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM,.05)
 def test_four_models_same_original_source_features(self):
    n=2;cols=m.last.ENV_FIELDS
    f=len(cols)+3+3
    X=np.ones((n,f))
    d={"X":X,"model_indices":{
      m.last.MODELS[1]:np.array(list(range(len(cols)+3))+[len(cols)+3]),
      m.last.MODELS[3]:np.arange(f)}}
    x,idx=m.model_matrix(d,np.array([[0.,1.],[1.,0.]]))
    self.assertEqual(x.shape,(2,f+2))
    self.assertEqual(len(idx[m.MODELS[1]]),len(idx[m.MODELS[0]])+2)
    self.assertTrue(np.array_equal(idx[m.MODELS[2]],np.arange(f)))
    self.assertFalse(np.any(idx[m.MODELS[0]]==f))
 def test_multioutput_ridge_keeps_intercept_unpenalized(self):
    g=np.diag([2.,2.])
    xy=np.array([[4.,6.],[1.,2.]])
    beta=m.fit_multiple(g,xy,np.array([0,1]))
    self.assertEqual(beta.shape,(2,2))
    self.assertTrue(np.allclose(beta[0],[2.,3.]))
    self.assertLess(beta[1,0],1.)
 def test_unadmitted_support_emits_no_metric(self):
    d={"start":np.array([np.datetime64("2011-01-01","us")]),"bird":np.array([0])}
    er=np.array([[1.,.8,.9,.7]])
    an=np.array([[float("nan")]*4])
    r=m.evaluate_equal_birds(d,er,an,[],{})
    self.assertEqual(r["status"],"NOT_ADMITTED_SOURCE_ORIGINAL_VECTOR_FORECAST_COHORT")
    self.assertFalse(r["any_vector_or_angular_model_scores_reported"])
 def test_heldout_month_training_does_not_leak_future_vector_response(self):
    # Deliberately forced tiny source-support only for this pure toy fixture.
    n=160
    t0=np.datetime64("2009-12-01","us")
    starts=t0+np.arange(n)*np.timedelta64(1,"D")
    ends=starts+np.timedelta64(10,"m")
    X=np.column_stack([np.ones(n),np.linspace(0,1,n)])
    Y=np.column_stack([np.sin(np.arange(n)),np.cos(np.arange(n))])
    d={"start":starts,"end":ends,"bird":np.arange(n)%12}
    ix={name:np.array([0,1]) for name in m.MODELS}
    orig=(m.last.TRAINING_MIN_EPISODES,m.last.TRAINING_MIN_BIRDS)
    try:
        m.last.TRAINING_MIN_EPISODES=10
        e1,_,f1,_=m.chronological_vector_forecast(d,X,Y,np.full(n,.2),ix)
        changed=Y.copy()
        changed[-1]=[1000000.,1000000.]
        e2,_,f2,_=m.chronological_vector_forecast(d,X,changed,np.full(n,.2),ix)
        early=starts<np.datetime64("2010-02-01","us")
        finite=np.isfinite(e1[:,0])&early
        self.assertTrue(np.any(finite))
        self.assertTrue(np.allclose(e1[finite],e2[finite]))
        self.assertEqual(f1,f2)
    finally:m.last.TRAINING_MIN_EPISODES,m.last.TRAINING_MIN_BIRDS=orig
 def test_original_v39_Schiermonnikoog_source_and_time_unchanged(self):
    self.assertEqual(m.tide.STATION,"schiermonnikoog.waddenzee")
    self.assertEqual(m.source.RECORD,10053970)
    self.assertEqual(len(m.source.PINS),7)
    self.assertEqual(m.last.MIN_GAP_MIN,5)
    self.assertEqual(m.last.MAX_GAP_MIN,360)
 def test_no_original_animal_or_GPS_export_in_code_contract(self):
    import inspect
    s=inspect.getsource(m.main)
    self.assertIn("V40_COMPLETE_AGGREGATE_JSON",s)
    self.assertNotIn("np.savetxt",inspect.getsource(m))
if __name__=="__main__":unittest.main()
