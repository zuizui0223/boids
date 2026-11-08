"""Order sensitivity of an AVAILABLE original 2026 cave-exit clustering helper.

Independent small port of source distanceTHClustering.m's SEED-ONLY one-hop
cluster logic, plus findRepeatedClusters.m's point-count threshold rule.
The function required by the published 'confusion with mitigation' branch
is absent from both original GitHub and Zenodo: this is NOT a replay of that
original complete group-flight model or an actual bat echo measurement.
"""
from __future__ import annotations
import itertools,json,math
from pathlib import Path
from collections import deque

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"MAZAR_2026_SOURCE_CLUSTER_ORDER_PREOUTPUT_2026_11_08.md"
OUT=ROOT/"MAZAR_2026_SOURCE_CLUSTER_ORDER_RESULT_V1.json"
AUTHOR_SOURCE="a74fb61a8efb57ca37693893c3bd7b35fa94fa89"
SOURCE_DISTANCE_BLOB="65a6a2079319220d324587ca0260b06e4a4f35dd"
SOURCE_REPEAT_BLOB="890bbbfdc0628c2c7d0c8e392c0cd99c55de8e72"
THRESHOLD_D=1.0
RATIO=.22
BASE_GROUP=((0.,0.),(.9,0.),(1.8,0.))
ISOLATES=tuple((float(k),0.) for k in range(10,71,10))
N_RELEVANT_CALLS=10

def dist(p,q):
    return math.hypot(p[0]-q[0],p[1]-q[1])

def source_one_hop_clusters(points,threshold=THRESHOLD_D):
    """Faithful grouping decisions from available author distanceTHClustering.m.

    For each first unused seed, add direct-neighbors only. Explicitly NO
    recursive linkage of a neighbor's other neighbors.
    """
    if threshold<=0:raise ValueError("threshold must be positive")
    pts=list(points)
    if any(len(p)!=2 or not all(math.isfinite(x) for x in p) for p in pts):
        raise ValueError("2D finite points required")
    used=[False]*len(pts)
    groups=[]
    while any(not f for f in used):
        idx=next(i for i,u in enumerate(used) if not u)
        seed=pts[idx]
        cluster=[idx]
        used[idx]=True
        for other in range(len(pts)):
            if not used[other] and dist(pts[other],seed)<=threshold:
                cluster.append(other)
                used[other]=True
        groups.append(cluster)
    return groups

def graph_components(points,threshold=THRESHOLD_D):
    """ALTERNATIVE comparator: transitive 1-hop connectivity, NOT original code."""
    if threshold<=0:raise ValueError("threshold must be positive")
    pts=list(points)
    open_set=set(range(len(pts)))
    groups=[]
    while open_set:
        start=min(open_set);open_set.remove(start)
        q=deque([start]);group=[start]
        while q:
            i=q.popleft()
            for j in sorted(tuple(open_set)):
                if dist(pts[i],pts[j])<=threshold:
                    open_set.remove(j);q.append(j);group.append(j)
        groups.append(group)
    return groups

def threshold_repeated_calls(n_relevant,ratio=RATIO):
    if n_relevant<1 or ratio<=0:raise ValueError("positive calls and threshold")
    return float(ratio if ratio>=1 else n_relevant*ratio)

def accepted(groups,points,n_relevant=N_RELEVANT_CALLS,ratio=RATIO):
    threshold=threshold_repeated_calls(n_relevant,ratio)
    records=[]
    for group in groups:
        if len(group)>=threshold:
            records.append({
             "cluster_size":len(group),
             "centroid_xy":[sum(points[j][k] for j in group)/len(group) for k in (0,1)]
            })
    return records

