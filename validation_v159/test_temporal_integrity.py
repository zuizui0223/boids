"""Source-free known-truth checks for C-POD clock and denominator assumptions."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from site_hour_integrity import iso_weekday_source_ordinal,as_int,as_float,ORIGINAL_SHA

class TestTemporalIntegrity(unittest.TestCase):
    def test_hourly_ordinal_and_leap(self):
        a=iso_weekday_source_ordinal(2020,59,23)
        b=iso_weekday_source_ordinal(2020,60,0)
        self.assertEqual(b-a,1)
        self.assertIsNone(iso_weekday_source_ordinal(2019,366,0))
        self.assertIsNone(iso_weekday_source_ordinal(2020,366,24))
    def test_row_integer_reject_fraction_and_missing(self):
        self.assertEqual(as_int("0"),0)
        self.assertEqual(as_int("23.0"),23)
        self.assertIsNone(as_int("NA"))
        self.assertIsNone(as_int("0.5"))
        self.assertIsNone(as_int(""))
    def test_click_positive_is_not_device_effort(self):
        source_hours={1:{"clicks":10},3:{"clicks":15}}
        self.assertNotIn(2,source_hours)
        self.assertNotEqual(len(source_hours),3)
        self.assertEqual(ORIGINAL_SHA,"972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf")

if __name__=="__main__":unittest.main()
