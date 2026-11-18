import unittest
from validation_v196.original_BAW_Wattflaechen_2018_2019_WFS_source import (
 WFS_OFFICIAL,is_official_WFS_url,candidate_original_NL_layer_year,inspect_authentic_WFS_source
)
class BAWIntertidalAnnualNativeSource(unittest.TestCase):
    def test_only_certified_official_service_capabilities(self):
        self.assertTrue(is_official_WFS_url(WFS_OFFICIAL))
        self.assertFalse(is_official_WFS_url(WFS_OFFICIAL.replace("https:","http:")))
        self.assertFalse(is_official_WFS_url("https://evil.example/wfs?REQUEST=GetCapabilities&SERVICE=WFS"))
        self.assertFalse(is_official_WFS_url("https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetFeature&SERVICE=WFS"))
    def test_native_NL_year_specific_names_unambiguous(self):
        xml=b'''<?xml version="1.0"?>
        <wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0"
         xmlns:ows="http://www.opengis.net/ows/1.1" version="2.0.0">
          <wfs:FeatureTypeList>
            <wfs:FeatureType><wfs:Name>original:intertidal_NL_2018</wfs:Name>
              <wfs:Title>Intertidal Netherlands 2018</wfs:Title>
              <wfs:DefaultCRS>EPSG:4326</wfs:DefaultCRS></wfs:FeatureType>
            <wfs:FeatureType><wfs:Name>original:intertidal_NL_2019</wfs:Name>
              <wfs:Title>Intertidal Netherlands 2019</wfs:Title>
            </wfs:FeatureType>
          </wfs:FeatureTypeList>
        </wfs:WFS_Capabilities>'''
        r=inspect_authentic_WFS_source(xml)
        self.assertEqual(r["n_native_feature_types"],2)
        self.assertTrue(r["original_native_NL_year_exactly_one_candidate_each"])
        self.assertEqual(r["native_2018_2019_NL_feature_type_candidates"]["2018"][0]["name"],
                         "original:intertidal_NL_2018")
    def test_ambiguous_same_year_never_auto_selects(self):
        x=inspect_authentic_WFS_source(b'''<WFS_Capabilities version="2.0.0">
          <FeatureTypeList>
           <FeatureType><Name>Intertidal_NL_2018</Name></FeatureType>
           <FeatureType><Name>OtherIntertidal_NL_2018</Name></FeatureType>
           <FeatureType><Name>Intertidal_NL_2019</Name></FeatureType>
          </FeatureTypeList></WFS_Capabilities>''')
        self.assertEqual(len(x["native_2018_2019_NL_feature_type_candidates"]["2018"]),2)
        self.assertFalse(x["original_native_NL_year_exactly_one_candidate_each"])
    def test_dtd_and_html_block(self):
        with self.assertRaises(ValueError):
            inspect_authentic_WFS_source(b'<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><WFS_Capabilities>&x;</WFS_Capabilities>')
        with self.assertRaises(ValueError):
            inspect_authentic_WFS_source(b'<html><body>error</body></html>')
if __name__=="__main__":
    unittest.main()
