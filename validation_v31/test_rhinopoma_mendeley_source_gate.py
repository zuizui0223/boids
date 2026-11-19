"""Offline known-truth tests for Mendeley source-only API gating."""
import unittest
from rhinopoma_mendeley_source_gate import audit, summarize_files, ENDPOINTS


class MendeleySourceOnlyTests(unittest.TestCase):
    def test_exact_endpoints_are_versioned(self):
        self.assertEqual(len(ENDPOINTS),3)
        self.assertTrue(all("k7pt2j84f7" in x and "version=1" in x for x in ENDPOINTS.values()))

    def test_listing_harvests_only_filename_size_hash(self):
        d=summarize_files([{
            "filename":"audio_original.wav","id":"a",
            "content_details":{"size":1000,"sha256_hash":"x"*64,
                               "content_type":"audio/wav"},
            "raw_bat_coordinates":[13,24,78],
        }])
        self.assertEqual(d["reported_file_entries"],1)
        self.assertEqual(d["files_metadata_up_to_100"][0]["size_bytes"],1000)
        self.assertNotIn("raw_bat_coordinates",repr(d))

    def test_no_metadata_is_explicit_access_stop(self):
        d=audit(lambda url:{"http_status":403,"status":"HTTP_ACCESS_STOP","response_is_json":False})
        self.assertEqual(d["record_status"],"ORIGINAL_PUBLIC_API_NOT_ACCESSIBLE")
        self.assertFalse(d["source_admitted_for_behavior_fitting"])
        self.assertFalse(d["raw_gps_or_acoustic_values_opened"])

    def test_public_metadata_is_not_premature_admission(self):
        def fake(url):
            if "/files" in url:
                return {"http_status":200,"response_is_json":True,
                    "parsed_json":[{"filename":"audio.mp3","size":200}]}
            return {"http_status":200,"response_is_json":True,
                "parsed_json":{"name":"wild bat source","version":1,
                    "doi":{"id":"10.17632/k7pt2j84f7.1"},
                    "files":[{"filename":"GPS.csv","size":111}]}}
        r=audit(fake)
        self.assertEqual(r["record_status"],"PUBLIC_SOURCE_METADATA_ONLY")
        self.assertEqual(r["dataset_metadata"]["published_version"],1)
        self.assertFalse(r["source_admitted_for_behavior_fitting"])
        self.assertFalse(r["time_aligned_same_bat_raw_audio_and_movement_verified"])


if __name__=="__main__":
    unittest.main()