def compare():
    if not CONTRACT.exists():raise ValueError("FROZEN_SOURCE_ORDER_PROTOCOL_MISSING")
    all_scenarios=[]
    for triple in itertools.permutations(BASE_GROUP):
        points=list(triple)+list(ISOLATES)
        source=source_one_hop_clusters(points)
        alternative=graph_components(points)
        a=accepted(source,points);b=accepted(alternative,points)
        all_scenarios.append({
            "source_order_original_first_three_x":[round(x,3) for x,y in triple],
            "source_available_helper_cluster_sizes":[len(c) for c in source],
            "source_available_helper_accepted_clusters":a,
            "source_accepted_cluster_count":len(a),
            "not_source_connected_components_cluster_sizes":[len(c) for c in alternative],
            "not_source_connected_components_accepted_clusters":b,
            "not_source_connected_components_accepted_cluster_count":len(b)
        })
    results={
      "schema":1,
      "status":"SOURCE_AVAILABLE_HELPER_MICROKERNEL_ORDER_DEPENDENCE_NOT_PUBLISHED_FIGURE_REPLAY",
      "source_author_mit_commit":AUTHOR_SOURCE,
      "source_distance_clustering_git_blob":SOURCE_DISTANCE_BLOB,
      "source_find_repeated_git_blob":SOURCE_REPEAT_BLOB,
      "unavailable_main_full_confusion_impl":"BatManueverDecision_FullConfusion_ver08Aug24.m",
      "original_GitHub_and_Zenodo_main_clustering_impl_missing":True,
      "is_original_MATLAB_simulator_reproduction":False,
      "new_bat_measurements":False,
      "source_author_confusion_experiment_ObsRepeationsFlag_is_zero":True,
      "source_author_confusion_workbook_ObsClusterFlag_is_one":True,
      "synthetic_input":{"original_call_count":N_RELEVANT_CALLS,
         "all_calls_have_one_echo":True,
         "source_echo_ratio":RATIO,
         "computed_accepted_min_cluster_size":threshold_repeated_calls(N_RELEVANT_CALLS,RATIO),
         "source_geometry_scale_assumed_not_species_calibrated":True,
         "threshold":THRESHOLD_D,
         "fixed_geometry_points":list(BASE_GROUP+ISOLATES),
         "relative_orderings":6
      },
      "permutations":all_scenarios,
      "number_of_source_helper_orderings_accepting_chain_cluster":
          sum(x["source_accepted_cluster_count"]>0 for x in all_scenarios),
      "number_of_alternative_graph_orderings_accepting_chain_cluster":
          sum(x["not_source_connected_components_accepted_cluster_count"]>0 for x in all_scenarios),
      "claim_limits":[
         "The original published main confusion+clustering code path calls an absent file; this alternate helper cannot be presumed the published algorithm.",
         "The helper input order is the temporal order of detections; this diagnostic permutes it while preserving an invented static spatial cloud.",
         "One-hop greedy clustering is an available source implementation, not demonstrated bat neurobiology.",
         "No collisions, cave exits, ecologically relevant false alarms, source observations, statistics on bats, or functional foraging gain generated.",
         "Original prior paper already showed effect of echo confusion and multi-call clustering; not re-discovered here."
      ]
    }
    return results

if __name__=="__main__":
    output=compare()
    OUT.write_text(json.dumps(output,indent=2,sort_keys=True)+"\n")
    print("SOURCE_HELPER_ORDER_DEPENDENCE",output["status"])
    print("SOURCE_AVAILABLE_HELPER_ACCEPT",output["number_of_source_helper_orderings_accepting_chain_cluster"],
          "OF",output["synthetic_input"]["relative_orderings"])
    print("SEPARATE_TRANSITIVE_COMPARATOR_ACCEPT",output["number_of_alternative_graph_orderings_accepting_chain_cluster"],
          "OF",output["synthetic_input"]["relative_orderings"])
    for scenario in output["permutations"]:
        print("SYNTHETIC_ORDER",scenario["source_order_original_first_three_x"],
              "SOURCE_ACCEPTED",scenario["source_accepted_cluster_count"],
              "ALT_ACCEPTED",scenario["not_source_connected_components_accepted_cluster_count"])
