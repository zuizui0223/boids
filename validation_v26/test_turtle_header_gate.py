"""v26-B1 marine turtle source-only header/MD5 known-truth tests."""
import tempfile
import unittest
from pathlib import Path

import turtle_header_gate as h

class TurtleOriginalHeaderOnly(unittest.TestCase):
    def test_expected_published_original_bytes_and_md5(self):
        self.assertEqual(h.SOURCE_BYTES,45669515)
        self.assertEqual(h.ORIGINAL_MD5,"5c5f25398720a663ae332097b49bf740")
        self.assertEqual(h.SOURCE_NAME,"Hart et al_iSSA.csv")

    def test_official_provider_file_manifest_strict(self):
        original={
            "status":"ORIGINAL_USGS_TURTLE_MANIFEST_ACQUIRED_NO_STEP_OUTCOMES",
            "original_source_metadata":{"files":[{
                "original_filename":h.SOURCE_NAME,
                "provider_bytes":h.SOURCE_BYTES,
                "provider_MD5_or_checksum":{
                  "type":"MD5","value":h.ORIGINAL_MD5},
                "download_provider_uri":"https://www.sciencebase.gov/catalog/file/get/"+
                       h.ORIGINAL_ITEM+"?f=original"}]}
        }
        spec=h.exact_file_in_manifest(original)
        self.assertEqual(spec["registered_published_bytes"],h.SOURCE_BYTES)
        self.assertEqual(spec["registered_published_md5"],h.ORIGINAL_MD5)
        original["original_source_metadata"]["files"][0]["provider_MD5_or_checksum"]["value"]="0"*32
        with self.assertRaisesRegex(ValueError,"MD5"):
            h.exact_file_in_manifest(original)

    def test_original_header_only_never_leaks_pit_or_depth_values(self):
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/"source.csv"
            f.write_text("PIT,step_id,t1,t2,case_,depth,chl\n"+
                         "SENSITIVE-PIT-X,9,2020-06-01,2020-06-01,1,12.45,.67\n"+
                         "SENSITIVE-PIT-X,9,2020-06-01,2020-06-01,0,33.22,.89\n")
            d=h.inspect_csv_header_only(f)
        self.assertEqual(d["n_original_columns"],7)
        self.assertEqual(d["physical_lines_after_header"],2)
        self.assertFalse(d["source_PIT_IDs_or_timestamps_read"])
        self.assertFalse(d["source_environmental_numeric_values_read"])
        self.assertNotIn("SENSITIVE-PIT-X",str(d))
        self.assertNotIn("12.45",str(d))

    def test_duplicate_header_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            f=Path(root)/"x.csv"
            f.write_text("PIT,PIT,case\n1,1,1\n")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                h.inspect_csv_header_only(f)

if __name__=="__main__":
    unittest.main()
