"""Synthetic only, direct interaction identifiability and 3D counterexample."""
import json
import math
import unittest
import numpy as np
import counterexample as m

class SyntheticKnownTruth(unittest.TestCase):
 def test_reference_v37_exact_original_sha(self):
  x=m.assert_original_v37_code()
  self.assertTrue(x["source_protocol_unchanged"])
  self.assertEqual(x["reference_v37_Git_blob_SHA"],m.V37_GIT_BLOB_SHA)
 def test_same_fixed_24_seeds_30_toy_agents_and_three_signs(self):
  self.assertEqual(tuple(m.SEEDS),tuple(range(24)))
  self.assertEqual(m.N_AGENTS,30)
  self.assertEqual(m.MOTIF_KEYS,("high_minus_low","low_ebb_minus_flood","high_ebb_minus_flood"))
 def test_source_free_direct_positive_speeds(self):
  h=np.array([-1.,0.,.5,1.2])
  d=np.array([-1.,1.,-1.,1.])
  x=m.direct_speed_at_tide(h,d,m.MODELS[1])
  self.assertTrue(np.isfinite(x).all())
  self.assertTrue((x>0).all())
 def test_additive_phase_difference_same_at_low_and_high_heights(self):
  for h in (-.8,1.):
   ebb=float(m.direct_speed_at_tide(h,-1,m.MODELS[0]))
   flood=float(m.direct_speed_at_tide(h,1,m.MODELS[0]))
   self.assertAlmostEqual(ebb-flood,2*m.BETA)
 def test_direct_interaction_has_opposite_phase_signs_without_state(self):
  for h in (-.8,0.):
   ebb=float(m.direct_speed_at_tide(h,-1,m.MODELS[1]))
   flood=float(m.direct_speed_at_tide(h,1,m.MODELS[1]))
   self.assertGreater(ebb-flood,0.)
  for h in (.8,1.):
   ebb=float(m.direct_speed_at_tide(h,-1,m.MODELS[1]))
   flood=float(m.direct_speed_at_tide(h,1,m.MODELS[1]))
   self.assertLess(ebb-flood,0.)
 def test_direct_model_does_not_refer_to_resource_state_machine(self):
  import inspect
  source=inspect.getsource(m.one_3d_step)
  self.assertNotIn("state_policy",source)
  self.assertNotIn("finish_transits",source)
  self.assertNotIn("ROOST",source)
 def test_crossing_threshold_interaction_flips_at_half_meter(self):
  a=m.direct_speed_at_tide(m.HEIGHT_THRESHOLD,-1,m.MODELS[1])
  b=m.direct_speed_at_tide(m.HEIGHT_THRESHOLD,1,m.MODELS[1])
  self.assertAlmostEqual(float(a),float(b))
 def test_phase_shift_wrong_clock_is_deliberate_half_cycle(self):
  self.assertAlmostEqual(m.HALF_CYCLE_HOURS,6.2103)
  h,dh=m.old.tide_height_slope(2.)
  hshift,dhshift=m.old.tide_height_slope(2.+m.HALF_CYCLE_HOURS)
  self.assertNotAlmostEqual(float(h),float(hshift))
  self.assertGreater(float(dh*dhshift),-10.)
 def test_3d_heading_only_social_motor_changes_orientation(self):
  p=np.array([[0.,0.,.01],[.1,.01,.02],[2.,2.,.01]])
  h=m.old.normalize3(np.array([[1.,0.,.1],[0.,1.,.1],[-1.,0.,.1]]))
  a,_=m.old.heading_update(h,p,np.random.default_rng(1),social=False)
  b,n=m.old.heading_update(h,p,np.random.default_rng(1),social=True)
  self.assertEqual(a.shape,(3,3))
  self.assertGreater(n,0.)
  self.assertFalse(np.allclose(a,b))
 def test_one_3d_step_emits_only_horizontal_observation_and_correct_shape(self):
  rng=np.random.default_rng(4)
  p=rng.uniform(0,m.old.WORLD_BOX_KM,size=(m.N_AGENTS,3))
  h=m.old.normalize3(rng.normal(size=(m.N_AGENTS,3)))
  pnew,hnew,response,neighbors=m.one_3d_step(m.MODELS[1],p,h,rng,1.5)
  self.assertEqual(pnew.shape,(m.N_AGENTS,3))
  self.assertEqual(hnew.shape,(m.N_AGENTS,3))
  self.assertEqual(response.shape,(m.N_AGENTS,))
  self.assertTrue(np.isfinite(response).all())
  self.assertEqual(neighbors,0.)
 def test_sensitivity_fixed_18_combinations(self):
  self.assertEqual(m.PARAM_GRID_COUNT,18)
  self.assertEqual(m.ALPHAS,(.20,.48,.80))
  self.assertEqual(m.BETAS,(.06,.12,.20))
  self.assertEqual(m.WIDTHS,(.15,.30))
 def test_identical_instantaneous_tide_state_vs_no_state_difference(self):
  x=m.source_free_history_intervention()
  self.assertEqual(x["memoryless_direct_both_histories_speed_km_h"][0],
                   x["memoryless_direct_both_histories_speed_km_h"][1])
  self.assertEqual(x["stateful_v37_ROOST_vs_FORAGE_speed_km_h"],[.09,1.1])
 def test_unregistered_variants_and_invalid_params_fail(self):
  with self.assertRaisesRegex(ValueError,"Unexpected"):
   m.direct_speed_at_tide(.0,.1,"nonexistent")
  with self.assertRaisesRegex(ValueError,"Unregistered"):
   m.trajectory_one_seed(m.MODELS[1],500)
  with self.assertRaisesRegex(ValueError,"parameter"):
   m.direct_speed_at_tide(.0,.1,m.MODELS[1],width=0)
 def test_replay_full_three_sign_metric_from_v37(self):
  h=np.repeat(np.array([-.75,-.25,.25,.75]),40)
  slope=np.tile(np.array([-1.,1.]),80)
  vals=np.full((len(h),m.N_AGENTS),.5)
  vals[slope<0]+=.1
  scores,_=m.old.signed_bin_effects(h,slope,vals)
  self.assertGreater(scores["low_ebb_minus_flood"],0.)
  self.assertGreater(scores["high_ebb_minus_flood"],0.)
  self.assertAlmostEqual(scores["low_minus_high_phase_difference"],0.)
if __name__=="__main__":unittest.main()
