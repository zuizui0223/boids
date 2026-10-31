"""Pure source-format tests; do not load original GPS movement."""
import datetime as dt
import unittest
import source_only as s

class SourceOnlyKnownTruth(unittest.TestCase):
    def test_exact_frozen_sources_and_years(self):
        self.assertEqual(s.RECORDS["O_SCHIERMONNIKOOG"]["record"],10053970)
        self.assertEqual(s.RECORDS["O_WESTERSCHELDE"]["record"],10053702)
        self.assertEqual(sum(len(x["years"]) for x in s.RECORDS.values()),10)
    def test_only_gps_years_selected(self):
        label="O_WESTERSCHELDE"
        make=lambda y:{"key":f"{label}-gps-{y}.csv.gz","size":9000,
           "checksum":"md5:"+"f"*32,
           "links":{"content":f"https://zenodo.org/records/10053702/files/{label}-gps-{y}.csv.gz/content"}}
        files=[make(y) for y in (2018,2019,2020)]
        files.append({"key":f"{label}-acceleration-2019.csv.gz","size":9000})
        years=s.select_gps_files({"files":files},label,[2018,2019,2020])
        self.assertEqual([e["year"] for e in years],[2018,2019,2020])
        with self.assertRaisesRegex(ValueError,"every frozen"):
            s.select_gps_files({"files":files[:-2]},label,[2018,2019,2020])
    def test_wrong_units_or_download_origin_stop(self):
        x={"files":[{"key":"S-gps-2020.csv.gz","size":1000,"checksum":"md5:"+"a"*32,
            "links":{"content":"https://example.com/evil"}}]}
        with self.assertRaisesRegex(ValueError,"Zenodo"):
            s.select_gps_files(x,"S",[2020])
    def test_UTC_timestamp_accepts_milliseconds_without_future_data(self):
        a=s.timestamp("2020-02-01 13:11:12.345")
        b=s.timestamp("2020-02-01T13:11:12.345Z")
        self.assertEqual(a,b)
        self.assertEqual(a,dt.datetime(2020,2,1,13,11,12,345000))
        with self.assertRaisesRegex(ValueError,"UTC"):
            s.timestamp("2020-02-01T13:11:12+09:00")
    def test_source_module_does_not_read_position_fields(self):
        self.assertNotIn("location-lat",s.ID_CANDIDATES)
        self.assertNotIn("location-long",s.TIME_CANDIDATES)

if __name__=="__main__": unittest.main()
