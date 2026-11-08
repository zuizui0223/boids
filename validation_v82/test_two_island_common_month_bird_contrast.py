"""v82 synthetic known truths for genuine original-bird two-site tide×sun C.

Synthetic samples are not original wild birds or biological confirmation.
"""
from __future__ import annotations

import unittest
from unittest.mock import patch
from datetime import datetime
import numpy as np
from scipy.spatial import cKDTree

import two_island_common_month_bird_contrast as v82
from wild_2010_modelled_tidal_exposure_rank import _locxy

def fake_source_month(month=6,site="Schier",bird_n=5,fixes_per_bird=50):
    yy=np.linspace(53.40,53.50,101)
    xx=np.linspace(6.0,6.08,101)
    la,lo=np.meshgrid(yy,xx,indexing="ij")
    xy=_locxy(la.ravel(),lo.ravel())
    model={
        "xy":xy,"tree":cKDTree(xy),"index":np.linspace(0,1,len(xy)),
        "n_native":len(xy)}
    fixes=[(f"synthetic_bird_{b}",datetime(2010,month,15),
            53.45+.00001*(k%5),6.04+.00001*(b%5))
           for b in range(bird_n) for k in range(fixes_per_bird)]
    return fixes,model

def fake_fourway(*,site_modifier=1.0):
    months=(6,7,8)
    fills={}
    fours={}
    for month in months:
        arr=[]
        circles=[]
        x=np.linspace(0,1,101)
        for b in range(8):
            for h in range(5):
                phase_data={}
                for phase in (-1,1):
                    group={}
                    for light in ("DAY","NIGHT"):
                        vals=[]
                        for j in range(5):
                            idx=len(arr)
                            vals.append((month,idx))
                            # exact source rank difference for flood vs ebb
                            r=.5 if light=="DAY" else (
                                .2 if phase==-1 else .2+.2*site_modifier)
                            arr.append(round(r*100))
                            circles.append(list(range(101)))
                        group[light]=vals
                    phase_data[phase]=group
                fours[(f"synthetic_{b}",month,h)]=phase_data
        fills[month]={"model_expo":x,"closest":np.array(arr),
                      "circles":circles}
    return fours,fills

class TwoIslandOriginalBirdContrasts(unittest.TestCase):
    def test_locked_original_source_month_frames_and_prior_real_sites(self):
        self.assertEqual(v82.SOURCE_MONTHS,(6,7,8,9,10,11,12))
        self.assertEqual(v82.LATE_MONTHS,(8,9,10,11,12))
        self.assertEqual(v82.SCHIER_SOURCE[6],(8874,19))
        self.assertEqual(v82.AMELAND_SOURCE[6],(6450,15))
        self.assertEqual(v82.EXPECTED_V77_LATE_SCHIER,(655,16,.03803110272968872))
        self.assertEqual(v82.EXPECTED_V81_FULL_AMELAND,(381,10,.0052737884296153855))
        self.assertEqual(v82.EXPECTED_V78_NATIVE_AMELAND,(267,7))

    def test_prior_month_source_geography_unread_nioz_used_values_and_birds(self):
        fixes,model=fake_source_month()
        with patch.object(v82,"SOURCE_MODEL_EXPECTED_CELLS",len(model["index"])):
            with patch.dict(v82.SCHIER_SOURCE,{6:(250,5)}):
                q=v82.geographic_month_source("Schier",6,fixes,model)
        self.assertEqual(q["source_receipt"]["fixed_source_admission"],v82.STATUS)
        self.assertEqual(q["source_receipt"]["original_real_bird_IDs_in_month"],5)
        self.assertEqual(q["source_receipt"]["genuine_GPS_source_nearest_model_grid_within300m"],250)
        self.assertTrue(q["source_receipt"]["original_model_used_index_values_NOT_READ_FOR_SOURCE"])
        self.assertNotIn("synthetic_bird_0",str(q["source_receipt"]))
        with self.assertRaisesRegex(ValueError,"MONTH_COUNT_DRIFT"):
            v82.geographic_month_source("Schier",6,fixes,model)

    def test_month_with_fewer_than_five_original_animals_is_not_admitted(self):
        fixes,model=fake_source_month(bird_n=4)
        with patch.object(v82,"SOURCE_MODEL_EXPECTED_CELLS",len(model["index"])):
            with patch.dict(v82.AMELAND_SOURCE,{6:(200,4)}):
                q=v82.geographic_month_source("Ameland",6,fixes,model)
        self.assertIn("NOT_ADMITTED",q["source_receipt"]["fixed_source_admission"])

    def test_site_difference_independently_block_bootstraps_original_birds_positive(self):
        q=v82.independent_bird_site_contrast([+.20]*16,[-.03]*10)
        self.assertAlmostEqual(q["Schier_bird_equal_minus_Ameland_bird_equal"],.23)
        for x in q["original_site_independent_whole_bird_10000_bootstrap95"]:
            self.assertAlmostEqual(x,.23)
        self.assertEqual(q["original_true_birds_in_Schier"],16)
        self.assertEqual(q["original_true_birds_in_Ameland"],10)
        self.assertIn("POSITIVE",q["point_positive_or_negative_status"])

    def test_site_difference_negative_null_and_nonfinite_abort(self):
        q=v82.independent_bird_site_contrast([-.2]*16,[+.1]*10)
        self.assertIn("NEGATIVE",q["point_positive_or_negative_status"])
        self.assertLess(q["original_site_independent_whole_bird_10000_bootstrap95"][1],0)
        n=v82.independent_bird_site_contrast(
            np.array([-.15,.15]*8),np.array([-.15,.15]*5))
        self.assertEqual(n["point_positive_or_negative_status"],
            "SITE_BIRD_CONDITIONAL_DIFFERENCE_NOT_ESTABLISHED")
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP_V82"):
            v82.independent_bird_site_contrast([],np.ones(10))
        with self.assertRaisesRegex(ValueError,"ESTIMAND_STOP_V82"):
            v82.independent_bird_site_contrast([np.nan]*16,np.ones(10))

    def test_four_way_exact_v77_frozen_bird_hierarchy_and_original_bootstrap(self):
        four,geo=fake_fourway()
        birds,replay=v82._exact_site_replay("synthetic_Schier",four,geo)
        self.assertEqual(len(birds),8)
        self.assertEqual(replay["original_four_way_tide_light_groups"],120)
        self.assertTrue(replay["reproduces_v77_and_native_source_bird_cluster_exactly"])
        self.assertNotIn("synthetic_0",str(replay))
        with self.assertRaisesRegex(ValueError,"PRIOR_KNOWN_ORIGINAL"):
            v82._exact_site_replay("synthetic_Schier",four,geo,
                                   expected=(655,16,.03803110272968872))

    def test_any_site_source_failure_scores_no_model_used_rank(self):
        bad={"all_four_conditions_same_real_bird_month_height_source":{
                 "admission":"NOT_ADMITTED_V77_FOUR_WAY_TIDE_LIGHT_SOURCE"}}
        good={"all_four_conditions_same_real_bird_month_height_source":{
                 "admission":v82.ADMIT}}
        x=v82.new_two_site_difference({}, {}, {}, {}, good,bad)
        self.assertEqual(x["common_calendar_bird_site_interaction_difference"],
                         "NOT_ESTIMATED_SOURCE_GATE")

if __name__=="__main__":
    unittest.main()
