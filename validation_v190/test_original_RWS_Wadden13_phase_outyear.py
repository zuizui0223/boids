import unittest,math
from datetime import datetime,timedelta,timezone
from validation_v190.original_RWS_Wadden13_phase_outyear import (
  GRID_MIN,fit_lag_one_edge,fit_all_edges,evaluate_window,SourceStop,STATIONS)
class PhaseSourceGates(unittest.TestCase):
    def test_frozen_phase_grid(self):
        self.assertEqual(GRID_MIN[0],-120)
        self.assertEqual(GRID_MIN[-1],120)
        self.assertEqual(len(GRID_MIN),25)
    def test_genuine_fixed_positive_delay_recovered_on_synthetic(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        source={t0+timedelta(minutes=10*i):math.sin(i*.11)+.23*math.cos(i*.19)
                for i in range(330)}
        target={t:.37+1.17*source[t-timedelta(minutes=30)] for t in source
                if t-timedelta(minutes=30) in source}
        fit=fit_lag_one_edge(target,source)
        self.assertEqual(fit["trained_2018_June_lag_min"],30)
        self.assertGreater(fit["training_max_pearson_r"],.9999)
    def test_all_models_same_targets_and_target_2018_calibrated(self):
        t0=datetime(2018,6,1,tzinfo=timezone.utc)
        ticks=[t0+timedelta(minutes=10*i) for i in range(300)]
        values={site:{t:math.sin(i*.06+.005*sindex)+.01*math.cos(i*.23)
            for i,t in enumerate(ticks)} for sindex,site in enumerate(STATIONS)}
        fitted=fit_all_edges(values)
        score=evaluate_window(values,fitted)
        self.assertEqual(score["n_frozen_gauge_targets"],13)
        self.assertTrue(all(v["source_same_target_UTC_for_every_model"]
                            for v in score["all_original_station_level_results"].values()))
    def test_empty_source_stop(self):
        with self.assertRaises(SourceStop):fit_all_edges({})
if __name__=="__main__":unittest.main()
