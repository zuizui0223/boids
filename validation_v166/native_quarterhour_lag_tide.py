"""v166: CORRECT original 2018 oystercatcher 15min bin lag and tide.

v165 original source gate STOPPED at 1904 exact EVENT-timestamp 15m matches
because native v129/v130 rows intentionally use EARLIEST ACC event within
their 15-minute bin as an observable representative timestamp, not the
quarterhour window start. Source lineage (v129 line):
  binutc = original native_UTC_15min_bin
  event  = earliest_true_classification_UTC, and 0 <= event-binutc <900s.

Correct the SOURCE-ONLY lag identity by rebuilding TRUE UTC floor15 bin
from each earliest observed event time. Each tagged bird × floor15 window
must be unique; only adjacent windows within the same ISO calendar week
qualify. No missing ACC/GPS source window is silently forged.

This is an EXPLICIT AFTER-STOP measurement clock repair, not changing
the scientific v165 source minimum (>=25,000) or fixed ridge/solar/tide
model/ghost offsets/whole-week folds. Legacy v165 source STOP is frozen.

A previous 15min WINDOW's Y is an observed earlier window, but the two
earliest events need NOT be exactly 900 seconds apart. Treat Yprev as
previous window acoustic/classifier state, not exact 15m ago or actual
feeding duration. TEST-week prior-window observations are test-time input
to conditional nowcasting, not a true week-ahead forecast.
"""
from __future__ import annotations

import argparse,hashlib,json,math
from collections import Counter
from datetime import timedelta
from pathlib import Path
import numpy as np
from bird_tide_after_prev15 import (
    source_input_and_replay,source_gate,score_models,
    source_actual_previous,MAX_SRC_H,MIN_HISTORY_PAIRS,
    RIDGE_LAMBDA,STAGE_OFFSETS,WEEK_FOLDS,NAMES
)

ROOT=Path(__file__).resolve().parents[1]
LEGACY=ROOT/"validation_v165/results/frozen_bird_source_model_receipt_v165.json"
RECEIPT=ROOT/"validation_v166/results/frozen_corrected_15min_source_receipt_v166.json"
FULL=ROOT/"validation_v166/results/original_true_15min_binned_bird_tide_v166.json"
OBSERVED_OLD_EVENT_EXACT_MATCHES=1904
QUARTER_SECONDS=900

