"""v25-E AFTER-outcome only, original source geometry/no fitted behavior tests."""
import unittest
from unittest.mock import patch
import numpy as np

import postresult_source_artifact as p


class SourceConstructionDiagnostic(unittest.TestCase):
    def test_original_previous_result_is_not_recast_as_confirmatory(self):
        self.assertEqual(p.SOURCE_D_PRIMARY_GAIN,0.0058554394644328165)
        self.assertEqual(p.D_PERFECT_PAIRED_RANKING,1.0)
        self.assertEqual(p.ORIGINAL_C_STOP,
            "NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE")
        self.assertEqual(p.EXPECTED_PAIRS,190289)

    def test_concentrated_used_and_averaged_available_is_trivially_separable(self):
        actual=np.array([[100,0,0,0,0,0,0],[0,100,0,0,0,0,0]],float)
        avail=np.array([[50,50,0,0,0,0,0],[20,60,20,0,0,0,0]],float)
        with patch.object(p,"EXPECTED_PAIRS",2):
            r=p.numeric_simple_probe(actual,avail)
        self.assertEqual(r["source_naive_NO_FIT_sum_ranking"][
            "fraction_TRUE_ranked_above_FALSE_by_naive_source_invariant"],.5)
        self.assertEqual(r["source_naive_NO_FIT_concentration_norm_ranking"][
            "fraction_TRUE_ranked_above_FALSE_by_naive_source_invariant"],1.)
        self.assertTrue(r["this_missing"] if False else not r["any_new_confirmatory_ecological_hypothesis_test"])
        self.assertFalse(r["fitted_prediction_models_or_coefficients_changed"])

    def test_nontrivial_used_can_have_less_concentration_than_available(self):
        a=np.array([[50,50,0,0,0,0,0],[1,1,1,1,1,1,1]],float)
        b=np.array([[100,0,0,0,0,0,0],[1,1,1,1,1,1,1]],float)
        with patch.object(p,"EXPECTED_PAIRS",2):
            r=p.numeric_simple_probe(a,b)
        self.assertEqual(r["source_naive_NO_FIT_concentration_norm_ranking"][
            "fraction_TRUE_ranked_above_FALSE_by_naive_source_invariant"],.25)

    def test_source_outside_original_percent_domain_stops_without_effect(self):
        a=np.array([[101]*7],float);b=np.array([[0]*7],float)
        with patch.object(p,"EXPECTED_PAIRS",1):
            with self.assertRaisesRegex(ValueError,"percentage"):
                p.numeric_simple_probe(a,b)

if __name__=="__main__":
    unittest.main()
