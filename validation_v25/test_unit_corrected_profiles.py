"""v25-D1 source-unit-only regression tests before real habitat effects are opened."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import unit_corrected_profiles as new
import retrospective_habitat_profiles as old
import source_numeric_unit_gate as source


class TestSeparatedSourceUnitExploration(unittest.TestCase):
    def fixture(self,root,negative=False):
        rows=[]
        for birdyear in ("synthetic_A","synthetic_B"):
            for date in ("1/1/2020 8:03","1/2/2020 8:03"):
                for typ in ("TRUE","FALSE"):
                    original={
                        "birdyear":birdyear,
                        "timestamp":date,
                        "species":"MALL",
                        "case":typ,
                        "season":"Early Winter",
                        "photoperiod":"day",
                    }
                    original.update({
                       name:float(50 if typ=="TRUE" else 20)
                       for name in old.ENV})
                    rows.append(original)
        data=pd.DataFrame(rows,columns=old.COLUMNS)
        if negative:
            data.loc[0,"Corn"]=-5.
        p=Path(root)/"author_original.csv"
        data.to_csv(p,index=False)
        return p

    def test_original_v25C_stop_and_frozen_source_still_preserved(self):
        self.assertEqual(new.FROZEN_OLD_C_STATUS,
            "NOT_ADMITTED_FROZEN_ORIGINAL_HABITAT_DOMAIN_OR_SOURCE")
        self.assertEqual(new.ONLY_PERMITTED_DIVISOR,100)
        self.assertEqual(new.SOURCE_SHA256,old.ORIGINAL_SOURCE_SHA256)
        self.assertEqual(new.BOOTSTRAP_REPS if hasattr(new,"BOOTSTRAP_REPS") else old.BOOTSTRAP_RESAMPLES,10000)
        self.assertEqual(old.N_FOLDS,5)
        self.assertEqual(old.SHRINK_KAPPA,2.)

    def test_only_universal_percent_divisor_and_categorical_IDs_unchanged(self):
        with tempfile.TemporaryDirectory() as root:
            original=self.fixture(root)
            corrected=Path(root)/"unit_corrected.csv"
            with patch.object(source,"EXPECTED_ROWS",8),patch.object(old,"ORIGINAL_ROWS",8):
                out=new.unit_normalized_transient_original(original,corrected)
            expected=pd.read_csv(corrected,dtype={"case":str,"birdyear":str})
        self.assertEqual(out["universal_divisor"],100)
        self.assertFalse(out["new_observed_effects_or_outcomes_used_to_choose_scaling"])
        self.assertEqual(expected["birdyear"].nunique(),2)
        self.assertEqual(set(expected["case"]),{"TRUE","FALSE"})
        self.assertTrue(all((expected[x]>=0).all() and (expected[x]<=1).all()
                            for x in old.ENV))
        self.assertAlmostEqual(expected.loc[0,"Corn"],.5)

    def test_unit_correction_cannot_rescue_raw_negative_habitat_values(self):
        with tempfile.TemporaryDirectory() as root:
            original=self.fixture(root,negative=True)
            corrected=Path(root)/"unit_corrected.csv"
            with patch.object(source,"EXPECTED_ROWS",8),patch.object(old,"ORIGINAL_ROWS",8):
                with self.assertRaisesRegex(ValueError,"percentage normalization gate"):
                    new.unit_normalized_transient_original(original,corrected)

    def test_identical_M0_history_and_source_fold_algorithm_reused(self):
        self.assertEqual(new.FROZEN_NEW_PROTOCOL,
            "docs/V25D_FROZEN_PERCENT_CORRECTED_EXPLORATORY_PROFILE.md")
        self.assertEqual(old.M0_LOGLOSS,float(np.log(2)))
        self.assertEqual(old.MIN_OWN_EARLIER_PAIRED_EVENTS,3)
        self.assertEqual(old.birdyear_fold("synthetic-year-1"),
                         old.birdyear_fold("synthetic-year-1"))

if __name__=="__main__":
    unittest.main()
