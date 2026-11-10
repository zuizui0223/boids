"""v122 original RWS modelled dry-duration QA synthetic tests only, not real historical ecological data."""
import unittest
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import original_RWS_2016_2021_Oosterschelde_drying_maps as m

class OriginalRWSModelledDryDurationNativeTruth(unittest.TestCase):
    def test_exact_authentic_pub_native_ecotope_years_fixed(self):
        self.assertEqual(set(m.SOURCE_FILES),{'2016','2021'})
        self.assertEqual(m.FIXED_NATIVE_5M_CENTERS,441)
        self.assertIn('edvd_os_2021.tif',m.SOURCE_FILES['2021'])
        self.assertIn('edvd_os_2016.tif',m.SOURCE_FILES['2016'])
        with self.assertRaisesRegex(ValueError,'NOT_FROZEN_ORIGINAL'):
            m.authentic_source_file('edvd_os_2001.tif','no',5000)
    def test_nearest_native_RWS_pixel_retains_zero_negative_missing_and_grid_mask(self):
        data=np.zeros((60,60),dtype='float32')
        data[1,1]=-12;data[2,2]=45;data[3,3]=-9999.
        affine=from_origin(40000,410000,5,5)
        profile={'driver':'GTiff','count':1,'width':60,'height':60,
            'dtype':'float32','crs':'EPSG:28992','nodata':-9999.,
            'transform':affine}
        with MemoryFile() as mem:
            with mem.open(**profile) as dst:dst.write(data,1)
            with mem.open() as ds:
                x=np.full(441,40080.,dtype=float)
                y=np.full(441,409920.,dtype=float)
                x[0],y[0]=40007,409992
                x[1],y[1]=40012,409987
                x[2],y[2]=40017,409982
                x[3],y[3]=39999,409990
                vals,q=m.original_native_raster_at_2019_fixed_centers(ds,x,y)
                self.assertEqual(len(vals),441)
                self.assertEqual(vals[0],-12)
                self.assertEqual(vals[1],45)
                self.assertTrue(np.isnan(vals[2]))
                self.assertTrue(np.isnan(vals[3]))
                self.assertEqual(vals[4],0)
                self.assertEqual(q['source_outside_native_footprint_n'],1)
    def test_raw_numeric_profile_does_not_assume_percentages(self):
        x=m.public_source_native_value_profile(np.array([0,1,2,50,np.nan]))
        self.assertEqual(x['n_original_valid_source_pixels'],4)
        self.assertIn('UNVERIFIED',x['source_numeric_unit'])
        self.assertEqual(x['original_raw_source_numeric_minmax'],[0,50])
    def test_real_units_must_derive_from_publisher_not_name(self):
        self.assertEqual(m.SOURCE_YEAR_TEMPORAL_CAVEAT,
            '2016 and 2021 ecotope models, not 2020 bird observation')
        self.assertEqual(m.MIN_YEAR_PAIRED_FRACTION,.9)
        self.assertIn('NOT the actual May',m.__doc__)
if __name__=='__main__':unittest.main()
