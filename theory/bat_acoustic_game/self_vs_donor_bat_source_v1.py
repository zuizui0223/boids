"""Equal-information self versus donor bat models on 2026 published acoustic source.

Uses original Figshare source only. No new animal observations, no archival
individual IDs, raw IF/TF rows or timestamps serialized. Personal 4 stimulus
levels versus each of six other bats' matching 4 levels; absolute donor errors
are averaged AFTER each single-donor model predicts held-out source call.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from statistics import mean,median

from double_holdout_IF_source_v1 import ols_fit
from published_IF_TF_convention_v1 import (
    EXPERIMENTS,SHA256,clean_source_rows,contrast_contexts,
    bootstrap_means,leave_one_out_range
)
from IF_TF_temporal_window_sensitivity_v1 import source,filter_window,WINDOWS

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"SELF_VS_DONOR_EQUAL_FOUR_CONDITIONS_PREOUTPUT_V1.md"
OUT=ROOT/"BAT_SELF_VS_DONOR_EQUAL_TRAINING_V1.json"
MODELS=("self_constant","other_constant","self_linear","other_linear")
COMPARE={
 "self_constant_minus_donor_constant":("self_constant","other_constant"),
 "self_linear_minus_donor_linear":("self_linear","other_linear"),
 "self_linear_minus_self_constant":("self_linear","self_constant"),
}
MIN_BATS=7
LEVELS=5

def fit_four(data,test):
    if len(data)!=LEVELS-1:
        raise ValueError("STOP_FOUR_SOURCE_LEVEL_TRAINING_REQUIRED")
    x=[r["coordinate"] for r in data]
    if len(set(x))!=LEVELS-1:
        raise ValueError("STOP_SOURCE_LEVELS_NOT_UNIQUE")
    m=mean(r["delta_IF_khz"] for r in data)
    a,b=ols_fit(data,"delta_IF_khz","coordinate")
    return {"constant":m,"linear":a+b*test["coordinate"]}

def group_test(bat_condition,experiment):
    cohort={bat:dict(levels)
            for (bat,e),levels in bat_condition.items()
            if e==experiment and len(levels)>=LEVELS}
    bats=sorted(cohort)
    if len(bats)<MIN_BATS:
        return {"status":"STOP_TOO_FEW_BIOLOGICAL_SOURCE_BATS",
                "bats":len(bats),"original_model_scores_exported":False}
    all_levels=sorted(set().union(*(set(cohort[i]) for i in bats)))
    common=sorted(set.intersection(*(set(cohort[i]) for i in bats)))
    if len(all_levels)!=LEVELS or len(common)!=LEVELS:
        return {"status":"STOP_UNMATCHED_SOURCE_STIMULUS_LEVELS",
                "bats":len(bats),"original_model_scores_exported":False}
    scores={i:{m:[] for m in MODELS} for i in bats}
    for bat in bats:
        for holdout in common:
            test=cohort[bat][holdout]
            own=[cohort[bat][c] for c in common if c!=holdout]
            selfpred=fit_four(own,test)
            donor_abs={"constant":[],"linear":[]}
            for donor in bats:
                if donor==bat:continue
                other=[cohort[donor][c] for c in common if c!=holdout]
                pred=fit_four(other,test)
                for type in ("constant","linear"):
                    donor_abs[type].append(abs(pred[type]-test["delta_IF_khz"]))
            expected=len(bats)-1
            if len(donor_abs["constant"])!=expected or len(donor_abs["linear"])!=expected:
                raise ValueError("STOP_DONOR_SOURCE_SUPPORT_DIFFERENCE")
            vals={
             "self_constant":abs(selfpred["constant"]-test["delta_IF_khz"]),
             "other_constant":mean(donor_abs["constant"]),
             "self_linear":abs(selfpred["linear"]-test["delta_IF_khz"]),
             "other_linear":mean(donor_abs["linear"]),
            }
            for k,v in vals.items():
                if not math.isfinite(v):
                    raise ValueError("STOP_NONFINITE_ORIGINAL_SOURCE_PREDICTION")
                scores[bat][k].append(v)
    individual={i:{m:mean(a[m]) for m in MODELS} for i,a in scores.items()}
    models={}
    for m in MODELS:
        vv=[a[m] for a in individual.values()]
        models[m]={"mean_bat_equal_condition_MAE_khz":mean(vv),
                   "median_bat_equal_condition_MAE_khz":median(vv),
                   "biological_bats":len(bats),
                   "bat_condition_test_cells":sum(len(a[m]) for a in scores.values()),
                   "trained_source_levels_per_individual_model":LEVELS-1,
                   "no_raw_source_IDs_exported":True}
    diffs={}
    for key,(a,b) in COMPARE.items():
        diff=[v[a]-v[b] for v in individual.values()]
        diffs[key]={
          "equal_bat_mean_error_difference_khz":mean(diff),
          "equal_bat_median_error_difference_khz":median(diff),
          "whole_bat_bootstrap_mean_95_khz":bootstrap_means(diff),
          "leave_one_bat_out_mean_min_max_khz":leave_one_out_range(diff),
          "bats_first_model_better":sum(v < -1e-12 for v in diff),
          "bats_second_model_better":sum(v > 1e-12 for v in diff),
          "bats_tie":sum(abs(v)<=1e-12 for v in diff),
          "evidence":"DESCRIPTIVE_POSTPUBLICATION_SOURCE_INDIVIDUAL_ONLY"
        }
    return {"status":"SUPPORTED_ORIGINAL_SOURCE_GROUP",
            "biological_bat_count":len(bats),
            "eligible_source_stimulus_levels":len(common),
            "source_test_bat_condition_cells":len(bats)*len(common),
            "donor_bats_compared_per_test":len(bats)-1,
            "one_model_source_level_training_count":LEVELS-1,
            "models":models,"comparison":diffs,
            "source_bat_IDs_in_results":False}


def evaluate(rows,method):
    by,qc=clean_source_rows(rows)
    context,support=contrast_contexts(by,method)
    return {"QC":qc,
            "original_eligible_subcontexts":support,
            "experiments":{e:group_test(context,e) for e in EXPERIMENTS}}


def run():
    if not CONTRACT.exists():
        raise ValueError("STOP_NO_FROZEN_POSTOUTCOME_ANALYSIS_CONTRACT")
    original,sha=source()
    if sha!=SHA256:
        raise ValueError("STOP_PUBLISHER_SHA_CHANGED")
    result={}
    for name in ("full",*WINDOWS.keys()):
        if name=="full":
            rows=original
        else:
            rows,_=filter_window(original,WINDOWS[name]["off"],WINDOWS[name]["on"])
        result[name]={"original_source_rows":len(rows),
                      "source_responses":{method:evaluate(rows,method)
                                          for method in ("median","mean")}}
    return {
        "schema":1,
        "status":"SOURCE_SECONDARY_SELF_VS_DONOR_EVALUATED",
        "source_paper":"10.1098/rspb.2026.0921",
        "source_Figshare":"10.6084/m9.figshare.30937379",
        "source_original_sha256":sha,
        "original_source_row_count":len(original),
        "original_source_unique_bat_ID_labels_across_experiments":11,
        "new_bat_measurements":False,
        "original_source_animal_IDs_or_pulses_exported":False,
        "source_prior_stimulus_predictive_failure_opened":True,
        "preoutput_matched_four_condition_rule":True,
        "no_donor_choice_or_donor_response_average_before_error":True,
        "source_time_causal_confound":"All 105 source playback control OFF groups chronologically precede ON",
        "scope":"Original 2026 within-study acute bat playback responses only, not longitudinal memory, prey capture, or independent generality",
        "source_model_groups":result
    }

def main():
    try:
        obj=run()
    except Exception as e:
        obj={"schema":1,"status":"STOP_SOURCE_OR_MATCHED_DONOR_DESIGN",
             "error":type(e).__name__+":"+str(e)[:250],
             "new_bat_measurements":False,
             "original_source_animal_IDs_or_pulses_exported":False}
    OUT.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print("BAT_SELF_DONOR_STATUS",obj["status"])
    if obj["status"].startswith("STOP"):
        print("STOP_REASON",obj["error"])
        return 3
    print("SOURCE_PIN",obj["source_original_sha256"])
    for window,rec in obj["source_model_groups"].items():
        for method,view in rec["source_responses"].items():
            for exp,group in view["experiments"].items():
                print("SOURCE_SELF_DONOR",window,method,exp,
                    "support",group["status"],
                    "bats",group.get("biological_bat_count"),
                    "source_test_cells",group.get("source_test_bat_condition_cells"))
                if group["status"]!="SUPPORTED_ORIGINAL_SOURCE_GROUP":continue
                print("MAE_SELF_DONOR",window,method,exp,
                    {n:round(v["mean_bat_equal_condition_MAE_khz"],6)
                     for n,v in group["models"].items()})
                for n,v in group["comparison"].items():
                    print("SELF_DONOR_DIFF",window,method,exp,n,
                        "delta_MAE",round(v["equal_bat_mean_error_difference_khz"],6),
                        "self_win",v["bats_first_model_better"],
                        "donor_win",v["bats_second_model_better"],
                        "CI",v["whole_bat_bootstrap_mean_95_khz"])
    return 0

if __name__=="__main__":
    raise SystemExit(main())
