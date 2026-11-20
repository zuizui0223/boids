import unittest
from ayu_source_gate import blobsha,structure,SourceStop,FILES
class TestAyuSource(unittest.TestCase):
 def test_known_sha(self):
    self.assertEqual(blobsha(b"abc"),"f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
 def test_seven_files_frozen(self):
    self.assertEqual(len(FILES),7)
    self.assertEqual(len(set(FILES)),7)
 def test_numeric_matrix_fixture(self):
    data=("1 2 3 4 5\n"*120).encode()
    out=structure(data)
    self.assertEqual(out["first20_field_count_min"],5)
    self.assertEqual(out["first_line_numeric_fraction"],1)
 def test_header_fixture(self):
    out=structure(("time,x,y,z\n"+"0,1,2,3\n"*120).encode())
    self.assertTrue(out["first_line_has_string_header"])
 def test_empty_source_stop(self):
    with self.assertRaises(SourceStop):structure(b"\n")
if __name__=="__main__":unittest.main()
