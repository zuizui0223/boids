"""v23 GPS/ERA5 day-ahead forecast pure known-truth and anti-time-leakage tests.

These invented bird tracks are NOT a source of biological conclusions.
"""
from __future__ import annotations
import csv
import datetime as dt
import math
import tempfile
import unittest
from pathlib import Path

import duck_daily_era5_forecast as d


def invented_events(nbirds=30,ndays=30):
    dates=[dt.date(2020,1,1)+dt.timedelta(days=i) for i in range(ndays)]
    data=[]
    for i in range(nbirds):
        for j,day in enumerate(dates):
            # One independent individual day. Hidden known truth is
            # stable individual history plus t-1 meteorological bin.
            category=(j%2,(j//2)%2)
            data.append({
                "bird":("999",f"duck{i:03d}"),
                "date":day,"site":"baikka_beel",
                "weather_class":category,
                "taxon":"invented duck",
                "response":.4+(i%7)*.04+category[0]*.08+category[1]*.05})
    return data


class RegisteredSourceAndFutureChronology(unittest.TestCase):
    def test_frozen_original_2025_gps_and_weather_hashes(self):
        self.assertEqual(d.PINNED_GPS_SHA256,
          "001ec8ffe1e9be5258129dfb931b0abd6551785080e2c755cbd4c72cd79ec52e")
        self.assertEqual(d.PINNED_CANONICAL_ERA5["baikka_beel"],
          "b6c1fc7323cb6cb7275e9f5d31ea8ad1f9f4bea4b479eb93e9a13058057d9b54")
        self.assertEqual(d.PINNED_CANONICAL_ERA5["tanguar_haor"],
          "c856bc0b884b5d13c1529003fc2a1d1d335c856559ae4d4ae7c097837eb54307")
        self.assertEqual(d.MIN_DAY_FIXES,6)
        self.assertEqual(d.MIN_DAY_HOURS,8)
        self.assertEqual(d.SHRINK_KAPPA,2)
        self.assertEqual(d.BOOT_REPS,10000)

    def test_geography_selected_from_prior_day_position_not_future(self):
        x=d.select_weather_point(24.351,91.700)
        self.assertEqual(x[0],"baikka_beel")
        self.assertLess(x[1],1.)
        y=d.select_weather_point(25.149,91.067)
        self.assertEqual(y[0],"tanguar_haor")
        self.assertIsNone(d.select_weather_point(-12.0,30.0))

    def test_synthetic_30_birds_future_days_and_all_four_comparable_models(self):
        records,qc=d.prequential_predictions(invented_events())
        self.assertGreater(len(records),200)
        self.assertEqual(qc["actual_individuals_in_common_target_set"],30)
        self.assertGreater(qc["weather_context_nonfallback_fraction"],.2)
        r=d.evaluate(records)
        self.assertEqual(r["status"],
          "EXPLORATORY_NEW_INDEPENDENT_WILD_DUCK_GPS_ERA5_FUTURE_DAY_PREDICTION")
        self.assertEqual(r["original_independent_bird_count"],30)
        self.assertEqual(len(r["mean_MSE_M0_ME_MI_MEI"]),4)
        self.assertEqual(len(r["frozen_contrasts"]),4)
        self.assertEqual(len(r["per_original_individual_anonymized"]),30)
        self.assertFalse(r["source_animal_social_network_membership_observed"])

    def test_frozen_same_day_prequential_folds_no_target_day_leakage(self):
        all_events=invented_events(nbirds=25,ndays=20)
        base,_=d.prequential_predictions(all_events)
        altered=[]
        t=dt.date(2020,1,12)
        focal=("999","duck000")
        for x in all_events:
            changed=dict(x)
            if x["date"]==t and x["bird"]==focal:
                changed["response"]+=1.2
            altered.append(changed)
        updated,_=d.prequential_predictions(altered)
        by_key=lambda a:{(x["bird"],x["date"]):x for x in a if x["date"]<t}
        self.assertEqual(by_key(base),by_key(updated))
        # Changing one focal duck's day-t response must not change
        # any DIFFERENT duck's contemporaneous errors: all history is
        # frozen before adding day-t observations.
        original_others={(r["bird"],r["date"]):r for r in base
                         if r["date"]==t and r["bird"]!=focal}
        modified_others={(r["bird"],r["date"]):r for r in updated
                         if r["date"]==t and r["bird"]!=focal}
        self.assertEqual(original_others,modified_others)

    def test_site_history_requires_previous_date_and_real_weather(self):
        bird=("1","A")
        t=dt.date(2020,1,2)
        days={
            (bird,t-dt.timedelta(days=1)):{
                "last_prior_location":(24.3503,91.6995),
                "radius_log1p_km":.3,"source_taxon":"Test"},
            (bird,t):{
                "last_prior_location":(50.0,2.0),
                "radius_log1p_km":1.3,"source_taxon":"Test"},
        }
        era={
            "baikka_beel":{t-dt.timedelta(days=1):(26.,2.5,12.)},
            "tanguar_haor":{t-dt.timedelta(days=1):(24.,0.,14.)},
        }
        events,qc=d.eligible_daily_events(days,era)
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]["site"],"baikka_beel")
        self.assertEqual(events[0]["weather_class"],(1,1))
        self.assertEqual(events[0]["response"],1.3)
        self.assertTrue(events[0]["weather_previous_date_only"])
        self.assertTrue(events[0]["weather_location_from_prior_GPS_only"])

    def test_lower_than_min_n_distinct_birds_fails_without_scores(self):
        r=d.evaluate(d.prequential_predictions(invented_events(nbirds=7))[0])
        self.assertEqual(r["status"],"NOT_ADMITTED_ORIGINAL_INDEPENDENT_DUCK_DAYS")
        self.assertFalse(r["any_forecast_score_exported"])

    def test_invalid_GPS_and_exact_duplicate_time_both_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"test.csv"
            with p.open("w",encoding="utf-8",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=d.ducks.SOURCE_COLS)
                writer.writeheader()
                def put(h,hdop=1.,ts="2020-01-03"):
                    writer.writerow({
                       "study.name":d.BANGLADESH_STUDY,
                       "study.id":"5","individual.id":"23",
                       "individual.taxon.canonical.name":"Anas acuta",
                       "timestamp":f"{ts} {h:02d}:00:00",
                       "location.lat":"24.35","location.long":"91.69",
                       "gps.hdop":hdop,"ground.speed":"0"})
                for h in range(0,12,2):put(h)
                put(0) # duplicate 00:00; both removed => only 5 valid
                for h in range(0,12,2):put(h,ts="2020-01-04")
                put(20,hdop=99.,ts="2020-01-04")
            dd,q=d.parse_original_gps(p)
        self.assertEqual(q["original_Bangladesh_study_GPS_rows"],14)
        self.assertEqual(q["original_duplicate_GPS_rows_discarded_entirely"],2)
        self.assertEqual(q["quality_invalid_Bangladesh_GPS_rows"],1)
        self.assertEqual(q["original_Bangladesh_qualifying_UTC_days"],1)

if __name__=="__main__":
    unittest.main()
