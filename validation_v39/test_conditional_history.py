"""Synthetic known truth: no actual oystercatcher coordinates/observations."""
import datetime as dt
import json
import math
import unittest
import numpy as np
import conditional_history as v

DAY=dt.datetime(2010,4,1,0,0)
COORD=(53.468937,6.202908)
def invented_tide(start=DAY, n_days=45):
    begin=start-dt.timedelta(hours=4)
    n=int(n_days*24*6+30)
    return {begin+dt.timedelta(minutes=10*i):
       .55*math.sin(i/7.) for i in range(n)}
def invented_fixes(bird="originally-fictional-bird"):
    return [(bird,DAY+dt.timedelta(minutes=x),COORD[0]+x*.000005,COORD[1]+x*.000002)
           for x in (0,10,20,30)]
class KnownTruth(unittest.TestCase):
 def test_original_embargo_and_time_forward_fixed_support(self):
    self.assertEqual(v.EMBARGO_DAYS,7)
    self.assertEqual(v.TRAINING_MIN_EPISODES,5000)
    self.assertEqual(v.TRAINING_MIN_BIRDS,10)
    self.assertEqual(v.TEST_YEARS,(2010,2011,2012,2013,2014))
    self.assertEqual(v.month_train_cutoff(dt.datetime(2010,1,1)),
                     np.datetime64("2009-12-25T00:00:00","us"))
 def test_no_shared_original_fix_between_lag_and_future(self):
    self.assertEqual(v.four_original_fix_indices(2),(0,1,2,3))
    for i in range(2,15):
        a,b,c,d=v.four_original_fix_indices(i)
        self.assertTrue(b<c)
        self.assertEqual(len({a,b,c,d}),4)
    with self.assertRaises(ValueError):v.four_original_fix_indices(1)
 def test_disjoint_four_point_episode_is_admitted_and_target_end_after_start(self):
    points=invented_fixes()
    a,reason=v.episode_eligibility(points,2,[True]*4,invented_tide())
    self.assertIsNone(reason)
    self.assertLess(a[0],a[1])
    self.assertEqual(a[2].shape,(len(v.ENV_FIELDS),))
    self.assertGreater(a[-1],0)
 def test_bad_previous_or_future_and_geography_rejected(self):
    points=invented_fixes()
    a,reason=v.episode_eligibility(points,2,[True,True,False,True],invented_tide())
    self.assertIsNone(a)
    self.assertEqual(reason,"outside_fixed_25km_gauge")
    changed=list(points)
    changed[1]=(changed[1][0],changed[1][1]+dt.timedelta(minutes=60),*changed[1][2:])
    _,reason=v.episode_eligibility(changed,2,[True]*4,invented_tide())
    self.assertIn("previous",reason)
 def test_original_future_duration_not_among_baseline_features(self):
    self.assertEqual(len(v.ENV_FIELDS),23)
    self.assertTrue(all("future" not in s and "next" not in s for s in v.ENV_FIELDS))
    self.assertEqual(v.ADDITIONAL_FIELDS[0],"prior_DISJOINT_same_bird_log1p_horizontal_speed")
 def test_three_hour_tide_is_prior_deterministic_source(self):
    astro=invented_tide()
    h=v.tide_features(DAY+dt.timedelta(minutes=20),astro)
    self.assertEqual(len(h),4)
    self.assertTrue(all(math.isfinite(x) for x in h))
    self.assertNotEqual(h[0],h[2])
 def test_v38_nonlinear_tidal_baseline_expressible(self):
    a=v.current_feature_vector(DAY,*COORD,(-.1,-.5),10,10)
    b=v.current_feature_vector(DAY,*COORD,(+.9,-.5),10,10)
    self.assertGreater(a[8],0.)
    self.assertLess(b[8],0.)
 def test_same_month_test_outcomes_do_not_enter_training(self):
    n=130
    d={"X":np.ones((n,5)),
       "y":np.linspace(0,1,n),
       "start":np.array([np.datetime64("2009-12-01","us")+np.timedelta64(i,"D") for i in range(n)]),
       "end":np.array([np.datetime64("2009-12-01","us")+np.timedelta64(i,"D")+np.timedelta64(15,"m") for i in range(n)]),
       "bird":np.array([i%11 for i in range(n)]),
       "model_indices":{m:np.array([0,1]) for m in v.MODELS}}
    orig=v.chronological_fit_predict
    globals0=(v.TRAINING_MIN_EPISODES,v.TRAINING_MIN_BIRDS)
    try:
       v.TRAINING_MIN_EPISODES=10
       e1,_,_=orig(d)
       d["y"]=d["y"].copy()
       # Change a future month outcome; it must not affect preceding test score.
       d["y"][-1]=1e6
       e2,_,_=orig(d)
       same=np.isfinite(e1[:100]).all(axis=1)
       self.assertTrue(np.allclose(e1[:100][same],e2[:100][same]))
    finally:v.TRAINING_MIN_EPISODES,v.TRAINING_MIN_BIRDS=globals0
 def test_ridge_fixed_nonpenalized_intercept(self):
    g=np.diag([3.,3.,3.])
    y=np.array([6.,3.,1.])
    a=v.frozen_ridge(g,y,np.array([0,1]),alpha=25.)
    self.assertAlmostEqual(a[0],2.)
    self.assertLess(a[1],1.)
 def test_no_original_source_support_no_scored_MSE(self):
    d={"start":np.array([np.datetime64("2011-01-01","us")]),
       "bird":np.array([0])}
    e=np.array([[1.,.8,1.2,.9]])
    r=v.summarize(d,e,[],{})
    self.assertEqual(r["status"],"NOT_ADMITTED_ORIGINAL_TIDAL_PAST_SPEED_HELDOUT_SUPPORT")
    self.assertFalse(r["any_model_scores_reported"])
    self.assertNotIn("absolute_equal_bird_MSE_E0_E1_E2_E3",r)
 def test_exact_registered_four_same_cohort_comparisons(self):
    self.assertEqual(len(v.MODELS),4)
    self.assertEqual(v.CONTRASTS[0],("PRIMARY_E0_minus_E1",0,1))
    self.assertEqual(len(v.CONTRASTS),4)
    self.assertEqual(v.BOOT_SEED,20261031)
 def test_source_code_is_no_eBird_no_model_label_leak(self):
    import inspect
    s=inspect.getsource(v.episode_eligibility)
    self.assertNotIn("eBird",s)
    self.assertNotIn("target_future_interval_as_input",s)
if __name__=="__main__":unittest.main()
