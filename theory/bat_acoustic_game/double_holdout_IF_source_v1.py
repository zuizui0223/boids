"""Double holdout of an ORIGINAL, ALREADY-PUBLISHED bat vocal playback source.

SOURCE-BACKED SECONDARY EXPLORATION, not new bat measurements, and no
independent bat sample. For each test bat and source condition, train on
other bats AND other original stimulus conditions. Training uses bat-condition
means (not pulse rows) and requires source-supported biological units.
No original bat IDs, raw IF/TF or individual responses are serialized.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import mean,median
import json,math

from published_IF_TF_convention_v1 import (
    EXPERIMENTS,SHA256,clean_source_rows,contrast_contexts,bat_error_summary,
    bootstrap_means,leave_one_out_range
)
from IF_TF_temporal_window_sensitivity_v1 import source,filter_window,WINDOWS

ROOT=Path(__file__).resolve().parent
CONTRACT=ROOT/"DOUBLE_HOLDOUT_IF_PREDICTION_PREOUTPUT_V1.md"
OUT=ROOT/"BAT_DOUBLE_HOLDOUT_IF_PREDICTION_V1.json"
METHODS=("median","mean")
MODELS=("zero","constant_training_mean","stimulus_linear",
        "fixed_bandwidth","trained_IF_TF_affine")
FORWARD_MODELS=("zero","constant_training_mean","stimulus_linear")
CONDITIONAL_MODELS=("fixed_bandwidth","trained_IF_TF_affine")
MIN_TRAIN_BATS=5
MIN_TRAIN_STIMULI=3


def ols_fit(train,key_y,key_x):
    # Ordinary least squares of original source bat-condition means with
    # equal cell weights; the fit sees NO target bat and NO target condition.
    x=[r[key_x] for r in train]
    y=[r[key_y] for r in train]
    avgx=mean(x); avgy=mean(y)
    var=sum((v-avgx)**2 for v in x)
    if var<=1e-15:
        raise ValueError("STOP_NO_TRAINING_VARIANCE_"+key_x)
    beta=sum((a-avgx)*(b-avgy) for a,b in zip(x,y))/var
    intercept=avgy-beta*avgx
    return intercept,beta


def predict(train,test):
    const=mean(r["delta_IF_khz"] for r in train)
    ax,bx=ols_fit(train,"delta_IF_khz","coordinate")
    at,bt=ols_fit(train,"delta_IF_khz","delta_TF_khz")
    return {
        "zero":0.0,
        "constant_training_mean":const,
        "stimulus_linear":ax+bx*test["coordinate"],
        # Requires current target bat's TF response: not forward prediction!
        "fixed_bandwidth":test["delta_TF_khz"],
        "trained_IF_TF_affine":at+bt*test["delta_TF_khz"]
    }


def group_double_holdout(bat_conditions,experiment):
    # A biological bat may also appear in other source experiments; never
    # admit those rows. Current e is a fully independent training scope.
    cohort={}
    for (bat,e),levels in bat_conditions.items():
        if e!=experiment or bat_error_summary(levels) is None:
            continue
        cohort[bat]=dict(levels)
    bats=sorted(cohort)
    if len(bats)<MIN_TRAIN_BATS+1:
        return {"status":"STOP_TOO_FEW_BIOLOGICAL_BATS",
                "eligible_bats":len(bats),"trained_models":[]}
    all_levels=sorted(set().union(*[set(v) for v in cohort.values()]))
    if len(all_levels)<MIN_TRAIN_STIMULI+1:
        return {"status":"STOP_TOO_FEW_SOURCE_CONDITIONS",
                "eligible_bats":len(bats),"trained_models":[]}

    errors_by_bat={bat:{model:[] for model in MODELS} for bat in bats}
    fold_counts=[]
    for bat in bats:
        for condition,test in sorted(cohort[bat].items()):
            train=[record for other,conditions in cohort.items() if other!=bat
                   for train_condition,record in conditions.items()
                   if train_condition!=condition]
            train_bats={other for other,conditions in cohort.items() if other!=bat
                        for train_condition in conditions if train_condition!=condition}
            train_levels={train_condition for other,conditions in cohort.items() if other!=bat
                          for train_condition in conditions if train_condition!=condition}
            if len(train_bats)<MIN_TRAIN_BATS or len(train_levels)<MIN_TRAIN_STIMULI:
                return {"status":"STOP_HELDOUT_FOLD_TRAIN_SUPPORT",
                        "eligible_bats":len(bats),"trained_models":[]}
            try:
                predicted=predict(train,test)
            except (ValueError,ZeroDivisionError) as e:
                return {"status":"STOP_FOLD_FIT_FAILED",
                        "reason":type(e).__name__+":"+str(e)[:100],
                        "eligible_bats":len(bats),"trained_models":[]}
            assert set(predicted)==set(MODELS)
            for name,guess in predicted.items():
                if not math.isfinite(guess):
                    return {"status":"STOP_NONFINITE_FOLD_PREDICTION",
                            "eligible_bats":len(bats),"trained_models":[]}
                errors_by_bat[bat][name].append(abs(test["delta_IF_khz"]-guess))
            fold_counts.append({"training_bats":len(train_bats),
                                "training_conditions":len(train_levels),
                                "train_bat_condition_cells":len(train)})
    sourcebat_errors={bat:{m:mean(ee[m]) for m in MODELS} for bat,ee in errors_by_bat.items()}
    model_summary={}
    for name in MODELS:
        v=[ee[name] for ee in sourcebat_errors.values()]
        model_summary[name]={
          "information_class":"stimulus_only_forward" if name in FORWARD_MODELS
                         else "conditional_uses_target_TF",
          "equal_bat_MAE_khz":mean(v),
          "median_bat_MAE_khz":median(v),
          "n_unique_source_bats":len(v),
          "n_source_bat_condition_test_pairs":sum(len(ee[name]) for ee in errors_by_bat.values()),
          "n_bats_model_error_finite":sum(math.isfinite(x) for x in v)
        }
    comparisons={}
    declared=(
        ("stimulus_linear_vs_constant","stimulus_linear","constant_training_mean"),
        ("stimulus_linear_vs_zero","stimulus_linear","zero"),
        ("trained_TF_affine_vs_fixed_bandwidth","trained_IF_TF_affine","fixed_bandwidth"),
        ("trained_TF_affine_vs_constant","trained_IF_TF_affine","constant_training_mean"),
    )
    for label,a,b in declared:
        delta=[ee[a]-ee[b] for ee in sourcebat_errors.values()]
        comparisons[label]={
           "mean_delta_MAE_khz":mean(delta),
           "median_delta_MAE_khz":median(delta),
           "source_bats_for_first_model":sum(x< -1e-12 for x in delta),
           "source_bats_for_second_model":sum(x>1e-12 for x in delta),
           "source_bats_ties":sum(abs(x)<=1e-12 for x in delta),
           "whole_bat_bootstrap_mean_delta_95_khz":bootstrap_means(delta),
           "whole_bat_leave_one_out_mean_delta_min_max_khz":leave_one_out_range(delta),
           "inference_level":"DESCRIPTIVE_SOURCE_BAT_ERRORS_NOT_INDEPENDENT_EXTERNAL_REPLICATION"
        }
    return {"status":"EVALUATED",
            "eligible_bats":len(bats),
            "n_source_levels":len(all_levels),
            "source_condition_coverage_per_bat_range":[min(len(x) for x in cohort.values()),
                                                       max(len(x) for x in cohort.values())],
            "n_evaluated_original_bat_condition_folds":len(fold_counts),
            "training_bats_min_max":[min(x["training_bats"] for x in fold_counts),
                                     max(x["training_bats"] for x in fold_counts)],
            "training_conditions_min_max":[min(x["training_conditions"] for x in fold_counts),
                                            max(x["training_conditions"] for x in fold_counts)],
            "training_cell_count_min_max":[min(x["train_bat_condition_cells"] for x in fold_counts),
                                           max(x["train_bat_condition_cells"] for x in fold_counts)],
            "no_source_ID_exported":True,
            "models":model_summary,"comparisons":comparisons}


def evaluate(rows,method):
    # Caller pre-pins source original bytes. Bat ID is only present here
    # during CI runtime and never reaches public result JSON.
    by,qc=clean_source_rows(rows)
    context,support=contrast_contexts(by,method)
    out={e:group_double_holdout(context,e) for e in EXPERIMENTS}
    return {"source_quality":qc,
            "eligible_original_ON_OFF_subcontexts":support,
            "experiments":out}


def run():
    if not CONTRACT.exists():
        raise ValueError("STOP_MISSING_PREOUTPUT_EVALUATION_CONTRACT")
    raw,sha=source()
    if sha!=SHA256:
        raise ValueError("STOP_ORIGINAL_SOURCE_SHA_MISMATCH")
    cases={}
    for label in ("full",*WINDOWS.keys()):
        if label=="full":
            rows=raw
            filters={"window":"all_original_source_times"}
        else:
            rows,reject=filter_window(raw,WINDOWS[label]["off"],WINDOWS[label]["on"])
            filters={"OFF_window":WINDOWS[label]["off"],"ON_window":WINDOWS[label]["on"],
                     "excluded_source_rows":reject}
        cases[label]={
          "n_source_rows_in_policy":len(rows),
          "original_time_policy":filters,
          "source_models":{mode:evaluate(rows,mode) for mode in METHODS}
        }
    primary=cases["full"]["source_models"]["median"]["experiments"]["IPIlow"]
    return {
      "schema":1,
      "status":"SOURCE_DOUBLE_HOLDOUT_EVALUATED" if primary["status"]=="EVALUATED"
               else "SOURCE_PRIMARY_SUPPORT_STOP",
      "source_paper_doi":"10.1098/rspb.2026.0921",
      "source_data_doi":"10.6084/m9.figshare.30937379",
      "source_SHA256":sha,
      "original_source_rows":len(raw),
      "original_source_bats_across_all_experiments":11,
      "source_outcomes_had_been_published_and_prior_source_analyses_examined":True,
      "novel_animal_measurements":False,
      "individual_BAT_IDs_and_original_pulse_rows_not_exported":True,
      "models_forward_ONLY":list(FORWARD_MODELS),
      "models_conditional_on_heldout_measured_TF":list(CONDITIONAL_MODELS),
      "source_groups_not_new_species_or_independent_populations":True,
      "temporal_causal_confound":"OFF precedes ON in all 105 eligible source contexts",
      "training_scheme":"leave one biological bat AND one entire source stimulus level out within source experiment",
      "no_hyperparameter_or_post_response_model_selection":True,
      "cases":cases,
      "novelty_ceiling":"Exploratory source-internal conditional transfer, not demonstrated new bat sensory mechanism, real prey capture or causal acoustic evolution."
    }


def main():
    try:
        obj=run()
    except Exception as exc:
        obj={"schema":1,"status":"STOP_SOURCE_OR_PREDICTION_GATE",
             "error":type(exc).__name__+":"+str(exc)[:240],
             "novel_animal_measurements":False,
             "individual_BAT_IDs_and_original_pulse_rows_not_exported":True}
    OUT.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    print("DOUBLE_HOLDOUT_SOURCE_STATUS",obj["status"])
    if obj["status"].startswith("STOP"):
        print("SOURCE_STOP_REASON",obj.get("error","source support failed"))
        return 3 if obj["status"]=="STOP_SOURCE_OR_PREDICTION_GATE" else 0
    print("SOURCE_SHA",obj["source_SHA256"],"ROWS",obj["original_source_rows"])
    for window,rows in obj["cases"].items():
        print("WINDOW",window,"source_rows",rows["n_source_rows_in_policy"])
        for method,mode in rows["source_models"].items():
            for exp,r in mode["experiments"].items():
                print("SOURCE_HOLDOUT",window,method,exp,
                  "status",r["status"],"bats",r["eligible_bats"],
                  "folds",r.get("n_evaluated_original_bat_condition_folds"),
                  "train_sizes",r.get("training_cell_count_min_max"))
                if r["status"]!="EVALUATED":continue
                print("MODEL_SOURCE_MAE",window,method,exp,
                      {k:round(v["equal_bat_MAE_khz"],6) for k,v in r["models"].items()})
                for label,v in r["comparisons"].items():
                    print("SOURCE_MODEL_DELTA",window,method,exp,label,
                          "delta_MAE",round(v["mean_delta_MAE_khz"],6),
                          "bat_better",v["source_bats_for_first_model"],
                          "bat_worse",v["source_bats_for_second_model"],
                          "CI",v["whole_bat_bootstrap_mean_delta_95_khz"])
    return 0


if __name__=="__main__":
    raise SystemExit(main())
