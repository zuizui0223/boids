"""Invented-only architectural source gate invariants; no original author code in tests."""
import unittest,hashlib
from mazar_2026_source_architecture_gate_v1 import (
  gitblob,summarize_matlab,BLOBS,UPSTREAM_PIN,DEPENDENCIES
)
class TestCaveExitSourceProvenance(unittest.TestCase):
 def test_git_original_blob_hash_formula(self):
  self.assertEqual(gitblob(b"test\n"),"9daeafb9864cf43055ae93beb0afd6c7d144bfa4")
 def test_seven_pinned_sources(self):
  self.assertEqual(len(BLOBS),7)
  self.assertEqual(len(set(BLOBS.values())),7)
 def test_original_source_commit_fixed(self):
  self.assertEqual(UPSTREAM_PIN,"a74fb61a8efb57ca37693893c3bd7b35fa94fa89")
 def test_matlab_script_finds_memory_vs_immediate_control(self):
  s=b"function x=BatManueverDecision(y)\nObsMemorySize=5; ConfusionObs=true; DistToReactObstacle=0.5;\n"
  x=summarize_matlab(s)
  self.assertEqual(x["source_architecture_token_counts"]["ObsMemorySize"],1)
  self.assertEqual(x["source_architecture_token_counts"]["ConfusionObs"],1)
  self.assertFalse(x["full_matlab_original_model_executed"])
 def test_windows_file_path_flag(self):
  x=summarize_matlab(b"runPath = 'C:\\Users\\bat\\Desktop';\nuigetfile('*.xlsx');\n")
  self.assertTrue(x["runtime_portability_flags"]["absolute_Windows_drive"])
  self.assertTrue(x["runtime_portability_flags"]["interactive_source_dialog"])
 def test_reproducibility_requires_matlab_not_python_only(self):
  self.assertIn("matlab_table_data_type",DEPENDENCIES)
  self.assertIn("matlab_polyshape",DEPENDENCIES)
if __name__=="__main__":unittest.main()
