"""v169: 2018-only fitted, 2019 untouched-source-year tidal component ablation.

Real biological question (observational): is the extra RWS Vlieland Haven
tidal block information after the SAME tagged oystercatcher's genuinely
observed previous ACC 15-minute bin attributable to coastal water HEIGHT,
ebb/flood PHASE, their coupling, or NIGHT interactions?

The v168 true cross-year (2018 fit -> full 2019 test) bird-neutral source
membership, original genuine 2018/19 GPS ACC member MD5, 2018/19 RWS
publisher monthly source SHA, prior native-UTC quarterhour correction,
Ridge L2 lambda20, 2019 labels and heldout week/bird loss are ALL pinned.

Freeze stage decomposition BEFORE v169 scores:
 X_H: v168 solar/clock/season + true own prior15 ACC classifier fraction
 PLUS 6 source RWS feature panels (0,3,7,11 days for each):
   HEIGHT: measured harbor stage height
   PHASE: measured rising/falling -1/+1
   HP: height + phase
   HPP: height + phase + height*phase
   HP_NIGHT: height + phase + night*phase + night*height
   FULL: all 5 original v168 RWS feature columns
 Note that subsets differ in dimension, so higher-capacity gains can arise.
 For each panel, compare correct-time RWS vs BEST wrong-date measured
 RWS for same fixed panel. No apparent "phase" as tidal cycle variable
 is equivalent to model error, and +3/7/11 calendar-day shifts are
 sensitivity diagnostics, NOT exchangeable random null replicates.

Score identical original 2019 full-year response / original source hours
using models fitted exclusively on original 2018 Y. Original 2019 previous
quarterhour response is observed at nowcast time; retrospective online
conditional prediction, NOT a prospective entire-2019 forecast.

Pre-specified descriptive source SUBGROUPS evaluated from same trained
year 2018 models (never refit to 2019):
  ALL, DAY, NIGHT, KNOWN_2018_BIRDS, NEW_2019_BIRDS, MONTH_6/7/8/9.
 Same actual 2019 source support within each subgroup across all models.
 No outcome-chosen strata or outcome-dependent source thresholds.
 Strict replay includes original v168 FULL model all-year score equality.

Reference gauge is harbour distance proxy, not actual intertidal exposed
foraging area, prey density, direct tide*sun causation, or Boids social forces.
No independent second coast/cross-taxon pooled p-values.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter
from pathlib import Path
import numpy as np

from v168_true_year_transfer import (
    source_receipts_exact,source_input_and_replay,verified_2019_source,
    corrected_previous_bin,original_features,true_window_y
)
from run_original_2018_matched_week_holdout import ridge_fit_predict,RIDGE_LAMBDA
from bird_tide_after_prev15 import score_grouped

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v168/results/frozen_true_year_transfer_receipt_v168.json"
FULL_OUT=ROOT/"validation_v169/results/original_yearout_tide_ablation_v169.json"
RECEIPT=ROOT/"validation_v169/results/frozen_tide_component_source_receipt_v169.json"
SHIFTS=(0,3,7,11)
TIDE_FEATURE_LABELS=("HEIGHT","PHASE","HEIGHT_X_PHASE","NIGHT_X_PHASE","NIGHT_X_HEIGHT")
TIDE_PANELS={
    "HEIGHT":(0,),
    "PHASE":(1,),
    "HEIGHT_PHASE":(0,1),
    "HEIGHT_PHASE_CROSS":(0,1,2),
    "HEIGHT_PHASE_NIGHT":(0,1,3,4),
    "FULL":(0,1,2,3,4),
}
PANEL_ORDER=tuple(TIDE_PANELS)
N_EXPECTED_TRAIN=157863
N_EXPECTED_TEST=125241
N_EXPECTED_WEEKS=17
N_EXPECTED_TEST_BIRDS=27
N_EXPECTED_SHARED_BIRDS=17
N_BOOT=10000
BOOT_SEED=20261117
MIN_SOURCE_STRATUM_HOURS=1500
MIN_SOURCE_STRATUM_WEEKS=2
NO_NEW_PVALUES=True

def ablation_feature_matrices(common,indices,prev,year,birdorder):
    """Use EXACT original v168 neutral basis and RWS 5-column source block."""
    src=original_features(common,indices,prev,year,birdorder,False)
    base=src["HISTORY"]
    solar=src["SOLAR"]
    if base.shape[1]!=solar.shape[1]+1:
        raise AssertionError("Original prior15 model is no longer nested in solar basis")
    out={"HISTORY":base}
    for shift in SHIFTS:
        full=src["HISTORY_TIDE"+str(shift)]
        p=solar.shape[1]
        if full.shape[1]!=p+6:
            raise AssertionError("v168 tidal source must be exactly five + observed history")
        if not np.allclose(full[:,:p],solar,rtol=0,atol=0):
            raise AssertionError("Historical solar and source tide baseline differ")
        if not np.allclose(full[:,-1],base[:,-1],rtol=0,atol=0):
            raise AssertionError("Historical self ACC state differs by tidal phase")
        tide=full[:,p:p+5]
        if not np.all(np.isfinite(tide)):
            raise AssertionError("Source tidal measurements must be finite")
        if not np.isin(tide[:,1],(-1,1)).all():
            raise AssertionError("Source RWS phase must remain +/-1")
        if not np.allclose(tide[:,2],tide[:,0]*tide[:,1],rtol=0,atol=1e-12):
            raise AssertionError("Original height×phase feature changed")
        if not np.allclose(tide[:,3],solar[:,-1]*tide[:,1],rtol=0,atol=1e-12):
            raise AssertionError("Original night×phase feature changed")
        if not np.allclose(tide[:,4],solar[:,-1]*tide[:,0],rtol=0,atol=1e-12):
            raise AssertionError("Original night×height feature changed")
        for panel,columns in TIDE_PANELS.items():
            name=panel+"_"+str(shift)
            # Order preserved (solar,tide,observed history), matching original
            # v168 FULL input and identical penalization.
            out[name]=(
                full if panel=="FULL" else
                np.column_stack((solar,tide[:,list(columns)],base[:,-1]))
            )
    if len(out)!=1+len(SHIFTS)*len(TIDE_PANELS):
        raise AssertionError("All predeclared tidal stage panels must be complete")
    return out

def score_weekly(y,predictions,week,bird):
    weeks,names,score,source=score_grouped(y,predictions,week,bird)
    means=score.mean(axis=0)
    models={n:float(means[i]) for i,n in enumerate(names)}
    return weeks,names,score,source,models

def model_gains(week_scores,names,original_weeks,
                nboot=N_BOOT,seed=BOOT_SEED):
    idx={m:i for i,m in enumerate(names)}
    if not all(panel+"_"+str(off) in idx for panel in PANEL_ORDER for off in SHIFTS):
        raise AssertionError("Frozen six-panel real and ghost model list incomplete")
    base=week_scores[:,idx["HISTORY"]]
    n=len(original_weeks)
    if n<MIN_SOURCE_STRATUM_WEEKS:
        raise ValueError("Source weeks too few for fixed score")
    overall=week_scores.mean(axis=0)
    means={m:float(overall[idx[m]]) for m in names}
    def calc(mean_rows):
        h=mean_rows[...,idx["HISTORY"]]
        answer={}
        for panel in PANEL_ORDER:
            true=mean_rows[...,idx[panel+"_0"]]
            wrong=np.stack([mean_rows[...,idx[panel+"_"+str(x)]] for x in (3,7,11)],axis=-1)
            bestwrong=np.min(wrong,axis=-1)
            answer[panel]={
                "tide_component_over_own_history":h-true,
                "correct_phase_over_best_wrong_same_component":bestwrong-true
            }
        answer["NESTED"]={
            "add_phase_to_height":mean_rows[...,idx["HEIGHT_0"]]-mean_rows[...,idx["HEIGHT_PHASE_0"]],
            "add_height_to_phase":mean_rows[...,idx["PHASE_0"]]-mean_rows[...,idx["HEIGHT_PHASE_0"]],
            "add_height_times_phase":mean_rows[...,idx["HEIGHT_PHASE_0"]]-mean_rows[...,idx["HEIGHT_PHASE_CROSS_0"]],
            "add_night_interactions_to_height_phase":mean_rows[...,idx["HEIGHT_PHASE_0"]]-mean_rows[...,idx["HEIGHT_PHASE_NIGHT_0"]],
            "add_height_times_phase_after_night_interactions":mean_rows[...,idx["HEIGHT_PHASE_NIGHT_0"]]-mean_rows[...,idx["FULL_0"]],
            "full_minus_height_only":mean_rows[...,idx["HEIGHT_0"]]-mean_rows[...,idx["FULL_0"]],
        }
        return answer
    estimates=calc(overall)
    # Source unit is original individual×week equal-weighted MSE, across
    # all true 2019 ISO weeks. Descriptive original-year only.
    rng=np.random.default_rng(seed)
    samples=rng.integers(0,n,size=(nboot,n))
    means_boot=week_scores[samples,:].mean(axis=1)
    b=calc(means_boot)
    def serialize(original,boots,weekvalues):
        return {
            "mean_MSE_improvement_positive_is_better":round(float(original),9),
            "original_2019_week_positive_n":int((weekvalues>0).sum()),
            "total_2019_original_weeks":int(n),
            "matched_estimand_2019_week_bootstrap_descriptive_95_interval":[
                round(float(x),9) for x in np.quantile(boots,[.025,.975])]
        }
    out={}
    for panel in PANEL_ORDER:
        p=estimates[panel]
        out[panel]={
            "original_2019_true_measured_tide_MSE":round(means[panel+"_0"],9),
            "original_2019_wrong_tide_MSE":{str(x):round(means[panel+"_"+str(x)],9) for x in (3,7,11)},
            "gain_over_source_own_prev15":serialize(
                p["tide_component_over_own_history"],
                b[panel]["tide_component_over_own_history"],
                base-week_scores[:,idx[panel+"_0"]]),
            "correct_vs_best_wrong":serialize(
                p["correct_phase_over_best_wrong_same_component"],
                b[panel]["correct_phase_over_best_wrong_same_component"],
                np.min(np.stack([week_scores[:,idx[panel+"_"+str(x)]] for x in (3,7,11)],axis=1),axis=1)
                  -week_scores[:,idx[panel+"_0"]]),
        }
    nested={}
    for name,original in estimates["NESTED"].items():
        if name=="add_phase_to_height":a,bname="HEIGHT_0","HEIGHT_PHASE_0"
        elif name=="add_height_to_phase":a,bname="PHASE_0","HEIGHT_PHASE_0"
        elif name=="add_height_times_phase":a,bname="HEIGHT_PHASE_0","HEIGHT_PHASE_CROSS_0"
        elif name=="add_night_interactions_to_height_phase":a,bname="HEIGHT_PHASE_0","HEIGHT_PHASE_NIGHT_0"
        elif name=="add_height_times_phase_after_night_interactions":a,bname="HEIGHT_PHASE_NIGHT_0","FULL_0"
        elif name=="full_minus_height_only":a,bname="HEIGHT_0","FULL_0"
        else:raise AssertionError("Unknown predeclared nested contrast")
        nested[name]=serialize(original,b["NESTED"][name],week_scores[:,idx[a]]-week_scores[:,idx[bname]])
    return {"baseline_HISTORY_MSE":round(means["HISTORY"],9),
            "by_component_panel":out,
            "predeclared_nested_component_gains":nested}

def optional_subgroup(y,pred,all_2019_rows,by_week,by_bird,mask,label):
    count=int(mask.sum())
    if count<MIN_SOURCE_STRATUM_HOURS:
        return {"status":"STOP_STRATUM_INSUFFICIENT_RECORDED_QUARTERHOURS",
                "n_original_test_source_bins":count}
    weeks=by_week[mask];nweeks=len(set(weeks))
    if nweeks<MIN_SOURCE_STRATUM_WEEKS:
        return {"status":"STOP_STRATUM_INSUFFICIENT_INDEPENDENT_SOURCE_WEEKS",
                "n_original_test_source_bins":count,"n_weeks":nweeks}
    _,names,score,grouped,model=score_weekly(
        y[mask],{k:v[mask] for k,v in pred.items()},weeks,by_bird[mask])
    effect=model_gains(score,names,np.unique(weeks),nboot=1000,seed=BOOT_SEED)
    # The subgroup intervals are shorter exploratory per-source panels,
    # not 95% independent-species or independent-coast confidence intervals.
    return {"status":"EVALUATED_FIXED_2018_COEFFICIENTS_2019_SUBGROUP",
            "label":label,"n_original_test_source_bins":count,
            "n_original_2019_week_groups":nweeks,
            "source_birdweek_weighting":grouped,
            "baseline_MSE":effect["baseline_HISTORY_MSE"],
            "by_component_panel":effect["by_component_panel"],
            "nested_gains":effect["predeclared_nested_component_gains"]}

def run(v128,v129,v126gps,v126rws,v127):
    ref=json.loads(PRIOR.read_text())
    prior,prior19=source_receipts_exact()
    if (
        ref["source_opportunity"]["genuine_train_2018_prev15_state_windows"]!=N_EXPECTED_TRAIN
        or ref["source_opportunity"]["genuine_full_2019_test_prev15_state_windows"]!=N_EXPECTED_TEST
        or ref["source_opportunity"]["n_original_2019_source_birds"]!=N_EXPECTED_TEST_BIRDS
        or ref["source_opportunity"]["n_same_genuine_tagged_birds_2018_and2019"]!=N_EXPECTED_SHARED_BIRDS
        or ref["panel_bird_neutral"]["status"]!="EVALUATED_2018_FIT_2019_ENTIRE_HELDOUT_YEAR"
        or ref["panel_shared_bird"]["status"]!="STOP_YEAR_TRANSFER_KNOWN_BIRD_SOURCE_GATE"
    ):
        raise AssertionError("Cannot fit v169 without original v168 frozen source/wholeyear result")
    c18,qa18=source_input_and_replay(v128,v129)
    c19,qa19=verified_2019_source(v126gps,v126rws,v127)
    tridx,trprev,diagn18=corrected_previous_bin(c18)
    teidx,teprev,diagn19=corrected_previous_bin(c19)
    if len(c18)!=193088 or len(c19)!=155387 or len(tridx)!=N_EXPECTED_TRAIN or len(teidx)!=N_EXPECTED_TEST:
        raise AssertionError("Original GPS ACC RWS complete source 2018/19 changed")
    train_birds=sorted({e["private_bird"] for e,_,_,_ in c18})
    shared=set(train_birds)
    X18=ablation_feature_matrices(c18,tridx,trprev,2018,train_birds)
    X19=ablation_feature_matrices(c19,teidx,teprev,2019,train_birds)
    response2018=true_window_y(c18,tridx)
    response2019=true_window_y(c19,teidx)
    if any(X18[k].shape[1]!=X19[k].shape[1] for k in X18):
        raise AssertionError("2018-only model feature dimensions cannot transfer to 2019")
    pred={}
    for name in X18:
        pred[name]=ridge_fit_predict(X18[name],response2018,X19[name],lam=RIDGE_LAMBDA)
    weeks=np.asarray([c19[i][3] for i in teidx],dtype=np.int32)
    birdNames=sorted({c19[i][0]["private_bird"] for i in teidx})
    birds={v:i for i,v in enumerate(birdNames)}
    birdlabels=np.asarray([birds[c19[i][0]["private_bird"]] for i in teidx],dtype=np.int32)
    testknown=np.asarray([c19[i][0]["private_bird"] in shared for i in teidx],dtype=bool)
    day=np.asarray([c19[i][1]=="day" for i in teidx],dtype=bool)
    month=np.asarray([c19[i][0]["source_month"] for i in teidx],dtype=np.int8)
    if len(set(weeks))!=N_EXPECTED_WEEKS or int(testknown.sum())!=92248 or int(day.sum())!=81408:
        raise AssertionError("Original v168 test cohort source bird/day/week drift")
    w,names,sc,grouped,model=score_weekly(response2019,pred,weeks,birdlabels)
    if len(w)!=N_EXPECTED_WEEKS:
        raise AssertionError("Original complete 2019 full-year heldout weeks changed")
    # This requires that the original FULL panel's SAME trained 2018 ridge
    # predicts IDENTICAL v168 original 2019 source MSE (not merely sign).
    refLoss=ref["panel_bird_neutral"]["week_bird_equal_out_of_year_MSE"]
    originalParity={
        "2019_original_history_source_loss":model["HISTORY"],
        "2019_original_v168_history_loss":refLoss["HISTORY"],
        "2019_original_full_tide_source_loss":model["FULL_0"],
        "2019_original_v168_full_tide_loss":refLoss["HISTORY_TIDE0"],
        "all_original_three_wrong_full_tide_MSE_match":all(
            abs(model["FULL_"+str(off)]-refLoss["HISTORY_TIDE"+str(off)])<1e-9 for off in (3,7,11)),
    }
    if (abs(model["HISTORY"]-refLoss["HISTORY"])>=1e-9 or
        abs(model["FULL_0"]-refLoss["HISTORY_TIDE0"])>=1e-9 or
        not originalParity["all_original_three_wrong_full_tide_MSE_match"]):
        raise AssertionError("Source v169 ablation does not replay original fixed v168 full model")
    summary=model_gains(sc,names,w)
    allMasks={
        "DAY":day,"NIGHT":~day,
        "BIRDS_SHARED_2018_2019":testknown,
        "BIRDS_NEW_ONLY_2019":~testknown,
        **{"MONTH_"+str(m):month==m for m in (6,7,8,9)}
    }
    strata={label:optional_subgroup(response2019,pred,teidx,weeks,birdlabels,mask,label)
            for label,mask in allMasks.items()}
    return {
        "version":"v169_original_2018_only_fitted_2019_full_source_tide_feature_ablation_1",
        "source_v168_2018_2019_frozen_data_receipt_sha":ref["first_full_original_source_model_SHA256"],
        "genuine_2018_source_bird_GPS_ACC_and_RWS_MD5_responseSHA_replayed":qa18,
        "genuine_2019_source_bird_GPS_ACC_and_RWS_MD5_responseSHA_replayed":qa19,
        "source_2018_original_common_2019_heldout":{
           "original_2018_total_common_quarterhours":len(c18),
           "original_2018_true_prev15_eligible_quarterhours":len(tridx),
           "original_2019_total_common_quarterhours":len(c19),
           "original_2019_true_prev15_eligible_quarterhours":len(teidx),
           "original_2019_full_source_weeks":len(w),
           "original_2019_test_birds":len(birdNames),
           "original_2019_source_bins_day":int(day.sum()),
           "original_2019_source_bins_night":int((~day).sum()),
           "original_2019_source_bins_known_2018_birds":int(testknown.sum()),
           "original_2019_source_bins_new_2019_birds":int((~testknown).sum()),
           "original_2019_source_bins_by_month":dict(sorted(Counter(map(int,month)).items())),
        },
        "frozen_source_design":{
           "target":"ACC 15min classified forage/(forage+inactive) event share, not intake",
           "train_only_year":2018,
           "test_entire_other_year":2019,
           "test_previous_quarterhour_observed_in_test_year":"YES_ONLINE_CONDITIONAL_NOWCAST",
           "bird_ID_effect":"NONE in primary 2018-fit/2019-test design",
           "original_ridge_lambda":RIDGE_LAMBDA,
           "original_tide_shift_calendar_days":list(SHIFTS),
           "five_native_tide_terms_in_original_source_order":list(TIDE_FEATURE_LABELS),
           "fixed_component_panels":{k:list(v) for k,v in TIDE_PANELS.items()},
           "true_and_wrong_RWS_each_PANEL_same_feature_dimensions":True,
           "all_models_same_source_Y_and_hourly_opportunity":True,
           "original_v168_all_seven_full_year_losses_parity_verified":True,
           "descriptive_week_bootstrap":"10000 whole 2019 week vectors main, 1000 for source strata; choose best wrong after within-resample week averages",
           "subgroup_names_fixed_before_new_model_scores":list(allMasks),
           "subgroup_models_never_refitted_on_2019_Y":True,
           "missing_GPS_ACC_not_imputed_as_no_foraging":True,
        },
        "original_v168_model_replay_parity":originalParity,
        "all_original_2019_week_bird_weighted_MSE":{
            k:round(v,9) for k,v in model.items()
        },
        "original_2019_full_year_component_gain_and_same_estimand_bootstrap":summary,
        "source_fixed_daynight_bird_status_months":strata,
        "pvalues_or_independent_coast_effects":"NOT_COMPUTED",
        "local_mudflat_water_depth_prey_access":"NOT_OBSERVED",
        "direct_tide_solar_causation_and_social_Boids_forces":"NOT_IDENTIFIED"
    }

def compact(v):
    canonical=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":v["version"],
        "original_full_source_and_ablation_model_SHA256":hashlib.sha256(canonical.encode()).hexdigest(),
        "reference_v168_initial_SHA":v["source_v168_2018_2019_frozen_data_receipt_sha"],
        "original_source_opportunity":v["source_2018_original_common_2019_heldout"],
        "frozen_design":v["frozen_source_design"],
        "exact_v168_full_model_original_yearout_parity":v["original_v168_model_replay_parity"],
        "original_2019_yearout_all_week_MSE":v["all_original_2019_week_bird_weighted_MSE"],
        "original_2019_component_panels":v["original_2019_full_year_component_gain_and_same_estimand_bootstrap"],
        "source_2019_fixed_day_night_bird_month_subsets":v["source_fixed_daynight_bird_status_months"],
        "original_2018_and_2019_member_and_provider_SHAs_replayed":True,
        "no_global_independent_coast_or_boids_social_effect":True
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("v128","v129","v126-gps","v126-rws","v127"):
        p.add_argument("--"+name,required=True)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    x=p.parse_args()
    v=run(x.v128,x.v129,x.v126_gps,x.v126_rws,x.v127)
    r=compact(v)
    FULL_OUT.parent.mkdir(parents=True,exist_ok=True)
    FULL_OUT.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if x.check:
        if not RECEIPT.is_file():raise AssertionError("Source v169 original source/gains receipt missing")
        old=json.loads(RECEIPT.read_text())
        differences=[]
        def compare(p,a,b):
            if len(differences)>=35:return
            if p=="root.original_full_source_and_ablation_model_SHA256":return
            if isinstance(a,(int,float)) and isinstance(b,(int,float)) and not isinstance(a,bool) and not isinstance(b,bool):
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
        compare("root",old,json.loads(json.dumps(r,sort_keys=True)))
        if differences:
            print("V169_FROZEN_ORIGINAL_ABLATION_REPLAY_DIFFERENCES="+json.dumps(differences[:30],ensure_ascii=True))
            raise AssertionError("Genuine original RWS source or component models changed")
        print("V169_ORIGINAL_2018FIT_2019TEST_TIDE_COMPONENT_SHA_AND_MSE_REPLAY_PASS")
    else:
        print("V169_SOURCE_RECEIPT_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V169_SOURCE_RECEIPT_END")
    print("V169_PUBLIC_COMPONENT_SUMMARY="+json.dumps({
        "source":r["original_source_opportunity"],
        "full":r["original_2019_component_panels"],
        "subgroup_source":{k:{"status":v["status"],"n":v["n_original_test_source_bins"],
                              "baseline":v.get("baseline_MSE")}
             for k,v in r["source_2019_fixed_day_night_bird_month_subsets"].items()}
    },sort_keys=True,ensure_ascii=True))

if __name__=="__main__":
    main()
