#!/usr/bin/env python3
"""v17-B: reproduce original published S3 bird-pair graph; no GPS/turn effects.

The original S3 2019 PLOS XLSX has fixed columns A (Bird ID),
E (similar-sized paired partner; Phase 2),
I (different-sized paired partner; Phase 3).
Graph is the UNION of experimental assigned pairs, not a data-derived GPS
contact graph. Bird-level or 458-file split would leak whole social units.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
from pathlib import Path

from published_S3_pair_source import acquire_supplement,parse_workbook
from tempfile import TemporaryDirectory

PINNED_S3_SHA256="f06a89cdb0bb4df338337c1d2f459d7eee545289ede06904bc76114653981e84"
EXPECTED_IDS=20
EXPECTED_PHASE_EDGES=10
MIN_INDEPENDENT_COMPONENTS=8


def parse_pairs(text_report:dict)->dict:
    reports=text_report["worksheet_reports"]
    if len(reports)!=1:
        raise ValueError("Expected one original S3 published worksheet")
    rows=reports[0]["preview_first_35_rows_numeric_body_traits_masked"]
    bynum={row["row"]:row["text_only_cells"] for row in rows}
    if (bynum.get(1,{}).get("E")!="Similar-sized pairs" or
        bynum.get(1,{}).get("I")!="Different-sized pairs" or
        bynum.get(2,{}).get("A")!="Bird ID" or
        bynum.get(2,{}).get("E")!="Partner ID" or
        bynum.get(2,{}).get("I")!="Partner ID"):
        raise ValueError("Original workbook source headers changed")
    pairs={}
    for no in range(3,23):
        row=bynum.get(no,{})
        a,b,c=(row.get(k) for k in ("A","E","I"))
        if not all(isinstance(x,str) for x in (a,b,c)):
            raise ValueError("Missing one published original pairing ID")
        if a in pairs:
            raise ValueError("Duplicated bird ID in source S3")
        if a in (b,c) or b==c:
            raise ValueError("Self-pair or unchanged partner across phases")
        pairs[a]={2:b,3:c}
    if len(pairs)!=EXPECTED_IDS:
        raise ValueError("Incomplete publication subject roster")
    vertices=set(pairs)
    for bird,phase in pairs.items():
        for phase_number,other in phase.items():
            if other not in vertices or pairs[other][phase_number]!=bird:
                raise ValueError("Non-reciprocal source partner assignment")
    phase_edges={}
    for phase_number in (2,3):
        items={tuple(sorted((bird,phase[phase_number])))
               for bird,phase in pairs.items()}
        if len(items)!=EXPECTED_PHASE_EDGES:
            raise ValueError("Source is not ten disjoint dyads per phase")
        phase_edges[phase_number]=sorted(items)
    if set(phase_edges[2])&set(phase_edges[3]):
        raise ValueError("Unexpected repeated dyad across changed treatments")

    adjacency={x:set() for x in vertices}
    for phase in phase_edges.values():
        for a,b in phase:
            adjacency[a].add(b);adjacency[b].add(a)
    comps=[]
    unseen=set(vertices)
    while unseen:
        initial=min(unseen)
        stack=[initial]
        component=set()
        while stack:
            n=stack.pop()
            if n in component:continue
            component.add(n);stack.extend(adjacency[n]-component)
        unseen-=component
        comps.append(sorted(component))
    comps.sort(key=lambda c:c[0])

    degrees=collections.Counter(len(v) for v in adjacency.values())
    if len(comps)!=5 or any(len(c)!=4 for c in comps) or degrees!={2:20}:
        # This check is an expected source provenance receipt, NOT the
        # eligibility criterion. A source update should stop, not be re-fit.
        raise ValueError("Published 2019 source pairing topology changed")
    # Each four-vertex component with degree two is exactly a 4-cycle.
    # A train/test split is graph-independent only if it assigns every
    # ENTIRE connected component to exactly one side. For a 4-bird test
    # set this gives 5 safe sets out of C(20,4)=4,845 possible selections.
    safe_four = sum(len(c)==4 for c in comps)
    all_four = math.comb(len(vertices),4)
    safe_half = sum(1 for a in range(1<<len(comps))
                    if sum(len(comps[k]) for k in range(len(comps))
                           if a&(1<<k))==len(vertices)//2)
    return {
        "status":"EXACT_S3_ORIGINAL_GRAPH_VERIFIED__CONFIRMATORY_GATE_FAILED",
        "source_participants":len(vertices),
        "phase2_undirected_pairs":len(phase_edges[2]),
        "phase3_undirected_pairs":len(phase_edges[3]),
        "unique_experiment_wide_edges":len(phase_edges[2])+len(phase_edges[3]),
        "source_reciprocity_validated":True,
        "degree_frequency":dict(sorted(degrees.items())),
        "experiment_wide_social_components":len(comps),
        "component_sizes":[len(c) for c in comps],
        "components_original_bird_IDs":comps,
        "each_component_is_a_four_cycle":True,
        "random_bird_split_diagnostic_EXPLORATORY_math_only":{
            "fixed_test_birds":4,
            "possible_random_four_of_twenty_sets":all_four,
            "sets_that_do_not_split_any_social_component":safe_four,
            "leaky_random_four_bird_sets":all_four-safe_four,
            "random_four_bird_holdout_leak_probability":1-safe_four/all_four,
            "all_network_safe_ten_bird_holdout_sets":safe_half,
            "interpretation":"A random individual-level split typically puts a known assigned social partner into the opposite training/test side; this says NOTHING about actual flight prediction outcomes."},
        "maximum_independent_bird_connected_source_units":len(comps),
        "pre_registered_minimum_confirmatory_units":MIN_INDEPENDENT_COMPONENTS,
        "eligible_for_confirmatory_v17_wind_neighbor_forecast":
             len(comps)>=MIN_INDEPENDENT_COMPONENTS,
        "reason":"Only five 4-bird components; eight required independently preregistered.",
        "source_B01_known_pairs_validated":
             pairs["B01"][2]=="B82" and pairs["B01"][3]=="B07",
        "flight_or_GPS_outcome_rows_read":0,
        "source_weather_time_zone_still_unverified":True,
    }


def run()->dict:
    with TemporaryDirectory() as temp:
        path=Path(temp)/"s3_original.xlsx"
        got=acquire_supplement(path)
        out={"study":"v17-b-independent-experiment-wide-assigned-partner-topology",
             "original_source":"PLOS Biology 2019 S3 Table doi:10.1371/journal.pbio.3000299.s008",
             "original_supplement_integrity":got,
             "status":"STOP_ORIGINAL_SOURCE_NOT_AVAILABLE",
             "no_GPS_heading_route_or_wind_outcomes_read":True}
        if got["status"]!="PUBLISHED_SUPPLEMENT_BYTES_VERIFIED":
            return out
        if got["sha256"]!=PINNED_S3_SHA256:
            out["status"]="STOP_SUPPLEMENT_SHA256_CHANGED"
            return out
        parsed=parse_workbook(path)
        graph=parse_pairs(parsed)
        out["status"]=graph["status"]
        out["graph"]=graph
        return out


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,
                   default=Path("validation_v17/results/original_s3_pair_graph_v17.json"))
    a=p.parse_args()
    report=run()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2,
                                 allow_nan=False)+"\n")
    print("ORIGINAL_S3_PAIR_GRAPH",json.dumps(report,sort_keys=True))
    print("NO_GPS_BEHAVIORAL_OUTCOMES_FITTED")


if __name__=="__main__":
    main()
