#!/usr/bin/env python3
"""v43: actual wild GPS past-neighbor heading out-of-month predictive comparison.

Original source Zenodo 10053970 and RWS astronomical tide. Not causal
Reynolds Boids force identification; all old source/behavior scores replayed.
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
for p in ("validation_v40","validation_v42","validation_v41","validation_v39",
          "validation_v34","validation_v33","validation_v32"):
    sys.path.insert(0,str(ROOT/p))
import vector_history as v40
import spatial_source as v42
import conditional_history as v39
import phase_response as gpsgeom
import tidal_forecast as tides
import forecast as source
import ebb_flood_height_matched as gate34

PROTO="docs/V43_SPATIALLY_NEAR_CONSPECIFIC_PAST_HEADING_FORECAST_PROTOCOL.md"
V42_SAVED=ROOT/"validation_v42/results/wild_gps_cotimed_200m_source_geometry_v42.json"
V40_SAVED=ROOT/"validation_v40/results/heldout_tidal_private_heading_v40.json"
NEAR_RADIUS_KM=.2
FAR_RADIUS_MIN_KM=1.
AGE_MAX_MIN=5.
GAUGE_MAX_KM=25.
BOOT=10000
RNG=20261031
MIN_BIRDS=20
MIN_EPISODES=20000
MIN_MONTHS=12
MIN_YEARS=2
MIN_PER_BIRD=30
MIN_ANGLE_BIRDS=20
MIN_ANGLE_EPISODES=10000
MIN_PER_BIRD_ANGLE=20
MODELS=("S0_NEIGHBOR_CONTEXT_AND_OWN_HEADING",
        "S1_PLUS_NEAR_200M_PAST_OTHER_HEADING",
        "S2_PLUS_FAR_1KM_PAST_OTHER_HEADING",
        "S3_PLUS_NEAR_AND_FAR_HEADINGS")
CONTRASTS=(("PRIMARY_S0_minus_S1_NEAR",0,1),
 ("SECONDARY_S0_minus_S2_FAR",0,2),
 ("SECONDARY_S2_minus_S3_NEAR_AFTER_FAR",2,3),
 ("SECONDARY_S1_minus_S3_FAR_AFTER_NEAR",1,3),
 ("descriptive_NEAR_GAIN_minus_FAR_GAIN",2,1))
CONTEXT_NAMES=(
 "near_source_observed","log1p_count_near",
 "nearest_other_distance_over_200m","nearest_other_fix_age_over_5min",
 "bearing_to_nearest_other_E","bearing_to_nearest_other_N",
 "mean_near_other_prior_log1p_speed",
 "far_source_observed","log1p_count_far","mean_far_other_prior_log1p_speed")
assert len(CONTEXT_NAMES)==10

def replay_sources(files,astro,tide_qa):
    """Replay v41 timestamp, v42 co-location, v33/v39 and v40 outcomes."""
    old_time=v42.source_original_v41_replay(files)  # NO coordinates read.
    points,gps_qa=gpsgeom.read_original_valid_gps(files)
    old_geo=v42.coordinate_source_support(points) # NO headings scored.
    frozen42=json.loads(V42_SAVED.read_text())
    for key,new in (
        ("previous_source_only_v41_time_AUDIT_replay",old_time),
        ("source_only_spatial_neighbor_opportunities_NOT_effects",old_geo),
        ("original_v33_GPS_quality_602380",gps_qa)):
        if not gate34.nested_close(new,frozen42.get(key),1e-12):
            raise ValueError("Original v41/v42 spatial source receipt drift: "+key)
    if old_geo["status"]!=v42.PASS:
        raise ValueError("Source 200m past GPS co-occurrence gate no longer admitted")
    previous,_,v39receipt=v40.old_v39_receipt_replay(points,astro,gps_qa,tide_qa)
    Y,heading,distance,source_qa=v40.vector_source_target_rows(points,astro,previous)
    X40,cols40=v40.model_matrix(previous,heading)
    err,ang,folds,foldQA=v40.chronological_vector_forecast(
        previous,X40,Y,distance,cols40)
    observed=v40.evaluate_equal_birds(previous,err,ang,folds,foldQA)
    saved40=json.loads(V40_SAVED.read_text())
    checks={
      "source_RWS_annual_10min_original_quality":tide_qa,
      "source_GPS_original_integrity_and_quality":gps_qa,
      "strict_source_old_v33D_and_v39_full_replay":v39receipt,
      "original_vector_eligible_4fix_source_support":source_qa,
      "calendar_month_7day_embargo_qa":foldQA,
      "observed_vector_forecast":observed}
    for name,val in checks.items():
        if not gate34.nested_close(val,saved40.get(name),1e-12):
            raise ValueError("Original v40 all-bird source+direction score drift: "+name)
    if (len(previous["y"])!=328323 or
        observed["support"]["whole_original_birds"]!=21 or
        observed["support"]["eligible_future_step_vector_labels"]!=305257):
        raise ValueError("Original v39/v40 fixed cohort drift")
    return points,previous,Y,distance,X40,cols40,err,{
        "status":"ALL_V41_TIME_V42_SPATIAL_V33D_V39_V40_NUMERIC_RECEIPTS_IDENTICAL",
        "source_ID_UTC_fix_count":old_time["original_valid_source_ID_UTC_events"],
        "source_time_only_2010_2012_other_bird_upper_bound":
           old_time["previous_time_only_2010_2012_other_heading_upper_bound"],
        "source_v42_200m_2010_2012_focal_opportunities":
           old_geo["2010_2012_support_all_fixed_radii"]["0.2_km"]["potential_spatially_cotimed_focal_starts"],
        "original_v39_v40_episode_candidates":len(previous["y"]),
        "original_v40_holdout_birds":observed["support"]["whole_original_birds"],
        "original_v40_heldout_episodes":observed["support"]["eligible_future_step_vector_labels"],
        "numeric_abs_tolerance":1e-12,
        "source_prior_v29_to_v42_unchanged":True}

def endpoint_candidates(points):
    bybird={b:list(rows) for b,rows in itertools.groupby(
        sorted(points,key=lambda x:(x[0],x[1])),key=lambda x:x[0])}
    ids={b:i for i,b in enumerate(sorted(bybird))}
    allend=[]
    for name,fixes in bybird.items():
        local=[gpsgeom.haversine_km(lat,lon,gpsgeom.STATION_LAT,
                   gpsgeom.STATION_LON)<=GAUGE_MAX_KM
               for _,t,lat,lon in fixes]
        bid=ids[name]
        for i in range(1,len(fixes)):
            p,q=fixes[i-1],fixes[i]
            minutes=(q[1]-p[1]).total_seconds()/60.
            if not (5.<=minutes<=30. and local[i-1] and local[i]):
                continue
            _,_,distance,e,n=v40.spherical_east_north(
                 p[2],p[3],q[2],q[3])
            allend.append((q[1],bid,q[2],q[3],e,n,
                           math.log1p(distance/(minutes/60.))))
    return sorted(allend,key=lambda x:x[0]),ids

def episode_starts(points,pinned,ids):
    fixed={}
    for b,t,lat,lon in points:
        key=(ids[b],t)
        if key in fixed:raise ValueError("Duplicate source GPS bird UTC after source gate")
        fixed[key]=(lat,lon)
    starts=[]
    for i,(timestamp,b) in enumerate(zip(pinned["start"],pinned["bird"])):
        time=timestamp.astype("datetime64[us]").astype(dt.datetime)
        key=(int(b),time)
        if key not in fixed:
            raise ValueError("Original v40 target-start fix source not found")
        starts.append((time,int(b),*fixed[key],i))
    if len(starts)!=328323:raise ValueError("Original v40 episode count drift")
    return sorted(starts,key=lambda x:(x[0],x[1]))

def source_neighbor_features(focal,latest):
    """Only source previous-other-bird fixes, NEVER target-time future fixes."""
    t,b,lat,lon,idx=focal
    near=[];far=[]
    for ob,(ot,olat,olon,e,n,speed) in latest.items():
        if ob==b:continue
        age=(t-ot).total_seconds()/60.
        if age<0 or age>AGE_MAX_MIN:continue
        dist=gpsgeom.haversine_km(lat,lon,olat,olon)
        sample=(dist,ob,age,olat,olon,e,n,speed)
        if dist<=NEAR_RADIUS_KM:near.append(sample)
        elif dist>=FAR_RADIUS_MIN_KM:far.append(sample)
    near.sort(key=lambda x:(x[0],x[1]))
    far.sort(key=lambda x:(x[0],x[1]))
    if near:
        closest=near[0]
        _,_,_,e,n=v40.spherical_east_north(lat,lon,closest[3],closest[4])
        ctrl=[1.,math.log1p(len(near)),closest[0]/NEAR_RADIUS_KM,
              closest[2]/AGE_MAX_MIN,e,n,float(np.mean([x[7] for x in near]))]
        nd=np.mean(np.array([[x[5],x[6]] for x in near]),axis=0)
    else:ctrl=[0.]*7;nd=np.zeros(2)
    ctrl.extend([float(bool(far)),math.log1p(len(far)),
                 float(np.mean([x[7] for x in far])) if far else 0.])
    fd=np.mean(np.array([[x[5],x[6]] for x in far]),axis=0) if far else np.zeros(2)
    if len(ctrl)!=10:raise ValueError("Frozen context control field count changed")
    return np.asarray(ctrl,float),np.asarray(nd,float),np.asarray(fd,float),bool(near),bool(far)

def construct_source_neighbor_table(points,pinned):
    endings,ids=endpoint_candidates(points)
    starts=episode_starts(points,pinned,ids)
    n=len(starts)
    context=np.empty((n,10),dtype=float)
    nd=np.empty((n,2),dtype=float)
    fd=np.empty((n,2),dtype=float)
    near=np.zeros(n,dtype=bool)
    far=np.zeros(n,dtype=bool)
    annual=collections.Counter()
    yearbird=collections.defaultdict(set)
    yearmonths=collections.defaultdict(set)
    coexist=collections.Counter()
    latest={}
    cursor=0
    for focal in starts:
        time,b,lat,lon,idx=focal
        while cursor<len(endings) and endings[cursor][0]<=time:
            stamp,other,olat,olon,e,n,speed=endings[cursor]
            latest[other]=(stamp,olat,olon,e,n,speed)
            cursor+=1
        ctx,xnear,xfar,seen_near,seen_far=source_neighbor_features(focal,latest)
        context[idx]=ctx;nd[idx]=xnear;fd[idx]=xfar
        near[idx]=seen_near;far[idx]=seen_far
        if seen_near:
            annual[time.year]+=1
            yearbird[time.year].add(b)
            yearmonths[time.year].add((time.year,time.month))
            if seen_far:coexist[time.year]+=1
    count=sum(annual[y] for y in (2010,2011,2012))
    if count!=171041:raise ValueError("Original spatial v42 171041 near 200m source opportunities drift")
    if not all(np.isfinite(x).all() for x in (context,nd,fd)):
        raise ValueError("Original near source directional feature nonfinite")
    qa={"status":"REPLAY_V42_FULL_200M_TIME_AND_SPATIAL_OPPORTUNITY_171041",
        "all_original_v40_focal_candidate_start_rows":n,
        "other_birds_original_past_GPS_pair_endpoints_count":len(endings),
        "near_source_starts_2010_2012":count,
        "all_years_source_near_and_far_counts":{
          str(y):{"focal_near_200m_original_source_starts":annual[y],
                  "focal_original_bird_count":len(yearbird[y]),
                  "focal_UTC_calendar_month_count":len(yearmonths[y]),
                  "near_200m_with_also_far_ge_1km_source":coexist[y]}
          for y in range(2008,2015)},
        "other_birds_never_use_fixes_after_focal_start":True,
        "no_original_neighbor_GPS_coordinates_or_IDs_exported":True}
    return context,nd,fd,near,far,qa

def model_matrix(X40,v40indices,context,nearhead,farhead):
    if context.shape!=(X40.shape[0],10) or nearhead.shape!=(X40.shape[0],2) or farhead.shape!=(X40.shape[0],2):
        raise ValueError("Original source expected exact 10+2+2 context and heading shapes")
    X=np.column_stack([X40,context,nearhead,farhead])
    orig=v40indices[v40.MODELS[1]]  # Exact V1: prior own speed and own heading included
    n=X40.shape[1]
    common=np.concatenate((orig,np.arange(n,n+10)))
    near=np.arange(n+10,n+12);far=np.arange(n+12,n+14)
    variants=(common,np.concatenate((common,near)),
              np.concatenate((common,far)),np.concatenate((common,near,far)))
    return X,{v40.MODELS[i]:variants[i] for i in range(4)}

def summary_contrasts(mat,bootstrap):
    result={}
    for name,i,j in CONTRASTS:
        effect=mat[:,i]-mat[:,j]
        positive=int(np.sum(effect>0));n=int(np.sum(effect!=0))
        result[name]={"equal_bird_MSE_gain":float(np.mean(effect)),
             "whole_bird_bootstrap_95":list(map(float,np.quantile(
                   effect[bootstrap].mean(axis=1),[.025,.975]))),
             "positive_original_birds":positive,
             "negative_original_birds":int(np.sum(effect<0)),
             "nonzero_original_birds":n,
             "one_sided_positive_bird_sign_p":v39.sign_tail(positive,n)}
    return result

def evaluate(pinned,errors,angles,near,far):
    scored=np.where(np.isfinite(errors).all(axis=1)&near)[0]
    bybird=collections.defaultdict(list)
    for i in scored:bybird[int(pinned["bird"][i])].append(int(i))
    eligible={b:np.array(ix,dtype=int) for b,ix in bybird.items() if len(ix)>=MIN_PER_BIRD}
    included=np.concatenate(list(eligible.values())) if eligible else np.array([],dtype=int)
    years=sorted({int(str(pinned["start"][i])[:4]) for i in included})
    months=sorted({str(pinned["start"][i])[:7] for i in included})
    support={"original_birds_with_30plus_heldout_near_steps":len(eligible),
       "original_birds_with_any_heldout_near_steps":len(bybird),
       "original_200m_heldout_vector_step_episodes":len(included),
       "original_near_heldout_step_episodes_before_bird_gate":len(scored),
       "original_source_years":years,"original_UTC_month_count":len(months),
       "near_heldout_steps_with_far_bird_direction_also_available":int(np.sum(far[included])) if len(included) else 0,
       "all_four_models_identical_future_target_episodes":True}
    if (len(eligible)<MIN_BIRDS or len(included)<MIN_EPISODES
        or len(years)<MIN_YEARS or len(months)<MIN_MONTHS):
        return {"status":"NOT_ADMITTED_NEAR_BIRD_HEADING_HELDOUT_SUPPORT",
            "support":support,"any_social_information_gain_reported":False}
    birds=sorted(eligible)
    mat=np.array([np.mean(errors[eligible[b]],axis=0) for b in birds])
    boot=np.random.default_rng(RNG).integers(0,len(birds),size=(BOOT,len(birds)))
    comparisons=summary_contrasts(mat,boot)
    angular_bybird={b:eligible[b][np.isfinite(angles[eligible[b],0])] for b in birds}
    accepted={b:ix for b,ix in angular_bybird.items() if len(ix)>=MIN_PER_BIRD_ANGLE}
    ans={"original_birds_with_20plus_directional_near_steps":len(accepted),
         "original_true_future_displacement_ge_50m_steps":sum(len(x) for x in accepted.values())}
    if len(accepted)<MIN_ANGLE_BIRDS or ans["original_true_future_displacement_ge_50m_steps"]<MIN_ANGLE_EPISODES:
        angular={"status":"NOT_ADMITTED_NEAR_BIRD_ANGULAR_SUPPORT",
                 "support":ans,"any_angular_effect_exported":False}
    else:
        order=sorted(accepted)
        am=np.array([np.mean(angles[accepted[b]],axis=0) for b in order])
        ab=np.random.default_rng(RNG).integers(0,len(order),size=(BOOT,len(order)))
        angular={"status":"EXPLORATORY_NEAR_BIRD_HEADING_ANGULAR_EVALUATION",
                 "support":ans,"equal_bird_angle_loss_S0_S1_S2_S3":list(map(float,am.mean(axis=0))),
                 "all_registered_angular_contrasts":summary_contrasts(am,ab)}
    annual=[]
    for year in years:
        per=[]
        for b in birds:
            ix=[i for i in eligible[b] if int(str(pinned["start"][i])[:4])==year]
            if ix:per.append(np.mean(errors[ix],axis=0))
        if per:
            ar=np.array(per)
            annual.append({"original_GPS_year":year,"birds_with_near_heldout_steps":len(per),
               "original_heldout_near_focal_step_count":sum(
                   int(str(pinned["start"][i])[:4])==year for i in included),
               "equal_bird_MSE_S0_S1_S2_S3":list(map(float,ar.mean(axis=0))),
               "registered_near_heading_gain_S0_minus_S1":float(np.mean(ar[:,0]-ar[:,1]))})
    periods=[]
    for key in months:
        ix=np.array([i for i in included if str(pinned["start"][i])[:7]==key],dtype=int)
        if len(ix):periods.append(float(np.mean(errors[ix,0]-errors[ix,1])))
    p=np.array(periods)
    draw=np.random.default_rng(RNG).integers(0,len(p),size=(BOOT,len(p)))
    return {"status":"EXPLORATORY_WILD_NEAR_BIRD_PAST_HEADING_PREDICTIVE_TEST",
       "support":support,"model_order":list(MODELS),
       "equal_bird_vector_MSE_S0_S1_S2_S3":list(map(float,mat.mean(axis=0))),
       "all_fixed_signed_vector_comparisons":comparisons,
       "secondary_fixed_moving_targets_angular_evaluation":angular,
       "original_year_descriptive":annual,
       "calendar_month_descriptive":{"count":len(months),
           "equal_month_heading_gain_not_primary_equal_bird_estimand":float(np.mean(p)),
           "naive_95_month_bootstrap_not_independent":list(map(float,np.quantile(
                p[draw].mean(axis=1),[.025,.975])))},
       "anonymous_original_bird_MSE":{
          f"bird_{i+1:03d}":{"original_heldout_near_200m_steps":len(eligible[b]),
               "model_MSE_S0_S1_S2_S3":list(map(float,mat[i]))}
          for i,b in enumerate(birds)},
       "boot_reps":BOOT,"seed":RNG,
       "only_one_original_coastal_study":True,
       "no_raw_animal_ID_GPS_or_original_UTC_exported":True}

def run():
    astronomy,tideqa=tides.load_original_astronomy()
    with tempfile.TemporaryDirectory() as work:
        original_files=source.original_files_to_temp(Path(work))
        points,pinned,Y,dist,X40,indices,old_errors,gate=replay_sources(
            original_files,astronomy,tideqa)
    ctx,nd,fd,near,far,sourceqa=construct_source_neighbor_table(points,pinned)
    X,models=model_matrix(X40,indices,ctx,nd,fd)
    errors,angular,folds,fitqa=v40.chronological_vector_forecast(
        pinned,X,Y,dist,models)
    if not np.array_equal(np.isfinite(errors).all(axis=1),np.isfinite(old_errors).all(axis=1)):
        raise ValueError("New source future-month cohort differs from pinned v40")
    result=evaluate(pinned,errors,angular,near,far)
    return {"status":result["status"],"protocol":PROTO,
        "source":"original Zenodo 10053970 v4 GPS and RWS Schiermonnikoog 7yrs astronomical WATHTE",
        "frozen_v41_v42_v33_v39_v40_all_source_receipts":gate,
        "source_spatial_neighbor_time_support_before_behavior_score":sourceqa,
        "near_radius_km":NEAR_RADIUS_KM,"far_control_distance_lower_bound_km":FAR_RADIUS_MIN_KM,
        "other_latest_original_GPS_endpoint_max_past_age_min":AGE_MAX_MIN,
        "original_other_bird_prior_GPS_pair_minutes":[5,30],
        "context_feature_order":list(CONTEXT_NAMES),
        "additional_heading_features":["near_unit_E","near_unit_N","far_unit_E","far_unit_N"],
        "source_chronological_month_7day_embargo_training_QA":fitqa,
        "original_monthwise_model_fitting_counts":[
            {"year":x["year"],"month":x["month"],
             "all_original_future_start_episodes_tested":x["future_target_steps"],
             "prior_original_training_steps_before_7day_embargo":x["original_training_steps_before_7day_embargo"]}
            for x in folds],
        "observed_near_bird_direction_forecast":result,
        "original_v29_v30_v31_v32_v33_v34_v39_v40_v41_v42_not_changed":True,
        "no_individual_original_ID_GPS_coordinates_timestamp_raw_other_bird_heading_published":True,
        "limitations":[
            "Originally opened same one coastal bird population, not independent validation",
            "Neighbor is spatially near and prior-time GPS observed, not necessarily socially interacting",
            "Mean other bird past heading may encode shared pathways, weather, tide and data-duty effects",
            "Far controls can differ in location, bird count, recording opportunity and habitat",
            "Original focal future recording interval 5-30min is response cohort selection not known prediction input",
            "2D GPS vector only; no 3D altitude, feeding location or causal Reynolds force inferred",
            "Bird-level and month-level bootstraps do not turn shared local study into independent ecosystems"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,default=Path("validation_v43/results/original_near_bird_heading_forecast_v43.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\\n"
    with tempfile.NamedTemporaryFile(mode="w",dir=args.out.parent,encoding="utf-8",
        prefix=".v43-original-",delete=False) as f:
        f.write(payload);temp=Path(f.name)
    os.replace(temp,args.out)
    print("V43_PRIOR_ORIGINAL_RECEIPTS",json.dumps(out["frozen_v41_v42_v33_v39_v40_all_source_receipts"],sort_keys=True))
    print("V43_200M_SOURCE_OPPORTUNITIES",json.dumps(out["source_spatial_neighbor_time_support_before_behavior_score"],sort_keys=True))
    print("V43_STATUS",out["status"])
    effect=out["observed_near_bird_direction_forecast"]
    if effect.get("all_fixed_signed_vector_comparisons"):
        print("V43_ABSOLUTE_VECTOR_MSE",json.dumps(effect["equal_bird_vector_MSE_S0_S1_S2_S3"]))
        print("V43_ALL_VECTOR_CONTRASTS",json.dumps(effect["all_fixed_signed_vector_comparisons"],sort_keys=True))
        angle=effect["secondary_fixed_moving_targets_angular_evaluation"]
        print("V43_ANGULAR_SUPPORT",json.dumps(angle.get("support"),sort_keys=True))
        if angle.get("all_registered_angular_contrasts"):
            print("V43_ALL_ANGULAR_CONTRASTS",json.dumps(angle["all_registered_angular_contrasts"],sort_keys=True))
    else:print("V43_NO_SOCIAL_PREDICTIVE_SCORE",json.dumps(effect,sort_keys=True))
    print("V43_ANONYMOUS_COMPLETE_JSON",json.dumps(out,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
