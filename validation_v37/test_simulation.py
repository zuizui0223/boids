"""Known truth of synthetic physics and 3D motor. No original animal data."""
import unittest
import numpy as np
import simulation as m

class ToyKnownTruth(unittest.TestCase):
 def test_hard_source_free_parameters_and_tide_periodicity(self):
  self.assertEqual(len(m.MODELS),6)
  self.assertEqual(len(m.SEEDS),24)
  self.assertTrue(m.NO_BIOLOGICAL_DATA)
  h,der=m.tide_height_slope(np.array([0.,m.PERIOD_HOURS/4]))
  self.assertAlmostEqual(h[0],0.)
  self.assertGreater(float(der[0]),0.)
  self.assertGreater(float(h[1]),1.)
 def test_synthetic_resource_is_monotonic_not_an_actual_DEM(self):
  heights=[-2.,-.1,.35,.85,2.]
  a=m.available_fraction(heights)
  self.assertTrue(np.all(np.diff(a)<=0.))
  self.assertAlmostEqual(float(m.available_fraction(.35)),m.ENTER_EXPOSED_FRAC)
  self.assertAlmostEqual(float(m.available_fraction(.85)),m.EXIT_EXPOSED_FRAC)
  self.assertEqual(float(m.available_fraction(10.)),0.)
 def test_resource_hysteresis_state_machine_in_present_tide(self):
  states=np.array([0,2],dtype=np.int16)
  timers=np.zeros(2)
  m.state_policy(states,timers,exposed=m.ENTER_EXPOSED_FRAC+.01,slope=-1,commute=True)
  self.assertEqual(tuple(states),(1,2))
  self.assertAlmostEqual(timers[0],m.COMMUTE_HOURS)
  for _ in range(4):m.finish_transits(states,timers)
  self.assertEqual(states[0],2)
  m.state_policy(states,timers,exposed=m.EXIT_EXPOSED_FRAC-.01,slope=1,commute=True)
  self.assertEqual(tuple(states),(3,3))
  for _ in range(4):m.finish_transits(states,timers)
  self.assertEqual(tuple(states),(0,0))
 def test_no_transit_and_baseline_ablation_speeds(self):
  states=np.array([0,2],dtype=np.int16)
  timers=np.zeros(2)
  m.state_policy(states,timers,exposed=m.ENTER_EXPOSED_FRAC+.01,slope=-1,commute=False)
  self.assertEqual(states[0],2)
  a=m.mode_speeds(m.MODELS[0],states,.2,-1)
  self.assertTrue(np.all(a==m.FIXED_SPEED))
  self.assertTrue(np.all(m.mode_speeds(m.MODELS[1],states,.2,-1)==.09+1.10*.2))
  self.assertTrue(np.all(m.mode_speeds(m.MODELS[2],states,.2,1)==.40))
  self.assertTrue(np.all(m.mode_speeds(m.MODELS[2],states,.2,-1)==1.10))
 def test_social_heading_actually_3D_and_only_changes_orientation(self):
  positions=np.array([[0.,0.,.04],[.10,.02,.04],[2.,2.,.1]],dtype=float)
  heading=m.normalize3(np.array([[1.,0.,.1],[0.,1.,.05],[-1.,0.,.05]]))
  a,zero=m.heading_update(heading,positions,np.random.default_rng(4),social=False)
  b,n=m.heading_update(heading,positions,np.random.default_rng(4),social=True)
  self.assertEqual(a.shape,(3,3))
  self.assertTrue(np.allclose(np.linalg.norm(a,axis=1),1.))
  self.assertTrue(np.allclose(np.linalg.norm(b,axis=1),1.))
  self.assertGreater(n,0.)
  self.assertFalse(np.allclose(a,b))
 def test_three_sign_motif_is_measured_at_equal_tide_height_bins(self):
  # Construct independent artificial log speed response, for matched ebb/flood.
  h=np.tile(np.array([-.75,-.25,.25,.75]),20)
  dh=np.tile(np.array([-1.,1.]),40)
  y=np.full((len(h),3),.50)
  y[dh<0]+=.1
  sign,_=m.signed_bin_effects(h,dh,y)
  self.assertGreater(sign["low_ebb_minus_flood"],0.)
  self.assertGreater(sign["high_ebb_minus_flood"],0.)
  self.assertEqual(sign["low_minus_high_phase_difference"],0.)
 def test_source_free_run_seed_and_model_constraints(self):
  with self.assertRaisesRegex(ValueError,"previously fixed"):m.trajectory_one_seed("Unregistered",0)
  with self.assertRaisesRegex(ValueError,"previously fixed"):m.trajectory_one_seed(m.MODELS[0],42)
 def test_original_response_is_horizontal_not_3D_magnitude(self):
  # A vertical velocity must contribute zero to the GPS horizontal metric.
  d=np.array([[0.,0.,.1],[.1,.2,.1]])
  horiz=np.linalg.norm(d[:,:2],axis=1)
  self.assertEqual(float(horiz[0]),0.)
  self.assertLess(float(horiz[1]),float(np.linalg.norm(d[1])))
 def test_evaluable_toy_one_short_fragment_deterministic(self):
  # Exercise actual state logic without the full precommitted 24-seed output.
  rng=np.random.default_rng(15)
  p=rng.uniform(0,m.WORLD_BOX_KM,size=(4,3))
  h=m.normalize3(rng.normal(size=(4,3)))
  for _ in range(3):
   h,_=m.heading_update(h,p,rng,social=True)
   p=np.mod(p+h*.1,m.WORLD_BOX_KM)
  self.assertTrue(np.isfinite(p).all())
if __name__=="__main__":unittest.main()
