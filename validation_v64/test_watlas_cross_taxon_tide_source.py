"""v64 synthetic source-only WATLAS individual tide-label and cadence tests."""
from __future__ import annotations
import csv
import io
import unittest
from watlas_cross_taxon_tide_source import (
    source_only_audit,_source_phase_proxy,MIN_TRIPLES,MIN_BIRDS,MIN_TIDES,
    MIN_PER_PHASE,MIN_HOLDOUT_CYCLES,NEEDED,ARTICLES)

FIELDS=["TAG","TIME","X","Y","NBS","VARX","VARY","COVXY",
        "tideID","tidaltime","waterlevel"]

def synthetic_source(*,tides=4,birds=3,each=16,include_flood=True,
                     firstyear=1567296000):
    fp=io.StringIO()
    writer=csv.DictWriter(fp,fieldnames=FIELDS)
    writer.writeheader()
    for tide in range(tides):
        for bird in range(birds):
            for phase,minutes in (("before",-180),("after",180)):
                if phase=="before" and not include_flood:continue
                for k in range(each):
                    writer.writerow({
                        "TAG":f"anonymized_{bird}",
                        "TIME":firstyear+tide*86400+(0 if phase=="before" else 3*3600)+k*30,
                        "X":650000+bird*200+k*12,
                        "Y":5900000+bird*200,
                        "NBS":4,"VARX":12,"VARY":12,"COVXY":0,
                        "tideID":f"original_cycle_{tide}",
                        "tidaltime":minutes+k/2,
                        "waterlevel":(100 if phase=="before" else 70)+k*.05})
    return fp.getvalue().encode()

class TwoSpeciesOriginalTideSource(unittest.TestCase):
    def test_original_figshare_species_have_pinned_distinct_ids(self):
        self.assertEqual(ARTICLES["red_knot"][0],26553446)
        self.assertEqual(ARTICLES["sanderling"][0],26553443)
        self.assertEqual(len(NEEDED),11)
        self.assertEqual(_source_phase_proxy(-60),"before_high")
        self.assertEqual(_source_phase_proxy(60),"after_high")
        for v in (-360,-15,0,15,360,None):
            self.assertIsNone(_source_phase_proxy(v))

    def test_outcome_free_positive_4_tides_and_both_signed_windows(self):
        result=source_only_audit(synthetic_source())
        self.assertEqual(result["original_raw_rows"],384)
        self.assertEqual(result["original_TAG_count_after_QC"],3)
        self.assertEqual(result["original_tideID_count_after_QC"],4)
        self.assertEqual(result["original_TAG_30s_location_bins"],384)
        self.assertEqual(result["observed_three_fix_candidates_with_both_gaps_30_to_180_s"],336)
        self.assertEqual(result["proxy_before_high_triplets"],168)
        self.assertEqual(result["proxy_after_high_triplets"],168)
        self.assertEqual(result["tideIDs_with_at_least_20_eligible_source_triples"],4)
        self.assertEqual(result["admission"],"SOURCE_FEASIBLE_FOR_SEPARATE_PREREGISTERED_TIDAL_FORECAST")
        self.assertEqual((MIN_TRIPLES,MIN_BIRDS,MIN_TIDES,MIN_PER_PHASE,MIN_HOLDOUT_CYCLES),
                         (120,3,4,30,2))
        self.assertTrue(result["no_observed_next_heading_effect_or_tide_model_estimated"])
        self.assertNotIn("anonymized_1",str(result))
        self.assertNotIn("original_cycle_1",str(result))
        self.assertNotIn("650012",str(result))

    def test_source_failure_without_before_or_four_cycles_not_null_ecology(self):
        for raw in (synthetic_source(include_flood=False),
                    synthetic_source(tides=2),
                    synthetic_source(birds=1),
                    synthetic_source(each=3)):
            with self.subTest(raw_len=len(raw)):
                result=source_only_audit(raw)
                self.assertEqual(result["admission"],
                                 "NOT_ADMITTED_INSUFFICIENT_ORIGINAL_INDIVIDUAL_TIDAL_TRAJECTORIES")
                self.assertTrue(result["no_observed_next_heading_effect_or_tide_model_estimated"])

    def test_no_interp_cross_gap_and_no_malformed_schema(self):
        with self.assertRaisesRegex(ValueError,"SCHEMA"):
            source_only_audit(b"TAG,TIME,X,Y\nbird,1567296000,650000,5900000\n")
        raw=synthetic_source(tides=1,birds=1,each=12)
        rows=list(csv.DictReader(io.StringIO(raw.decode())))
        for r in rows:r["TIME"]=str(float(r["TIME"])*10)
        fp=io.StringIO();w=csv.DictWriter(fp,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
        qa=source_only_audit(fp.getvalue().encode())
        self.assertEqual(qa["original_TAG_30s_location_bins"],0)
        self.assertEqual(qa["original_source_dropped_rows"]["timestamp_outside_source_years"],24)

    def test_no_headings_in_features_and_duplicate_source_cannot_raise_counts(self):
        raw=synthetic_source(tides=1,birds=1,each=12).decode()
        rows=list(csv.DictReader(io.StringIO(raw)))
        rows.append({**rows[0],"X":rows[0]["X"]})
        fp=io.StringIO();w=csv.DictWriter(fp,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
        qa=source_only_audit(fp.getvalue().encode())
        self.assertEqual(qa["original_raw_rows"],25)
        self.assertEqual(qa["duplicate_original_TAG_TIME_instances"],1)
        self.assertEqual(qa["original_TAG_30s_location_bins"],24)

if __name__=="__main__":unittest.main()
