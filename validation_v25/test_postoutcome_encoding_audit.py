"""v25-D2 POST-OUTCOME diagnostic pure known truth, not fitted ecology.

Both YES and NO possibilities are deliberately tested; the algorithm
cannot choose a winning rule after seeing USGS observed outcomes.
"""
from __future__ import annotations
import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np
import postoutcome_encoding_audit as d


def source_frame(original_TRUE,source_FALSE):
    rows=[]
    for b,(a,c) in enumerate(zip(original_TRUE,source_FALSE)):
        for name,x in (("TRUE",a),("FALSE",c)):
            rows.append({
                "birdyear":f"TEST_BIRD_{b//3}",
                "timestamp":f"1/{1+b%3}/2020 8:03",
                "species":"MALL",
                "case":name,
                "season":"Early Winter",
                "photoperiod":"day",
                **dict(zip(d.HABITAT,x))})
    return pd.DataFrame(rows,columns=d.COLUMNS)


class StructuralEncodingAudit(unittest.TestCase):
    def test_original_published_source_and_postoutcome_status(self):
        self.assertEqual(d.SOURCE_ROWS,380578)
        self.assertEqual(d.SOURCE_PAIRS,190289)
        self.assertEqual(d.SOURCE_BIRDYEARS,493)
        self.assertEqual(d.ORIGINAL_SHA256,
            "1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15")

    def test_trivial_onehot_versus_multicategory_needs_no_training(self):
        true=[[0,0,0,0,100,0,0],
              [0,100,0,0,0,0,0],
              [0,0,0,100,0,0,0]]
        false=[[15,12,6,5,21,5,36],
               [20,40,20,0,10,0,10],
               [9,11,15,30,14,8,13]]
        with patch.object(d,"SOURCE_ROWS",6),\
             patch.object(d,"SOURCE_PAIRS",3),\
             patch.object(d,"SOURCE_BIRDYEARS",1):
            out=d.diagnostic(source_frame(true,false))
        self.assertEqual(out["status"],
            "POSTOUTCOME_ORIGINAL_USED_AVAIL_PROFILE_ENCODING_DIAGNOSTIC")
        self.assertEqual(
            out["source_case_TRUE_used_original_profile_summary"]["n_exact_one_hot_100"],3)
        self.assertEqual(
            out["source_case_FALSE_simulated_available_aggregate_profile_summary"]["n_exact_one_hot_100"],0)
        for model in d.SCORES:
            self.assertEqual(
                out["three_no_training_structural_rank_controls"][model]["overall_paired_classification_rank"],1.0)
            self.assertTrue(
                out["three_no_training_structural_rank_controls"][model]["method_has_no_fitted_parameter"])
        self.assertFalse(out["source_future_locations_or_behavioral_choice_effect_model_fitted"])
        self.assertTrue(out["this_is_post_outcome_not_confirmatory"])
        self.assertNotIn("TEST_BIRD",str(out))

    def test_trivial_rules_may_be_inconclusive_or_wrong(self):
        # Intentionally make FALSE equally sparse in one record, more
        # concentrated than TRUE in another. Neither sign is forced.
        true=[[100,0,0,0,0,0,0],[50,50,0,0,0,0,0],[0,0,0,0,100,0,0]]
        false=[[100,0,0,0,0,0,0],[100,0,0,0,0,0,0],[20,20,20,0,20,0,20]]
        with patch.object(d,"SOURCE_ROWS",6),\
             patch.object(d,"SOURCE_PAIRS",3),\
             patch.object(d,"SOURCE_BIRDYEARS",1):
            out=d.diagnostic(source_frame(true,false))
        test=out["three_no_training_structural_rank_controls"]["max_pct"]
        self.assertEqual(test["source_pairs_tied"],1)
        self.assertEqual(test["source_pairs_false_wins"],1)
        self.assertEqual(test["source_pairs_true_wins"],1)
        self.assertEqual(
            out["n_paired_used_TRUE_equals_available_FALSE_in_all_seven_fields"],1)
        self.assertAlmostEqual(test["overall_paired_classification_rank"],.5)

    def test_source_not_allow_original_habitat_percent_above_100(self):
        a=source_frame([[100,0,0,0,0,0,0]],
                       [[20,20,20,20,20,0,0]])
        a.loc[0,"Corn"]=101
        with patch.object(d,"SOURCE_ROWS",2),\
             patch.object(d,"SOURCE_PAIRS",1),\
             patch.object(d,"SOURCE_BIRDYEARS",1):
            with self.assertRaisesRegex(ValueError,"percentage"):
                d.diagnostic(a)

    def test_missing_true_or_false_pair_stops(self):
        a=source_frame([[100,0,0,0,0,0,0]],
                       [[20,20,20,20,20,0,0]])
        a.loc[1,"timestamp"]="1/2/2020 8:03"
        with patch.object(d,"SOURCE_ROWS",2),\
             patch.object(d,"SOURCE_PAIRS",1),\
             patch.object(d,"SOURCE_BIRDYEARS",1):
            with self.assertRaisesRegex(ValueError,"paired"):
                d.diagnostic(a)


if __name__=="__main__":
    unittest.main()
