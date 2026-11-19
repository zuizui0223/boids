"""Known-truth original ZIP directory extraction from one pinned HTTP range."""
import hashlib
import io
import struct
import unittest
import zipfile
from usfws_zip_in_tail_v43a import run
from usfws_zip_range_directory import ORIGINAL_TOTAL, TAIL_BYTES, central_location

def synthetic_tail():
    tmp=io.BytesIO()
    with zipfile.ZipFile(tmp,"w",compression=zipfile.ZIP_STORED) as z:
        z.writestr("sensitive-roost-123/Nightly Pass Counts.xlsx",b"NEVER_EXPORT_BAT_ACTIVITY_888")
        z.writestr("other/Pass Lists.xlsx",b"NEVER_EXPORT_GPS_999")
        z.writestr("Metadata.txt",b"NOT_AN_ANIMAL_TABLE")
    original=tmp.getvalue()
    loc=central_location(original)
    start=loc["central_directory_offset"]
    end=start+loc["central_directory_size"]
    cd=original[start:end]
    footer=bytearray(original[end:])
    assert footer[:4]==b"PK\x05\x06"
    footer[16:20]=struct.pack("<I",ORIGINAL_TOTAL-22-len(cd))
    tail=b"\x00"*(TAIL_BYTES-len(cd)-len(footer))+cd+bytes(footer)
    assert len(tail)==TAIL_BYTES
    return tail

def fake_fetch(blob):
    def f(url,start,end):
        assert start==ORIGINAL_TOTAL-TAIL_BYTES
        assert end==ORIGINAL_TOTAL-1
        return 206,f"bytes {start}-{end}/{ORIGINAL_TOTAL}",blob
    return f

class SingleRangeTests(unittest.TestCase):
    def test_original_metadata_without_file_payloads(self):
        tail=synthetic_tail()
        out=run(fake_fetch(tail),expected_tail_sha256=hashlib.sha256(tail).hexdigest())
        self.assertEqual(out["status"],"CENTRAL_DIRECTORY_INDEX_VERIFIED_SOURCE_ONLY")
        m=out["central_directory_metadata"]
        self.assertEqual(m["directory_entry_count"],3)
        self.assertEqual(m["original_member_extension_counts"][".xlsx"],2)
        self.assertEqual(m["source_filename_keyword_categories"]["night"],1)
        self.assertFalse(out["complete_detector_effort_or_zeros_verified"])
        self.assertFalse(out["original_member_payloads_requested_or_read"])
        self.assertNotIn("sensitive-roost-123",str(out))
        self.assertNotIn("NEVER_EXPORT_BAT_ACTIVITY",str(out))
    def test_hash_difference_never_re_pinned(self):
        out=run(fake_fetch(synthetic_tail()),expected_tail_sha256="0"*64)
        self.assertEqual(out["status"],"PINNED_TAIL_CHECKSUM_MISMATCH_STOP")
        self.assertNotIn("central_directory_metadata",out)
    def test_ignored_range_status_does_not_promote_source(self):
        out=run(lambda url,start,end:(200,"",synthetic_tail()),expected_tail_sha256="x"*64)
        self.assertEqual(out["status"],"TAIL_RANGE_SOURCE_STOP")
        self.assertFalse(out["source_full_archive_sha256_verified"])
    def test_corrupted_directory_count_fails(self):
        tail=bytearray(synthetic_tail())
        start=len(tail)-22
        tail[start+10:start+12]=struct.pack("<H",4)
        tail[start+8:start+10]=struct.pack("<H",4)
        blob=bytes(tail)
        out=run(fake_fetch(blob),expected_tail_sha256=hashlib.sha256(blob).hexdigest())
        self.assertEqual(out["status"],"CENTRAL_DIRECTORY_COUNT_MISMATCH_STOP")
    def test_unchanged_v43_stop_and_no_model(self):
        tail=synthetic_tail()
        out=run(fake_fetch(tail),expected_tail_sha256=hashlib.sha256(tail).hexdigest())
        self.assertTrue(out["original_v42_whole_zip_size_cap_stop_unchanged"])
        self.assertTrue(out["original_v43_second_range_transport_stop_unchanged"])
        self.assertFalse(out["ecological_model_fitted"])

if __name__=="__main__":
    unittest.main()
