import unittest
from social_force_rank import build_force_matrix,trial,experiment,TRUE_BETA
import numpy as np
class ForceRankTests(unittest.TestCase):
 def test_one_neighbor_fixed_distance_collinear(self):
  r=trial(20261027,1,'fixed')
  self.assertEqual(r['rank'],1)
  self.assertLess(r['heldout_mse'],0.05)
  self.assertGreater(r['beta_absolute_error'],.2)
 def test_three_neighbors_same_distance_still_degenerate(self):
  r=trial(20261027,3,'fixed')
  self.assertEqual(r['rank'],1)
 def test_one_neighbor_variable_distance_rank_recovered(self):
  r=trial(20261027,1,'variable')
  self.assertEqual(r['rank'],2)
  self.assertLess(r['beta_absolute_error'],.1)
 def test_multi_neighbors_variable_distance_full_rank(self):
  r=trial(20261027,3,'variable')
  self.assertEqual(r['rank'],2)
  self.assertLess(r['beta_absolute_error'],.1)
 def test_invalid_neighbors_fail_closed(self):
  with self.assertRaises(ValueError):
   build_force_matrix(rng=np.random.default_rng(1),n_states=5,n_neighbors=2,distance_regime='variable')
 def test_deterministic_replay(self):
  self.assertEqual(experiment(3),experiment(3))
if __name__=='__main__':unittest.main()
