"""Independent v41 original 12-group heldout joint speed×turn statistic audit.

Reads ONLY the GitHub Action's source-safe original summary RESULT JSON.
Does not read/reimplement model training or any fish XY/frame/future Y.
Independently recalculates ratios, original group signs and 5000 x 12 group
bootstrap, without importing v32/v33/v40/v41 model implementations.
"""
from __future__ import annotations
import argparse,json,hashlib
from pathlib import Path
import numpy as np

HORIZONS=("short","delayed")
CATS=("SLOW_TLOW","SLOW_THIGH","SHIGH_TLOW","SHIGH_THIGH")
MODELS=("G_geometry","GLOBAL","NEAR_TRUE","NEAR_ROT1")
METRICS=("local_beyond_GLOBAL","true_neighbor_identity_vs_ROT1")
TESTS={
 "TURN_EFFECT_WITHIN_LOW_SPEED":("SLOW_THIGH","SLOW_TLOW"),
 "TURN_EFFECT_WITHIN_HIGH_SPEED":("SHIGH_THIGH","SHIGH_TLOW"),
 "SPEED_EFFECT_WITHIN_LOW_TURN":("SHIGH_TLOW","SLOW_TLOW"),
 "SPEED_EFFECT_WITHIN_HIGH_TURN":("SHIGH_THIGH","SLOW_THIGH"),
 "SPEEDxTURN_DIFF_IN_DIFF":None
}
STATUS="V41_ORIGINAL_84_TRACKS_12_SHOAL_POSTV40_JOINT_SPEED_TURN_EXPLORATORY_RESULT"

def fail(reason):
    raise ValueError("V41_INDEPENDENT_ORIGINAL_SOURCE_GROUP_AUDIT_STOP_"+reason)

def bootstrap_original_groups(arr,seed):
    rng=np.random.default_rng(seed)
    boot=arr[rng.integers(0,12,size=(5000,12))].mean(axis=1)
    return np.quantile(boot,[.025,.975]).tolist()

