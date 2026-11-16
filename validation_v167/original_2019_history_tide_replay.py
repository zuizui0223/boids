"""v167: 2019 independent OBSERVATION YEAR of Vlieland tagged oystercatchers,
same bird-own-previous native 15-min source and correctly timed RWS tide
out-of-whole-week vs three wrong tide phase alignments.

This SOURCE pipeline reuses frozen genuine v127 2019 original Zenodo GPS/ACC
MD5-checked source and 2019 measured RWS June-Sep, with publisher original
RWS response SHA exact match to the prior successful v127 source archive.

After source, transport the SAME v166 source native 15-min bin correction,
original v165>=25k source threshold and identical v130 fixed models/scoring.

2019 is a distinct original calendar year, BUT already analyzed in v127 and
it overlaps 2018 original GPS bird IDs; therefore this is a HISTORICAL
same-site year reproduction, not new independent cohort or prospective 2019
forecast from frozen 2018 coefficients. The models retrain on 2019 remaining
week-folds, and actual test-week previous ACC history is provided to the
conditional online nowcast. Not a causal tidal clock or Reynolds Boids force.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

from original_2019_Vlieland_behaviour_source import (
    original_publisher_manifest,original_native_file,
    _reference_anonymous_identity,SourceStop)
from real_2019_Vlieland_foraging_GPS_source import (
    authenticate_original_gps_2019,original_2019_gps_source_index,
    true_original_2019_behaviour_gps_join,GPS_FILE,BEHAVIOUR_FILE)
from real_2019_vlieland_RWS_fourmonths import (
    fetch_all_2019_Vlieland_real_RWS_months,NativeTideSourceStop)
from run_original_2019_vlieland_forage_tide_solar import (
    verify_previous_original_v126_source,original_RWS_transport_retry)
from vlieland_acc_forage_tide_sun_fourway import (
    original_2019_gps_acc_quarterhour_source)
from run_original_2018_matched_week_holdout import (
    common_matched_source,STAGE_OFFSETS,RIDGE_LAMBDA,WEEK_FOLDS)
from native_quarterhour_lag_tide import corrected_previous_bin
from bird_tide_after_prev15 import source_gate,score_models,MIN_HISTORY_PAIRS

ROOT=Path(__file__).resolve().parents[1]
V166=ROOT/"validation_v166/results/frozen_corrected_15min_source_receipt_v166.json"
FULL=ROOT/"validation_v167/results/original_2019_vlieland_history_tide_weekcv_v167.json"
RECEIPT=ROOT/"validation_v167/results/frozen_2019_history_tide_receipt_v167.json"
SOURCE_YEAR=2019
ORIGINAL_V127_RUN=43461048062
MIN_COMMON_BIRD_TIDE_SOURCE=20000
MIN_NATIVE_QH_MONTHS=4

def verified_2019_source(prior_gps,prior_48h,prior_v127):
    old_gps=json.loads(Path(prior_gps).read_text())
    old_rws=json.loads(Path(prior_48h).read_text())
    old_v127=json.loads(Path(prior_v127).read_text())
    if old_v127.get("source_or_field_status")!="ORIGINAL_2019_VLIELAND_ACC_CLASSIFIED_FORAGE_FOURWAY_REAL_RWS_SOLAR_EVALUATED":
        raise SourceStop("STOP_PRIOR_V127_ORIGINAL_2019_SOURCE_NOT_SUCCESSFUL")
    # Strict current publisher member manifest and original MD5 through the
    # exact already successful v127 source functions, BEFORE any Y model.
    files,pubmeta=original_publisher_manifest()
    original_ref,ref_sha=original_native_file(files["O_VLIELAND-reference-data.csv"])
    known_birds,refqa=_reference_anonymous_identity(original_ref)
    raw_acc,acc_sha=original_native_file(files[BEHAVIOUR_FILE])
    raw_gps,gps_sha=authenticate_original_gps_2019()
    index,gpsmeta=original_2019_gps_source_index(raw_gps,known_birds)
    anonymous,private=true_original_2019_behaviour_gps_join(
        raw_acc,known_birds,index,return_private_quarterhour_bins=True)
    source_gps_identity=verify_previous_original_v126_source(
        old_gps,gpsmeta,anonymous)
    original_bins,original_bin_receipt=original_2019_gps_acc_quarterhour_source(private)
    if original_bin_receipt["original_2019_true_source_bin_n"]<MIN_COMMON_BIRD_TIDE_SOURCE:
        raise SourceStop("STOP_2019_NATIVE_BIRD_QUARTERHOUR_COUNT_LOW")
    # Source-level 2019 four-month true gauge response SHA compared to actual
    # original v127 successful run. Wrong tide offsets are aligned later.
    def real_month_with_same_transport(month):
        (source,body_sha),retry=original_RWS_transport_retry(month)
        return source,body_sha
    RWS,proof=fetch_all_2019_Vlieland_real_RWS_months(
        old_rws,request_fn=real_month_with_same_transport,sleeper=lambda _:None)
    prior=old_v127["original_2019_full_RWS_measured_fourmonths"]
    source_prior=prior["original_true_2019_months"]
    source_now=proof["original_true_2019_months"]
    if len(source_prior)!=4 or len(source_now)!=4:
        raise SourceStop("STOP_ORIGINAL_V127_RWS_MONTH_COUNT_CHANGED")
    for a,b in zip(source_prior,source_now):
        if (a["source_month"]!=b["source_month"] or
            a["original_RWS_2019_month_JSON_SHA256"]!=b["original_RWS_2019_month_JSON_SHA256"] or
            a["true_original_2019_10min_unique_count"]!=b["true_original_2019_10min_unique_count"]):
            raise SourceStop("STOP_ORIGINAL_2019_RWS_PUBLISHER_RESPONSE_SHA_OR_COUNTS_CHANGED")
    if prior["native_RWS_true_2019_10min_unique_readings_four_months"] != proof["native_RWS_true_2019_10min_unique_readings_four_months"]:
        raise SourceStop("STOP_ORIGINAL_2019_RWS_FULL_COUNT_CHANGED")
    common,matched_source=common_matched_source(original_bins,RWS)
    if len(common)<MIN_COMMON_BIRD_TIDE_SOURCE:
        raise SourceStop("STOP_ORIGINAL_2019_REAL_AND_WRONG_TIDE_COMMON_SOURCE_LT20K")
    return common,{
        "genuine_Zenodo_2019_GPS_ACC_native_MD5_replay":source_gps_identity,
        "genuine_original_2019_15min_source_bin_proof":original_bin_receipt,
        "genuine_2019_RWS_months_provider_SHA_exact_replayed":True,
        "genuine_2019_RWS_month_count":len(source_now),
        "genuine_2019_RWS_total_10min_observed_times":proof["native_RWS_true_2019_10min_unique_readings_four_months"],
        "2019_original_v130_common_source_matching_method_reused":True,
        "2019_native_real_and_3_7_11day_source_common_hour_proof":matched_source,
        "original_reference_source_MD5_reverified":ref_sha["source_SHA256_local"] if "source_SHA256_local" in ref_sha else ref_sha,
        "source_gps_native_response_SHA256":gps_sha.get("source_SHA256_local"),
        "source_ACC_native_response_SHA256":acc_sha.get("source_SHA256_local"),
        "publisher_original_record":10053988,
        "private_2019_bird_GPS_ACC_times_not_exported":True
    }

def evaluate(prior_gps,prior_rws,prior_v127):
    old166=json.loads(V166.read_text())
    if (old166["source_actual_previous_bin_gate"]["source_true_previous_15min_same_bird_rows"]!=157863 or
        old166["source_actual_previous_bin_gate"]["all_predeclared_source_gates_pass"] is not True or
        old166["source_scoring_fixed_parameters"]["ridge_lambda_exact_legacy"] != RIDGE_LAMBDA):
        raise SourceStop("STOP_FROZEN_V166_2018_NATIVE_QUARTERHOUR_RESULT_CHANGED")
    common,proof=verified_2019_source(prior_gps,prior_rws,prior_v127)
    idx,prev,quality=corrected_previous_bin(common)
    gate=source_gate(common,idx,prev)
    result={
       "version":"v167_original_2019_Vlieland_historical_bird_prev15_and_real_RWS_tide_1",
       "source_original_year":SOURCE_YEAR,
       "source_prior_2018_v166_result_replayed_for_design":True,
       "original_2019_v125_v126_v127_bird_RWS_publisher_SHA_verified":proof,
       "source_clock_native_2019_15min_window_offset_audit":quality,
       "source_2019_previous_real_quarterhour_bird_gate":gate,
       "frozen_methods":{
           "models":"identical fixed v166 prev15 + true-vs-ghost RWS source and ridge design",
           "true_wrong_shift_days":list(STAGE_OFFSETS),
           "Ridge_lambda":RIDGE_LAMBDA,
           "CV_grouping":"five original ISO-week modulo folds, bird-equal within-week, week-equal",
           "testweek_actual_prev15_behavior_is_observed":"YES_ONLINE_NOWCAST",
           "source_min_qualified_previous_bins":MIN_HISTORY_PAIRS,
           "source_min_original_full_common_bins":MIN_COMMON_BIRD_TIDE_SOURCE,
           "native_calendar_year_2019_is_distinct_from_v166_2018":True,
           "original_tagged_birds_overlap_2018_2019":True,
           "frozen_history_source_rule_was_chosen_after_original_2018_results":True
       },
       "source_2019_original_common_15min_bins":len(common),
       "source_2019_true_previous_window_15min_bins":len(idx),
       "original_2019_model_if_source_admitted":(
           score_models(common,idx,prev) if gate["all_predeclared_source_gates_pass"] else
           {"status":"STOP_ORIGINAL_2019_PREVIOUS_BIN_COHORT_GATE"}
       ),
       "biological_cross_coast_independent_study":"NOT_ADDED",
       "true_local_tidal_intertidal_patch_access":"NOT_MEASURED",
       "true_individual_memory_or_social_Boids_parameters":"NOT_IDENTIFIED",
       "causal_global_tide_solar_effect":"NOT_ESTIMATED"
    }
    return result

def compact(v):
    canonical=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":v["version"],
        "original_full_result_first_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
        "source_calendar_year":v["source_original_year"],
        "source_common_real_ghost_quarterhour_bins":v["source_2019_original_common_15min_bins"],
        "source_true_prev15_real_observations":v["source_2019_true_previous_window_15min_bins"],
        "source_gate":v["source_2019_previous_real_quarterhour_bird_gate"],
        "source_native_clock_QA":v["source_clock_native_2019_15min_window_offset_audit"],
        "original_2019_model":v["original_2019_model_if_source_admitted"],
        "original_2019_source_RWS_months_sha":v["original_2019_v125_v126_v127_bird_RWS_publisher_SHA_verified"]["genuine_2019_RWS_months_provider_SHA_exact_replayed"],
        "same_individual_population_not_independent_new_coast":True,
        "no_biological_tide_by_solar_causes_or_social_Boids_inferred":True,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v126-original-gps",required=True)
    p.add_argument("--v126-original-rws",required=True)
    p.add_argument("--v127-original",required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=p.parse_args()
    full=evaluate(args.v126_original_gps,args.v126_original_rws,args.v127_original)
    rec=compact(full)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("No frozen original 2019 source receipt")
        saved=json.loads(RECEIPT.read_text())
        differences=[]
        def compare(p,a,b):
            if len(differences)>=35:return
            if p=="root.original_full_result_first_sha256":return
            if (isinstance(a,(int,float)) and not isinstance(a,bool) and
                isinstance(b,(int,float)) and not isinstance(b,bool)):
                if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-7:
                    differences.append([p,a,b])
            elif type(a)!=type(b):differences.append([p,"TYPE"])
            elif isinstance(a,dict):
                if set(a)!=set(b):differences.append([p,"KEYS"])
                else:
                    for k in sorted(a):compare(p+"."+str(k),a[k],b[k])
            elif isinstance(a,list):
                if len(a)!=len(b):differences.append([p,"LEN",len(a),len(b)])
                else:
                    for i in range(len(a)):compare(p+"["+str(i)+"]",a[i],b[i])
            elif a!=b:differences.append([p,a,b])
        compare("root",saved,json.loads(json.dumps(rec,sort_keys=True)))
        if differences:
            print("V167_ORIGINAL_SOURCE_REPLAY_DIFFS="+json.dumps(differences,ensure_ascii=True))
            raise AssertionError("v167 source SHA, original group or model changed")
        print("V167_TRUE_2019_SOURCE_AND_ORIGINAL_WEEK_MODEL_REPLAY_PASS")
    else:
        print("V167_SOURCE_RECEIPT_START")
        print(json.dumps(rec,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V167_SOURCE_RECEIPT_END")
    print("V167_PUBLIC_SCOPE_AND_MODEL="+json.dumps({
        "source_2019_quarterhours":rec["source_common_real_ghost_quarterhour_bins"],
        "observed_previous_bins":rec["source_true_prev15_real_observations"],
        "passed":rec["source_gate"]["all_predeclared_source_gates_pass"],
        "gains":rec["original_2019_model"].get("conditional_observed_prev15_behavior_tide_gains"),
        "bootstrap":rec["original_2019_model"].get("conditional_10000_week_score_bootstrap_CI95_NOT_causal")
    },ensure_ascii=True,sort_keys=True))

if __name__=="__main__":
    main()
