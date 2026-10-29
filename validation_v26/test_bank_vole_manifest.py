"""v26-D no-outcome bank vole source manifest static tests."""
from __future__ import annotations
import unittest
import bank_vole_manifest as v

class OriginalVoleManifest(unittest.TestCase):
    def test_exact_publication_source(self):
        self.assertEqual(v.RECORD,10101651)
        self.assertEqual(v.DOI,"10.5281/zenodo.10101651")
        self.assertEqual(v.API,"https://zenodo.org/api/records/10101651")

    def test_file_list_cannot_serve_as_behaviour_result(self):
        out=v.common.safe_original_files_zenodo({
           "files":[{"key":"source_steps.csv","size":100000,
                     "checksum":"md5:"+"0"*32,
                     "links":{"content":"https://zenodo.org/records/10101651/files/data"}}]})
        self.assertEqual(out[0]["provider_bytes"],100000)
        self.assertNotIn("animal_choice",out[0])
        self.assertTrue(v.common.classify_aggregate(out)[
            "no_original_animal_or_environmental_rows_accessed"])

    def test_original_archive_larger_than_cap_stops_file(self):
        out=v.common.classify_aggregate([{
          "original_filename":"original.RData",
          "provider_bytes":400_000_000
        }])
        self.assertEqual(out["bounded_candidate_original_files"],[])
        self.assertEqual(out["source_files_above_predeclared_250MB"],["original.RData"])

if __name__=="__main__":
    unittest.main()
