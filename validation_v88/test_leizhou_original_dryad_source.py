"""v88 original China Dryad source safety tests; all inputs SYNTHETIC.

Tests source DOI/version selection, publication-only file identity, public
download/HTTP stop, original UTC GPS COLLECTING vs transmission time,
ZIP path traversal rejection and no leaked source animal/device serial IDs.
"""
from __future__ import annotations

from io import BytesIO
from unittest.mock import patch
from zipfile import ZipFile
import json
import unittest

import leizhou_original_dryad_source as v

def fake_metadata(url,client=None):
    if url.endswith("/versions"):
        return {"_embedded":{"stash:versions":[{
            "id":444,"versionNumber":1,"publicationDate":"2026-06-04T00:00:00Z"}]}}
    if url.endswith("/versions/444/files"):
        return {"_embedded":{"stash:files":[
            {"id":123,"path":"Raw_data.zip","size":1000000},
            {"id":124,"path":"README.md","size":11000}
        ]}}
    if url.endswith(v.ENCODED):
        return {"identifier":v.DRYAD_DOI,
                "title":"Shorebird GPS tracking, survey data and habitat map at Leizhou, China"}
    raise AssertionError("Unknown original synthetic API "+url)

def synthetic_original_nested_zip(*,badclock=False):
    rows=[
        "S/N,UUID,Collecting time,Transmitting time,Longitude,Latitude,HorAccuracy",
        "123,U1,"+("2020-11-25T04:37:49" if badclock else
                   "2020-11-25T04:37:49Z")+
                ",2020-11-26T10:37:49Z,110.2,20.8,8.5",
        "123,U1,2020-11-25T05:37:49Z,2020-11-27T04:00:00Z,110.21,20.81,9",
        "456,U2,2020-11-25T06:37:49Z,2020-11-27T05:00:00Z,110.2,20.7,2",
    ]
    rows.extend([
        f"123,U1,2020-11-25T{hour:02d}:37:49Z,2020-11-27T04:00:00Z,110.20,20.80,8.5"
        for hour in range(7,16)
    ])
    with BytesIO() as b:
        with ZipFile(b,"w") as z:
            z.writestr("tracking data/GPS records.csv","\n".join(rows))
            z.writestr("SN to id.txt",
                "S/N\tid\n123\tRedshank one\n456\tPlover one\n")
            z.writestr("Habitat mapping scheme.txt",
                "0: tidal flat\n1: aquaculture pond\n")
            z.writestr("Habitat map.tif",b"synthetic_geotiff_not_real")
        return b.getvalue()

class LeizhouOriginalPublicDryadKnownTruth(unittest.TestCase):
    def test_four_published_species_source_expectations_not_twenty_independent_tags(self):
        self.assertEqual(v.DOI,"10.5061/dryad.51c59zwm3")
        self.assertEqual(v.PUBLIC_VERSION_DATE,"2026-06-04")
        self.assertEqual(v.ORIGINAL_EXPECTED_TAXA,{
            "Tringa totanus":9,
            "Pluvialis squatarola":3,
            "Charadrius leschenaultii":2,
            "Calidris canutus":2})
        self.assertEqual(sum(v.ORIGINAL_EXPECTED_TAXA.values()),16)
        self.assertEqual(v.MAX_PACKAGED_DOWNLOAD,12000000)

    def test_correct_2026_original_version_file_ids_from_public_metadata_only(self):
        with patch.object(v,"_json",side_effect=fake_metadata):
            result=v.metadata_source()
        q=result["sanitized_receipt"]
        self.assertEqual(q["original_DOI"],v.DOI)
        self.assertEqual(q["chosen_Dryad_version_ID"],"444")
        self.assertEqual(
            [a["true_original_filename"] for a in q["original_source_files"]],
            ["Raw_data.zip","README.md"])

    def test_dont_use_transmission_time_instead_of_gps_collection_UTC(self):
        self.assertEqual(v._gps_time("2020-11-25T04:37:49Z").year,2020)
        with self.assertRaises(ValueError):
            v._gps_time("2020-11-25T04:37:49")
        with self.assertRaises(ValueError):
            v._gps_time("")

    def test_synthetic_original_nested_zip_provides_source_header_only(self):
        q=v.raw_zip_source_summary(synthetic_original_nested_zip())
        self.assertEqual(q["original_GPS_source_raw_rows"],12)
        self.assertEqual(q["original_GPS_source_valid_UTC_WGS84_rows"],12)
        self.assertEqual(q["original_GPS_source_device_serial_count_NOT_equivalent_to_independent_birds"],2)
        self.assertEqual(q["original_years"],{2020:12})
        self.assertEqual(q["original_2019_2020_2021_calendar_months_source_counts"],{"2020-11":12})
        self.assertNotIn("110.21",str(q))
        self.assertNotIn("Redshank one",str(q))
        self.assertNotIn("2020-11-25T04:37:49Z",str(q))
        self.assertTrue(q["no_tide_solar_habitat_outcome_was_scored"])

    def test_zip_cannot_traverse_or_escape_source(self):
        b=BytesIO()
        with ZipFile(b,"w") as z:
            z.writestr("../secret-tracks.csv",b"test")
        with self.assertRaisesRegex(v.SourceStop,"ORIGINAL_PUBLIC_ZIP_UNSAFE"):
            v.zip_members(b.getvalue())

    def test_source_public_api_unauthorized_reports_failure_not_fake_wild_result(self):
        with patch.object(v,"metadata_source",
            side_effect=v.SourceStop("SOURCE_UNAVAILABLE_V88_ORIGINAL_DRYAD_PUBLIC_HTTP_401")):
            with __import__("tempfile").TemporaryDirectory() as d:
                dst=__import__("pathlib").Path(d)/"result.json"
                q=v.run(str(dst))
                self.assertTrue(dst.exists())
        self.assertIn("NOT_PUBLICLY_ACCESSIBLE",q["public_Dryad_source_API_status"])
        self.assertNotIn("original_GPS_and_habitat_source_preflight",q)

if __name__=="__main__":
    unittest.main()
