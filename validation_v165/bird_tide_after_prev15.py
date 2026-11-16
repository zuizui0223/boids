"""v165 original 2018 Vlieland bird behaviour-state persistence vs real tide.

Biological question: after conditioning on an actually observed previous
15-minute ACC forage/(forage+inactive) classifier-event fraction from the
SAME tagged oystercatcher, does correctly timed measured RWS Vlieland
Haven harbour water level improve the 2018 ISO-whole-week heldout
observed-state CONDITIONAL prediction more than 3/7/11-day wrong tides?

Reuses exact published original v128 source SHA, v129 true 2018 measured
2018 Vlieland RWS hour, v130 SAME 193088 source 15-min bins / 35 birds
/ 17 ISO weeks / 4 months. The only additional source filter: actual
same-individual previous 15-min bin also on the source-complete v130
matched sample, with both bins in the same heldout ISO week. Never impute
missing GPS/ACC or tag data as no-foraging.

History y(t-15m) is OBSERVED within the heldout test week and is used as
a covariate; thus this is an ON-LINE observation-conditioned nowcast, not
a true week-ahead prospective forecast or an animal individual-memory
causal estimator. Comparing whole-week model refit uses fixed folds,
but yprev from the heldout week is used at test time. Keep this explicit.

TIDE is original measured harbour proxy <=25km from GPS, not actual
intertidal patch-level exposure. ACC event fraction is NOT feeding time.
All numerical results exploratory after v127-v130; no individual IDs,
raw GPS points/times or native tide measurements redistributed.
"""
from __future__ import annotations

import argparse,json,hashlib,math
from collections import Counter
from datetime import timedelta
from pathlib import Path
import numpy as np

from original_2019_Vlieland_behaviour_source import _reference_anonymous_identity,SourceStop
from original_Vlieland_2018_ACC_GPS_year_source import (
    immutable_original_manifest,original_bytes,original_GPS_bird_year,
    original_2018_ACC_GPS_source_feasibility,
    ORIGINAL_REFERENCE,ORIGINAL_2018_GPS,ORIGINAL_2019_GPS,ORIGINAL_2018_ACC)
from run_original_2018_vlieland_forage_tide_solar import (
    source_only_replay,bins_2018_exact_v127_schema)
from real_2018_vlieland_RWS_measured import (
    original_2018_vlieland_fourmonth_measured_tide,NativeSourceStop)
from run_original_2018_matched_week_holdout import (
    exact_previous_2018_source_proof,common_matched_source,
    fixed_predictor_matrices,ridge_fit_predict,STAGE_OFFSETS,
    RIDGE_LAMBDA,WEEK_FOLDS,ORIGINAL_V129_RUN
)

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"validation_v165/results/original_bird_tide_after_history_v165.json"
RECEIPT=ROOT/"validation_v165/results/frozen_bird_source_model_receipt_v165.json"
MIN_HISTORY_PAIRS=25000
MIN_TAGGED_BIRDS=20
MIN_ISO_WEEKS=12
MIN_COMMON_MONTHS=4
MIN_WEEKS_PER_TEST_FOLD=2
MIN_DAY_NIGHT_SHARE=.15
MAX_SRC_H=193088
WEEK_BOOT_N=10000
BOOT_SEED=20261116
NAMES=(
    "SOLAR","MEASURED_TIDE0","HISTORY",
    "HISTORY_TIDE0","HISTORY_TIDE3","HISTORY_TIDE7","HISTORY_TIDE11")
GHOSTS=(3,7,11)

def source_actual_previous(common):
    """Source admission uses only original bird/time/week, NEVER response Y."""
    seen={}
    for i,(e,s,_,week) in enumerate(common):
        tag=(e["private_bird"],e["source_utc_event"])
        if tag in seen:
            raise AssertionError("Duplicate original bird×UTC 15-min source bin")
        seen[tag]=i
    current=[];previous=[]
    qa=Counter()
    for i,(e,s,_,week) in enumerate(common):
        p=seen.get((e["private_bird"],e["source_utc_event"]-timedelta(minutes=15)))
        if p is None:
            qa["NO_GENUINE_PREVIOUS_15MIN_BIN"]+=1
            continue
        pe,_,_,pw=common[p]
        if (pw!=week or pe["source_utc_event"].isocalendar().year
                 != e["source_utc_event"].isocalendar().year):
            qa["CROSS_ISO_WEEK_BOUNDARY_REJECTED"]+=1
            continue
        if pe["source_utc_event"]+timedelta(minutes=15)!=e["source_utc_event"]:
            raise AssertionError("Non-adjacent source row treated as previous")
        current.append(i);previous.append(p)
        qa["MATCHED_15MIN_SAME_BIRD_WITHIN_WEEK"]+=1
    if len(current)!=len(previous) or len(set(current))!=len(current):
        raise AssertionError("Original adjacent sample has duplicate current source bins")
    return np.asarray(current,dtype=np.int64),np.asarray(previous,dtype=np.int64),dict(qa)