def audit(original):
    if original.get("status")!=STATUS:fail("NOT_SUCCESSFUL_SOURCE_PAPER")
    if original.get("original_EIDC_tracking_files")!=84 or original.get("true_original_biological_shoal_test_fold_count")!=12:
        fail("SOURCE_84_12_SCOPE_DRIFT")
    source=original.get("original_84_true_group_source_provenance",{})
    if (source.get("v40_all_original_12_shoal_G_GLOBAL_NEAR_ROT_REPLAY_PASS") is not True or
        source.get("v40_four_speed_turn_marginals_both_horizons_replayed") is not True):
        fail("PREVIOUS_2021_V33_V40_SOURCE_AND_Y_NOT_REPLAYED")
    mass=source.get("frozen_source_2021_cohort_totals",{})
    if mass!={"native_rows":3147771,"original_eligible_group_times":570360,
              "original_eligible_fish_time_rows":4562880,"dropped_group_times":57968}:
        fail("ORIGINAL_2021_SOURCE_MASS_MISMATCH")
    counts=source.get("n_original_source_4_joint_category_rows",{})
    if set(counts)!=set(CATS) or sum(counts.values())+source.get("n_original_source_turn_undefined_rows",-1)!=4562880:
        fail("JOINT_TURN_PREVIOUS_HEADING_COHORT_DRIFT")
    if original.get("not_independent_from_v40_original_source") is not True or original.get("not_a_randomized_2026_VR_treatment_or_causal_fish_following") is not True:
        fail("CAUSAL_OVERCLAIM_IN_SOURCE_RESULT")
    folds=original.get("source_12_true_shoal_joint_prediction_model_MSE",[])
    if len(folds)!=12 or [f.get("original_biological_shoal_test_ID") for f in folds]!=[str(i) for i in range(1,13)]:
        fail("SOURCE_ORIGINAL_REAL_SHOAL_ID_LIST_CHANGED")
    if sum(f.get("n_source_original_test_recordings",-1) for f in folds)!=84:
        fail("ORIGINAL_84_EXPERIMENTS_INCOMPLETE")
    if any(f.get("original_train_test_true_shoal_overlap") is not False or
           f.get("n_original_training_shoals")!=11 for f in folds):
        fail("ORIGINAL_TRUE_EXPERIMENT_FOLD_LEAKAGE")
    output={
      "status":"V41_INDEPENDENT_POSTV40_2x2_ORIGINAL_12_BIOLOGICAL_SHOAL_NUMERICAL_AUDIT_PASS",
      "original_EIDC_source_DOI":"10.5285/08305a43-79b5-432f-ad20-2ddffe0d1077",
      "source_original_84_trial_files":84,"source_original_12_heldout_biological_shoals":12,
      "source_true_joint_category_counts":counts,
      "source_original_preceding_heading_undefined_focal_rows":source["n_original_source_turn_undefined_rows"],
      "source_original_full_v33_and_marginal_v40_replay":"PASS",
      "new_experiment_or_causal_speed_turn_effect_measured":False,
      "original_fish_XY_velocities_or_individual_audio_republished":False,
      "by_future_horizon":{}
    }
    for hi,h in enumerate(HORIZONS):
        model_source=original["original_joint_speed_and_turn_predictions_by_future_horizon"][h]
        if set(model_source["four_original_joint_test_strata"])!=set(CATS) or set(model_source["speed_and_turn_conditional_outcomes"])!=set(TESTS):
            fail("SOURCE_SCIENTIFIC_CONDITION_NUMBER_CHANGED_"+h)
        vals={cat:{} for cat in CATS}
        for cat in CATS:
            source_cat=model_source["four_original_joint_test_strata"][cat]
            for metric in METRICS:
                per=[]
                for fold in folds:
                    m={mod:fold["joint_category_file_equal_group_MSE"][cat][mod][h] for mod in MODELS}
                    if m["GLOBAL"]<=0 or any(not np.isfinite(z) for z in m.values()):
                        fail("NONFINITE_OR_NONPOSITIVE_ORIGINAL_GLOBAL_MSE")
                    v=((m["GLOBAL"]-m["NEAR_TRUE"]) if metric==METRICS[0]
                      else (m["NEAR_ROT1"]-m["NEAR_TRUE"]))/m["GLOBAL"]
                    per.append(v)
                per=np.asarray(per,dtype=float)
                field=source_cat[metric]
                if abs(np.mean(per)-field["equal_12_original_shoal_MSE_relative_improvement"])>1e-12:
                    fail("ORIGINAL_JOINT_CATEGORY_MEAN_REAGGREGATION")
                if int(np.sum(per>0))!=field["positive_original_shoals"] or int(np.sum(per<0))!=field["negative_original_shoals"]:
                    fail("ORIGINAL_JOINT_CATEGORY_GROUP_SIGN_MISMATCH")
                vals[cat][metric]=per
        tested={}
        for ei,(name,pair) in enumerate(TESTS.items()):
            tested[name]={}
            for mi,metric in enumerate(METRICS):
                if pair is None:
                    arr=(vals["SHIGH_THIGH"][metric]-vals["SHIGH_TLOW"][metric])-(vals["SLOW_THIGH"][metric]-vals["SLOW_TLOW"][metric])
                else:
                    high,low=pair
                    arr=vals[high][metric]-vals[low][metric]
                source_pair=model_source["speed_and_turn_conditional_outcomes"][name][metric]
                if abs(np.mean(arr)-source_pair["equal_original_12_shoal_mean_relative_GAIN_difference"])>1e-12:
                    fail("SPEED_TURN_CROSSED_MARGINAL_CONTRAST_"+name)
                if (int(np.sum(arr>0))!=source_pair["positive_original_shoals"] or
                    int(np.sum(arr<0))!=source_pair["negative_original_shoals"]):
                    fail("CONDITIONAL_OR_INTERACTION_SHOAL_SIGN_"+name)
                seed=20261124+50*hi+10*ei+mi
                interval=bootstrap_original_groups(arr,seed)
                if not np.allclose(interval,source_pair["descriptive_5000_original_group_bootstrap_95pct"],atol=1e-12,rtol=0):
                    fail("SOURCE_FREE_ORIGINAL_GROUP_BOOTSTRAP_MISMATCH_"+name)
                tested[name][metric]={
                    "independently_calculated_mean_percent_points":float(100*np.mean(arr)),
                    "positive_real_original_shoals":int(np.sum(arr>0)),
                    "negative_real_original_shoals":int(np.sum(arr<0)),
                    "independently_calculated_bootstrap_CI95_percent_points":[100*float(v) for v in interval],
                    "original_12_group_signed_percent_points":[100*float(v) for v in arr],
                    "small_absolute_gain_below_fixed_0_1pp":bool(abs(np.mean(arr))<.001)
                }
        output["by_future_horizon"][h]={
          "four_original_speed_turn_cells_percent_prediction_gain":{
              cat:{metric:float(np.mean(vals[cat][metric])*100) for metric in METRICS}
                   for cat in CATS},
          "original_shoal_joint_conditional_deltas":tested
        }
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-result",type=Path,required=True)
    p.add_argument("--audit-out",type=Path,required=True)
    a=p.parse_args()
    raw=a.original_result.read_bytes()
    result=json.loads(raw)
    receipt=audit(result)
    receipt["source_safe_original_model_aggregated_JSON_SHA256"]=hashlib.sha256(raw).hexdigest()
    a.audit_out.parent.mkdir(parents=True,exist_ok=True)
    a.audit_out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({
        "status":receipt["status"],
        "original_sha256":receipt["source_safe_original_model_aggregated_JSON_SHA256"],
        "per_future_original_conditional_deltas":{
             h:{name:{
               metric:round(d["independently_calculated_mean_percent_points"],8)
               for metric,d in contrasts.items()} for name,contrasts in z["original_shoal_joint_conditional_deltas"].items()}
             for h,z in receipt["by_future_horizon"].items()}
    },sort_keys=True))

if __name__=="__main__":main()
