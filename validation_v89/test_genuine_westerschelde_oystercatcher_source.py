"""v89 synthetic original Westerschelde public Zenodo GPS source tests only.

No actual bird IDs, individual exact locations, real RWS tide values,
sun angle, original habitats, or animal location-use effect is modeled.
"""
from __future__ import annotations
from datetime import datetime,timedelta
from io import BytesIO,StringIO
from unittest.mock import patch
import csv,gzip,hashlib,json,unittest

import genuine_westerschelde_oystercatcher_source as v

def fake_original_zip_gps(*,year=2018,birds=8,fixes_per_month_bird=90,
                          months=(6,7,8),in_coast=True):
    text=StringIO()
    f=("event-id","timestamp","location-lat","location-long",
       "individual-local-identifier","visible","original_outcome_UNUSED")
    writer=csv.DictWriter(text,fieldnames=f);writer.writeheader()
    row=0
    for m in months:
        for b in range(birds):
            for j in range(fixes_per_month_bird):
                t=datetime(year,m,1)+timedelta(hours=j)
                writer.writerow({
                    "event-id":str(row),
                    "timestamp":t.strftime("%Y-%m-%d %H:%M:%S"),
                    "location-lat":51.30 if in_coast else 49.0,
                    "location-long":3.80 if in_coast else 7.0,
                    "individual-local-identifier":f"SYNTHETIC_WEST_SCHELDT_{b}",
                    "visible":"TRUE",
                    "original_outcome_UNUSED":"flood_night_positive_fake"})
                row+=1
    return gzip.compress(text.getvalue().encode("utf-8"),mtime=0),row

def fake_publisher(*,alter_checksum=False):
    mock={}
    files=[]
    for name in v.ALLOWED_FILES:
        content=b"original_publisher_synthetic_"+name.encode()
        actual=hashlib.md5(content).hexdigest()
        checksum=actual if not alter_checksum else "f"*32
        mock[name]=content
        files.append({
            "key":name,
            "size":len(content),
            "checksum":"md5:"+checksum,
            "links":{"self":"https://zenodo.org/api/records/10053702/files/"+name+"/content"}})
    record={"id":10053702,"files":files}
    def client(url,cap):
        if url==v.ZENODO_META:
            return json.dumps(record).encode()
        if "/files/" in url:
            key=url.split("/files/")[-1].removesuffix("/content")
            return mock[key]
        raise AssertionError("unregistered source URL "+url)
    return client,mock

class GenuineIndependentEstuarySourceKnownTruth(unittest.TestCase):
    def test_immutable_original_gps_publisher_md5_and_geography(self):
        self.assertEqual(v.SOURCE_DOI,"10.5281/zenodo.10053702")
        self.assertEqual(v.YEARS,(2018,2019,2020))
        self.assertEqual(v.ORIGINAL_GPS_FILES[2018][1],
                         "2d37d87d42fe23925f1ab5869f9b49f2")
        self.assertEqual(v.ORIGINAL_GPS_FILES[2019][1],
                         "ba0bf9f1fd1bcc415a0505485d3f4f27")
        self.assertEqual(v.ORIGINAL_GPS_FILES[2020][1],
                         "255beb9052fd84f93c3aeb4d621f5d36")
        self.assertEqual(v.SOURCE_BBOX,(50.9,51.65,3.0,4.7))
        self.assertEqual(v.EXPECTED_TAGGED_IN_PUBLICATION,13)

    def test_original_manifest_blocks_changed_publisher_MD5(self):
        client,_=fake_publisher()
        with patch.dict(v.ALLOWED_FILES,{k:hashlib.md5(
                b"original_publisher_synthetic_"+k.encode()).hexdigest()
                for k in v.ALLOWED_FILES},clear=True):
            meta,receipt=v.original_manifest(fetch=client)
        self.assertEqual(len(meta),5)
        self.assertEqual(receipt["original_source_DOI"],v.SOURCE_DOI)
        self.assertNotIn("SYNTHETIC_WEST_SCHELDT",str(receipt))
        client,_=fake_publisher(alter_checksum=True)
        with self.assertRaisesRegex(v.SourceStop,"PUBLISHER_MD5_DRIFT"):
            v.original_manifest(fetch=client)

    def test_original_2018_bird_hours_qualify_as_SOURCE_not_2018_tide_effect(self):
        zipfile,n=fake_original_zip_gps()
        q=v.original_native_hourly_GPS(zipfile,2018)
        self.assertEqual(n,8*3*90)
        self.assertEqual(q["source_original_raw_GPS_event_rows"],2160)
        self.assertEqual(q["source_original_valid_native_bird_IDs_in_year"],8)
        self.assertEqual(q["source_original_hourly_GPS_fixes_in_any_WGS84_area"],2160)
        self.assertEqual(q["original_fixed_WesterScheldt_EastFlanders_source_region_GPS_hours"],2160)
        self.assertEqual(q["original_2018_2020_genuine_source_months_5birds_200hours"],[6,7,8])
        self.assertEqual(q["original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"],
                         "CANDIDATE_YEAR_WITH_GPS_BIRD_SOURCE_ONLY")
        self.assertNotIn("SYNTHETIC_WEST_SCHELDT",str(q))
        self.assertNotIn("flood_night_positive_fake",str(q))
        self.assertTrue(q["NO_actual_original_tide_or_sunlight_or_foraging_habitat_response"])

    def test_fewer_original_animal_birds_or_wrong_geography_does_not_get_admitted(self):
        binary,n=fake_original_zip_gps(birds=7)
        q=v.original_native_hourly_GPS(binary,2018)
        self.assertEqual(q["source_original_valid_native_bird_IDs_in_year"],7)
        self.assertIn("NOT_ADMITTED",q[
            "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"])
        binary,n=fake_original_zip_gps(in_coast=False)
        q=v.original_native_hourly_GPS(binary,2018)
        self.assertEqual(q[
            "original_fixed_WesterScheldt_EastFlanders_source_region_GPS_hours"],0)
        self.assertIn("NOT_ADMITTED",q[
            "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"])

    def test_2020_is_source_only_not_favorable_temporal_frame_rescue(self):
        binary,n=fake_original_zip_gps(year=2020)
        q=v.original_native_hourly_GPS(binary,2020)
        self.assertEqual(q["source_original_valid_native_bird_IDs_in_year"],8)
        self.assertIn("NOT_PRIMARY_YEAR",q[
            "original_source_status_candidate_for_separate_RWS_tide_and_ecotope_test"])
        with self.assertRaisesRegex(v.SourceStop,"UNREGISTERED_ORIGINAL_YEAR"):
            v.original_native_hourly_GPS(binary,2021)

if __name__=="__main__":
    unittest.main()
