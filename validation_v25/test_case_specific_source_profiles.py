"""v25-F case-specific original units test; not a source-outcome confidence claim."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import case_specific_source_profiles as corrected
import retrospective_habitat_profiles as original


class FrozenCaseSpecificOriginalData(unittest.TestCase):
    def example(self,folder,bad=None):
        rows=[]
        for bird in ("SYN_A","SYN_B"):
            for date in ("1/2/2019 8:03","1/3/2019 8:03"):
                for case in ("TRUE","FALSE"):
                    v={
                        "birdyear":bird,"timestamp":date,
                        "species":"MALL","case":case,
                        "season":"Early Winter","photoperiod":"day"}
                    v.update({c:0 for c in original.ENV})
                    if case=="TRUE":
                        v["Rice"]=2 if bird=="SYN_A" else 1
                    else:
                        v["Rice"]=70
                        v["Field"]=30
                        if bird=="SYN_B":
                            v["Protected"]=100
                    rows.append(v)
        df=pd.DataFrame(rows,columns=original.COLUMNS)
        if bad=="used_multi_class":df.loc[0,"Corn"]=1
        if bad=="used_count_outside":df.loc[0,"Rice"]=3
        if bad=="false_noninteger":df.loc[1,"Rice"]=70.5
        path=Path(folder)/"source.csv"
        df.to_csv(path,index=False)
        return path

    def test_prior_v25c_and_v25d_invalid_are_immutable(self):
        self.assertEqual(corrected.ORIGINAL_C_STOP,
            "NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE")
        self.assertIn("INVALID_FOR_ECOLOGY",corrected.ORIGINAL_D_INVALID)
        self.assertEqual(corrected.DIVIDE_FALSE_BY,100.)
        self.assertEqual(corrected.SOURCE_SHA256,original.ORIGINAL_SOURCE_SHA256)
        self.assertEqual(original.N_FOLDS,5)
        self.assertEqual(original.SHRINK_KAPPA,2.)

    def test_used_occurrence_1_or_2_becomes_onehot_and_false_count_div_100(self):
        with tempfile.TemporaryDirectory() as root:
            input_file=self.example(root)
            normalized=Path(root)/"ephemeral_normalized.csv"
            with patch.object(corrected,"SOURCE_ROWS",8), \
                 patch.object(corrected,"EXPECTED_TRUE",4), \
                 patch.object(corrected,"EXPECTED_FALSE",4):
                qc=corrected.correct_original_case_specific_percentage(
                    input_file,normalized)
            d=pd.read_csv(normalized,dtype={"case":"string"})
        self.assertEqual(qc["original_used_category_nonzero_encoded_2"],2)
        self.assertEqual(qc["original_used_category_nonzero_encoded_1"],2)
        self.assertEqual(qc["original_false_total_more_than_100"],2)
        self.assertTrue(qc["old_D_all_field_100_division_IS_INVALID_FOR_ECOLOGY"])
        self.assertEqual(qc["normalized_source_rows_dropped"],0)
        tr=d[d["case"]=="TRUE"]
        fl=d[d["case"]=="FALSE"]
        self.assertTrue((tr["Rice"]==1.).all())
        self.assertTrue((fl["Rice"]==.7).all())
        self.assertTrue((fl["Field"]==.3).all())
        self.assertFalse(qc["animal_GPS_exact_time_ID_or_habitat_rows_redistributed"])

    def test_orig_used_more_than_one_nonzero_category_fails(self):
        with tempfile.TemporaryDirectory() as root:
            path=self.example(root,bad="used_multi_class")
            with patch.object(corrected,"SOURCE_ROWS",8), \
                 patch.object(corrected,"EXPECTED_TRUE",4), \
                 patch.object(corrected,"EXPECTED_FALSE",4):
                with self.assertRaisesRegex(ValueError,"one nonzero"):
                    corrected.correct_original_case_specific_percentage(
                        path,Path(root)/"out.csv")

    def test_orig_used_code_3_and_false_float_gate_fail(self):
        for bad,reason in (("used_count_outside","exactly 1 or 2"),
                           ("false_noninteger","integer 0..100")):
            with tempfile.TemporaryDirectory() as root:
                path=self.example(root,bad=bad)
                with patch.object(corrected,"SOURCE_ROWS",8), \
                     patch.object(corrected,"EXPECTED_TRUE",4), \
                     patch.object(corrected,"EXPECTED_FALSE",4):
                    with self.assertRaisesRegex(ValueError,reason):
                        corrected.correct_original_case_specific_percentage(
                            path,Path(root)/"out.csv")

if __name__=="__main__":
    unittest.main()
