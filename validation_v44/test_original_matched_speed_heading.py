"""v44: pure original GPS matching and paired axis forecast correctness tests."""
from __future__ import annotations

import csv,gzip,math,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np

from tidal_front import TideSeries
from original_heading_tide import (
    original_three_fix_heading_episodes,vector,forecast as frozen_v41_forecast)
from original_matched_speed_heading import (
    attach_same_next_fix_speed,joint_predict,grouped_score,mean_ratio_summary,
    SOURCE_MIN_TEST,SOURCE_MIN_TEST_BIRDS,SOURCE_MIN_TEST_WEEKS)

class OriginalMatchedEpisodeTests(unittest.TestCase):
    def make_row(self,k,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=k*3)
        phase=1 if k%3 else -1
        target_e=.66*phase+.03*math.sin(k+bird)
        target_n=math.sqrt(1-target_e*target_e)
        return {"id":f"animal{bird}","t":t,
                "lat":53.41+bird*.006,"lon":5.73+bird*.006,
                "h":math.sin(k*.18+bird/3),"phase":phase,
                "previous_e":.8,"previous_n":.6,
                "previous_speed_log":math.log1p(3.+.03*bird),
                "target_e":target_e,"target_n":target_n,
                "target_speed_log":1.1+.20*phase+.02*math.cos(k*.18),
                "clocksin":math.sin(2*math.pi*t.hour/24),
                "clockcos":math.cos(2*math.pi*t.hour/24),
                "yearsin":math.sin(2*math.pi*t.timetuple().tm_yday/365.25),
                "yearcos":math.cos(2*math.pi*t.timetuple().tm_yday/365.25)}
    def test_source_three_fix_tide_episode_and_next_speed_are_exactly_paired(self):
        start=datetime(2010,6,1,0,tzinfo=timezone.utc)
        tide=TideSeries([
            (start-timedelta(hours=3)+timedelta(minutes=10*k),
             .8*math.sin(2*math.pi*k/74.5)) for k in range(190)],
            datum="NAP_m",provenance="synthetic")
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/"original_source.csv.gz"
            with gzip.open(source,"wt",newline="") as out:
                writer=csv.writer(out)
                writer.writerow(["event-id","timestamp","location-lat",
                                 "location-long","individual-local-identifier","visible"])
                event=0
                for ident in ("A","B","C"):
                    for k in range(15):
                        at=start+timedelta(hours=k)
                        event+=1
                        writer.writerow([event,
                                        at.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S.%f"),
                                        53.39,5.73+.011*k,ident,"TRUE"])
            original,prior_audit=original_three_fix_heading_episodes(source,tide,"ameland")
            self.assertGreater(len(original),0)
            attached,receipt=attach_same_next_fix_speed(source,original,"ameland",0)
            self.assertEqual(len(attached),len(original))
            self.assertTrue(receipt["exact_same_B_to_C_source_heading_verified"])
            self.assertTrue(all(x["target_speed_log"]>0 for x in attached))
            self.assertEqual([x["target_e"] for x in attached],
                             [x["target_e"] for x in original])
            forged=[{**r,"target_e":-r["target_e"]} for r in original]
            with self.assertRaisesRegex(ValueError,"HEADING_DOES_NOT_MATCH"):
                attach_same_next_fix_speed(source,forged,"ameland",0)
    def test_v41_feature_and_forecast_identical_despite_new_future_speed_field(self):
        train=[self.make_row(k,b,2010) for b in range(4) for k in range(320)]
        test=[self.make_row(k,b,2011) for b in range(4) for k in range(300)]
        a=joint_predict(train,test,0);b=joint_predict(train,test,1)
        self.assertEqual(a.shape,(1200,3))
        self.assertTrue(np.allclose(a[:,1:],frozen_v41_forecast(train,test,0),atol=1e-10))
        self.assertTrue(np.allclose(b[:,1:],frozen_v41_forecast(train,test,1),atol=1e-10))
        row=train[0]
        changed={**row,"target_speed_log":-200,
                 "target_e":-100,"target_n":-100}
        self.assertEqual(vector(row,0),vector(changed,0))
        self.assertEqual(vector(row,1),vector(changed,1))
    def test_paired_synthetic_known_truth_2011_evaluated(self):
        train=[self.make_row(k,b,2010) for b in range(4) for k in range(320)]
        test=[self.make_row(k,b,2011) for b in range(4) for k in range(320)]
        r=grouped_score(train,test,year=2011,bird_draws=200,week_draws=200)
        self.assertEqual(r["admission"],"OBSERVED_MATCHED_EPISODE_PREDICTIVE_COMPARISON_EXPLORATORY")
        self.assertEqual(r["test_genuine_three_fix_episodes"],1280)
        self.assertEqual(r["n_test_birds"],4)
        self.assertGreaterEqual(r["n_test_ISO_weeks"],4)
        self.assertTrue(r["same_original_test_rows_for_both_axes"])
        self.assertTrue(r["v41_heading_forecast_replayed_exactly"])
        skills=r["paired_relative_skill_comparisons"]
        self.assertGreater(skills["speed_fractional_MSE_reduction"]["pooled_equal_bird_fractional_gain"],0)
        self.assertGreater(skills["direction_fractional_MSE_reduction"]["pooled_equal_bird_fractional_gain"],0)
        self.assertEqual(len(skills["direction_minus_speed_fractional_reduction"]["pooled_equal_bird_paired_bootstrap95"]),2)
        self.assertEqual(len(skills["direction_minus_speed_fractional_reduction"]["separate_equal_week_paired_bootstrap95"]),2)
    def test_2012_only_869_source_episodes_must_stop_both_axes(self):
        train=[self.make_row(k,b,2010) for b in range(4) for k in range(350)]
        test=[self.make_row(k%300,b,2012) for b in range(5)
              for k in range(174)][:869]
        result=grouped_score(train,test,year=2012,bird_draws=20,week_draws=20)
        self.assertEqual(result["admission"],
                         "NOT_ADMITTED_INSUFFICIENT_MATCHED_ORIGINAL_THREE_FIX_SOURCE")
        self.assertEqual(result["speed_or_heading_delta"],"NOT_ESTIMATED")
        self.assertEqual(SOURCE_MIN_TEST,1000)
        self.assertEqual(SOURCE_MIN_TEST_BIRDS,3)
        self.assertEqual(SOURCE_MIN_TEST_WEEKS,4)
    def test_no_invalid_relative_comparison_with_zero_baseline(self):
        x=mean_ratio_summary(np.array([[1.,.8,2.,1.],[2.,1.8,1.5,.8]]))
        self.assertTrue(np.allclose(x[:,2],x[:,1]-x[:,0]))
        with self.assertRaisesRegex(ValueError,"Nonpositive baseline"):
            mean_ratio_summary(np.array([0.,.1,2.,1.]))

if __name__=="__main__":unittest.main()
