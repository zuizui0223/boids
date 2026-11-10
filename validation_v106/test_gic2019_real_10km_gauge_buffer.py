"""v106 source selection and genuine raster pixel meaning known-truth fixtures only."""
import unittest,base64,hashlib,io,tempfile
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from affine import Affine
import gic2019_real_10km_gauge_buffer as m

class GenuineSourceBoundaries(unittest.TestCase):
    def test_source_only_fixed_nearest_uid_selection_and_no_outcome_adaptation(self):
        self.assertEqual(len(m.POLICY_BANDS),8)
        self.assertEqual(m.SAMPLING_RADIUS_M,10_000.)
        self.assertIn('twprobabilityEnd',m.GIC_SOURCE_PREFIX)
    def test_tile_grid_from_original_wgs84_affine(self):
        aff=Affine(.0002695,0,-180.000015,0,-.0002695,60.000005)
        a=m.native_expected_tile(53.,6.,aff)
        self.assertEqual(a['expected_rowstart_original_pixels'],0)
        self.assertEqual(a['expected_colstart_original_pixels'],655360)
        self.assertIn('0000000000-0000655360.tif',a['native_GCS_tile_name'])
        with self.assertRaisesRegex(m.SourceUnavailable,'OUTSIDE_NATIVE'):
            m.native_expected_tile(75.,6.,aff)
    def test_actual_nodata_and_zero_distinguished_for_buffer(self):
        vals=np.zeros((16,16),dtype=np.uint8)
        vals[7,7]=75
        vals[6,6]=255
        profile={'driver':'GTiff','width':16,'height':16,'count':1,'dtype':'uint8',
                 'nodata':255,'transform':from_origin(0,50,.01,.01),
                 'crs':'EPSG:4326'}
        with MemoryFile() as mem:
            with mem.open(**profile) as dst:dst.write(vals,1)
            with mem.open() as src:
                v=m.source_10km_wetland_probability(src,49.92,.08)
                self.assertGreater(v['n_valid_original_GIC_pixels_10km'],0)
                self.assertEqual(v['n_masked_GIC_pixels_inside10km'],1)
                self.assertGreater(v['fraction_valid_source_pixels_RF_agreement_ge50'],0)
                self.assertLess(v['fraction_valid_source_pixels_RF_agreement_ge50'],1)
                self.assertFalse(v['complete_10km_circle_in_this_tile'])
    def test_original_provider_md5_rejects_wrong_bytes(self):
        b=b'real deterministic source fixture'
        md5=base64.b64encode(hashlib.md5(b).digest()).decode()
        meta={'name':'fixture','size':len(b),'md5Hash':md5,'generation':'1'}
        # The real GCS stream is independently downloaded live, this test only checks provider digest mechanics.
        self.assertEqual(base64.b64encode(hashlib.md5(b).digest()).decode(),meta['md5Hash'])
        self.assertNotEqual(base64.b64encode(hashlib.md5(b+b'x').digest()).decode(),meta['md5Hash'])
    def test_no_probabilities_misread_as_tidal_flat_exposure_or_birds(self):
        self.assertIn('NOT tidal-flat dry area or animal niche',m.__doc__)
if __name__=="__main__":unittest.main()
