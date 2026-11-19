import json,unittest
from validation_v197.true_BAW_WMS_24_timestamp_NoData_source import (
 FIXED_HOURS_UTC,FIXED_DAYS,feature_query,utc_timestamp,
 classify_original_Wasserstand_response
)
class FrozenNativeWMSQA(unittest.TestCase):
    def test_frozen_24_and_original_GET_BBOX_axis(self):
        self.assertEqual(len(FIXED_HOURS_UTC)*len(FIXED_DAYS)*3,24)
        self.assertEqual(FIXED_HOURS_UTC,("00","06","12","18"))
        self.assertEqual(utc_timestamp("2019-06-01","12"),"2019-06-01T12:00:00.000Z")
        u=feature_query("2019",5.09,53.3,utc_timestamp("2019-06-01","06"))
        self.assertIn("GetFeatureInfo",u)
        self.assertIn("sea_surface_height_2d_2019_NL",u)
        with self.assertRaises(ValueError):
            feature_query("2019",5.09,53.3,"2019-06-10T06:00:00.000Z")
    def test_original_Wasserstand_extreme_float_is_not_water(self):
        d={"type":"FeatureCollection","features":[{
          "properties":{"Wasserstand":9.999999848243207E30}}]}
        label,value=classify_original_Wasserstand_response(d)
        self.assertEqual(label,"EXTREME_NODATA_SENTINEL_CANDIDATE")
        self.assertIsNone(value)
    def test_2019_valid_negative_model_value_is_not_NAP_proven(self):
        d={"type":"FeatureCollection","features":[{
          "properties":{"Wasserstand":-0.9412793517112732}}]}
        label,value=classify_original_Wasserstand_response(d)
        self.assertEqual(label,"PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED")
        self.assertLess(value,0)
    def test_native_unknown_no_features_and_bool_are_rejected(self):
        for d in (
          {"type":"FeatureCollection","features":[]},
          {"type":"FeatureCollection","features":[{"properties":{"Wasserstand":True}}]},
          {"type":"FeatureCollection","features":[{"properties":{"Wasserstand":0.1,"other":42}}]},
        ):
            label,val=classify_original_Wasserstand_response(d)
            self.assertTrue(label.startswith("REJECTED"))
            self.assertIsNone(val)
if __name__=="__main__":
    unittest.main()
