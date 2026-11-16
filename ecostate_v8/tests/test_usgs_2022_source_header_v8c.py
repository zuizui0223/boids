import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import usgs_2022_source_header_v8c as m
class SourceOnly(unittest.TestCase):
 def test_verbatim_file(self):
  self.assertEqual(m.PUBLISHED_BYTES,30403945)
  self.assertTrue(m.NAME.endswith('_MNDWI.csv'))
 def test_no_nonpublisher_url(self):
  with self.assertRaisesRegex(ValueError,'unapproved'):
   m.request_bytes('https://example.org/not_original.csv',200)
 def test_checksum_shape(self):
  self.assertEqual(len(m.PUBLISHED_MD5),32)
if __name__=='__main__':unittest.main()
