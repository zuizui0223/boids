import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import usgs_source_identity_crosswalk_v8d as m
class KnownMetadata(unittest.TestCase):
 def test_date_format_used_2023(self):
  self.assertEqual(m.parsed_time('12/04/2020 14:07'),('2020-12-04T14:07','us_minutes'))
 def test_date_iso(self):
  self.assertEqual(m.parsed_time('2020-12-04 14:07:01'),('2020-12-04T14:07','iso_seconds'))
 def test_no_timezone_repair(self):
  self.assertIn('provided_offset_no_zone_conversion',m.parsed_time('2020-12-04T14:07:01+0900')[1])
 def test_reject_forged_provider_host(self):
  with self.assertRaisesRegex(ValueError,'unapproved'):m.get('https://bad.example/dataset.csv',100)
if __name__=='__main__':unittest.main()
