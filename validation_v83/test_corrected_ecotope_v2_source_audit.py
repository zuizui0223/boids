"""v83 synthetic source known-truth: corrected ecotope v2 metadata, codes, CRS.

All generated SQLite/ZIP content is SYNTHETIC, never actual Wadden ecotope
polygons or GPS/wild-animal outcomes. Original version 1 must be rejected.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zipfile import ZipFile
from io import BytesIO
import json
import sqlite3
import unittest

from pyproj import CRS

import corrected_ecotope_v2_source_audit as s

def fixture_api(version=2,*,sha=True):
    content=b"Original-publisher-UUID-known-truth-synthetic"
    f={
      "id":"17c984af-e881-488e-ae91-f857b1f4d0ed",
      "filename":s.ARCHIVE,
      "size":len(content),
      "content_details":{"sha256_hash":sha256(content).hexdigest() if sha else None}}
    def request(endpoint):
        if endpoint.startswith("/datasets/"+s.SOURCE_ID+"?"):
            return {"id":s.SOURCE_ID,"version":version,
                    "doi":{"id":s.EXPECTED_DOI if version==2 else
                          "10.17632/27mysx289g.1"},"name":s.DATASET_NAME}
        if endpoint.startswith("/datasets/"+s.SOURCE_ID+"/files?"):
            return [f]
        raise AssertionError("unapproved endpoint: "+endpoint)
    return request,content

def synthetic_ecotope_gpkg(path,*,native_class=True,codebook=True):
    con=sqlite3.connect(path)
    con.executescript("""
        CREATE TABLE gpkg_contents (
            table_name TEXT PRIMARY KEY, data_type TEXT, identifier TEXT,
            description TEXT DEFAULT '', last_change TEXT DEFAULT '',
            min_x REAL,min_y REAL,max_x REAL,max_y REAL,srs_id INTEGER);
        CREATE TABLE gpkg_spatial_ref_sys (
            srs_name TEXT,srs_id INTEGER PRIMARY KEY, organization TEXT,
            organization_coordsys_id INTEGER, definition TEXT, description TEXT);
        CREATE TABLE gpkg_geometry_columns(
            table_name TEXT,column_name TEXT,geometry_type_name TEXT,
            srs_id INTEGER,z TINYINT,m TINYINT);
        CREATE TABLE EcotopeWS3_mp(
            fid INTEGER PRIMARY KEY, geom BLOB, LitoralCod INTEGER);
        CREATE TABLE EcotopeWS3CodeInterpretation(
            native_field TEXT, meaning TEXT);
        CREATE TABLE ZESsmpleCode2Legend(code TEXT,label TEXT);
    """)
    con.execute("INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)",
        ("WGS84",4326,"EPSG",4326,CRS.from_epsg(4326).to_wkt(),""))
    for name,datatype in [
        ("EcotopeWS3_mp","features"),
        ("EcotopeWS3CodeInterpretation","attributes"),
        ("ZESsmpleCode2Legend","attributes")]:
        con.execute("INSERT INTO gpkg_contents(table_name,data_type,identifier,min_x,min_y,max_x,max_y,srs_id)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (name,datatype,name,5.,53.,7.,54.,4326))
    con.execute("INSERT INTO gpkg_geometry_columns VALUES (?,?,?,?,?,?)",
                ("EcotopeWS3_mp","geom","MULTIPOLYGON",4326,0,0))
    for cod in range(7):
        con.execute("INSERT INTO EcotopeWS3_mp(fid,LitoralCod) VALUES (?,?)",
                    (cod+1,cod))
    if codebook:
        con.execute("INSERT INTO EcotopeWS3CodeInterpretation VALUES (?,?)",
             ("LitoralCod","littoral depth by mean exposure, corrected 4 percent low"))
    else:
        con.execute("INSERT INTO EcotopeWS3CodeInterpretation VALUES (?,?)",
             ("unknown","unverified source class"))
    con.execute("INSERT INTO ZESsmpleCode2Legend VALUES (?,?)",
                ("Low","low intertidal littoral"))
    if not native_class:
        con.execute('ALTER TABLE EcotopeWS3_mp RENAME COLUMN LitoralCod TO unknown')
    con.commit()
    con.close()

def original_shaped_zip(path):
    buf=BytesIO()
    with ZipFile(buf,"w") as archive:
        archive.write(path,"EctpWZ3L_gpkg/Map.gpkg")
    return buf.getvalue()

class OriginalCorrectedEcotopeKnownTruth(unittest.TestCase):
    def test_original_corrected_v2_dataset_and_publisher_SHA(self):
        call,payload=fixture_api()
        with patch.object(s,"_api_json",side_effect=call):
            file,origin=s.publisher_metadata()
        self.assertEqual(origin["source_version_2021_corrected"],2)
        self.assertEqual(origin["source_published_DOI"],s.EXPECTED_DOI)
        self.assertTrue(origin["source_v2_2019_low_intertidal_4pct_correction_required"])
        def fake_download(url,cap,expected_host):
            self.assertIn(file["original_file_UUID"],url)
            self.assertEqual(expected_host,"api.data.mendeley.com")
            return payload,{}
        data,receipt=s.download_publisher_zip(file,fetch=fake_download)
        self.assertEqual(receipt["original_download_SHA256"],sha256(data).hexdigest())
        self.assertTrue(receipt["publisher_SHA256_available_and_verified"])

    def test_wrong_v1_corrected_source_hard_stops(self):
        call,_=fixture_api(1)
        with patch.object(s,"_api_json",side_effect=call):
            with self.assertRaisesRegex(s.SourceStop,"WRONG_ORIGINAL_PUBLISHED_VERSION"):
                s.publisher_metadata()
        self.assertEqual(s.SOURCE_VERSION,2)
        self.assertEqual(s.LITTORAL_CODES,(2,3,4))
        self.assertNotIn(1,s.LITTORAL_CODES)

    def test_missing_publisher_digest_is_not_labeled_verified(self):
        call,payload=fixture_api(sha=False)
        with patch.object(s,"_api_json",side_effect=call):
            file,_=s.publisher_metadata()
        data,receipt=s.download_publisher_zip(file,
            fetch=lambda url,cap,expected_host:(payload,{}))
        self.assertFalse(receipt["publisher_SHA256_available_and_verified"])
        altered={**file,"publisher_sha256_or_null":"a"*64}
        with self.assertRaisesRegex(s.SourceStop,"SHA256_NOT_PUBLISHER"):
            s.download_publisher_zip(altered,
                fetch=lambda url,cap,expected_host:(payload,{}))

    def test_class2_3_4_native_corrected_legend_and_site_coordinates(self):
        with TemporaryDirectory() as td:
            p=Path(td)/"test.gpkg"
            synthetic_ecotope_gpkg(p)
            summary=s.geopackage_source_audit(p)
            self.assertEqual(summary["original_GPKG_integrity_check"],"ok")
            self.assertEqual(summary["true_littoral_class_count_from_corrected_polygons"],3)
            self.assertEqual(summary["original_native_polygon_srs_id"],4326)
            self.assertTrue(all(x["public_station_inside_polygon_LAYER_bounds"] for x
                in summary["original_source_map_layer_geographic_station_bounds"].values()))
            self.assertEqual(summary["original_litoralcode_class_polygon_counts"]["4"],1)
            archive=original_shaped_zip(p)
            with ZipFile(BytesIO(archive)) as z:
                self.assertEqual(len(z.infolist()),1)
            seen=[]
            for tmpfile,receipt in s.selected_gpkg_from_zip(archive):
                seen.append(s.geopackage_source_audit(tmpfile))
                self.assertGreater(receipt["zip_GPKG_original_member_size"],1000)
            self.assertEqual(len(seen),1)

    def test_unverified_native_littoral_code_or_missing_column_stops(self):
        with TemporaryDirectory() as d:
            p=Path(d)/"map.gpkg"
            synthetic_ecotope_gpkg(p,codebook=False)
            with self.assertRaisesRegex(s.SourceStop,"CODEBOOK_UNVERIFIED"):
                s.geopackage_source_audit(p)
            p2=Path(d)/"bad.gpkg"
            synthetic_ecotope_gpkg(p2,native_class=False)
            with self.assertRaisesRegex(s.SourceStop,"LITORALCOD_ABSENT"):
                s.geopackage_source_audit(p2)

    def test_zip_path_traversal_refused_no_animal_data(self):
        buff=BytesIO()
        with ZipFile(buff,"w") as archive:
            archive.writestr("../hidden-original.gpkg",b"not_a_data_file")
        with self.assertRaisesRegex(s.SourceStop,"UNSAFE_ZIP"):
            list(s.selected_gpkg_from_zip(buff.getvalue()))

if __name__=="__main__":
    unittest.main()
