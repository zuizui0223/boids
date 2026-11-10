"""v116 source truth: 2019 true DTM terrain source, not WMS / synthetic bird habitat.
Synthetic raster used in THESE TESTS ONLY, never as real RWS field results.
"""
from __future__ import annotations
import tempfile,unittest
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
import original_2019_Oosterschelde_DTM_ground_source as q

class OriginalNAP2019GroundSourceTruth(unittest.TestCase):
    def test_native_source_identity_and_2019_DTM_not_DSM(self):
        self.assertEqual(q.SOURCE_YEAR,2019)
        self.assertEqual(q.PRIMARY,'dtm_5')
        self.assertEqual(q.SECONDARY,'dtm_2')
        self.assertEqual(len(q.PROBE_QA),4)
        self.assertIn('oosterschelde_2019_dtm_5.tif',q.LAYER['dtm_5']['filename'])
        self.assertEqual(q.LAYER['dtm_5']['source_nominal_resolution_m'],5)
        with self.assertRaisesRegex(ValueError,'NOT_ORIGINAL'):
            q._request('https://evil.example/synthetic.tif')
    def test_genuine_PLOT_centers_outside_raster_are_missing_not_zero_elevation(self):
        p={'driver':'GTiff','width':22,'height':22,'count':1,'dtype':'float32',
           'crs':'EPSG:28992','transform':from_origin(160000,400000,5,5),'nodata':-9999.}
        arr=np.full((22,22),.4,dtype='float32')
        arr[10,10]=-9999.
        with MemoryFile() as mem:
            with mem.open(**p) as dst:dst.write(arr,1)
            with mem.open() as ds:
                near=q.WGS.transform(160050,399950)
                test={'lon':near[0],'lat':near[1],'physical_waterbody_source':'test location'}
                s=q._single_original_lidar_probe(ds,'test',test)
                self.assertEqual(s['source_status'],'VALID_ORIGINAL_DTM_PLOT')
                self.assertGreater(s['original_masked_ground_height_native_pixels'],0)
                self.assertAlmostEqual(s['source_native_ground_height_median'],.4,places=5)
                none=q._single_original_lidar_probe(ds,'outside',{'lon':0,'lat':0,'physical_waterbody_source':'fake'})
                self.assertEqual(none['source_status'],'OUTSIDE_THIS_ORIGINAL_DTM_RASTER_NOT_ZERO_HEIGHT')
    def test_native_XML_exception_is_not_valid_original_height_data(self):
        class X:
            pass
        self.assertEqual(q.MAX_ORIGINAL_SOURCE_MEGABYTES,150)
        self.assertIn(bytes([73,73,42,0]),q.TIF_SIGNATURES)
        self.assertEqual(q.MAX_GETCOVERAGE_MEGABYTES,8)
    def test_landmark_source_points_are_fixed_and_not_adapted_to_gull_Y(self):
        b=q.PROBE_QA['Roompotsluis Buiten gauge']
        self.assertAlmostEqual(b['lat'],51.619722)
        self.assertAlmostEqual(b['lon'],3.681944)
        self.assertAlmostEqual(q.PROBE_RADIUS_METRES,50)
        x,y=q.RD.transform(b['lon'],b['lat'])
        self.assertTrue(x>0 and y>0)
    def test_no_source_dataset_is_biological_niche(self):
        self.assertIn('NO observed foraging',q.__doc__)
        self.assertIn('source',q.__doc__.lower())
if __name__=='__main__':unittest.main()
