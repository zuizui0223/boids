"""v28 new noctule bat source is metadata-only; no bat field data opened."""
import unittest
import original_source_manifest as s

class SourceProvenance(unittest.TestCase):
    def fixture(self):
        return {"id":s.RECORD_ID,"files":[
          {"key":"Annotated_Bat_GPS_ResourceSelection.csv","size":14_000_000,
           "checksum":"md5:"+"a"*32,
           "links":{"self":"https://zenodo.org/api/files/example.csv"}},
          {"key":"Data_Structure_UploadedFiles.pdf","size":220_000,
           "checksum":"md5:"+"b"*32,
           "links":{"self":"https://zenodo.org/api/files/schema.pdf"}}]}
    def test_original_source_identity_and_bound(self):
        self.assertEqual(s.RECORD_ID,7535030)
        self.assertEqual(s.SINGLE_FILE_CAP,100_000_000)
        self.assertTrue(s.API.startswith("https://zenodo.org/api/records/"))

    def test_only_bounded_original_tabular_data_admitted_for_later_stages(self):
        d=s.source_list(self.fixture())
        self.assertEqual(len(d),2)
        self.assertEqual(sum(x["single_source_cap_admissible"] for x in d),1)
        self.assertFalse(d[1]["structured_file_candidate"])
        self.assertTrue(d[0]["provider_original_checksum"].startswith("md5:"))

    def test_oversized_source_is_structural_not_ecological_failure(self):
        x=self.fixture()
        x["files"][0]["size"]=s.SINGLE_FILE_CAP+1
        d=s.source_list(x)
        self.assertFalse(d[0]["single_source_cap_admissible"])

    def test_duplicate_filenames_and_external_provider_file_urls_stop(self):
        x=self.fixture()
        x["files"].append(dict(x["files"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicated"):
            s.source_list(x)
        x=self.fixture()
        x["files"][0]["links"]["self"]="https://attacker.example/file.csv"
        with self.assertRaisesRegex(ValueError,"outside Zenodo"):
            s.source_list(x)

    def test_no_animal_identity_or_habitat_values_in_output(self):
        d=s.source_list(self.fixture())
        self.assertTrue(all("location.lat" not in str(x) for x in d))
        self.assertTrue(all("batid" not in str(x) for x in d))
if __name__=="__main__":
    unittest.main()
