import math,unittest
from datetime import datetime,timedelta
from collections import defaultdict
from unittest.mock import patch

import numpy as np
from rasterio.io import MemoryFile
from rasterio.transform import from_origin
from pyproj import Transformer

from source_original_gps_ahn2_overlap import (
    CELL_M,K_TILES,PATCH_PIXELS,
    MIN_VALID_C,MIN_VALID_BIRDS,MIN_VALID_WEEKS,MIN_VALID_CELLS,
    rd_tile_at,freeze_training_cells,source_destination_support,
    source_triples,source_tile,SourceStop)

class OriginalGPSAHN2SourceCoverageTest(unittest.TestCase):
    def test_fixed_source_grid_and_only_training_bird_day_selection(self):
        self.assertEqual(CELL_M,2000)
        self.assertEqual(K_TILES,8)
        self.assertEqual(MIN_VALID_C,500)
        self.assertEqual(MIN_VALID_BIRDS,3)
        self.assertEqual(MIN_VALID_WEEKS,4)
        self.assertEqual(MIN_VALID_CELLS,2)
        # Data from different synthetic birds and days in each cell.
        inv=Transformer.from_crs(28992,4326,always_xy=True)
        synthetic=defaultdict(list)
        for cell_id in range(9):
            x=160000+CELL_M*cell_id+1000;y=604000
            lon,lat=inv.transform(x,y)
            for bird in range(3):
                for day in range(3+(cell_id%3)):
                    stamp=datetime(2010,6,1)+timedelta(days=day)
                    synthetic[str(bird)].append((stamp,lat,lon))
        chosen,rank=freeze_training_cells(synthetic)
        self.assertEqual(len(chosen),8)
        self.assertEqual(len(rank),8)
        self.assertEqual(rank[0]["source_training_bird_days"],15)
        self.assertGreaterEqual(rank[0]["source_training_bird_days"],
                                rank[-1]["source_training_bird_days"])
        with self.assertRaisesRegex(ValueError,"frozen"):
            freeze_training_cells(synthetic,k=7)
    def test_original_next_GPS_source_geometry_gate(self):
        start=datetime(2011,7,1)
        points=[]
        for i in range(8):
            t=start+timedelta(hours=i)
            points.append((t,53.45,5.75+i*.015))
        triples,reason=source_triples({"onebird":points})
        self.assertEqual(len(triples),6)
        self.assertTrue(all("bird" in x and "time" in x for x in triples))
        self.assertFalse(any("tide" in x or "phase" in x for x in triples))
    def test_2010_fixed_tiles_cover_2011_source_positions_only(self):
        loc=Transformer.from_crs(28992,4326,always_xy=True)
        cells=[(85,300),(86,300)]
        patches={}
        for cell in cells:
            e,n=cell[0]*CELL_M,cell[1]*CELL_M
            patches[cell]={
                "transform":from_origin(e,n+CELL_M,CELL_M/PATCH_PIXELS,
                                        CELL_M/PATCH_PIXELS),
                "height":np.full((PATCH_PIXELS,PATCH_PIXELS),.5)}
        trips=[]
        for i in range(600):
            cell=cells[i%2]
            x=cell[0]*CELL_M+1000;y=cell[1]*CELL_M+1000
            lon,lat=loc.transform(x,y)
            trips.append({"bird":str(i%3),
                          "time":datetime(2011,1,1)+timedelta(days=i%42),
                          "lat":lat,"lon":lon})
        score=source_destination_support(trips,patches,cells)
        self.assertEqual(score["source_status"],"SAMPLE_SUPPORT_FEASIBLE_ONLY")
        self.assertEqual(score["n_original_C_with_valid_AHN2_height"],600)
        self.assertEqual(score["n_original_C_in_broad_minus3_plus3_NAP"],600)
        self.assertEqual(score["n_test_birds_with_valid_C_height"],3)
        self.assertEqual(score["n_distinct_2010_selected_cells_with_valid_C"],2)
        self.assertTrue(score["no_original_RWS_tide_join_or_phase_estimated"])
        # Mark other tile masked: no new source values may be fabricated.
        patches[cells[1]]["height"][:,:]=np.nan
        reduced=source_destination_support(trips,patches,cells)
        self.assertEqual(reduced["n_original_C_with_valid_AHN2_height"],300)
        self.assertEqual(reduced["source_status"],"NOT_ADMITTED_INSUFFICIENT_HISTORICAL_DTM_OVERLAP")
    def test_two_band_original_WCS_tile_bounded_and_masked(self):
        cell=(85,300);e,n=cell[0]*CELL_M,cell[1]*CELL_M
        h=np.zeros((PATCH_PIXELS,PATCH_PIXELS),dtype="float32")
        aux=np.ones_like(h)
        aux[:40,:40]=0.
        with MemoryFile() as mem:
            with mem.open(driver="GTiff",height=PATCH_PIXELS,width=PATCH_PIXELS,
                          count=2,dtype="float32",crs="EPSG:28992",
                          transform=from_origin(e,n+CELL_M,
                                    CELL_M/PATCH_PIXELS,CELL_M/PATCH_PIXELS),
                          nodata=-9999) as ds:
                ds.write(h,1);ds.write(aux,2)
            tiff=mem.read()
        with patch("source_original_gps_ahn2_overlap.bounded_get",return_value=(tiff,"image/tiff")):
            result=source_tile(cell,"preverified-AHN2-DTM","GeoTIFF")
        self.assertEqual(result["source_CRS_epsg"],28992)
        self.assertEqual(result["valid_NAP_candidate_pixels"],PATCH_PIXELS**2-1600)
        self.assertTrue(result["auxiliary_band_semantics_unverified"])
        self.assertEqual(result["candidate_minus3_plus3_NAP_pixels"],PATCH_PIXELS**2-1600)
if __name__=="__main__":unittest.main()
