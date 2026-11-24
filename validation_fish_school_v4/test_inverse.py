import unittest
import numpy as np
from inverse_identifiability import emission_ambiguity,centroid_ambiguity,attenuation,MICROPHONES,FISH
class InverseTests(unittest.TestCase):
 def test_acoustic_nullspace(self):
  a=emission_ambiguity()
  self.assertEqual((a["operator_rank"],a["null_dimension"]),(5,7))
  self.assertLess(a["max_receiver_difference"],1e-10)
  self.assertGreater(abs(a["total_emission_B"]-a["total_emission_A"]),.001)
 def test_different_centroids_identical_audio(self):
  a=centroid_ambiguity()
  self.assertAlmostEqual(a["centroid_displacement_m"],1.2,places=9)
  self.assertLess(a["max_receiver_difference"],1e-10)
  self.assertGreaterEqual(a["min_weight_B"],0.)
  self.assertLessEqual(a["max_weight_B"],1.)
 def test_overshift_stops(self):
  with self.assertRaises(ValueError):centroid_ambiguity(10.)
 def test_receiver_relabel_does_not_change_rank(self):
  a=attenuation(MICROPHONES,FISH);b=attenuation(MICROPHONES[[4,2,0,3,1]],FISH)
  self.assertEqual(np.linalg.matrix_rank(a),np.linalg.matrix_rank(b))
 def test_invalid_spread(self):
  with self.assertRaises(ValueError):attenuation(MICROPHONES,FISH,0)
if __name__=="__main__":unittest.main()
