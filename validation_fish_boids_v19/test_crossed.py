import unittest
import numpy as np
from validation_fish_boids_v15 import simulation as orig
from validation_fish_boids_v19 import crossed_simulation as sim
from validation_fish_boids_v19.score_crossed import SEEDS,ARMS,SCALES,N,scene,acoustic_weights,callcounts,report

class OriginalSourceChecks(unittest.TestCase):
 def test_seed_range_and_crossed_matrix(self):
  self.assertEqual((len(SEEDS),SEEDS[0],SEEDS[-1]),(768,6000,6767))
  self.assertEqual(len(ARMS),8)
 def test_geometry_preserves_components(self):
  s=sim.initialize(3,N)
  a=scene(s,.65);b=scene(s,1.35)
  self.assertTrue(np.array_equal(a.velocity,b.velocity))
  self.assertTrue(np.array_equal(a.calling,b.calling))
  self.assertEqual(a.rng_state,b.rng_state)
  np.testing.assert_allclose(a.pos.mean(0),b.pos.mean(0),atol=1e-12,rtol=0)
 def test_same_acoustic_initial_weights_on_crossed_physical(self):
  s=sim.initialize(4,N)
  a=scene(s,.65);b=scene(s,1.35)
  np.testing.assert_allclose(acoustic_weights(a,1.),acoustic_weights(b,.65/1.35),atol=1e-13,rtol=0)
 def test_default_diagonal_matches_original_state_and_traces(self):
  s=sim.initialize(5,N)
  src=orig.State(s.pos,s.velocity,s.calling,s.completed_steps,s.rng_state)
  for cue in (None,10):
   a=sim.advance(s,40,pulse_start=cue,acoustic_ratio=1.)
   b=orig.advance(src,40,pulse_start=cue)
   for key in ("call_fraction","hull_area","cue"):
    np.testing.assert_array_equal(a[key],b[key])
   for key in ("pos","velocity","calling"):
    np.testing.assert_array_equal(getattr(a["final_state"],key),getattr(b["final_state"],key))
   self.assertEqual(a["final_state"].rng_state,b["final_state"].rng_state)
 def test_new_ratio_changes_signal_in_predicted_direction(self):
  s=sim.initialize(6,N)
  compact=acoustic_weights(s,.65/1.35)
  spread=acoustic_weights(s,1.35/.65)
  self.assertTrue(np.all(compact>=spread))
 def test_invalid_audio_ratio_raises(self):
  with self.assertRaises(ValueError):sim.advance(sim.initialize(1,N),2,acoustic_ratio=0.)
 def test_integer_grid(self):
  c=np.zeros(3040,dtype=float);c[40]=.013
  with self.assertRaises(RuntimeError):callcounts(c)
 def test_missing_low_support_stops(self):
  original={seed:1. for seed in SEEDS}
  out=report(original,[])
  self.assertEqual(out["support_gate"],"LOW_ELIGIBLE_N_STOP")
if __name__=="__main__":unittest.main()
