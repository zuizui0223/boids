#!/usr/bin/env python3
"""v45-B exact geometric mirror-turn null for already observed v45 wild heading.

Post-outcome, not a new wild field population. Keep same v45 17 bird/4660
original motion events; preserve all prior source/observed numerical receipts.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for path in ("validation_v45","validation_v44","validation_v43","validation_v40",
             "validation_v42","validation_v41","validation_v39","validation_v34",
             "validation_v33","validation_v32"):
    sys.path.insert(0,str(ROOT/path))
import turning_convergence as v45
import conditional_history as v39
import ebb_flood_height_matched as old
import tidal_forecast as tide
import forecast as original

PROTO="docs/V45B_EXACT_GEOMETRIC_ROTATION_NULL_PROTOCOL.md"
OLD_SOURCE=ROOT/"validation_v45/results/original_near_far_turning_convergence_v45.json"
BOOT=10000
SEED=20261031
MIN_HEIGHT_STRATUM_BIRDS=10
MIN_PER_STRATUM_BIRD=10
MIN_STRATUM_EPISODES=1000
MEASURES=(
    "PRIMARY_NEAR_MINUS_FAR_EXCESS_AFTER_SYMMETRIC_TURN",
    "secondary_ORIGINAL_v45_RAW_NEAR_MINUS_FAR",
    "secondary_GEOMETRIC_MIRROR_EXPECTATION",
    "secondary_INITIAL_NEAR_MINUS_FAR_HEADING_ALIGNMENT_B",
    "secondary_ORIGINAL_COSINE_FOCAL_TURN",
    "secondary_NEAR_ONLY_EXCESS",
    "secondary_FAR_ONLY_EXCESS")

def replay_exact_prior_v45_then_keep_vectors(files,astronomy,tideqa):
    pinned,Y,dist,X40,near,far,originalidx,old_receipt=v45.source_replay(
        files,astronomy,tideqa)
    idx,turn,n,f,qa=v45.direction_ready(
        pinned,Y,dist,X40,near,far,originalidx)
    old_observed=v45.evaluate(pinned,idx,turn,n,f,qa)
    old_saved=json.loads(OLD_SOURCE.read_text(encoding="utf-8"))
    required={
        "status":old_observed["status"],
        "protocol":v45.PROTOCOL,
        "complete_old_v41_v42_v33_v39_v40_v43_v44_receipt":old_receipt,
        "original_untouched_v44_matched_source_opportunities":len(originalidx),
        "observed_orientation_association":old_observed,
        "precommitted_distance_threshold_m":50,
        "precommitted_mean_other_bird_direction_resultant_threshold":v45.MIN_OTHER_RESULTANT,
        "previous_v29_to_v44_source_and_numerical_results_unchanged":True,
        "no_original_animal_ID_GPS_UTC_position_heading_or_tide_heights_published":True,
    }
    if set(required)-set(old_saved):
        raise ValueError("Frozen original v45 report keys changed")
    for key,value in required.items():
        if not old.nested_close(value,old_saved.get(key),1e-12):
            raise ValueError("Frozen v45 source or all-bird numerical result drift: "+key)
    if (old_observed["status"]!="EXPLORATORY_WILD_NEAR_VS_FAR_FOCAL_TURNING_CONVERGENCE"
        or old_observed["support"]["source_birds_with_10plus_original_direction_episodes"]!=17
        or old_observed["support"]["original_direction_episodes_in_admitted_whole_birds"]!=4660
        or len(idx)!=4667):
        raise ValueError("Original v45 17 birds / 4660 eligible future steps source changed")
    # Static saved source/caution keys must retain exact shapes; numerical source
    # effects were independently re-run above, never inferred from JSON alone.
    if "Zenodo 10053970 v4" not in old_saved.get("source",""):
        raise ValueError("Original v45 source provenance changed")
    if not isinstance(old_saved.get("limits"),list):
        raise ValueError("Original v45 limitations absent")
    return pinned,X40,idx,turn,n,f,{
       "status":"OLD_FULL_V45_17_BIRD_4660_AND_V44_V43_V41_SOURCE_REPLAY_MATCH",
       "all_original_17_whole_bird_convergence_and_100_shams_reproduced":True,
       "original_v45_admitted_whole_birds":17,
       "original_v45_admitted_directional_steps":4660,
       "original_all_direction_reliable_future_step_rows":len(idx),
       "previous_numerical_abs_tolerance":1e-12,
       "old_source_anonymized_per_bird_results_UNCHANGED":True}

def rotate_decompose(previous,nextunit,near,far):
    """Analytic exact decomposition, independent of fitted statistical model.

    Symmetric equal-probability left/right turn null keeps |turn angle| and
    previous heading fixed. Its mean C is (cos(angle)-1)*initial alignment B.
    """
    previous=np.asarray(previous,float)
    nextunit=np.asarray(nextunit,float)
    near=np.asarray(near,float)
    far=np.asarray(far,float)
    if previous.ndim!=2 or previous.shape[1]!=2 or any(
       x.shape!=previous.shape for x in (nextunit,near,far)):
        raise ValueError("Frozen unit 2D GPS direction source shape mismatch")
    if len(previous)==0:return np.empty((0,7)),{"max_algebra_error":0.,"max_mirror_error":0.}
    if (np.max(np.abs(np.linalg.norm(previous,axis=1)-1))>1e-8 or
        np.max(np.abs(np.linalg.norm(nextunit,axis=1)-1))>1e-8 or
        np.max(np.abs(np.linalg.norm(near,axis=1)-1))>1e-8 or
        np.max(np.abs(np.linalg.norm(far,axis=1)-1))>1e-8):
        raise ValueError("Source previous/next/near/far heading not unit")
    direction=near-far
    perp=np.column_stack((-previous[:,1],previous[:,0]))
    cos_angle=np.clip(np.sum(nextunit*previous,axis=1),-1,1)
    sin_angle=np.sum(nextunit*perp,axis=1)
    initial=np.sum(previous*direction,axis=1)
    observed=np.sum((nextunit-previous)*direction,axis=1)
    expectation=(cos_angle-1)*initial
    residual=observed-expectation
    residual_direct=sin_angle*np.sum(perp*direction,axis=1)
    mirrored_next=cos_angle[:,None]*previous-sin_angle[:,None]*perp
    mirror_observed=np.sum((mirrored_next-previous)*direction,axis=1)
    expected_as_mean=(observed+mirror_observed)/2
    near_excess=np.sum((nextunit-previous)*near,axis=1)-(
          cos_angle-1)*np.sum(previous*near,axis=1)
    far_excess=np.sum((nextunit-previous)*far,axis=1)-(
          cos_angle-1)*np.sum(previous*far,axis=1)
    differences=np.array([
        np.max(np.abs(residual-residual_direct)),
        np.max(np.abs(expectation-expected_as_mean)),
        np.max(np.abs(residual-(near_excess-far_excess)))
    ])
    if differences.max()>1e-12:
        raise ValueError("Exact mirror-turn/inertial-angle algebra identity violated")
    return np.column_stack([
       residual,observed,expectation,initial,cos_angle,near_excess,far_excess]),{
       "max_per_episode_difference_analytic_vs_directional_residual":float(differences[0]),
       "max_per_episode_mirror_mean_vs_geometric_expectation":float(differences[1]),
       "max_per_episode_NEAR_minus_FAR_excess_identity":float(differences[2]),
       "original_source_focal_signed_turns_never_permuted_or_refitted":True}

def bird_boot(vals,draw):
    x=np.asarray(vals,float)
    positive=int(np.sum(x>0));nonzero=int(np.sum(x!=0))
    return {"equal_original_bird_mean":float(np.mean(x)),
       "paired_bird_bootstrap95":list(map(float,np.quantile(
                    x[draw].mean(axis=1),[.025,.975]))),
       "positive_source_birds":positive,
       "negative_source_birds":int(np.sum(x<0)),
       "exact_one_sided_positive_bird_sign_p":v39.sign_tail(positive,nonzero),
       "whole_original_animal_inference_unit":True}

def initial_alignment_strata(pinned,idx,admitted,values):
    strata={}
    for label,sign in (("INITIAL_NEAR_MORE_ALIGNED_B_POSITIVE",1),
                       ("INITIAL_FAR_MORE_OR_EQUAL_B_NONPOSITIVE",0)):
        arrs={}
        for bird,positions in admitted.items():
            x=values[positions,3]
            indices=positions[x>0] if sign else positions[x<=0]
            if len(indices)>=MIN_PER_STRATUM_BIRD:arrs[bird]=indices
        count=sum(len(x) for x in arrs.values())
        support={"original_birds_with_10plus_stratum_episodes":len(arrs),
            "original_stratum_episodes_in_admitted_birds":count,
            "preset_first_contact_B_positive":bool(sign),
            "source_bird_min":MIN_HEIGHT_STRATUM_BIRDS,
            "source_episode_min":MIN_STRATUM_EPISODES}
        if len(arrs)<MIN_HEIGHT_STRATUM_BIRDS or count<MIN_STRATUM_EPISODES:
            strata[label]={"status":"NOT_ADMITTED_INITIAL_ALIGNMENT_STRATUM_SOURCE_SUPPORT",
                           "support":support,"any_stratum_effect_exported":False}
            continue
        birds=sorted(arrs)
        v=np.array([[float(np.mean(values[arrs[b],k])) for k in (0,1,2)]
                    for b in birds])
        resample=np.random.default_rng(SEED).integers(0,len(birds),size=(BOOT,len(birds)))
        strata[label]={"status":"EXPLORATORY_ORIGINAL_INITIAL_ALIGNMENT_STRATUM",
            "support":support,
            "EXCESS_AFTER_GEOMETRIC_NULL":bird_boot(v[:,0],resample),
            "RAW_original_convergence":bird_boot(v[:,1],resample),
            "GEOMETRIC_expected":bird_boot(v[:,2],resample)}
    return strata

def evaluate(pinned,idx,values,algebra_qa):
    admitted,selected,months,years,old_gate=v45.eligible_birds(pinned,idx)
    support={
      "original_17_bird_v45_matched_source_support":old_gate,
      "frozen_original_17_birds_4660_future_directional_episodes_verified":
        len(admitted)==17 and len(selected)==4660,
      "all_episode_exact_rotation_algebra":algebra_qa}
    if len(admitted)!=17 or len(selected)!=4660 or len(months)!=11 or years!=[2010,2011]:
        return {"status":"NOT_ADMITTED_FROZEN_V45_GEOMETRIC_NULL_SOURCE_SUPPORT",
                "support":support,"any_new_excess_turning_effect_reported":False}
    birds=sorted(admitted)
    matrix=np.array([np.mean(values[admitted[b]],axis=0) for b in birds])
    draw=np.random.default_rng(SEED).integers(0,len(birds),size=(BOOT,len(birds)))
    estimates={name:bird_boot(matrix[:,k],draw) for k,name in enumerate(MEASURES)}
    # Mandatory same v45 primary should match original source result to 1e-12.
    frozen=json.loads(OLD_SOURCE.read_text())["observed_orientation_association"]
    old_mu=frozen["all_three_frozen_signed_estimands"][
          "PRIMARY_NEAR_MINUS_FAR_TURN_CONVERGENCE"]["equal_bird_mean"]
    if abs(estimates[MEASURES[1]]["equal_original_bird_mean"]-old_mu)>1e-12:
        raise ValueError("Geometric source reconstruction changed original v45 primary C")
    yearlist=[]
    for yr in years:
        per=[]
        count=0
        for bird in birds:
            position=[i for i in admitted[bird] if
                      int(str(pinned["start"][idx[i]])[:4])==yr]
            if position:
                per.append(np.mean(values[position,:3],axis=0))
                count+=len(position)
        yy=np.mean(per,axis=0)
        yearlist.append({"original_source_year":yr,
           "whole_birds_with_future_steps":len(per),
           "original_orientation_episodes":count,
           "equal_bird_EXCESS_C_RAW_C_GEOMETRIC_C":list(map(float,yy))})
    monthmeans=[]
    for month in months:
        pos=[p for p in selected if str(pinned["start"][idx[p]])[:7]==month]
        monthmeans.append(float(np.mean(values[pos,0])))
    m=np.array(monthmeans)
    bs=np.random.default_rng(SEED).integers(0,len(months),size=(BOOT,len(months)))
    return {"status":"EXPLORATORY_FOCAL_TURN_SYMMETRIC_GEOMETRIC_NULL",
      "support":support,
      "primary_residual_orientation_formula":"C_obs-(cosδ-1)*prior·(NEAR−FAR)",
      "source_per_episode_exact_algebraic_identity_within_1e_12":True,
      "all_prespecified_primary_and_secondary_whole_bird_effects":estimates,
      "source_original_initial_NEAR_vs_FAR_relative_alignment_strata":
          initial_alignment_strata(pinned,idx,admitted,values),
      "original_source_years_no_favorable_selection":yearlist,
      "calendar_month_descriptive":{
         "original_source_months":len(months),
         "equal_month_excess_not_equal_bird_primary":float(m.mean()),
         "naive_month_bootstrap95_source_shared":list(map(float,
                         np.quantile(m[bs].mean(axis=1),[.025,.975]))),
         "month_shared_birds_weather_and_roosts_NOT_independent":True},
      "anonymous_whole_original_bird_geometry":{
         f"bird_{i+1:03d}":{
           "original_source_directional_episodes":len(admitted[b]),
           "EXCESS":float(matrix[i,0]),
           "RAW_original":float(matrix[i,1]),
           "GEOMETRIC_symmetric_turn_null":float(matrix[i,2]),
           "INITIAL_align_NEAR_minus_FAR_B":float(matrix[i,3]),
           "COS_of_actual_turn":float(matrix[i,4])}
         for i,b in enumerate(birds)},
      "bootstrap_reps":BOOT,"rng_seed":SEED,
      "one_nonrandom_Wadden_Sea_population_NOT_society_causal_identification":True}

def run():
    astronomy,sourceyear=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as directory:
        files=original.original_files_to_temp(Path(directory))
        pinned,X40,idx,turn,n,f,previous=replay_exact_prior_v45_then_keep_vectors(
            files,astronomy,sourceyear)
    u_before=X40[idx,-2:]
    u_after=u_before+turn
    values,algebra=rotate_decompose(u_before,u_after,n,f)
    result=evaluate(pinned,idx,values,algebra)
    return {"status":result["status"],
       "source":"Original v45 wild GPS, seven original Zenodo 10053970 v4 years and RWS astronomical tide",
       "protocol":PROTO,
       "all_original_v41_through_v45_source_and_17_bird_results_replayed":previous,
       "geometric_mirror_turn_analytic_identity":algebra,
       "observed_original_source_geometric_rotation_residual":result,
       "all_original_v29_to_v45_GitHub_source_results_unchanged":True,
       "no_original_bird_ID_position_UTC_GPS_bearing_or_RWS_water_height_redistributed":True,
       "limitations":[
          "Postoutcome geometric diagnostic after v45 raw negative near/far heading convergence",
          "Symmetric left/right turn null conditions on observed original turn magnitude, not an intervention",
          "Nonzero excess cannot isolate wind, prey routes, roosting, shore geometry or social intention",
          "Same one original coastal field study; whole-bird bootstrap not independent geographic replication",
          "Previous focal/future GPS segments are disjoint but source GPS observation process remains serially correlated",
          "No altitude, foraging state or Reynolds social alignment/cohesion/separation forces identified"]}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,
        default=Path("validation_v45b/results/original_wild_mirror_turn_geometric_null_v45b.json"))
    args=parser.parse_args()
    j=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(j,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
          prefix=".v45b-",delete=False) as f:
        f.write(payload);out=Path(f.name)
    os.replace(out,args.out)
    print("V45B_ALL_PRIOR_SOURCE_AND_ORIGINAL_V45_SCORE_REPLAY",json.dumps(
          j["all_original_v41_through_v45_source_and_17_bird_results_replayed"],sort_keys=True))
    print("V45B_EXACT_SOURCE_TURNING_ALGEBRA",json.dumps(j["geometric_mirror_turn_analytic_identity"],sort_keys=True))
    effect=j["observed_original_source_geometric_rotation_residual"]
    print("V45B_STATUS",j["status"])
    if effect.get("all_prespecified_primary_and_secondary_whole_bird_effects"):
        print("V45B_GEOMETRIC_NULL_AND_EXCESS",json.dumps(
          effect["all_prespecified_primary_and_secondary_whole_bird_effects"],sort_keys=True))
        print("V45B_INITIAL_ALIGNMENT_STRATA",json.dumps(
          effect["source_original_initial_NEAR_vs_FAR_relative_alignment_strata"],sort_keys=True))
    else:print("V45B_NO_NEW_GEOMETRIC_EFFECT_SCORED",json.dumps(effect,sort_keys=True))
    print("V45B_COMPLETE_ANON_SOURCE_SAFE_JSON",json.dumps(j,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
