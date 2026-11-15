"""v155: own-state persistence vs same-hour acoustic partner and day-shift ghost.

Exploratory from SAME 2018-23 original California fish chorus source, AFTER
v145-v154 results. This is an observed heldout-year *conditional association*
task, not a new field population, and not fish social causation.

Data: exact v145 complete original local 24h days (9 sites; 275 runs;
136032 original source recorder hours) from all 60 checksum-pinned Dryad
workbooks; NOAA original 14 station×year body SHA replay via v154 helper.

New common feature support drops only the very FIRST hour of each original
contiguous 7+-day month run so previous A=1h is genuinely observed.
Do not cross missing or DST hours. Evaluate same source Y/hours across all
models. Same-hour B and day-cycled B ghosts are *test-year observed features*,
so these are retrospective conditional classifications, not actionable
prospective predictions or proof of individual interaction.

Ghost B+3,+5 complete local 24h day series preserve recorded diel hour,
source year/month, and B call bouts; wrap within each original 7+-day run,
so source-day seam still exists. No statistical p value.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter,defaultdict
from datetime import timedelta
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for p in ("validation_v144","validation_v145","validation_v154"):
    sys.path.insert(0,str(ROOT/p))
from v145_blockshift import eligible_complete_days,contiguous_runs
from full9_temporal import local_time
from v154_year_holdout import (
    merge_sources,solar_clock_features,tide_proxy_features,
    model_predictions,loss,brier,
    MIN_TRAIN_HOURS,MIN_TEST_HOURS,MIN_TRAIN_TARGET_POS,
    MIN_TEST_TARGET_POS,MIN_TRAIN_PARTNER_POS,MIN_TEST_PARTNER_POS,
    MIN_POSITIVE_AND_NEGATIVE,Y_CLIP,ALPHA_C,MAX_ITER,TARGET,PAIRS
)

PRIOR=ROOT/"validation_v154/results/frozen_source_model_receipt_v154.json"
V145=ROOT/"validation_v145/results/source_blockshift_cochorus_null.json"
RECEIPT=ROOT/"validation_v155/results/frozen_source_receipt_v155.json"
FULL=ROOT/"validation_v155/results/source_partner_autostate_full_v155.json"
GHOST_DAY_SHIFTS=(3,5)
MODELS=("constant","solar","tide","own_prev","partner_real",
        "partner_ghost3d","partner_ghost5d")
MIN_FRACTION_LAG_AND_TIDE=.995  # expected only 275 run-start exclusions in 136032
SOURCE_RUN_STARTS_EXPECTED=275

def run_rows(fulldays,positive_by_type):
    """Only source-real preceding-hour A; every B ghost is same month/run.

    full days are tuples of exactly 24 source-hour indices in ORIGINAL local
    clock order, already split by same-yearmonth v145 contiguous run.
    """
    n=len(fulldays)
    if n<7 or any(len(day)!=24 for day in fulldays):
        raise AssertionError("Frozen seven-plus-day original source run required")
    A=positive_by_type.get(TARGET,set())
    ps={p:positive_by_type.get(p,set()) for p in PAIRS}
    for i,day in enumerate(fulldays):
        for hour_of_day,h in enumerate(day):
            if i==0 and hour_of_day==0:
                continue
            prev=day[hour_of_day-1] if hour_of_day else fulldays[i-1][23]
            if prev!=h-1:
                raise AssertionError("Original source previous acoustic observation not continuous")
            y=int(h in A)
            lag=int(prev in A)
            actual={p:int(h in ps[p]) for p in PAIRS}
            ghosts={p:{
                shift:int(fulldays[(i+shift)%n][hour_of_day] in ps[p])
                for shift in GHOST_DAY_SHIFTS
            } for p in PAIRS}
            yield h,y,lag,actual,ghosts

def score_pair(features,y,partner,local_years,holdout):
    """Fixed source gate and strict earlier local years; no model tuning."""
    years=np.asarray(local_years,dtype=np.int32)
    tr=(years<holdout);te=(years==holdout)
    y=np.asarray(y,dtype=np.int8)
    partner=np.asarray(partner,dtype=np.int8)
    ntr=int(tr.sum());nte=int(te.sum())
    qual={
        "train_hours":ntr,"heldout_hours":nte,
        "train_target_positive":int(y[tr].sum()),"heldout_target_positive":int(y[te].sum()),
        "train_partner_positive":int(partner[tr].sum()),"heldout_partner_positive":int(partner[te].sum())
    }
    if ntr<MIN_TRAIN_HOURS or nte<MIN_TEST_HOURS:
        return {"status":"STOP_SOURCE_LAG_HOURS",**qual}
    if (
        qual["train_target_positive"]<MIN_TRAIN_TARGET_POS
        or qual["heldout_target_positive"]<MIN_TEST_TARGET_POS
        or qual["train_partner_positive"]<MIN_TRAIN_PARTNER_POS
        or qual["heldout_partner_positive"]<MIN_TEST_PARTNER_POS
        or min(ntr-qual["train_target_positive"],nte-qual["heldout_target_positive"],
               ntr-qual["train_partner_positive"],nte-qual["heldout_partner_positive"])
               <MIN_POSITIVE_AND_NEGATIVE
    ):
        return {"status":"STOP_SOURCE_LAG_POSITIVE_NEGATIVE",**qual}
    pred={"constant":np.full(nte,float(y[tr].mean()))}
    for model in MODELS:
        if model=="constant":continue
        x=features[model]
        pred[model]=model_predictions(x[tr],x[te],y[tr])
    l={k:loss(y[te],pred[k]) for k in MODELS}
    b={k:brier(y[te],pred[k]) for k in MODELS}
    def r(v):return round(float(v),8)
    improvements={
        "solar_over_constant":r(l["constant"]-l["solar"]),
        "tide_over_solar":r(l["solar"]-l["tide"]),
        "own_previous_1h_over_tide":r(l["tide"]-l["own_prev"]),
        "real_partner_over_own_previous":r(l["own_prev"]-l["partner_real"]),
        "wrong_partner_3d_over_own_previous":r(l["own_prev"]-l["partner_ghost3d"]),
        "wrong_partner_5d_over_own_previous":r(l["own_prev"]-l["partner_ghost5d"]),
        "real_partner_over_best_dayghost":r(
            min(l["partner_ghost3d"],l["partner_ghost5d"])-l["partner_real"]),
        "real_partner_over_constant":r(l["constant"]-l["partner_real"]),
    }
    return {
        "status":"EVALUATED_PRIOR_COASTAL_SOURCE_YEAR",
        **qual,
        "heldout_logloss_nats_per_hour":{k:r(v) for k,v in l.items()},
        "heldout_brier":{k:r(v) for k,v in b.items()},
        "improvement_nats_per_original_hour":improvements,
        "same_test_target_and_source_hours_across_models":True,
    }

def summarize(gated):
    if not gated:
        return {"n_cohorts":0,"n_sites":0,"status":"NOT_ESTIMATED"}
    keys=list(gated[0]["improvement_nats_per_original_hour"])
    by_site=defaultdict(list)
    for x in gated:by_site[x["site"]].append(x)
    def avg(vals):return round(float(np.mean(vals)),8)
    equal_cohort={key:{
        "mean_gain":avg([z["improvement_nats_per_original_hour"][key] for z in gated]),
        "positive_cohorts":sum(z["improvement_nats_per_original_hour"][key]>0 for z in gated),
        "negative_cohorts":sum(z["improvement_nats_per_original_hour"][key]<0 for z in gated)
    } for key in keys}
    per_site=[{
        "site":site,"n_holdout_years":len(xx),
        "mean_gain_by_endpoint":{
            key:avg([z["improvement_nats_per_original_hour"][key] for z in xx])
            for key in keys
        }
    } for site,xx in sorted(by_site.items())]
    equal_site={
        key:{"mean_gain":avg([z["mean_gain_by_endpoint"][key] for z in per_site]),
             "positive_sites":sum(z["mean_gain_by_endpoint"][key]>0 for z in per_site)}
        for key in keys
    }
    # Every site is a correlated field group, and exclusion is exploratory.
    lose_one={
        key:[{"excluded_site":z["site"],
              "remaining_equal_site_mean":avg([
                  other["mean_gain_by_endpoint"][key]
                  for other in per_site if other["site"]!=z["site"]
              ]) if len(per_site)>1 else None}
             for z in per_site]
        for key in ("real_partner_over_own_previous",
                    "real_partner_over_best_dayghost")
    }
    return {
        "n_cohorts":len(gated),"n_sites":len(per_site),
        "equal_siteyear":equal_cohort,
        "equal_source_site":equal_site,
        "per_site":per_site,
        "leave_one_site_out_exploratory":lose_one,
        "independent_study_count":1,
        "p_values_computed":False,
    }

def estimate():
    # Real fish+NOAA providers and previous 14-year source hashes are checked
    # BEFORE any new feature or acoustic behavior effect is assessed.
    planned,gauge,source_qc,original,frozen=merge_sources()
    old=json.loads(PRIOR.read_text())
    source_v145=json.loads(V145.read_text())
    if not (old["n_source_original_hours"]==136032
            and old["n_evaluated_original_holdout_siteyear_partner_contrasts"]==21
            and source_v145["screened_site_pairs"]==32):
        raise AssertionError("Frozen v145/v154 source study scope changed")
    previously_admitted={(z["site"],z["test_local_year"],z["partner"])
                         for z in old["all_evaluated_group_scores_and_source_support"]}
    if len(previously_admitted)!=21:
        raise AssertionError("Prior v154 model source cohorts must be distinct")
    site_quality=[];results=[]
    source_original_total=0;runstart_total=0;new_source_total=0
    for site,item in sorted(planned.items()):
        station=item["reference_station_id"]
        original_hours=item["site_source_hours"]
        source_original_total+=len(original_hours)
        record=original[site]
        source_day_map=eligible_complete_days(record["nominal"]-record["off"]-record["noise"])
        runs=contiguous_runs(source_day_map)
        if len(runs)!=item["source_yearmonth_7dplus_runs"]:
            raise AssertionError("Original same 7+ day source run count changed")
        target_pos=record["fish"]
        src=[]
        for run in runs:
            full_days=[source_day_map[d] for d in run]
            src.extend(run_rows(full_days,target_pos))
        runstart_total+=len(runs)
        new_source_total+=len(src)
        assert len(src)==len(original_hours)-len(runs)
        assert {x[0] for x in src}.issubset(original_hours)
        total_n=len(src)
        audio=np.asarray([q[1] for q in src],dtype=np.int8)
        ownprev=np.asarray([q[2] for q in src],dtype=np.float64)
        years=np.asarray([local_time(q[0]).year for q in src],dtype=np.int32)
        xbase=np.asarray([solar_clock_features(q[0],site) for q in src],dtype=np.float64)
        tide=np.asarray([tide_proxy_features(gauge,station,q[0],0,float(xbase[i,-1]))
                          for i,q in enumerate(src)],dtype=np.float64)
        if tide.shape!=(total_n,5) or not np.isfinite(tide).all():
            raise AssertionError("Missing original NOAA verified gauge for common shifted-source support")
        base_tide=np.column_stack([xbase,tide])
        baseline_own=np.column_stack([base_tide,ownprev])
        site_quality.append({
            "site":site,"source_original_frozen_24h_hours":len(original_hours),
            "source_7day_yearmonth_runs":len(runs),
            "dropped_only_first_source_hour_per_run":len(runs),
            "source_hourly_previous_observation_and_NOAA_valid":total_n,
            "retained_fraction":round(total_n/len(original_hours),8),
            "local_years":sorted(set(years.tolist())),
            "gauge_distance_km":item["geodesic_station_distance_km"],
            "source_provider_body_SHA_checks":True,
        })
        for partner in PAIRS:
            b0=np.asarray([q[3][partner] for q in src],dtype=np.float64)
            b3=np.asarray([q[4][partner][3] for q in src],dtype=np.float64)
            b5=np.asarray([q[4][partner][5] for q in src],dtype=np.float64)
            features={
                "solar":xbase,
                "tide":base_tide,
                "own_prev":baseline_own,
                "partner_real":np.column_stack([baseline_own,b0]),
                "partner_ghost3d":np.column_stack([baseline_own,b3]),
                "partner_ghost5d":np.column_stack([baseline_own,b5])
            }
            for year in sorted(set(years)):
                tag=(site,int(year),partner)
                if tag not in previously_admitted:
                    results.append({
                        "site":site,"partner":partner,"holdout_year":int(year),
                        "status":"PRIOR_V154_SOURCE_COHORT_STOP",
                        "original_v154_accepts_this_cohort":False
                    })
                    continue
                s=score_pair(features,audio,b0,years,year)
                results.append({
                    "site":site,"partner":partner,"holdout_year":int(year),
                    "original_v154_accepts_this_cohort":True,
                    "distance_to_gauge_km":item["geodesic_station_distance_km"],
                    **s
                })
    if len(results)!=64 or source_original_total!=136032 or runstart_total!=SOURCE_RUN_STARTS_EXPECTED or new_source_total!=135757:
        raise AssertionError("Frozen source cohorts/original run starters changed")
    if any(x["source_hourly_previous_observation_and_NOAA_valid"] / x["source_original_frozen_24h_hours"] <MIN_FRACTION_LAG_AND_TIDE
           for x in site_quality):
        raise AssertionError("Excessive loss of original source due to own-prev1 feature")
    eligible=[r for r in results if r["status"]=="EVALUATED_PRIOR_COASTAL_SOURCE_YEAR"]
    stop_count=Counter(r["status"] for r in results)
    # No post-opening selection: both previously known source categories
    # and all stopped cohorts remain in emitted result.
    summaries={}
    for p in PAIRS:
        sub=[r for r in eligible if r["partner"]==p]
        summaries[p]={
            "all_original_cohort_gates":sum(r["partner"]==p for r in results),
            "previously_admitted_v154_count":sum(r["partner"]==p and r["original_v154_accepts_this_cohort"] for r in results),
            "new_evaluated":len(sub),
            "site_equal_all":summarize(sub),
            "site_equal_gauge_distance_lte80km":summarize([
                r for r in sub if r["distance_to_gauge_km"]<=80.0
            ])
        }
    return {
        "version":"v155_observed_fish_self_prev1_bout_control_and_partner_day_ghost_1",
        "source":"Kim 2025 original California 60 member-SHA-verified fish chorus+verified NOAA gauge historical original",
        "prior_original_v154_evaluated_source_cohorts":len(previously_admitted),
        "original_fish_60_files_SHA256_replayed":True,
        "original_NOAA_14_gauge_year_body_SHA256_replayed":True,
        "source_original_audio_hours":source_original_total,
        "dropped_first_hour_each_v145_7dayplus_run":runstart_total,
        "same_original_hours_for_all_conditional_models":new_source_total,
        "all_site_source_quality":site_quality,
        "fixed_analysis":{
            "target":TARGET,
            "partners_posthoc_from_prior_study":list(PAIRS),
            "models":list(MODELS),
            "train_test":"train same site strictly earlier local calendar years, test complete later year; source-first v154 cohort gate unchanged",
            "own_state":"previous physically observed 1h original target label, no first source-run hour or synthetic absence",
            "other_source_real":"B same-recording hour; only conditional retrospective prediction",
            "day_shuffled_ghosts":list(GHOST_DAY_SHIFTS),
            "ghost_preserves":"same local contiguous yearmonth run and B complete day 24h clock-hour + temporal bout, except run-cyclic boundary",
            "model_logistic_fixed_L2_C":ALPHA_C,
            "model_logistic_maxiter":MAX_ITER,
            "feature_scaling":"training years only",
            "score":"heldout year binary negative log-loss nats/h, Brier sensitivity",
            "no_new_coefficients_or_tuning_based_on_known_source_outcome":True,
        },
        "all_site_year_pair_source_gates_and_scores":results,
        "site_year_equal_and_site_equal_descriptive_results":summaries,
        "stop_status_counts":dict(sorted(stop_count.items())),
        "new_real_acoustic_p_values":"NOT_COMPUTED",
        "independent_biological_coasts":1,
        "fish_direct_interspecific_interaction":"NOT_IDENTIFIED",
        "global_tide_solar_meta_effect":"NOT_ESTIMATED",
    }

def compact_receipt(v):
    canonical=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":v["version"],
        "full_original_source_model_JSON_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
        "full_original_source_model_nbytes":len(canonical.encode()),
        "all_60_original_fish_members_verified":v["original_fish_60_files_SHA256_replayed"],
        "all_14_NOAA_verified_body_sha256":v["original_NOAA_14_gauge_year_body_SHA256_replayed"],
        "n_source_original_hours":v["source_original_audio_hours"],
        "n_dropped_first_hour_per_run":v["dropped_first_hour_each_v145_7dayplus_run"],
        "same_source_scored_hours":v["same_original_hours_for_all_conditional_models"],
        "prior_v154_admitted_cohorts":v["prior_original_v154_evaluated_source_cohorts"],
        "source_site_quality":v["all_site_source_quality"],
        "fixed_models":v["fixed_analysis"],
        "source_gate_status":v["stop_status_counts"],
        "all_grouped_summary":v["site_year_equal_and_site_equal_descriptive_results"],
        "evaluated_cohort_scores":[
            {"site":z["site"],"year":z["holdout_year"],"partner":z["partner"],
             "n_train":z["train_hours"],"n_test":z["heldout_hours"],
             "n_positive_test":z["heldout_target_positive"],
             "loss_improvement":z["improvement_nats_per_original_hour"]}
            for z in v["all_site_year_pair_source_gates_and_scores"]
            if z["status"]=="EVALUATED_PRIOR_COASTAL_SOURCE_YEAR"
        ],
        "no_new_p_values":True,
        "no_independent_replication_or_direct_social_mechanism":True,
        "global_tide_x_solar_effect":"NOT_ESTIMATED",
    }

def main():
    arg=argparse.ArgumentParser()
    p=arg.add_mutually_exclusive_group(required=True)
    p.add_argument("--emit",action="store_true")
    p.add_argument("--check",action="store_true")
    options=arg.parse_args()
    full=estimate()
    receipt=compact_receipt(full)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    if options.check:
        if not RECEIPT.exists():raise AssertionError("Frozen first original-data model receipt absent")
        frozen=json.loads(RECEIPT.read_text())
        # Byte-exact original 60 acoustic member SHA and 14 NOAA provider
        # body-SHA enforced upstream. CPU sklearn floating point loss scores
        # may differ at <=1e-8, so identity gates are exact while numeric
        # fixed-model scores have a predeclared 1e-7 absolute tolerance.
        changed=[]
        def compare(path,x,y):
            if len(changed)>=50:return
            if path in {
                "root.full_original_source_model_JSON_sha256",
                "root.full_original_source_model_nbytes"}:return
            if type(x) is not type(y):changed.append([path,"TYPE",str(type(x)),str(type(y))])
            elif isinstance(x,dict):
                if set(x)!=set(y):changed.append([path,"KEYS",sorted(x),sorted(y)])
                else:
                    for key in sorted(x):compare(path+"."+str(key),x[key],y[key])
            elif isinstance(x,list):
                if len(x)!=len(y):changed.append([path,"COUNT",len(x),len(y)])
                else:
                    for i in range(len(x)):compare(path+"["+str(i)+"]",x[i],y[i])
            elif isinstance(x,float):
                if not math.isfinite(x) or not math.isfinite(y):
                    if x!=y:changed.append([path,x,y])
                elif abs(x-y)>1e-7:changed.append([path,x,y])
            elif x!=y:changed.append([path,x,y])
        compare("root",frozen,receipt)
        if changed:
            print("V155_SOURCE_REPLAY_DIAGNOSTIC="+json.dumps(changed[:20],ensure_ascii=True))
            raise AssertionError("Original-source categorical/numeric replay failed")
        print("V155_ORIGINAL_SOURCE_SHA_AND_HELDOUT_SCORE_REPLAY_PASS")
    else:
        print("V155_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V155_SOURCE_RECEIPT_END")
    print("V155_RESULT_SCOPE="+json.dumps({
        "original_source_hours":receipt["n_source_original_hours"],
        "matched_prev_source_hours":receipt["same_source_scored_hours"],
        "gate_counts":receipt["source_gate_status"],
        "grouped":receipt["all_grouped_summary"]},sort_keys=True,ensure_ascii=True))

if __name__=="__main__":main()
