"""Invented known-truth physics/timeline tests. Do not open animal outcomes."""
import datetime as dt
import json
import math
import unittest
import numpy as np
import tidal_forecast as m

DAY=dt.date(2010,1,1)
class TidalKnownTruth(unittest.TestCase):
 def test_frozen_single_real_RWS_station_and_UTC_source(self):
  self.assertEqual(m.STATION,"schiermonnikoog.waddenzee")
  self.assertEqual(len(m.YEARS),7)
  self.assertEqual(m.rws_body(2010)["AquoPlusWaarnemingMetadata"]["AquoMetadata"]["ProcesType"],"astronomisch")
  with self.assertRaises(ValueError):m.rws_body(2030)
  self.assertEqual(m.utc_stamp("2010-05-12T00:00:00.000+01:00"),dt.datetime(2010,5,11,23))
  with self.assertRaises(ValueError):m.utc_stamp("2010-05-12T00:00:00+02:00")
 def test_RWS_metadata_units_and_process_must_match(self):
  src={"Succesvol":True,"WaarnemingenLijst":[{
   "Locatie":{"Code":m.STATION},
   "AquoMetadata":{"Grootheid":{"Code":"WATHTE"},"Eenheid":{"Code":"cm"},
        "Hoedanigheid":{"Code":"NAP"},"ProcesType":"astronomisch"},
   "MetingenLijst":[{"Tijdstip":"2010-01-01T00:00:00.000+01:00",
      "Meetwaarde":{"Waarde_Numeriek":130}}]}]}
  with self.assertRaisesRegex(ValueError,"missing"):
   m.tide_series_from_response(src,2010) # full year not present
  src["WaarnemingenLijst"][0]["AquoMetadata"]["Eenheid"]["Code"]="m"
  with self.assertRaisesRegex(ValueError,"metadata"):m.tide_series_from_response(src,2010)
 def test_10minute_daily_quadrant_support(self):
  start=dt.datetime(2010,5,12)
  series={start+dt.timedelta(minutes=10*i):math.sin(2*math.pi*i/72)
          for i in range(144)}
  d=m.daily_tide_range(series)
  self.assertEqual(len(d),1)
  self.assertAlmostEqual(d[DAY+dt.timedelta(days=131)]["range_m"],2.)
  thin={k:v for k,v in series.items() if k.hour<18}
  self.assertEqual(m.daily_tide_range(thin),{})
 def test_freeze_tide_feature_requires_both_exact_dates(self):
  base={DAY+dt.timedelta(days=i):{"range_m":2+.1*i,"slots":144} for i in range(30)}
  r=[{"bird":"private","date":DAY+dt.timedelta(days=12),"y":.5,"mh":.4,
       "original_v32_errors":[.3,.2,.1,.01]}]
  rows,qa=m.freeze_tide_features(r,base)
  self.assertEqual(qa,{})
  self.assertAlmostEqual(rows[0]["z"],.1)
  self.assertAlmostEqual(rows[0]["z_shift"],.1)
  del base[DAY+dt.timedelta(days=19)]
  self.assertEqual(m.freeze_tide_features(r,base)[0],[])
 def test_no_same_day_residual_updates_beta(self):
  date=DAY+dt.timedelta(days=8)
  rows=[{"bird":"a","date":date,"y":1.,"mh":0.,"z":1.,"z_shift":0.,
         "year_sin":.1,"year_cos":.5,"original_v32_errors":[1.,1.,1.,1.]},
        {"bird":"b","date":date,"y":99.,"mh":0.,"z":1.,"z_shift":0.,
         "year_sin":.1,"year_cos":.5,"original_v32_errors":[1.,1.,1.,99**2]}]
  res,qa=m.predicted_errors(rows)
  self.assertEqual([x["errors"][1] for x in res],[1.,99**2])
  self.assertTrue(qa["same_day_all_target_outcomes_embargoed"])
 def test_equal_bird_means_not_day_counts(self):
  rs=[]
  for i in range(30):
   n=400 if i==0 else 200
   errs=[4.,0.,4.,0.,4.] if i==0 else [0.,2.,0.,2.,0.]
   rs.extend({"bird":f"private-{i:02d}","errors":errs} for _ in range(n))
  out=m.evaluate(rs)
  self.assertEqual(out["status"],"EXPLORATORY_RWS_ASTRONOMICAL_TIDE_FORECAST")
  self.assertEqual(out["original_birds"],30)
  self.assertEqual(out["common_future_bird_days"],6200)
  self.assertAlmostEqual(out["mean_MSE"][0],4./30.)
  self.assertAlmostEqual(out["mean_MSE"][1],58./30.)
  self.assertEqual(out,m.evaluate(rs))
 def test_admission_fail_no_tide_scores(self):
  out=m.evaluate([{"bird":"b","errors":[1.,0.,1.,0.,1.]}])
  self.assertEqual(out["status"],"NOT_ADMITTED_TIDE_MATCHED_SUPPORT")
  self.assertFalse(out["any_tidal_forecast_scores_exported"])
  self.assertNotIn("comparisons",out)
 def test_reconstruct_never_changes_v32_baseline(self):
  daily={}
  bird="x"
  for i in range(8):daily[bird,DAY+dt.timedelta(days=i)]=float(i)/10
  events=m.v32.candidate_events(daily)
  records=[{"bird":bird,"date":DAY+dt.timedelta(days=5),"n_past_own":4,
            "errors":[.0,.0,.0,.0]}]
  with self.assertRaisesRegex(ValueError,"receipt"):
   m.reconstruct_original_v32_predictions(events,daily,records)

if __name__=="__main__":unittest.main()
