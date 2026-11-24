"""v34d fixed provider-redirect source-only synthetic verification."""
from __future__ import annotations
import hashlib,unittest
from urllib import request
from validation_fish_school_v34.onehop_figshare_original_files import (
    EXACT_VENDOR_CDN,ORIGINAL_PROVIDER,VerifiedOriginalOneHopFigshare,
    verified_original_figshare_small_bytes,SourceStop
)

ORIGIN="https://ndownloader.figshare.com/files/1234"
DEST="https://"+EXACT_VENDOR_CDN+"/original-author-object?X-Amz-Signature=SECRET_UNLOGGED"

class Res:
    def __init__(self,body):self.body=body
    def __enter__(self):return self
    def __exit__(self,*a):return False
    def geturl(self):return DEST
    def read(self,n):return self.body[:n]

class OriginalVerifiedRedirect(unittest.TestCase):
    def test_only_one_official_provider_source_redirect_allowed(self):
        h=VerifiedOriginalOneHopFigshare()
        req=request.Request(ORIGIN,method="GET")
        nxt=h.redirect_request(req,None,302,"Found",{},DEST)
        self.assertEqual(h.onehop_count,1)
        self.assertEqual(nxt.full_url,DEST)
        with self.assertRaises(SourceStop):
            h.redirect_request(nxt,None,302,"Found",{},DEST)

    def test_unregistered_other_object_storage_hostname_rejected(self):
        h=VerifiedOriginalOneHopFigshare()
        with self.assertRaises(SourceStop):
            h.redirect_request(request.Request(ORIGIN),None,302,"Found",{},
                               "https://untrusted.example.net/file")

    def test_source_checksum_byte_count_using_simulated_valid_official_hop(self):
        content=b"ORIGINAL_AUTHOR_CODE_ONLY_FAKE"
        md5=hashlib.md5(content).hexdigest()
        class Opener:
            def __init__(self,h):self.h=h
            def open(self,req,timeout):
                self.h.onehop_count=1
                return Res(content)
        actual=verified_original_figshare_small_bytes(
            ORIGIN,len(content),md5,opener_factory=lambda handler:Opener(handler))
        self.assertEqual(actual,content)

    def test_forged_source_md5_cannot_be_accepted_after_redirect(self):
        content=b"ORIGINAL_AUTHOR_CODE_ONLY_FAKE"
        class Opener:
            def __init__(self,h):self.h=h
            def open(self,req,timeout):
                self.h.onehop_count=1
                return Res(content)
        with self.assertRaises(SourceStop):
            verified_original_figshare_small_bytes(
                ORIGIN,len(content),"0"*32,opener_factory=lambda handler:Opener(handler))

    def test_original_provider_link_rejects_foreign_and_query_signatures(self):
        with self.assertRaises(SourceStop):
            verified_original_figshare_small_bytes(
                "https://fish-unverified.example/file",100,"0"*32)
        with self.assertRaises(SourceStop):
            verified_original_figshare_small_bytes(
                ORIGIN+"?unverified=1",100,"0"*32)

if __name__=="__main__":unittest.main()
