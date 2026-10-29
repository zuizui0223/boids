"""v27 original 18 breeding tit pair/trees Dryad source-only mock contract tests."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import original_source_gate as s

class OriginalTitsSource(unittest.TestCase):
    def test_original_DOI_and_files_without_inventing_source_bytes(self):
        self.assertEqual(s.DOI,"10.5061/dryad.kprr4xhm0")
        self.assertEqual(len(s.EXPECTED_FILES),5)
        self.assertIn("GPS_LOCATIONS.csv",s.EXPECTED_FILES)
        self.assertIn("Tree_Availability_Data.csv",s.EXPECTED_FILES)

    def test_Dryad_original_link_host_strict(self):
        x={"_links":{"self":{"href":"/api/v2/files/12345"}}}
        self.assertEqual(s.official_href(x,"self"),
                         "https://datadryad.org/api/v2/files/12345")
        with self.assertRaisesRegex(ValueError,"outside"):
            s.official_href({"_links":{"self":{"href":
               "https://attacker.invalid/observations.csv"}}},"self")

    def test_original_file_id_from_provider_self_link(self):
        x={"_embedded":{"stash:files":[
           {"path":"GPS_LOCATIONS.csv","size":136020,
            "digest":"0"*64,"digestType":"sha-256",
            "_links":{"self":{"href":"/api/v2/files/12345"}}},
           {"path":"Tree_Availability_Data.csv","size":128480,
            "_links":{"self":{"href":"/api/v2/files/12346"}}}]}}
        out=s.official_files(x)
        self.assertEqual(out[0]["provider_file_ID"],12345)
        self.assertEqual(out[1]["name"],"Tree_Availability_Data.csv")
        self.assertEqual(out[0]["provider_digest_type"],"sha-256")
        self.assertNotIn("bird_location",out[0])

    def test_missing_ident_or_inadmissible_file_size_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            value=s.public_file_download({
                "name":"GPS_LOCATIONS.csv","provider_file_ID":None,
                "size":136020},Path(root)/"source.csv")
        self.assertEqual(value["status"],"NOT_ADMITTED_MISSING_ID_OR_SIZE_LIMIT")

    def test_duplicate_provider_file_names_hard_stop(self):
        x={"files":[{"path":"GPS_LOCATIONS.csv","size":100},
                    {"path":"GPS_LOCATIONS.csv","size":200}]}
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            s.official_files(x)

if __name__=="__main__":
    unittest.main()
