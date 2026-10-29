"""v25-C synthetic-only original-style paired habitat source model tests.

No original environmental habitat numeric value or real USGS waterfowl choice
observation is read before all these model and no-future-leakage tests pass.
"""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

import retrospective_habitat_profiles as m


def synthetic_original(nbirds=35, n_steps=10):
    rows=[]
    for bird in range(nbirds):
        for k in range(n_steps):
            metadata={
                "birdyear":f"Bird{bird:03d}_2020",
                "timestamp":f"1/{k+1}/2020 {8+k%12}:03",
                "species":m.SOURCE_TAXA[bird%4],
                "season":m.SOURCE_SEASONS[k%3],
                "photoperiod":m.SOURCE_PHOTOPERIOD[k%2],
            }
            for use in ("TRUE","FALSE"):
                # Known source truth: selected profile usually more rice
                # and protected habitat than aggregate availability,
                # with individual differences; no real field data.
                x=np.array([.10,.05,.02,.5,.6,.01,.12]) if use=="TRUE" else np.array(
                    [.18,.25,.15,.18,.16,.04,.20])
                x=x.copy()
                x[4]+=(bird%5)*.018
                x[3]+=(k%3)*.01
                rows.append({**metadata,"case":use,
                             **dict(zip(m.ENV,map(float,x)))})
    return pd.DataFrame(rows,columns=m.COLUMNS)


class OriginalPairedSourceKnownTruth(unittest.TestCase):
    def test_source_pin_and_stratum_not_101_real_options(self):
        self.assertEqual(m.ORIGINAL_SOURCE_SHA256,
            "1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15")
        self.assertEqual(m.ORIGINAL_ROWS,380578)
        self.assertEqual(m.ORIGINAL_PAIRS,190289)
        self.assertEqual(m.ORIGINAL_BIRDYEAR_IDS,493)
        self.assertEqual(m.SHRINK_KAPPA,2.)
        self.assertEqual(m.MIN_OWN_EARLIER_PAIRED_EVENTS,3)
        self.assertEqual(len(m.ENV),7)

    def _write_and_read(self,raw:pd.DataFrame):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/"synthetic.csv"
            raw.to_csv(p,index=False)
            with patch.object(m,"ORIGINAL_ROWS",len(raw)), \
                 patch.object(m,"ORIGINAL_PAIRS",len(raw)//2), \
                 patch.object(m,"ORIGINAL_BIRDYEAR_IDS",raw["birdyear"].nunique()):
                paired,qc=m.original_source_paired_profile(p)
        return paired,qc

    def test_original_TRUE_false_aggregate_pair_mapping_and_no_raw_values_exported(self):
        raw=synthetic_original()
        paired,qc=self._write_and_read(raw)
        self.assertEqual(len(paired),350)
        self.assertEqual(qc["source_matched_TRUE_FALSE_profile_pairs"],350)
        self.assertEqual(qc["source_birdyear_tokens"],35)
        self.assertTrue(qc["source_TRUE_FALSE_is_retroactive_aggregated_comparison"])
        self.assertFalse(qc["original_habitat_row_values_republished"])
        self.assertEqual(set(paired["species"]),set(m.SOURCE_TAXA))
        self.assertEqual(set(paired["season"]),set(m.SOURCE_SEASONS))
        self.assertEqual(set(paired["photoperiod"]),set(m.SOURCE_PHOTOPERIOD))

    def test_original_invalid_habitat_range_stops_before_scoring(self):
        raw=synthetic_original()
        raw.loc[0,"Corn"]=1.2
        with self.assertRaisesRegex(ValueError,"domain violated"):
            self._write_and_read(raw)
        raw=synthetic_original()
        raw.loc[1,"Wetland"]=np.nan
        with self.assertRaisesRegex(ValueError,"domain violated"):
            self._write_and_read(raw)

    def test_predeclared_birdyear_folds_never_train_on_test_identity(self):
        original,qc=self._write_and_read(synthetic_original(nbirds=45))
        scored,folds=m.all_fold_results(original)
        self.assertEqual(len(folds),5)
        self.assertEqual(len(scored),45*7)
        self.assertTrue(all(v["model_training_contains_target_birdyear"] is False
                            for v in folds.values()))
        with patch.object(m,"MIN_EVALUATED_BIRDYEAR",10):
            result=m.cluster_stats(scored)
        self.assertEqual(result["original_independent_source_birdyear_tokens"],45)
        self.assertAlmostEqual(result["whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3"][0],
                               np.log(2))
        self.assertLess(result["whole_birdyear_equal_mean_surrogate_logloss_M0_M1_M2_M3"][1],
                        np.log(2))
        self.assertFalse(result["no_real_before_step_destinations_or_100_options"] is False)
        self.assertEqual(len(result["frozen_contrasts"]),4)

    def test_own_future_last_pair_cannot_affect_earlier_history_scores(self):
        paired,_=self._write_and_read(synthetic_original(nbirds=35))
        f=m.birdyear_fold(str(paired["birdyear"].iloc[0]))
        test=paired[paired["birdyear"].map(m.birdyear_fold)==f].copy()
        train=paired[paired["birdyear"].map(m.birdyear_fold)!=f].copy()
        beta=m.train_equal_birdyear_logit(train)
        bs=m.train_equal_birdyear_logit(train,True)
        a=m.test_birdyear_holdout(test,beta,bs)
        changed=test.copy()
        target=changed["birdyear"].iloc[0]
        last_idx=changed.index[changed["birdyear"]==target][-1]
        changed.loc[last_idx,"d_Corn"]+=.25
        b=m.test_birdyear_holdout(changed,beta,bs)
        def earlier(items):
            return {(r["birdyear"],r["year"],r["season"],r["photoperiod"],j):
                    (r["loss_M1"],r["loss_M3"]) for j,r in enumerate(items)
                    if r["birdyear"]!=target}
        self.assertEqual(earlier(a),earlier(b))
        self.assertTrue(all(x["birdyear"]==y["birdyear"] for x,y in zip(a,b)))

    def test_species_features_are_conditional_differences_not_main_effect(self):
        pair,_=self._write_and_read(synthetic_original(nbirds=35))
        d=m.env_difference(pair)
        features=m.individual_model_input(d,pair["species"].to_numpy())
        self.assertEqual(features.shape,(len(pair),7+4*7))
        self.assertTrue(np.isfinite(features).all())
        self.assertEqual(m.birdyear_fold("stable-birdyear"),
                         m.birdyear_fold("stable-birdyear"))


if __name__=="__main__":
    unittest.main()
