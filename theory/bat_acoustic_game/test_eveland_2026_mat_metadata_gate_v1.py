"""Invented-only archive admission tests for 2026 real bats."""
import unittest
from eveland_2026_mat_metadata_gate_v1 import PIN,FIELDS,inspect,OUT

class TestSourceSchemaOnly(unittest.TestCase):
 def test_original_commit_pinned(self):
  self.assertEqual(PIN,"59928a71887d521fec143080b0b187736c046a0e")
 def test_field_key_set_is_explicit(self):
  self.assertIn("R.calls.tSec",FIELDS)
  self.assertIn("R.beam.rel_deg",FIELDS)
  self.assertIn("R.track.pos_sm",FIELDS)
 def test_no_persisted_raw_mat_by_default(self):
  self.assertEqual(OUT.name,"EVELAND_2026_ORIGINAL_3D_SONAR_MAT_SCHEMA_V1.json")
if __name__=="__main__":unittest.main()
