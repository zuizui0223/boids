#!/usr/bin/env python3
"""v19 post-source-availability exploratory original-pair GPS memory prediction.

v18 all-14 original SOURCE STOP is immutable. This distinct source-blind
follow-on admits exactly 13 original pairs with CM data, solely by filename
existence verified before any GPS target was opened. O19 TR contributes to M0
population template, but O19 has no CM score. The original v18 route shells,
site coordinates and training-only benchmark are reused UNMODIFIED.
"""
from __future__ import annotations
import argparse
import collections
import json
import tempfile
import zipfile
from pathlib import Path

import fourteen_pair_source_gate as source
import slow_pair_memory as prior

EXCLUDED_SOURCE_NO_CM_PAIR="O19"
EXPECTED_EVALUATED_PAIRS=13
EXPECTED_original_pairs=14
ORIGINAL_FULL_PAIR_STOP="NOT_ADMITTED_ORIGINAL_FILENAME_STAGE_SITE_GATE"
RESULT_STATUS="EXPLORATORY_POST_SOURCE_AVAILABILITY_13_PAIR_MEMORY"
NAME="v19-independent-13pair-observational-navigation-history"

def source_manifest(archive:Path,metadata_file:Path)->tuple[list[dict],dict,dict]:
    original=source.independent_pair_assignments(metadata_file)
    if original["original_published_pair_ID_count"]!=EXPECTED_original_pairs:
        raise ValueError("Original pair ledger no longer has fourteen units")
    with metadata_file.open("r",encoding="utf-8-sig") as raw:
        import csv
        rows=list(csv.DictReader(raw))
    member_pair={}
    bird_by_pair=collections.defaultdict(set)
    for row in rows:
        for bird in (row["Bird"],row["Partner"]):
            if bird in member_pair:raise ValueError("Duplicate original bird membership")
            member_pair[bird]=row["Pair_ID"]
            bird_by_pair[row["Pair_ID"]].add(bird)
    expected=sorted(set(member_pair.values())-{EXCLUDED_SOURCE_NO_CM_PAIR})
    if len(expected)!=EXPECTED_EVALUATED_PAIRS:
        raise ValueError("Exactly O19 must be solely out of CM evaluation")
    with zipfile.ZipFile(archive,"r") as zipf:
        names=sorted(n for n in zipf.namelist()
                     if n.lower().endswith(".csv") and
                     not Path(n).name.startswith("._"))
        if len(names)!=prior.ORIGINAL_GPS_FILES:
            raise ValueError("Original ZIP changed from source-frozen 426 track CSVs")
        records=[];counts=collections.defaultdict(collections.Counter)
        for name in names:
            idn=prior.file_identity(name)
            if idn is None:
                raise ValueError("Unrecognized author-native Checked/pair* original file")
            bird,site,mode,stage,date=idn
            if bird not in member_pair:
                raise ValueError("GPS bird not linked to original pair roster")
            pair=member_pair[bird]
            counts[pair][(site,stage)]+=1
            records.append({"name":name,"pair":pair,"bird":bird,
                            "site":site,"mode":mode,"stage":stage})
    missing=[]
    for site in ("LH","SH"):
        if counts[EXCLUDED_SOURCE_NO_CM_PAIR][(site,"CM")]!=0:
            missing.append(f"O19_{site}_unexpected_CM_present")
        if counts[EXCLUDED_SOURCE_NO_CM_PAIR][(site,"TR")]==0:
            missing.append(f"O19_{site}_expected_historical_TR_missing")
    for pair in expected:
        if len(bird_by_pair[pair])!=2:
            missing.append(f"{pair}_partner_membership_malformed")
        for site in ("LH","SH"):
            if counts[pair][(site,"TR")]==0:
                missing.append(f"{pair}_{site}_missing_training")
            if counts[pair][(site,"CM")]==0:
                missing.append(f"{pair}_{site}_missing_memory_test")
        if sum(counts[pair][(site,"CM")] for site in ("LH","SH"))<2:
            missing.append(f"{pair}_fewer_than_two_CM_files")
    qc={"source_file_count":len(records),
        "original_source_pair_components":14,
        "eligible_pair_ID_count":len(expected),
        "excluded_pair_without_any_CM":EXCLUDED_SOURCE_NO_CM_PAIR,
        "excluded_pair_cm_filename_count":sum(counts[EXCLUDED_SOURCE_NO_CM_PAIR][(site,"CM")]
                                             for site in ("LH","SH")),
        "source_files_at_each_pair_site_stage":{pair:{
            site:{"TR":counts[pair][(site,"TR")],
                  "CM":counts[pair][(site,"CM")]} for site in ("LH","SH")}
            for pair in sorted(counts)},
        "pre_GPS_observation_source_filename_gate_errors":missing,
        "raw_GPS_positions_read_before_stage_gate":False}
    return records,qc,{"eligible":expected,"member_pair":member_pair}

