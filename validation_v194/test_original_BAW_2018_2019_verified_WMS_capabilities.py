import unittest
from validation_v194.original_BAW_2018_2019_verified_WMS_capabilities import (
    OFFICIAL_YEAR_WMS,OFFICIAL_CENTRAL_WMS,
    official_verified_endpoint,inspect_WMS_xml
)
class AuthenticBAWWMS(unittest.TestCase):
    def test_fixed_original_official_urls_and_no_insecure_downgrade(self):
        self.assertEqual(len(OFFICIAL_YEAR_WMS),2)
        self.assertTrue(all(official_verified_endpoint(s) for s in OFFICIAL_YEAR_WMS.values()))
        self.assertTrue(official_verified_endpoint(OFFICIAL_CENTRAL_WMS))
        self.assertFalse(official_verified_endpoint('http://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wms?request=GetCapabilities'))
        self.assertFalse(official_verified_endpoint('https://evil.example/TrilaWatt.nc?request=GetCapabilities'))
        self.assertFalse(official_verified_endpoint('https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wms?request=GetMap'))
    def test_authentic_wms_declares_water_layer_and_target_year(self):
        xml=b'''<?xml version="1.0"?>
        <WMS_Capabilities version="1.3.0" xmlns="http://www.opengis.net/wms">
          <Service><Name>WMS</Name></Service>
          <Capability><Layer><Title>original source</Title><Layer>
           <Name>TrilaWatt:sea_surface_height_2d</Name>
           <Title>Sea surface height</Title>
           <Dimension name="time">2018-06-01T00:00:00Z/2018-06-03T00:00:00Z/PT20M</Dimension>
          </Layer></Layer></Capability>
        </WMS_Capabilities>'''
        v=inspect_WMS_xml(xml,"2018")
        self.assertEqual(v["native_WMS_version"],"1.3.0")
        self.assertTrue(v["native_service_metadata_declares_target_year"])
        self.assertEqual(v["source_tide_water_height_named_layers_cap45"][0]["name"],
                         "TrilaWatt:sea_surface_height_2d")
        self.assertTrue(v["does_not_verify_native_model_water_level_or_vertical_datum"])
    def test_reject_bad_or_external_entity_xml(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            inspect_WMS_xml(b'<!DOCTYPE x [ <!ENTITY local SYSTEM "file:///etc/passwd"> ]><WMS_Capabilities>&local;</WMS_Capabilities>')
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            inspect_WMS_xml(b'<html><body>Sorry</body></html>')
    def test_valid_wms_without_height_layer_does_not_claim_tide(self):
        s=b'<WMS_Capabilities version="1.3.0"><Capability><Layer><Layer><Name>temperature</Name></Layer></Layer></Capability></WMS_Capabilities>'
        a=inspect_WMS_xml(s,"2019")
        self.assertFalse(a["source_tide_water_height_named_layers_cap45"])
        self.assertFalse(a["native_service_metadata_declares_target_year"])
if __name__=="__main__":
    unittest.main()
