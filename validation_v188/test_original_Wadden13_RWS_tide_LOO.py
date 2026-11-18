import math
import unittest
from datetime import datetime,timezone,timedelta
from validation_v188.original_Wadden13_RWS_tide_LOO import STATIONS,REFERENCE_RD,geometry_for_target,score_source_only
class FixedStationLOO(unittest.TestCase):
    def test_frozen_source_cohort_and_no_self_in_any_predictors(self):
        self.assertEqual(len(STATIONS),13)
        for s in STATIONS:
            g=geometry_for_target(s)
            self.assertNotEqual(g["nearest_name"],s)
            self.assertNotIn(s,g["idw3_sites"])
            if g["reference_geometry_triangle"] is not None:
                self.assertNotIn(s,[x for x,w in g["reference_geometry_triangle"]])
            self.assertAlmostEqual(sum(g["idw3_weights"]),1,places=10)
    def test_perfect_flat_field_has_zero_mse_for_all_sources(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        ticks=[t0+timedelta(minutes=i*10) for i in range(200)]
        x={site:{t:math.sin(i*.1) for i,t in enumerate(ticks)} for site in STATIONS}
        a=score_source_only(x,ticks)
        self.assertEqual(a["n_frozen_station_target_holdouts"],13)
        self.assertEqual(a["equal_station_mean_IDW3_MSE_m2"],0)
        self.assertEqual(a["equal_station_mean_nearest_MSE_m2"],0)
    def test_triangle_is_exact_on_spatial_plane_at_hull_interior(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        ticks=[t0+timedelta(minutes=i*10) for i in range(200)]
        x={site:{t:0.000002*REFERENCE_RD[site][0]+0.000001*REFERENCE_RD[site][1]+.01*i
                 for i,t in enumerate(ticks)} for site in STATIONS}
        a=score_source_only(x,ticks)
        self.assertGreater(a["n_reference_triangle_inside_hull_targets"],0)
        for sc in a["station_source_only_LOO"].values():
            if sc["mse_triangle_m2"] is not None:
                self.assertAlmostEqual(sc["mse_triangle_m2"],0,places=8)
if __name__=="__main__":
    unittest.main()
