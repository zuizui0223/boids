"""v89 known truth for true GLOBAL UHSLC original station SOURCE, no ecology.

Synthetic CSV station identifiers mimic public ERDDAP RQDS; measured sea
level/observed animals not included. Datum segments cannot count as
independent gauge stations. Later true hourly waterheight outcomes must
have separate frozen source/coverage protocols.
"""
from __future__ import annotations
import csv,io,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import real_global_UHSLC_hourly_station_manifest as g

def fake_csv():
    sio=io.StringIO()
    w=csv.writer(sio)
    w.writerow(g.FIXED_FIELDS)
    w.writerow(["","", "", "", "degrees_north","degrees_east"])
    w.writerows([
        [1,11,"Synthetic Pohnpei-A","Micronesia",6.983,158.233],
        [1,12,"Synthetic Pohnpei-B","Micronesia",6.983,158.250],
        [2,20,"Synthetic Tasmania","Australia",-42.50,146.9],
        [3,30,"Synthetic WestCoast","United States",35.1,238.7],
        [4,40,"Synthetic Arctic","Norway",79.8,22.1],
        [3,30,"Synthetic WestCoast","United States",35.1,238.7]
    ])
    return sio.getvalue().encode()

class OriginalGlobalRqdStationSource(unittest.TestCase):
    def test_original_hourly_quality_source_and_global_variables_fixed(self):
        self.assertEqual(len(g.PROVIDERS),2)
        self.assertEqual(g.ORIGINAL_QC_QUALITY,4)
        self.assertEqual(g.REFERENCE_UNITS,"millimeters")
        self.assertEqual(g.SOURCE_YEAR_FOR_FUTURE_PILOT,2019)
        self.assertTrue(g.source_URL(g.PROVIDERS[0][1]).endswith(
            "&distinct()"))
        with self.assertRaisesRegex(g.SourceUnavailable,"NON_FROZEN"):
            g.source_URL("https://unofficial.example.net/none")

    def test_actual_count_datum_segments_not_fake_independent_stations(self):
        stations,skipped=g.parse_original_station_manifest(fake_csv())
        q=g.aggregate_station_source(stations)
        self.assertEqual(len(stations),5)
        self.assertEqual(q["original_total_versioned_station_datum_records"],5)
        self.assertEqual(q["original_unique_physical_UHSLC_stations_by_station_ID"],4)
        self.assertEqual(q["original_station_IDs_with_more_than_one_datum_version"],1)
        self.assertEqual(len(q["original_latitude_15deg_source_bands"]),4)
        self.assertEqual(q["original_global_latitude_bounds"],[-42.5,79.8])
        self.assertGreaterEqual(
            skipped.get("duplicated_original_station_record_segment",0),1)
        coast=next(x for x in stations if x["uhslc_id"]==3)
        self.assertAlmostEqual(coast["longitude_signed"],-121.3)
        self.assertFalse(
            q["source_not_yet_original_2019_hourly_coverage_verified"] is False)

    def test_reject_missing_original_station_identifiers_no_fake_source(self):
        txt=b"uhslc_id,record_id,station_name,station_country,latitude,longitude\nunits,units,units,units,units,units\n"
        with self.assertRaisesRegex(g.SourceUnavailable,"NO_GENUINE"):
            g.parse_original_station_manifest(txt)
        with self.assertRaisesRegex(g.SourceUnavailable,"FIELDS_MISSING"):
            g.parse_original_station_manifest(b"year,latitude\n2019,20\n")

    def test_local_original_manifest_report_is_source_only_no_waterlevel_outcomes(self):
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/"source.json"
            manifest=Path(d)/"public_stations.json"
            with patch.object(g,"_download",return_value=fake_csv()),\
                 patch.object(g,"MIN_SOURCE_STATIONS_WITH_VALID_COORDS",2):
                report=g.run(str(file),str(manifest))
            self.assertTrue(file.exists())
            self.assertTrue(manifest.exists())
            self.assertTrue(report["source_status"].startswith("SOURCE_ADMITTED"))
            self.assertEqual(report["original_global_station_source"][
                "original_unique_physical_UHSLC_stations_by_station_ID"],4)
            content=manifest.read_text()
            self.assertNotIn("sea_level",content)
            self.assertIn("uhslc_id",content)
            self.assertTrue(
                report["none_original_wild_GPS_RWS_2island_or_global_hourly_waterheights_scored"])

    def test_if_all_original_sources_blocked_no_fabricated_count(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)/"report.json"
            def fail(_):
                raise g.SourceUnavailable("SOURCE_UNAVAILABLE_TEST_PUBLIC_PROVIDER")
            with patch.object(g,"_download",side_effect=fail):
                report=g.run(str(dst))
            self.assertEqual(report["source_status"],
              "SOURCE_UNAVAILABLE_V89_GENUINE_UHSLC_GLOBAL_STATION_MANIFEST")
            self.assertNotIn("original_global_station_source",report)
            self.assertEqual(len(report["source_attempts_failure_if_any"]),2)

if __name__=="__main__":
    unittest.main()