def read_source_crossings(archive:Path,records:list[dict])->tuple[dict,dict]:
    alltracks={}
    quality=collections.defaultdict(collections.Counter)
    with zipfile.ZipFile(archive) as arc:
        for e in records:
            position,info=prior.read_first_crossing(arc,e["name"],e["site"])
            key=(e["pair"],e["bird"],e["site"],e["mode"],e["stage"],e["name"])
            alltracks[key]=position
            q=quality[e["pair"]]
            q["original_GPS_files"]+=1
            q["source_GPS_rows_scanned"]+=info["valid_original_rows_scanned_until_final_first_crossing"]
            q["invalid_rows"]+=info["invalid_original_rows_scanned"]
            q["GPS_temporal_or_spatial_gaps"]+=info["clock_or_distance_discontinuities"]
            q["observed_radial_crossings"]+=info["shells_observed"]
    return alltracks,{x:dict(v) for x,v in quality.items()}

def experiment(out:Path)->dict:
    with tempfile.TemporaryDirectory() as temp:
        metadata=Path(temp)/"CM info.csv"
        archive=Path(temp)/"CM_trimmed.zip"
        sm=source.download_pinned(source.PAIR_PATH,source.PAIR_BYTES,
                                  source.PAIR_BLOB_SHA1,100000,metadata)
        sg=source.download_pinned(source.ZIP_PATH,source.ZIP_BYTES,
                                  source.ZIP_BLOB_SHA1,source.ZIP_CAP,archive)
        if sm["sha256"]!=prior.ORIGINAL_META_SHA256 or sg["sha256"]!=prior.ORIGINAL_ZIP_SHA256:
            raise ValueError("Previously v17D source-pinned raw bytes changed")
        entries,qc,groups=source_manifest(archive,metadata)
        source_profile={}
        if qc["pre_GPS_observation_source_filename_gate_errors"]:
            calculated={"status":"NOT_ADMITTED_V19_SOURCE_FILE_STRUCTURE",
                        "failures":qc["pre_GPS_observation_source_filename_gate_errors"],
                        "any_prediction_scores_computed":False}
        else:
            tracks,source_profile=read_source_crossings(archive,entries)
            # Reuse original v18 code unchanged, including O19's historical
            # training routes in the global population model.
            legacy=prior.score(tracks,groups["eligible"])
            if legacy["status"]!="EXPLORATORY_14_PAIR_FUTURE_CM_ROUTE_MEMORY_FORECAST":
                calculated={
                    "status":"NOT_ADMITTED_V19_FROZEN_CM_CROSSING_SUPPORT",
                    "predeclared_13_pair_support":legacy,
                    "any_prediction_scores_computed":False}
            else:
                if len(legacy["per_pair"])!=EXPECTED_EVALUATED_PAIRS:
                    raise ValueError("Unexpected fewer/more than thirteen scored pairs")
                calculated={
                    **legacy,"status":RESULT_STATUS,
                    "preregistered_previous_14_pair_status":ORIGINAL_FULL_PAIR_STOP,
                    "excluded_original_pair_has_no_CM_and_no_test_gain":True,
                    "source_population_TR_has_O19":True,
                    "independence_unit":"13 original non-overlapping author pair components, not birds/files/fixes",
                    "interpretive_scope":"post-source-availability-conditioned exploratory slow route bearing prediction only"}
    receipt={
        "study":NAME,
        "result_status":calculated["status"],
        "source_provenance":{
            "author_git_commit":source.REV,"metadata_SHA256":sm["sha256"],
            "gps_original_ZIP_SHA256":sg["sha256"],
            "original_source_pair_count":14,
            "source_derived_GPS_license":"not independently verified; no redistribution"},
        "source_only_stage_gate":qc,
        "source_GPS_observability_aggregate":source_profile,
        "registered_protocol":"docs/V19_EXPLORATORY_COMPLETECASE_13PAIR_MEMORY_CONTRACT.md",
        "original_v18_full_cohort_confirmatory_status":ORIGINAL_FULL_PAIR_STOP,
        "evaluation_pair_count":EXPECTED_EVALUATED_PAIRS,
        "original_route_shells_m":list(prior.SHELLS),
        "training_stage":"TR",
        "future_target_stage":"CM",
        "result":calculated,
        "raw_source_GPS_coordinates_or_event_level_targets_exported":False,
        "prior_v6_v8_v15_v16_v17_B_and_v18_endpoints_unchanged":True
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2,
                              allow_nan=False)+"\n",encoding="utf-8")
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path(
      "validation_v19/results/thirteen_pair_route_memory_v19.json"))
    a=p.parse_args()
    r=experiment(a.out)
    print("V19_SOURCE",json.dumps(r["source_provenance"],sort_keys=True))
    print("V19_PREOUTCOME_STAGE_GATE",json.dumps(r["source_only_stage_gate"],sort_keys=True))
    print("V19_OBSERVED_DATA_QUALITY",json.dumps(r["source_GPS_observability_aggregate"],sort_keys=True))
    print("V19_STATUS",r["result_status"])
    if r["result_status"]==RESULT_STATUS:
        print("V19_PRIMARY",json.dumps(r["result"]["primary_pair_history"],sort_keys=True))
        print("V19_SECONDARY",json.dumps(r["result"]["secondary_individual_history"],sort_keys=True))
        print("V19_EVERY_PAIR",json.dumps(r["result"]["per_pair"],sort_keys=True))
        print("V19_FULL_TARGET_COUNT",r["result"]["total_matched_CM_shell_targets"])
    else:
        print("V19_STRUCTURAL_STOP",json.dumps(r["result"],sort_keys=True))
    print("V19_AGGREGATE_JSON",a.out)

if __name__=="__main__":
    main()
