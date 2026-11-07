"""v61 strict original Schier source admission: tests only, no field GPS."""
import unittest
from copy import deepcopy
from run_original_schier_paired_heading import verify_schier_source,EXPECTED,EXPECTED_STAGES
import matched_tide_support as v59

def receipt():
    return {**EXPECTED,"admission":"SOURCE_SUPPORT_ADMITTED_FOR_LATER_PREREGISTERED_OUTCOME",
            "rising_rows_with_candidate_after_sequential_gates":
                dict(zip(v59.STAGES,EXPECTED_STAGES))}

class FrozenSchierAdmissibility(unittest.TestCase):
    def test_original_schier_immutable_gate(self):
        self.assertTrue(verify_schier_source([],[(0,1)]*211,receipt()))

    def test_any_source_gate_drift_hard_stops(self):
        for field in EXPECTED:
            r=receipt()
            r[field]+=1
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
                verify_schier_source([],[(0,1)]*211,r)
        for stage in v59.STAGES:
            r=receipt()
            r["rising_rows_with_candidate_after_sequential_gates"][stage]+=1
            with self.subTest(stage=stage),self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
                verify_schier_source([],[(0,1)]*211,r)

    def test_source_only_fail_not_biological_null(self):
        r=receipt()
        r["admission"]="NOT_ADMITTED_INSUFFICIENT_REAL_MATCHED_SOURCE_SUPPORT"
        with self.assertRaisesRegex(ValueError,"NOT_ADMITTED"):
            verify_schier_source([],[(0,1)]*211,r)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            verify_schier_source([],[(0,1)]*210,receipt())

if __name__=="__main__":unittest.main()
