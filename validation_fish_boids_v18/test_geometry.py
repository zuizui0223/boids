"""Pre-outcome simulator-only v18 geometry falsification fixtures."""
import unittest
import numpy as np
from validation_fish_boids_v15 import simulation as sim
from validation_fish_boids_v18.geometry_intervention import (
  SEEDS,SCALES,ARMS,N,SPLIT,scale_geometry,_counts_fraction,aggregate
)
class GeometryFixtures(unittest.TestCase):
 def state(self):
  return sim.initialize(13,N)
 def test_frozen_census_and_ten_arms(self):
  self.assertEqual((len(SEEDS),SEEDS[0],SEEDS[-1]),(768,5000,5767))
  self.assertEqual(len(ARMS),10)
  self.assertEqual(list(SCALES.values()),[.65,1.,1.35])
 def test_identity_scale_is_byte_identical_for_positions(self):
  p=self.state()
  x=scale_geometry(p,1.)
  np.testing.assert_array_equal(x.pos,p.pos)
  np.testing.assert_array_equal(x.calling,p.calling)
  np.testing.assert_array_equal(x.velocity,p.velocity)
  self.assertEqual(x.rng_state,p.rng_state)
 def test_compact_and_spread_not_mutating_source(self):
  p=self.state();orig=p.pos.copy();v=p.velocity.copy()
  a=scale_geometry(p,.65);b=scale_geometry(p,1.35)
  np.testing.assert_array_equal(p.pos,orig)
  np.testing.assert_array_equal(a.velocity,v)
  np.testing.assert_array_equal(b.calling,p.calling)
  self.assertLess(np.linalg.norm(a.pos.mean(0)-p.pos.mean(0)),1e-12)
  self.assertGreater(np.linalg.norm(b.pos[0]-b.pos[1]),np.linalg.norm(a.pos[0]-a.pos[1]))
 def test_invalid_scale(self):
  with self.assertRaises(ValueError):scale_geometry(self.state(),.7)
 def test_integer_counts_grid_stop(self):
  a=np.zeros(3040);a[30]=.013
  with self.assertRaises(ValueError):_counts_fraction(a,3040)
 def test_null_eligible_support(self):
  census={seed:1. for seed in SEEDS}
  result=aggregate(census,[])
  self.assertEqual(result["primary_gate"],"STOP_INSUFFICIENT_ELIGIBLE_SEEDS")
  self.assertEqual(result["eligible_pre_cue_low"],0)
 def test_short_native_branch_replays_frozen_simulator(self):
  start=sim.initialize(23,N)
  none=sim.advance(start,2)
  a=scale_geometry(none["final_state"],1.)
  n0=sim.advance(a,8)
  n1=sim.advance(none["final_state"],8)
  np.testing.assert_array_equal(n0["call_fraction"],n1["call_fraction"])
if __name__=="__main__":unittest.main()
