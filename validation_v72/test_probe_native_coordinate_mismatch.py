"""v72D source coordinate drift diagnostics known-truth, no ecological inference."""
import unittest
import numpy as np
from probe_native_coordinate_mismatch import diagnostic,geo_valid,quantile
from native_monthly_exposure_source import native_readme_meaning

class PostFailureNativeGridDiagnostics(unittest.TestCase):
    def src(self,*,shift_m=0,missing=False):
        lat=np.array([[53.44,53.45,53.47],
                      [53.43,53.46,53.48]],float)
        lon=np.array([[5.76,5.8,6.2],
                      [5.74,5.9,6.21]],float)
        lat=lat+shift_m/111000.
        if missing:lat[0,0]=np.nan
        return lat,lon,np.ones_like(lat)

    def test_original_tiny_shift_still_does_not_rescue_exact_v72_gate(self):
        m=native_readme_meaning(b"time_expo: modeled percentage of exposed time\n")
        r=diagnostic(self.src(),self.src(shift_m=2),m)
        self.assertEqual(r["frozen_v72_strict_source_admission_status"],
                         "STILL_NOT_ADMITTED_V72_STRICT_SAME_GRID_FAILURE")
        self.assertGreater(r["original_both_months_same_index_displacement_m"]["median"],1)
        self.assertLess(r["original_both_months_same_index_displacement_m"]["median"],10)

    def test_missing_grid_cells_do_not_appear_as_coordinate_movement(self):
        m=native_readme_meaning(b"time_expo: modeled percentage of exposed time\n")
        r=diagnostic(self.src(),self.src(missing=True),m)
        self.assertEqual(r["one_year_only_native_geo_cells"],1)
        self.assertEqual(r["both_original_months_degree_valid_same_array_indices"],5)
        self.assertAlmostEqual(r["original_both_months_same_index_displacement_m"]["median"],0)
        self.assertFalse(r["exact_lat_lon_all_native_array_indices_equal_unmodified"])

    def test_identical_original_native_grid_reports_requires_full_gate(self):
        m=native_readme_meaning(b"README exposure not documented")
        r=diagnostic(self.src(),self.src(),m)
        self.assertTrue(r["exact_lat_lon_all_native_array_indices_equal_unmodified"])
        self.assertEqual(r["frozen_v72_strict_source_admission_status"],
                         "STRICT_SAME_GRID_PASS_REQUIRES_SEPARATE_V72_FULL_GATE")
        self.assertTrue(r["never_fits_wild_bird_GPS_or_interpolates_source_rasters"])

if __name__=="__main__":unittest.main()
