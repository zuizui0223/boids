"""v175 source-free true survey-date conversion and no fabricated grid values."""
import unittest
import numpy as np
from datetime import datetime,timezone
from native_actual_survey_time_source import (
    true_source_time_days_to_dates,MAX_TIMES_PER_TILE,TARGET_SURVEY_YEAR
)
class TestOriginalSurveyDates(unittest.TestCase):
    def test_true_native_day_offsets_years(self):
        self.assertEqual(true_source_time_days_to_dates([0,365,366]),
                         ["1970-01-01","1971-01-01","1971-01-02"])
        day=(datetime(2016,9,12,tzinfo=timezone.utc)-
             datetime(1970,1,1,tzinfo=timezone.utc)).days
        self.assertEqual(true_source_time_days_to_dates(np.array([day]))[0],"2016-09-12")
    def test_catalog_may_span_2016_but_actual_source_time_may_not(self):
        true_dates=true_source_time_days_to_dates([16400,18200])
        self.assertNotIn(TARGET_SURVEY_YEAR,[int(s[:4]) for s in true_dates])
    def test_corrupt_dates_stop_not_assume_2016(self):
        with self.assertRaises(ValueError):true_source_time_days_to_dates([float("nan")])
        with self.assertRaises(ValueError):true_source_time_days_to_dates([1e8])
        with self.assertRaises(ValueError):true_source_time_days_to_dates([])
    def test_source_time_vector_cap(self):
        self.assertEqual(MAX_TIMES_PER_TILE,125)
        with self.assertRaises(ValueError):true_source_time_days_to_dates(np.arange(200))
if __name__=="__main__":
    unittest.main()
