import hashlib
import urllib.parse
import unittest
from unittest.mock import patch
from validation_v195.original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
 FIXED_PUBLICATION_RD_POINTS,FIXED_TARGET_UTC,NATIVE_HEIGHT_LAYERS,
 validate_capability_and_layer,make_fixed_feature_request
)
class NativeWMSNumericSourceContract(unittest.TestCase):
    def test_pinned_sites_layer_clock_and_axis_order(self):
        self.assertEqual(len(FIXED_PUBLICATION_RD_POINTS),3)
        self.assertEqual(set(FIXED_TARGET_UTC),{"2018","2019"})
        self.assertEqual(NATIVE_HEIGHT_LAYERS["2018"],"sea_surface_height_2d_2018_NL")
        url,p=make_fixed_feature_request("2018",5.09,53.30,"text/plain")
        self.assertTrue(url.startswith("https://coast.baw.de/"))
        self.assertEqual(p["BBOX"],"53.290000,5.080000,53.310000,5.100000")
        self.assertEqual(p["TIME"],"2018-06-01T12:00:00.000Z")
        self.assertEqual(p["CRS"],"EPSG:4326")
        self.assertEqual(p["I"],"25")
        self.assertEqual(p["J"],"25")
    def test_native_layer_requires_queryable_CRS_time_and_original_SHA(self):
        xml=b'''<?xml version="1.0"?>
        <WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms">
          <Capability><Request><GetFeatureInfo><Format>text/plain</Format></GetFeatureInfo></Request>
          <Layer queryable="1"><CRS>EPSG:4326</CRS><Layer>
           <Name>sea_surface_height_2d_2018_NL</Name>
           <Dimension name="time">2018-01-01T00:00:00Z/2019-01-01T00:00:00Z/PT20M</Dimension>
          </Layer></Layer></Capability>
        </WMS_Capabilities>'''
        name="validation_v195.original_BAW_two_year_NL_WMS_public_stations_featureinfo.FIXED_CAPABILITIES_SHA256"
        with patch.dict(name,{"2018":hashlib.sha256(xml).hexdigest()}):
            got=validate_capability_and_layer(xml,"2018")
            self.assertTrue(got["source_admissible_for_feature_info_probe"])
            self.assertEqual(got["chosen_predeclared_feature_info_format"],"text/plain")
            bad=xml.replace(b'queryable="1"',b'queryable="0"')
            with self.assertRaisesRegex(ValueError,"SHA_CHANGED"):
                validate_capability_and_layer(bad,"2018")
    def test_unverified_site_and_format_are_rejected(self):
        with self.assertRaises(ValueError):
            make_fixed_feature_request("2020",5.1,53.3,"text/plain")
        with self.assertRaises(ValueError):
            make_fixed_feature_request("2019",5.1,53.3,"text/html")
        with self.assertRaises(ValueError):
            make_fixed_feature_request("2019",51.0,53.3,"text/plain")
if __name__=="__main__":
    unittest.main()
