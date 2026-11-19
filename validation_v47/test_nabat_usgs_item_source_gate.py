"""NABat 2026 original manifest metadata-only known-truth source tests."""
import json
import unittest
from nabat_usgs_item_source_gate import ITEM_ID,audit,provider_json,URLS

class USGSItemSourceTests(unittest.TestCase):
    def test_exact_published_item(self):
        self.assertEqual(ITEM_ID,"6ace802b1ba49b69a5819e47")
        self.assertEqual(len(URLS),2)
    def test_metadata_only_counts_and_never_exports_recording_names(self):
        d=provider_json({"id":ITEM_ID,"files":[
            {"name":"nabat-acoustic-data-manifest-20261015.csv","size":1244444},
            {"name":"README.md","size":2134},
            {"name":"secret_roost-location-001.wav","size":55555},
        ]})
        self.assertEqual(d["source_file_name_keyword_categories"]["manifest"],1)
        self.assertEqual(d["source_file_name_keyword_categories"]["readme"],1)
        self.assertNotIn("secret_roost",str(d))
        self.assertFalse(d["source_body_numeric_acoustic_values_parsed"])
    def test_valid_original_json_not_effort_admission(self):
        body=json.dumps({"id":ITEM_ID,"files":[{"name":"README.md","size":2}]}).encode()
        d=audit(lambda url:(200,"application/json",body))
        self.assertEqual(d["status"],"PUBLIC_ORIGINAL_ITEM_METADATA_ONLY")
        self.assertFalse(d["complete_site_night_effort_verified"])
        self.assertTrue(d["original_usfws_2010_2018_overlap_not_yet_resolved"])
    def test_http_access_stop_not_ecological_null(self):
        d=audit(lambda url:(401,"application/json",b"unauthorized"))
        self.assertEqual(d["status"],"PUBLIC_SOURCE_API_ACCESS_STOP")
        self.assertFalse(d["biological_prediction_fitted"])
    def test_wrong_id_refused(self):
        d=audit(lambda url:(200,"application/json",b'{"id":"wrong"}'))
        self.assertEqual(d["status"],"PUBLIC_SOURCE_API_ACCESS_STOP")
if __name__=="__main__":
    unittest.main()
