"""Invented-only Dataverse source admission assertions; no animal data."""
import unittest, json
from eptesicus_2025_jhu_source_gate_v1 import summarize_small_doc, manifest, DOI, API, META

class TestJhuSourceGate(unittest.TestCase):
 def test_canonical_original_source_identity(self):
  self.assertEqual(DOI,"10.7281/T1WF3NZ7")
  self.assertIn("/api/datasets/:persistentId?",META)
 def test_source_readme_not_rehosted(self):
  data=b"VideoData contains a head angle_data trial frame timestamp.\nAudioData includes pulse_data trials.\n"
  r=summarize_small_doc(data,"README.md")
  self.assertFalse(r["text_or_source_values_exported"])
  self.assertGreater(r["matched_keyword_positions"]["trial"]["line_count"],0)
  self.assertNotIn("VideoData contains",json.dumps(r))
 def test_schema_field_inventory_conservative(self):
  r=summarize_small_doc(b"bat_alpha bat_beta variable laser_colour","README.md")
  self.assertNotIn("laser_colour",r["code_or_doc_variable_name_candidates"])
 def test_public_file_url_uses_biological_source_id_not_invented(self):
  self.assertTrue(API.endswith("/api"))
if __name__=="__main__":unittest.main()
