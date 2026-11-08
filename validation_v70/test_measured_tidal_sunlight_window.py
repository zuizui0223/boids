"""v70 synthetic (NOT empirical) official gauge and GPS opportunity-model tests."""
from __future__ import annotations

import math
import unittest
from datetime import date,datetime,timedelta,timezone
from collections import Counter

import numpy as np

from tidal_front import TideSeries
from physical_low_tide_sun_overlap import (
    FIXED_SOURCE_CLOCK,ObservedGaugeSolarOpportunity,
    measured_2010_low_cutoff,match_same_astronomical_daylength,
    source_only_GPS_window_gate)
from real_low_tide_sun_direction import features,forecast,score_field_opportunity

def sample_tide(*,bins=900):
    first=datetime(2010,1,1,tzinfo=FIXED_SOURCE_CLOCK)
    pairs=[(first+timedelta(minutes=10*i),
            .6*math.cos(2*math.pi*i/75))
           for i in range(bins+1)]
    return TideSeries(pairs,datum="NAP_m",provenance="synthetic")

def model_rows(nbirds,year,*,nper=60):
    source=[]
    for bird in range(nbirds):
        for i in range(nper):
            t=datetime(year,i%12+1,15,12 if i%2 else 3,
                       tzinfo=timezone.utc)
            # Low-water phase *does not* identify which clock phases are
            # coobserved; synthetic known-truth joint feature adds signal.
            phase=(1 if (bird+i//2)%2 else -1)
            joint=2. if i%2 else 0.
            # previous position/unit bearing etc same frozen v41 data shape
            target=np.array([1.,joint*1.3-1.3])
            target=target/np.linalg.norm(target)
            source.append({
                "id":f"private_synthetic_{year}_{bird}",
                "t":t,"lat":53.45,"lon":6.2,"h":.1,
                "phase":phase,"previous_e":0.,"previous_n":1.,
                "previous_speed_log":1.,"clocksin":0.,
                "clockcos":1.,"yearsin":math.sin(i%12/6*math.pi),
                "yearcos":math.cos(i%12/6*math.pi),
                "target_e":float(target[0]),"target_n":float(target[1]),
                "solar":.2 if i%2 else -.3,
                "daylen":.25,"low12":3.,"sun12":6.,
                "joint12":joint,"ghostjoint12":2.-joint,
                "sunlit":i%2==0})
    return source

class TideDaylightPhysicalSourceTests(unittest.TestCase):
    def test_original_gauge_12h_is_exclusively_historical_and_bounded(self):
        t=sample_tide()
        obj=ObservedGaugeSolarOpportunity(t,site="schiermonnikoog",cutoff=0.)
        for day in range(3,5):
            date_=datetime(2010,1,day,12,tzinfo=timezone.utc)
            q=obj.history_hours(date_)
            self.assertLessEqual(q["joint"],q["low"]+1e-9)
            self.assertLessEqual(q["joint"],q["sun"]+1e-9)
            self.assertGreaterEqual(q["joint"],0.)
            self.assertGreaterEqual(q["low"]+q["sun"]-q["joint"],0.)
            self.assertLessEqual(q["low"]+q["sun"]-q["joint"],12.+1e-9)
        at=datetime(2010,1,4,12,tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            obj.history_hours(at,offset_hours=6)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            obj.history_hours(datetime(2009,12,30,tzinfo=timezone.utc))

    def test_frozen_quantile_2010_original_year_requires_exact_gauge(self):
        first=datetime(2010,1,1,tzinfo=FIXED_SOURCE_CLOCK)
        gauge=TideSeries(((first+timedelta(minutes=10*k),
                            (k%100)/100)
                          for k in range(52561)),
                         datum="NAP_m",provenance="synthetic")
        self.assertAlmostEqual(measured_2010_low_cutoff(gauge),.24)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            measured_2010_low_cutoff(sample_tide())

    def test_daylength_matched_source_dates_do_not_access_low_water_results(self):
        first=date(2011,1,1)
        source=[]
        for i in range(365):
            d=first+timedelta(days=i)
            # proxy daylength symmetric around late June, source-only
            daylen=12+4*math.cos((i-171)*2*math.pi/365)
            source.append({
                "source_day":d,"daylength_h":daylen,
                "joint_light_h":8. if i%7==0 else 0.})
        pairs=match_same_astronomical_daylength(source)
        self.assertGreater(len(pairs),60)
        self.assertEqual(len(set(i for ij in pairs for i in ij)),2*len(pairs))
        copy=[{**r,"joint_light_h":1000-i} for i,r in enumerate(source)]
        self.assertEqual(pairs,match_same_astronomical_daylength(copy))
        self.assertTrue(all(abs(source[i]["daylength_h"]-source[j]["daylength_h"])
                            <=5/60 for i,j in pairs))

    def test_source_only_eligibility_and_never_mix_train_2011_birds(self):
        train=model_rows(8,2010)
        test=model_rows(13,2011)
        q=source_only_GPS_window_gate(train,test,strict=False)
        self.assertEqual(q["train2010"]["original_source_triplets"],480)
        self.assertEqual(q["test2011"]["original_source_triplets"],780)
        self.assertEqual(q["test2011"]["source_calendar_months"],12)
        with self.assertRaisesRegex(ValueError,"SHARED"):
            source_only_GPS_window_gate(
                train,test+[{**train[0]}],strict=False)
        one=[{**r,"joint12":2.} for r in test]
        with self.assertRaisesRegex(ValueError,"SOURCE_NOT_ADMITTED"):
            source_only_GPS_window_gate(train,one,strict=False)

    def test_nested_2010_source_model_and_real_2011_outcome_nonleak(self):
        train=model_rows(8,2010)
        test=model_rows(13,2011)
        self.assertEqual([len(features(train[0],m))
                          for m in ("M0","M1","M2","Mghost")],
                         [18,19,20,19])
        v=forecast(train,test,"M0")
        flipped=[{**r,"target_e":-r["target_e"],
                  "target_n":-r["target_n"]} for r in test]
        w=forecast(train,flipped,"M0")
        np.testing.assert_array_equal(v,w)
        result=score_field_opportunity(train,test,strict=False)
        self.assertEqual(result["2010_disjoint_training_and_2011_original_bird_equal_heldout"][
            "primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"]["original_birds"],13)
        self.assertNotIn("private_synthetic",str(result))
        self.assertEqual(result["frozen_primary_source_and_bird_interval_decision"],
                         "POSITIVE_GAUGE_LOW_WATER_SUN_OVERLAP_EXPLORATORY_DIRECTION_GAIN")
        flipped_out=score_field_opportunity(train,flipped,strict=False)
        self.assertNotEqual(result["2010_disjoint_training_and_2011_original_bird_equal_heldout"][
           "primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
           "bird_equal_gain_half_MSE"],
           flipped_out["2010_disjoint_training_and_2011_original_bird_equal_heldout"][
           "primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"][
           "bird_equal_gain_half_MSE"])

if __name__=="__main__":
    unittest.main()
