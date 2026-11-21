import csv,hashlib,os,tempfile,unittest
from pathlib import Path
from trajectory_source_gate import row_structure,permitted_file_link,RECORDINGS
class TrialGateTests(unittest.TestCase):
 def test_all_six_source_names(self):
  self.assertEqual(len(RECORDINGS),6)
  self.assertEqual(len(set(RECORDINGS)),6)
 def test_official_links_only(self):
  self.assertTrue(permitted_file_link("https://zenodo.org/api/records/10890112/files/8.csv/content"))
  self.assertFalse(permitted_file_link("https://not-zenodo.org/api/records/10890112/files/8.csv/content"))
  self.assertFalse(permitted_file_link("https://zenodo.org/api/records/999/files/8.csv/content"))
 def test_numeric_headerless_csv(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.csv";p.write_text("2.0,1.0,3.0,4.0\n5.0,2.0,4.0,3.0\n")
   x=row_structure(p);self.assertEqual(x["columns"],4);self.assertFalse(x["has_header"])
 def test_string_header_csv(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"x.csv";p.write_text("frame,id,x,y\n1,2,3.0,4.0\n")
   self.assertEqual(row_structure(p)["header_columns"],["frame","id","x","y"])
if __name__=="__main__":unittest.main()
