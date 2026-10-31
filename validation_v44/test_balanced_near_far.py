"""Invented aligned masks, whole-bird matched index and stop/contrast tests."""
import datetime as dt
import json
import unittest
import numpy as np
import balanced_near_far as m
class KnownTruth(unittest.TestCase):
 def test_frozen_both_observed_radii_and_support(self):
    self.assertEqual(m.prior.NEAR_RADIUS_KM,.2)
    self.assertEqual(m.prior.FAR_RADIUS_MIN_KM,1.)
    self.assertEqual(m.MIN_BIRDS,15)
    self.assertEqual(m.MIN_ORIGINAL_FUTURE_STEPS,25000)
    self.assertEqual(m.MIN_YEARS,2)
    self.assertEqual(m.MIN_CALENDAR_MONTHS,8)
 def test_primary_is_matched_near_gain_minus_far_gain(self):
    self.assertEqual(m.CONTRASTS[0],(
        "PRIMARY_NEAR_GAIN_MINUS_FAR_GAIN_MATCHED_BOTH",2,1))
    ma=np.array([[3.,2.,2.5,1.8],[1.,.8,.9,.7]])
    draws=np.zeros((10000,2),dtype=int)
    a=m.signed_score(ma,draws)
    self.assertAlmostEqual(a[m.PRIMARY]["equal_bird_mean_MSE_gain"],.3)
    self.assertEqual(a[m.PRIMARY]["positive_original_birds"],2)
 def test_balanced_source_only_strict_intersection(self):
    n=50
    y=np.zeros((n,4))
    pinned={"bird":np.arange(n)%10,
       "start":np.array([np.datetime64("2010-01-01","us")+
                np.timedelta64(i,"D") for i in range(n)])}
    near=np.zeros(n,bool);far=np.zeros(n,bool)
    near[:35]=True;far[20:]=True
    eligible,ids,months,years,support=m.target_indices(pinned,y,near,far)
    self.assertEqual(support["both_near_200m_and_far_1km_available_before_bird_gate"],15)
    self.assertEqual(len(eligible),0)
    self.assertEqual(len(ids),0)
 def test_temporary_no_far_observed_never_exports_social_score(self):
    n=12
    p={"bird":np.array([i%3 for i in range(n)]),
      "start":np.array([np.datetime64("2010-01-01","us")]*n)}
    e=np.zeros((n,4));a=np.full((n,4),np.nan)
    r=m.matched_cohort_score(p,e,a,np.ones(n,bool),np.zeros(n,bool))
    self.assertEqual(r["status"],"NOT_ADMITTED_BALANCED_NEAR_FAR_ORIGINAL_HELDOUT_SUPPORT")
    self.assertFalse(r["any_directional_MSE_or_angular_effect_exported"])
    self.assertNotIn("MSE_S0",json.dumps(r))
 def test_no_future_target_scope_expansion(self):
    self.assertEqual(m.MODELS,m.prior.MODELS)
    self.assertEqual(m.prior.vec.RIDGE_ALPHA,25.)
    self.assertEqual(m.BOOTS,10000)
    self.assertEqual(m.SEED,20261031)
 def test_exact_1980s_local_source_cant_be_relabelled_new_field(self):
    self.assertIn("Zenodo 10053970",m.run.__code__.co_consts.__str__())
    self.assertTrue(m.ORIGINAL_V43_EXPECTED_NEAR_CANDIDATES==171041)
 def test_pairwise_bird_bootstrap_not_observation_pseudoreplication(self):
    a=np.array([[3.,2.,2.2,1.9],[1.,1.1,.9,.8]])
    bootstrap=np.array([[0,1],[0,0],[1,1]]*3334)[:10000]
    effect=m.signed_score(a,bootstrap)
    self.assertAlmostEqual(effect[m.PRIMARY]["equal_bird_mean_MSE_gain"],0.0)
 def test_complete_old_result_is_required(self):
    self.assertEqual(m.V43_RECEIPT.name,"original_near_bird_heading_forecast_v43.json")
    import inspect
    s=inspect.getsource(m.replay_previous_original_before_balanced_scoring)
    self.assertIn("old original v43",s.lower())
    self.assertIn("original_gate.nested_close",s)
 def test_exact_both_available_month_and_year(self):
    N=60;p={"bird":np.repeat(np.arange(3),20),
      "start":np.array([np.datetime64("2010-01-01","us")+
              np.timedelta64(i%20,"D") for i in range(N)])}
    mat=np.ones((N,4))
    near=np.ones(N,bool);far=np.ones(N,bool)
    _,_,_,_,support=m.target_indices(p,mat,near,far)
    self.assertEqual(support["both_near_200m_and_far_1km_available_before_bird_gate"],60)
    self.assertEqual(support["whole_birds_with_30plus_BOTH_observed_heldout_steps"],0)
 def test_exact_intercept_and_not_using_target_as_feature(self):
    import inspect
    s=inspect.getsource(m.run)
    self.assertNotIn("future_angle_as_predictor",s)
    self.assertIn("prior_model_coefficients_and_full_training_cohort_UNCHANGED",s)
if __name__=="__main__":unittest.main()
