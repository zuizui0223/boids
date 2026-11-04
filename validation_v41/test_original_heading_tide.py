import csv
import gzip
import math
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path

import numpy as np
from tidal_front import TideSeries
from original_heading_tide import (
    CLOCKS,MIN_KMPH,MIN_DT_S,RIDGE, TEST_YEAR,
    unit_direction,original_three_fix_heading_episodes,
    vector,forecast,score,directional_half_mse)

class V41HeadingTests(unittest.TestCase):
    def record(self,k,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=4*k)
        phase=(-1 if k%3==0 else 1)
        e=phase*.75+.02*math.sin(k+bird)
        n=math.sqrt(1-e*e)
        return {"id":f"bird_{bird}","t":t,"lat":53.35+bird*.02,
                "lon":5.8+bird*.01,"h":math.sin(k*.1),
                "phase":phase,"previous_e":.8,"previous_n":.6,
                "previous_speed_log":math.log1p(2.0),
                "target_e":e,"target_n":n,
                "clocksin":math.sin(t.hour*2*math.pi/24),
                "clockcos":math.cos(t.hour*2*math.pi/24),
                "yearsin":math.sin(t.timetuple().tm_yday*2*math.pi/365.25),
                "yearcos":math.cos(t.timetuple().tm_yday*2*math.pi/365.25)}
    def test_direction_orientation_and_sensor_stationarity(self):
        a=(None,53.4,5.70);b=(None,53.4,5.72)
        direction=unit_direction(a,b)
        self.assertGreater(direction[0],.999)
        self.assertLess(abs(direction[1]),1e-7)
        self.assertIsNone(unit_direction(a,a))
        self.assertEqual(CLOCKS,(0,-15))
        self.assertEqual(MIN_DT_S,1800)
        self.assertEqual(MIN_KMPH,.4)
        self.assertEqual(RIDGE,10.)
        self.assertEqual(TEST_YEAR,2012)
    def test_no_future_endpoints_are_model_features(self):
        a=self.record(0,1,2010)
        self.assertEqual(len(vector(a,0)),12)
        self.assertEqual(len(vector(a,1)),14)
        altered={**a,"target_e":-a["target_e"],"target_n":-a["target_n"]}
        self.assertEqual(vector(a,0),vector(altered,0))
        self.assertEqual(vector(a,1),vector(altered,1))
    def test_unchanged_source_steps_and_event_tracking(self):
        origin=datetime(2012,6,1,0,tzinfo=timezone.utc)
        tide=TideSeries([(origin-timedelta(hours=3)+timedelta(minutes=k*10),
                          .75*math.sin(2*math.pi*k/74.5)) for k in range(100)],
                        datum="NAP_m",provenance="synthetic")
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'original.csv.gz'
            with gzip.open(p,'wt',newline='') as handle:
                w=csv.writer(handle)
                w.writerow(["event-id","timestamp","location-lat","location-long",
                            "individual-local-identifier","visible"])
                counter=0
                for bird in ('A','B','C'):
                    for k in range(8):
                        t=origin+timedelta(hours=k)
                        counter+=1
                        w.writerow([counter,t.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f"),
                                    53.35,5.76+.012*k,bird,'TRUE'])
            rows,audit=original_three_fix_heading_episodes(p,tide,"ameland")
            self.assertEqual(audit["source_selected_hourly_first_fixes"],24)
            self.assertGreater(len(rows),0)
            self.assertTrue(all(abs(r["target_e"])<=1 for r in rows))
            self.assertTrue(audit["source_future_C_only_used_as_target_not_predictor"])
    def test_synthetic_heading_phase_increment_and_score_units(self):
        train=[self.record(k,b,2010) for b in range(4) for k in range(450)]
        test=[self.record(k,b,2012) for b in range(4) for k in range(410)]
        prediction=forecast(train,test,0)
        self.assertEqual(prediction.shape,(len(test),2))
        target=np.array([[r["target_e"],r["target_n"]] for r in test])
        self.assertEqual(directional_half_mse(target,prediction).shape,(len(test),))
        report=score(train,test,bird_draws=200,week_draws=200)
        self.assertEqual(report["test_birds"],4)
        self.assertTrue(report["outcome_not_in_source_features"])
        self.assertGreater(report["phase_gain_pooled_equal_bird_half_MSE"],0)
        self.assertEqual(report["status"],"OBSERVED_2012_TIDE_CONDITIONAL_HEADING_TRANSFER")
    def test_insufficient_original_test_birds_hard_stop(self):
        train=[self.record(k,0,2010) for k in range(30)]
        test=[self.record(k,0,2012) for k in range(30)]
        self.assertTrue(score(train,test)["status"].startswith("NOT_ADMITTED"))

if __name__=="__main__":
    unittest.main()
