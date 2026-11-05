"""v50 source-verified full-model no-refit AHN2 mask stratification tests."""
import math,unittest
from datetime import datetime,timedelta,timezone
from collections import Counter
import numpy as np
from pyproj import Transformer
from rasterio.transform import from_origin

from original_heading_tide import unit_direction
from ahn2_destination_z_tide_prediction import triplets_with_past_motion
from original_heading_skill_by_ahn2_mask import (
    GROUPS,GROUP_MIN_ROWS,MIN_SAME_BIRDS,MIN_WITHIN_BIRD_EPISODES_EACH,
    REF_V43,exact_original_C_for_v41_rows,classify_original_C_source,
    group_score,within_bird_masked_minus_valid,skill_pair)

class V50SpatialSourceMaskKnownTruth(unittest.TestCase):
    def row(self,bird,index):
        return {"id":str(bird),"t":datetime(2011,1,1,tzinfo=timezone.utc)+
                timedelta(hours=index*3),
                "target_e":1.,"target_n":0.}
    def test_past_original_GPS_heading_and_future_destination_exact(self):
        t=datetime(2011,6,1)
        arr=[(t+timedelta(hours=k),53.45,5.7+.01*k) for k in range(10)]
        original={"A":arr}
        tris,_=triplets_with_past_motion(original)
        rows=[]
        for v in tris:
            b=(v["B_time"],v["B_lat"],v["B_lon"])
            c=(v["time"],v["lat"],v["lon"])
            u=unit_direction(b,c)
            rows.append({"id":v["bird"],"t":v["B_time"].replace(tzinfo=timezone.utc),
                         "lat":v["B_lat"],"lon":v["B_lon"],
                         "previous_e":v["previous_e"],"previous_n":v["previous_n"],
                         "previous_speed_log":v["previous_speed_log"],
                         "target_e":u[0],"target_n":u[1]})
        matched,meta=exact_original_C_for_v41_rows(original,rows)
        self.assertEqual(len(matched),len(rows))
        self.assertTrue(meta["no_future_C_coordinates_in_v41_model_features"])
        self.assertEqual(len(set((v["bird"],v["time"]) for v in matched)),len(rows))
        forgery=[{**rows[0],"target_e":-rows[0]["target_e"]}]+rows[1:]
        with self.assertRaisesRegex(ValueError,"CHANGED_ORIGINAL_NEXT_GPS"):
            exact_original_C_for_v41_rows(original,forgery)
    def test_2010_tile_mask_are_data_availability_categories_not_water(self):
        cell=(85,300);e,n=cell[0]*2000,cell[1]*2000
        lon,lat=Transformer.from_crs(28992,4326,always_xy=True).transform(e+1000,n+1000)
        record={"lat_C":lat,"lon_C":lon}
        tile={"height":np.ones((256,256),dtype=float),
              "transform":from_origin(e,n+2000,2000/256,2000/256)}
        self.assertEqual(classify_original_C_source(record,[cell],{cell:tile}),
                         GROUPS[0])
        tile["height"][:,:]=np.nan
        self.assertEqual(classify_original_C_source(record,[cell],{cell:tile}),
                         GROUPS[1])
        self.assertEqual(classify_original_C_source(record,[],{}),GROUPS[2])
        self.assertEqual(REF_V43["schiermonnikoog"]["n_test"],4948)
    def test_group_source_and_matched_bird_skill_bootstraps(self):
        records=[];labels=[];e0=[];e1=[]
        for bird in range(5):
            for k in range(250):
                for g in (GROUPS[0],GROUPS[1],GROUPS[2]):
                    records.append(self.row(bird,k))
                    labels.append(g)
                    e0.append(.5+.01*bird)
                    e1.append((.48 if g==GROUPS[0] else
                               .39 if g==GROUPS[1] else .46)+.01*bird)
        e0=np.asarray(e0);e1=np.asarray(e1)
        v=group_score(records,e0,e1,labels,GROUPS[0],bird_draws=100,week_draws=100)
        m=group_score(records,e0,e1,labels,GROUPS[1],bird_draws=100,week_draws=100)
        self.assertEqual(v["admission"],"ORIGINAL_GPS_PREDICTION_GROUP_DESCRIPTIVE")
        self.assertEqual(m["admission"],"ORIGINAL_GPS_PREDICTION_GROUP_DESCRIPTIVE")
        self.assertGreater(m["source_group_pooled_equal_bird_relative_gain"],
                           v["source_group_pooled_equal_bird_relative_gain"])
        matched=within_bird_masked_minus_valid(records,e0,e1,labels,bird_draws=150)
        self.assertEqual(matched["admission"],
                         "POSTRESULT_SOURCE_MASK_CONDITIONAL_PREDICTIVE_COMPARISON")
        self.assertGreater(matched["masked_minus_valid_relative_phase_gain"],0)
        self.assertEqual(matched["n_individual_birds_masked_skill_higher"],5)
        self.assertEqual(len(matched["paired_common_bird_bootstrap95"]),2)
    def test_small_source_group_and_shared_bird_gates(self):
        records=[self.row(k%2,k) for k in range(90)]
        labels=[GROUPS[0] if k%2 else GROUPS[1] for k in range(90)]
        e0=np.full(90,.5);e1=np.full(90,.4)
        self.assertEqual(group_score(records,e0,e1,labels,GROUPS[0])["admission"],
                         "NOT_ADMITTED_INSUFFICIENT_SOURCE_GROUP")
        self.assertEqual(within_bird_masked_minus_valid(records,e0,e1,labels)["admission"],
                         "NOT_ADMITTED_SOURCE_MASK_WITHIN_BIRD_CONTRAST")
        self.assertEqual(GROUP_MIN_ROWS,200)
        self.assertEqual(MIN_SAME_BIRDS,3)
        self.assertEqual(MIN_WITHIN_BIRD_EPISODES_EACH,5)
    def test_error_ratio_requires_nonzero_baseline(self):
        self.assertAlmostEqual(float(skill_pair([.5,.4])),.2)
        with self.assertRaises(ValueError):
            skill_pair(np.asarray([0.,.2]))

if __name__=="__main__":unittest.main()
