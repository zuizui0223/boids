import unittest
from validation_v198.original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import (
 URLS,NeverFollowHTTPRedirects,validate_original_url,inspect_ogc_metadata
)
class OfficialBAWWattflaechenRoutes(unittest.TestCase):
    def test_three_published_exact_routes_only(self):
        self.assertEqual(set(URLS),{"WFS","WMS","WCS"})
        for service,url in URLS.items():
            self.assertTrue(validate_original_url(url,service))
            with self.assertRaises(ValueError):
                validate_original_url(url.replace("https://","http://"),service)
    def test_redirect_never_followed(self):
        self.assertIsNone(NeverFollowHTTPRedirects().redirect_request(
            None,None,302,"Moved",{}, "https://untrusted.example/original-source"))
    def test_accept_native_wfs_capabilities_but_not_features(self):
        xml=b'''<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0" version="2.0.0">
        <wfs:FeatureTypeList><wfs:FeatureType>
          <wfs:Name>trilawatt:Watt_NL_2018</wfs:Name>
          <wfs:Title>Watt 2018 NL</wfs:Title>
        </wfs:FeatureType></wfs:FeatureTypeList></wfs:WFS_Capabilities>'''
        r=inspect_ogc_metadata(xml,"WFS")
        self.assertEqual(r["original_layer_count"],1)
        self.assertEqual(r["2018_NL_candidate_layer_names"],["trilawatt:Watt_NL_2018"])
        self.assertTrue(r["no_original_feature_geom_or_WMS_height_grid_or_NC_native_datum"])
    def test_reject_html_or_XXE(self):
        with self.assertRaises(ValueError):
            inspect_ogc_metadata(b'<html>Authentication expired</html>',"WFS")
        with self.assertRaises(ValueError):
            inspect_ogc_metadata(b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><WFS_Capabilities>&x;</WFS_Capabilities>',"WFS")
if __name__=="__main__":
    unittest.main()
