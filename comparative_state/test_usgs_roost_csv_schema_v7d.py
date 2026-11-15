from comparative_state.usgs_roost_csv_schema_v7d import SRC,allowed_uri,file_url,header_only
import unittest
class SourceHeader(unittest.TestCase):
 def test_only_source_files(self):
  for itemid,name,_,_ in SRC.values(): self.assertTrue(allowed_uri(file_url(itemid,name)))
  self.assertFalse(allowed_uri('https://example.com/catalog/file/get/a'))
 def test_header_will_not_parse_body(self):
  b=b'ID,Date,ROOST,Night\n123,2022-01-01,foo,bar\n'
  self.assertEqual(header_only(b),['ID','Date','ROOST','Night'])
 def test_non_csv_rejected(self):
  with self.assertRaises(ValueError):header_only(b'PK\x03\x04not csv')
if __name__=='__main__':unittest.main()
