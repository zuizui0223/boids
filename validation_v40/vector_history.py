#!/usr/bin/env python3
"""v40 original GPS: previous direction beyond previous speed and tidal environment.

This is an observational exploratory next-RECORDED-step 2D vector forecast,
not cognition/Boids force estimation and not a free-running location forecast.
All original v33-D AND v39 numerical source receipts must replay identically.
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
sys.path.insert(0,str(ROOT/"validation_v39"))
sys.path.insert(0,str(ROOT/"validation_v34"))
sys.path.insert(0,str(ROOT/"validation_v33"))
sys.path.insert(0,str(ROOT/"validation_v32"))
import conditional_history as last
import ebb_flood_height_matched as old
import phase_response as phase
import tidal_forecast as tide
import forecast as source

PROTOCOL="docs/V40_PRIVATE_DIRECTION_TIDAL_VECTOR_PROTOCOL.md"
V39_ORIGINAL=ROOT/"validation_v39/results/conditional_private_history_over_tide_v39.json"
MODELS=("V0_TIDE_CURRENT_PLUS_PREVIOUS_SPEED",
        "V1_V0_PLUS_PREVIOUS_DISJOINT_HEADING",
        "V2_V0_PLUS_ASTRONOMICAL_TIDE_3H_AGO",
        "V3_V0_PLUS_HEADING_AND_PAST_TIDE")
CONTRASTS=(("PRIMARY_V0_minus_V1",0,1),
           ("SECONDARY_V0_minus_V2",0,2),
           ("SECONDARY_V2_minus_V3",2,3),
           ("SECONDARY_V1_minus_V3",1,3))
ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM=.05
ANGULAR_MIN_PREDICTED_SPEED_KM_H=.05
ANGULAR_MIN_ORIGINAL_BIRDS=20
ANGULAR_MIN_DIRECTIONAL_TARGETS_PER_BIRD=20
ANGULAR_MIN_DIRECTIONAL_TARGETS_TOTAL=10000
VELOCITY_COMPONENT_SCALE_KM_H=1.
RIDGE_ALPHA=25.
BOOT=10000
SEED=20261031
NUM_VECTORS=2
R_EARTH=6371.0088

def spherical_east_north(startlat,startlon,endlat,endlon):
    """Return exact spherical great-circle displacement in km, and heading unit.

    At identical coordinates (true step distance exactly zero) return zero
    vector and zero heading rather than invent an orientation.
    """
    distance=phase.haversine_km(startlat,startlon,endlat,endlon)
    if distance==0.:
        return (0.,0.,0.,0.,0.)
    phi1=math.radians(startlat)
    phi2=math.radians(endlat)
    dl=math.radians(endlon-startlon)
    eastraw=math.sin(dl)*math.cos(phi2)
    northraw=math.cos(phi1)*math.sin(phi2)-math.sin(phi1)*math.cos(phi2)*math.cos(dl)
    bearing=math.atan2(eastraw,northraw)
    e=distance*math.sin(bearing)
    n=distance*math.cos(bearing)
    if not all(map(math.isfinite,(distance,e,n,bearing))):
        raise ValueError("Source spherical displacement nonfinite")
    return e,n,distance,math.sin(bearing),math.cos(bearing)

def old_v39_receipt_replay(original_animal_fixes,astronomy,source_gps_qa,source_tide_qa):
    """STOP if any original v33-D/v39 source, model or bird-level endpoint drifts."""
    pinned=json.loads(V39_ORIGINAL.read_text(encoding="utf-8"))
    if pinned.get("status")!="EXPLORATORY_TIME_FORWARD_TIDE_CONDITIONAL_PRIVATE_HISTORY_FORECAST":
        raise ValueError("Frozen original v39 positive endpoint not found")
    d_receipt=old.replay_original_D(original_animal_fixes,astronomy,source_gps_qa)
    original_data,original_eligibility=last.assemble_original_episodes(original_animal_fixes,astronomy)
    e,f,fold_qa=last.chronological_fit_predict(original_data)
    result=last.summarize(original_data,e,f,fold_qa)
    comparison={
        "source_astronomy_annual_10minute_quality":source_tide_qa,
        "source_original_GPS_QA":source_gps_qa,
        "full_original_v33D_replay_gate":d_receipt,
        "new_original_source_four_nonoverlapping_GPS_fix_eligibility":original_eligibility,
        "chronological_monthwise_prequential_QA":fold_qa,
        "observed_holdout":result,
        "fixed_environment_feature_names_excluding_original_animal_IDs":original_data["feature_names"],
        "monthly_fold_training_source_ranges_not_target_values":[
          {"year":x["year"],"month":x["month"],
           "count_original_scored_next_steps":x["target_rows"],
           "number_training_original_steps_before_7day_embargo":x["prior_training_rows"],
           "source_training_birds":x["prior_original_training_birds"]}
          for x in f],
    }
    for key,val in comparison.items():
        if not old.nested_close(val,pinned.get(key),1e-12):
            raise ValueError("Frozen v39 original source/speed numerical receipt DRIFT: "+key)
    return original_data,e,{
      "status":"FULL_FROZEN_V39_AND_V33D_SOURCE_PER_BIRD_RECEIPT_MATCH",
      "abs_tolerance":1e-12,
      "v39_original_birds":result["support"]["whole_original_birds_in_eligible_score"],
      "v39_original_future_step_episodes":result["support"]["original_test_step_episodes_in_eligible_birds"],
      "v33D_original_gauge_matched_birds":d_receipt["original_source_whole_birds"],
      "v33D_original_clock_month_strata":d_receipt["original_bird_month_clock_strata"],
      "same_original_source_and_all_original_anonymous_results":True,
    }

def vector_source_target_rows(original_fixes,astronomy,pinned_v39):
    """Reconstruct identical v39 episodes and only then expose new vector labels.

    New rows contain only private intermediate values; none are exported.
    """
    bybird={}
    for b,rec in itertools.groupby(sorted(original_fixes,key=lambda x:(x[0],x[1])),
                                    key=lambda x:x[0]):
        bybird[b]=list(rec)
    id_mapping={b:i for i,b in enumerate(sorted(bybird))}
    rows=[]
    qa=collections.Counter()
    for bird,fixes in bybird.items():
        inside=[phase.haversine_km(lat,lon,phase.STATION_LAT,phase.STATION_LON)<=last.SOURCE_RADIUS_KM
                for _,_,lat,lon in fixes]
        for i in range(2,len(fixes)-1):
            x,reason=last.episode_eligibility(fixes,i,inside,astronomy)
            if reason:continue
            old0,old1,new0,new1=(fixes[k] for k in last.four_original_fix_indices(i))
            prev_e,prev_n,prev_d,prev_s,prev_c=spherical_east_north(old0[2],old0[3],
                                                                  old1[2],old1[3])
            east,north,d,s,c=spherical_east_north(new0[2],new0[3],new1[2],new1[3])
            hours=(new1[1]-new0[1]).total_seconds()/3600.
            if not 5./60 <= hours <= 30./60:
                raise ValueError("Original GPS response step duration changed after eligibility")
            response=np.arcsinh(np.array([east,north])/(hours*VELOCITY_COMPONENT_SCALE_KM_H))
            if not np.isfinite(response).all():raise ValueError("Source vector response nonfinite")
            qa["prior_disjoint_zero_distance_GPS_steps"]+=int(prev_d==0.)
            qa["future_zero_distance_GPS_steps"]+=int(d==0.)
            qa["future_steps_with_true_displacement_ge_50m"]+=int(d>=ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM)
            rows.append((x[0],x[1],id_mapping[bird],x[3],x[6],prev_s,prev_c,
                         float(response[0]),float(response[1]),float(d)))
    rows.sort(key=lambda r:r[0])
    if len(rows)!=len(pinned_v39["y"]):
        raise ValueError("Original v39 future GPS episode count changed")
    n=len(rows)
    Y=np.empty((n,2),dtype=float)
    prev_heading=np.empty((n,2),dtype=float)
    distance=np.empty(n,dtype=float)
    for k,row in enumerate(rows):
        start,end,bird,prior_speed,target_speed,ps,pc,ye,yn,d=row
        if (np.datetime64(start,"us")!=pinned_v39["start"][k] or
            np.datetime64(end,"us")!=pinned_v39["end"][k] or
            bird!=int(pinned_v39["bird"][k]) or
            abs(target_speed-pinned_v39["y"][k])>1e-11 or
            abs(prior_speed-pinned_v39["X"][k,-3])>1e-11):
            raise ValueError("Original v39 source episode/date/bird/target/prior-speed mismatch")
        Y[k]=ye,yn
        prev_heading[k]=ps,pc
        distance[k]=d
    if not np.isfinite(Y).all() or not np.isfinite(prev_heading).all():
        raise ValueError("Nonfinite source GPS vector or prior heading")
    if np.any(np.linalg.norm(prev_heading,axis=1)>1.00000000001):
        raise ValueError("Impossible source prior bearing norm")
    qa["v39_original_eligible_episodes_matching_all_prior_and_future_sources"]=n
    qa["new_directional_label_computation_without_original_GPS_overlap"]=True
    qa["no_future_displacement_or_duration_in_model_features"]=True
    return Y,prev_heading,distance,dict(qa)

def model_matrix(pinned,previous_heading):
    X=np.column_stack([pinned["X"],previous_heading])
    e1=pinned["model_indices"][last.MODELS[1]]
    e3=pinned["model_indices"][last.MODELS[3]]
    sh=np.array([X.shape[1]-2,X.shape[1]-1],dtype=int)
    indices={
       MODELS[0]:e1,
       MODELS[1]:np.append(e1,sh),
       MODELS[2]:e3,
       MODELS[3]:np.append(e3,sh),
    }
    if len(indices[MODELS[0]])+2!=len(indices[MODELS[1]]):
        raise ValueError("Original baseline prior-speed features changed")
    return X,indices

def fit_multiple(gram,xy,cols):
    if cols[0]!=0:raise ValueError("Original intercept no longer first")
    matrix=gram[np.ix_(cols,cols)].copy()
    diag=np.full(len(cols),RIDGE_ALPHA)
    diag[0]=0.
    matrix[np.diag_indices_from(matrix)]+=diag
    beta=np.linalg.solve(matrix,xy[cols,:])
    if beta.shape!=(len(cols),NUM_VECTORS) or not np.isfinite(beta).all():
        raise ValueError("Invalid original multi-output ridge")
    return beta

def angular_loss(truth,estimate,movement_distance):
    """1-cos target-vs-pred bearing on a fixed 50m minimum moving subset.

    Low predicted speed is scored as LOSS 1, never dropped to make model better.
    Target distance mask is evaluation-only and is common to all models.
    """
    tr=np.sinh(np.asarray(truth))
    pr=np.sinh(np.asarray(estimate))
    dist=np.asarray(movement_distance)
    target_mask=dist>=ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM
    loss=np.full(len(dist),np.nan,dtype=float)
    if target_mask.any():
        tv=tr[target_mask]
        pv=pr[target_mask]
        t_norm=np.linalg.norm(tv,axis=1)
        p_norm=np.linalg.norm(pv,axis=1)
        ok=(p_norm>=ANGULAR_MIN_PREDICTED_SPEED_KM_H)
        sel=np.ones(int(target_mask.sum()),dtype=float)
        if ok.any():
            cos=np.sum(tv[ok]*pv[ok],axis=1)/(t_norm[ok]*p_norm[ok])
            sel[ok]=1.-np.clip(cos,-1.,1.)
        loss[target_mask]=sel
    return loss

def chronological_vector_forecast(pinned,X,Y,dist,cols):
    """Equivalent train/test dates and 7d original embargo to frozen v39."""
    start,end,bird=[pinned[k] for k in ("start","end","bird")]
    order=np.argsort(end)
    cursor=0
    gram=np.zeros((X.shape[1],X.shape[1]),dtype=float)
    xy=np.zeros((X.shape[1],2),dtype=float)
    train_birds=set()
    errs=np.full((len(Y),len(MODELS)),np.nan)
    angles=np.full((len(Y),len(MODELS)),np.nan)
    folds=[]
    qa=collections.Counter()
    for month in last.month_starts():
        first=np.datetime64(month,"us")
        following=dt.datetime(month.year+(month.month==12),(month.month%12)+1,1)
        lastday=np.datetime64(following,"us")
        cutoff=last.month_train_cutoff(month)
        idxstart=cursor
        while cursor<len(order) and end[order[cursor]]<cutoff:
            cursor+=1
        if cursor>idxstart:
            ix=order[idxstart:cursor]
            block=X[ix]
            gram+=block.T@block
            xy+=block.T@Y[ix]
            train_birds.update(int(z) for z in bird[ix])
        monthidx=np.where((start>=first)&(start<lastday))[0]
        if not len(monthidx):
            qa["no_original_future_step_this_month"]+=1
            continue
        if cursor<last.TRAINING_MIN_EPISODES or len(train_birds)<last.TRAINING_MIN_BIRDS:
            qa["month_failed_original_frozen_training_support"]+=1
            continue
        if np.any(end[order[:cursor]]>=cutoff):
            raise ValueError("Original source heldout label contaminated 7-day embargo")
        angmask=dist[monthidx]>=ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM
        for mi,mode in enumerate(MODELS):
            mcols=cols[mode]
            beta=fit_multiple(gram,xy,mcols)
            predictions=X[np.ix_(monthidx,mcols)]@beta
            errs[monthidx,mi]=np.sum((Y[monthidx]-predictions)**2,axis=1)
            angles[monthidx,mi]=angular_loss(Y[monthidx],predictions,dist[monthidx])
        if not np.isfinite(errs[monthidx]).all():
            raise ValueError("Nonfinite original vector forecast errors")
        if not np.isfinite(angles[monthidx][angmask]).all():
            raise ValueError("Invalid directional-only angular prediction loss")
        if np.isfinite(angles[monthidx][~angmask]).any():
            raise ValueError("Angular evaluation exposed stationary target")
        folds.append({"year":month.year,"month":month.month,"future_target_steps":len(monthidx),
                      "original_training_steps_before_7day_embargo":cursor,
                      "previous_original_bird_ID_count":len(train_birds)})
        qa["months_tested"]+=1
        qa["scored_future_original_vector_steps"]+=len(monthidx)
    return errs,angles,folds,dict(qa)

def evaluate_equal_birds(pinned,errors,angles,folds,qa):
    good=np.where(np.isfinite(errors).all(axis=1))[0]
    orig={int(b):np.array([i for i in good if pinned["bird"][i]==b],dtype=int)
          for b in sorted(set(map(int,pinned["bird"][good])))}
    eligible={b:idx for b,idx in orig.items() if len(idx)>=last.MIN_EPISODES_PER_BIRD}
    included=np.concatenate(list(eligible.values())) if eligible else np.array([],dtype=int)
    yrs=sorted({int(str(pinned["start"][i])[:4]) for i in included})
    months=sorted({str(pinned["start"][i])[:7] for i in included})
    support={"whole_original_birds":len(eligible),
       "eligible_future_step_vector_labels":len(included),
       "original_birds_before_min_30":len(orig),
       "source_tested_months":len(months),"source_tested_years":yrs,
       "required_birds":last.MIN_SCOREABLE_BIRDS,"required_episodes":last.MIN_TARGET_EPISODES,
       "required_years":last.MIN_YEARS,"required_months":last.MIN_MONTHS}
    if (len(eligible)<last.MIN_SCOREABLE_BIRDS or len(included)<last.MIN_TARGET_EPISODES
       or len(yrs)<last.MIN_YEARS or len(months)<last.MIN_MONTHS):
        return {"status":"NOT_ADMITTED_SOURCE_ORIGINAL_VECTOR_FORECAST_COHORT",
                "support":support,"any_vector_or_angular_model_scores_reported":False}
    birds=sorted(eligible)
    mat=np.array([np.mean(errors[eligible[b]],axis=0) for b in birds])
    if not np.isfinite(mat).all():raise ValueError("Nonfinite original heldout vector bird scores")
    bootstrap=np.random.default_rng(SEED).integers(0,len(birds),size=(BOOT,len(birds)))
    gains={}
    for name,i,j in CONTRASTS:
        diff=mat[:,i]-mat[:,j]
        k=int((diff>0).sum())
        n=int((diff!=0).sum())
        gains[name]={"equal_bird_2D_vector_MSE_gain":float(np.mean(diff)),
           "whole_bird_bootstrap_95":list(map(float,np.quantile(diff[bootstrap].mean(axis=1),[.025,.975]))),
           "original_birds_positive":k,"original_birds_negative":int((diff<0).sum()),
           "nonzero_original_birds":n,"one_sided_positive_bird_sign_p":last.sign_tail(k,n)}
    ang_birds={b:eligible[b][np.isfinite(angles[eligible[b],0])]
               for b in birds}
    directional={b:ix for b,ix in ang_birds.items()
                 if len(ix)>=ANGULAR_MIN_DIRECTIONAL_TARGETS_PER_BIRD}
    angular_support={"birds_with_20plus_directional_steps":len(directional),
       "original_displacements_of_50m_plus_in_admitted_birds":sum(len(ix) for ix in directional.values()),
       "minimum_true_future_displacement_km":ANGULAR_MIN_TRUE_FUTURE_DISPLACEMENT_KM,
       "neutral_loss_when_predicted_velocity_lt_km_h":ANGULAR_MIN_PREDICTED_SPEED_KM_H,
       "same_directional_targets_all_four_models":True}
    if (len(directional)>=ANGULAR_MIN_ORIGINAL_BIRDS and
        angular_support["original_displacements_of_50m_plus_in_admitted_birds"]>=ANGULAR_MIN_DIRECTIONAL_TARGETS_TOTAL):
        abirds=sorted(directional)
        amat=np.array([np.mean(angles[directional[b]],axis=0) for b in abirds])
        arng=np.random.default_rng(SEED).integers(0,len(abirds),size=(BOOT,len(abirds)))
        agains={}
        for name,i,j in CONTRASTS:
            diff=amat[:,i]-amat[:,j]
            k=int((diff>0).sum());n=int((diff!=0).sum())
            agains[name]={"equal_bird_angular_1_minus_cosine_loss_gain":float(np.mean(diff)),
              "whole_bird_bootstrap_95":list(map(float,np.quantile(diff[arng].mean(axis=1),[.025,.975]))),
              "birds_positive":k,"birds_negative":int((diff<0).sum()),
              "one_sided_positive_bird_sign_p":last.sign_tail(k,n)}
        angular={"status":"SECONDARY_ANGULAR_EVALUATION_ADMITTED",
          "support":angular_support,"equal_bird_angular_1_minus_cosine_absolute_loss":list(map(float,amat.mean(axis=0))),
          "all_frozen_angular_secondary_comparisons":agains}
    else:
        angular={"status":"NOT_ADMITTED_ANGULAR_DIRECTION_SUPPORT",
                 "support":angular_support,"any_angular_effect_reported":False}
    annual=[]
    for year in yrs:
        per=[]
        for b in birds:
            ix=np.array([i for i in eligible[b] if int(str(pinned["start"][i])[:4])==year],dtype=int)
            if len(ix):per.append(np.mean(errors[ix],axis=0))
        if per:
            z=np.array(per)
            annual.append({"year":year,"original_birds":len(per),
               "original_heldout_steps":sum(int(str(pinned["start"][i])[:4])==year for i in included),
               "equal_bird_MSE_V0_V1_V2_V3":list(map(float,z.mean(axis=0))),
               "V0_minus_V1_gain":float(np.mean(z[:,0]-z[:,1])),
               "source_one_coastal_population":True})
    permonth=[]
    for period in months:
        ix=np.array([i for i in included if str(pinned["start"][i])[:7]==period],dtype=int)
        if len(ix):permonth.append(float(np.mean(errors[ix,0]-errors[ix,1])))
    ps=np.array(permonth)
    dr=np.random.default_rng(SEED).integers(0,len(ps),size=(BOOT,len(ps)))
    month_effect={"source_months":len(ps),
      "equal_calendar_month_gain_differs_from_equal_bird_estimator":float(np.mean(ps)),
      "naive_calendar_month_bootstrap95_descriptive_only":list(map(float,np.quantile(ps[dr].mean(axis=1),[.025,.975]))),
      "shared_climate_same_birds_nonindependent_months":True}
    return {"status":"EXPLORATORY_TIME_FORWARD_PRIVATE_HEADING_VECTOR_FORECAST",
      "support":support,
      "registered_model_order":list(MODELS),
      "primary_response":"sum squared asinh east and north km/h residuals, entire original heldout v39 cohort",
      "equal_bird_2D_vector_MSE_V0_V1_V2_V3":list(map(float,mat.mean(axis=0))),
      "all_prespecified_vector_MSE_contrasts":gains,
      "secondary_angular_target_only_when_true_step_distance_ge_50m":angular,
      "all_years_descriptive":annual,"month_level_descriptive":month_effect,
      "anonymous_per_original_bird_vector_MSE":{
          f"bird_{i+1:03d}":{"original_heldout_steps":len(eligible[b]),
             "vector_MSE_V0_V1_V2_V3":list(map(float,mat[i]))}
          for i,b in enumerate(birds)},
      "bird_resample_reps":BOOT,"rng_seed":SEED,
      "reused_original_v39_heldout_target_episodes":True,
      "no_raw_original_animal_GPS_coords_ID_or_UTC_episodes_exported":True}

def run():
    astronomy,tide_qa=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as directory:
        original_files=source.original_files_to_temp(Path(directory))
        points,gps_qa=phase.read_original_valid_gps(original_files)
    prev,prev_err,replay=old_v39_receipt_replay(points,astronomy,gps_qa,tide_qa)
    vector,prior_heading,displacement,source_qa=vector_source_target_rows(points,astronomy,prev)
    X,indices=model_matrix(prev,prior_heading)
    errors,angles,folds,fold_qa=chronological_vector_forecast(prev,X,vector,displacement,indices)
    # Require unchanged original test rows and month-to-month training support.
    expected=np.isfinite(prev_err).all(axis=1)
    new=np.isfinite(errors).all(axis=1)
    if not np.array_equal(expected,new):
        raise ValueError("New directional test cohort differs from frozen original v39 future steps")
    saved=json.loads(V39_ORIGINAL.read_text())
    if fold_qa.get("months_tested")!=saved["chronological_monthwise_prequential_QA"]["source_UTC_months_scored"]:
        raise ValueError("Original v39 source future-month support changed")
    observed=evaluate_equal_birds(prev,errors,angles,folds,fold_qa)
    if observed["status"]=="EXPLORATORY_TIME_FORWARD_PRIVATE_HEADING_VECTOR_FORECAST":
        if (observed["support"]["whole_original_birds"]!=21 or
            observed["support"]["eligible_future_step_vector_labels"]!=305257):
            raise ValueError("Original heldout v39 cohort changed despite source replay")
    return {"status":observed["status"],
      "study":"v40 original wild oystercatcher private disjoint heading beyond past speed/tide",
      "protocol":PROTOCOL,
      "original_bird_source":"Zenodo 10053970 v4; full 7 years original SHA-pinned GPS",
      "original_astronomical_tide":"RWS official schiermonnikoog.waddenzee WATHTE cm NAP, 2008-2014",
      "source_RWS_annual_10min_original_quality":tide_qa,
      "source_GPS_original_integrity_and_quality":gps_qa,
      "strict_source_old_v33D_and_v39_full_replay":replay,
      "original_vector_eligible_4fix_source_support":source_qa,
      "current_and_past_feature_names_from_v39":prev["feature_names"],
      "prespecified_additional_previous_heading_features":["prior_disjoint_original_unit_east","prior_disjoint_original_unit_north"],
      "ridge_alpha":RIDGE_ALPHA,
      "calendar_month_7day_embargo_qa":fold_qa,
      "original_monthwise_holdout_folds":folds,
      "observed_vector_forecast":observed,
      "previous_v29_to_v39_all_old_GitHub_result_receipts_unchanged":True,
      "NO_original_animal_GPS_ID_UTC_positions_or_raw_tides_redistributed":True,
      "important_limits":[
        "Previously opened one Schiermonnikoog source, exploratory after known speed/tide results",
        "Prediction conditional on next original 5-30 minute GPS step materializing; unknown future duration is not a predictor",
        "Source GPS prior and target steps share no fix but site/device errors can remain correlated",
        "Spherical 2D vector components do not establish 3D altitude or vertical ecological niche",
        "Prior heading incremental information can reflect path inertia, specific corridors, unobserved habitat, wind or measurement artifact rather than memory",
        "Individual heading prediction is not contemporaneous neighbor interaction or causal Reynolds Boids rule",
        "Years 2010-2012 from one field study, not distinct independent ecosystems",
      ]}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,
        default=Path("validation_v40/results/heldout_tidal_private_heading_v40.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    s=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
         prefix=".v40-source-",delete=False) as tmp:
        tmp.write(s); dest=Path(tmp.name)
    os.replace(dest,args.out)
    print("V40_FULL_ORIGINAL_V39_AND_V33_REPLAY",json.dumps(result["strict_source_old_v33D_and_v39_full_replay"],sort_keys=True))
    print("V40_NEW_SOURCE_ELIGIBILITY",json.dumps(result["original_vector_eligible_4fix_source_support"],sort_keys=True))
    print("V40_STATUS",result["status"])
    observed=result["observed_vector_forecast"]
    if observed.get("all_prespecified_vector_MSE_contrasts"):
        print("V40_VECTOR_ABSOLUTE_MSE",json.dumps(observed["equal_bird_2D_vector_MSE_V0_V1_V2_V3"]))
        print("V40_ALL_VECTOR_CONTRASTS",json.dumps(observed["all_prespecified_vector_MSE_contrasts"],sort_keys=True))
        a=observed["secondary_angular_target_only_when_true_step_distance_ge_50m"]
        print("V40_ANGULAR_STATUS",a["status"])
        if a.get("all_frozen_angular_secondary_comparisons"):
            print("V40_ANGULAR_ABSOLUTE_LOSS",json.dumps(a["equal_bird_angular_1_minus_cosine_absolute_loss"]))
            print("V40_ALL_ANGULAR_CONTRASTS",json.dumps(a["all_frozen_angular_secondary_comparisons"],sort_keys=True))
        print("V40_ANNUAL_VECTOR_GAIN",json.dumps(observed["all_years_descriptive"],sort_keys=True))
    else:
        print("V40_NO_VECTOR_EFFECT_SCORED",json.dumps(observed,sort_keys=True))
    print("V40_COMPLETE_AGGREGATE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
