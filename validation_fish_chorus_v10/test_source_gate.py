import unittest
from source_gate import first_row,filename,get_num,embedded,SourceStop
class DryadFixtures(unittest.TestCase):
 def test_original_header(self):
  self.assertEqual(first_row(b"Depth,Sv_mean,NASC,datetime\n10,-80,1,2020\n"),
   ["Depth","Sv_mean","NASC","datetime"])
 def test_utf8_bom(self):
  self.assertEqual(first_row(b"\xef\xbb\xbfSite,timestamp_utc,UF440_SPL_no20iso_noday\n"),
     ["Site","timestamp_utc","UF440_SPL_no20iso_noday"])
 def test_dryad_filename_fields(self):
  self.assertEqual(filename({"path":"a/b/South_T_master_dryad.csv"}),"South_T_master_dryad.csv")
 def test_version_embedded(self):
  self.assertEqual(len(embedded({"_embedded":{"stash:versions":[{"id":99}]}},"version")),1)
 def test_missing_source_stop(self):
  with self.assertRaises(SourceStop):embedded({"_embedded":{}},"file")
if __name__=="__main__":unittest.main()
