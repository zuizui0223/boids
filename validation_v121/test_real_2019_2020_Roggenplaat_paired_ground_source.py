"""v121 synthetic known-truth unit tests. No synthetic source becomes field result."""
import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import real_2019_2020_Roggenplaat_paired_ground_source as q

class OriginalRoggenplaatPairedTerrainSourceTruth(unittest.TestCase):
    def test_source_URL_exact_2020_RWS_DTM_ground_not_DSM(self):
        self.assertEqual(q.SOURCE_YEAR_2020,2020)
        self.assertIn('roggenplaat_2020_dtm_2m.tif',q.SOURCE_2020_URL)
        self.assertNotIn('dsm',q.SOURCE_2020_URL.lower())
        self.assertEqual(q.SOURCE_2020_PRODUCT_START,'2020-10-31')
        self.assertEqual(q.FIXED_NATIVE_5M_CENTERS,441)
        self.assertEqual(q.MIN_PAIRED_VALID_FRACTION,.9)
    def test_true_original_2020_DTM_native_zero_and_missing_never_interpolated(self):
        a=np.full((55,55),-.25,dtype=np.float32)
        a[4,4]=0.
        a[8,8]=-9999
        profile={'driver':'GTiff','count':1,'width':55,'height':55,
           'dtype':'float32','nodata':-9999,'crs':'EPSG:28992',
           'transform':from_origin(100000,400000,2,2)}
        with MemoryFile() as m:
            with m.open(**profile) as ds:ds.write(a,1)
            with m.open() as ds:
                X=np.repeat(100010.,q.FIXED_NATIVE_5M_CENTERS)
                Y=np.repeat(399990.,q.FIXED_NATIVE_5M_CENTERS)
                X[0]=100009.;Y[0]=399991.
                X[1]=100017.;Y[1]=399983.
                X[2]=99999.;Y[2]=399990.
                values,proof=q.nearest_original_2020_DTM_at_fixed_2019_centers(ds,X,Y)
                self.assertEqual(len(values),441)
                self.assertEqual(values[0],0.)
                self.assertTrue(np.isnan(values[1]))
                self.assertTrue(np.isnan(values[2]))
                self.assertTrue(np.isfinite(values[3]))
                self.assertEqual(proof['original_2020_DTM_valid_at_exact_2019_fixed_cell_centres'],439)
    def test_paired_ground_and_stage_monotonic_no_bird_outcome(self):
        z19=np.full(441,-.1);z20=np.full(441,.1)
        t0=datetime(2020,5,1,tzinfo=timezone.utc)
        stages={t0+timedelta(hours=i):0. for i in range(8)}
        with patch.object(q,'elevation',side_effect=lambda observer,t:10. if t.hour%2==0 else -10.):
            result=q.true_ground_change_and_gauge_screen(z19,z20,stages,51.66,3.79)
        self.assertEqual(result['status'],'2020_ORIGINAL_RWS_DTM_GROUND_CHANGE_AT_FIXED_2019_CELL_CENTRES')
        self.assertAlmostEqual(result['2020_minus_2019_native_ground_z_diff_mean_m'],.2)
        sc=result['same_fixed_real_2020_RWS_measured_gauge_stage_counterfactual_across_two_DTM_survey_eras']
        self.assertEqual(sc['0.0']['2019_ground_fraction_above_same_2020_gauge_stage_mean'],0.)
        self.assertEqual(sc['0.0']['2020_october_ground_fraction_above_same_earlier_2020_gauge_stage_mean'],1.)
        self.assertTrue(sc['0.2']['2020_october_ground_fraction_above_same_earlier_2020_gauge_stage_mean']<=1.)
        self.assertTrue(result['NO_actual_2020_bird_forage_activity_true_local_h_x_t'])
    def test_pair_source_coverage_source_stop_not_zero_ground(self):
        z19=np.full(441,-.1);z20=np.full(441,np.nan)
        stages={datetime(2020,5,1,tzinfo=timezone.utc):0.}
        r=q.true_ground_change_and_gauge_screen(z19,z20,stages,51.6,3.7)
        self.assertEqual(r['status'],'NOT_ESTIMATED_PAIRED_SOURCE_GEOGRAPHY_LT90PCT')
        self.assertEqual(r['n_both_native_years_valid'],0)
    def test_no_local_tide_or_animal_claim(self):
        self.assertIn('AFTER 2020 May',q.__doc__)
        self.assertIn('No bird inference',q.__doc__)
        self.assertEqual(len(q.SHA_2019),64)
if __name__=='__main__':unittest.main()