def source_input_and_replay(v128_file,v129_file):
    prior128=json.loads(Path(v128_file).read_text())
    prior129=json.loads(Path(v129_file).read_text())
    files,_=immutable_original_manifest()
    raw_ref,sha_ref=original_bytes(files[ORIGINAL_REFERENCE])
    ident,qa_ref=_reference_anonymous_identity(raw_ref)
    raw18,sha18=original_bytes(files[ORIGINAL_2018_GPS])
    gps_index,birds18,qa18=original_GPS_bird_year(raw18,2018,ident,True)
    del raw18
    raw19,sha19=original_bytes(files[ORIGINAL_2019_GPS])
    _,birds19,qa19=original_GPS_bird_year(raw19,2019,ident,False)
    del raw19
    original_overlap={
      "original_2018_genuine_GPS_birds":len(birds18),
      "original_2019_genuine_GPS_birds":len(birds19),
      "same_true_tagged_birds_recorded_in_BOTH_2018_and2019_GPS_years":len(birds18&birds19),
      "original_2018_only_tagged_birds":len(birds18-birds19),
      "original_2019_only_tagged_birds":len(birds19-birds18),
      "source_new_2018_year_not_independent_2019_bird_replicates":len(birds18&birds19)>0}
    rawacc,shaacc=original_bytes(files[ORIGINAL_2018_ACC])
    acc,qualified,original_aggregated=original_2018_ACC_GPS_source_feasibility(
        rawacc,ident,gps_index,return_private_quarterhour_bins=True)
    del rawacc,ident,gps_index
    original_source_replay=source_only_replay(
        prior128,qa18,qa19,acc,original_overlap,{
            ORIGINAL_REFERENCE:sha_ref,ORIGINAL_2018_GPS:sha18,
            ORIGINAL_2019_GPS:sha19,ORIGINAL_2018_ACC:shaacc})
    if len(qualified)<8 or not acc["source_frozen_YEAR2018_bird_ge8_15minute_bins_ge1000_eligible"]:
        raise SourceStop("v165 STOP native tagged bird sources failed")
    original_bins,proof=bins_2018_exact_v127_schema(original_aggregated,acc)
    del original_aggregated
    RWS,rwsprovenance=original_2018_vlieland_fourmonth_measured_tide()
    gaugeproof=exact_previous_2018_source_proof(prior129,rwsprovenance)
    common,commonproof=common_matched_source(original_bins,RWS)
    if not commonproof["all_source_gates_pass"] or len(common)!=MAX_SRC_H:
        raise SourceStop("v165 STOP frozen v130 original common-observation source drift")
    return common,{
        "original_source_v128_md5_sha_replayed":original_source_replay,
        "native_2018_RWS_v129_provider_sha_exact_replayed":gaugeproof,
        "original_v130_common_source_gate":commonproof,
        "original_same_birds_2018_2019_overlap":len(birds18&birds19),
        "total_source_bins_before_prev15_gate":len(common),
        "source_expected_bird_RWS_months":[6,7,8,9],
    }

