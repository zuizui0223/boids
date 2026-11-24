"""v31b fake Zenodo responses: MD5, link and crosswalk source-only."""
from __future__ import annotations
import hashlib
import unittest
from validation_fish_school_v31.zenodo_author_source import (
    SourceStop,_meta_field,original_file_link,r_source_identity_signature,
    auth_file
)
class FakeResponse:
    def __init__(self,url,body):
        self.url=url;self.body=body
    def read(self,size):return self.body[:size]
    def geturl(self):return self.url
    def __enter__(self):return self
    def __exit__(self,*args):return False

class OriginalSourceAuthority(unittest.TestCase):
    def fixture(self):
        content=b"Trial,Group\n1,G1\n"
        return content,{"key":"MacGregorIoannou_Data.csv",
         "size":len(content),"checksum":"md5:"+hashlib.md5(content).hexdigest(),
         "links":{"self":"https://zenodo.org/api/records/5490572/files/MacGregorIoannou_Data.csv/content"}}

    def test_real_original_provider_checksum_only_authorized(self):
        b,meta=self.fixture()
        def mock(url,cap):
            return b,url
        raw,rec=auth_file(meta,"MacGregorIoannou_Data.csv",mock)
        self.assertEqual(raw,b)
        self.assertTrue(rec["author_provider_MD5_verified"])
        self.assertTrue(rec["original_download_link_was_author_metadata"])

    def test_original_author_md5_mismatch_stops(self):
        b,meta=self.fixture()
        with self.assertRaises(SourceStop):
            auth_file(meta,"MacGregorIoannou_Data.csv",lambda url,cap:(b+b"!",url))

    def test_wrong_filename_or_official_record_link_stops(self):
        b,meta=self.fixture()
        with self.assertRaises(SourceStop):
            _meta_field(meta,"Readme.csv")
        meta["links"]["self"]="https://unverified.example.net/file"
        with self.assertRaises(SourceStop):
            original_file_link(meta)

    def test_zenodo_file_path_must_be_original_record_api(self):
        b,meta=self.fixture()
        meta["links"]["self"]="https://zenodo.org/unrelated/u"
        with self.assertRaises(SourceStop):
            original_file_link(meta)

    def test_r_source_only_signature_never_redistributes_code(self):
        txt=b"data <- read.csv('MacGregorIoannou_Data.csv')\n" \
          + b"for (trial in 1:84) { group <- id[trial] }\n" \
          + b"x <- 0\n"*15
        parsed=r_source_identity_signature(txt)
        self.assertGreaterEqual(parsed["n_lines_containing_both_group_and_trial_or_file_identity"],1)
        self.assertFalse(parsed["original_author_R_source_lines_redistributed"])
        self.assertTrue(parsed["author_R_code_not_executed"])
        self.assertIn("MacGregorIoannou_Data.csv",parsed["original_R_source_filename_literals"])

if __name__=="__main__":unittest.main()
