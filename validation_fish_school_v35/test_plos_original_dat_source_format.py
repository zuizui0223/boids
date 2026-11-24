"""v35 synthetic only real-virtual experimental original .dat source preflight."""
import hashlib,io,unittest
from validation_fish_school_v35.plos_original_dat_source_format import (
    ORIGINAL,SourceStop,run,safe_source_format,original_bytes_checksum_only)

class Obj:
    def __init__(self,content):self.content=content
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def geturl(self):return "https://44c1cec316ec56bca76dfd65d2882b20.r2.cloudflarestorage.com/fake"
    def read(self,n):return self.content.read(n)

class OriginalAuthorFullChecksum(unittest.TestCase):
    def test_numeric_only_source_rows_no_group_id_inferred(self):
        report=safe_source_format(b"1 2.3 4.5 6\n2 5.6 8.7 9\n3 6.6 9 1\n")
        self.assertEqual(report["original_source_format"],"ASCII_OR_UTF8_TEXT")
        self.assertFalse(report["first_source_header_is_pure_nonnumeric_tokens"])
        self.assertEqual(report["source_explicit_subject_session_real_virtual_identity"],"NOT_ADMITTED")
        self.assertFalse(report["original_numeric_X_Y_Z_time_or_treatment_values_exported"])

    def test_source_header_can_be_potential_only_not_group_verified(self):
        d=safe_source_format(b"trial frame real_x virtual_x\n1 2 3.4 5.6\n")
        self.assertTrue(d["first_source_header_is_pure_nonnumeric_tokens"])
        self.assertFalse(d["source_identification_HEADER_ONLY_NOT_FULL_SESSION_ID"]["original_real_virtual_agent_column_named_explicitly"])
        self.assertEqual(d["original_header_nonnumeric_COLUMN_NAMES_only_max25"],
                         ["trial","frame","real_x","virtual_x"])

    def test_binary_source_not_decoded_as_coordinates(self):
        d=safe_source_format(b"\x00\x01\xff"+bytes(range(30)))
        self.assertEqual(d["original_source_format"],"BINARY_OR_NONPLAIN_TEXT")
        self.assertEqual(d["source_explicit_subject_session_real_virtual_identity"],"NOT_ADMITTED")

    def test_untrusted_external_non_author_download_fails(self):
        with self.assertRaises(SourceStop):
            original_bytes_checksum_only("https://nonfigshare.example.com/big.dat",50,"0"*32)

    def test_full_stream_authenticates_original_size_MD5_only(self):
        content=b"source header only\n"+b"1 2 3\n"*120
        class Opener:
            def __init__(self,handler):self.handler=handler
            def open(self,req,timeout):
                self.handler.onehop_count=1
                return Obj(io.BytesIO(content))
        out=original_bytes_checksum_only("https://ndownloader.figshare.com/files/123",
                      len(content),hashlib.md5(content).hexdigest(),
                      opener_factory=lambda h:Opener(h))
        self.assertEqual(out["authenticated_original_author_bytes_count"],len(content))
        self.assertEqual(out["computed_original_source_SHA256"],hashlib.sha256(content).hexdigest())
        self.assertEqual(out["n_original_source_newline_bytes"],121)

    def test_declared_source_MD5_tampered_is_scientific_stop(self):
        content=b"VALID SOURCE BYTES"
        class Opener:
            def __init__(self,handler):self.handler=handler
            def open(self,req,timeout):
                self.handler.onehop_count=1
                return Obj(io.BytesIO(content))
        with self.assertRaises(SourceStop):
            original_bytes_checksum_only("https://ndownloader.figshare.com/files/123",
                     len(content),"0"*32,opener_factory=lambda h:Opener(h))

    def test_unregistered_original_condition_disallowed(self):
        with self.assertRaises(SourceStop):
            run("C4-OneReal+OneVirtual.dat")
        self.assertEqual(len(ORIGINAL),4)

if __name__=="__main__":unittest.main()