def source_gate(common,idx,prev):
    original_birds={e["private_bird"] for e,_,_,_ in common}
    eligible_birds={common[i][0]["private_bird"] for i in idx}
    weeks={common[i][3] for i in idx}
    months={common[i][0]["source_month"] for i in idx}
    day=sum(common[i][1]=="day" for i in idx)
    night=sum(common[i][1]=="night" for i in idx)
    folds={f:len({common[i][3] for i in idx if common[i][3]%WEEK_FOLDS==f})
           for f in range(WEEK_FOLDS)}
    passes={
        "prev15_true_original_same_bird_pairs_at_least_25000":len(idx)>=MIN_HISTORY_PAIRS,
        "at_least_20_tagged_birds_with_actual_prev15":len(eligible_birds)>=MIN_TAGGED_BIRDS,
        "at_least_12_whole_2018_iso_weeks":len(weeks)>=MIN_ISO_WEEKS,
        "all_four_source_months_present":len(months)>=MIN_COMMON_MONTHS,
        "five_ISO_week_folds_have_at_least_two_weeks":all(x>=MIN_WEEKS_PER_TEST_FOLD for x in folds.values()),
        "both_day_night_source_samples_at_least_15percent":bool(len(idx)) and min(day,night)>=len(idx)*MIN_DAY_NIGHT_SHARE,
    }
    return {
        "source_original_2018_v130_common_rows":len(common),
        "source_true_previous_15min_same_bird_rows":len(idx),
        "source_excluded_due_missing_prev15_or_week_boundary":len(common)-len(idx),
        "source_original_distinct_birds_before_history":len(original_birds),
        "source_distinct_birds_with_true_previous_15min":len(eligible_birds),
        "source_months":sorted(months),
        "source_ISO_week_count":len(weeks),
        "source_qualifying_day_rows":day,"source_qualifying_night_rows":night,
        "source_week_count_by_five_holdout_folds":dict(sorted(folds.items())),
        "passed_source_gates":passes,
        "all_predeclared_source_gates_pass":all(passes.values()),
        "no_response_Y_used_in_previous_source_hour_eligibility":True,
        "observed_prev15_from_same_heldout_week_uses_testweek_state":True,
        "forecast_interpretation":"OBSERVED_STATE_CONDITIONAL_NOWCAST_NOT_PRIOR_WEEK_FORECAST"
    }

def score_grouped(y,preds,weeks,birds):
    names=list(preds)
    ws=np.unique(weeks)
    uu=np.unique(birds)
    birds_n=len(uu)
    wi=np.searchsorted(ws,weeks)
    bi=np.searchsorted(uu,birds)
    labels=wi*birds_n+bi
    n=np.bincount(labels,minlength=len(ws)*birds_n).reshape(len(ws),birds_n)
    nz=n>0
    if not nz.any(axis=1).all():
        raise AssertionError("Original source week empty of all genuine tagged birds")
    scores=np.zeros((len(ws),len(names)),dtype=float)
    for j,name in enumerate(names):
        d=(y-preds[name])**2
        s=np.bincount(labels,weights=d,minlength=len(ws)*birds_n).reshape(len(ws),birds_n)
        obs=np.divide(s,n,out=np.zeros_like(s),where=nz)
        scores[:,j]=obs.sum(axis=1)/nz.sum(axis=1)
    return ws,names,scores,{
        "source_calendar_ISO_weeks_in_scores":len(ws),
        "source_distinct_birds_in_scores":len(uu),
        "source_bird_week_aggregated_outcome_cells":int(nz.sum()),
        "weekly_one_score_each_bird_then_week_equal_weighted":True,
    }

