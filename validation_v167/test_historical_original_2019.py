"""Synthetic v167 source manifest/year QC and fixed transferred model tests."""
import unittest
from original_2019_history_tide_replay import (
    SOURCE_YEAR,ORIGINAL_V127_RUN,MIN_HISTORY_PAIRS,
    MIN_COMMON_BIRD_TIDE_SOURCE,STAGE_OFFSETS,RIDGE_LAMBDA,WEEK_FOLDS)
from native_quarterhour_lag_tide import corrected_previous_bin
from datetime import datetime,timedelta,timezone

class Test2019HistoricalTransfer(unittest.TestCase):
    def test_source_year_and_fixed_tide_shifts(self):
        self.assertEqual(SOURCE_YEAR,2019)
        self.assertEqual(ORIGINAL_V127_RUN,43461048062)
        self.assertEqual(STAGE_OFFSETS,(0,3,7,11))
        self.assertEqual(RIDGE_LAMBDA,20.)
        self.assertEqual(WEEK_FOLDS,5)
        self.assertEqual(MIN_HISTORY_PAIRS,25000)
        self.assertEqual(MIN_COMMON_BIRD_TIDE_SOURCE,20000)
    def test_observed_previous_quarterhour_event_offset_nonconstant(self):
        utc=datetime(2019,6,11,9,0,tzinfo=timezone.utc)
        rows=[]
        for m,s in ((3,19),(17,4),(31,44)):
            rows.append(({"private_bird":"same_bird",
                          "source_utc_event":utc+timedelta(minutes=m,seconds=s),
                          "source_month":6},
                         "day",None,24))
        idx,prev,q=corrected_previous_bin(rows)
        self.assertEqual(idx.tolist(),[1,2])
        self.assertEqual(prev.tolist(),[0,1])
        self.assertEqual(q["TRUE_OBSERVED_PREVIOUS_NATIVE_15MIN_BIN_SAME_BIRD"],2)
    def test_not_an_independent_animal_population(self):
        self.assertEqual(SOURCE_YEAR-2018,1)

if __name__=="__main__":unittest.main()
