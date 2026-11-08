"""v84 synthetic corrected-boundary-immune mid/high littoral source masking.

All vectors here are fabricated and not authentic Wadden habitat or birds.
"""
from __future__ import annotations
from hashlib import sha256
import json
import unittest
import numpy as np
import shapely
from shapely.geometry import box
from unittest.mock import patch

import wmr_original_midhigh_native_nioz_grid_source as v

def _gps_source_center_geo(lon,lat):
    return shapely.transform(
        box(lon-.012,lat-.012,lon+.012,lat+.012),
        lambda c:c*np.array([v.METRIC_X,v.METRIC_Y]))

def sample_wfs(*,bad_low_code=False,overflow=False):
    polygons=[
      {"type":"Feature","properties":{"litoralcode":3},
       "geometry":{"type":"Polygon","coordinates":[[
         [6.04,53.39],[6.08,53.39],[6.08,53.43],
         [6.04,53.43],[6.04,53.39]]]}},
      {"type":"Feature","properties":{"litoralcode":2 if bad_low_code else 4},
       "geometry":{"type":"Polygon","coordinates":[[
          [6.12,53.44],[6.15,53.44],[6.15,53.47],
          [6.12,53.47],[6.12,53.44]]]}}
    ]
    return json.dumps({
        "type":"FeatureCollection","numberMatched":3 if overflow else 2,
        "features":polygons}).encode()

class WMRMidHighOnlySiteSourceKnownTruth(unittest.TestCase):
    def test_original_code3_4_completely_excludes_low_boundary_code2(self):
        self.assertEqual(v.FIXED_CODES,(3,4))
        self.assertEqual(v.SOURCE_LOWER_LITTORAL_CODE_NEVER_USED,2)
        self.assertEqual(v.NIOZ_ORIGINAL_SHA,
            "f8df67d7351754173978364cd89afbf3a2bba4f3a4f85ef270b1090c14e72bad")
        self.assertEqual(v.SOURCE_MIN_GRID_CELLS_PER_SITE,100)
        self.assertEqual(len(v.FIXED_SITE_BBOX),2)

    def test_publisher_geojson_source_accepts_only_true_mid_high_polygons(self):
        def getter(req,limit):
            self.assertEqual(req["CQL_FILTER"],"litoralcode IN (3,4)")
            self.assertEqual(req["srsName"],"CRS:84")
            return sample_wfs()
        shapes,info=v._wfs_region(
            "Schiermonnikoog",v.FIXED_SITE_BBOX["Schiermonnikoog"],
            fetch=getter)
        self.assertEqual(info["actual_received_full_geojson_polygons"],2)
        self.assertEqual(info["published_original_mid_littoral3_polygon_count"],1)
        self.assertEqual(info["published_original_high_littoral4_polygon_count"],1)
        self.assertEqual([q[1] for q in shapes],[3,4])
        self.assertNotIn("coordinates",json.dumps(info))

    def test_original_provider_returning_low_littoral_must_stop(self):
        with self.assertRaisesRegex(v.SourceStop,"OUTSIDE_MIDHIGH"):
            v._wfs_region("Schiermonnikoog",
                v.FIXED_SITE_BBOX["Schiermonnikoog"],
                fetch=lambda p,limit:sample_wfs(bad_low_code=True))
        with self.assertRaisesRegex(v.SourceStop,"MORE_POLYGONS"):
            v._wfs_region("Schiermonnikoog",
                v.FIXED_SITE_BBOX["Schiermonnikoog"],
                fetch=lambda p,limit:sample_wfs(overflow=True))

    def test_actual_native_grid_points_classed_with_geometry_not_naive_litoralcod_number(self):
        # Source-only toy geographic grid points, no NIOZ model exposure field
        lat=np.array([53.41,53.455,53.5,53.40])
        lon=np.array([6.06,6.135,6.2,5.90])
        polygons=[
            (_gps_source_center_geo(6.06,53.41),3),
            (_gps_source_center_geo(6.135,53.455),4)]
        a=v._overlay_model_centers(
            lat,lon,polygons,site="Schiermonnikoog")
        self.assertEqual(a["WMR_original_code3_mid_littoral_NATIVE_2010_model_center_count"],1)
        self.assertEqual(a["WMR_original_code4_high_littoral_NATIVE_2010_model_center_count"],1)
        self.assertEqual(a["mid_high_littoral_NATIVE_2010_model_centers_source_only"],2)
        self.assertEqual(a["native_original_WMR_mid_vs_high_conflicting_model_centers"],0)
        self.assertTrue(a["source_mapping_only_no_GPS_or_NIOZ_time_expo_values"])

    def test_conflicting_mid_high_source_polygons_rejected_not_doublecounted(self):
        lat=np.array([53.41,53.41,53.455,53.46])
        lon=np.array([6.06,6.06,6.14,6.15])
        same=_gps_source_center_geo(6.06,53.41)
        with self.assertRaisesRegex(v.SourceStop,"OVERLAP_CONFLICT"):
            v._overlay_model_centers(
                lat,lon,[(same,3),(same,4)],
                site="Schiermonnikoog")

if __name__=="__main__":unittest.main()
