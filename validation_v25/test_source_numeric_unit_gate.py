"""v25-D0 source numeric domain tests, without looking at original used/available values."""
from __future__ import annotations
import unittest
from unittest.mock import patch
import pandas as pd
import source_numeric_unit_gate as m

class SourceDomainTests(unittest.TestCase):
    def source(self,rows):
        return pd.DataFrame(rows,columns=m.ENV)

    def test_exact_source_and_original_frozen_stop(self):
        self.assertEqual(m.SOURCE_SHA256,
            "1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15")
        self.assertEqual(m.EXPECTED_ROWS,380578)
        self.assertEqual(len(m.ENV),7)

    def test_original_percentages_trigger_only_precommitted_divide_by_100(self):
        data=self.source([
            [0,0,0,0,0,0,100],
            [12,23,5,0,45,0,15],
            [30,0,30,30,20,0,20]])
        with patch.object(m,"EXPECTED_ROWS",3):
            d=m.characterize_raw_numeric_only(data)
        self.assertEqual(d["status"],"SOURCE_PERCENTAGE_UNIT_RULE_VERIFIED_NO_EFFECT")
        self.assertEqual(d["prespecified_all_field_scale_divisor"],100)
        self.assertFalse(d["original_source_case_used_available_values_read"])
        self.assertFalse(d["original_birdyear_or_timestamp_ID_values_read"])
        self.assertFalse(d["any_source_habitat_prediction_or_coefficients_computed"])

    def test_fraction_source_uses_identity(self):
        data=self.source([[0.1]*7,[0.2]*7,[1.0]*7])
        with patch.object(m,"EXPECTED_ROWS",3):
            d=m.characterize_raw_numeric_only(data)
        self.assertEqual(d["prespecified_all_field_scale_divisor"],1)

    def test_invalid_raw_range_or_na_fails_closed(self):
        for value in (-1,101,None):
            data=self.source([[1]*7,[0]*7,[1]*7])
            data.loc[1,"Corn"]=value
            with patch.object(m,"EXPECTED_ROWS",3):
                d=m.characterize_raw_numeric_only(data)
            self.assertEqual(d["status"],"NOT_ADMITTED_ORIGINAL_NUMERIC_RANGE_OR_MISSINGNESS")
            self.assertIsNone(d["prespecified_all_field_scale_divisor"])

if __name__=="__main__":
    unittest.main()
