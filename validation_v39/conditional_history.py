#!/usr/bin/env python3
"""v39: frozen past-speed increment over current tide×phase for wild oystercatchers.

This is an EXPLORATORY held-out chronological predictive comparison after
v33/v34 animal data were known. Current-tide baseline includes a fixed v38
nonlinear interaction; prior and future segments share NO original GPS fixes.
No causal cognition / wetland access / social Boids interpretation allowed.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v32"))
sys.path.insert(0,str(ROOT/"validation_v33"))
sys.path.insert(0,str(ROOT/"validation_v34"))
import forecast as gps
import tidal_forecast as tidal
import phase_response as pairs
import ebb_flood_height_matched as old_effect

PROTOCOL="docs/V39_CONDITIONAL_TIDE_PRIVATE_HISTORY_PROTOCOL.md"
SOURCE_ORIGINAL_BIRDS=39
SOURCE_RADIUS_KM=25.
MIN_PAST_PAIR_MIN=5.
MAX_PAST_PAIR_MIN=30.
MIN_FUTURE_PAIR_MIN=5.
MAX_FUTURE_PAIR_MIN=30.
MIN_GAP_MIN=5.
MAX_GAP_MIN=360.
TIDE_LAG_HOURS=3.
EMBARGO_DAYS=7
TRAINING_MIN_EPISODES=5000
TRAINING_MIN_BIRDS=10
TEST_YEARS=tuple(range(2010,2015))
MIN_TARGET_EPISODES=10000
MIN_SCOREABLE_BIRDS=20
MIN_EPISODES_PER_BIRD=30
MIN_YEARS=3
MIN_MONTHS=12
RIDGE_ALPHA=25.
BOOT=10000
BOOT_SEED=20261031
MODELS=("E0_DIRECT_ENVIRONMENT","E1_ENV_PLUS_DISJOINT_PRIOR_SPEED",
        "E2_ENV_PLUS_PRIOR_ASTRONOMICAL_TIDE",
        "E3_ENV_PLUS_BOTH_HISTORIES")
CONTRASTS=(("PRIMARY_E0_minus_E1",0,1),
           ("SECONDARY_E0_minus_E2",0,2),
           ("SECONDARY_E2_minus_E3",2,3),
           ("SECONDARY_E1_minus_E3",1,3))
ENV_FIELDS=(
  "intercept",
  "current_H_m_NAP","current_H_squared","current_dH_m_per_h",
  "current_dH_squared","current_H_times_dH","abs_current_dH",
  "analytical_v38_exposed_fraction_NOT_measured_mudflat",
  "analytical_v38_phase_height_smooth_interaction",
  "sin_UTC_hour_24","cos_UTC_hour_24","sin_UTC_hour_12","cos_UTC_hour_12",
  "sin_UTC_DOY_365p25","cos_UTC_DOY_365p25",
  "calendar_year_minus_2011",
  "latitude_relative_station_scaled","longitude_relative_station_scaled",
  "latitude_squared","longitude_squared","latitude_times_longitude",
  "prior_observed_device_pair_elapsed_minutes_over_30",
  "elapsed_since_disjoint_prior_pair_endpoint_minutes_over_360",
)
ADDITIONAL_FIELDS=(
  "prior_DISJOINT_same_bird_log1p_horizontal_speed",
  "astronomical_H_3hours_before_target",
  "astronomical_dH_3hours_before_target",
)
NO_GPS_FIX_SHARED_BETWEEN_PAST_AND_FUTURE=True

def four_original_fix_indices(i):
    if i<2:raise ValueError("Require four distinct original GPS fix indexes")
    idx=(i-2,i-1,i,i+1)
    if len(set(idx))!=4:raise ValueError("Original GPS intervals overlap")
    return idx

def tide_features(t,astro):
    """Only deterministic RWS astronomical levels, including t +/- 30 min."""
    center=pairs.nearest_tide_key(t)
    lag=center-dt.timedelta(hours=TIDE_LAG_HOURS)
    def levels(stamp):
        h=astro.get(stamp)
        before=astro.get(stamp-dt.timedelta(minutes=30))
        after=astro.get(stamp+dt.timedelta(minutes=30))
        if h is None or before is None or after is None:return None
        if any(not math.isfinite(v) for v in (h,before,after)):
            raise ValueError("Nonfinite original RWS astronomical WATHTE")
        return (float(h),float(after-before))
    present=levels(center)
    past=levels(lag)
    if present is None or past is None:return None
    return (*present,*past)

def current_feature_vector(t,lat,lon,tide_at_t,lag_interval_minutes,gap_minutes):
    H,slope=tide_at_t
    hh=t.hour+t.minute/60+t.second/3600
    dd=t.timetuple().tm_yday+(hh/24.)
    xlat=(lat-pairs.STATION_LAT)/.20
    xlon=(lon-pairs.STATION_LON)/.30
    exposed_analytic=np.clip((1.25-H)/2.4,0.,1.)
    direct_interaction=float(np.sign(-slope)*np.tanh((.5-H)/.30))
    arr=np.array([
       1.,H,H*H,slope,slope*slope,H*slope,abs(slope),
       float(exposed_analytic),direct_interaction,
       math.sin(2*math.pi*hh/24),math.cos(2*math.pi*hh/24),
       math.sin(2*math.pi*hh/12),math.cos(2*math.pi*hh/12),
       math.sin(2*math.pi*dd/365.25),math.cos(2*math.pi*dd/365.25),
       float(t.year-2011),
       xlat,xlon,xlat*xlat,xlon*xlon,xlat*xlon,
       lag_interval_minutes/30.,gap_minutes/360.
    ],dtype=float)
    if len(arr)!=len(ENV_FIELDS) or not np.isfinite(arr).all():
        raise ValueError("Frozen instantaneous source feature definition drift")
    return arr

def episode_eligibility(fixes,i,local_flags,astro):
    """Source 4-fix disjoint eligibility. Returns features and target, not IDs."""
    i0,i1,j0,j1=four_original_fix_indices(i)
    p0,p1,a0,a1=(fixes[k] for k in (i0,i1,j0,j1))
    if not (local_flags[i0] and local_flags[i1] and
            local_flags[j0] and local_flags[j1]):return None,"outside_fixed_25km_gauge"
    lag=(p1[1]-p0[1]).total_seconds()/60.
    future=(a1[1]-a0[1]).total_seconds()/60.
    gap=(a0[1]-p1[1]).total_seconds()/60.
    if not MIN_PAST_PAIR_MIN<=lag<=MAX_PAST_PAIR_MIN:
        return None,"not_5_to_30_min_previous_nonoverlapping_pair"
    if not MIN_FUTURE_PAIR_MIN<=future<=MAX_FUTURE_PAIR_MIN:
        return None,"not_5_to_30_min_upcoming_original_pair"
    if not MIN_GAP_MIN<=gap<=MAX_GAP_MIN:
        return None,"previous_pair_not_5_to_360_min_before_forecast"
    weather=tide_features(a0[1],astro)
    if weather is None:return None,"missing_original_astronomical_tide_at_target_or_lag"
    H,slope,H3,slope3=weather
    response=math.log1p(pairs.haversine_km(a0[2],a0[3],a1[2],a1[3])/(future/60.))
    lag_response=math.log1p(pairs.haversine_km(p0[2],p0[3],p1[2],p1[3])/(lag/60.))
    if not all(map(math.isfinite,(response,lag_response))):
        raise ValueError("Invalid source GPS speed")
    base=current_feature_vector(a0[1],a0[2],a0[3],(H,slope),lag,gap)
    return (a0[1],a1[1],base,lag_response,H3,slope3,response),None

def assemble_original_episodes(source_fixes,astro):
    """Original tuples are (anonymous_internal_bird_key, UTC, lat, lon)."""
    counts=collections.Counter()
    bybird={}
    grouped=itertools.groupby(sorted(source_fixes,key=lambda x:(x[0],x[1])),key=lambda x:x[0])
    for bird,items in grouped:bybird[bird]=list(items)
    birdnames=sorted(bybird)
    if len(birdnames)!=SOURCE_ORIGINAL_BIRDS:
        raise ValueError("Original source bird-ID structural count drift")
    birdlookup={b:i for i,b in enumerate(birdnames)}
    rows=[]
    for bird,points in bybird.items():
        local=[pairs.haversine_km(lat,lon,pairs.STATION_LAT,pairs.STATION_LON)<=SOURCE_RADIUS_KM
               for _,t,lat,lon in points]
        counts["original_source_GPS_fixes"]+=len(points)
        for i in range(2,len(points)-1):
            counts["original_four_fix_windows_scanned"]+=1
            episode,reason=episode_eligibility(points,i,local,astro)
            if reason:
                counts["excluded_"+reason]+=1
                continue
            start,end,base,lag_speed,H3,slope3,y=episode
            if y>math.log1p(100.):
                counts["included_future_step_over_100_km_h_descriptive"]+=1
            if lag_speed>math.log1p(100.):
                counts["included_prior_step_over_100_km_h_descriptive"]+=1
            rows.append((start,end,birdlookup[bird],base,
                         lag_speed,H3,slope3,y))
    if not rows:raise ValueError("No original source 4-fix episodes")
    rows.sort(key=lambda x:x[0])
    n=len(rows)
    n_birds=len(birdnames)
    base_dim=len(ENV_FIELDS)+n_birds
    total=base_dim+len(ADDITIONAL_FIELDS)
    X=np.zeros((n,total),dtype=float)
    label=np.empty(n,dtype=float)
    bird=np.empty(n,dtype=np.int16)
    start=np.empty(n,dtype="datetime64[us]")
    end=np.empty(n,dtype="datetime64[us]")
    for k,(t0,t1,bid,env,lag,H3,dh3,y) in enumerate(rows):
        X[k,:len(ENV_FIELDS)]=env
        X[k,len(ENV_FIELDS)+bid]=1.
        X[k,base_dim:]=[lag,H3,dh3]
        label[k]=y
        bird[k]=bid
        start[k]=np.datetime64(t0,"us")
        end[k]=np.datetime64(t1,"us")
    if not np.isfinite(X).all() or not np.isfinite(label).all():
        raise ValueError("Nonfinite original source episode model rows")
    counts["original_four_distinct_fix_future_episode_rows"]=n
    counts["source_distinct_birds_with_any_eligible_episode"]=len(set(map(int,bird)))
    counts["private_speed_and_forecast_no_shared_GPS_fix"]=True
    counts["future_original_interval_length_NOT_exposed_as_model_covariate"]=True
    counts["any_target_GPS_response_used_as_predictor"]=False
    names=list(ENV_FIELDS)+[f"original_bird_intercept_{i+1:03d}" for i in range(n_birds)]+list(ADDITIONAL_FIELDS)
    cols0=np.arange(base_dim)
    indices={
      MODELS[0]:cols0,
      MODELS[1]:np.append(cols0,base_dim),
      MODELS[2]:np.append(cols0,[base_dim+1,base_dim+2]),
      MODELS[3]:np.arange(total),
    }
    return {"X":X,"y":label,"start":start,"end":end,"bird":bird,
             "feature_names":names,"model_indices":indices},dict(counts)

def frozen_ridge(gram,xy,cols,alpha=RIDGE_ALPHA):
    if alpha!=RIDGE_ALPHA:
        raise ValueError("Unregistered ridge parameter")
    block=gram[np.ix_(cols,cols)].copy()
    diag=np.full(len(cols),alpha)
    # Original first feature is a constant intercept; do not penalize it.
    if cols[0]!=0:raise ValueError("Fixed source design lost intercept")
    diag[0]=0.
    block[np.diag_indices_from(block)]+=diag
    coeff=np.linalg.solve(block,xy[cols])
    if not np.isfinite(coeff).all():raise ValueError("Bad ridge coefficients")
    return coeff

def month_starts():
    return [dt.datetime(year,month,1) for year in TEST_YEARS for month in range(1,13)]

def month_train_cutoff(month):
    return np.datetime64(month-dt.timedelta(days=EMBARGO_DAYS),"us")

def chronological_fit_predict(d):
    """Month-forward blocked ridge; no test labels can update same-month fit."""
    X,y,start,end,bird=(d[k] for k in ("X","y","start","end","bird"))
    cols=d["model_indices"]
    order=np.argsort(end)
    cursor=0
    gram=np.zeros((X.shape[1],X.shape[1]),dtype=float)
    xy=np.zeros(X.shape[1],dtype=float)
    train_birds=set()
    errors=np.full((len(y),len(MODELS)),np.nan,dtype=np.float64)
    source_counts=collections.Counter()
    folds=[]
    for month in month_starts():
        first=np.datetime64(month,"us")
        next_month=dt.datetime(month.year+(month.month==12),(month.month%12)+1,1)
        last=np.datetime64(next_month,"us")
        cutoff=month_train_cutoff(month)
        newly_start=cursor
        while cursor<len(order) and end[order[cursor]]<cutoff:
            cursor+=1
        if cursor>newly_start:
            idx=order[newly_start:cursor]
            z=X[idx]
            gram+=z.T@z
            xy+=z.T@y[idx]
            train_birds.update(int(v) for v in bird[idx])
        testidx=np.where((start>=first)&(start<last))[0]
        if len(testidx)==0:
            source_counts["months_with_no_original_eligible_episodes"]+=1
            continue
        if cursor<TRAINING_MIN_EPISODES or len(train_birds)<TRAINING_MIN_BIRDS:
            source_counts["months_failing_frozen_training_support"]+=1
            source_counts["test_episodes_unscored_due_training_support"]+=len(testidx)
            continue
        if not np.all(end[order[:cursor]]<cutoff):
            raise ValueError("Same/future source observation leaked across seven-day embargo")
        if np.any(start[testidx]<first) or np.any(start[testidx]>=last):
            raise ValueError("Test month original UTC block mismatch")
        for m,mode in enumerate(MODELS):
            cs=cols[mode]
            co=frozen_ridge(gram,xy,cs)
            yh=X[np.ix_(testidx,cs)]@co
            errors[testidx,m]=(y[testidx]-yh)**2
        if not np.isfinite(errors[testidx]).all():
            raise ValueError("Nonfinite source-verified next-step error")
        folds.append({"year":month.year,"month":month.month,
            "target_rows":len(testidx),"prior_training_rows":cursor,
            "prior_original_training_birds":len(train_birds)})
        source_counts["scored_future_original_GPS_step_episodes"]+=len(testidx)
        source_counts["source_UTC_months_scored"]+=1
    return errors,folds,dict(source_counts)

def sign_tail(k,n):
    return sum(math.comb(n,i) for i in range(k,n+1))/(2**n) if n else 1.

def summarize(ep,errors,folds,source_qa):
    test=np.where(np.isfinite(errors).all(axis=1))[0]
    bybird=collections.defaultdict(list)
    for idx in test:bybird[int(ep["bird"][idx])].append(int(idx))
    eligible={bird:np.array(ix,dtype=int) for bird,ix in bybird.items()
              if len(ix)>=MIN_EPISODES_PER_BIRD}
    accepted=np.concatenate(list(eligible.values())) if eligible else np.array([],dtype=int)
    years={int(str(ep["start"][v])[:4]) for v in accepted}
    months={str(ep["start"][v])[:7] for v in accepted}
    support={
      "whole_original_birds_in_eligible_score":len(eligible),
      "source_birds_with_any_scored_future_step":len(bybird),
      "birds_with_lt_30_scored_future_steps_excluded_from_equal_bird_scores":len(bybird)-len(eligible),
      "original_test_step_episodes_in_eligible_birds":len(accepted),
      "original_scored_future_step_episodes_before_bird_support":len(test),
      "independent_calendar_years_observed_NOT_ecosystem_replicates":len(years),
      "calendar_months_scored_from_eligible_birds":len(months),
      "source_original_future_episode_start_years":sorted(years),
      "frozen_bird_min_episodes":MIN_EPISODES_PER_BIRD,
      "frozen_required_birds":MIN_SCOREABLE_BIRDS,
      "frozen_required_future_steps":MIN_TARGET_EPISODES,
      "frozen_required_years":MIN_YEARS,
      "frozen_required_months":MIN_MONTHS,
    }
    if (len(eligible)<MIN_SCOREABLE_BIRDS or len(accepted)<MIN_TARGET_EPISODES or
        len(years)<MIN_YEARS or len(months)<MIN_MONTHS):
        return {"status":"NOT_ADMITTED_ORIGINAL_TIDAL_PAST_SPEED_HELDOUT_SUPPORT",
            "support":support,"any_model_scores_reported":False}
    birds=sorted(eligible)
    matrix=np.array([np.mean(errors[eligible[b]],axis=0) for b in birds])
    if not np.isfinite(matrix).all():raise ValueError("Invalid held-out whole-bird MSE")
    draws=np.random.default_rng(BOOT_SEED).integers(0,len(birds),size=(BOOT,len(birds)))
    comparisons={}
    for name,i,j in CONTRASTS:
        effect=matrix[:,i]-matrix[:,j]
        npositive=int((effect>0).sum())
        nnonzero=int((effect!=0).sum())
        comparisons[name]={
          "equal_bird_MSE_gain_positive_means_added_information":float(np.mean(effect)),
          "paired_whole_original_bird_bootstrap_95":list(map(float,
                    np.quantile(effect[draws].mean(axis=1),[.025,.975]))),
          "positive_original_birds":npositive,
          "negative_original_birds":int((effect<0).sum()),
          "nonzero_original_birds":nnonzero,
          "one_sided_positive_bird_sign_p":sign_tail(npositive,nnonzero),
        }
    annual=[]
    for year in sorted(years):
        scores=[]
        for b in birds:
            xi=[r for r in eligible[b] if int(str(ep["start"][r])[:4])==year]
            if xi:scores.append(np.mean(errors[xi],axis=0))
        if not scores:continue
        annual.append({"source_GPS_year":year,
            "birds_with_any_future_step":len(scores),
            "original_future_step_count":sum(1 for ix in accepted
                         if int(str(ep["start"][ix])[:4])==year),
            "equal_bird_MSE_E0_E1_E2_E3":list(map(float,np.mean(scores,axis=0))),
            "PRIVATE_SPEED_GAIN_E0_minus_E1":float(np.mean(
                     np.array(scores)[:,0]-np.array(scores)[:,1])),
            "same_coastal_study_not_independent_external_site":True})
    # Calendar-month equal-block descriptive (weights are not whole-bird weights).
    permonth=[]
    for period in sorted(months):
        ids=[idx for idx in accepted if str(ep["start"][idx])[:7]==period]
        if ids:permonth.append(float(np.mean(errors[ids,0]-errors[ids,1])))
    month_boot=np.random.default_rng(BOOT_SEED).integers(0,len(permonth),
                                            size=(BOOT,len(permonth)))
    month_summary={
      "source_UTC_months":len(permonth),
      "mean_month_effect_different_weighting_than_primary":float(np.mean(permonth)),
      "naive_calendar_month_bootstrap95_descriptive_only":list(map(float,
            np.quantile(np.array(permonth)[month_boot].mean(axis=1),[.025,.975]))),
      "not_independent_of_shared_climate_seasons_or_repeated_birds":True,
    }
    return {"status":"EXPLORATORY_TIME_FORWARD_TIDE_CONDITIONAL_PRIVATE_HISTORY_FORECAST",
      "original_one_site_whole_bird_units":len(birds),
      "source_UTC_years":sorted(years),
      "support":support,
      "model_order":list(MODELS),
      "absolute_equal_bird_MSE_E0_E1_E2_E3":list(map(float,matrix.mean(axis=0))),
      "all_frozen_signed_comparisons":comparisons,
      "whole_bird_bootstrap_reps":BOOT,
      "whole_bird_bootstrap_rng_seed":BOOT_SEED,
      "calendar_month_paired_effect_support":month_summary,
      "original_years_descriptive_no_cherry_picking":annual,
      "anonymized_per_bird_model_errors":{
           f"bird_{i+1:03d}":{
             "heldout_original_step_episodes":len(eligible[b]),
             "equal_bird_MSE_E0_E1_E2_E3":list(map(float,matrix[i]))
           } for i,b in enumerate(birds)},
      "no_animal_GPS_ID_position_or_raw_UTC_episode_exported":True,
      "future_actual_GPS_reporting_interval_not_used_as_predictor":True,
      "prior_history_disjoint_GPS_fixes":True,
      "calendar_blocked_train_with_7day_embargo":True,
      "source_original_observation_process_not_random_and_target_selection_post_observation":True}

def run():
    astronomy,source_tide_years=tidal.load_original_astronomy()
    with tempfile.TemporaryDirectory() as folder:
        files=gps.original_files_to_temp(Path(folder))
        positions,source_gps_qa=pairs.read_original_valid_gps(files)
    original_gate=old_effect.replay_original_D(positions,astronomy,source_gps_qa)
    if original_gate["original_source_whole_birds"]!=36 or original_gate["original_bird_month_clock_strata"]!=5422:
        raise ValueError("Frozen v33-D previous source evidence gate changed")
    dataset,admission=assemble_original_episodes(positions,astronomy)
    errors,folds,fold_qa=chronological_fit_predict(dataset)
    result=summarize(dataset,errors,folds,fold_qa)
    output={
      "status":result["status"],
      "protocol":PROTOCOL,
      "source_original_bird_zenodo":"10053970, full 7 source years 2008-2014, provider MD5 SHA pins",
      "source_astronomy":"RWS official schiermonnikoog.waddenzee astronomical WATHTE in NAP cm",
      "source_astronomy_annual_10minute_quality":source_tide_years,
      "source_original_GPS_QA":source_gps_qa,
      "full_original_v33D_replay_gate":original_gate,
      "new_original_source_four_nonoverlapping_GPS_fix_eligibility":admission,
      "chronological_monthwise_prequential_QA":fold_qa,
      "monthly_fold_training_source_ranges_not_target_values":[
         {"year":x["year"],"month":x["month"],
          "count_original_scored_next_steps":x["target_rows"],
          "number_training_original_steps_before_7day_embargo":x["prior_training_rows"],
          "source_training_birds":x["prior_original_training_birds"]}
         for x in folds],
      "fixed_environment_feature_names_excluding_original_animal_IDs":dataset["feature_names"],
      "all_four_models_regression_ridge_alpha":RIDGE_ALPHA,
      "registered_model_order":list(MODELS),
      "observed_holdout":result,
      "no_original_individual_ID_UTC_location_future_tide_or_animal_response_published":True,
      "all_prior_v29_v30_v31_v32_v33_v34_v34B_v37_v38_results_unchanged":True,
      "science_cautions":[
         "Only previously opened Schiermonnikoog original bird population; exploratory post-v33 and post-v38",
         "Fixed target is next original 5-30min GPS step; observation schedule eligibility uses a future fix, never operational all-times prediction",
         "Disjoint past step avoids direct shared GPS fix but leaves temporal autocorrelation and measurement error",
         "Current tide and prior tide are astronomical predictions, not measured wind-driven water exposure",
         "H×dH, spatial and clock feature basis may not represent all local causes or bird foraging state",
         "Private-speed predictive increment cannot identify learned memory, individual cognitive state or causal Boids forces",
         "Whole-bird and calendar-month uncertainty are not independent geographic replications",
      ]}
    return output

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,
         default=Path("validation_v39/results/conditional_private_history_over_tide_v39.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    contents=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
          prefix=".v39-",delete=False) as temp:
        temp.write(contents); tmp=Path(temp.name)
    os.replace(tmp,args.out)
    print("V39_OLD_SOURCE_REPLAY",json.dumps(result["full_original_v33D_replay_gate"],sort_keys=True))
    print("V39_ORIGINAL_FOUR_FIX_SOURCE_GATE",json.dumps(result["new_original_source_four_nonoverlapping_GPS_fix_eligibility"],sort_keys=True))
    print("V39_MONTHWISE_QA",json.dumps(result["chronological_monthwise_prequential_QA"],sort_keys=True))
    print("V39_STATUS",result["status"])
    if result["observed_holdout"].get("all_frozen_signed_comparisons"):
        o=result["observed_holdout"]
        print("V39_OBSERVED_MODEL_MSE",json.dumps(o["absolute_equal_bird_MSE_E0_E1_E2_E3"]))
        print("V39_ALL_FROZEN_SIGNS",json.dumps(o["all_frozen_signed_comparisons"],sort_keys=True))
        print("V39_ANNUAL_DESCRIPTIVE",json.dumps(o["original_years_descriptive_no_cherry_picking"],sort_keys=True))
    else:print("V39_NO_PREDICTION_SCORES",json.dumps(result["observed_holdout"],sort_keys=True))
    print("V39_COMPLETE_ANONYMOUS_AGGREGATE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
