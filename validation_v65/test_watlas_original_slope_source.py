"""v65 known-truth slope-from-source tests: synthetic data are NOT wildlife effects."""
from __future__ import annotations

import csv
import io
import unittest
from watlas_original_slope_source import (
    audit_slope_source_only,source_waterlevel_rate,_nearest_existing_reference,
    _phase, SOURCE_SHA,EXACT_RAW,EXACT_V64_MOVING_WITH_TIDE)
from watlas_cross_taxon_tide_source import source_only_audit

FIELDS=("TAG","TIME","X","Y","NBS","VARX","VARY","COVXY",
        "tideID","tidaltime","waterlevel")

def known_original_like(*,cycles=4,birds=3,minutes=241,falling=True,
                        mismatch=False,extra_heading=False):
    """All positions are *genuine synthetic records*, no hidden interpolation."""
    stream=io.StringIO()
    cols=list(FIELDS)+(["target_direction_east"] if extra_heading else [])
    w=csv.DictWriter(stream,fieldnames=cols)
    w.writeheader()
    for cycle in range(cycles):
        for bird in range(birds):
            for minute in range(minutes):
                h=(50+.4*min(minute,240-minute)) if falling else (50+.4*minute)
                if mismatch and bird==1:
                    h+=30.
                row={
                    "TAG":f"synthetic_tag_{bird}",
                    "TIME":1567296000+cycle*86400+minute*60,
                    "X":650000+bird*500+minute*24,
                    "Y":5900000+bird*500,
                    "NBS":4,"VARX":10,"VARY":10,"COVXY":0,
                    "tideID":f"synthetic_tide_{cycle}",
                    # Original clock can be nonnegative without labeling
                    # rising/falling physical waterlevel derivative.
                    "tidaltime":float(minute),
                    "waterlevel":h}
                if extra_heading:
                    row["target_direction_east"]=-9999 if minute%2 else 9999
                w.writerow(row)
    return stream.getvalue().encode()

class SourceSlopeTests(unittest.TestCase):
    def test_checksum_and_v64_source_receipt_pins(self):
        self.assertEqual(len(SOURCE_SHA),2)
        self.assertTrue(all(len(s)==64 for s in SOURCE_SHA.values()))
        self.assertEqual(EXACT_RAW["red_knot"],7595)
        self.assertEqual(EXACT_RAW["sanderling"],6509)
        self.assertEqual(EXACT_V64_MOVING_WITH_TIDE,{"red_knot":194,"sanderling":572})

    def test_genuine_30min_bracket_both_physical_signs(self):
        raw=known_original_like()
        q=audit_slope_source_only(raw)
        old=source_only_audit(raw)
        self.assertEqual(q["eligible_moving_stage_counts"][
            "original_waterlevel_and_tidaltime_present"],
            old["three_fix_candidates_with_original_tide_metadata"])
        self.assertEqual(q["source"]["source_tidaltime_negative_bins"],0)
        self.assertEqual(q["source"]["source_tidaltime_zero_bins"],12)
        self.assertGreater(q["source_phase_classification_counts"]["rising"],30)
        self.assertGreater(q["source_phase_classification_counts"]["falling"],30)
        self.assertEqual(q["source_distinct_tideIDs_with_rising_or_falling_triples"],4)
        self.assertEqual(q["original_birds_with_rising_or_falling_triples"],3)
        self.assertGreaterEqual(q["source_tideIDs_with_at_least_20_non_slack_triples"],2)
        self.assertEqual(q["admission"],"SOURCE_FEASIBLE_FOR_FUTURE_INDEPENDENT_TIDAL_SLOPE_FORECAST")
        self.assertTrue(q["no_next_heading_angle_model_or_ecological_effect_scored"])
        self.assertNotIn("synthetic_tag_1",str(q))
        self.assertNotIn("synthetic_tide_0",str(q))
        self.assertNotIn("650024",str(q))

    def test_no_future_heading_leakage(self):
        plain=audit_slope_source_only(known_original_like(cycles=1))
        with_future=audit_slope_source_only(known_original_like(cycles=1,extra_heading=True))
        self.assertEqual(plain,with_future)

    def test_without_real_pre_and_post_gauge_brackets_does_not_qualify(self):
        q=audit_slope_source_only(known_original_like(minutes=12))
        self.assertEqual(q["source_phase_classification_counts"]["rising"],0)
        self.assertEqual(q["source_phase_classification_counts"]["falling"],0)
        self.assertGreater(q["source_phase_classification_counts"]["unbracketed"],0)
        self.assertIn("NOT_ADMITTED",q["admission"])

    def test_real_brackets_one_physical_phase_not_two_directions(self):
        q=audit_slope_source_only(known_original_like(minutes=121,falling=False))
        self.assertGreater(q["source_phase_classification_counts"]["rising"],0)
        self.assertEqual(q["source_phase_classification_counts"]["falling"],0)
        self.assertIn("NOT_ADMITTED",q["admission"])

    def test_simultaneous_contradictions_are_removed_no_averaging(self):
        q=audit_slope_source_only(known_original_like(mismatch=True))
        self.assertGreater(q["reference_simultaneous_report_contradictions_dropped"],0)
        self.assertEqual(q["source_phase_classification_counts"]["rising"],0)
        self.assertEqual(q["source_phase_classification_counts"]["falling"],0)
        self.assertIn("NOT_ADMITTED",q["admission"])

    def test_nearest_genuine_reference_earlier_tie_no_interpolation(self):
        self.assertEqual(_nearest_existing_reference([0,600,1200],0,1200,900),1)
        self.assertIsNone(_nearest_existing_reference([0,600,1200],601,1199,900))
        self.assertIsNone(source_waterlevel_rate(3600,"cycle",{"cycle":([3000],[120])}))
        ref={"cycle":([1800,5400],[20.,80.])}
        self.assertAlmostEqual(source_waterlevel_rate(3600,"cycle",ref),60.)
        self.assertEqual(_phase(60.),"rising")
        self.assertEqual(_phase(-60.),"falling")
        self.assertEqual(_phase(2.),"slack")
        self.assertEqual(_phase(None),"unbracketed")

    def test_source_schema_is_required(self):
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            audit_slope_source_only(b"TAG,TIME,X,Y\nid,1567296000,650000,5900000\n")

if __name__=="__main__":
    unittest.main()
