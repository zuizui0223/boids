"""v84B synthetic WMR WFS bounded query HTTP semantics, no biology."""
import unittest,json
import wmr_wfs_http500_diagnostics as m

class OriginalWMRWFSQueryShapeSafety(unittest.TestCase):
 def test_fix_all_predeclared_http_methods_and_class_codes(self):
  self.assertEqual([x[0] for x in m.QUERY_SETTINGS],
    ["CQL_hits","CQL10","UNFILTERED10","CQL3_10","CQL100"])
  self.assertEqual(m.EXPECTED_CLASSES,(3,4))
 def test_synthetic_geojson_original_class_metadata_only(self):
  binary=json.dumps({"type":"FeatureCollection","numberMatched":1,
     "features":[{"properties":{"litoralcode":3,"gps_secret":"not_used"},
       "geometry":{"type":"Polygon","coordinates":[[[0,0],[1,0],[0,1],[0,0]]]}}]}).encode()
  a=m.parse_native_return(200,binary,None)
  self.assertEqual(a["status"],"SOURCE_WFS_ORIGINAL_GEOJSON_SAMPLE")
  self.assertEqual(a["actual_original_class_sample_counts"],{"3":1})
  self.assertNotIn("gps_secret",str(a))
  self.assertNotIn("coordinates",str(a))
 def test_actual_http500_error_cannot_be_classified_as_source_field(self):
  x=m.parse_native_return(500,b"","Original WFS internal error")
  self.assertEqual(x["status"],"SOURCE_HTTP_OR_NETWORK_ERROR")
 def test_source_resulttype_hits_xml_is_not_original_polygon(self):
  x=m.parse_native_return(200,
      b'<wfs:FeatureCollection xmlns:wfs="http://www.opengis.net/wfs/2.0" numberMatched="245" numberReturned="0"/>',
      None)
  self.assertEqual(x["reported_numberMatched"],"245")
  self.assertEqual(x["status"],"SOURCE_WFS_NON_GEOJSON_HITS")
 def test_mock_5_original_shapes_no_changes_to_actual_bbox(self):
  def fake(q):
   if q.get("CQL_FILTER"):
    return 500,b"","synthetic WFS error"
   return 200,json.dumps({"type":"FeatureCollection",
       "features":[{"type":"Feature","properties":{"litoralcode":4},
                    "geometry":{"type":"Polygon","coordinates":[]}}]}).encode(),None
  samples=m.diagnostic_one_site("Schiermonnikoog",
      m.FIXED_SITE_BBOX["Schiermonnikoog"],fetch=fake)
  self.assertEqual(len(samples),5)
  self.assertEqual(samples["CQL10"]["http_status"],500)
  self.assertEqual(samples["UNFILTERED10"]["source_native_returned_features"],1)

if __name__=="__main__":unittest.main()
