"""v85 synthetic known truths: strict intertidal source, bird source gate, no scores before gate.

All test positions, geometry/model indices and synthetic 4-way classes are
fabricated. No claim original 2010 Wadden bird behavior in these tests.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from unittest.mock import patch
import unittest
import numpy as np
from scipy.spatial import cKDTree
import shapely

import midhigh_intertidal_source_and_fourway as s
from wild_2010_modelled_tidal_exposure_rank import _locxy
from tide_solar_four_way_source_and_effect import ADMIT

def fake_original_shape_model():
    y=np.linspace(53.41,53.49,41)
    x=np.linspace(6.00,6.08,41)
    lat,lon=np.meshgrid(y,x,indexing="ij")
    xy=_locxy(lat.ravel(),lon.ravel())
    return {
        "n_native":len(xy),
        "xy":xy,
        "tree":cKDTree(xy),
        "index":np.linspace(0.,1.,len(xy))}

def fake_original_shape_GPS(month=6,n_birds=5,n_perbird=60):
    return [(f"SYNTHETIC_BIRD_{b}",datetime(2010,month,12),
             53.448+0.00001*(i%10),6.039+0.00001*(b%5))
            for b in range(n_birds) for i in range(n_perbird)]

def fake_mask(model, code3=True):
    n=model["n_native"]
    mask=np.full(n,3 if code3 else 0,dtype=np.uint8)
    allowed=np.flatnonzero(mask>0)
    return {
        "class":mask,
        "admitted_native_cell_indices":allowed,
        "native_allowed_center_tree":cKDTree(model["xy"][allowed])
            if len(allowed) else cKDTree(np.empty((0,2))),
        "native_reference_xy":model["xy"]}

class WMRNativeEcotopeWildGPSKnownTruth(unittest.TestCase):
    def test_original_source_shas_and_class_codes_locked(self):
        self.assertEqual(s.GEO_INDEX_CODES,(3,4))
        self.assertEqual(s.MODEL_MONTHS,(6,7,8,9,10,11,12))
        self.assertEqual(s.FROZEN_WMR_SHA["Schier"],
            "b77e38c7f60ef5daa8c205b99161fca3ab6c94fa4d75cb49d92c31ae169cd6b1")
        self.assertEqual(s.FROZEN_MODEL_SOURCE_CLASS_COUNTS["Ameland"],{3:3130,4:70})
        self.assertEqual(s.REFERENCE_RADIUS_M,1000)

    def test_gps_inside_midhigh_eligible_and_original_bird_hours_not_independent(self):
        model=fake_original_shape_model()
        mask=fake_mask(model)
        fixes=fake_original_shape_GPS()
        with patch.object(s,"MODEL_NATIVE_SOURCE_N",model["n_native"]):
            with patch.dict(s.SCHIER_SOURCE,{6:(300,5)}):
                out=s.source_class_restricted_gps_month("Schier",6,fixes,model,mask)
        qa=out["source_qa"]
        self.assertEqual(qa["original_gps_hourly_source_records"],300)
        self.assertEqual(qa["original_gps_used_native_model_code3_before_neighborhood"],300)
        self.assertEqual(qa["original_gps_used_on_mid_high_with_at_least20_nearby_mid_high_pixels"],300)
        self.assertEqual(qa["original_birds_with_ge20_strict_intertidal_GPS_this_month"],5)
        self.assertEqual(len(out["valid_birds"]),5)
        self.assertTrue(all(len(out["circles"][i])>=20 for i in range(300)))
        self.assertNotIn("SYNTHETIC_BIRD_",str(qa))
        self.assertTrue(qa["source_original_NIOZ_used_index_value_NOT_INSPECTED"])

    def test_gps_on_outside_non_tidal_source_class_never_snapped_to_flat(self):
        model=fake_original_shape_model()
        mask=fake_mask(model,code3=False)
        fixes=fake_original_shape_GPS()
        with patch.object(s,"MODEL_NATIVE_SOURCE_N",model["n_native"]):
            with patch.dict(s.SCHIER_SOURCE,{6:(300,5)}):
                out=s.source_class_restricted_gps_month("Schier",6,fixes,model,mask)
        qa=out["source_qa"]
        self.assertEqual(qa["original_gps_used_native_model_code3_before_neighborhood"],0)
        self.assertEqual(qa["original_gps_after_bird_month20_and_WMR_neighborhood20"],0)
        self.assertEqual(qa["original_gps_outside_mid_high_WMR_mask_or_300m_geocoding"],300)
        self.assertFalse(out["valid"].any())

    def test_original_static_month_grid_and_bird_source_drift_fail(self):
        model=fake_original_shape_model()
        mask=fake_mask(model)
        fixes=fake_original_shape_GPS()
        with patch.object(s,"MODEL_NATIVE_SOURCE_N",model["n_native"]):
            with self.assertRaisesRegex(ValueError,"SOURCE_DRIFT"):
                s.source_class_restricted_gps_month("Schier",6,fixes,model,mask)
            with patch.dict(s.SCHIER_SOURCE,{6:(300,5)}):
                changed={**model,"xy":model["xy"]+1}
                with self.assertRaisesRegex(ValueError,"MODEL_STATIC_GRID_MONTH_DRIFT"):
                    s.source_class_restricted_gps_month("Schier",6,fixes,changed,mask)

    def test_source_3_common_months_and_both_full_fourcell_needed_first(self):
        sources={}
        match={}
        for site in ("Schier","Ameland"):
            monthly={}
            for month in s.SOURCE_MONTHS:
                monthly[month]={
                  "source_qa":{
                    "original_birds_with_ge20_strict_intertidal_GPS_this_month":
                        7 if month in (6,7,8) else 1,
                    "original_gps_after_bird_month20_and_WMR_neighborhood20":
                        150 if month in (6,7,8) else 0}}
            sources[site]=monthly
            four={
                (f"TEST_ORIGINAL_{b}",m,h):{}
                for b in range(8) for m in (6,7,8) for h in range(5)}
            match[site]=(four,{
                "original_tide_astro_same_bird_month_height_strata":{
                    "admission":ADMIT,
                    "original_birds_in_all_four_tide_and_light_conditions":8,
                    "original_four_way_source_fix_count":3000,
                    "original_four_way_exact_same_bird_month_RWS_height_groups":120}})
        gate=s.shared_source_gates(sources,match)
        self.assertTrue(gate["all_fixed_original_source_gates_admitted_BEFORE_model_use_rank"])
        self.assertEqual(gate["source_both_sites_fourway_months_shared"],[6,7,8])
        sources["Ameland"][8]["source_qa"][
            "original_gps_after_bird_month20_and_WMR_neighborhood20"]=0
        gate=s.shared_source_gates(sources,match)
        self.assertFalse(gate["all_fixed_original_source_gates_admitted_BEFORE_model_use_rank"])

    def test_no_effect_when_true_rws_bird_source_gate_fails(self):
        result=s.score_if_both_source_admitted({}, {},
            {"all_fixed_original_source_gates_admitted_BEFORE_model_use_rank":False},
            {})
        self.assertEqual(result["score"],s.RESULT_STOP)
        q=s.original_one_site_rank_delta([.2,.2,.2,.2,.2])
        self.assertEqual(q["true_original_birds"],5)
        self.assertAlmostEqual(q["original_independent_bird_equal_difference"],.2)
        self.assertTrue(all(abs(x-.2)<1e-12 for x in
            q["independent_original_bird_bootstrap_95"]))

if __name__=="__main__":
    unittest.main()
