"""v80 source-only known-truth: static native original model coordinate template.

Synthetic grid numbers prove matching/rejecting, NOT wildlife or true NIOZ.
"""
from __future__ import annotations
import unittest
import numpy as np

from original_nioz_static_2010_grid import (
    MONTHS_2010,PRESELECTED_OTHERYEAR,EXPECTED_CELLS,NATIVE_SHAPE,
    PRE_PINNED,audit_month,static_grid_decision,valid_coords,
    gauge_reference_qa)

def sample_original_synthetic():
    y=np.linspace(53.1,53.9,NATIVE_SHAPE[0],dtype=float)
    x=np.linspace(5.3,6.7,NATIVE_SHAPE[1],dtype=float)
    lat=np.broadcast_to(y[:,None],NATIVE_SHAPE).copy()
    lon=np.broadcast_to(x[None,:],NATIVE_SHAPE).copy()
    return lat,lon

class OriginalNIOZ2010ModelMeshKnownTruth(unittest.TestCase):
    def test_exact_immutable_month_preselection(self):
        self.assertEqual(len(MONTHS_2010),12)
        self.assertEqual(MONTHS_2010[0],"eco_av.201001.nc")
        self.assertEqual(MONTHS_2010[-1],"eco_av.201012.nc")
        self.assertEqual(PRESELECTED_OTHERYEAR,(
            "eco_av.200901.nc","eco_av.200908.nc",
            "eco_av.201108.nc","eco_av.201112.nc"))
        self.assertEqual(EXPECTED_CELLS,486*820)
        self.assertEqual(len(PRE_PINNED),2)

    def sample_QA(self,*,altered_complete=False,altered_missing_lon=False,
                  outsideyear_complete=2):
        a,b=sample_original_synthetic()
        qa={}
        original={}
        for f in MONTHS_2010+PRESELECTED_OTHERYEAR:
            is_missing=f in ("eco_av.201006.nc","eco_av.201007.nc")
            if f in PRESELECTED_OTHERYEAR:
                rank=PRESELECTED_OTHERYEAR.index(f)
                is_missing=rank>=outsideyear_complete
            la=a.copy()
            lo=b.copy()
            if is_missing:la[:]=np.nan
            if altered_missing_lon and f=="eco_av.201007.nc":
                lo[2,3]+=.0001
            if altered_complete and f=="eco_av.201010.nc":
                la[10,10]+=.00001
            header={
                "lat":{"source_finite_count":int(np.isfinite(la).sum())},
                "lon":{"source_finite_count":int(np.isfinite(lo).sum())}
            }
            qa[f]=audit_month(a,b,la,lo,header,f)
        gauges=gauge_reference_qa(a,b)
        return qa,gauges

    def test_all_complete_identical_and_two_external_models_support_conditional_template(self):
        qa,gauges=self.sample_QA()
        verdict=static_grid_decision(qa,gauges)
        self.assertEqual(len(verdict["original_2010_months_full_native_lat_lon"]),10)
        self.assertTrue(verdict["all_ten_original_2010_complete_grid_coordinates_exact_same"])
        self.assertEqual(len(verdict["original_external_year_complete_grid_months_matching_Jan2010"]),2)
        self.assertIn("PROVENANCE_SUPPORTED",verdict["model_static_geo_template_SOURCE_ONLY_status"])
        self.assertFalse(verdict["genuine_original_June_July_lat_values_were_observed"])
        self.assertFalse(verdict["imputed_JuneJuly_lat_values_created_or_released"])

    def test_source_identical_lon_but_one_complete_month_drift_is_not_admitted(self):
        qa,gauges=self.sample_QA(altered_complete=True)
        d=static_grid_decision(qa,gauges)
        self.assertFalse(d["all_ten_original_2010_complete_grid_coordinates_exact_same"])
        self.assertTrue(d["model_static_geo_template_SOURCE_ONLY_status"].startswith("NOT_ADMITTED"))
        self.assertGreater(qa["eco_av.201010.nc"][
            "same_original_index_coordinate_displacement_metres"]["maximum"],0)

    def test_source_masked_lat_and_indexwise_lon_changed_in_july_rejected(self):
        qa,gauges=self.sample_QA(altered_missing_lon=True)
        d=static_grid_decision(qa,gauges)
        self.assertFalse(d["original_2010_June_July_lat_all_missing_lon_each_index_exact_match"])
        self.assertTrue(d["model_static_geo_template_SOURCE_ONLY_status"].startswith("NOT_ADMITTED"))

    def test_external_year_not_originally_complete_is_not_made_up(self):
        qa,gauges=self.sample_QA(outsideyear_complete=1)
        d=static_grid_decision(qa,gauges)
        self.assertEqual(len(d["original_external_year_complete_grid_months_matching_Jan2010"]),1)
        self.assertTrue(d["model_static_geo_template_SOURCE_ONLY_status"].startswith("NOT_ADMITTED"))

    def test_invalid_native_degree_grid_cannot_be_claimed_original_wadden_geographic(self):
        lat,lon=sample_original_synthetic()
        self.assertEqual(int(valid_coords(lat,lon).sum()),EXPECTED_CELLS)
        z=lat.copy();z[:]=np.nan
        self.assertEqual(int(valid_coords(z,lon).sum()),0)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            gauge_reference_qa(z,lon)

if __name__=="__main__":
    unittest.main()
