"""v23 original-source gate pure tests, never decode real animal GPS outcomes."""
import csv
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

import source_gate as s

class OriginalDucksSourceContract(unittest.TestCase):
    def test_exact_zenodo_source_identity_and_md5(self):
        self.assertEqual(s.RECORD_ID,16940654)
        self.assertEqual(s.ORIGINAL_PROVIDER_MD5,"1972d0ef08b83c2b88a169ba07bb48b3")
        self.assertEqual(s.SOURCE_NAME,"250823_LNU_dabbling_ducks_hourly.csv")

    def test_manifest_strict_size_md5_and_origin(self):
        z={"files":[{"key":s.SOURCE_NAME,"size":49_000_000,
                     "checksum":"md5:"+s.ORIGINAL_PROVIDER_MD5,
                     "links":{"self":"https://zenodo.org/api/records/16940654/files/xyz"}}]}
        out=s.select_original(z)
        self.assertEqual(out["size"],49_000_000)
        self.assertEqual(out["md5"],s.ORIGINAL_PROVIDER_MD5)
        with self.assertRaisesRegex(ValueError,"MD5"):
            s.select_original({"files":[{**z["files"][0],"checksum":"md5:"+"0"*32}]})
        with self.assertRaisesRegex(ValueError,"not Zenodo"):
            s.select_original({"files":[{**z["files"][0],
                           "links":{"self":"https://fake.test/file.csv"}}]})

    def _synthetic(self,root,birds=24,days=15):
        path=Path(root)/"source.csv"
        with path.open("w",newline="",encoding="utf-8") as fp:
            cols=list(s.SOURCE_COLS)
            w=csv.DictWriter(fp,fieldnames=cols)
            w.writeheader()
            for bird in range(birds):
                for day in range(days):
                    stamp=f"2020-06-{(day+1):02d} 12:00:00"
                    w.writerow({"study.name":"test-only-study",
                                "study.id":"109",
                                "individual.id":str(bird),
                                "individual.taxon.canonical.name":"Test duck",
                                "timestamp":stamp,
                                "location.long":"12.345",
                                "location.lat":"-12.345",
                                "gps.hdop":"1.5",
                                "ground.speed":"1.1"})
        return path

    def test_min_twenty_repeated_individual_days_passes(self):
        with tempfile.TemporaryDirectory() as root:
            d=s.inspect_source_ID_date_only(self._synthetic(root))
        self.assertEqual(d["unique_individuals_within_source_study_ID"],24)
        self.assertEqual(d["individuals_at_least_14_distinct_UTC_days"],24)
        self.assertEqual(d["original_physical_data_rows"],360)
        self.assertTrue(d["precommitted_minimum_individual_history_passes"])
        self.assertFalse(d["source_GPS_latitude_longitude_or_speed_read"])
        self.assertFalse(d["actual_group_assigned_social_network_available"])
        self.assertNotIn("12.345",json.dumps(d))
        self.assertNotIn("2020-06-01 12:00:00",json.dumps(d))

    def test_short_tracks_fail_repeated_day_gate(self):
        with tempfile.TemporaryDirectory() as root:
            d=s.inspect_source_ID_date_only(self._synthetic(root,birds=60,days=3))
        self.assertEqual(d["unique_individuals_within_source_study_ID"],60)
        self.assertFalse(d["precommitted_minimum_individual_history_passes"])

    def test_malformed_date_is_rejected(self):
        with self.assertRaises(ValueError):
            s.parse_utc("2025-06-01T12:00:00+09:00")
        self.assertEqual(s.parse_utc("2020-01-01 00:00:00"),
                         dt.datetime(2020,1,1))

if __name__=="__main__":
    unittest.main()
