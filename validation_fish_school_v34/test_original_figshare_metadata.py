"""v34 synthetic-only official Figshare source-gate known-truth fixtures."""
import json
import unittest
from validation_fish_school_v34.original_figshare_metadata import (
    SOURCE_RECORDS,SourceStop,decode_author_record,run
)
ID=31378621

def legitimate_article():
    return {"id":ID,"title":"ORIGINAL AUTHORS controlled experimental fish VR data",
        "doi":f"10.6084/m9.figshare.{ID}.v1",
        "is_public":True,"is_embargoed":False,
        "files":[{"id":54321,"name":"trial_manifest.csv","size":12000,
            "supplied_md5":"0"*32,"computed_md5":"a"*32,
            "download_url":"https://ndownloader.figshare.com/files/54321"}],
        "license":{"name":"CC BY 4.0"},"published_date":"2026-10-29"}

def blob(d): return json.dumps(d).encode()

class SourceOriginalDataProvenanceTests(unittest.TestCase):
    def test_exact_author_article_ID_DOI_and_original_provider_file(self):
        x=decode_author_record(blob(legitimate_article()),ID)
        self.assertEqual(x["status"],"AUTHOR_FIGSHARE_ORIGINAL_METADATA_VERIFIED")
        self.assertEqual(x["n_author_source_files"],1)
        self.assertEqual(x["total_source_provider_published_file_bytes"],12000)
        self.assertFalse(x["original_file_bytes_or_fish_behavior_loaded"])
        self.assertFalse(x["original_subject_session_treatment_IDs_verified"])

    def test_200_http_permission_error_envelope_is_not_real_dataset(self):
        with self.assertRaises(SourceStop):
            decode_author_record(blob({"id":ID,"message":"You lack access to this private dataset"}),ID)

    def test_html_login_response_is_rejected(self):
        with self.assertRaises(SourceStop):
            decode_author_record(b"<html><body>Login</body></html>",ID)

    def test_wrong_DOI_or_ID_rejected_even_with_files(self):
        d=legitimate_article()
        d["doi"]="10.6084/m9.figshare.0000"
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)
        d=legitimate_article()
        d["id"]=123
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)

    def test_files_with_external_domain_or_missing_provider_MD5_are_not_trusted(self):
        d=legitimate_article()
        d["files"][0]["download_url"]="https://unverified-data.example.net/raw.csv"
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)
        d=legitimate_article()
        d["files"][0]["supplied_md5"]="BAD"
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)

    def test_empty_original_filenames_unsafe_or_no_files_rejected(self):
        d=legitimate_article()
        d["files"]=[]
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)
        d=legitimate_article()
        d["files"][0]["size"]=0
        with self.assertRaises(SourceStop):decode_author_record(blob(d),ID)

    def test_stop_no_synthetic_trial_intervention_effect_leakage(self):
        def f(article):
            if article==ID:return blob(legitimate_article())
            raise SourceStop("TEST_ONLY_RECORD_OTHER_NOT_AVAILABLE")
        x=run(f)
        self.assertEqual(x["status"],"PARTIAL_SOURCE_METADATA_STOP")
        self.assertFalse(x["original_fish_file_contents_downloaded"])
        self.assertFalse(x["original_vr_or_robot_manipulation_outcomes_computed"])
        self.assertEqual(len(x["author_figshare_record_source_manifest"]),len(SOURCE_RECORDS))

if __name__=="__main__":unittest.main()
