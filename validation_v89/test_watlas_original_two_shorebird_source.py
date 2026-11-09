"""v89 synthetic known truths for authentic-source WATLAS Fig13/14 only.

No synthetic value here is presented as real wild bird ecology, tide phase,
measured West Terschelling gauge or independently replicated effect.
"""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import numpy as np
from pyproj import Transformer

import watlas_original_two_shorebird_source as v

def fake_original_watlas_csv(*,bad_coords=False,nonunix=False):
    lines=[
     "TAG,TIME,X,Y,NBS,VARX,VARY,COVXY,ts,tideID,tidaltime,waterlevel"]
    proj=Transformer.from_crs("EPSG:4326","EPSG:32631",always_xy=True)
    x,y=proj.transform(5.25,53.26)
    if bad_coords:x=1000
    import datetime
    for tag in ("SYNTHETIC_KNOT_A","SYNTHETIC_KNOT_B"):
        for day in (1,2):
            for hour in (0,13):
                dt=datetime.datetime(2018,8,day,hour,30,
                                     tzinfo=datetime.timezone.utc)
                tm=dt.timestamp()
                if nonunix:tm=tm*1000
                t="tide1" if hour==0 else "tide2"
                lines.append(
                  f"{tag},{tm},{x},{y},4,15,17,2,UNVERIFIED_CET,{t},"
                  +("-120,40" if hour==0 else "110,-100"))
    return ("\n".join(lines)+"\n").encode()

class WATLASSyntheticSourceOnly(unittest.TestCase):
    def test_original_figshare_two_taxa_and_exact_sources_frozen(self):
        self.assertEqual(v.FIGSHARE_ORIGINAL["Red_knot"]["article_id"],26553446)
        self.assertEqual(v.FIGSHARE_ORIGINAL["Sanderling"]["article_id"],26553443)
        self.assertEqual(v.FIGSHARE_ORIGINAL["Red_knot"]["doi"],
                         "10.6084/m9.figshare.26553446.v1")
        self.assertEqual(v.FIGSHARE_ORIGINAL["Sanderling"]["doi"],
                         "10.6084/m9.figshare.26553443.v1")
        self.assertEqual(v.TRACKING_SOURCE_YEAR,2018)
        self.assertEqual(v.MIN_BIRD_WATLAS_RECEIVERS,3)

    def test_original_unix_UTM_waterlevel_and_daynight_source_anonymous(self):
        b=fake_original_watlas_csv()
        r=v.audit_watlas_CSV(b,"Red_knot")
        self.assertEqual(r["original_source_total_CSV_rows_including_source_invalid"],8)
        self.assertEqual(r["original_source_valid_genuine_WATLAS_localizations"],8)
        self.assertEqual(r["original_SOURCE_TAG_count_not_necessarily_independent_recaptures"],2)
        self.assertEqual(r["source_TAGs_with_original_positions_in_both_astroDAY_NIGHT"],2)
        self.assertEqual(r["source_time_relative_to_high_tide_sign_counts"],
                         {"before_high":4,"after_high":4})
        self.assertEqual(r["source_date_year_counts"],{"2018":8})
        self.assertGreaterEqual(r["source_original_tide_cycles_per_TAG_unique"],4)
        self.assertNotIn("SYNTHETIC_KNOT_A",str(r))
        self.assertNotIn("UNVERIFIED_CET",str(r))
        self.assertNotIn("153308",str(r))
        self.assertTrue(r["no_tidal_solar_animal_movement_or_habitat_effect_scored"])

    def test_original_UTM_GPS_outside_wadden_source_is_rejected_not_remapped(self):
        b=fake_original_watlas_csv(bad_coords=True)
        with self.assertRaisesRegex(v.SourceStop,"NO_VALID_ORIGINAL"):
            v.audit_watlas_CSV(b,"Red_knot",check_solar=False)

    def test_original_time_unix_seconds_not_milliseconds_or_CET(self):
        b=fake_original_watlas_csv(nonunix=True)
        with self.assertRaisesRegex(v.SourceStop,"NO_VALID_ORIGINAL"):
            v.audit_watlas_CSV(b,"Sanderling",check_solar=False)

    def test_actual_springer_exact_file_returns_local_sha_not_provider_MD5(self):
        fake=fake_original_watlas_csv()
        spec=v.FIGSHARE_ORIGINAL["Sanderling"]
        def f(url,cap,allowed_metadata_host=None):
            self.assertEqual(url,spec["springer_publisher_csv"])
            self.assertEqual(cap,v.MAX_PUBLISHER_CSV_BYTES)
            return fake,{}
        b,p=v.original_csv(spec,fetch=f)
        self.assertEqual(b,fake)
        self.assertFalse(p["source_MD5_provider_verified"])
        self.assertEqual(p["original_path"],"SPRINGER_EXACT_PUBLISHED_ADDITIONAL_FILE")

    def test_fallback_only_literal_public_figshare_file_with_real_provider_MD5(self):
        spec=v.FIGSHARE_ORIGINAL["Red_knot"]
        data=fake_original_watlas_csv()
        import hashlib
        file={"id":1122,"name":"supplemental14.csv",
              "size":len(data),"computed_md5":hashlib.md5(data).hexdigest(),
              "download_url":"https://ndownloader.figshare.com/files/1122"}
        def fetch(url,cap,allowed_metadata_host=None):
            if url==spec["springer_publisher_csv"]:
                raise v.SourceStop("SOURCE_UNAVAILABLE_SPRINGER")
            if url==f"https://api.figshare.com/v2/articles/{spec['article_id']}":
                return json.dumps({"id":spec["article_id"],"doi":spec["doi"],
                                   "files":[file]}).encode(),{}
            if url==file["download_url"]:
                return data,{}
            raise AssertionError("unpublished URL")
        b,meta=v.original_csv(spec,fetch=fetch)
        self.assertEqual(b,data)
        self.assertTrue(meta["source_MD5_provider_verified"])
        self.assertEqual(meta["real_original_file_ID"],1122)

    def test_provider_bad_md5_source_stop_no_misleading_biological_result(self):
        spec=v.FIGSHARE_ORIGINAL["Red_knot"]
        data=fake_original_watlas_csv()
        file={"id":1122,"name":"data.csv","size":len(data),
              "computed_md5":"f"*32,
              "download_url":"https://ndownloader.figshare.com/files/1122"}
        def fetch(url,cap,allowed_metadata_host=None):
            if url==spec["springer_publisher_csv"]:
                raise v.SourceStop("SOURCE_UNAVAILABLE_SPRINGER")
            if "api.figshare.com" in url:return json.dumps(
                {"id":spec["article_id"],"doi":spec["doi"],"files":[file]}).encode(),{}
            return data,{}
        with self.assertRaisesRegex(v.SourceStop,"MD5_PROVIDER_MISMATCH"):
            v.original_csv(spec,fetch=fetch)

if __name__=="__main__":
    unittest.main()
