"""v28-C1 no-outcome known truth: independent bats and source sampled RSF.

All synthetic source rows are invented, never original animal positions.
"""
from __future__ import annotations
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
import pandas as pd
import bat_wind_heldout as v


def synthetic_bats(nbat=30,flights=2,used_per_flight=8,random_per_flight=40):
    rows=[]
    for b in range(nbat):
        for track in range(flights):
            for k in range(used_per_flight+random_per_flight):
                used=k<used_per_flight
                rows.append({
                    "batid":f"B{b:03d}",
                    "trackid":f"FLIGHT_{b:03d}_{track}",
                    "case_":"TRUE" if used else "FALSE",
                    "response_rvso":"1" if used else "0",
                    "field_period":"one" if track==0 else "two",
                    "sex":"m" if b%2 else "f",
                    "age_class":"ad",
                    "clc2_20m":"forest" if k%2 else "meadows",
                    "forestornot":"forest" if k%2 else "others",
                    "DistanceAssumedRoostsInKm":.5+(k%3)*.1,
                    # Known truth: used points closer to wind turbines,
                    # source bat and flight nesting, no individual learning.
                    "mindist_WKA_inKm":.12 if used else 5.8,
                })
    return pd.DataFrame(rows)


class FrozenBatEnvironmentDesign(unittest.TestCase):
    def test_actual_source_provenance_and_fit_scope(self):
        self.assertEqual(v.SOURCE_SHA256,
          "76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375")
        self.assertEqual(v.SOURCE_BATS,60)
        self.assertEqual(v.SOURCE_TRACKS,107)
        self.assertEqual(v.SOURCE_TRUE,8129)
        self.assertEqual(v.SOURCE_FALSE,40645)
        self.assertEqual(v.N_FOLDS,5)
        self.assertEqual(v.BOOT_REPS,10000)

    def test_original_source_uses_observations_not_GPS_coordinates(self):
        f=synthetic_bats()
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"synthetic.csv"
            f.to_csv(file,index=False)
            with patch.object(v,"SOURCE_ROWS",len(f)),\
                 patch.object(v,"SOURCE_BATS",30),\
                 patch.object(v,"SOURCE_TRACKS",60),\
                 patch.object(v,"SOURCE_TRUE",len(f[f["case_"]=="TRUE"])),\
                 patch.object(v,"SOURCE_FALSE",len(f[f["case_"]=="FALSE"])):
                parsed,profile=v.source_table(file)
        self.assertEqual(profile["source_independent_bats"],30)
        self.assertEqual(profile["source_flight_tracks"],60)
        self.assertFalse(profile["source_UTM_GPS_coordinates_or_height_parsed"])
        self.assertFalse(profile["original_bat_ID_and_flight_ID_values_exported"])
        self.assertEqual(len(parsed),len(f))

    def test_each_bat_equal_and_within_each_trip_balanced_source_weight(self):
        f=synthetic_bats(nbat=12)
        f["_bat"]=f["batid"];f["_track"]=f["trackid"]
        f["_y"]=(f["case_"]=="TRUE").astype(int)
        w=v.original_training_weights(f)
        for b,x in f.groupby("_bat"):
            self.assertAlmostEqual(float(w[x.index].sum()),1.,places=12)
            for _,flight in x.groupby("_track"):
                self.assertAlmostEqual(float(w[flight.index].sum()),.5,places=12)
                self.assertAlmostEqual(float(w[flight.index[flight["_y"]==1]].sum()),.25,places=12)
                self.assertAlmostEqual(float(w[flight.index[flight["_y"]==0]].sum()),.25,places=12)

    def test_known_turbine_effect_appears_beyond_landcover_roost_for_unseen_bats(self):
        f=synthetic_bats()
        f["_bat"]=f["batid"];f["_track"]=f["trackid"]
        f["_y"]=(f["case_"]=="TRUE").astype(int)
        with patch.object(v,"SOURCE_BATS",30):
            out,folds=v.all_bat_holdouts(f)
            report=v.summarize(out)
        self.assertEqual(len(folds),5)
        self.assertTrue(all(q["source_any_bat_ID_train_test_overlap"] is False
                            for q in folds.values()))
        self.assertEqual(report["source_total_independent_bat_IDs"],30)
        self.assertEqual(report["source_original_flights"],60)
        self.assertGreater(report["registered_outcome_contrasts"][
            "primary_wind_turbine_increment_M0_minus_M1"]["mean_bat_equal_gain"],.02)
        self.assertGreater(report["bat_equal_AUC_MN_M0_M1_M2"][2],.8)
        self.assertLess(report["bat_equal_balanced_logloss_MN_M0_M1_M2"][2],
                        report["bat_equal_balanced_logloss_MN_M0_M1_M2"][1])

    def test_heldout_bat_features_never_refit_train_preprocessing(self):
        f=synthetic_bats(12)
        f["_bat"]=f["batid"];f["_track"]=f["trackid"]
        f["_y"]=(f["case_"]=="TRUE").astype(int)
        train=f[f["_bat"]!="B000"].copy()
        test=f[f["_bat"]=="B000"].copy()
        before=v.build_design(train,test,1)[0]
        test.loc[test.index[0],"mindist_WKA_inKm"]=99.0
        after=v.build_design(train,test,1)[0]
        np.testing.assert_allclose(before,after,rtol=0,atol=0)
        self.assertNotIn("batid",v.CATEGORICAL+v.NUMERIC)
        self.assertNotIn("trackid",v.CATEGORICAL+v.NUMERIC)
        self.assertNotIn("case_",v.CATEGORICAL+v.NUMERIC)

    def test_numeric_domain_or_source_label_conflict_stop(self):
        f=synthetic_bats()
        f.loc[0,"mindist_WKA_inKm"]=-2
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"original.csv";f.to_csv(path,index=False)
            with patch.object(v,"SOURCE_ROWS",len(f)),\
                 patch.object(v,"SOURCE_BATS",30),\
                 patch.object(v,"SOURCE_TRACKS",60),\
                 patch.object(v,"SOURCE_TRUE",len(f[f["case_"]=="TRUE"])),\
                 patch.object(v,"SOURCE_FALSE",len(f[f["case_"]=="FALSE"])):
                with self.assertRaisesRegex(ValueError,"numeric km"):
                    v.source_table(path)

if __name__=="__main__":
    unittest.main()
