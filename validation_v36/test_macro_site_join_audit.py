"""v36 synthetic protected source join tests; no measured animal GPS."""
import unittest
from macro_site_join_audit import audit,distance,number

def fake(n=20,swapped=False,dupe=False):
    land=[]
    meta=[]
    for i in range(n):
        lat=40+i*0.1
        lon=-100+i*0.1
        land.append({"X":str(lat if swapped else lon),"Y":str(lon if swapped else lat)})
        if dupe and i==0:land.append(land[-1].copy())
        for j in range(8):
            meta.append({"Lat":str(lat),"Long":str(lon),
                "Authors":"Author"+str(i),"Year_pub":"2020",
                "Journal":"Ecology","Pays":"country"+str(i%5),
                "Species":"species"+str(i),"MCP":"2.0","Dist":"5.0"})
    return meta,land

class GeometryTests(unittest.TestCase):
    def test_geo_distance_zero(self):
        self.assertAlmostEqual(distance(-80,42,-80,42),0)
    def test_original_lat_lon_orientation(self):
        r=audit(*fake())
        self.assertEqual(r["status"],"JOIN_STRUCTURALLY_ELIGIBLE_OUTCOMES_UNOPENED")
        self.assertEqual(r["chosen_orientation"],"X_LON_Y_LAT")
        self.assertFalse(r["movement_outcome_numeric_values_opened"])
        self.assertFalse(r["source_coordinates_exported"])
    def test_swapped_orientation_registered_before_outcomes(self):
        r=audit(*fake(swapped=True))
        self.assertEqual(r["chosen_orientation"],"X_LAT_Y_LON")
    def test_duplicate_source_site_blocks_selecting(self):
        r=audit(*fake(dupe=True))
        self.assertEqual(r["status"],"JOIN_OR_GRAIN_STOP_NO_PREDECLARED_UNIQUE_ORIENTATION")
    def test_missing_coordinates_not_auto_joined(self):
        meta,land=fake()
        for row in meta:row["Lat"]="NA"
        r=audit(meta,land)
        self.assertIsNone(r["chosen_orientation"])
    def test_no_biological_effects_ever_fitted(self):
        r=audit(*fake())
        self.assertFalse(r["ecological_effects_fitted"])
        self.assertEqual(r["countries_all_meta"],5)

if __name__=="__main__":unittest.main()
