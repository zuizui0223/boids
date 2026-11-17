"""Known-truth original 20m tile source geometry and 2016 time index fixtures.

No biological GPS locations or original bathymetric values are loaded here.
"""
import unittest
import numpy as np

from real_GPS_to_2016_DEM_source_gate import (
    nearest_index,source_frame_metadata,EXPECTED_N_TILES,EXPECTED_COVERED_CELLS,
    MIN_SOURCE_BINS_FOR_ADMISSION,EXPECTED_PREVIOUS_BINS,
    EXPECTED_GRID_SHAPE
)

class TestOriginalHistoricalGeoGate(unittest.TestCase):
    def test_genuine_native_20m_centers_and_no_interpolation(self):
        centers=np.array([120010.,120030.,120050.,120070.])
        q=np.array([120010.,120040.,120061.,119990.,120090.,np.nan])
        inds,good=nearest_index(centers,q)
        self.assertEqual(good.tolist(),[True,True,True,False,False,False])
        self.assertEqual(inds[:3].tolist(),[0,2,3])
    def test_descending_native_projected_axis(self):
        centers=np.array([590050.,590030.,590010.])
        inds,good=nearest_index(centers,np.array([590047.,590018.,590074.]))
        self.assertEqual(inds.tolist(),[0,2,0])
        self.assertEqual(good.tolist(),[True,True,False])
    def test_bad_spacing_must_stop(self):
        with self.assertRaises(AssertionError):
            nearest_index(np.array([0.,21.,42.]),np.array([20.]))
    def test_actual_2016_source_index_must_match_snapshot(self):
        time={"status":"REAL_NATIVE_TIME_COORDINATES_VERIFIED",
              "original_indices_for_2016_native_time_label":[2],
              "native_time_coordinate_labels_not_proven_field_days":[
                 "2010-01-01","2013-01-01","2016-01-01"]}
        z={"status":"REAL_2016_NATIVE_LAYER_HAS_NONFILL_Z_SUPPORT",
           "original_2016_native_TIME_index":2,
           "native_2016_grid_shape_y_x":list(EXPECTED_GRID_SHAPE)}
        self.assertEqual(source_frame_metadata(time,z),2)
        z["original_2016_native_TIME_index"]=1
        with self.assertRaises(AssertionError):
            source_frame_metadata(time,z)
    def test_source_free_nonzero_is_not_missing(self):
        z=np.ma.asarray([[0.0,-.3],[np.nan,1.0]])
        self.assertEqual(int(np.isfinite(z).sum()),3)
        self.assertEqual(EXPECTED_N_TILES,10)
        self.assertEqual(EXPECTED_COVERED_CELLS,1881902)
        self.assertEqual(EXPECTED_PREVIOUS_BINS[2019],125241)
        self.assertEqual(MIN_SOURCE_BINS_FOR_ADMISSION[2018],20000)
if __name__=="__main__":
    unittest.main()
