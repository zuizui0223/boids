import unittest
import numpy as np
from rasterio.transform import from_origin
from pyproj import Transformer
from validation_v214.BAW_native_annual_count_histogram_vs_timed_WMS_availability import (
    PUBLIC_SITE_RD,FROZEN_NUMERIC_PIXEL_N,FROZEN_TIFF_SHA,
    EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR,
    source_native_annual_histogram,original_WMS_source_availability_by_site,
    compare_products
)
from validation_v210.sha_verified_v209_source_WMS_selection_bias import (
    EXPECTED_SOURCE_GROUP_NODATA
)

class NativeSourceAnnualVsTimeDimension(unittest.TestCase):
    def test_frozen_six_annual_original_binary_SHA_receipts_and_sites(self):
        self.assertEqual(set(FROZEN_TIFF_SHA),{"2018","2019"})
        self.assertEqual(set(PUBLIC_SITE_RD),{"VlielandHaven","WestTerschelling","Wierumergronden"})
        self.assertEqual(FROZEN_NUMERIC_PIXEL_N,
            {"VlielandHaven":1621,"WestTerschelling":1283,"Wierumergronden":2500})
        self.assertEqual(EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR,26281)
        self.assertTrue(all(len(value)==64 for r in FROZEN_TIFF_SHA.values() for value in r.values()))

    def test_full_native_count_pixel_distribution_and_centre_are_separate(self):
        e,n=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
            *PUBLIC_SITE_RD["VlielandHaven"])
        tr=from_origin(e-500,n+500,20,20)
        source=np.full((50,50),26281,dtype=float)
        valid=np.ones((50,50),dtype=bool)
        source[0,0]=21000
        source[0,1]=0
        source[0,2]=25000
        valid[0,3]=False
        out=source_native_annual_histogram(valid,source,tr,"VlielandHaven")
        self.assertEqual(out["n_native_pixels_with_annual_count_value"],2499)
        self.assertEqual(out["n_native_count_pixels_below_26281"],3)
        self.assertEqual(out["n_native_count_pixels_equal_26281"],2496)
        self.assertEqual(out["n_native_count_pixels_zero"],1)
        self.assertEqual(out["n_distinct_source_annual_count_values"],4)
        self.assertTrue(out["native_public_reference_centre_pixel_has_annual_count"])
        self.assertEqual(out["native_public_reference_centre_pixel_annual_count_value"],26281)
        self.assertTrue(out["native_product_temporal_sampling_denominator_UNVERIFIED"])

    def test_original_model_24_by_site_source_not_annual_pixel_fraction(self):
        groups={}
        for k,s in EXPECTED_SOURCE_GROUP_NODATA.items():
            groups[k]={"source_RWS_levels_by_original_model_validity_class":{
                "n_original_WMS_plausible_source_candidates":6-s,
                "n_original_WMS_extreme_NoData_candidates":s}}
        data={"all_12_official_model_validity_vs_measured_tide_level_cohorts":groups}
        wms=original_WMS_source_availability_by_site(data)
        self.assertEqual(wms["VlielandHaven"]["n_original_WMS_plausible_24"],11)
        self.assertEqual(wms["WestTerschelling"]["n_original_WMS_plausible_24"],15)
        self.assertEqual(wms["Wierumergronden"]["n_original_WMS_plausible_24"],24)
        self.assertEqual(sum(x["n_original_WMS_plausible_24"] for x in wms.values()),50)
        annual={y:{site:{"native_spatial_count_value_fraction":{
             "VlielandHaven":.6484,"WestTerschelling":.5132,"Wierumergronden":1.0}[site]}
          for site in PUBLIC_SITE_RD} for y in ("2018","2019")}
        paired=compare_products(None,annual,wms)
        self.assertGreater(paired["three_published_sites"]["VlielandHaven"][
            "native_annual_WCS_mean_2018_2019_spatial_count_presence_fraction"],
            paired["three_published_sites"]["WestTerschelling"][
            "native_annual_WCS_mean_2018_2019_spatial_count_presence_fraction"])
        self.assertLess(paired["three_published_sites"]["VlielandHaven"][
            "separate_20min_WMS_public_reference_24time_numeric_reply_fraction"],
            paired["three_published_sites"]["WestTerschelling"][
            "separate_20min_WMS_public_reference_24time_numeric_reply_fraction"])
        self.assertTrue(paired["different_model_products_spatial_cell_vs_temporal_sample"])

    def test_negative_noninteger_native_source_and_no_annual_time_division(self):
        e,n=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
            *PUBLIC_SITE_RD["Wierumergronden"])
        arr=np.full((50,50),26281,dtype=float)
        arr[0,0]=2.3
        with self.assertRaisesRegex(ValueError,"INVALID_NATIVE_ANNUAL_COUNT_PIXEL_VALUES"):
            source_native_annual_histogram(np.ones((50,50),bool),arr,
                from_origin(e-500,n+500,20,20),"Wierumergronden")

if __name__=="__main__":
    unittest.main()
