"""v24-S synthetic-only wetland brood holdout and environmental score tests.

Does not open ANY 2026 USGS habitat choice outcomes. Synthetic brood
observations contain known environmental preferences and generated available
points, with the same 400-control shape as the source.
"""
from __future__ import annotations

import math
import unittest
import numpy as np
import pandas as pd

import static_habitat_transfer as v


def synthetic_broods(ids=("A","B"), nused=2):
    rows=[]
    for b in ids:
        for k in range(nused + 400):
            used=int(k<nused)
            rows.append({
                "_brood":b,
                "_label":used,
                "_species":"Mallard" if b=="A" else "Gadwall",
                "_year":"2017",
                "Wetland Type":"seasonal" if used else "permanent",
                "Dominant Veg Category":"emergent" if used else "openwater",
                "Percent Veg of Unit":60 if used else 5,
                "Salinity Concentration":1.5 if used else 15.,
                "Wetland Area":10000 if used else 50000,
            })
    return pd.DataFrame(rows)


class TestOriginalStaticPreferenceDesign(unittest.TestCase):
    def test_declared_undated_original_source_and_hashes(self):
        self.assertEqual(v.SOURCE_SHA256,
           "e4ac32416e2f013efcca8e40b9916e73c72e2e1891a09f78d865524ee16ea036")
        self.assertEqual(v.EXPECTED_BROODS,185)
        self.assertEqual(v.EXPECTED_USED,2069)
        self.assertEqual(v.EXPECTED_AVAIL,74000)
        self.assertEqual(v.EXPECTED_AVAILABLE_PER_BROOD,400)
        self.assertEqual(v.ORIGINAL_FUTURE_HISTORY_STATUS,
           "NOT_ADMITTED_NO_DATED_WETLAND_CHOICE_OR_MATCHED_TEMPORAL_AVAILABILITY")
        self.assertEqual(v.BOOT_REPS,10000)
        self.assertEqual(v.C_VALUE,1.)

    def test_all_duckling_points_in_one_brood_fold(self):
        x=synthetic_broods(ids=("A","B","C","D","E","F"))
        folds=x["_brood"].map(v.fold_for_brood)
        self.assertEqual(folds[x["_brood"]=="A"].nunique(),1)
        self.assertEqual(folds[x["_brood"]=="C"].nunique(),1)
        self.assertIn(v.fold_for_brood("A"),range(5))
        self.assertEqual(v.fold_for_brood("A"),v.fold_for_brood("A"))

    def test_equal_independent_brood_and_class_training_weights(self):
        x=synthetic_broods(nused=3)
        w=v.training_brood_weights(x)
        for b in ("A","B"):
            test=x["_brood"]==b
            self.assertAlmostEqual(float(w[test].sum()),1.)
            self.assertAlmostEqual(float(w[test & (x["_label"]==1)].sum()),.5)
            self.assertAlmostEqual(float(w[test & (x["_label"]==0)].sum()),.5)

    def test_train_only_features_and_source_missingness_imputation(self):
        x=synthetic_broods()
        train=x[x["_brood"]=="A"].copy()
        test=x[x["_brood"]=="B"].copy()
        test.loc[test.index[0],"Wetland Type"]="unseen_future_wetland_class"
        test.loc[test.index[0],"Salinity Concentration"]=np.nan
        z,ztest=v.build_features(train,test,False)
        z2,ztest2=v.build_features(train,test,True)
        self.assertEqual(len(z),len(train))
        self.assertEqual(len(ztest),len(test))
        self.assertEqual(z2.shape[1],2*z.shape[1])
        self.assertTrue(np.isfinite(ztest).all())
        self.assertTrue(np.isfinite(ztest2).all())

    def test_original_generated_available_not_401_independent_birds(self):
        x=synthetic_broods()
        predictions={
          "M1":np.where(x["_label"].to_numpy()==1,2.,0.),
          "M2":np.zeros(len(x)),
        }
        r=v.per_brood_metrics(x,predictions)
        self.assertEqual(len(r),2)
        for val in r.values():
            self.assertEqual(val["n_generated_available_source_points"],400)
            self.assertAlmostEqual(val["M0_auc_uniform"],.5)
            self.assertAlmostEqual(val["M1_brood_used_available_auc"],1.)
            self.assertAlmostEqual(val["M2_brood_used_available_auc"],.5)
            self.assertLess(val["M1_pseudochoice_logloss"],math.log(401))
            self.assertAlmostEqual(val["M2_pseudochoice_logloss"],math.log(401))

    def test_out_of_range_source_habitat_covariate_fails_closed(self):
        x=synthetic_broods()
        x.loc[0,"Percent Veg of Unit"]=104.
        with self.assertRaisesRegex(ValueError,"Percent vegetation"):
            v.numeric_source_values(x)
        x=synthetic_broods()
        x.loc[0,"Salinity Concentration"]=-1.
        with self.assertRaisesRegex(ValueError,"Nonnegative"):
            v.numeric_source_values(x)

    def test_uniform_environment_no_fake_gain(self):
        same=synthetic_broods()
        same["Wetland Type"]="permanent"
        same["Dominant Veg Category"]="openwater"
        same["Percent Veg of Unit"]=25.
        same["Salinity Concentration"]=5.
        same["Wetland Area"]=20000.
        pred=v.fit_predict(same,same,False)
        r=v.per_brood_metrics(same,{"M1":pred})
        for val in r.values():
            self.assertAlmostEqual(val["M1_brood_used_available_auc"],.5)
            self.assertAlmostEqual(val["M1_pseudochoice_logloss"],math.log(401))

    def test_anonymized_bootstrap_group_level_known_truth(self):
        rows={}
        for i in range(v.EXPECTED_BROODS):
            rows[f"source#{i:03d}"]={
                "M1_brood_used_available_auc":.7,
                "M2_brood_used_available_auc":.71,
                "M1_pseudochoice_logloss":5.2,
                "M2_pseudochoice_logloss":5.0,
                "n_used_source_points":5,
                "n_generated_available_source_points":400,
            }
        q=v.aggregate_per_brood(rows)
        self.assertEqual(q["original_independent_brood_count"],185)
        self.assertEqual(q["original_pseudoused_points"],925)
        primary=q["original_registered_contrasts"][
            "primary_M1_auc_minus_uniform_half"]
        self.assertAlmostEqual(primary["equal_brood_mean_gain"],.2)
        self.assertEqual(primary["broods_with_positive_gain"],185)
        self.assertTrue(all(
          k.startswith("source_brood_") for k in q["per_brood_anonymized"]))
        self.assertNotIn("source#001",str(q))


if __name__=="__main__":
    unittest.main()
