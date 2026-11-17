"""v181 native source filenames with spaces must not shift isource IDs."""
import unittest
import numpy as np
from strict_native_source_extension_filename_audit import parse_native_source_filenames,native_isource_flag_names,filename_upper_year

class NativeVariable:
    def __init__(self,code,names):
        self.flag_values=np.asarray(code,dtype=float)
        self.flag_meanings=names

class V181Synthetic(unittest.TestCase):
    def test_whole_names_including_internal_spaces(self):
        names="_20160101_Vliestroom_2016tt20.asc _20170101_KB 125_1716 done.asc _20250101_TESK2025.asc"
        got=parse_native_source_filenames(names)
        self.assertEqual(len(got),3)
        self.assertEqual(got[1],"_20170101_KB 125_1716 done.asc")
        self.assertEqual(native_isource_flag_names(NativeVariable([0,7,9],names))[7],got[1])
        self.assertLess(filename_upper_year(got[1]),2018)
        self.assertGreaterEqual(filename_upper_year(got[2]),2018)
    def test_no_realign_when_filename_has_unknown_extension(self):
        names="_20160101_a.asc _20170101_b.unknown"
        self.assertIsNone(parse_native_source_filenames(names))
        self.assertEqual(native_isource_flag_names(NativeVariable([0,1],names)),{})
    def test_no_realign_when_native_flag_count_differs(self):
        names="_20160101_a.asc _20170101_b.asc"
        self.assertEqual(native_isource_flag_names(NativeVariable([0],names)),{})
    def test_case_insensitive_extensions_and_gzip(self):
        names="_20160101_a.ASC _20170101_b.xyz.gz _20180101_c.csv"
        self.assertEqual(len(parse_native_source_filenames(names)),3)
    def test_blank_unknowns_stop(self):
        self.assertIsNone(parse_native_source_filenames(""))
        self.assertIsNone(parse_native_source_filenames("_20160101_bad"))
        self.assertEqual(native_isource_flag_names(NativeVariable([0,0],"_20160101_a.asc _20170101_b.asc")),{})
    def test_raw_date_parser_unverified_survey_day(self):
        self.assertEqual(filename_upper_year("_20160101_Vliestroom_2016tt20.asc"),2016)
        self.assertEqual(filename_upper_year("_20150101_Wadden_2015_16tmp.asc"),2016)
if __name__=="__main__":unittest.main()
