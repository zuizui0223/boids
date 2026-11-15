"""Known-truth claim ceiling and source-inventory invariants for v7."""
import json, unittest
from pathlib import Path
from comparative_state.usgs_roost_source_v7 import parse_inventory, valid_source

class NoveltyAuditTests(unittest.TestCase):
    def test_manifest_bounds(self):
        p=Path(__file__).with_name("novelty_evidence_manifest_v7.json")
        d=json.loads(p.read_text())
        self.assertEqual(d["comparative_paper_category"],"ecological synthesis / perspective, not pooled original meta-analysis")
        self.assertEqual(d["source_results"]["snow_goose_evaluable_candidate_tags"],69)
        self.assertEqual(d["source_results"]["snow_goose_positive_candidate_tags"],54)
        self.assertEqual(d["v6e_null"]["primary"],"FAIL")
        self.assertFalse(d["source_results"]["original_california_source_has_step_origin_class"])
        self.assertFalse(d["new_source_candidate"]["matched_accessibility_confirmed"])
    def test_no_independent_source_claim_from_one_study(self):
        d=json.loads(Path(__file__).with_name("novelty_evidence_manifest_v7.json").read_text())
        self.assertIn("independent four-taxon field replications",d["no_claims"])
        self.assertEqual(d["status"],"NOVELTY_AUDIT_COMPLETE_NEW_FIELD_EFFECT_NONE")
    def test_usgs_host_allowlist(self):
        self.assertTrue(valid_source("https://www.sciencebase.gov/catalog/item/601478d0d34edf5c66ea0ead?format=json"))
        self.assertFalse(valid_source("http://www.sciencebase.gov/catalog/item/123"))
        self.assertFalse(valid_source("https://example.com/catalog/item/123"))
    def test_file_inventory_does_not_certify_origin(self):
        out=parse_inventory({"title":"Waterfowl public source","files":[{"name":"roost.csv","size":42,"md5":"x"}]})
        self.assertEqual(out["file_count"],1)
        self.assertFalse(out["true_step_origin_schema_admitted"])
        self.assertFalse(out["matched_option_set_schema_admitted"])
        self.assertFalse(out["source_bird_independence_from_Overton_2023"])
    def test_invalid_source_manifest(self):
        with self.assertRaises(ValueError):parse_inventory({"files":"not-a-list"})

if __name__=="__main__":unittest.main()
