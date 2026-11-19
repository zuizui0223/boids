import unittest
import numpy as np
from validation_v204.authentic_BAW_mask_turnover_near_annual_tide_lines import (
 FIXED_CURVE_CLIPPED_LENGTH_KM, FIXED_TOPO_SHA256, FIXED_MASK_COUNTS,
 BINS_METERS, BIN_NAMES, semantic_original_geojson_fingerprint,
 canonical_classes, bin_source_masks, risk_ratio_near_far, quadrants
)

class FrozenOriginalSourceMaskMechanismControls(unittest.TestCase):
    def test_source_previous_counts_and_yearly_binary_sha_locked(self):
        self.assertEqual(FIXED_MASK_COUNTS["2018_valid"],247437)
        self.assertEqual(FIXED_MASK_COUNTS["2019_valid"],219396)
        self.assertEqual(FIXED_MASK_COUNTS["both"],215587)
        self.assertEqual(FIXED_MASK_COUNTS["2018_only"],31850)
        self.assertEqual(FIXED_MASK_COUNTS["2019_only"],3809)
        self.assertEqual(sum(FIXED_MASK_COUNTS[k] for k in
          ("both","2018_only","2019_only","neither")),1_000_000)
        self.assertEqual(len(FIXED_CURVE_CLIPPED_LENGTH_KM),4)
        self.assertEqual(len(FIXED_TOPO_SHA256),2)
        self.assertEqual(BIN_NAMES,("0-50m","50-100m","100-250m",
                      "250-500m","500-1000m","1000m_plus"))
        self.assertEqual(tuple(BINS_METERS[:5]),(0,50,100,250,500))

    def test_semantic_json_sha_ignores_only_root_timestamp(self):
        base={"type":"FeatureCollection","features":[
              {"type":"Feature","id":"1","geometry":{"type":"LineString",
               "coordinates":[[201000,5900000],[201100,5900100]]}}],
              "timeStamp":"2026-11-19T00:01:01Z"}
        changed={"features":base["features"],"timeStamp":"2026-11-19T03:22:02Z",
                 "type":"FeatureCollection"}
        self.assertEqual(semantic_original_geojson_fingerprint(base),
                         semantic_original_geojson_fingerprint(changed))
        changed["features"]=[{"type":"Feature","id":"1",
            "geometry":{"type":"LineString",
                "coordinates":[[201000,5900000],[202100,5900100]]}}]
        self.assertNotEqual(semantic_original_geojson_fingerprint(base),
                            semantic_original_geojson_fingerprint(changed))

    def test_four_pixel_classes_disjoint_and_distance_binned(self):
        a=np.array([[True,True,False,False],[True,True,False,False]],dtype=bool)
        b=np.array([[True,False,True,False],[True,False,False,False]],dtype=bool)
        classes=canonical_classes(a,b)
        totals={k:int(v.sum()) for k,v in classes.items()}
        self.assertEqual(totals,{"2018_only":2,"2019_only":1,"both":2,"neither":3})
        dist=np.array([[0,55,95,125],[320,800,1500,1850.]],dtype=float)
        table=bin_source_masks(classes,dist)
        self.assertEqual(sum(x["all_native_grid_pixels_in_band"]
                             for x in table.values()),8)
        self.assertEqual(table["50-100m"]["2018_only"],1)
        self.assertEqual(table["500-1000m"]["2018_only"],1)
        ratio=risk_ratio_near_far(classes,dist)
        self.assertIsNotNone(ratio["loss_risk_ratio_near100m_to_far500m"])
        self.assertEqual(sum(x["2018_only"] for x in quadrants(classes).values()),2)

    def test_no_far_denominator_does_not_invent_ratio(self):
        a=np.array([[True,True]],dtype=bool)
        b=np.array([[True,False]],dtype=bool)
        cls=canonical_classes(a,b)
        out=risk_ratio_near_far(cls,np.array([[5.,55.]]))
        self.assertIsNone(out["loss_risk_ratio_near100m_to_far500m"])

    def test_no_mutated_or_nonfinite_source_masks(self):
        a=np.array([[True,False]],dtype=bool)
        with self.assertRaisesRegex(ValueError,"BOOLEAN_MASKS"):
            canonical_classes(a,np.array([[1.,0.]]))
        cl=canonical_classes(a,a)
        with self.assertRaisesRegex(ValueError,"BOUNDARY_DISTANCE"):
            bin_source_masks(cl,np.array([[np.nan,0.]]))

if __name__=="__main__":
    unittest.main()
