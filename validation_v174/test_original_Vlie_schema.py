"""No original elevation read: known-truth DDS/DAS source parser tests."""
import unittest
from original_Vlie_DDS_DAS_source_schema import (
    source_inspect_dds,source_inspect_das,KEYWORDS,N_TILE,SUFFIXES
)
class TestOriginalRemoteSchema(unittest.TestCase):
    def test_original_DDS_grid_variables(self):
        dds='''Dataset {
          Grid {
            ARRAY:
              Float64 altitude[time = 16][y = 624][x = 499];
            MAPS:
              Float64 time[time = 16];
              Float64 x[x = 499];
              Float64 y[y = 624];
          } altitude;
          Int32 isource[time = 16];
        } synthetic.nc;'''
        x=source_inspect_dds(dds)
        self.assertTrue(x["source_DDS_has_real_altitude_variable"])
        self.assertTrue(x["source_DDS_has_real_time_variable"])
        self.assertTrue(x["source_DDS_has_real_isource_variable"])
        self.assertEqual(x["native_time_dimension_lengths"],[16])
    def test_original_DAS_terms_cannot_prove_real_2016_survey(self):
        das='''Attributes { altitude { String units "m"; }
          time { String units "days since 1970-01-01"; }
          NC_GLOBAL { String geospatial_vertical_datum "NAP"; } }'''
        x=source_inspect_das(das)
        self.assertGreater(x["source_DAS_metadata_keyword_line_hits"]["NAP"],0)
        self.assertEqual(x["original_pixel_survey_year"],"NOT_VERIFIED_BY_DAS_ONLY")
    def test_correct_original_ten_source_candidates(self):
        self.assertEqual(N_TILE,10)
        self.assertEqual(SUFFIXES,(".dds",".das"))
        self.assertIn("isource",KEYWORDS)
if __name__=="__main__":unittest.main()
