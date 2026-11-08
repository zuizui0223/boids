"""Invented original-index-mapped 3D virtual-echolocation metrics only."""
import unittest
from steckel_2026_original_28_run_comparison_v1 import (
 compose,METRICS,ORIGINAL_MAIN,GROUP_REFERENCE,CONTROL_COMPARISONS
)

def fake_source():
    allnames=sorted(set().union(*(set(v) for v in CONTROL_COMPARISONS.values())))
    allnames += ["other-"+str(x) for x in range(28-len(allnames))]
    assert len(allnames)==28 and len(set(allnames))==28
    index=[{"source_run_name":name,"source_experiment":"E1",
            "source_description":"fabricated original source label"} for name in allnames]
    rows=[{"matched_source_name":name,
           "original_source_scalar_metrics":{
               "az":float(i+1),"el":float(i+2),"gc":float(i+3),
               "n":3990,"step":59984,
               "leftright_correct":0.9,"updown_correct":0.8,
               "corr":0.5 if i%2 else None
           }} for i,name in enumerate(allnames)]
    planned={k:{"planned_run_names":v} for k,v in CONTROL_COMPARISONS.items()}
    return {"original_source_all_metric_rows":rows,
            "original_source_28_declared_runs":index,
            "comparison_support":planned}

class TestAuthor3DOriginalRunComparison(unittest.TestCase):
    def test_all_28_source_simulations_complete(self):
        out=compose(fake_source())
        self.assertEqual(len(out["all_runs"]),28)
        self.assertEqual(len(out["comparisons"]),len(CONTROL_COMPARISONS))
        self.assertEqual(set(out["all_runs"]),set(x["source_run_name"] for x in fake_source()["original_source_28_declared_runs"]))
    def test_every_original_metric_retained_without_sign_selection(self):
        o=compose(fake_source())
        self.assertEqual(set(o["all_runs"][ORIGINAL_MAIN]["author_original_scalar_metrics"]),set(METRICS))
    def test_same_stage_and_sample_count_does_not_prove_same_evaluation_examples(self):
        o=compose(fake_source())
        for c in o["comparisons"].values():
            for row in c["original_runs"]:
                self.assertFalse(row["evaluation_same_drawn_examples_verified"])
    def test_original_memory_levels_not_optimised_post_output(self):
        o=compose(fake_source())
        self.assertEqual(len(o["comparisons"]["memory_call_counts"]["original_runs"]),6)
    def test_nonfavourable_metric_difference_is_not_deleted(self):
        o=compose(fake_source())
        d=o["comparisons"]["head_motion_axes"]["original_runs"]
        delta=[x["difference_from_original_source_reference"]["el"] for x in d]
        self.assertTrue(any(x<0 for x in delta))
        self.assertTrue(any(x==0 for x in delta))
    def test_duplicate_original_source_names_fail(self):
        o=fake_source()
        o["original_source_all_metric_rows"][0]["matched_source_name"]=o["original_source_all_metric_rows"][1]["matched_source_name"]
        with self.assertRaisesRegex(ValueError,"UNIQUELY_MATCHED"):
            compose(o)
    def test_missing_original_metric_fails_not_filled(self):
        o=fake_source()
        del o["original_source_all_metric_rows"][0]["original_source_scalar_metrics"]["el"]
        with self.assertRaisesRegex(ValueError,"MISSING_REQUIRED"):
            compose(o)
    def test_supplementary_source_28_not_27(self):
        o=fake_source()
        o["original_source_28_declared_runs"].pop()
        with self.assertRaisesRegex(ValueError,"28_RUN_COUNT"):
            compose(o)
if __name__=="__main__":
    unittest.main()
