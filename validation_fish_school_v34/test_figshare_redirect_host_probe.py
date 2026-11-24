"""v34c fake HTTP redirect only, no real original author file body downloads."""
from __future__ import annotations
import io,json,unittest
from urllib import error
from email.message import Message
from validation_fish_school_v34.figshare_redirect_host_probe import (
    nofollow_one_request,SourceStop,run
)

URL="https://ndownloader.figshare.com/files/123"
SIGNED="https://figshare.s3-eu-west-1.amazonaws.com/private/bucket/obj?X-Amz-Signature=SECRET_SHOULD_NEVER_APPEAR"

def headers(location):
    h=Message()
    h["Location"]=location
    return h

class OnlyRedirectProvenance(unittest.TestCase):
    def test_official_original_http302_response_only_HOST_exported(self):
        def fetch(req,timeout):
            raise error.HTTPError(URL,302,"Found",headers(SIGNED),io.BytesIO(b"must not read"))
        r=nofollow_one_request(URL,"HEAD",fetch)
        self.assertEqual(r["status"],"ORIGINAL_PROVIDER_REDIRECT_METADATA_ONLY")
        self.assertEqual(r["original_location_host_ONLY_no_query_or_path"],"figshare.s3-eu-west-1.amazonaws.com")
        self.assertNotIn("SECRET",json.dumps(r))
        self.assertFalse(r["redirect_followed"])
        self.assertEqual(r["n_downloaded_author_file_bytes"],0)

    def test_http200_direct_source_does_not_read_original_content(self):
        class R:
            status=200
            headers={}
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,*args):raise AssertionError("MUST NEVER READ ORIGINAL AUTHOR FILE")
        out=nofollow_one_request(URL,"HEAD",lambda req,timeout:R())
        self.assertEqual(out["status"],"NO_REDIRECT_SOURCE_DIRECT")
        self.assertEqual(out["n_downloaded_author_file_bytes"],0)

    def test_http302_location_must_be_https(self):
        def bad(req,timeout):
            raise error.HTTPError(URL,302,"Found",headers("http://untrusted.example.test/original"),io.BytesIO())
        with self.assertRaises(SourceStop):
            nofollow_one_request(URL,"HEAD",bad)

    def test_original_malformed_file_URL_rejected(self):
        with self.assertRaises(SourceStop):
            nofollow_one_request("https://notfigshare.example.test/files/1","HEAD")

    def test_all_metadata_unavailable_no_original_action_taken(self):
        def missing(article):raise SourceStop("TEST_ONLY_MISSING_SOURCE_RECORD")
        x=run(fetchmeta=missing)
        self.assertEqual(x["status"],"SOURCE_ACCESS_STOP")
        self.assertEqual(len(x["original_provider_file_probe_receipts"]),4)
        self.assertEqual(x["n_original_file_bytes_downloaded"],0)
        self.assertFalse(x["original_real_fish_trial_or_treatment_rows_read"])

if __name__=="__main__":unittest.main()
