"""v84C known-truth 345/280 COMPLETE WMR unfiltered original-source logic.

All polygons are synthetically generated. No actual Wadden GPS/biology.
"""
from __future__ import annotations
import json
import unittest

import wmr_original_complete_unfiltered_mid_high_source as v

def fixture(site,*,publisher_count=None,returned=None,bad_code=None,source_next=False):
    n=v.PUBLISHER_FULL_WFS_UNFILTERED_MATCHED[site]
    b=v.FIXED_SITE_BBOX[site]
    lon=(b[0]+b[2])/2
    lat=(b[1]+b[3])/2
    geom={"type":"Polygon","coordinates":[[
        [lon-.005,lat-.005],[lon+.005,lat-.005],
        [lon+.005,lat+.005],[lon-.005,lat+.005],[lon-.005,lat-.005]]]}
    full=[
       {"type":"Feature","properties":{
           "litoralcode":(bad_code if i==0 and bad_code is not None
                          else i%7)},"geometry":geom}
       for i in range(n if returned is None else returned)]
    q={"type":"FeatureCollection","numberMatched":n if publisher_count is None
       else publisher_count,"features":full}
    if source_next:q["next"]="https://provider.invalid/pagination"
    return json.dumps(q).encode()

def fake_from(source_blob):
    def call(params,*,limit):
        assert "CQL_FILTER" not in params
        assert params["count"]=="800"
        assert params["srsName"]=="CRS:84"
        assert limit==v.MAX_GEOJSON_BYTES
        return source_blob
    return call

class OriginalWMRFullUnfilteredSourceKnownTruth(unittest.TestCase):
    def test_fixed_publisher_original_counts_and_robust_codes(self):
        self.assertEqual(v.PUBLISHER_FULL_WFS_UNFILTERED_MATCHED,
            {"Schiermonnikoog":345,"Ameland_Nes":280})
        self.assertEqual(v.TRUE_MIDHIGH,(3,4))
        self.assertEqual(v.MAX_NATIVE_SOURCE_ALL_FEATURES,800)
        self.assertEqual(v.ALL_ORIGINAL_CODES,tuple(range(7)))

    def test_genuine_shaped_original_Schier_complete_unfiltered_source(self):
        site="Schiermonnikoog"
        shapes,report=v._original_full_site(
            site,v.FIXED_SITE_BBOX[site],
            fetch=fake_from(fixture(site)))
        self.assertEqual(
            report["original_full_WFS_GetFeature_NO_CQL_source_count"],345)
        self.assertEqual(report["original_true_received_source_polygon_features"],345)
        self.assertEqual(len(shapes),
            report["source_mid3_selected_native_polygon_count"]+
            report["source_high4_selected_native_polygon_count"])
        self.assertTrue(all(code in (3,4) for _,code in shapes))
        self.assertFalse("coordinates" in json.dumps(report))
        self.assertEqual(report["native_all_litoralcode_0_6_polygon_counts"]["0"],50)
        self.assertTrue(report["original_2019_v1_vs_2021_v2_status"].startswith("UNVERIFIED"))

    def test_original_Ameland_280_all_source_response_complete(self):
        site="Ameland_Nes"
        shapes,report=v._original_full_site(
            site,v.FIXED_SITE_BBOX[site],fetch=fake_from(fixture(site)))
        self.assertEqual(report["original_full_WFS_GetFeature_NO_CQL_source_count"],280)
        self.assertTrue(any(code==3 for _,code in shapes))
        self.assertTrue(any(code==4 for _,code in shapes))
        self.assertEqual(sum(report["native_all_litoralcode_0_6_polygon_counts"].values()),280)

    def test_publisher_reported_more_features_than_retrieved_stops(self):
        site="Schiermonnikoog"
        with self.assertRaisesRegex(v.SourceStop,"NOT_COMPLETE"):
            v._original_full_site(site,v.FIXED_SITE_BBOX[site],
                                  fetch=fake_from(fixture(site,returned=344)))
        with self.assertRaisesRegex(v.SourceStop,"NOT_COMPLETE"):
            v._original_full_site(site,v.FIXED_SITE_BBOX[site],
                                  fetch=fake_from(fixture(site,publisher_count=346)))
        with self.assertRaisesRegex(v.SourceStop,"NOT_COMPLETE"):
            v._original_full_site(site,v.FIXED_SITE_BBOX[site],
                                  fetch=fake_from(fixture(site,source_next=True)))

    def test_native_code2_or_unexpected_code_cannot_be_used_as_midhigh(self):
        site="Ameland_Nes"
        shapes,report=v._original_full_site(
            site,v.FIXED_SITE_BBOX[site],fetch=fake_from(fixture(site,bad_code=2)))
        self.assertEqual(len(shapes),
          report["source_mid3_selected_native_polygon_count"]+
          report["source_high4_selected_native_polygon_count"])
        self.assertTrue(all(code not in (1,2,5,6,0) for _,code in shapes))
        with self.assertRaisesRegex(v.SourceStop,"OUTSIDE_0_6"):
            v._original_full_site(site,v.FIXED_SITE_BBOX[site],
                                  fetch=fake_from(fixture(site,bad_code=12)))

    def test_new_bbox_or_wrong_site_refused_before_source_data(self):
        with self.assertRaisesRegex(v.SourceStop,"SITE_SOURCE_BBOX_CHANGED"):
            v._original_full_site("Ameland_Nes",(4,53,7,54),
                                  fetch=fake_from(b"{}"))
        with self.assertRaisesRegex(v.SourceStop,"UNFROZEN_WMR_SITE"):
            v._original_full_site("NewPlace",(5.3,53.2,6.1,53.6),
                                  fetch=fake_from(b"{}"))

if __name__=="__main__":
    unittest.main()
