"""Source-available 2026 echo clustering HELPER count grain, invented calls only.

Uses source helper count-threshold and seed-one-hop grouping from available
MIT MATLAB; original eLife 2026 main clustering branch implementation MISSING.
This is not a source-published cluster model reproduction or bat observation.
"""
from __future__ import annotations
import json
from pathlib import Path
from mazar_2026_source_cluster_order_v1 import (
    source_one_hop_clusters,threshold_repeated_calls
)

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"MAZAR_2026_SOURCE_POINT_VS_CALL_SUPPORT_PREOUTPUT_V1.md"
OUT=ROOT/"MAZAR_2026_SOURCE_POINT_VS_CALL_SUPPORT_RESULT_V1.json"
NEAR=((.9,0.),(0.,0.),(1.8,0.))
FAR=tuple((float(x),0.) for x in range(10,100,10))
RATIO=.22
D=1.

def invented_calls(scattered):
    if scattered:
        calls=[(NEAR[0],FAR[0],FAR[1]),(NEAR[1],),(NEAR[2],)]
        calls += [(p,) for p in FAR[2:]]
    else:
        calls=[NEAR] + [(p,) for p in FAR]
    if len(calls)!=10 or sum(len(c) for c in calls)!=12:
        raise ValueError("SOURCE_SYNTHETIC_INPUT_NOT_LOCKED")
    return calls

def analyze(calls):
    n_relevant=sum(len(c)>0 for c in calls)
    if n_relevant!=10:raise ValueError("STOP_CALLS_NOT_ALL_RELEVANT")
    pts=[];ids=[]
    for callidx,echoes in enumerate(calls):
        for echo in echoes:
            pts.append(echo);ids.append(callidx)
    groups=source_one_hop_clusters(pts,D)
    th=threshold_repeated_calls(n_relevant,RATIO)
    support=[]
    for group in groups:
        if len(group)<th:continue
        n_calls=len({ids[j] for j in group})
        support.append({
          "source_helper_echo_point_count":len(group),
          "distinct_source_calls_contributing":n_calls,
          "source_point_count_accepts":len(group)>=th,
          "not_source_call_recurrence_accepts":n_calls>=th,
          "centroid_xy":[sum(pts[j][k] for j in group)/len(group) for k in (0,1)]
        })
    return {"n_relevant_source_calls":n_relevant,
      "n_2d_echo_points":len(pts),
      "source_ratio":RATIO,
      "threshold_min_real_valued_count":th,
      "source_seed_clustering_groups":len(groups),
      "source_accepted_echo_point_clusters":support,
      "source_accepted_cluster_count":len(support),
      "not_source_distinct_call_accepted_count":sum(s["not_source_call_recurrence_accepts"] for s in support)}

def run():
    if not CONTRACT.exists():raise ValueError("STOP_PREOUTPUT_PROTOCOL_MISSING")
    a=invented_calls(False);b=invented_calls(True)
    pa=sorted((xy for call in a for xy in call))
    pb=sorted((xy for call in b for xy in call))
    if pa!=pb:raise ValueError("STOP_PHYSICAL_POINT_CLOUD_DIFFERENT")
    c1=analyze(a);c2=analyze(b)
    return {"schema":1,
      "status":"ORIGINAL_SOURCE_HELPER_ECHO_POINTS_VS_CALL_RECURRENCE_FROZEN_SYNTHETIC",
      "source_author_commit":"a74fb61a8efb57ca37693893c3bd7b35fa94fa89",
      "source_findRepeatedClusters_blob":"890bbbfdc0628c2c7d0c8e392c0cd99c55de8e72",
      "source_distanceTHClustering_blob":"65a6a2079319220d324587ca0260b06e4a4f35dd",
      "original_main_cluster_function_missing_in_both_archives":True,
      "not_a_full_source_MATLAB_simulation":True,
      "new_animal_measurements":False,
      "source_CaveExit_Confusion_experiment_ObsRepeationsFlag_is_zero":True,
      "exact_same_static_2D_point_cloud":True,
      "same_ten_nonempty_emitted_calls":True,
      "source_repeated_echo_threshold_equals_2p2_points":True,
      "single_call_triple_echoes":c1,
      "three_distinct_calls_one_echo_each":c2,
      "limitations":[
        "Helper checks source number of detections per spatial group, not independent echo-bearing calls per spatial group.",
        "Different counts of calls could be intentional: multiple reflections from a single call may be biologically informative.",
        "Does not prove original published missing full confusion algorithm has this same behavior.",
        "Synthesized positions and call groupings are not empirical bat acoustic or movement observations.",
        "Neither clustering nor call-repetition comparator is a causal animal foraging or colony-exit simulation."
      ]}
if __name__=="__main__":
    result=run()
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("SOURCE_POINTS_VS_CALLS",result["status"])
    for key in ("single_call_triple_echoes","three_distinct_calls_one_echo_each"):
        print("GROUPING",key,json.dumps(result[key],sort_keys=True))
