"""v85D synthetic two WMR source reads: same shapes different GeoJSON order.

Never original wild GPS or true tide. Source geometric canonical source
must be same even when byte serialization of WFS changes.
"""
import json,unittest
from unittest.mock import patch

from wmr_original_complete_unfiltered_mid_high_source import (
    _original_full_site)
import wmr_original_complete_unfiltered_mid_high_source as m

def polygons(swapped=False,altered=False):
    f=[
      {"type":"Feature","properties":{"litoralcode":2},
       "geometry":{"type":"Polygon","coordinates":[[
         [6.01,53.3],[6.05,53.3],[6.05,53.34],[6.01,53.3]]]}},
      {"type":"Feature","properties":{"litoralcode":3},
       "geometry":{"type":"Polygon","coordinates":[[
         [6.12,53.4],[6.16,53.4],[6.16,53.46],[6.12,53.4]]]}},
      {"type":"Feature","properties":{"litoralcode":4},
       "geometry":{"type":"Polygon","coordinates":[[
         [6.3,53.41],[6.35+(0.001 if altered else 0),53.41],
         [6.35,53.43],[6.3,53.41]]]}}
    ]
    if swapped:f=list(reversed(f))
    return json.dumps({"type":"FeatureCollection","numberMatched":3,
                       "features":f}).encode()

class OriginalWMRCanonicalSourceKnownTruth(unittest.TestCase):
 def get(self,swapped=False,altered=False):
  with patch.dict(m.PUBLISHER_FULL_WFS_UNFILTERED_MATCHED,
                  {"Schiermonnikoog":3}):
   return _original_full_site("Schiermonnikoog",
     (5.70,53.20,6.60,53.70),
     fetch=lambda req,limit:polygons(swapped=swapped,altered=altered))[1]
 def test_original_WFS_raw_order_change_does_not_change_semantic_shapes(self):
  one=self.get()
  two=self.get(swapped=True)
  self.assertNotEqual(
      one["original_full_provider_WFS_response_SHA256_COMPUTED_NOT_PUBLISHER"],
      two["original_full_provider_WFS_response_SHA256_COMPUTED_NOT_PUBLISHER"])
  self.assertEqual(
      one["original_all_0_6_native_litoralcode_normalized_geometry_SHA256"],
      two["original_all_0_6_native_litoralcode_normalized_geometry_SHA256"])
  self.assertEqual(one["original_normalized_source_all_features_count"],3)
 def test_actual_original_geometry_change_not_hidden_by_canonical_sorting(self):
  one=self.get()
  changed=self.get(altered=True)
  self.assertNotEqual(
      one["original_all_0_6_native_litoralcode_normalized_geometry_SHA256"],
      changed["original_all_0_6_native_litoralcode_normalized_geometry_SHA256"])
 def test_class_low_littoral_does_not_become_eligible_source_polygon(self):
  with patch.dict(m.PUBLISHER_FULL_WFS_UNFILTERED_MATCHED,
                  {"Schiermonnikoog":3}):
   polygons_used,qa=_original_full_site(
      "Schiermonnikoog",(5.70,53.20,6.60,53.70),
      fetch=lambda req,limit:polygons())
  self.assertEqual([x[1] for x in polygons_used],[3,4])
  self.assertEqual(qa["native_all_litoralcode_0_6_polygon_counts"]["2"],1)
  self.assertTrue(qa["no_low_littoral2_geometry_or_biology_included"])
if __name__=="__main__":
 unittest.main()
