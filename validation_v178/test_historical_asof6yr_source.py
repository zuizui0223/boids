"""v178 synthetic source-only as-of real z / isource and no-future evidence."""
import unittest
import hashlib
import numpy as np
from real_asof6yr_terrain_pixel_GPS_source import (
    native_time_label_allowed,native_z_and_source_at_points,verify_original_time_vector,
    MAX_SOURCE_LABEL_AGE_YEARS,MIN_GPS_BINS_PER_YEAR,
    EXPECTED_GRID_SHAPE,TARGET_YEARS,PUBLISHED_SURVEY_ROTATION
)
class TestHistoricalAsOfSource(unittest.TestCase):
    def test_2018_strict_prior_year_and_six_year_window(self):
        self.assertTrue(native_time_label_allowed("2017-01-01",2018))
        self.assertTrue(native_time_label_allowed("2012-01-01",2018))
        self.assertFalse(native_time_label_allowed("2011-12-31",2018))
        self.assertFalse(native_time_label_allowed("2018-01-01",2018))
        self.assertFalse(native_time_label_allowed("2019-01-01",2018))
        self.assertFalse(native_time_label_allowed("2025-01-01",2018))
    def test_2019_strict_prior_label_excludes_2019_and_older_2012(self):
        self.assertTrue(native_time_label_allowed("2018-12-31",2019))
        self.assertTrue(native_time_label_allowed("2013-01-01",2019))
        self.assertFalse(native_time_label_allowed("2012-12-31",2019))
        self.assertFalse(native_time_label_allowed("2019-01-01",2019))
        self.assertFalse(native_time_label_allowed("bogus",2019))
    def test_valid_zero_and_invalid_source_index_are_not_confused(self):
        z=np.ma.masked_all(EXPECTED_GRID_SHAPE,dtype=float)
        source=np.ma.masked_all(EXPECTED_GRID_SHAPE,dtype=float)
        z[0,0]=0.;source[0,0]=0.
        z[2,2]=-0.3;source[2,2]=3.
        z[3,3]=1.;source[3,3]=-1.
        z[4,4]=1.;source[4,4]=np.nan
        vals,sv,ok=native_z_and_source_at_points(
             z,source,np.array([0,2,3,4,10]),np.array([0,2,3,4,10]))
        self.assertEqual(ok.tolist(),[True,True,False,False,False])
        self.assertEqual(vals[0],0.)
        self.assertEqual(vals[1],-.3)
        self.assertEqual(sv[0],0.)
    def test_original_time_vector_content_SHA_and_calendar_labels_fail_closed(self):
        vals=np.asarray([16801.,17167.],dtype="<f8") # 2016-01-01 and 2017-01-01
        source_sha=hashlib.sha256(vals.tobytes()).hexdigest()
        self.assertEqual(
            verify_original_time_vector(vals,["2016-01-01","2017-01-01"],source_sha),
            ["2016-01-01","2017-01-01"]
        )
        with self.assertRaises(AssertionError):
            verify_original_time_vector(vals,["2016-01-01","2018-01-01"],source_sha)
        with self.assertRaises(AssertionError):
            verify_original_time_vector(vals,["2016-01-01","2017-01-01"],"0"*64)
    def test_source_rotating_surveys_are_not_2016_everywhere(self):
        self.assertEqual(MAX_SOURCE_LABEL_AGE_YEARS,6)
        self.assertEqual(PUBLISHED_SURVEY_ROTATION,(3,6))
        self.assertEqual(MIN_GPS_BINS_PER_YEAR,20000)
        self.assertEqual(TARGET_YEARS,(2018,2019))
if __name__=="__main__":
    unittest.main()
