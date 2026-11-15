"""Technical source-convention tests; not bat neural/performance evidence."""
import unittest
import numpy as np
from hase_TF_convention_crosswalk_v1 import signal,corr,make_curve,run,FAMILIES,GRID_KHZ
class TestPublishedSourceContrast(unittest.TestCase):
 def test_same_pulse_correlation_unity(self):
  for p in FAMILIES:
   a=signal(90,45,p)
   self.assertAlmostEqual(corr(a,a),1,places=10)
 def test_equal_energy(self):
  for p in FAMILIES:
   a=signal(90,45,p)
   self.assertAlmostEqual(float(np.linalg.norm(a)),1,places=12)
 def test_fixed_start_keeps_Fs(self):
  a=make_curve("fixed_start_2018_like","linear")
  self.assertTrue(all(x["source_synthetic_Fs_khz"]==90 for x in a["points"]))
  self.assertEqual(a["points"][-1]["source_synthetic_TF_khz"],51)
 def test_fixed_bandwidth_keeps_B(self):
  a=make_curve("fixed_bandwidth_2026_like","linear")
  self.assertTrue(all(abs(x["source_synthetic_Fs_khz"]-x["source_synthetic_TF_khz"]-40)<1e-12 for x in a["points"]))
 def test_pre_declared_grid_and_shape_families(self):
  self.assertEqual(len(GRID_KHZ),12)
  self.assertEqual(set(FAMILIES),{"linear","power_0p6","power_2p0"})
 def test_no_extra_research_outputs_or_biological_claim(self):
  d=run()
  self.assertFalse(d["raw_2018_Dryad_audio_opened"])
  self.assertFalse(d["new_animal_measurements"])
  self.assertFalse(d["original_2026_author_waveform_reproduced"])
  self.assertEqual(len(d["curves"]),6)
 def test_bounded_0_to_1(self):
  for x in run()["curves"]:
   for r in x["points"]:
    self.assertGreaterEqual(r["normalized_max_lag_cross_correlation"],0)
    self.assertLessEqual(r["normalized_max_lag_cross_correlation"],1+1e-8)
 def test_dissimilarity_near_zero_perturbation_is_identity(self):
  for x in run()["curves"]:
   self.assertAlmostEqual(x["points"][0]["normalized_max_lag_cross_correlation"],1,places=10)
if __name__=="__main__":unittest.main()
