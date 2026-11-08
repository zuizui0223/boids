"""Source-provenance receipt and two available-helper numerical replay checks.

This intentionally cannot verify the UNAVAILABLE author full-cluster function
or run the original 2026 Matlab simulations. It validates immutable code,
contracts and synthetic result values only.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json
import mazar_2026_source_cluster_order_v1 as orders
import mazar_2026_source_point_vs_call_v1 as calls

ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"MAZAR_2026_CLUSTERING_SOURCE_AUTHORITY_LEDGER_2026_11_08.json"

def gitblob(filename):
    b=(ROOT/filename).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def main():
    v=json.loads(LEDGER.read_text())
    assert v["schema"]==1
    assert v["source_cluster_impl_in_author_GitHub"] is False
    assert v["source_cluster_impl_in_original_Zenodo"] is False
    assert v["original_MATLAB_full_source_simulator_rerun"] is False
    assert v["original_eLife_published_Figure4_cluster_results_reproduced"] is False
    assert v["newly_measured_animals"]==0
    assert v["source_withConfusion_workbook_ObsClusterFlag"]=="1"
    assert v["source_experiment_override_ObsMemorySize"]=="10"
    assert v["source_experiment_override_ObsRepeationsFlag"]=="0"
    for file,sourcehash in v["research_code_sha"].items():
        assert gitblob(file)==sourcehash,("SOURCE_PROTOCOL_OR_CODE_CHANGED",file)
    a=orders.compare()
    b=calls.run()
    first=v["numerical_microbenchmarks"]["seed_order_same_ten_synthetic_echoes"]
    assert a["number_of_source_helper_orderings_accepting_chain_cluster"]==first["source_accepted_orderings_of_six"]==2
    assert a["number_of_alternative_graph_orderings_accepting_chain_cluster"]==first["non_source_transitive_connectivity_accepts_of_six"]==6
    assert len(a["permutations"])==6 and first["other_source_orderings_rejected_of_six"]==4
    second=v["numerical_microbenchmarks"]["input_echo_points_vs_independent_calls"]
    c=b["single_call_triple_echoes"]
    d=b["three_distinct_calls_one_echo_each"]
    assert c["n_relevant_source_calls"]==d["n_relevant_source_calls"]==10
    assert c["source_accepted_cluster_count"]==d["source_accepted_cluster_count"]==1
    assert c["source_accepted_echo_point_clusters"][0]["distinct_source_calls_contributing"]==second["inputA_distinct_calls_supporting_cluster"]==1
    assert d["source_accepted_echo_point_clusters"][0]["distinct_source_calls_contributing"]==second["inputB_distinct_calls_supporting_cluster"]==3
    assert c["not_source_distinct_call_accepted_count"]==0
    assert d["not_source_distinct_call_accepted_count"]==1
    assert not a["new_bat_measurements"] and not b["new_animal_measurements"]
    print("AUTHOR_ARCHIVE_SOURCE_GAP_PRIOR_2026_11_08_CONFIRMED")
    print("AVAILABLE_CLUSTER_HELPER_SIX_ORDERS_AND_TWO_CALL_GRAINS_REPLAYED")
    print("ALL_SOURCE_CODE_AND_FROZEN_CONTRACT_BLOBS_MATCH")
    print("NO_ORIGINAL_MATLAB_MODEL_REPRODUCTION_NO_BAT_MEASUREMENTS")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
