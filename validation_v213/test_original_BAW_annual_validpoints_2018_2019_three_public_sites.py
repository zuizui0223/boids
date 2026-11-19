import unittest
import urllib.parse
import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from validation_v213.original_BAW_annual_validpoints_2018_2019_three_public_sites import (
    PUBLIC_SITE_RD,HALF_KM,FROZEN_VALID_COUNTS,DESCRIBE_SHA,
    frozen_public_ROI,source_annual_WCS_GetCoverage,
    exact_frozen_source_WCS_query,summarize_native_annual_count_TIFF
)

CAP2018="https://coast.baw.de/geoserver/TrilaWatt_Hydrodynamik_2018/ows?service=WCS&version=2.0.1&request=GetCapabilities"

class OriginalBAWAnnualValidCountNotFloodFraction(unittest.TestCase):
    def test_site_year_scope_and_predeclared_public_half_kilometer_ROIs(self):
        self.assertEqual(PUBLIC_SITE_RD,{
           "VlielandHaven":(135280,590000),
           "WestTerschelling":(143870,597420),
           "Wierumergronden":(192882,614562)})
        self.assertEqual(len(PUBLIC_SITE_RD)*len(FROZEN_VALID_COUNTS),6)
        self.assertEqual(HALF_KM,500)
        self.assertEqual(len(DESCRIBE_SHA),2)
        for name in PUBLIC_SITE_RD:
            roi=frozen_public_ROI(name)
            self.assertAlmostEqual(roi[2]-roi[0],1000)
            self.assertAlmostEqual(roi[3]-roi[1],1000)
        with self.assertRaises(ValueError):
            frozen_public_ROI("unverified_site")

    def test_only_verified_native_WCS_GetCoverage_and_exact_subset_axes(self):
        uri=source_annual_WCS_GetCoverage("2018","VlielandHaven",CAP2018)
        self.assertTrue(exact_frozen_source_WCS_query(
           uri,"2018","VlielandHaven",CAP2018))
        p=urllib.parse.urlsplit(uri)
        q=urllib.parse.parse_qsl(p.query)
        self.assertEqual(dict(q)["coverageId"],FROZEN_VALID_COUNTS["2018"])
        self.assertEqual(len([v for k,v in q if k=="subset"]),2)
        self.assertIn(("format","image/tiff"),q)
        self.assertIn("GetCoverage",uri)
        with self.assertRaises(ValueError):
            source_annual_WCS_GetCoverage("2019","VlielandHaven",CAP2018)
        with self.assertRaises(ValueError):
            source_annual_WCS_GetCoverage("2018","VlielandHaven",CAP2018.replace(
                "coast.baw.de","evil.example"))

    def test_synthetic_native_20m_valid_count_mask_and_no_inundation_inference(self):
        roi=frozen_public_ROI("VlielandHaven")
        values=np.full((50,50),26000,dtype="float32")
        values[0,:]=-9999
        values[1,:]=0
        with MemoryFile() as mf:
            with mf.open(driver="GTiff",height=50,width=50,count=1,
                dtype="float32",crs="EPSG:25832",
                transform=from_origin(roi[0],roi[3],20,20),nodata=-9999) as d:
                d.write(values,1)
            raw=mf.read()
        stat,valid,actual,transform=summarize_native_annual_count_TIFF(raw,"VlielandHaven")
        self.assertEqual(stat["n_original_native_numeric_valid_sample_count_pixels"],2450)
        self.assertEqual(stat["n_original_native_zero_annual_valid_count_pixels"],50)
        self.assertEqual(stat["source_valid_count_median"],26000)
        self.assertEqual(stat["source_valid_count_max"],26000)
        self.assertTrue(stat["SOURCE_DOES_NOT_DEFINE_A_365DAY_WET_TIME_DENOMINATOR"])
        self.assertEqual(int(valid.sum()),2450)

    def test_fractional_source_values_cannot_be_mislabeled_a_count(self):
        roi=frozen_public_ROI("WestTerschelling")
        values=np.full((50,50),12.6,dtype="float32")
        with MemoryFile() as mf:
            with mf.open(driver="GTiff",height=50,width=50,count=1,
                dtype="float32",crs="EPSG:25832",
                transform=from_origin(roi[0],roi[3],20,20)) as d:
                d.write(values,1)
            raw=mf.read()
        with self.assertRaisesRegex(ValueError,"NONINTEGER"):
            summarize_native_annual_count_TIFF(raw,"WestTerschelling")
if __name__=="__main__":
    unittest.main()
