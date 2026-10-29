"""v25-B1 source-only USGS original item & no outcomes tests."""
import unittest
import usgs_step_manifest_gate as v

class OriginalUSGSSource(unittest.TestCase):
    def sample(self):
        return {
          "id":v.SOURCE_ID,
          "title":"Movements, used habitats, and available habitats identified using Step Selection Processes for four species of waterfowl in California's Central Valley, 2016-2022",
          "identifiers":[{"type":"DOI","key":"doi:10.5066/P9ELSUHN"}],
          "rights":"CC0",
          "files":[{
              "name":"original_step_choice.csv","size":19_000_000,
              "contentType":"text/csv",
              "checksum":{"type":"MD5","value":"f"*32},
              "downloadUri":"https://www.sciencebase.gov/catalog/file/get/"+v.SOURCE_ID+"?f=abc"}]
        }

    def test_original_USGS_source_and_DOI_fixed(self):
        self.assertEqual(v.SOURCE_ID,"652edfe8d34edd15305a9ab0")
        self.assertEqual(v.SOURCE_DOI,"10.5066/P9ELSUHN")
        self.assertEqual(v.MAX_SINGLE,250_000_000)
        self.assertTrue(all(x.startswith("https://") for x in v.ENDPOINTS))

    def test_original_DOI_title_and_ID_cannot_silently_change(self):
        v.original_item(self.sample())
        for replacement in (
          {"id":"different"},
          {"title":"Independent fictional animal data"},
          {"identifiers":[{"type":"DOI","key":"doi:10.5066/WRONG"}]},
        ):
            bad={**self.sample(),**replacement}
            with self.assertRaisesRegex(ValueError,"Wrong|title|DOI"):
                v.original_item(bad)

    def test_original_manifest_files_size_gate_no_animal_rows(self):
        o=v.original_item(self.sample())
        self.assertEqual(o["candidate_original_data_files"],1)
        self.assertEqual(o["candidate_files_under_limit"],
                         ["original_step_choice.csv"])
        self.assertEqual(o["file_manifest"][0]["provider_checksum"]["value"],
                         "f"*32)
        self.assertFalse(o["model_fitted"])
        self.assertFalse(o["animal_step_or_original_numeric_habitat_data_read"])

    def test_large_original_file_only_reports_size_not_source_success(self):
        item=self.sample()
        item["files"][0]["size"]=500_000_000
        out=v.original_item(item)
        self.assertEqual(out["candidate_data_file_over_fixed_250MB_limit"],
                         ["original_step_choice.csv"])
        self.assertEqual(out["candidate_files_under_limit"],[])

    def test_duplicate_original_file_is_rejected(self):
        x=self.sample()
        x["files"].append(dict(x["files"][0]))
        with self.assertRaisesRegex(ValueError,"Repeated"):
            v.original_item(x)

if __name__=="__main__":
    unittest.main()