def floor15(dt):
    if dt.tzinfo is None or dt.utcoffset()!=timedelta(0):
        raise ValueError("Original normalized source event time must be UTC")
    return dt.replace(minute=dt.minute//15*15,second=0,microsecond=0)

def corrected_previous_bin(common):
    """Source-only true bin-time, not the different native earliest event time."""
    by_bird_quarter={}
    delta=[]
    for i,(e,sol,stage,week) in enumerate(common):
        t=e["source_utc_event"]
        bin_start=floor15(t)
        within=(t-bin_start).total_seconds()
        if not 0<=within<QUARTER_SECONDS:
            raise AssertionError("Original ACC event time outside its native quarterhour bin")
        key=(e["private_bird"],bin_start)
        if key in by_bird_quarter:
            raise AssertionError("Source contains duplicate same bird x reconstructed 15min bin")
        by_bird_quarter[key]=i
        delta.append(within)
    idx=[];prior=[];qa=Counter()
    for i,(e,_,_,week) in enumerate(common):
        t=floor15(e["source_utc_event"])
        p=by_bird_quarter.get((e["private_bird"],t-timedelta(minutes=15)))
        if p is None:
            qa["NO_OBSERVED_PREVIOUS_NATIVE_15MIN_BIN"]+=1
            continue
        old,_,_,oldweek=common[p]
        oldstart=floor15(old["source_utc_event"])
        if oldstart+timedelta(minutes=15)!=t:
            raise AssertionError("Wrong original source lag bin match")
        if oldweek!=week or oldstart.isocalendar().year!=t.isocalendar().year:
            qa["ORIGINAL_QUARTERHOUR_SOURCE_WEEK_BOUNDARY"]+=1
            continue
        idx.append(i);prior.append(p)
        qa["TRUE_OBSERVED_PREVIOUS_NATIVE_15MIN_BIN_SAME_BIRD"]+=1
    if len(idx)!=len(set(idx)) or len(idx)!=len(prior):
        raise AssertionError("Source lag identifiers duplicated")
    d=np.asarray(delta,dtype=float)
    qa["ORIGINAL_SOURCE_EARLIEST_EVENT_TIMESTAMP_NOT_NATIVE_BIN_START_n"]=int((d!=0).sum())
    return (
        np.asarray(idx,dtype=np.int64),
        np.asarray(prior,dtype=np.int64),
        {
            **dict(qa),
            "original_source_bins_count":len(common),
            "fraction_original_earliest_event_timestamp_differs_from_exact_quarterhour_start":
                 round(float((d!=0).mean()),8),
            "earliest_event_offset_inside_original_quarterhour_p05_seconds":
                 round(float(np.quantile(d,.05)),3),
            "earliest_event_offset_inside_original_quarterhour_median_seconds":
                 round(float(np.median(d)),3),
            "earliest_event_offset_inside_original_quarterhour_p95_seconds":
                 round(float(np.quantile(d,.95)),3),
            "observed_previous_state_is_previous_15min_window_not_900s_between_events":True,
            "test_week_prior_window_Y_is_observed_nowcast_input":True
        }
    )

def run(v128_file,v129_file):
    legacy=json.loads(LEGACY.read_text())
    if (legacy["source_n_recorded_original_common_bins"]!=MAX_SRC_H or
        legacy["source_n_true_prev15_qualifying_bins"]!=OBSERVED_OLD_EVENT_EXACT_MATCHES or
        legacy["new_source_quality"]["all_predeclared_source_gates_pass"]):
        raise AssertionError("Frozen v165 initial source stop/definition evidence changed")
    original,proof=source_input_and_replay(v128_file,v129_file)
    idx,prev,qa=corrected_previous_bin(original)
    gate=source_gate(original,idx,prev)
    result={
        "version":"v166_original_2018_bird_native_quarterhour_bin_corrected_lag_tide_1",
        "original_genuine_source_scope":{
            "full_original_common_recorded_source_bins":len(original),
            "v165_exact_earliest_event_UTC_source_pairs_STOP":OBSERVED_OLD_EVENT_EXACT_MATCHES,
            "native_quarterhour_start_reconstruction":"UTC floor earliest ACC event to 15-minute grid, justified by original v129 native bin validation",
            "v165_and_v166_identical_source_minimum_qualifying_pairs":MIN_HISTORY_PAIRS,
            "v165_stop_result_left_unchanged":True,
        },
        "original_v128_v129_v130_source_SHA_verified":proof,
        "native_source_clock_diagnostic":qa,
        "corrected_actual_observed_previous_15min_window_gate":gate,
        "fixed_scoring":{
            "models":list(NAMES),
            "ridge_lambda_exact_legacy":RIDGE_LAMBDA,
            "five_original_calendar_week_folds":WEEK_FOLDS,
            "true_wrong_RWS_offsets_days":list(STAGE_OFFSETS),
            "source_sampling_unit":"genuine tagged bird 15min ACC/GPS classification window",
            "previous_state":"genuine SAME bird previous original 15min window, not event exactly 15m earlier",
            "outcome":"observed ACC classified forage/(forage+inactive) event fraction; not food intake",
            "test_week_prior_Y_access":"OBSERVED_ONLINE_TESTWEEK_STATE_not_week_ahead",
            "original_2018_behavior_and_true_tide_v130_outcomes_ALREADY_SEEN":True,
            "individual_tag_ID_GPS_or_raw_RWS_values_publication":"NO",
        },
        "model_outcomes_if_original_source_passes":(
            score_models(original,idx,prev) if gate["all_predeclared_source_gates_pass"] else
            {"status":"STOP_QUARTERHOUR_CORRECTED_SOURCE_MINIMUM_NOT_MET"}
        ),
        "physical_true_patch_tide_sun_mechanism":"NOT_ESTIMATED",
        "independent_other_coastal_site_species":"NOT_ESTIMATED",
        "social_Boids_forces":"NOT_IDENTIFIED"
    }
    return result

def compact(v):
    canon=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":v["version"],
        "first_run_canonical_full_source_original_model_SHA256":hashlib.sha256(canon.encode()).hexdigest(),
        "all_original_source_gates":v["original_genuine_source_scope"],
        "source_earliest_event_vs_bin_start_audit":v["native_source_clock_diagnostic"],
        "source_actual_previous_bin_gate":v["corrected_actual_observed_previous_15min_window_gate"],
        "source_scoring_fixed_parameters":v["fixed_scoring"],
        "original_bird_RWS_source_week_test_outcomes":v["model_outcomes_if_original_source_passes"],
        "original_provider_GPS_ACC_RWS_SHA_rechecked":True,
        "no_claim_of_independent_biological_confirmation_or_social_causation":True
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--v128-source",required=True)
    p.add_argument("--v129-original",required=True)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    full=run(args.v128_source,args.v129_original)
    receipt=compact(full)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("No original frozen v166 source/model receipt")
        old=json.loads(RECEIPT.read_text())
        errors=[]
        def verify(prefix,a,b):
            if len(errors)>=40:return
            if prefix=="root.first_run_canonical_full_source_original_model_SHA256":
                return
            if type(a)!=type(b):errors.append([prefix,"TYPE"])
            elif isinstance(a,dict):
                if set(a)!=set(b):errors.append([prefix,"KEYS"])
                else:
                    for k in sorted(a):verify(prefix+"."+str(k),a[k],b[k])
            elif isinstance(a,list):
                if len(a)!=len(b):errors.append([prefix,"LEN",len(a),len(b)])
                else:
                    for i in range(len(a)):verify(prefix+"["+str(i)+"]",a[i],b[i])
            elif isinstance(a,float):
                if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-7:
                    errors.append([prefix,a,b])
            elif a!=b:errors.append([prefix,a,b])
        verify("root",old,json.loads(json.dumps(receipt,sort_keys=True)))
        if errors:
            print("V166_QUARTERHOUR_ORIGINAL_SOURCE_REPLAY_DIFFS="+json.dumps(errors,ensure_ascii=True))
            raise AssertionError("Original 2018 bird native quarterhour or RWS score changed")
        print("V166_GENUINE_ORIGINAL_NATIVE_QUARTERHOUR_BIRD_RWS_REPLAY_PASS")
    else:
        print("V166_ORIGINAL_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V166_ORIGINAL_SOURCE_RECEIPT_END")
    print("V166_RESULT_FOCUS="+json.dumps({
        "source_old_exact_event_pairs":OBSERVED_OLD_EVENT_EXACT_MATCHES,
        "source_quarterhour_true_previous_pairs":receipt["source_actual_previous_bin_gate"]["source_true_previous_15min_same_bird_rows"],
        "passed":receipt["source_actual_previous_bin_gate"]["all_predeclared_source_gates_pass"],
        "gains":receipt["original_bird_RWS_source_week_test_outcomes"].get("conditional_observed_prev15_behavior_tide_gains"),
        "conditional95":receipt["original_bird_RWS_source_week_test_outcomes"].get("conditional_10000_week_score_bootstrap_CI95_NOT_causal"),
    },sort_keys=True))

if __name__=="__main__":
    main()
