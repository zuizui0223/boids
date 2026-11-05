"""Known-truth v49 same-original GPS heading/terrain-source sample tests."""
from __future__ import annotations

import math,unittest
from datetime import datetime,timedelta,timezone
import numpy as np

from ahn2_destination_z_tide_prediction import triplets_with_past_motion
from original_heading_tide import unit_direction
from matched_height_valid_direction_elevation import (
    attach_exact_next_heading,joint_predict,relative_fractions,score,
    TRAIN_YEAR,TEST_YEAR)

class V49OriginalSameHeightAndHeadingTests(unittest.TestCase):
    def row(self,k,bird,year):
        t=datetime(year,1,1,tzinfo=timezone.utc)+timedelta(hours=k*4)
        phase=1 if k%3 else -1
        e=.72*phase+.02*math.sin(k+bird)
        n=math.sqrt(1-e*e)
        return {"id":f"b{bird}","t":t,"h":math.sin(k*.17),
                "phase":phase,
                "ghost_phase":1 if (k+bird)%5 in (1,4) else -1,
                "lat":53.45+.01*bird,"lon":5.78+.01*bird,
                "clocksin":math.sin(2*math.pi*t.hour/24),
                "clockcos":math.cos(2*math.pi*t.hour/24),
                "yearsin":math.sin(2*math.pi*t.timetuple().tm_yday/365.25),
                "yearcos":math.cos(2*math.pi*t.timetuple().tm_yday/365.25),
                "previous_e":.8,"previous_n":.6,
                "previous_speed_log":math.log1p(1.8+.1*bird),
                "target_e":e,"target_n":n,
                "target_z_C_NAP_m":.8+.07*math.sin(k*.25)+.02*bird,
                "source_C_selected_tile":(85+bird%2,300)}
    def test_original_C_altitude_valid_rows_match_same_exact_next_heading_key(self):
        t=datetime(2010,7,1)
        tracks={"bird":[(t+timedelta(hours=k),53.43,5.7+.009*k) for k in range(12)]}
        original,_=triplets_with_past_motion(tracks)
        base=[]
        for r in original:
            bstamp=r["B_time"].replace(tzinfo=timezone.utc)
            base.append({"id":r["bird"],"t":bstamp,
                         "lat":r["B_lat"],"lon":r["B_lon"],
                         "previous_e":r["previous_e"],"previous_n":r["previous_n"],
                         "previous_speed_log":r["previous_speed_log"],
                         "target_z_C_NAP_m":.25})
        matched,audit=attach_exact_next_heading(base,tracks,clock_shift_s=0)
        self.assertEqual(len(matched),len(base))
        self.assertTrue(audit["all_v48_source_rows_matched_exactly"])
        self.assertTrue(all(math.isclose(math.hypot(x["target_e"],x["target_n"]),1.)
                            for x in matched))
        changed=[{**base[0],"previous_e":-base[0]["previous_e"]}]+base[1:]
        with self.assertRaisesRegex(ValueError,"PREVIOUS_MOVE_DIFFERED"):
            attach_exact_next_heading(changed,tracks)
    def test_three_models_replay_old_v41_and_v48_forecasts(self):
        train=[self.row(k,b,2010) for b in range(4) for k in range(350)]
        test=[self.row(k,b,2011) for b in range(4) for k in range(350)]
        for model in ("M0","Mreal","Mghost"):
            predicted=joint_predict(train,test,model)
            self.assertEqual(predicted.shape,(len(test),3))
        report=score(train,test,bird_draws=150,week_draws=150)
        self.assertEqual(report["admission"],
                         "MATCHED_ORIGINAL_AHN2_C_VALID_GPS_DIRECTION_ELEVATION_TIDE_PREDICTION")
        self.assertTrue(report["frozen_v41_direction_and_v48_elevation_predictors_replay"])
        self.assertEqual(report["test_source_birds"],4)
        gap=report["paired_original_relative_predictive_skill"][
            "direction_minus_destination_height_phase_relative_skill_gap"]
        self.assertGreater(gap["pooled_equal_bird_relative_gain"],0)
        self.assertEqual(len(gap["pooled_equal_bird_paired_bootstrap95"]),2)
        self.assertEqual(len(gap["separate_equal_week_paired_bootstrap95"]),2)
        self.assertEqual(set(report["previous_year_tidal_phase_negative_controls"]),
                         {"direction","altitude"})
    def test_different_future_height_does_not_change_previously_frozen_features(self):
        from original_heading_tide import vector
        a=self.row(4,0,2010)
        b={**a,"target_z_C_NAP_m":999,
           "target_e":-99,"target_n":99}
        self.assertEqual(vector(a,0),vector(b,0))
        self.assertEqual(vector(a,1),vector(b,1))
    def test_original_test_gate_stops_both_axes(self):
        train=[self.row(k,b,2010) for b in range(4) for k in range(350)]
        test=[self.row(k,b,2011) for b in range(2) for k in range(350)]
        result=score(train,test,bird_draws=30,week_draws=30)
        self.assertEqual(result["admission"],"NOT_ADMITTED_MATCHED_SOURCE_GPS_AHN2_TIDE")
        self.assertEqual(result["matched_axis_outcome"],"NOT_ESTIMATED")
    def test_paired_dimensionless_fractional_skill(self):
        q=relative_fractions(np.array([[.5,.4,2.,2.1],[.7,.5,2.,1.9]]))
        self.assertTrue(np.allclose(q[:,2],q[:,0]-q[:,1]))
        with self.assertRaises(ValueError):
            relative_fractions(np.array([1.,0.,0.,3.]))

if __name__=="__main__":
    unittest.main()
