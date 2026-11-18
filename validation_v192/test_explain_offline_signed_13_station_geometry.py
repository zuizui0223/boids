import math
import unittest
import numpy as np
from validation_v192.explain_offline_signed_13_station_geometry import (
 RIDGE_ALPHA,leave_one_station_out,predict_ridge_train_only,geometrical_descriptives
)
class StationGeometryOnly(unittest.TestCase):
    def test_fixed_ridge_alpha_and_fold_heldout_target_not_used(self):
        self.assertEqual(RIDGE_ALPHA,1.0)
        x=np.column_stack((np.linspace(-2,2,13),np.sin(np.arange(13))))
        y=np.linspace(-.04,.04,13)+np.sin(np.arange(13))*.01
        a=leave_one_station_out(x,y)
        changed=y.copy()
        changed[0]=1e6
        b=leave_one_station_out(x,changed)
        self.assertEqual(a["ridge_station_LOSO_gain_predictions_m2"][0],
                         b["ridge_station_LOSO_gain_predictions_m2"][0])
        self.assertEqual(a["training_only_mean_station_LOSO_gain_predictions_m2"][0],
                         b["training_only_mean_station_LOSO_gain_predictions_m2"][0])
    def test_learnable_synthetic_geography_beats_baseline(self):
        x=np.column_stack((np.linspace(1.0,5.0,13),np.cos(np.arange(13)*.43)))
        y=.02*np.linspace(1.0,5.0,13)+.006*np.cos(np.arange(13)*.43)-.06
        got=leave_one_station_out(x,y)
        self.assertGreater(got["station_LOSO_baseline_minus_geometry_ridge_MSE_gain_m4"],0)
    def test_nonlearnable_constant_zero_gain_no_fake_success(self):
        x=np.column_stack((np.linspace(0,1,13),np.cos(np.arange(13))))
        got=leave_one_station_out(x,np.zeros(13))
        self.assertEqual(got["station_LOSO_baseline_minus_geometry_ridge_MSE_gain_m4"],0.0)
    def test_shape_and_nonfinite_source_stop(self):
        with self.assertRaises(ValueError):
            leave_one_station_out(np.ones((12,2)),np.ones(12))
        with self.assertRaises(ValueError):
            leave_one_station_out(np.full((13,2),np.nan),np.ones(13))
if __name__=="__main__":
    unittest.main()
