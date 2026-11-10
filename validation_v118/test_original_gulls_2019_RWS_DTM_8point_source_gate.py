"""v118 original 2020 gull genuine z-source eligibility tests ONLY, not simulated animals."""
from __future__ import annotations
import unittest
import numpy as np
from pyproj import Transformer
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import original_gulls_2019_RWS_DTM_8point_source_gate as q

def raster():
    arr=np.zeros((20,20),dtype='float32')
    arr[2,2]=2.5;arr[3,3]=-9999.
    aff=from_origin(36000,406000,5.,5.)
    p={'driver':'GTiff','width':20,'height':20,'count':1,'dtype':'float32',
       'nodata':-9999.,'crs':'EPSG:28992','transform':aff}
    m=MemoryFile()
    with m.open(**p) as ds:ds.write(arr,1)
    return m

class GenuineTerrainNativeSourceTruth(unittest.TestCase):
    def test_exact_original_2019_DTM_SHA_source_and_not_dsm(self):
        self.assertEqual(len(q.KNOWN_GENUINE_2019_RWS_DTM5_SHA),64)
        self.assertEqual(q.KNOWN_SOURCE_DTM5_BYTES,34799884)
        self.assertEqual(q.EXPECTED_GULL_STEPS_COMMON_MAY_JULY,45133)
        self.assertEqual(q.ORIGINAL_GROUND_DTM_RWS_CRS,'EPSG:28992')
    def test_native_zero_z_valid_mask_missing_and_outside_must_not_be_zero(self):
        to_wgs=Transformer.from_crs('EPSG:28992','EPSG:4326',always_xy=True)
        points=[(36012.5,405987.5),(36017.5,405982.5),(36087.5,405912.5),(45000,410000)]
        lon,lat=to_wgs.transform([p[0] for p in points],[p[1] for p in points])
        with raster() as m:
            with m.open() as ds:
                values,qa=q.sample_original_DTM_native_pixels(ds,lat,lon)
        self.assertAlmostEqual(values[0],2.5)
        self.assertTrue(np.isnan(values[1]))
        self.assertTrue(np.isnan(values[3]))
        self.assertAlmostEqual(values[2],0.)
        self.assertEqual(qa['n_native_source_pixel_ground_z_present'],2)
        self.assertEqual(qa['n_original_coordinates_outside_2019_DTM_tile'],1)
        self.assertEqual(qa['n_original_DTM_inside_source_tile_but_lidar_masked'],1)
    def test_deterministic_128_tile_chunk_identical_to_manual_native_pixel_samples(self):
        xy=[(36002.5,405997.5),(36042.5,405957.5),(36012.5,405987.5)]
        lon,lat=Transformer.from_crs('EPSG:28992','EPSG:4326',always_xy=True).transform(
            [x for x,y in xy],[y for x,y in xy])
        with raster() as m:
            with m.open() as ds:
                x,qa=q.sample_original_DTM_native_pixels(ds,lat,lon)
                native=[]
                for pt in xy:
                    r,c=ds.index(*pt)
                    v=ds.read(1,masked=True)
                    native.append(float(v[r,c]) if not np.ma.is_masked(v[r,c]) else np.nan)
        np.testing.assert_allclose(x,native,equal_nan=True)
        self.assertTrue(qa['source_no_interpolated_DTM_values'])
        self.assertEqual(qa['n_exact_original_WGS84_coordinates_processed'],3)
    def test_no_original_2020_GPS_movement_source_selection_adapted(self):
        with self.assertRaisesRegex(ValueError,'45133'):
            q._v115_same_original_move_source_checks([])
        self.assertEqual(q.N_SOURCE_NATIVE_GEO_CHUNK_PIXELS,128)
        self.assertAlmostEqual(q.MIN_SOURCE_COMPLETE_EIGHT_DTM_HEIGHT_RATIO,.90)
    def test_non_source_coords_are_rejected_and_not_invented_DTM(self):
        with raster() as m:
            with m.open() as ds:
                with self.assertRaisesRegex(ValueError,'GEO_COORDINATE_INVALID'):
                    q.sample_original_DTM_native_pixels(ds,[np.nan],[3.6])
    def test_no_tide_bird_effect_is_claimed_by_geometry_only(self):
        self.assertIn('coverage accounting ONLY',q.__doc__)
        self.assertIn('not actual 2020 dry-flat time',q.__doc__.lower())
if __name__=='__main__':unittest.main()
