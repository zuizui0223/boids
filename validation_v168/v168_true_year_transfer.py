"""v168 TRUE frozen-coefficients 2018 train -> all of 2019 held-out year.

Source: genuine MD5/SHA-pinned Zenodo O_VLIELAND corrected GPS+ACC 2018
and 2019 plus genuine Rijkswaterstaat Vlieland Haven measured 10-minute
water heights in both summers. Reuses independently frozen v166 and v167
full-original verified source construction and native true 15-minute window
history; this is not another within-2019 weekly model refit.

Fix BEFORE seeing v168 source year-transfer effects:
  Panel NEUTRAL_ALL: common bird-agnostic feature basis (remove bird OHE
    entirely from BOTH 2018 training and 2019 test), all eligible 2019
    original birds. This can generalize to unseen individuals without
    inventing their 2018 fixed-effect coefficients.
  Panel KNOWN_BIRDS: original v130/v166 ONE-HOT bird fixed-effect design
    frozen to ALL 2018 source birds (one omitted reference), 2019 test
    only true overlapping tagged birds. No new bird effects estimated.
  Optional transparent subset summary of neutral prediction for known
    vs new birds, but only if source-support thresholds pass.

Train ridge ONCE on 2018 genuine observed t and t-15min labels only.
Test 2019 full original source year: all observed Y labels are UNOPENED
during training, but observed PREVIOUS-15min 2019 Y is supplied at
test time. Thus this is a genuine OUT-OF-YEAR *online conditional nowcast*,
NOT a 2018-time prediction of 2019 behavior without 2019 observations.

The correct measured 2019 RWS harbor tide is compared to real measured
2019 tide heights at t+3,+7,+11 calendar days, same 2019 response rows.
The week-level bootstrap here samples full 2019 weekly SCORE VECTORS,
and selects the best wrong phase AFTER the per-resample week means,
matching the reported cross-year point estimand exactly.

No new p-values, full independent field cohort, local tidal exposure,
true feeding success, social Reynolds Boids force, or global causal tide×solar.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter
from datetime import timedelta
from pathlib import Path
import numpy as np

from bird_tide_after_prev15 import source_input_and_replay,score_grouped
from native_quarterhour_lag_tide import corrected_previous_bin
from original_2019_history_tide_replay import verified_2019_source
from run_original_2018_matched_week_holdout import (
    STAGE_OFFSETS,RIDGE_LAMBDA,ridge_fit_predict
)

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"validation_v168/results/frozen_true_year_transfer_receipt_v168.json"
FULL=ROOT/"validation_v168/results/true_2018_fit_2019_heldout_original_v168.json"
V166=ROOT/"validation_v166/results/frozen_corrected_15min_source_receipt_v166.json"
V167=ROOT/"validation_v167/results/frozen_2019_history_tide_receipt_v167.json"
N_SOURCE_YEAR_TRAIN=2018
N_SOURCE_YEAR_TEST=2019
MIN_ALL_TEST=50000
MIN_TRAIN=100000
MIN_COMMON_BIRDS=20
MIN_KNOWN_TEST=30000
MIN_WEEKS=12
MIN_MONTHS=4
MIN_EACH_NIGHT_DAY=.15
BOOT_N=10000
SEED=20261117
MODELS=("SOLAR","TIDE0","HISTORY","HISTORY_TIDE0",
        "HISTORY_TIDE3","HISTORY_TIDE7","HISTORY_TIDE11")
WRONG_DAYS=(3,7,11)
PANELS=("NEUTRAL_ALL","KNOWN_BIRDS")
HISTORY_TIME_STEP=timedelta(minutes=15)

def source_receipts_exact():
    old18=json.loads(V166.read_text())
    old19=json.loads(V167.read_text())
    if (old18["source_actual_previous_bin_gate"]["source_true_previous_15min_same_bird_rows"]!=157863 or
        old18["source_actual_previous_bin_gate"]["all_predeclared_source_gates_pass"] is not True or
        old19["source_true_prev15_real_observations"]!=125241 or
        old19["source_gate"]["all_predeclared_source_gates_pass"] is not True or
        old18["source_scoring_fixed_parameters"]["ridge_lambda_exact_legacy"]!=RIDGE_LAMBDA):
        raise AssertionError("Original source v166/167 verified year cohorts have drifted")
    return old18,old19

def true_window_y(common,rows):
    val=np.asarray([
        common[i][0]["original_acc_forage_events"]/
        (common[i][0]["original_acc_forage_events"]+
         common[i][0]["original_acc_inactive_events"])
        for i in rows
    ],dtype=np.float64)
    if not np.isfinite(val).all() or (val<0).any() or (val>1).any():
        raise AssertionError("Invalid original ACC classifier source response")
    return val

def original_features(common,indices,prev_indices,year,
                      bird_order,include_bird):
    """Bird order is the fixed 2018 TRAINING cohort, never learned from 2019 Y.

    This preserves the original v130 feature transformation exactly for all
    non-bird columns and the original year-2018 one-hot mapping for the
    known bird panel, using original earliest event time for astronomy and
    tide alignment; only source bin ID is reconstructed for lag matching.
    """
    n=len(indices)
    if n!=len(prev_indices):raise AssertionError("Previous native source rows mismatch")
    if n==0:raise ValueError("No actual 15min source observations")
    training_birds={b:i for i,b in enumerate(bird_order)}
    rows=[common[i] for i in indices]
    if any(e["source_utc_event"].year!=year for e,_,_,_ in rows):
        raise AssertionError("Leaked calendar year outside original source")
    month=np.asarray([e["source_month"] for e,_,_,_ in rows],dtype=np.int16)
    if not np.isin(month,[6,7,8,9]).all():
        raise AssertionError("Nonfrozen months in source")
    night=np.asarray([float(s=="night") for e,s,_,_ in rows])
    if any(s not in ("day","night") for e,s,_,_ in rows):
        raise AssertionError("Source twilight/non-finite solar category not excluded")
    ts=[e["source_utc_event"] for e,_,_,_ in rows]
    hour=np.asarray([t.hour+t.minute/60+t.second/3600 for t in ts],dtype=np.float64)
    day=np.asarray([t.day for t in ts],dtype=np.float64)
    terms=[np.ones(n,dtype=np.float64)]
    if include_bird:
        bidx=np.asarray([training_birds.get(e["private_bird"],-1)
                         for e,_,_,_ in rows],dtype=np.int32)
        if (bidx<0).any():
            raise AssertionError("Cannot apply frozen known-bird effect to unseen 2019 tagged bird")
        # 2018 v130: one reference bird omitted; columns fixed by 2018 original cohort
        terms.extend((bidx==j).astype(np.float64) for j in range(1,len(bird_order)))
    terms.extend((month==m).astype(np.float64) for m in (7,8,9))
    terms.extend(v for k in (1,2,3) for v in (
        np.sin(2*math.pi*k*hour/24),np.cos(2*math.pi*k*hour/24)))
    terms.append((day-15.5)/15.0)
    Xclock=np.column_stack(terms)
    Xsolar=np.column_stack((Xclock,night))
    history=true_window_y(common,prev_indices)
    cov={"SOLAR":Xsolar,"HISTORY":np.column_stack((Xsolar,history))}
    for pos,off in enumerate(STAGE_OFFSETS):
        stage=np.asarray([matches[pos][0] for e,s,matches,w in rows])
        phase=np.asarray([matches[pos][1] for e,s,matches,w in rows])
        if not np.isfinite(stage).all() or not np.isin(phase,[-1,1]).all():
            raise AssertionError("Original observed RWS source harbor stage or phase invalid")
        tide=np.column_stack((stage,phase,stage*phase,night*phase,night*stage))
        if off==0:
            cov["TIDE0"]=np.column_stack((Xsolar,tide))
        cov["HISTORY_TIDE"+str(off)]=np.column_stack((Xsolar,tide,history))
    if set(cov)!=set(MODELS):
        raise AssertionError("Frozen year-transfer feature families not complete")
    if any(x.shape[0]!=n or not np.isfinite(x).all() for x in cov.values()):
        raise AssertionError("Nonfinite/unequal original source feature support")
    k=sorted(set(cov[n].shape[1] for n in MODELS if n.startswith("HISTORY_TIDE")))
    if len(k)!=1:
        raise AssertionError("Correct/wrong tidal phase original feature dimensions differ")
    return cov

def year_panel_score(train_common,train_idx,train_prev,
                     test_common,test_idx,test_prev,
                     bird_order,include_bird,panel):
    tr=original_features(train_common,train_idx,train_prev,2018,bird_order,include_bird)
    te=original_features(test_common,test_idx,test_prev,2019,bird_order,include_bird)
    yt=true_window_y(train_common,train_idx)
    y=true_window_y(test_common,test_idx)
    if len(yt)<MIN_TRAIN or len(y)<MIN_KNOWN_TEST:
        return {"status":"STOP_SOURCE_TRAIN_OR_TEST_OPPORTUNITY"}
    if any(tr[m].shape[1]!=te[m].shape[1] for m in MODELS):
        raise AssertionError("Nonmatching frozen feature basis between 2018 train and 2019 test")
    preds={}
    for m in MODELS:
        preds[m]=ridge_fit_predict(tr[m],yt,te[m],lam=RIDGE_LAMBDA)
    weeks=np.asarray([test_common[i][3] for i in test_idx],dtype=np.int32)
    bird_to_ix={b:j for j,b in enumerate(sorted(
        {test_common[i][0]["private_bird"] for i in test_idx}))}
    birds=np.asarray([bird_to_ix[test_common[i][0]["private_bird"]]
                      for i in test_idx],dtype=np.int32)
    wholeweek,names,weekMSE,grouped=score_grouped(y,preds,weeks,birds)
    if names!=list(MODELS):
        raise AssertionError("Predictor score name order changed")
    means=weekMSE.mean(axis=0)
    overall={n:float(means[j]) for j,n in enumerate(names)}
    def gain(a,b):return overall[a]-overall[b]
    wrong_scores=[overall["HISTORY_TIDE"+str(d)] for d in WRONG_DAYS]
    point={
        "previous_15min_state_over_solar":gain("SOLAR","HISTORY"),
        "correct_tide_over_solar":gain("SOLAR","TIDE0"),
        "correct_tide_after_actual_previous_state":gain("HISTORY","HISTORY_TIDE0"),
        "correct_real_tide_over_globally_best_wrong_phase_after_prev":
            min(wrong_scores)-overall["HISTORY_TIDE0"]
    }
    for shift in WRONG_DAYS:
        point["wrong_tide_"+str(shift)+"d_after_prev_state"]=gain(
            "HISTORY","HISTORY_TIDE"+str(shift))
    pidx={k:names.index(k) for k in names}
    history_week=weekMSE[:,pidx["SOLAR"]]-weekMSE[:,pidx["HISTORY"]]
    tidal_week=weekMSE[:,pidx["HISTORY"]]-weekMSE[:,pidx["HISTORY_TIDE0"]]
    phase_week=np.min(np.column_stack([
        weekMSE[:,pidx["HISTORY_TIDE"+str(shift)]] for shift in WRONG_DAYS]),axis=1)-weekMSE[:,pidx["HISTORY_TIDE0"]]
    # Exact **matched** statistic: resample whole week vectors, average all
    # models over sampled weeks, THEN choose best global wrong-date MSE.
    rng=np.random.default_rng(SEED)
    sample=rng.integers(0,len(wholeweek),size=(BOOT_N,len(wholeweek)))
    bm=weekMSE[sample].mean(axis=1)
    bh=bm[:,pidx["SOLAR"]]-bm[:,pidx["HISTORY"]]
    bt=bm[:,pidx["HISTORY"]]-bm[:,pidx["HISTORY_TIDE0"]]
    bp=np.min(np.column_stack([
        bm[:,pidx["HISTORY_TIDE"+str(shift)]] for shift in WRONG_DAYS]),axis=1)-bm[:,pidx["HISTORY_TIDE0"]]
    boot={
       "previous_15min_state_over_solar":[float(q) for q in np.quantile(bh,[.025,.975])],
       "correct_tide_after_actual_previous_state":[float(q) for q in np.quantile(bt,[.025,.975])],
       "correct_tide_over_globally_best_wrong_phase_after_prev":[float(q) for q in np.quantile(bp,[.025,.975])],
    }
    source_week_summary={
        str(int(w)):{
            "observed_tagged_birds_in_week":int(
                len({test_common[i][0]["private_bird"] for i in test_idx if test_common[i][3]==w})),
            "previous_state_gain":float(history_week[j]),
            "measured_tide_gain_after_prev":float(tidal_week[j]),
            "correct_tide_vs_each_week_best_wrong":float(phase_week[j])
        } for j,w in enumerate(wholeweek)
    }
    return {
        "status":"EVALUATED_2018_FIT_2019_ENTIRE_HELDOUT_YEAR",
        "model":"same 2018 original ridge coefficients, no 2019 Y in training",
        "panel":panel,
        "observed_current_source_bins_2019":len(test_idx),
        "observed_training_source_bins_2018":len(train_idx),
        "n_2019_test_original_week_rows":len(wholeweek),
        "n_2019_test_tagged_birds":len(bird_to_ix),
        "n_train_2018_tagged_birds_with_identity_basis":len(bird_order),
        "training_model_bird_identity_columns":bool(include_bird),
        "train_year_only_source_Y":2018,
        "heldout_year_source_Y":2019,
        "2019_observed_previous_quarterhour_Y_explanatory_input":True,
        "week_bird_equal_out_of_year_MSE":overall,
        "2018_fitted_2019_scores_gain_MSE":point,
        "source_week_positive_gains":{
            "previous_state":int((history_week>0).sum()),
            "measured_tide_after_previous":int((tidal_week>0).sum()),
            "correct_tide_vs_all_wrong_phase":int((phase_week>0).sum())
        },
        "descriptive_2019_week_bootstrap_CI95_of_EXACT_reported_global_best_wrong_phase_statistic":boot,
        "n_bootstrap_full_2019_week_vector_resamples":BOOT_N,
        "2019_week_by_week_aggregate_source_scores":source_week_summary,
        "source_bird_week_weighting":grouped,
        "all_models_same_original_2019_outcome_and_available_source":True,
        "no_real_2019_heldout_Y_used_in_fitting":True,
        "not_a_true_without_2019_prior_history_future_year_prediction":True
    }

def run(v128,v129,v126gps,v126rws,v127):
    old18,old19=source_receipts_exact()
    train,src18=source_input_and_replay(v128,v129)
    test,src19=verified_2019_source(v126gps,v126rws,v127)
    if len(train)!=193088 or len(test)!=155387:
        raise AssertionError("2018 original or 2019 original source common rows drift")
    tridx,trprev,qa18=corrected_previous_bin(train)
    teidx,teprev,qa19=corrected_previous_bin(test)
    if len(tridx)!=157863 or len(teidx)!=125241:
        raise AssertionError("Original source native 15min previous window count changed")
    train_birds=sorted({e["private_bird"] for e,_,_,_ in train})
    test_birds=sorted({e["private_bird"] for e,_,_,_ in test})
    shared=set(train_birds)&set(test_birds)
    known_rows=np.asarray([j for j,i in enumerate(teidx) if test[i][0]["private_bird"] in shared],dtype=np.int64)
    knownidx=teidx[known_rows];knownprev=teprev[known_rows]
    only_new=len(teidx)-len(knownidx)
    test_week_counts=Counter(test[i][3] for i in teidx)
    test_month_counts=Counter(test[i][0]["source_month"] for i in teidx)
    test_days=sum(test[i][1]=="day" for i in teidx)
    test_nights=len(teidx)-test_days
    shared_test_birds=len({test[i][0]["private_bird"] for i in knownidx})
    source_gate={
       "n_original_2018_common_bins":len(train),
       "n_original_2019_common_bins":len(test),
       "genuine_train_2018_prev15_state_windows":len(tridx),
       "genuine_full_2019_test_prev15_state_windows":len(teidx),
       "n_original_2018_source_birds":len(train_birds),
       "n_original_2019_source_birds":len(test_birds),
       "n_same_genuine_tagged_birds_2018_and2019":len(shared),
       "2019_test_source_bins_in_known_2018_tagged_birds":len(knownidx),
       "2019_test_source_bins_in_new_birds_not_in_2018_train":only_new,
       "2019_2018_overlap_birds_with_valid_prev15_windows":shared_test_birds,
       "source_2019_test_months":sorted(test_month_counts),
       "source_2019_test_ISO_week_n":len(test_week_counts),
       "source_2019_test_quarterhours_day":test_days,
       "source_2019_test_quarterhours_night":test_nights,
       "source_gate_neutral_ALL":{
           "real_2018_training_prev15_n_ge100k":len(tridx)>=MIN_TRAIN,
           "real_2019_test_prev15_n_ge50k":len(teidx)>=MIN_ALL_TEST,
           "2019_source_weeks_ge12":len(test_week_counts)>=MIN_WEEKS,
           "2019_original_months_all_four":len(test_month_counts)>=MIN_MONTHS,
           "2019_true_source_night_and_day_share_ge15pct":min(test_days,test_nights)>=MIN_EACH_NIGHT_DAY*len(teidx)
       },
       "source_gate_known_BIRDS":{
           "known_tagged_bird_ids_ge20":shared_test_birds>=MIN_COMMON_BIRDS,
           "known_2019_actual_previous_windows_ge30k":len(knownidx)>=MIN_KNOWN_TEST,
           "train_2018_original_bird_identity_frozen_no_target_year_fit":True,
       },
       "source_only_selected_known_birds_by_original_identity_not_outcome_Y":True,
       "common_source_year_2018_and2019_overlap_not_independent_populations":True
    }
    can_neutral=all(source_gate["source_gate_neutral_ALL"].values())
    can_known=can_neutral and all(source_gate["source_gate_known_BIRDS"].values())
    panel_neutral=year_panel_score(
        train,tridx,trprev,test,teidx,teprev,train_birds,False,"NEUTRAL_ALL") if can_neutral else
        {"status":"STOP_YEAR_TRANSFER_NEUTRAL_SOURCE_GATE"}
    panel_known=year_panel_score(
        train,tridx,trprev,test,knownidx,knownprev,train_birds,True,"KNOWN_BIRDS") if can_known else
        {"status":"STOP_YEAR_TRANSFER_KNOWN_BIRD_SOURCE_GATE"}
    if can_neutral and panel_neutral.get("status")!="EVALUATED_2018_FIT_2019_ENTIRE_HELDOUT_YEAR":
        raise AssertionError("Source-admitted neutral model failed unexpectedly")
    return {
        "version":"v168_true_2018_only_fitted_2019_entire_holdout_oystercatcher_1",
        "source_v166_2018_verified_full_GPS_ACC_RWS_member_and_provider_SHA":src18,
        "source_v167_2019_verified_full_GPS_ACC_RWS_member_and_provider_SHA":src19,
        "source_2018_native_quarterhour_clock_QA":qa18,
        "source_2019_native_quarterhour_clock_QA":qa19,
        "source_only_year_transfer_opportunity":source_gate,
        "freeze_prior_models_and_original_year_facts":{
            "year2018_frozen_source_sha":old18["first_run_canonical_full_source_original_model_SHA256"],
            "year2019_frozen_source_sha":old19["original_full_result_first_sha256"],
            "training_source_calendar_year":2018,
            "testing_only_full_source_calendar_year":2019,
            "reference_bird_source_order":"sorted 2018 genuine source birds only",
            "main_generalized_feature_basis":"2018 bird-neutral months/UTC hour sin-cos k1-3/day/night/observed real RWS tide+own real previous quarterhour",
            "known_bird_panel_feature_basis":"2018 original complete list frozen bird dummy coefficients; 2019 shared known bird only",
            "2018_original_Ridge_L2_lambda":RIDGE_LAMBDA,
            "observed_tide_shift_source_days":[0,*WRONG_DAYS],
            "all_model_Y":"ACC classifier forage/(forage+inactive) within genuine GPS source quarterhour",
            "2019_test_week_own_previous_Y_supplied":"ONLINE_CONDITIONAL_NOWCAST_NOT_STANDALONE_YEAR_AHEAD",
            "all_2019_current_source_Y_UNOPENED_for_training":True,
            "model_selected_hyperparams_or_source_thresholds_based_on_2019_Y":False
        },
        "primary_bird_agnostic_2018fit_2019test":panel_neutral,
        "secondary_common_tagged_birds_fixed_2018_effect_2019test":panel_known,
        "original_2019_test_year_model_retrained_on_2019_Y":False,
        "n_independent_coasts_added":0,
        "causal_local_tide_by_sun_effect":"NOT_ESTIMATED",
        "social_Boids_forces":"NOT_IDENTIFIED"
    }

def receipt(v):
    canonical=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
       "version":v["version"],
       "first_full_original_source_model_SHA256":hashlib.sha256(canonical.encode()).hexdigest(),
       "source_opportunity":v["source_only_year_transfer_opportunity"],
       "frozen_comparison_design":v["freeze_prior_models_and_original_year_facts"],
       "panel_bird_neutral":v["primary_bird_agnostic_2018fit_2019test"],
       "panel_shared_bird":v["secondary_common_tagged_birds_fixed_2018_effect_2019test"],
       "both_original_years_source_member_and_gauge_SHA_verified":True,
       "no_2019_Y_in_fit":True,
       "true_independent_coast_or_global_biological_effect":"NOT_ESTIMATED"
    }

def main():
    parser=argparse.ArgumentParser()
    for name in ("v128","v129","v126-gps","v126-rws","v127"):
        parser.add_argument("--"+name,required=True)
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    x=parser.parse_args()
    v=run(x.v128,x.v129,x.v126_gps,x.v126_rws,x.v127)
    r=receipt(v)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(v,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if x.check:
        if not RECEIPT.exists():raise AssertionError("No frozen 2018-2019 true-year transfer original result")
        frozen=json.loads(RECEIPT.read_text())
        differences=[]
        def compare(p,a,b):
            if len(differences)>=40:return
            if p=="root.first_full_original_source_model_SHA256":return
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
        compare("root",frozen,json.loads(json.dumps(r,sort_keys=True)))
        if differences:
            print("V168_SOURCE_TRANSFER_MODEL_REPLAY_DIFFERENCES="+json.dumps(differences[:35],ensure_ascii=True))
            raise AssertionError("Genuine original GPS+ACC RWS year-transfer SOURCE/model replay failed")
        print("V168_ORIGINAL_FROZEN_2018_TRAIN_2019_FULLYEAR_TEST_SOURCE_REPLAY_PASS")
    else:
        print("V168_SOURCE_RECEIPT_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V168_SOURCE_RECEIPT_END")
    def short(z):
        return {
           "status":z.get("status"),"test_source_n":z.get("observed_current_source_bins_2019"),
           "n_birds":z.get("n_2019_test_tagged_birds"),
           "MSE":z.get("week_bird_equal_out_of_year_MSE"),
           "gains":z.get("2018_fitted_2019_scores_gain_MSE"),
           "CI":z.get("descriptive_2019_week_bootstrap_CI95_of_EXACT_reported_global_best_wrong_phase_statistic"),
           "week_positive":z.get("source_week_positive_gains"),
        }
    print("V168_PUBLIC_YEAR_TRANSFER_SUMMARY="+json.dumps({
        "source":r["source_opportunity"],
        "neutral":short(r["panel_bird_neutral"]),
        "known":short(r["panel_shared_bird"])
    },sort_keys=True,ensure_ascii=True))

if __name__=="__main__":
    main()
