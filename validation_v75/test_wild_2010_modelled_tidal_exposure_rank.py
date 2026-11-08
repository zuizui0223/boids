"""v75 synthetic known truth, not a new wild ecological effect."""
from __future__ import annotations

import unittest
from unittest.mock import patch
from datetime import datetime,timedelta,timezone

import numpy as np
from scipy.spatial import cKDTree

import wild_2010_modelled_tidal_exposure_rank as model

def synthetic_month(month,*,higher=True):
    lat=np.linspace(53.43,53.47,81)
    lon=np.linspace(6.0,6.06,81)
    la,lo=np.meshgrid(lat,lon,indexing="ij")
    xy=model._locxy(la.ravel(),lo.ravel())
    base=.05 if higher else .95
    expo=np.full(len(xy),base,dtype=float)
    targets=[(25+(i*9)%30,25+(i*13)%30) for i in range(25)]
    for i,(y,x) in enumerate(targets):
        expo[y*81+x]=(.54+.017*i if higher else .46-.017*i)
    native={"xy":xy,"index":expo,"n_native":len(expo),"tree":cKDTree(xy)}
    fixes=[]
    for bird in range(5):
        for k in range(40):
            y,x=targets[(bird+k)%25]
            stamp=datetime(2010,month,2)+timedelta(hours=k)
            fixes.append((f"SYNTHETIC_{bird}",stamp,float(la[y,x]),float(lo[y,x])))
    return native,fixes

class RealOrdinalSourceAndInferenceSafety(unittest.TestCase):
    def test_original_frozen_months_and_2010_hashes(self):
        self.assertEqual(model.MONTHS,(8,9,10,11,12))
        self.assertEqual(len(model.PINNED_MODEL_SHA),5)
        self.assertEqual(model.ORIGINAL_GPS_RAW,282920)
        self.assertEqual(sum(v[0] for v in model.MONTH_GPS_AND_BIRDS.values()),45138)
        self.assertEqual(model.GPS_SHA,
            "8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d")

    def test_source_only_real_geographic_month_gate_known_truth(self):
        with patch.object(model,"NATIVE_EXPECTED",81*81):
            with patch.dict(model.MONTH_GPS_AND_BIRDS,
                 {m:(200,5) for m in model.MONTHS},clear=True):
                native,fixes=synthetic_month(8)
                source=model.geometric_preflight(8,fixes,native)
        rec=source["source_receipt"]
        self.assertEqual(rec["original_gps_source_hourly_positions"],200)
        self.assertEqual(rec["source_original_bird_IDs_with_twenty_1km_complete_GPS"],5)
        self.assertTrue(rec["fixed_source_admission"].startswith("SOURCE_ADMITTED"))
        self.assertNotIn("SYNTHETIC_0",str(rec))
        self.assertNotIn("time_expo_used",str(rec))

    def make_all(self,*,higher=True):
        result={}
        with patch.object(model,"NATIVE_EXPECTED",81*81):
            with patch.dict(model.MONTH_GPS_AND_BIRDS,
                 {m:(200,5) for m in model.MONTHS},clear=True):
                for month in model.MONTHS:
                    native,fixes=synthetic_month(month,higher=higher)
                    result[month]=model.geometric_preflight(month,fixes,native)
        return result

    def test_frozen_five_source_months_positive_ordinal_bird_rank(self):
        src=self.make_all(higher=True)
        r=model.combined_field_score(src)
        self.assertEqual(r["source_admission"],"SOURCE_ADMITTED_ALL_FIVE_ORIGINAL_2010_MONTHS")
        q=r["original_used_vs_local_ordinal_rank_bird_equal_primary"]
        self.assertEqual(q["source_original_birds"],5)
        self.assertEqual(q["source_admitted_bird_months"],25)
        self.assertGreater(q["equal_month_within_bird_then_bird_equal_mean"],.3)
        self.assertGreater(q["whole_bird_cluster_bootstrap_percentile95"][0],0)
        self.assertEqual(q["source_original_birds_with_positive_contrast"],5)
        self.assertTrue(r["frozen_primary_status"].startswith("EXPLORATORY_POSITIVE"))
        self.assertEqual(len(r["per_2010_month_observed_source_ordinal_result_ALL_FIVE"]),5)
        self.assertNotIn("SYNTHETIC_",str(r))

    def test_known_truth_negative_stays_negative_no_month_selection(self):
        r=model.combined_field_score(self.make_all(higher=False))
        q=r["original_used_vs_local_ordinal_rank_bird_equal_primary"]
        self.assertLess(q["equal_month_within_bird_then_bird_equal_mean"],-.3)
        self.assertLess(q["whole_bird_cluster_bootstrap_percentile95"][1],0)
        self.assertEqual(r["frozen_primary_status"],
            "LOCAL_MODELED_INDEX_RANK_OVER_LOCAL_GEOMETRIC_REFERENCE_NOT_ESTABLISHED")
        with self.assertRaisesRegex(ValueError,"FAVORABLE_MONTH_SUBSET"):
            model.combined_field_score({
                k:v for k,v in self.make_all().items() if k!=12})
        src=self.make_all()
        src[12]["source_receipt"]["fixed_source_admission"]="NOT_ADMITTED_V75_TEST"
        refused=model.combined_field_score(src)
        self.assertEqual(refused["wild_observed_tidal_modelled_use_effect"],
                         "NOT_ESTIMATED_SOURCE_GATE")

    def test_midrank_and_monotonic_invariance_including_ties(self):
        arr=np.array([0,0,0,1,2,3],dtype=float)
        self.assertAlmostEqual(model._rank(arr,0,list(range(6))),.25)
        self.assertAlmostEqual(model._rank(np.exp(arr),0,list(range(6))),.25)
        a=np.full(10,.4)
        self.assertAlmostEqual(model._rank(a,0,list(range(10))),.5)

    def test_gps_new_field_clock_and_model_unknown_units_not_causality(self):
        src=self.make_all()
        r=model.combined_field_score(src)
        self.assertTrue(r["no_real_food_resource_or_daylight_tide_causal_mechanism_estimated"])
        self.assertTrue(r["not_new_wild_species_or_independent_area"])
        self.assertEqual(r["original_model_exposure_index_unit"],
                         "UNKNOWN_ORDINAL_NOT_HOURS_OR_PERCENT_OF_EXPOSURE")
        for q in model._whole_bird_bootstrap([.1]*5,seed=123):
            self.assertAlmostEqual(q,.1)

if __name__=="__main__":
    unittest.main()
