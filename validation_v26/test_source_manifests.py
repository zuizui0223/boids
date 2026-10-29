"""v26 offline known-truth tests for two independent source manifests, no telemetry."""
from __future__ import annotations
import unittest
import source_manifests as v

class OriginalSourceManifestTests(unittest.TestCase):
    def test_original_USGS_turtle_and_Zenodo_mammal_fixed(self):
        self.assertEqual(v.TURTLE_ITEM,"5faab074d34eb413d5df1f41")
        self.assertEqual(v.TURTLE_DOI,"10.5066/P9UZU4GG")
        self.assertEqual(v.MAMMAL_RECORD,15756163)
        self.assertEqual(v.MAMMAL_DOI,"10.5281/zenodo.15756163")
        self.assertEqual(v.CAP_ONE_DATA_FILE,250_000_000)

    def test_USGS_original_files_not_animal_outcomes(self):
        x={"files":[{"name":"source.csv","size":15_000_000,
                     "checksum":{"type":"MD5","value":"a"*32},
                     "downloadUri":"https://www.sciencebase.gov/catalog/file/get/abc"}]}
        out=v.safe_original_files_usgs(x)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["provider_bytes"],15_000_000)
        self.assertEqual(out[0]["provider_MD5_or_checksum"]["value"],"a"*32)
        self.assertNotIn("animal_id",out[0])
        self.assertTrue(v.classify_aggregate(out)["aggregate_size_allowed_if_all_bounded"])

    def test_Zenodo_record_version_file_checksum_and_no_ghost_names(self):
        x={"files":[{"key":"original_input.rds","size":125_000_000,
                     "checksum":"md5:"+"b"*32,
                     "links":{"content":"https://zenodo.org/api/records/15756163/files/abc"}}]}
        out=v.safe_original_files_zenodo(x)
        self.assertEqual(len(out),1)
        self.assertIn("original_input.rds",
                      v.classify_aggregate(out)["bounded_candidate_original_files"])
        self.assertNotIn("movement_values",out[0])

    def test_larger_than_frozen_source_cap_never_admitted(self):
        x=[{"original_filename":"large.csv","provider_bytes":401_000_000},
           {"original_filename":"small.csv","provider_bytes":2_000_000}]
        p=v.classify_aggregate(x)
        self.assertEqual(p["source_files_above_predeclared_250MB"],["large.csv"])
        self.assertEqual(p["bounded_candidate_original_files"],["small.csv"])

    def test_duplicate_names_hard_stop(self):
        item={"files":[{"name":"same.csv","size":100},
                       {"name":"same.csv","size":100}]}
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            v.safe_original_files_usgs(item)
        item={"files":[{"key":"same.csv","size":100},
                       {"key":"same.csv","size":100}]}
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            v.safe_original_files_zenodo(item)

    def test_not_trust_unlisted_hosts(self):
        with self.assertRaisesRegex(ValueError,"Untrusted"):
            v.read_original_json("https://malicious.invalid/api/source")

if __name__=="__main__":
    unittest.main()
