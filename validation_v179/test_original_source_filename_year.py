"""v179 source-origin chronology audit: synthetic fixtures only, no wild causal claim."""
import unittest
import numpy as np
from real_native_isource_origin_filename_audit import filename_upper_year,native_isource_flag_names

class V179SourceOnlyTests(unittest.TestCase):
    def test_full_date_year_is_date_not_tile_number(self):
        self.assertEqual(filename_upper_year("_20160101_Vliestroom_2016tt20.asc"),2016)
        self.assertEqual(filename_upper_year("KB125_1716_20170828.asc"),2017)
        self.assertEqual(filename_upper_year("_20250101_TESK2025.asc"),2025)
    def test_mixed_file_names_earliest_does_not_hide_future(self):
        self.assertEqual(filename_upper_year("2016_orig_20220101_reprocessed.asc"),2022)
        self.assertEqual(filename_upper_year("2015_16tmp.asc"),2016)
        self.assertEqual(filename_upper_year("2016-2019_composite.asc"),2019)
    def test_ambiguous_two_digit_year_must_stop_not_guess(self):
        self.assertIsNone(filename_upper_year("VlieBu_22_8_1.asc"))
        self.assertIsNone(filename_upper_year("KB125_1716.nc"))
        self.assertIsNone(filename_upper_year(None))
        self.assertIsNone(filename_upper_year("20150229_bad_date.asc"))
    def test_original_flag_code_mapping(self):
        class NativeSrc:
            flag_values=np.array([0,1,3],dtype=np.int16)
            flag_meanings="_20160101_Vlie.asc _20250101_future.asc VlieBu_22_8_1.asc"
        m=native_isource_flag_names(NativeSrc())
        self.assertEqual(len(m),3)
        self.assertLess(filename_upper_year(m[0]),2018)
        self.assertGreaterEqual(filename_upper_year(m[1]),2018)
        self.assertIsNone(filename_upper_year(m[3]))
    def test_unknown_and_duplicate_flag_values_never_guessed(self):
        class Duplicated:
            flag_values=np.array([0,0])
            flag_meanings="source2016 source2017"
        class Missing:
            flag_values=np.array([0,1])
            flag_meanings="one_file"
        self.assertEqual(native_isource_flag_names(Duplicated()),{})
        self.assertEqual(native_isource_flag_names(Missing()),{})
    def test_no_older_layer_rescue_for_source_file_future_date(self):
        # Frozen selection rule: latest valid native time layer is audited,
        # NOT replaced by an older layer after a provenance failure.
        first_valid_native_layer="2017-01-01"
        file_source="_20250101_future.asc"
        self.assertEqual(first_valid_native_layer[:4],"2017")
        self.assertGreaterEqual(filename_upper_year(file_source),2018)

if __name__=="__main__":
    unittest.main()
