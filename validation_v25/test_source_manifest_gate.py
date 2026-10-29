"""v25 original Dryad source integrity/source-only negative control tests."""
import hashlib
import unittest

import source_manifest_gate as d


class OriginalMallardSourceTests(unittest.TestCase):
    def test_exact_source_DOI_and_named_files(self):
        self.assertEqual(d.DOI,"10.5061/dryad.cjsxksnd5")
        self.assertEqual(d.TARGET_DATA,"EAP23-0437_data.rds")
        self.assertEqual(d.TARGET_DOC,"README.md")
        self.assertEqual(d.MAX_FILE,50_000_000)

    def test_self_link_stays_on_official_Dryad_host(self):
        sample={"_links":{"self":{"href":"/api/v2/files/54321"}}}
        self.assertEqual(d.provider_link(sample,"self"),
                         "https://datadryad.org/api/v2/files/54321")
        with self.assertRaisesRegex(ValueError,"Unexpected external"):
            d.provider_link({"_links":{"self":{"href":
              "https://attacker.test/example.rds"}}},"self")

    def test_official_original_manifest_hides_any_animal_values(self):
        rec={"_embedded":{"stash:files":[{
            "path":"EAP23-0437_data.rds","size":16090000,
            "digest":"a"*64,"digestType":"sha-256",
            "_links":{"self":{"href":"/api/v2/files/54321"}}},
            {"path":"README.md","size":3290,
             "_links":{"self":{"href":"/api/v2/files/54322"}}}]}}
        out=d.list_original_files(rec)
        self.assertEqual(len(out),2)
        self.assertEqual(out[0]["original_file_id"],54321)
        self.assertEqual(out[1]["filename"],"README.md")
        self.assertTrue(all("animal" not in k for k in out[0].keys()))
        self.assertEqual(out[0]["original_provider_digest"],"a"*64)

    def test_duplicate_provider_source_filenames_fail(self):
        f={"path":"EAP23-0437_data.rds","size":1000,
           "_links":{"self":{"href":"/api/v2/files/1234"}}}
        with self.assertRaisesRegex(ValueError,"duplicate"):
            d.list_original_files({"_embedded":{"stash:files":[f,f]}})

    def test_missing_original_file_ID_cannot_be_faked(self):
        with __import__("tempfile").TemporaryDirectory() as root:
            from pathlib import Path
            r=d.original_file_download({
                "filename":"EAP23-0437_data.rds","original_size_bytes":16_000_000,
                "original_file_id":None},Path(root)/"orig.rds")
        self.assertEqual(r["status"],"NOT_ADMITTED_SOURCE_ID_OR_SIZE")

    def test_source_failure_is_redacted_and_NOT_biological(self):
        import urllib.error
        e=urllib.error.HTTPError("https://datadryad.org",403,"Forbidden",{},None)
        self.assertEqual(d.safe_error(e),"HTTP_403")
        self.assertFalse(d.API.startswith("http://"))


if __name__=="__main__":
    unittest.main()
