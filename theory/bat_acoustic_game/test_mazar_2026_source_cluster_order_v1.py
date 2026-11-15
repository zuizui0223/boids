"""Available source clustering helper invariants on invented 2-D echoes only."""
import unittest
from mazar_2026_source_cluster_order_v1 import (
 THRESHOLD_D,RATIO,BASE_GROUP,ISOLATES,
 source_one_hop_clusters,graph_components,threshold_repeated_calls,accepted,compare
)
class TestOriginalSourceHelperMicrokernel(unittest.TestCase):
 def test_pinned_threshold_is_source_ratio_times_relevant_calls(self):
  self.assertAlmostEqual(threshold_repeated_calls(10,.22),2.2)
  self.assertEqual(threshold_repeated_calls(10,3),3)
 def test_first_endpoint_does_not_recurse_to_neighbors_neighbors(self):
  points=[(0,0),(.9,0),(1.8,0)]
  clusters=source_one_hop_clusters(points,1)
  self.assertEqual([len(g) for g in clusters],[2,1])
 def test_first_middle_point_absorbs_both_endpoints(self):
  points=[(.9,0),(0,0),(1.8,0)]
  clusters=source_one_hop_clusters(points,1)
  self.assertEqual([len(g) for g in clusters],[3])
 def test_connected_components_is_distinct_comparator(self):
  points=[(0,0),(.9,0),(1.8,0)]
  self.assertEqual([len(g) for g in graph_components(points)],[3])
  self.assertEqual([len(g) for g in source_one_hop_clusters(points)],[2,1])
 def test_source_ratio_min_size_3_after_10_echoes(self):
  points=list(BASE_GROUP)+list(ISOLATES)
  self.assertEqual(len(accepted(source_one_hop_clusters(points),points)),0)
  a=[BASE_GROUP[1],BASE_GROUP[0],BASE_GROUP[2],*ISOLATES]
  self.assertEqual(len(accepted(source_one_hop_clusters(a),a)),1)
 def test_non_source_graph_comparator_accepts_all_relative_orders(self):
  z=compare()
  self.assertEqual(len(z["permutations"]),6)
  self.assertEqual(z["number_of_alternative_graph_orderings_accepting_chain_cluster"],6)
 def test_available_source_helper_is_order_dependent(self):
  z=compare()
  self.assertEqual(z["number_of_source_helper_orderings_accepting_chain_cluster"],2)
  self.assertEqual([x["source_accepted_cluster_count"] for x in z["permutations"]].count(0),4)
 def test_directed_seed_preserves_all_points(self):
  points=list(BASE_GROUP)+list(ISOLATES)
  groups=source_one_hop_clusters(points)
  self.assertEqual(sorted(j for g in groups for j in g),list(range(10)))
 def test_bad_source_parameters_fail(self):
  for p in (-1,0):
   with self.assertRaises(ValueError):source_one_hop_clusters([(0,0)],p)
  with self.assertRaises(ValueError):threshold_repeated_calls(0)
 def test_reproduction_safety_and_unavailable_original_function(self):
  out=compare()
  self.assertFalse(out["is_original_MATLAB_simulator_reproduction"])
  self.assertFalse(out["new_bat_measurements"])
  self.assertTrue(out["original_GitHub_and_Zenodo_main_clustering_impl_missing"])
  self.assertTrue(out["source_author_confusion_experiment_ObsRepeationsFlag_is_zero"])
if __name__=="__main__":unittest.main()
