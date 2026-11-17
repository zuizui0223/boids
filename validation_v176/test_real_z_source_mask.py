"""No original raster fetched in tests. Known truth masked DEM + isource grid."""
import unittest
import numpy as np
from native_2016_z_source_pixel_audit import (
    finite_valid_z,source_counts,MIN_VALID_CELLS_FOR_TILE,TARGET_TIME_LABEL,
    EXPECTED_TILES
)
class TestPerPixelSurveySource(unittest.TestCase):
    def test_masked_altitudes_are_not_zero_elevations(self):
        z=np.ma.array([[1.,-1.],[0.,1e7]],mask=[[0,1],[0,0]])
        vals,valid=finite_valid_z(z)
        self.assertEqual(int(valid.sum()),2)
        self.assertFalse(valid[0,1])
        self.assertFalse(valid[1,1])
        self.assertTrue(valid[1,0])
    def test_isource_and_z_must_have_original_same_grid(self):
        z=np.ma.array([[1.,2.],[0.,-99.]],mask=[[0,1],[0,0]])
        source=np.ma.array([[0.,0.],[1.,-32768.]])
        q=source_counts(z,source)
        self.assertEqual(q["original_native_grid_cells_total"],4)
        self.assertEqual(q["native_2016_time_label_z_nonfill_finite_cells"],3)
        self.assertEqual(q["native_2016_valid_z_AND_source_code_cells"],2)
        self.assertEqual(q["source_file_index_counts_in_valid_z"],{"0":1,"1":1})
    def test_mismatched_native_survey_grids_must_fail(self):
        with self.assertRaises(AssertionError):
            source_counts(np.zeros((2,3)),np.zeros((3,2)))
    def test_source_threshold_and_annual_time_label_fixed(self):
        self.assertEqual(MIN_VALID_CELLS_FOR_TILE,1000)
        self.assertEqual(TARGET_TIME_LABEL,"2016-01-01")
        self.assertEqual(EXPECTED_TILES,10)
if __name__=="__main__":
    unittest.main()
