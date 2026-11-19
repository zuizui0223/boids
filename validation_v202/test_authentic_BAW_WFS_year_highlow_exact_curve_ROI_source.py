import json,unittest,urllib.parse
from validation_v202.authentic_BAW_WFS_year_highlow_exact_curve_ROI_source import (
 EXPECTED_ORIGINAL_HITS,MAX_NATIVE_FEATURES,fixed_roi,
 get_exact_original_GeoJSON_request,is_exact_GeoJSON_source_request,
 extract_original_exact_geometrical_intersection
)
class OriginalBAWNativeCurvesNoGeometryPersisted(unittest.TestCase):
    def test_fixed_four_original_source_and_no_site_filter_rescue(self):
        self.assertEqual(list(EXPECTED_ORIGINAL_HITS.values()),[7,52,8,50])
        self.assertEqual(MAX_NATIVE_FEATURES,100)
        for source in EXPECTED_ORIGINAL_HITS:
            u=get_exact_original_GeoJSON_request(source)
            self.assertTrue(is_exact_GeoJSON_source_request(u))
            q=dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(u).query))
            self.assertEqual(q["count"],"100")
            self.assertEqual(q["outputFormat"],"application/json")
        with self.assertRaises(ValueError):
            get_exact_original_GeoJSON_request("invented_2020_layer")
    def test_exact_geometry_rejects_bbox_only_false_positive(self):
        minx,miny,maxx,maxy=fixed_roi()
        feat=[]
        for i in range(7):
            y=(miny+maxy)/2 if i<6 else maxy+1200
            feat.append({"type":"Feature","id":str(i),
                "geometry":{"type":"LineString","coordinates":[
                [minx-1000,y],[maxx+1000,y]]},"properties":{}})
        raw=json.dumps({"type":"FeatureCollection","features":feat,"numberReturned":7}).encode()
        result=extract_original_exact_geometrical_intersection(
            raw,"TrilaWatt_Wattflaechen:high_water_boundary_2018_nl")
        self.assertEqual(result["native_WFS2_original_source_count"],7)
        self.assertEqual(result["n_exact_curve_geometries_intersect_fixed_ROI"],6)
        self.assertEqual(result["n_WFS_BBOX_matched_but_no_true_curve_intersection"],1)
        self.assertGreater(result["original_line_length_clipped_to_public_Vlieland10km_km"],0)
    def test_original_crs_unit_must_be_UTM_meters(self):
        feat=[{"type":"Feature","id":str(i),
               "geometry":{"type":"LineString","coordinates":[[5.0,53.0],[5.1,53.1]]},
               "properties":{}} for i in range(7)]
        raw=json.dumps({"type":"FeatureCollection","features":feat}).encode()
        with self.assertRaisesRegex(ValueError,"EPSG25832"):
            extract_original_exact_geometrical_intersection(
                raw,"TrilaWatt_Wattflaechen:high_water_boundary_2018_nl")
    def test_no_result_cherry_pick_mismatched_count_stops(self):
        raw=json.dumps({"type":"FeatureCollection","features":[]}).encode()
        with self.assertRaisesRegex(ValueError,"FROZEN_V201"):
            extract_original_exact_geometrical_intersection(
                raw,"TrilaWatt_Wattflaechen:high_water_boundary_2018_nl")
if __name__=="__main__":
    unittest.main()
