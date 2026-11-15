"""Synthetic source-only NOAA alignment and parser known truths."""
import unittest,sys,json
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from noaa_source_gate import parse_noaa,hourly_index,PARAMS

class TestV153(unittest.TestCase):
    def test_one_day_and_station_id(self):
        start=datetime(2019,1,1,0,0,tzinfo=timezone.utc)
        rows=[{"t":f"2019-01-01 {i:02d}:00","v":str(i/10)} for i in range(24)]
        raw=json.dumps({"metadata":{"id":"9411340","name":"Test"},
                        "data":rows}).encode()
        data,meta=parse_noaa(raw,"9411340",2019)
        self.assertEqual(len(data),24)
        self.assertEqual(meta["verified_numeric_hours"],24)
        self.assertEqual(data[hourly_index(start)],0)
        self.assertEqual(meta["source_min_height_m_MLLW"],0)
        self.assertEqual(meta["source_max_height_m_MLLW"],2.3)
    def test_wrong_gauge_is_hard_stop(self):
        raw=json.dumps({"metadata":{"id":"WRONG"},"data":[{"t":"2019-01-01 00:00","v":"1.0"}]*24}).encode()
        with self.assertRaises(ValueError):parse_noaa(raw,"9411340",2019)
    def test_duplicate_utc_hour_hard_stop(self):
        raw=json.dumps({"metadata":{"id":"1"},"data":[{"t":"2019-01-01 00:00","v":"1.0"}]*25}).encode()
        with self.assertRaises(AssertionError):parse_noaa(raw,"1",2019)
    def test_never_allow_missing_station_datum(self):
        self.assertEqual(PARAMS["product"],"hourly_height")
        self.assertEqual(PARAMS["datum"],"MLLW")
        self.assertEqual(PARAMS["time_zone"],"gmt")

if __name__=="__main__":unittest.main()
