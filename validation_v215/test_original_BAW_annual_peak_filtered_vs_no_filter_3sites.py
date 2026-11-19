import unittest
import urllib.parse
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from validation_v215.original_BAW_annual_peak_filtered_vs_no_filter_3sites import (
 FROZEN,PUBLIC_SITE_RD,frozen_public_ROI,
 frozen_source_coverage_url,native_annual_peak_mask,compare_masks
)

CAP_2018="https://coast.baw.de/geoserver/TrilaWatt_Hydrodynamik_2018/ows?service=WCS&version=2.0.1&request=GetCapabilities"

def sample_tiff(site,data,nodata=-9999):
    box=frozen_public_ROI(site)
    with MemoryFile() as m:
        with m.open(driver="GTiff",height=50,width=50,count=1,
            dtype="float32",crs="EPSG:25832",
            transform=from_origin(box[0],box[3],20,20),nodata=nodata) as d:
            d.write(data,1)
        return m.read()

class FrozenBAWAnnualPeaksFilteredVsNoFilter(unittest.TestCase):
    def test_only_original_annual_peak_two_variants_three_sites(self):
        self.assertEqual(set(FROZEN),{"2018","2019"})
        self.assertEqual(len(PUBLIC_SITE_RD),3)
        for year,variants in FROZEN.items():
            self.assertEqual(set(variants),{"filtered","no_filter"})
            self.assertTrue(variants["no_filter"].endswith("_no_filter"))
        for site in PUBLIC_SITE_RD:
            bbox=frozen_public_ROI(site)
            self.assertAlmostEqual(bbox[2]-bbox[0],1000.0)
            self.assertAlmostEqual(bbox[3]-bbox[1],1000.0)

    def test_original_only_this_exact_2018_source_coverageid_and_no_tide_timeseries(self):
        u=frozen_source_coverage_url("2018","VlielandHaven","no_filter",CAP_2018)
        q=urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query)
        self.assertEqual(dict(q)["coverageId"],FROZEN["2018"]["no_filter"])
        self.assertEqual(dict(q)["request"],"GetCoverage")
        self.assertEqual(len([k for k,v in q if k=="subset"]),2)
        self.assertNotIn("GetFeatureInfo",u)
        with self.assertRaises(ValueError):
            frozen_source_coverage_url("2019","VlielandHaven","filtered",CAP_2018)
        with self.assertRaises(ValueError):
            frozen_source_coverage_url("2018","unknown","filtered",CAP_2018)

    def test_original_native_geoTiff_filtered_vs_no_filter_source_mask_counts(self):
        a=np.full((50,50),1.1,dtype="float32")
        b=a.copy()
        a[:5,:]=-9999  # 250 pixels absent in normal year product
        b[:1,:]=-9999  # 50 absent in no_filter year product
        original=(native_annual_peak_mask(sample_tiff("VlielandHaven",a),"VlielandHaven"))
        expanded=(native_annual_peak_mask(sample_tiff("VlielandHaven",b),"VlielandHaven"))
        cross=compare_masks(original,expanded)
        self.assertEqual(cross["n_numeric_filtered_only"],0)
        self.assertEqual(cross["n_numeric_no_filter_only"],200)
        self.assertEqual(cross["n_numeric_both_variants"],2250)
        self.assertEqual(cross["n_numeric_neither_variant"],50)
        self.assertTrue(cross["annual_product_only_not_model_20min_WMS_missing_reason"])

    def test_exact_native_raster_alignment_must_match(self):
        a=np.ones((50,50),dtype=bool)
        t=from_origin(100000,6000000,20,20)
        with self.assertRaisesRegex(ValueError,"ALIGNMENT"):
            compare_masks((a,t,{}),(a,from_origin(100020,6000000,20,20),{}))

    def test_source_extreme_value_is_not_emitted_as_native_height(self):
        a=np.ones((50,50),dtype="float32")
        a[0,0]=9.999999e30
        masked,transform,meta=native_annual_peak_mask(
            sample_tiff("Wierumergronden",a),"Wierumergronden")
        self.assertEqual(meta["n_source_extreme_uninterpretable_pixels"],1)
        self.assertFalse(masked[0,0])
        self.assertEqual(meta["n_original_numeric_candidate_pixels"],2499)
if __name__=="__main__":
    unittest.main()
