"""Pre-outcome graph tests for S3 2019 original partner-assignment source."""
from __future__ import annotations

import copy
import unittest
import published_S3_graph as m


def four_cycle_source_fixture():
    components=[
        ("B01","B82","B07","B87"),
        ("B61","S25","S87","B84"),
        ("B65","S84","S13","S27"),
        ("B67","B80","S05","S12"),
        ("B75","S06","S30","S03"),
    ]
    pairs={}
    for a,b,c,d in components:
        pairs[a]={2:b,3:c}
        pairs[b]={2:a,3:d}
        pairs[c]={2:d,3:a}
        pairs[d]={2:c,3:b}
    rows=[
      {"row":1,"text_only_cells":{"A":"Individual information",
                                  "E":"Similar-sized pairs",
                                  "I":"Different-sized pairs"}},
      {"row":2,"text_only_cells":{"A":"Bird ID","E":"Partner ID","I":"Partner ID"}},
    ]
    for i,(bird,val) in enumerate(sorted(pairs.items()),start=3):
        rows.append({"row":i,"text_only_cells":{
             "A":bird,"E":val[2],"I":val[3]}})
    return {"worksheet_reports":[
       {"preview_first_35_rows_numeric_body_traits_masked":rows}
    ]}


class TestOriginalGraph(unittest.TestCase):
    def test_known_truth_five_four_cycles_with_no_eight_cluster_claim(self):
        g=m.parse_pairs(four_cycle_source_fixture())
        self.assertEqual(g["source_participants"],20)
        self.assertEqual(g["phase2_undirected_pairs"],10)
        self.assertEqual(g["phase3_undirected_pairs"],10)
        self.assertEqual(g["unique_experiment_wide_edges"],20)
        self.assertEqual(g["component_sizes"],[4]*5)
        self.assertTrue(g["each_component_is_a_four_cycle"])
        self.assertEqual(g["experiment_wide_social_components"],5)
        self.assertFalse(g["eligible_for_confirmatory_v17_wind_neighbor_forecast"])
        self.assertTrue(g["source_B01_known_pairs_validated"])
        self.assertEqual(g["flight_or_GPS_outcome_rows_read"],0)
        x=g["random_bird_split_diagnostic_EXPLORATORY_math_only"]
        self.assertEqual(x["possible_random_four_of_twenty_sets"],4845)
        self.assertEqual(x["sets_that_do_not_split_any_social_component"],5)
        self.assertEqual(x["leaky_random_four_bird_sets"],4840)
        self.assertAlmostEqual(x["random_four_bird_holdout_leak_probability"],4840/4845)
        self.assertEqual(x["all_network_safe_ten_bird_holdout_sets"],0)

    def test_nonreciprocal_assignment_fails_closed(self):
        x=four_cycle_source_fixture()
        rows=x["worksheet_reports"][0]["preview_first_35_rows_numeric_body_traits_masked"]
        next(r for r in rows if r["text_only_cells"].get("A")=="B82")["text_only_cells"]["E"]="S03"
        with self.assertRaisesRegex(ValueError,"Non-reciprocal"):
            m.parse_pairs(x)

    def test_original_phase_headers_are_required(self):
        x=four_cycle_source_fixture()
        x["worksheet_reports"][0]["preview_first_35_rows_numeric_body_traits_masked"][0]["text_only_cells"]["E"]="unknown"
        with self.assertRaisesRegex(ValueError,"headers changed"):
            m.parse_pairs(x)

    def test_one_phase_cannot_be_independently_split_for_8_cluster_claim(self):
        g=m.parse_pairs(four_cycle_source_fixture())
        # All 20 bird IDs are arranged into 10 disjoint pairs in each
        # phase alone. Combining both phases yields only 5 units.
        self.assertGreater(g["phase2_undirected_pairs"],
                           g["experiment_wide_social_components"])
        self.assertEqual(m.MIN_INDEPENDENT_COMPONENTS,8)


if __name__=="__main__":
    unittest.main()
