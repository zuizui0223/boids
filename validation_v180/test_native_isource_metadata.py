"""v180 pure synthetic metadata decoder controls."""
import unittest
import numpy as np
from probe_native_isource_metadata import numeric_codes,names_from_native_attribute,inspect_var_attributes
class Mock:
 def __init__(self,**k):self.d=k
 def ncattrs(self):return list(self.d)
 def getncattr(self,k):return self.d[k]
class Cases(unittest.TestCase):
 def test_valid_original_flag_vec(self):
  v=Mock(flag_values=np.array([0,2,3],dtype=np.float32), flag_meanings="_20160101_file.asc _20170101_file.asc _20250101_file.asc")
  self.assertTrue(inspect_var_attributes(v)["exact_unambiguous_code_filename_mapping_possible"])
 def test_count_mismatch_does_not_infer(self):
  v=Mock(flag_values=np.array([0,1]),flag_meanings="old.asc")
  self.assertFalse(inspect_var_attributes(v)["exact_unambiguous_code_filename_mapping_possible"])
 def test_no_flags_wont_pass(self):
  self.assertFalse(inspect_var_attributes(Mock(source="VAK VAK"))["exact_unambiguous_code_filename_mapping_possible"])
 def test_repeated_codes_dont_pass(self):
  self.assertIsNone(numeric_codes(np.array([1,1])))
 def test_native_vector_string_names(self):
  self.assertEqual(names_from_native_attribute(np.array(["a.asc","b.asc"])),["a.asc","b.asc"])
 def test_mapping_requires_known_code_count(self):
  v=Mock(flag_values=np.array([0,1]), flag_meanings=np.array(["a.asc","b.asc","c.asc"]))
  self.assertFalse(inspect_var_attributes(v)["exact_unambiguous_code_filename_mapping_possible"])
if __name__=="__main__":unittest.main()
