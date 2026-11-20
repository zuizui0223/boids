import unittest
import numpy as np
from acoustic_feedback import meanfield,microscopic,P0,fixed_points
class AcousticTests(unittest.TestCase):
 def test_low_single_state(self):
    r=meanfield(2.,1.)
    self.assertEqual(len(r["equilibria"]),1)
    self.assertAlmostEqual(r["equilibria"][0],P0,places=7)
    self.assertAlmostEqual(r["last_call_probability"],P0,delta=.0001)
 def test_high_two_stable_states_plus_one_unstable(self):
    r=meanfield(4.,2.)
    self.assertEqual(len(r["equilibria"]),3)
    self.assertLess(r["equilibria"][0],.1)
    self.assertAlmostEqual(r["equilibria"][1],.5,places=6)
    self.assertGreater(r["equilibria"][-1],.9)
    self.assertGreater(r["last_call_probability"],.9)
 def test_unstimulated_high_gain_remains_low(self):
    r=meanfield(4.,2.,pulse=False)
    self.assertAlmostEqual(r["last_call_probability"],P0,places=8)
 def test_micro_sound_zero_motor_has_identical_trajectory(self):
    x=np.array([v["hull_area"] for v in microscopic(seed=2,playback=True,audio_weight=0,heard_weight=0)])
    y=np.array([v["hull_area"] for v in microscopic(seed=2,playback=False,audio_weight=0,heard_weight=0)])
    np.testing.assert_array_equal(x,y)
 def test_micro_has_positive_area_and_bounded_call_rate(self):
    z=microscopic(seed=3,steps=90)
    self.assertTrue(all(0<=v["call_fraction"]<=1 for v in z))
    self.assertTrue(all(v["hull_area"]>0 for v in z))
if __name__=="__main__":unittest.main()
