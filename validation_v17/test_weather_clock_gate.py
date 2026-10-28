"""v17-A3 synthetic-only MATLAB source clock and no-response controls."""
import datetime as dt
import json
import unittest

import weather_clock_gate as m


class TimeGateTests(unittest.TestCase):
    def test_fixed_three_predeclared_utc_offsets_no_argmax(self):
        self.assertEqual(m.OFFSET_HOURS,(-1,0,1))
        self.assertEqual(m.NEAREST_WEATHER_SEC,90)

    def test_matlab_datenum_known_truth_conversion(self):
        moment=dt.datetime(2015,7,1,12,0,0)
        x=moment.toordinal()+366+.5
        self.assertEqual(m.matlab_datenum_candidate(str(x)),moment)
        with self.assertRaisesRegex(ValueError,"outside plausible"):
            m.matlab_datenum_candidate("123.4")

    def test_original_Qstarz_UTC_prefix_year_and_UK_day_first(self):
        row={"UTC DATE":"2015/7/1","UTC TIME":"9:2:3","MS":"200"}
        self.assertEqual(m.original_utc_candidate(row),
                         dt.datetime(2015,7,1,9,2,3,200000))
        row2={"UTC DATE":"13/07/2015","UTC TIME":"9:2:3","MS":"20"}
        self.assertEqual(m.original_utc_candidate(row2),
                         dt.datetime(2015,7,13,9,2,3,20000))
        with self.assertRaisesRegex(ValueError,"out-of-range"):
            m.original_utc_candidate({**row,"MS":"1000"})

    def test_overlap_source_clock_does_not_auto_choose_timezone(self):
        observed=[dt.datetime(2015,7,1,13)]
        wind=[dt.datetime(2015,7,1,14)]
        result=m.nearest_structure(observed,wind)
        self.assertEqual(result["-1"]["source_timing_matches_within_90s"],1)
        self.assertEqual(result["0"]["source_timing_matches_within_90s"],0)
        self.assertEqual(result["1"]["source_timing_matches_within_90s"],0)
        self.assertNotIn("selected",json.dumps(result))

    def test_continuous_weather_can_make_all_clock_shifts_ambiguous(self):
        date=dt.datetime(2015,7,1,11)
        wind=[date+dt.timedelta(minutes=k) for k in range(240)]
        out=m.nearest_structure([date+dt.timedelta(hours=2)],wind)
        self.assertTrue(all(x["coverage_fraction"]==1.0 for x in out.values()))
        # This is why coverage is not a causal, timezone or response validation.


if __name__=="__main__":
    unittest.main()
