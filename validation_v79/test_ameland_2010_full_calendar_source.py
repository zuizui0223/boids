"""v79 known-truth source census, no original ecological tide or solar results."""
import csv,gzip,io,tempfile,unittest
from datetime import datetime,timedelta
from pathlib import Path

from ameland_2010_full_calendar_source import (
    source_month_counts,EXPECTED_AMELAND_GPS_SHA,
    ORIGINAL_OLD_V78_2010_SOURCE,
    MODEL_NATIVE_GEO_VALID_2010_MONTHS)

def fixture_source():
    b=io.StringIO()
    fieldnames=("event-id","timestamp","location-lat","location-long",
                "individual-local-identifier","visible","unopened_bird_future")
    w=csv.DictWriter(b,fieldnames=fieldnames);w.writeheader()
    raw=0
    for bird in range(10):
        months=(1,2,3,4,5) if bird<=3 else (8,9,10,11,12)
        # Original last bird also observed early to test counted intersection.
        if bird==4:months=(1,2,3,4,5,8,9,10,11,12)
        for m in months:
            for hour in range(25):
                t=datetime(2010,m,2)+timedelta(hours=hour)
                w.writerow({"event-id":str(raw),
                    "timestamp":t.strftime("%Y-%m-%d %H:%M:%S"),
                    "location-lat":53.44,"location-long":5.75,
                    "individual-local-identifier":f"SYNTHETIC_AMELAND_{bird}",
                    "visible":"TRUE","unopened_bird_future":1000+hour})
                raw+=1
    return b.getvalue(),raw

class AmelandAll2010SourceTests(unittest.TestCase):
    def test_original_source_pins_and_10_prospectively_geocoded_months(self):
        self.assertEqual(len(ORIGINAL_OLD_V78_2010_SOURCE),5)
        self.assertEqual(tuple(MODEL_NATIVE_GEO_VALID_2010_MONTHS),
            (1,2,3,4,5,8,9,10,11,12))
        self.assertEqual(EXPECTED_AMELAND_GPS_SHA,
            "c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c")

    def test_earliest_native_hour_and_bird_union_without_exposing_bird_identity(self):
        text,raw=fixture_source()
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"observations.gz"
            with gzip.open(f,"wt",encoding="utf-8",newline="") as stream:
                stream.write(text)
            q=source_month_counts(f,expected_raw=raw,
                                  verify_v78_late_source=False)
        self.assertEqual(len(q["all_twelve_original_months"]),12)
        self.assertEqual(q["original_2010_total_distinct_bird_IDs_after_geographic_visible_hour_filter"],10)
        self.assertEqual(q["original_2010_month_01_05_birds_union_count"],5)
        self.assertEqual(q["original_2010_month_08_12_birds_union_count"],6)
        self.assertEqual(q["original_2010_birds_both_early_and_late_count"],1)
        self.assertEqual(q["original_2010_early_only_birds_not_in_v78_late_source"],4)
        self.assertEqual(q["original_2010_2010JanMay_AugDec_geo_candidate_birds_union"],10)
        self.assertTrue(q["new_full_year_candidate_status"].startswith("CANDIDATE"))
        self.assertNotIn("SYNTHETIC_AMELAND_1",str(q))
        self.assertEqual(q["all_twelve_original_months"]["06"]["original_Ame_distinct_bird_IDs"],0)
        self.assertIn("MISSING_LAT",
            q["all_twelve_original_months"]["06"]["2010_native_NIOZ_model_geographic_status_previously_audited"])

    def test_original_v78_frozen_late_month_drift_fails_no_hidden_7bird_to_8bird_rescue(self):
        text,raw=fixture_source()
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"observations.gz"
            with gzip.open(f,"wt",encoding="utf-8",newline="") as stream:
                stream.write(text)
            with self.assertRaisesRegex(ValueError,"V78_AUG_DEC_SOURCE_DRIFT"):
                source_month_counts(f,expected_raw=raw,
                                    verify_v78_late_source=True)
            with self.assertRaisesRegex(ValueError,"119507"):
                source_month_counts(f,expected_raw=raw+1,
                                    verify_v78_late_source=False)

if __name__=="__main__":
    unittest.main()