def score_models(common,idx,prev):
    raw_mats,labels=fixed_predictor_matrices(common)
    original_y=np.asarray([
        e["original_acc_forage_events"]/
        (e["original_acc_forage_events"]+e["original_acc_inactive_events"])
        for e,_,_,_ in common],dtype=np.float64)
    if not np.isfinite(original_y).all() or np.min(original_y)<0 or np.max(original_y)>1:
        raise SourceStop("Original ACC classifier event-share value invalid")
    target=original_y[idx]
    history=original_y[prev]
    source_mats={
        "SOLAR":raw_mats["SOLAR"][idx],
        "MEASURED_TIDE0":raw_mats["TIDE-0"][idx],
        "HISTORY":np.column_stack([raw_mats["SOLAR"][idx],history]),
    }
    for offset in STAGE_OFFSETS:
        source_mats["HISTORY_TIDE"+str(offset)]=np.column_stack([raw_mats["TIDE-"+str(offset)][idx],history])
    if set(source_mats)!=set(NAMES) or len({source_mats[n].shape[0] for n in NAMES})!=1:
        raise AssertionError("Original common source rows differ across candidate models")
    if len({source_mats["HISTORY_TIDE"+str(k)].shape[1] for k in STAGE_OFFSETS})!=1:
        raise AssertionError("Tide true and wrong-phase source feature counts differ")
    weeks=labels["source_week"][idx]
    bird_ids=labels["bird_index"][idx]
    folds=weeks%WEEK_FOLDS
    preds={name:np.full(len(idx),np.nan) for name in NAMES}
    for k in range(WEEK_FOLDS):
        train=folds!=k;test=~train
        if min(train.sum(),test.sum())<=0:
            raise SourceStop("Incomplete source week CV fold")
        for name in NAMES:
            preds[name][test]=ridge_fit_predict(source_mats[name][train],target[train],
                                               source_mats[name][test],lam=RIDGE_LAMBDA)
    if any(not np.isfinite(preds[k]).all() for k in NAMES):
        raise SourceStop("One original model has invalid test-week predictions")
    ws,names,score,source=score_grouped(target,preds,weeks,bird_ids)
    mean=score.mean(axis=0)
    scores={k:float(mean[j]) for j,k in enumerate(names)}
    def gain(a,b):return scores[a]-scores[b]
    improvements={
        "solar_to_original_real_tide":gain("SOLAR","MEASURED_TIDE0"),
        "solar_to_observed_previous15m_behavior":gain("SOLAR","HISTORY"),
        "observed_prev15_to_true_tide":gain("HISTORY","HISTORY_TIDE0"),
        "observed_prev15_real_vs_best_wrong_tide":min(scores["HISTORY_TIDE"+str(z)] for z in GHOSTS)-scores["HISTORY_TIDE0"],
        "solar_to_prev15_plus_real_tide":gain("SOLAR","HISTORY_TIDE0"),
    }
    for days in GHOSTS:
        improvements["observed_prev15_wrong_tide_"+str(days)+"day"]=gain("HISTORY","HISTORY_TIDE"+str(days))
    week_actual=score[:,names.index("HISTORY")]-score[:,names.index("HISTORY_TIDE0")]
    week_wrong=np.column_stack([score[:,names.index("HISTORY")]-score[:,names.index("HISTORY_TIDE"+str(z))]
                                for z in GHOSTS])
    week_phase=week_actual-week_wrong.max(axis=1)
    rng=np.random.default_rng(BOOT_SEED)
    sample=rng.integers(0,len(ws),size=(WEEK_BOOT_N,len(ws)))
    d_history=score[:,names.index("SOLAR")]-score[:,names.index("HISTORY")]
    bootstrap={
        "prev15_over_solar":list(map(float,np.quantile(d_history[sample].mean(axis=1),[.025,.975]))),
        "true_tide_after_prev15":list(map(float,np.quantile(week_actual[sample].mean(axis=1),[.025,.975]))),
        "real_tide_after_prev15_vs_best_wrong_day":list(map(float,np.quantile(week_phase[sample].mean(axis=1),[.025,.975]))),
    }
    fold_out={}
    for fold in range(WEEK_FOLDS):
        ids=(ws%WEEK_FOLDS)==fold
        fold_out[str(fold)]={
            "source_whole_weeks":int(ids.sum()),
            "gain_prev15_over_solar":float(d_history[ids].mean()),
            "gain_true_tide_after_prev15":float(week_actual[ids].mean()),
            "gain_real_tide_after_prev15_vs_best_wrong":float(week_phase[ids].mean())
        }
    return {**source,
        "week_bird_equal_heldout_MSE":scores,
        "conditional_observed_prev15_behavior_tide_gains":improvements,
        "conditional_10000_week_score_bootstrap_CI95_NOT_causal":bootstrap,
        "n_week_positive_prev15":int((d_history>0).sum()),
        "n_week_positive_tide_after_prev15":int((week_actual>0).sum()),
        "n_week_positive_correct_tide_over_all_three_wrong":int((week_phase>0).sum()),
        "n_five_source_week_groups":WEEK_FOLDS,
        "fold_grouped_scores":fold_out,
        "model_dimensions":{k:int(source_mats[k].shape[1]) for k in NAMES},
        "same_source_rows_and_original_bird_label_ids_across_models":True,
        "true_tide_is_measured_25km_harbour_proxy_not_intertidal_patch":True,
        "observed_prev15_y_available_in_testweek_ONLINE_nowcast":True,
        "no_animal_tag_id_GPS_hour_or_native_tide_values_exported":True
    }

