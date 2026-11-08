"""v69 synthetic physical solar/daylength and source-only/model unit tests."""
import unittest
from datetime import datetime,timedelta,timezone
from math import sin,cos,pi
import numpy as np

from tide_daylight_interaction import (
    solar_features,feature_vector,source_gate,augment,predict,
    score_two_clocks,_boot)

def fixture(n_birds,year,*,n_per_bird=84):
    rows=[]
    for bird in range(n_birds):
        for k in range(n_per_bird):
            month=1+(k%12)
            # Synthetic original-shaped rows, not real wild animal records.
            t=datetime(year,month,15,(8 if k%2 else 21),0,tzinfo=timezone.utc)
            solar=1 if k%2 else -1
            phase=1 if ((k//2+bird)%2) else -1
            daylen=(month-6)/5
            light_signal=phase*(solar+daylen)
            target=np.asarray([light_signal+.15,.5])
            target=target/np.linalg.norm(target)
            rows.append({"id":f"synthetic_{year}_{bird}",
                "t":t,"lat":53.45,"lon":6.,"h":0.3+(k%7)*.01,
                "phase":phase,
                "previous_e":1.,"previous_n":0.,"previous_speed_log":1.2,
                "clocksin":sin(2*pi*t.hour/24),"clockcos":cos(2*pi*t.hour/24),
                "yearsin":sin(2*pi*month/12),"yearcos":cos(2*pi*month/12),
                "target_e":float(target[0]),"target_n":float(target[1]),
                "solar":float(solar),"daylen":float(daylen),
                "ghost_solar":float(-solar),
                "sunlit":solar>0,"twilight":False,
                "day_length_hours":12+4*daylen})
    return rows

class SolarAndTidalInteractionTests(unittest.TestCase):
    def test_real_53n_summer_winter_daylength_and_noon_night(self):
        winter=solar_features({"t":datetime(2010,12,21,12,tzinfo=timezone.utc),
                               "lat":53.45,"lon":6.0})
        summer=solar_features({"t":datetime(2010,6,21,12,tzinfo=timezone.utc),
                               "lat":53.45,"lon":6.0})
        night=solar_features({"t":datetime(2010,6,21,0,tzinfo=timezone.utc),
                              "lat":53.45,"lon":6.0})
        self.assertLess(winter["day_length_hours"],9)
        self.assertGreater(summer["day_length_hours"],16)
        self.assertTrue(summer["sunlit"])
        self.assertFalse(night["sunlit"])
        self.assertGreater(summer["solar"],night["solar"])
        self.assertNotEqual(summer["solar"],summer["ghost_solar"])

    def test_feature_nesting_and_model_disallowed(self):
        row=fixture(1,2010)[0]
        self.assertEqual([len(feature_vector(row,m))
                          for m in ("M0","M1","M2","Mghost")],
                         [16,17,18,18])
        self.assertEqual(feature_vector(row,"M2")[:-2],
                         feature_vector(row,"M0"))
        self.assertNotEqual(feature_vector(row,"M2")[-2],
                            feature_vector(row,"Mghost")[-2])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            feature_vector(row,"data_tuned_best")

    def test_literal_bird_disjoint_and_both_light_support_gate(self):
        train=fixture(8,2010)
        test=fixture(13,2011)
        counts=source_gate(train,test,strict=False)
        self.assertEqual(counts["train"]["observed_original_GPS_triplets"],8*84)
        self.assertEqual(counts["test"]["observed_original_GPS_triplets"],13*84)
        self.assertEqual(counts["test"]["original_calendar_months_with_source"],12)
        mixed=test.copy()
        mixed.append({**train[0]})
        with self.assertRaisesRegex(ValueError,"SHARED_BIRD"):
            source_gate(train,mixed,strict=False)
        all_day=[{**r,"sunlit":True} for r in train]
        with self.assertRaisesRegex(ValueError,"SOURCE_NOT_ADMITTED"):
            source_gate(all_day,test,strict=False)

    def test_target_handling_with_same_source_features(self):
        train=fixture(8,2010)
        test=fixture(13,2011)
        a=predict(train,test,"M0")
        self.assertEqual(a.shape,(13*84,2))
        altered=[{**r,"target_e":-r["target_e"],
                  "target_n":-r["target_n"]} for r in test]
        b=predict(train,altered,"M0")
        self.assertTrue(np.array_equal(a,b))
        out=score_two_clocks(train,test,strict=False)
        self.assertEqual(
            out["original_2011_equal_bird_heldout_next_heading_2D_half_MSE"][
                "primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"][
                "original_birds"],13)
        self.assertTrue(out["not_new_cross_species_or_unseen_coast_validation"])
        self.assertNotIn("synthetic_2011_0",str(out))

    def test_independent_test_bird_bootstrap_extends_thirteen_not_thousands(self):
        a=_boot([.1]*13,200,20261108)
        self.assertAlmostEqual(a[0],.1)
        self.assertAlmostEqual(a[1],.1)
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP"):
            _boot([np.nan],20,20261108)

if __name__=="__main__":
    unittest.main()
