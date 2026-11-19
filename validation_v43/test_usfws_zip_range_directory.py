"""Synthetic test of bounded 206 byte ranges and ZIP central directory only."""
import io,struct,unittest,zipfile
from usfws_zip_range_directory import central_location,scan_directory,http_range,run,ORIGINAL_TOTAL

def sample_zip():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("Nightly Pass Counts.xlsx",b"night acoustic value 999 100 200")
        z.writestr("Metadata.txt",b"site latitude 42")
    return b.getvalue()

class USFWSRangeTests(unittest.TestCase):
    def test_original_zip_directory_metadata_without_member_values(self):
        raw=sample_zip()
        loc=central_location(raw)
        self.assertEqual(loc["status"],"STANDARD_ZIP_CENTRAL_DIRECTORY_LOCATED")
        d=raw[loc["central_directory_offset"]:loc["central_directory_offset"]+loc["central_directory_size"]]
        r=scan_directory(d,loc["declared_entry_count"])
        self.assertEqual(r["status"],"CENTRAL_DIRECTORY_INDEX_VERIFIED_SOURCE_ONLY")
        self.assertEqual(r["directory_entry_count"],2)
        self.assertEqual(r["source_filename_keyword_categories"]["night"],1)
        self.assertNotIn("999",str(r))
        self.assertNotIn("latitude 42",str(r))
    def test_reject_incomplete_directory(self):
        raw=sample_zip();loc=central_location(raw)
        d=raw[loc["central_directory_offset"]:loc["central_directory_offset"]+loc["central_directory_size"]]
        self.assertNotEqual(scan_directory(d[:-1],loc["declared_entry_count"])["status"],
                            "CENTRAL_DIRECTORY_INDEX_VERIFIED_SOURCE_ONLY")
    def test_ignoring_range_is_fail_closed(self):
        r,data=http_range(ORIGINAL_TOTAL-10,ORIGINAL_TOTAL-1,
                          lambda u,s,e:(200,"",b"pretend whole original file"))
        self.assertEqual(r["status"],"RANGE_NOT_VERIFIED_STOP")
        self.assertIsNone(data)
    def test_exact_byte_range_status_required(self):
        start=ORIGINAL_TOTAL-10;end=ORIGINAL_TOTAL-1
        r,data=http_range(start,end,
            lambda u,s,e:(206,f"bytes {s}-{e}/{ORIGINAL_TOTAL}",b"0123456789"))
        self.assertEqual(r["status"],"RANGE_CONFIRMED_206")
        self.assertEqual(data,b"0123456789")
    def test_transport_stopped_without_animal_claim(self):
        d=run(lambda u,s,e:(200,"",b"no valid partial request"))
        self.assertEqual(d["status"],"TAIL_RANGE_SOURCE_STOP")
        self.assertFalse(d["behavior_model_fitted"])
        self.assertTrue(d["v42_whole_archive_size_cap_stop_unchanged"])
if __name__=="__main__":
    unittest.main()
