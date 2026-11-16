import unittest
from zenodo_archive_inventory import RECORD,MAXSIZE,MD5,source
class TestSource(unittest.TestCase):
 def test_source_id(self):self.assertEqual(RECORD,6319709)
 def test_md5(self):self.assertEqual(len(MD5),32)
 def test_maxsize(self):self.assertLessEqual(MAXSIZE,30_000_000)
 def test_no_http(self):
  with self.assertRaises(ValueError):source('http://zenodo.org/test',40)
 def test_no_untrusted(self):
  with self.assertRaises(ValueError):source('https://test.example.org/test',40)
if __name__=='__main__':unittest.main()
