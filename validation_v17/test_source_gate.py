"""v17 source-only fail-closed tests; no third-party bird or wind records."""
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import source_gate as v


class SourceOnlyContract(unittest.TestCase):
    def test_record_and_both_provider_md5s_are_frozen(self):
        self.assertEqual(v.RECORD_ID, 5026107)
        self.assertEqual(
            v.SOURCE_EXPECTED["Experiment 1 - GPS data.zip"]["md5"],
            "499943131e1f6596187cf2a756e3c8dd",
        )
        self.assertEqual(
            v.SOURCE_EXPECTED["Experiment 1 - Weather Data.csv"]["md5"],
            "1a8c56601ed982a7f2968f1348831317",
        )

    def _record(self):
        return {"id": 5026107, "files": [
            {"key": name, "size": 22_000_000,
             "checksum": "md5:" + spec["md5"],
             "links": {"content": "https://zenodo.org/api/records/5026107/files/" + name}}
            for name, spec in v.SOURCE_EXPECTED.items()
        ]}

    def test_exact_two_independent_files_and_license_not_invented(self):
        m = v.select_manifest(self._record())
        self.assertEqual(set(m), set(v.SOURCE_EXPECTED))
        self.assertEqual(len(m), 2)
        self.assertNotIn("license", m["Experiment 1 - GPS data.zip"])
        with self.assertRaisesRegex(ValueError, "Other record"):
            v.select_manifest({**self._record(), "id": 21092705})

    def test_conflicting_digest_is_rejected(self):
        bad = self._record()
        bad["files"][0]["checksum"] = "md5:" + "0"*32
        with self.assertRaisesRegex(ValueError, "MD5 changed"):
            v.select_manifest(bad)

    def test_duplicate_source_filename_blocks_the_gate(self):
        bad = self._record()
        bad["files"].append(dict(bad["files"][0]))
        with self.assertRaisesRegex(ValueError, "Missing/duplicate"):
            v.select_manifest(bad)

    def test_untrusted_download_origin_is_not_opened(self):
        bad = self._record()
        bad["files"][0]["links"] = {"content": "https://evil.test/fake.zip"}
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            v.select_manifest(bad)

    def test_header_does_not_expose_any_numeric_coordinate(self):
        out = v.safe_header_line(b"2015-07-21,51.805300,-1.340200,12.4\n")
        self.assertEqual(out["status"], "unverified_or_numeric_first_line")
        self.assertNotIn("51.805300", json.dumps(out))
        out2 = v.safe_header_line(b"$GNRMC,120200.50,A,5149.23,N\n")
        self.assertEqual(out2["status"], "raw_nmea_sentence_not_column_header")
        self.assertNotIn("5149", json.dumps(out2))

    def test_named_weather_and_gps_header_and_duplicate_columns(self):
        out = v.safe_header_line(b"UTC Date,UTC Time,Wind Speed (m/s),Wind Bearing (deg)\n")
        self.assertEqual(out["status"], "verified_named_header")
        self.assertEqual(len(out["columns"]), 4)
        bad = v.safe_header_line(b"Lat,1.5,Wind\n")
        self.assertNotEqual(bad["status"], "verified_named_header")

    def test_evenly_spaced_source_selection_never_exceeds_limit(self):
        ix = v.sample_member_indices(300)
        self.assertEqual(len(ix), v.SAMPLED_HEADERS)
        self.assertEqual(ix[0], 0)
        self.assertEqual(ix[-1], 299)
        self.assertEqual(v.sample_member_indices(3), [0,1,2])

    def test_zip_structural_only_excludes_macos_sidecars(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"dummy.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("GPS/S30_001.csv", "Time,Lat,Lon\n1200,51.805,-1.34\n")
                z.writestr("__MACOSX/._S30_001.csv", "raw hidden")
                z.writestr("GPS/S31_001.csv", "Time,Lat,Lon\n1201,51.804,-1.35\n")
            result = v.zip_structure(p)
        self.assertEqual(result["appledouble_metadata_excluded"], 1)
        self.assertEqual(result["normal_files"], 2)
        self.assertEqual(result["csv_or_raw_text_candidates"], 2)
        self.assertEqual(result["source_observations_scored"], 0)
        self.assertNotIn("51.805", json.dumps(result))
        self.assertFalse(result["gps_original_utc_precision_verified"])

    def test_encrypted_or_parent_directory_zip_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"malicious.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("../GPS.csv", "x,y\n1,2\n")
            with self.assertRaisesRegex(ValueError,"Unsafe"):
                v.zip_structure(p)

    def test_original_weather_file_is_only_counted_not_analyzed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"weather.csv"
            p.write_text(
                "Timestamp,Wind speed,Wind direction\n"
                "2015-08-21 13:25:00,4.2,135\n"
                "2015-08-21 13:26:00,5.8,110\n", encoding="utf-8")
            q = v.weather_structure(p)
        self.assertEqual(q["physical_rows_after_first"],2)
        self.assertEqual(q["header"]["status"], "verified_named_header")
        self.assertFalse(q["weather_values_read_or_analyzed"])
        self.assertNotIn("135",json.dumps(q))
        self.assertFalse(q["weather_timezone_verified"])


if __name__ == "__main__":
    unittest.main()
