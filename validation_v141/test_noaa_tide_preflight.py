"""NOAA hourly data validation fixtures; no biological records."""
from __future__ import annotations
import json
import unittest
from noaa_tide_preflight import parse_noaa

class TestVerifiedNoaaParser(unittest.TestCase):
    def test_noaa_misidentified_station_refused(self):
        raw=json.dumps({"metadata":{"id":"9999999"},"data":[{"t":"2019-06-01 00:00","v":"1.1"}]}).encode()
        with self.assertRaises(ValueError):
            parse_noaa(raw,9413450)
    def test_duplicate_hour_refused(self):
        raw=json.dumps({"metadata":{"id":"9413450"},"data":[
            {"t":"2019-06-01 00:00","v":"1.1"},{"t":"2019-06-01 00:00","v":"1.2"}]}).encode()
        with self.assertRaises(ValueError):
            parse_noaa(raw,9413450)
    def test_known_week_subset(self):
        raw=json.dumps({"metadata":{"id":"9413450","name":"Monterey"},
           "data":[{"t":"2019-06-01 00:00","v":"1.1"},
                   {"t":"2019-06-01 01:00","v":"1.7"}]}).encode()
        out=parse_noaa(raw,9413450)
        self.assertEqual(out["n_verified_hourly_source_rows"],2)
        self.assertEqual(out["n_missing_hours_in_range"],166)
        self.assertAlmostEqual(out["height_range_m"],.6)

if __name__=="__main__":unittest.main()
