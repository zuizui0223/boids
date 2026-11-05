"""v47 known-truth source-only B+C historic AHN2 GPS coverage; no tide."""
import math
import unittest
from datetime import datetime,timedelta
import numpy as np
from pyproj import Transformer
from rasterio.transform import from_origin
from ahn2_both_original_endpoints_source import (
    both_endpoint_support,exact_source_triples_both,height_from_original_tile,
    MIN_BOTH,MIN_BOTH_TIDAL_BAND,MIN_BIRDS,MIN_WEEKS,MIN_CELLS)
from source_original_gps_ahn2_overlap import (
    CELL_M,PATCH_PIXELS,source_triples,source_destination_support)

class BothOriginalAHNEndpoints(unittest.TestCase):
    def test_source_three_fix_parser_replays_original_C_cohort(self):
        t=datetime(2011,1,1,0)
        fixes=[(t+timedelta(hours=k),53.44,5.75+k*.01) for k in range(10)]
        original={"bird0":fixes}
        c,exclude=source_triples(original)
        bc,exb=exact_source_triples_both(original)
        self.assertEqual(exb,exclude)
        self.assertEqual(len(bc),len(c))
        self.assertEqual([r["lat"] for r in c],[r["lat"] for r in bc])
        self.assertTrue(all("B_lat" in r and "B_time" in r for r in bc))
        self.assertFalse(any("tide" in r or "phase" in r for r in bc))
    def test_static_source_geometry_B_and_C_with_missingness_gate(self):
        xform=Transformer.from_crs(28992,4326,always_xy=True)
        cells=[(85,300),(86,300)]
        tiles={}
        for key in cells:
            e,n=key[0]*CELL_M,key[1]*CELL_M
            tiles[key]={"height":np.full((PATCH_PIXELS,PATCH_PIXELS),.5),
                        "transform":from_origin(e,n+CELL_M,
                                                CELL_M/PATCH_PIXELS,CELL_M/PATCH_PIXELS)}
        Bx,By=85*CELL_M+1000,300*CELL_M+1000
        Cx,Cy=86*CELL_M+1000,300*CELL_M+1000
        Blon,Blat=xform.transform(Bx,By)
        Clon,Clat=xform.transform(Cx,Cy)
        trips=[]
        for i in range(600):
            trips.append({"bird":f"bird{i%3}","time":datetime(2011,1,1)+timedelta(days=i%42),
                          "B_lat":Blat,"B_lon":Blon,
                          "lat":Clat,"lon":Clon})
        report=both_endpoint_support(trips,tiles,cells)
        self.assertEqual(report["source_status"],"B_C_SOURCE_FEASIBLE_FOR_PREREGISTERING_FRONT_TEST")
        self.assertEqual(report["n_B_source_valid"],600)
        self.assertEqual(report["n_C_source_valid"],600)
        self.assertEqual(report["n_B_C_source_valid"],600)
        self.assertEqual(report["n_B_C_broad_NAP_minus3_plus3"],600)
        self.assertEqual(report["n_eligible_B_C_source_birds"],3)
        self.assertEqual(report["n_B_C_contributing_selected_source_cells"],2)
        self.assertEqual(report["n_eligible_B_C_source_ISO_weeks"],6)
        self.assertTrue(report["source_tide_gauge_join"] is False)
        # Exact same original-C support as v46 with independent sampler.
        simple=[{"bird":x["bird"],"time":x["time"],
                 "lat":x["lat"],"lon":x["lon"]} for x in trips]
        independent=source_destination_support(simple,tiles,cells)
        self.assertEqual(independent["n_original_C_with_valid_AHN2_height"],
                         report["n_C_source_valid"])
        tiles[cells[0]]["height"][:,:]=np.nan
        rejected=both_endpoint_support(trips,tiles,cells)
        self.assertEqual(rejected["n_C_source_valid"],600)
        self.assertEqual(rejected["n_B_source_valid"],0)
        self.assertEqual(rejected["n_B_C_source_valid"],0)
        self.assertEqual(rejected["source_status"],"NOT_ADMITTED_INSUFFICIENT_DUAL_END_DTM")
    def test_outside_fixed_2010_cells_is_never_filled(self):
        p=height_from_original_tile(53.4,5.9,[],{})
        self.assertEqual(p["status"],"OUTSIDE_ORIGINAL_2010_SELECTED_TILES")
        self.assertEqual(MIN_BOTH,500)
        self.assertEqual(MIN_BOTH_TIDAL_BAND,300)
        self.assertEqual((MIN_BIRDS,MIN_WEEKS,MIN_CELLS),(3,4,2))

if __name__=="__main__":unittest.main()
