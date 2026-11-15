import unittest
from comparative_state.usgs_roost_csv_schema_v7e import choose_download
class PublisherLinkTest(unittest.TestCase):
 def test_trust_exact_provider_uri(self):
  d={'files':[{'name':'x.csv','downloadUri':'https://www.sciencebase.gov/catalog/file/get/abc/file.csv'}]}
  self.assertTrue(choose_download(d,'x.csv').endswith('/file.csv'))
 def test_host_blocked(self):
  with self.assertRaises(ValueError):choose_download({'files':[{'name':'x.csv','downloadUri':'https://example.com/private.csv'}]},'x.csv')
 def test_no_other_file_substitute(self):
  with self.assertRaises(ValueError):choose_download({'files':[{'name':'y.csv','downloadUri':'https://www.sciencebase.gov/catalog/file/get/abc'}]},'x.csv')
if __name__=='__main__': unittest.main()
