import unittest,urllib.parse
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from validation_v203.original_BAW_WCS_2018_2019_NL_topography_Vlieland_ROI import (
 COVERS,fixed_roi,make_native_original_WCS_ROI_request,fixed_native_WCS_original_request,
 parse_original_NL_grid
)
class OriginalWCS2SourceOnly(unittest.TestCase):
    def test_original_2018_and_2019_WCS_ids_and_exact_same_bbox(self):
        self.assertEqual(set(COVERS),{"2018","2019"})
        roi=fixed_roi()
        self.assertAlmostEqual(roi[2]-roi[0],10000)
        for y in COVERS:
            u=make_native_original_WCS_ROI_request(y)
            self.assertTrue(fixed_native_WCS_original_request(u))
            q=urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query)
            self.assertEqual(len([a for a,b in q if a=="subset"]),2)
        with self.assertRaises(ValueError):
            make_native_original_WCS_ROI_request("2020")
    def test_original_tiff_synthetic_native_meta_and_nodata_mask(self):
        minx,miny,maxx,maxy=fixed_roi()
        data=np.full((100,100),1.5,dtype="float32")
        data[0,:]=9999
        with MemoryFile() as m:
            with m.open(driver="GTiff",height=100,width=100,count=1,
                dtype="float32",crs="EPSG:25832",
                transform=from_origin(minx,maxy,100,100),nodata=9999) as dst:
                dst.write(data,1)
            raw=m.read()
        stat,valid,arr,transform=parse_original_NL_grid(raw)
        self.assertEqual(stat["n_native_total_raster_cells"],10000)
        self.assertEqual(stat["n_plausible_numeric_topography_pixels_NOT_surveyday_calibrated"],9900)
        self.assertEqual(stat["plausible_numeric_topography_native_median"],1.5)
        self.assertEqual(int(valid.sum()),9900)
    def test_wrong_native_horizontal_CRS_stops(self):
        minx,miny,maxx,maxy=fixed_roi()
        with MemoryFile() as m:
            with m.open(driver="GTiff",height=100,width=100,count=1,
                dtype="float32",crs="EPSG:4326",
                transform=from_origin(minx,maxy,100,100)) as dst:
                dst.write(np.ones((100,100),dtype="float32"),1)
            raw=m.read()
        with self.assertRaisesRegex(ValueError,"CRS"):
            parse_original_NL_grid(raw)
if __name__=="__main__":
    unittest.main()