def run(v128_file,v129_file):
    original,proof=source_input_and_replay(v128_file,v129_file)
    idx,prev,qa=source_actual_previous(original)
    gate=source_gate(original,idx,prev)
    result={
        "version":"v165_original_2018_Vlieland_measured_tide_after_actual_behavior_prev15_1",
        "original_species":"Haematopus ostralegus",
        "data_source":"Zenodo 10053988 corrected O_VLIELAND 2018 GPS and ACC, true RWS vlieland.haven measured tide June–Sep",
        "source_original_v128_v129_v130_replay":proof,
        "new_15min_previous_original_source_eligibility":gate,
        "source_previous_15min_reason_counts":qa,
        "fixed_model_parameters":{
            "year":2018,"week_fold_count":WEEK_FOLDS,
            "real_and_wrong_tide_offsets_days":list(STAGE_OFFSETS),
            "observed_behavior_response":"ACC classified forage events/(forage+inactive events), no true ingestion duration",
            "observed_prev15_covariate":"same tagged bird exactly one observed 15min earlier and same heldout ISO week",
            "week_score":"equal genuine tagged bird mean MSE within each week, then equal original weeks",
            "regularization":"exact v130 raw-source ridge lambda20, same feature sets except observed previous ACC share appended",
            "temporal_transfer":"five whole-ISO-week fold same 2018 birds, not independent population or prior-week forecast",
            "bootstrapping":"fixed 10000 whole original ISO week score rows, seed 20261116, descriptive conditional intervals",
            "response_selected_source":"v127-v130 original results were seen before v165 exploration"
        },
        "source_n_recorded_original_common_bins":len(original),
        "source_n_true_prev15_qualifying_bins":len(idx),
        "source_model_result":score_models(original,idx,prev) if gate["all_predeclared_source_gates_pass"]
                               else {"status":"STOP_SOURCE_PREVIOUS_OR_QUALIFYING_WEEK_SUPPORT"},
        "no_new_independent_coastal_species_population":True,
        "physical_local_tide_x_solar_causal_effect":"NOT_ESTIMATED",
        "actual_intertidal_patch_exposure":"NOT_OBSERVED",
        "real_social_Boids_forces":"NOT_IDENTIFIED",
    }
    return result

def compact(result):
    original=json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":result["version"],
        "canonical_full_source_result_SHA256":hashlib.sha256(original.encode()).hexdigest(),
        "source_n_recorded_original_common_bins":result["source_n_recorded_original_common_bins"],
        "source_n_true_prev15_qualifying_bins":result["source_n_true_prev15_qualifying_bins"],
        "new_source_quality":result["new_15min_previous_original_source_eligibility"],
        "fixed_model_parameters":result["fixed_model_parameters"],
        "source_model_result":result["source_model_result"],
        "original_v128_v129_source_sha_replayed":True,
        "no_global_tide_solar_causation_or_boids_social_effect":True,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--v128-source",required=True)
    parser.add_argument("--v129-original",required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit",action="store_true")
    group.add_argument("--check",action="store_true")
    args=parser.parse_args()
    full=run(args.v128_source,args.v129_original)
    r=compact(full)
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    RESULT.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.exists():
            raise AssertionError("Frozen authentic original bird source model receipt missing")
        frozen=json.loads(RECEIPT.read_text())
        errors=[]
        def compare(path,a,b):
            if len(errors)>=20:return
            if path=="root.canonical_full_source_result_SHA256":return
            if type(a)!=type(b):errors.append([path,"TYPE"])
            elif isinstance(a,dict):
                if set(a)!=set(b):errors.append([path,"KEYS"])
                else:
                    for k in sorted(a):compare(path+"."+str(k),a[k],b[k])
            elif isinstance(a,list):
                if len(a)!=len(b):errors.append([path,"LEN",len(a),len(b)])
                else:
                    for i in range(len(a)):compare(path+"["+str(i)+"]",a[i],b[i])
            elif isinstance(a,float):
                if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-7:
                    errors.append([path,a,b])
            elif a!=b:errors.append([path,a,b])
        compare("root",frozen,json.loads(json.dumps(r,sort_keys=True)))
        if errors:
            print("V165_SOURCE_AND_MODEL_REPLAY_DIFFERENCES="+json.dumps(errors,ensure_ascii=True))
            raise AssertionError("Original source/model numeric v165 results changed")
        print("V165_ORIGINAL_BIRD_PREV15_AND_RWS_PHASE_REPLAY_PASS")
    else:
        print("V165_SOURCE_RECEIPT_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V165_SOURCE_RECEIPT_END")
    print("V165_ORIGINAL_MODEL_SUMMARY="+json.dumps({
        "n_orig":r["source_n_recorded_original_common_bins"],
        "n_prev15":r["source_n_true_prev15_qualifying_bins"],
        "source_pass":r["new_source_quality"]["all_predeclared_source_gates_pass"],
        "models":r["source_model_result"].get("week_bird_equal_heldout_MSE"),
        "improvements":r["source_model_result"].get("conditional_observed_prev15_behavior_tide_gains"),
    },sort_keys=True))

if __name__=="__main__":
    main()
