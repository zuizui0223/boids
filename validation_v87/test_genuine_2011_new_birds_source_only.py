"""v87 synthetic 2011 genuine-year source QA for new bird IDs, no biology."""
from __future__ import annotations

from collections import Counter,defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import csv,gzip,io,unittest

import genuine_2011_new_birds_source_only as v

def fake_gps_csv(year=2011):
    out=io.StringIO()
    fields=("event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible","old_tide_index_IGNORE")
    w=csv.DictWriter(out,fieldnames=fields)
    w.writeheader()
    n=0
    for bird in ("SYNTHETIC_0","SYNTHETIC_1"):
        for month in (6,7,8):
            for h in range(20):
                w.writerow({
                    "event-id":str(n),
                    "timestamp":f"{year}-{month:02d}-01 "+
                                f"{(h//60):02d}:{(h%60):02d}:00",
                    "location-lat":53.45,"location-long":6.1,
                    "individual-local-identifier":bird,
                    "visible":"TRUE","old_tide_index_IGNORE":999})
                n+=1
    return out.getvalue(),n

class Genuine2011SourceNewBirdKnownTruth(unittest.TestCase):
    def test_original_frozen_two_sites_provider_2011_MD5_pins(self):
        self.assertEqual(v.TARGET_MONTHS,(6,7,8,9,10,11,12))
        self.assertEqual(v.YEARS,(2010,2011))
        self.assertEqual(v.SCHIER_PROVIDER_MD5[2011],
                         "610e3edb48bda7d922d63978feb22ac1")
        self.assertEqual(v.AMELAND_PROVIDER_MD5[2011],
                         "ab74f7443bb09bd5be90bde69fc612eb")
        self.assertEqual(v.MIN_NOVEL_BIRDS_IN_FIXED_YEAR_PERIOD,8)
        self.assertEqual(v.MIN_TOTAL_2011_ONLY_GPS_HOURS_IN_FIXED_PERIOD,2000)

    def test_source_original_year_earliest_bird_hours_and_no_tag_export(self):
        payload,n=fake_gps_csv()
        with TemporaryDirectory() as d:
            f=Path(d)/"original-gps.gz"
            with gzip.open(f,"wt",encoding="utf-8",newline="") as s:
                s.write(payload)
            months,birds,qa=v.original_year_source(
                f,"Schier",2011,expected_raw=n)
        self.assertEqual(n,120)
        self.assertEqual(len(birds),2)
        # Native timestamps in fixture all in hour00, so 1 source fix per bird-month.
        self.assertEqual(qa["original_all_twelve_calendar_month_source"]["06"][
           "original_hourly_GPS_positions"],2)
        self.assertEqual(qa["original_all_twelve_calendar_month_source"]["07"][
           "original_hourly_GPS_positions"],2)
        self.assertEqual(qa["original_all_twelve_calendar_month_source"]["08"][
           "original_hourly_GPS_positions"],2)
        self.assertEqual(qa["original_raw_full_gps_year_records"],120)
        self.assertNotIn("SYNTHETIC_",str(qa))
        self.assertNotIn("old_tide_index_IGNORE",str(qa))

    def test_new_only_2011_bird_ids_genuinely_distinct_from_2010(self):
        old=defaultdict(Counter)
        new=defaultdict(Counter)
        for m in (6,7,8):
            for i in range(8):
                new[m][f"NEW_2011_BIRD_{i}"]=110
            new[m]["REPEAT_BIRD_2010"]=500
            old[m]["REPEAT_BIRD_2010"]=20
        oldIDs={"REPEAT_BIRD_2010"}
        newIDs={"REPEAT_BIRD_2010"}|{f"NEW_2011_BIRD_{i}" for i in range(8)}
        x=v.independent_2011_source(old,oldIDs,new,newIDs,site="Schier")
        self.assertEqual(x["original_distinct_2010_source_birds"],1)
        self.assertEqual(x["original_same_literal_bird_IDs_in_both_years"],1)
        self.assertEqual(x["original_2011_only_distinct_IDs_not_in_2010_original_source"],8)
        self.assertEqual(x["original_2011_JunDec_new_only_GPS_positions"],2640)
        self.assertEqual(x["original_2011_JunDec_months_with_ge5_novel_birds_and_ge200_GPS"],
                         [6,7,8])
        self.assertTrue(x["frozen_source_prospect"]["source_status"].startswith("CANDIDATE"))
        self.assertNotIn("NEW_2011_BIRD_",str(x))
        self.assertNotIn("REPEAT_BIRD_2010",str(x))

    def test_only_seven_new_birds_never_rescue_eight_bird_source_gate(self):
        old=defaultdict(Counter)
        new=defaultdict(Counter)
        for month in (6,7,8,9):
            for i in range(7):
                new[month][f"NEW2011_{i}"]=120
        result=v.independent_2011_source(old,set(),new,
                      {f"NEW2011_{i}" for i in range(7)},site="Ameland")
        self.assertEqual(result["original_2011_new_only_birds_ge20_original_GPS_in_JunDec"],7)
        self.assertEqual(result["original_2011_JunDec_months_with_ge5_novel_birds_and_ge200_GPS"],
                         [6,7,8,9])
        self.assertEqual(result["frozen_source_prospect"]["source_status"],
                         "NOT_ADMITTED_V87_2011_NEW_BIRD_SOURCE_OR_CALENDAR_SUPPORT")

    def test_old_2010_source_census_must_replay_exact_native_counts(self):
        payload,n=fake_gps_csv(year=2010)
        with TemporaryDirectory() as d:
            f=Path(d)/"original-gps.gz"
            with gzip.open(f,"wt",encoding="utf-8",newline="") as s:
                s.write(payload)
            with self.assertRaisesRegex(ValueError,"ORIGINAL_V82_MONTH_COUNT_DRIFT"):
                v.original_year_source(f,"Schier",2010,expected_raw=n)
            with patch.dict(v.SCHIER_SOURCE,{
                6:(2,2),7:(2,2),8:(2,2),9:(0,0),10:(0,0),11:(0,0),12:(0,0)
            },clear=True):
                _,ids,qa=v.original_year_source(f,"Schier",2010,expected_raw=n)
        self.assertEqual(len(ids),2)
        self.assertEqual(qa["original_distinct_bird_IDs_whole_nominal_year"],2)

if __name__=="__main__":
    unittest.main()
