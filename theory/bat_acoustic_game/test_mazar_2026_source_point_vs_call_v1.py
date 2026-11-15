"""Invented echo-call membership only; no original bats or eLife MATLAB outputs."""
import unittest
from mazar_2026_source_point_vs_call_v1 import (
 invented_calls,analyze,run,RATIO,FAR,NEAR
)
class TestOriginalSourceEchoGranularity(unittest.TestCase):
 def test_ten_nonempty_source_calls(self):
  for s in (False,True):
   v=invented_calls(s)
   self.assertEqual(len(v),10)
   self.assertTrue(all(len(x)>0 for x in v))
   self.assertEqual(sum(len(x) for x in v),12)
 def test_fixed_same_echo_coordinates(self):
  a=invented_calls(False);b=invented_calls(True)
  self.assertEqual(sorted(x for y in a for x in y),sorted(x for y in b for x in y))
 def test_source_threshold_still_original_ratio(self):
  self.assertAlmostEqual(RATIO,.22)
  self.assertAlmostEqual(analyze(invented_calls(False))["threshold_min_real_valued_count"],2.2)
 def test_one_call_can_qualify_three_echo_points(self):
  v=analyze(invented_calls(False))
  self.assertEqual(v["source_accepted_cluster_count"],1)
  self.assertEqual(v["source_accepted_echo_point_clusters"][0]["source_helper_echo_point_count"],3)
  self.assertEqual(v["source_accepted_echo_point_clusters"][0]["distinct_source_calls_contributing"],1)
  self.assertEqual(v["not_source_distinct_call_accepted_count"],0)
 def test_three_calls_and_same_points_qualify(self):
  v=analyze(invented_calls(True))
  self.assertEqual(v["source_accepted_cluster_count"],1)
  self.assertEqual(v["source_accepted_echo_point_clusters"][0]["distinct_source_calls_contributing"],3)
  self.assertEqual(v["not_source_distinct_call_accepted_count"],1)
 def test_source_centroid_identical(self):
  a=analyze(invented_calls(False))
  b=analyze(invented_calls(True))
  self.assertEqual(a["source_accepted_echo_point_clusters"][0]["centroid_xy"],b["source_accepted_echo_point_clusters"][0]["centroid_xy"])
 def test_no_bat_or_original_published_model_result(self):
  z=run()
  self.assertFalse(z["new_animal_measurements"])
  self.assertTrue(z["not_a_full_source_MATLAB_simulation"])
  self.assertTrue(z["original_main_cluster_function_missing_in_both_archives"])
  self.assertTrue(z["source_CaveExit_Confusion_experiment_ObsRepeationsFlag_is_zero"])
if __name__=="__main__":unittest.main()
