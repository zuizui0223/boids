"""v17-C independent Figshare source metadata known-truth tests, no GPS."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import ten_chain_source_gate as m


class TestFigshareCandidate(unittest.TestCase):
    def test_exact_new_source_and_different_old_ids(self):
        self.assertEqual(m.SOURCE_ID,14043362)
        self.assertEqual(m.SOURCE_DOI,"10.6084/m9.figshare.14043362")
        self.assertNotIn(str(m.SOURCE_ID),("5026107","4943714","21092705"))

    def test_original_provider_md5_source_manifest(self):
        source={"id":14043362,"files":[{
            "name":"gps_data.zip","size":2048,
            "computed_md5":"a"*32,
            "download_url":"https://ndownloader.figshare.com/files/777",
            "id":777}]}
        r=m.original_listing(source)
        self.assertEqual(r["files"][0]["provider_md5"],"a"*32)
        self.assertEqual(r["total_listed_bytes"],2048)
        with self.assertRaisesRegex(ValueError,"duplicated"):
            m.original_listing({"files":[source["files"][0]]*2})

    def test_untrusted_download_origins_are_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unexpected"):
            m.original_listing({"files":[{
                "name":"gps.zip","size":300,
                "download_url":"https://attacker.example.com/places.zip",
                "computed_md5":"b"*32}]})

    def test_source_zip_inventory_never_reads_motion_values(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/"source.zip"
            with zipfile.ZipFile(path,"w") as arc:
                arc.writestr("chain01/generation1/release01.csv",
                             "time,x,y\n123,51.801,-1.312\n")
                arc.writestr("chain02/generation2/release11.csv",
                             "time,x,y\n124,51.811,-1.313\n")
                arc.writestr("README.txt","example source labels")
            r=m.inventory_zip(path)
        self.assertEqual(r["source_explicit_chain_label_count"],2)
        self.assertEqual(r["files_in_zip"],3)
        self.assertEqual(r["extension_counts"][".csv"],2)
        self.assertFalse(r["source_navigational_outcomes_analyzed"])
        self.assertNotIn("51.801",json.dumps(r))
        self.assertFalse(r["weather_with_verified_clock_available"])

    def test_numeric_coordinate_first_line_is_masked_not_header(self):
        value=m.masked_header(b"2019-06-22,51.8021,-1.31\n")
        self.assertEqual(value["status"],"UNKNOWN_HEADER_OR_NUMERIC_DATA_FIRST_LINE")
        self.assertNotIn("51.8021",json.dumps(value))


if __name__=="__main__":
    unittest.main()
