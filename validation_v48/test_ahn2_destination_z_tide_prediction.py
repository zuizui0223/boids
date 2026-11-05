"""v48 synthetic known-truth tests for GPS-original next terrain height target.

These tests cannot be cited as wild tide/terrain effects. Wild source is only
read by v48 CLI after the exact pre-outcome contract is committed.
"""
import math,random,unittest
from datetime import datetime,timedelta,timezone

import numpy as np
from original_heading_tide import vector
from source_original_gps_ahn2_overlap import source_triples
from ahn2_destination_z_tide_prediction import (
    SOURCE_YEARS,MIN_TRAIN,MIN_TEST,MIN_TEST_BIRDS,MIN_TEST_WEEKS,
    MIN_TEST_CELLS,triplets_with_past_motion,predict_z,score)

class HistoricalAHN2DestinationPhaseTests(unittest.TestCase):
    def row(self,k,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=k*3)
        phase=1 if k%3 else -1
        ghost=1 if (k+bird)%4 in (0,1) else -1
        src_cell=(85+bird%2,300)
        return {"id":f"bird{bird}","t":t,
                "lat":53.43+bird*.01,"lon":5.7+bird*.007,
                "h":.8*math.sin(k*.17+bird*.13),"phase":phase,
                "ghost_phase":ghost,
                "clocksin":math.sin(2*math.pi*t.hour/24),
                "clockcos":math.cos(2*math.pi*t.hour/24),
                "yearsin":math.sin(2*math.pi*t.timetuple().tm_yday/365.25),
                "yearcos":math.cos(2*math.pi*t.timetuple().tm_yday/365.25),
                "previous_e":.8,"previous_n":.6,
                "previous_speed_log":math.log1p(1.+bird*.4),
                "source_C_selected_tile":src_cell,
                "target_z_C_NAP_m":-.3+.7*phase+.01*bird+.06*math.cos(k*.2)}
    def test_frozen_years_source_and_admission(self):
        self.assertEqual(SOURCE_YEARS,(2010,2011))
        self.assertEqual((MIN_TRAIN,MIN_TEST),(400,500))
        self.assertEqual((MIN_TEST_BIRDS,MIN_TEST_WEEKS,MIN_TEST_CELLS),(3,4,2))
    def test_independent_GPS_geometry_replays_v46_original_C(self):
        t=datetime(2011,6,1)
        track={"a":[(t+timedelta(hours=i),53.43,5.8+.01*i) for i in range(12)]}
        original,reasons=source_triples(track)
        fresh,again=triplets_with_past_motion(track)
        self.assertEqual(reasons,again)
        self.assertEqual(len(original),len(fresh))
        self.assertEqual([(r["bird"],r["time"],r["lat"],r["lon"]) for r in original],
                         [(r["bird"],r["time"],r["lat"],r["lon"]) for r in fresh])
        self.assertTrue(all("previous_speed_log" in r and "previous_e" in r for r in fresh))
        self.assertFalse(any("phase" in r for r in fresh))
    def test_original_terrain_outcome_is_not_part_of_phase_predictors(self):
        row=self.row(4,0,2010)
        altered={**row,"target_z_C_NAP_m":100.0}
        self.assertEqual(vector(row,0),vector(altered,0))
        self.assertEqual(vector(row,1),vector(altered,1))
        self.assertEqual(len(vector(row,0)),12)
        self.assertEqual(len(vector(row,1)),14)
    def test_synthetic_true_phase_beats_same_station_yearago_placebo(self):
        train=[self.row(k,b,2010) for b in range(4) for k in range(420)]
        test=[self.row(k,b,2011) for b in range(4) for k in range(420)]
        p0=predict_z(train,test,"M0")
        p1=predict_z(train,test,"Mreal")
        pg=predict_z(train,test,"Mghost")
        self.assertEqual(p0.shape,(len(test),))
        self.assertEqual(p1.shape,p0.shape)
        self.assertEqual(pg.shape,p0.shape)
        result=score(train,test,bird_draws=150,week_draws=150)
        self.assertEqual(result["admission"],
                         "OBSERVED_ORIGINAL_NEXT_DESTINATION_AHN2_ELEVATION_TIDE_PREDICTION")
        self.assertGreater(result["contrasts"]["M0_minus_Mreal"]["pooled_equal_bird_MSE_gain_NAP_m2"],0)
        self.assertGreater(result["contrasts"]["Mghost_minus_Mreal"]["pooled_equal_bird_MSE_gain_NAP_m2"],0)
        self.assertTrue(result["original_true_AHN2_destination_z_C_not_tide_defined"])
        self.assertEqual(result["test_birds"],4)
        self.assertEqual(result["test_source_AHN2_cells"],2)
        self.assertGreaterEqual(result["test_weeks"],4)
    def test_inadequate_observed_source_fails_without_fake_effect(self):
        train=[self.row(k,b,2010) for b in range(4) for k in range(410)]
        test=[self.row(k,b,2011) for b in range(3) for k in range(100)]
        r=score(train,test,bird_draws=20,week_draws=20)
        self.assertEqual(r["admission"],"NOT_ADMITTED_DESTINATION_TERRAIN_OR_TIDE_SOURCE")
        self.assertEqual(r["test_outcome"],"NOT_ESTIMATED")
        with self.assertRaises(ValueError):
            predict_z(train,test,"unregistered_model")

if __name__=="__main__":unittest.main()
