"""Generality v1 known-truth and source/endpoint boundaries, not new field results."""
import unittest
import json
from copy import deepcopy
from math import isclose
from cross_source_evidence import (
    PUBLIC, LOCAL,blob_sha,verify_pin,summarize_rsds_twelve,
    summarize_rsds_four,build_evidence,_document_receipts)
from dynamic_policy_geometry import (
    phase_policy,phase_switch_total_variation)

class MechanisticSufficientConditions(unittest.TestCase):
    def test_same_current_state_opposite_derivative_changes_choices_when_accessible(self):
        before=phase_policy([1,1],[1,-1],[0,0],
                            phase=-1,response_horizon=1.)
        after=phase_policy([1,1],[1,-1],[0,0],
                           phase=1,response_horizon=1.)
        self.assertGreater(after[0],before[0])
        self.assertLess(after[1],before[1])
        self.assertAlmostEqual(after[0],before[1])
        self.assertGreater(phase_switch_total_variation(
            [1,1],[1,-1],[0,0],response_horizon=1.),.5)

    def test_zero_horizon_and_equal_state_rate_are_biological_null_cases(self):
        self.assertAlmostEqual(phase_switch_total_variation(
            [1,1],[1,-1],[0,0],response_horizon=0.),0)
        self.assertAlmostEqual(phase_switch_total_variation(
            [1,1],[.4,.4],[0,0],response_horizon=10.),0)
        self.assertAlmostEqual(phase_switch_total_variation(
            [1,1],[1,-1],[0,0],response_horizon=10.,reachable=[True,False]),0)
        with self.assertRaises(ValueError):
            phase_policy([1],[0],[0],phase=0,response_horizon=1)
        with self.assertRaises(ValueError):
            phase_policy([1],[0],[0],phase=1,response_horizon=1,reachable=[False])

class SourceUnitAndSignatureGuards(unittest.TestCase):
    def test_git_blob_byte_guard_detects_any_changed_source(self):
        raw=b'{"species":1,"estimate":null}\n'
        pin=blob_sha(raw)
        self.assertEqual(verify_pin(raw,pin,"KNOWN_SOURCE"),pin)
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            verify_pin(raw+b" ",pin,"KNOWN_SOURCE")
        self.assertEqual(len(PUBLIC),4)
        self.assertEqual(len(LOCAL),2)
        self.assertTrue(all(len(m[2])==40 for m in PUBLIC.values()))

    def test_original_holds_and_native_DOI_denominators_cannot_disappear(self):
        # Source-level in-memory fixture, not a new biological inference.
        rows=[]
        for i in range(12):
            count=3 if i<2 else 2 if i<8 else 1
            for j in range(count):
                # This fixture has intentionally wrong total/signs and MUST stop.
                rows.append({"original_study_doi":f"doi{i}",
                             "native_taxon":f"species{i}_{j}",
                             "q":{"status":"UNAVAILABLE","mean":None},
                             "daylength":{"status":"UNAVAILABLE","mean":None}})
        fake={"all_original_studies":12,
              "distinct_native_species_labels":20,
              "all_original_study_native_taxon_rows_including_HOLD":rows}
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            summarize_rsds_twelve(json.dumps(fake).encode())

    def test_shared_calendar_overlaps_not_four_extra_doIs(self):
        doc={
            "original_source_studies_with_identical_native_source_calendar_days":4,
            "original_studies_with_at_least_one_resolved_native_relative_q_rank":4,
            "original_studies_with_opposite_supported_native_daylength_slope_signs":3,
            "four_calendar_study_DOIs_already_in_twelve_study_full_source_macro":3,
            "Illinois_original_DOI_is_NOT_part_of_twelve_full_source_study_frame":True}
        out=summarize_rsds_four(json.dumps(doc).encode(),set())
        self.assertEqual(out["already_nested_within_twelve_DOIs"],3)
        self.assertTrue(out["no_second_independent_four_DOI_pool_allowed"])
        doc["four_calendar_study_DOIs_already_in_twelve_study_full_source_macro"]=0
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            summarize_rsds_four(json.dumps(doc).encode(),set())

    def test_independent_source_receipts_must_not_be_conflated_as_one_measure(self):
        fake=("186 source sites 24,290 site×date pairs "
              "38,792 recorded mammal/other-taxon detections "
              "43 source taxon labels 15 source labels 2.6284 0.7917 "
              "353 source photograph-date pairs 988 original camera detection rows "
              "camera ON-days")
        louis="10/10 birds 83.8% 0.162 1.001"
        boids="211 204 1,024 0.176419 0.038154 0.033282 0.304653 0.016655 0.065092"
        gauge="4,465 373 423 75.12% 431 433 99.54% NOT_ADMITTED"
        out=_document_receipts(fake,louis,boids,gauge)
        self.assertEqual(out["serengeti"]["independent_landscapes"],1)
        self.assertTrue(out["watlas"]["minus30_is_not_independent_new_species_heading_gain"])
        self.assertNotEqual(out["louis"]["response"],
                            out["wadden"]["response"])
        with self.assertRaisesRegex(ValueError,"SOURCE_STOP"):
            _document_receipts(fake.replace("camera ON-days",""),
                               louis,boids,gauge)

if __name__=="__main__":
    unittest.main()
