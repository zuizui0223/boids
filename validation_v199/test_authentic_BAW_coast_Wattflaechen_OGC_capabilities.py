import unittest
from validation_v199.authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
 DESTINATIONS, EVIDENCE_308_RUNS, only_pinned_original_destination,
)
class FrozenAuthenticBAWRedirects(unittest.TestCase):
    def test_source_original_308_destinations_locked(self):
        self.assertEqual(len(DESTINATIONS),3)
        self.assertEqual(EVIDENCE_308_RUNS,(44429348878,44429376545))
        for service,url in DESTINATIONS.items():
            self.assertTrue(only_pinned_original_destination(url,service))
            with self.assertRaises(ValueError):
                only_pinned_original_destination(url.replace("https://","http://"),service)
            with self.assertRaises(ValueError):
                only_pinned_original_destination(url.replace("coast.baw.de","attacker.example"),service)
    def test_no_invented_year_specific_feature_layer(self):
        self.assertTrue(all("GetCapabilities" in url for url in DESTINATIONS.values()))
        self.assertTrue(all("GetFeature" not in url for url in DESTINATIONS.values()))
if __name__=="__main__":
    unittest.main()
