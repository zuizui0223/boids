"""v105 known truths on a tiny synthetic GeoTIFF: original real download tested only live in CI."""
import unittest,io,tempfile
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import verify_original_GIC2019_first_tile_pixels as q

class RasterGeoreferenceTruth(unittest.TestCase):
    def _source(self,nodata=255):
        arr=np.zeros((8,8),dtype=np.uint8)
        arr[0,1]=75
        arr[0,2]=255
        profile={'driver':'GTiff','width':8,'height':8,'count':1,'dtype':'uint8',
                 'nodata':nodata,'transform':from_origin(0,50,1,1),'crs':'EPSG:4326'}
        m=MemoryFile()
        with m.open(**profile) as ds:ds.write(arr,1)
        return m
    def test_original_publisher_fixed_identity(self):
        self.assertEqual(q.SOURCE_SIZE_BYTES,53506115)
        self.assertIn('twprobabilityEnd',q.NATIVE_PATH)
        self.assertIn('gic-archive',q.URL)
    def test_real_geo_position_only_inside_selected_tile(self):
        with self._source().open() as ds:
            rows=q._gauge_points_in_this_one_tile(ds,[
                {'uid':3,'latitude':49.5,'longitude_signed':1.5},
                {'uid':4,'latitude':49.5,'longitude_signed':2.5},
                {'uid':5,'latitude':20,'longitude_signed':1.5}])
            self.assertEqual(len(rows),2)
            self.assertEqual(rows[0]['pixel_tidal_wetland_RF_agreement_0_to_100'],75)
            self.assertIsNone(rows[1]['pixel_tidal_wetland_RF_agreement_0_to_100'])
            self.assertFalse(rows[1]['valid_source_pixel'])
    def test_zero_is_valid_wetland_probability_not_automatically_nodata(self):
        with self._source().open() as ds:
            z=q._qa_windows(ds)
            self.assertGreater(z[0]['unmasked_pixels'],0)
            self.assertEqual(z[0]['source_valid_min'],0)
            self.assertEqual(z[0]['source_valid_max'],75)
            self.assertEqual(z[0]['n_source_valid_above_50'],1)
    def test_mismatched_tiff_md5_cannot_claim_real_original_download(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,'PROVIDER_SIZE_OR_MD5_MISMATCH'):
                q._fetch_original_geotiff(d+'/wrong.tif',request_fn=lambda url:io.BytesIO(b'fake'))
    def test_distinct_source_dataset_is_tidal_wetlands_not_true_dry_area(self):
        self.assertIn('neither bare tidalflat habitat',q.__doc__)
        self.assertIn('NOT animal time-niche evidence',q.__doc__)
if __name__=='__main__':unittest.main()
