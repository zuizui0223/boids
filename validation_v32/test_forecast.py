"""Pure invented GPS source / forecast tests, no biological outcome inspection."""
import csv
import datetime as dt
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import forecast as m

DAY=dt.date(2010,1,1)
def synthetic_days(nbirds=28,ndays=35):
    return {(f"private-bird-{i}",DAY+dt.timedelta(days=d)):
             .5+0.04*(i%8)+0.03*(d%5)
             for i in range(nbirds) for d in range(ndays)}

class KnownTruth(unittest.TestCase):
    def test_exact_checksum_pins_for_all_7_source_years(self):
        self.assertEqual(list(m.PINS),list(range(2008,2015)))
        self.assertEqual(sum(x[0] for x in m.PINS.values()),28613430 )
    def test_exact_previous_calendar_day_not_last_eligible(self):
        days=synthetic_days(nbirds=1,ndays=8)
        bird="private-bird-0"
        del days[bird,DAY+dt.timedelta(days=4)]
        ev=m.candidate_events(days)
        dates={date for b,date,v in ev if b==bird}
        self.assertNotIn(DAY+dt.timedelta(days=5),dates)
        self.assertIn(DAY+dt.timedelta(days=6),dates)
    def test_time_parser_and_flags_are_strict(self):
        self.assertEqual(m.parse_timestamp("2011-04-02 10:11:12.500Z"),
                         dt.datetime(2011,4,2,10,11,12,500000))
        with self.assertRaises(ValueError):
            m.parse_timestamp("2011-04-02T10:11:12+02:00")
        self.assertTrue(m.flag_true("TRUE"))
        self.assertFalse(m.flag_true("false"))
        self.assertIsNone(m.flag_true(""))
        self.assertFalse(m.flag_true("",blank_false=True))
        with self.assertRaisesRegex(ValueError,"Boolean"):
            m.flag_true("maybe")
    def test_future_outcome_embargo_without_current_or_future_leakage(self):
        days=synthetic_days()
        events=m.candidate_events(days)
        early=[e for e in events if e[1]<DAY+dt.timedelta(days=25)]
        a,qa=m.predict(days,early)
        changed=dict(days)
        for (bird,date),v in days.items():
            if date>=DAY+dt.timedelta(days=25):changed[bird,date]=v*10000
        b,qb=m.predict(changed,early)
        self.assertEqual(a,b)
        self.assertEqual(qa,qb)
    def test_hybrid_exact_half_and_equal_common_cohort(self):
        days=synthetic_days()
        records,qa=m.predict(days,m.candidate_events(days))
        self.assertGreater(qa["common_future_days_scored"],500)
        self.assertEqual(qa["common_future_birds_scored"],28)
        result=m.evaluate(records)
        self.assertEqual(result["status"],"EXPLORATORY_INDEPENDENT_ORIGINAL_OYSTERCATCHER_NEXT_DAY_FORECAST")
        self.assertEqual(result["model_order"],list(m.MODELS))
        self.assertEqual(list(result["all_frozen_comparisons"]),[
             "PRIMARY_MP_minus_MH","secondary_M0_minus_MP","secondary_MP_minus_MI"])
        self.assertTrue(all(len(r["errors"])==4 for r in records))
        self.assertEqual(result,m.evaluate(records))
    def test_frozen_cohort_stop_no_score_export(self):
        days=synthetic_days(nbirds=19)
        records,_=m.predict(days,m.candidate_events(days))
        outcome=m.evaluate(records)
        self.assertEqual(outcome["status"],"NOT_ADMITTED_ORIGINAL_INDEPENDENT_GPS_QUALITY_SUPPORT")
        self.assertFalse(outcome["any_model_scores_exported"])
        self.assertNotIn("mean_MSE_M0_MP_MI_MH",outcome)
    def test_no_animal_IDs_dates_or_raw_GPS_exposed(self):
        days=synthetic_days()
        records,_=m.predict(days,m.candidate_events(days))
        result=m.evaluate(records)
        encoded=json.dumps(result,sort_keys=True)
        self.assertNotIn("private-bird-",encoded)
        self.assertNotIn("2010-01-",encoded)
        self.assertNotIn('"bird"',encoded)
        self.assertNotIn('"date"',encoded)
    def test_source_flag_duplicate_and_quality_discard_on_invented_gzip(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"O_SCHIERMONNIKOOG-gps-2008.csv.gz"
            with gzip.open(p,"wt",encoding="utf-8",newline="") as io:
                w=csv.DictWriter(io,fieldnames=m.EXPECTED_FIELDS);w.writeheader()
                for day in range(10):
                    for hour in (0,2,4,6,8,12):
                        row={"timestamp":f"2010-01-{day+1:02d} {hour:02d}:00:00",
                             "individual-local-identifier":"private",
                             "individual-taxon-canonical-name":"Haematopus ostralegus",
                             "study-name":"O_SCHIERMONNIKOOG","visible":"true",
                             "manually-marked-outlier":"false",
                             "location-lat":"53.0","location-long":"6.0"}
                        w.writerow(row)
                        if day==0 and hour==2:w.writerow(row)
            with self.assertRaisesRegex(ValueError,"row count drift"):
                m.read_original_daily([p])
    def test_sign_test_edges(self):
        self.assertEqual(m.sign_tail(0,0),1)
        self.assertEqual(m.sign_tail(4,4),.0625)

if __name__=="__main__":unittest.main()
