"""Known-truth checks; no reserved v17 seed inspected here."""
import unittest
import numpy as np
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v17.motor_feedback import (
  ARM_SPECS,SEEDS,WINDOW,BOOTSTRAP_REPS,
  fixed_window_call_delta,motor_interaction,_bootstrap,_counts
)

class MotorFeedbackTests(unittest.TestCase):
 def test_frozen_seed_and_arms(self):
  self.assertEqual((len(SEEDS),SEEDS[0],SEEDS[-1]),(384,4000,4383))
  self.assertEqual(len(ARM_SPECS),6)
  self.assertEqual(WINDOW,(1040,4040))
 def test_fixed_integer_delta(self):
  a=np.zeros(3040,dtype=float);b=a.copy()
  a[40:]=1./32
  k,v=fixed_window_call_delta(a,b)
  self.assertEqual(k,3000)
  self.assertEqual(v,1/32)
 def test_primary_interaction_algebra(self):
  zero=np.zeros(3040,dtype=float);one=zero.copy();one[40:]=1/32
  two=zero.copy();two[40:]=2/32
  arms={name:zero.copy() for name,*_ in ARM_SPECS}
  arms["motor5_hear3_pulse"]=two
  arms["motor0_hear3_pulse"]=one
  z=motor_interaction(arms)
  self.assertEqual(z["numerator_primary"],3000)
  self.assertEqual(z["primary_motor_feedback_interaction"],1/32)
 def test_biased_fraction_rejected(self):
  a=np.zeros(3040);a[50]=.12345
  with self.assertRaises(ValueError):
   _counts(a,3040)
 def test_constant_bootstrap(self):
  self.assertEqual(_bootstrap([.5,.5]),[.5,.5])
 def test_hearing_disabled_structurally_after_pulse(self):
  # Old/unreserved seed, same exact RNG and initial geometry.
  state=sim.initialize(9,32)
  c=sim.advance(state,85,pulse_start=None,heard_weight=0,audio_weight=5.)
  b=sim.advance(state,85,pulse_start=20,pulse_duration=40,heard_weight=0,audio_weight=5.)
  np.testing.assert_array_equal(c["call_fraction"][60:],b["call_fraction"][60:])
if __name__=="__main__":unittest.main()
