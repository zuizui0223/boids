"""Invented 3D learning result table fixtures, zero author outcome values."""
import json,unittest
from steckel_2026_original_run_metrics_v1 import (
 source_rows,numerics,labels,analyze_index,source_report,EXPERIMENTS,CONTROL_COMPARISONS
)
def index28():
    return [{"experiment":"E1","name":"run_"+str(i),
             "run":"runs/run_"+str(i),"description":"invented trial"}
            for i in range(28)]
class TestOriginalAuthorRunTableGate(unittest.TestCase):
 def test_source_28_index_accepts_only_unique_supported_experiment_ids(self):
    x=analyze_index(index28())
    self.assertEqual(len(x),28)
    self.assertTrue(all(y["source_experiment"]=="E1" for y in x))
 def test_duplicate_run_name_fails(self):
    x=index28();x[0]["name"]=x[1]["name"]
    with self.assertRaisesRegex(ValueError,"DUPLICATE"):
        analyze_index(x)
 def test_unknown_experiment_id_fails(self):
    x=index28();x[0]["experiment"]="E99"
    with self.assertRaisesRegex(ValueError,"SOURCE_EXP_ID"):
        analyze_index(x)
 def test_numeric_metrics_preserve_negative_and_zero(self):
    a=numerics({"az_deg":-2,"el_deg":0,"nested":{"error":3.2},"boolean":True})
    self.assertEqual(a,{"az_deg":-2,"el_deg":0,"nested.error":3.2})
 def test_list_dictionary_row_grain_only(self):
    rows,grain=source_rows([{"name":"test","error":3.2}])
    self.assertEqual(grain,"list")
    self.assertEqual(len(rows),1)
    with self.assertRaises(ValueError):source_rows([5])
 def test_join_exact_run_names_to_original_index(self):
    x=source_report(json.dumps([{"name":"run_0","mae_deg":3.2,"error_q50":0.8}]).encode(),json.dumps(index28()).encode())
    self.assertEqual(x["original_source_matched_unique_runs"],1)
    self.assertEqual(x["original_source_numeric_metric_fields"],["error_q50","mae_deg"])
    self.assertIn("run_1",x["source_original_run_names_missing_from_metrics"])
 def test_main_bat_control_sets_are_prespecified(self):
    self.assertIn("main_source_vs_head_fixed",CONTROL_COMPARISONS)
    self.assertIn("memory_call_counts",CONTROL_COMPARISONS)
    self.assertIn("E9",EXPERIMENTS)
    self.assertIn("C5",EXPERIMENTS)
 def test_source_extra_metrics_are_reported_not_cherry_picked(self):
    fake=[{"run":"runs/run_0","median_error":12,"mean_error":22,"negative_log_likelihood":-5}]
    x=source_report(json.dumps(fake).encode(),json.dumps(index28()).encode())
    self.assertEqual(len(x["original_source_all_metric_rows"][0]["original_source_scalar_metrics"]),3)
if __name__=="__main__":unittest.main()
