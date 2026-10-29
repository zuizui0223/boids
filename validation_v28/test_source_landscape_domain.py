"""v28-C0 independent bat source numeric scale/no-outcome safety tests."""
import unittest
from unittest.mock import patch
import pandas as pd
import source_landscape_domain as v

class FourOriginalCovariates(unittest.TestCase):
    def fixtures(self):
        return pd.DataFrame({
          "mindist_WKA_inKm":[0.,1.4,5.8,22.],
          "DistanceAssumedRoostsInKm":[.3,1.2,8.5,0.],
          "clc2_20m":["312","112","311","231"],
          "forestornot":["forest","nonforest","forest","forest"],
        })
    def test_pinned_original_source(self):
        self.assertEqual(v.ROWS,48774)
        self.assertEqual(v.SOURCE_SHA256,
            "76f92b1442eb4350ee6d83ede83b5e43fda4b9f3997e3fd9a3618a44f2470375")
        self.assertEqual(v.NUMERIC,("mindist_WKA_inKm","DistanceAssumedRoostsInKm"))
        self.assertEqual(v.CATEGORIES,("clc2_20m","forestornot"))

    def test_nonnegative_km_and_categories_only_no_used_label(self):
        with patch.object(v,"ROWS",4):
            d=v.audit(self.fixtures())
        self.assertEqual(d["status"],"SOURCE_COVARIATE_DOMAIN_VERIFIED_NO_BAT_PREFERENCE")
        self.assertEqual(d["original_numeric_source_global_domains"]["mindist_WKA_inKm"]["finite_maximum"],22.)
        self.assertFalse(d["source_original_used_random_case_label_read"])
        self.assertFalse(d["source_actual_bat_ID_or_track_ID_read"])
        self.assertFalse(d["source_effect_or_predictive_model_fitted"])

    def test_negative_or_missing_original_distance_requires_failure(self):
        f=self.fixtures()
        f.loc[0,"mindist_WKA_inKm"]=-1
        with patch.object(v,"ROWS",4):
            r=v.audit(f)
        self.assertEqual(r["status"],"NOT_ADMITTED_NUMERIC_OR_CATEGORY_SOURCE_DOMAIN")
        f=self.fixtures()
        f.loc[0,"mindist_WKA_inKm"]=None
        with patch.object(v,"ROWS",4):
            r=v.audit(f)
        self.assertEqual(r["status"],"NOT_ADMITTED_NUMERIC_OR_CATEGORY_SOURCE_DOMAIN")
if __name__=="__main__":
    unittest.main()
