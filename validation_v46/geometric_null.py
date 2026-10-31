#!/usr/bin/env python3
"""v46: source-backed geometric null for observed wild near-vs-far focal turning.

Explicitly POST v45 exploratory. No wild social force inferred. Replay full
v45 and older original animal/tide evidence BEFORE calculating new effects.
"""
from __future__ import annotations
import argparse,collections,datetime as dt,json,os,sys,tempfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
for d in ("validation_v45","validation_v44","validation_v43","validation_v40",
          "validation_v42","validation_v41","validation_v39","validation_v34",
          "validation_v33","validation_v32"):
    sys.path.insert(0,str(ROOT/d))
import turning_convergence as oldv
import ebb_flood_height_matched as check
import conditional_history as past
import tidal_forecast as tide
import forecast as source

OLD=ROOT/"validation_v45/results/original_near_far_turning_convergence_v45.json"
PROTOCOL="docs/V46_GEOMETRIC_INERTIAL_TURNING_NULL_PROTOCOL.md"
N_BIRDS=17
N_STEPS=4660
BOOTS=10000
SHAMS=1000
RNG=20261031
NAMES=("PRIMARY_EXCESS_NF_AFTER_SYMMETRIC_TURN_NULL",
       "SECONDARY_EXCESS_NEAR","SECONDARY_EXCESS_FAR",
       "AUDIT_EXPECTED_GEOMETRIC_NF","AUDIT_OBSERVED_V45_NF")

def original_replay(files,astro,tideqa):
    pinned,Y,dist,X40,near,far,oldcohort,oldreceipt=oldv.source_replay(files,astro,tideqa)
    idx,turn,n,f,quality=oldv.direction_ready(pinned,Y,dist,X40,near,far,oldcohort)
    oldscore=oldv.evaluate(pinned,idx,turn,n,f,quality)
    frozen=json.loads(OLD.read_text(encoding="utf-8"))
    for name,computed in (
       ("observed_orientation_association",oldscore),
       ("complete_old_v41_v42_v33_v39_v40_v43_v44_receipt",oldreceipt)):
        if not check.nested_close(computed,frozen.get(name),1e-12):
            raise ValueError("Original frozen v45 full numerical receipt changed: "+name)
    if len(oldcohort)!=frozen["original_untouched_v44_matched_source_opportunities"]:
        raise ValueError("v44 original model cohort changed")
    admitted,positions,months,years,qualified=oldv.eligible_birds(pinned,idx)
    if (len(admitted)!=N_BIRDS or len(positions)!=N_STEPS
        or oldscore["support"]["source_birds_with_10plus_original_direction_episodes"]!=N_BIRDS
        or oldscore["support"]["original_direction_episodes_in_admitted_whole_birds"]!=N_STEPS):
        raise ValueError("Original 17 wild birds / 4660 direction-eligible steps drift")
    before=X40[:,-2:][idx]
    after=before+turn
    if (np.abs(np.linalg.norm(before[positions],axis=1)-1).max()>1e-10
        or np.abs(np.linalg.norm(after[positions],axis=1)-1).max()>1e-10):
        raise ValueError("Wild before/after heading not unit length")
    receipt={"status":"ORIGINAL_V41_TO_V45_ALL_SOURCE_AND_PER_BIRD_NUMERIC_RECEIPTS_REPLAYED",
       "old_v44_both_other_heading_episodes":len(oldcohort),
       "v45_eligible_candidate_focal_turns":len(idx),
       "v45_original_admitted_birds":len(admitted),
       "v45_original_admitted_future_turns":len(positions),
       "prior_full_source_receipt_abs_tolerance":1e-12,
       "v45_sham_100_source_replayed":True}
    return pinned,idx,before,after,n,f,admitted,positions,receipt,frozen

def geometry(before,after,near,far):
    before=np.asarray(before,float);after=np.asarray(after,float)
    near=np.asarray(near,float);far=np.asarray(far,float)
    if before.shape!=after.shape or before.shape!=near.shape or before.shape!=far.shape or before.ndim!=2 or before.shape[1]!=2:
        raise ValueError("All directional source arrays must be Nx2")
    if not all(np.isfinite(x).all() for x in (before,after,near,far)):
        raise ValueError("Nonfinite direction source")
    d=near-far
    c=np.clip(np.einsum("ij,ij->i",before,after),-1,1)
    B=np.einsum("ij,ij->i",before,d)
    observed=np.einsum("ij,ij->i",after-before,d)
    expected=(c-1)*B
    excess=observed-expected
    residual_direction=after-c[:,None]*before
    near_excess=np.einsum("ij,ij->i",residual_direction,near)
    far_excess=np.einsum("ij,ij->i",residual_direction,far)
    if (not np.allclose(excess,near_excess-far_excess,atol=1e-12,rtol=0)
        or not np.allclose(observed,expected+excess,atol=1e-12,rtol=0)):
        raise ValueError("Symmetric-turn geometric decomposition inconsistent")
    return np.stack((excess,near_excess,far_excess,expected,observed),axis=1),B,c

def bootstrap(values,draw):
    val=np.asarray(values)
    k=int(np.sum(val>0));n=int(np.sum(val!=0))
    return {"equal_whole_bird_mean":float(val.mean()),
       "whole_bird_bootstrap95":list(map(float,np.quantile(val[draw].mean(axis=1),[.025,.975]))),
       "positive_birds":k,"negative_birds":int(np.sum(val<0)),
       "nonzero_birds":n,"one_sided_positive_bird_sign_tail":past.sign_tail(k,n)}

def symmetric_handedness_sham(before,c,n,f,admitted):
    d=n-f
    B=np.einsum("ij,ij->i",before,d)
    perp=np.stack((-before[:,1],before[:,0]),axis=1)
    amplitude=np.sqrt(np.clip(1-c*c,0,1))*np.einsum("ij,ij->i",perp,d)
    geom=(c-1)*B
    birds=sorted(admitted)
    rng=np.random.default_rng(RNG)
    sh_omega=[];sh_residual=[]
    for _ in range(SHAMS):
        sign=rng.choice([-1.,1.],size=len(c))
        ex=sign*amplitude
        sh_residual.append(float(np.mean([ex[admitted[b]].mean() for b in birds])))
        sh_omega.append(float(np.mean([(geom[admitted[b]]+ex[admitted[b]]).mean() for b in birds])))
    return {"status":"SYMMETRIC_1000_HANDEDNESS_SHAM_SOURCE_FREE",
       "sham_repetitions":SHAMS,
       "same_source_observed_turn_magnitudes_and_initial_directions_fixed":True,
       "same_near_far_original_past_bird_headings_fixed":True,
       "mean_sham_C_NF_OBSERVED":float(np.mean(sh_omega)),
       "sham_C_NF_percentile5_95":list(map(float,np.quantile(sh_omega,[.05,.95]))),
       "mean_sham_C_NF_GEOMETRIC_EXCESS":float(np.mean(sh_residual)),
       "sham_EXCESS_percentile5_95":list(map(float,np.quantile(sh_residual,[.05,.95]))),
       "1000_synthetic_draws_NOT_independent_wild_bird_replicates":True}

def score(pinned,idx,before,after,near,far,admitted,positions,old_saved):
    if len(admitted)!=N_BIRDS or len(positions)!=N_STEPS:
        return {"status":"NOT_ADMITTED_GPS_GEOMETRIC_SYMMETRIC_TURN_NULL",
                "birds":len(admitted),"episodes":len(positions),"any_new_effect_reported":False}
    matrix,B,c=geometry(before,after,near,far)
    birds=sorted(admitted)
    rows=np.array([matrix[admitted[b]].mean(axis=0) for b in birds])
    old_bird=old_saved["observed_orientation_association"]["anonymous_bird_mean_convergence"]
    for k in range(len(birds)):
        if abs(rows[k,4]-old_bird[f"bird_{k+1:03d}"]["NEAR_minus_FAR_turn"])>1e-12:
            raise ValueError("Old original v45 per-bird observed turning mean drift")
    old_total=old_saved["observed_orientation_association"]["all_three_frozen_signed_estimands"][oldv.LABELS[0]]["equal_bird_mean"]
    if abs(rows[:,4].mean()-old_total)>1e-12:
        raise ValueError("Old original v45 equal whole bird mean changed")
    draw=np.random.default_rng(RNG).integers(0,len(birds),size=(BOOTS,len(birds)))
    estimates={name:bootstrap(rows[:,i],draw) for i,name in enumerate(NAMES)}
    angle=np.arccos(np.clip(c[positions],-1,1))
    audit={"source_original_episodes":len(positions),
      "original_initial_NEAR_more_aligned_than_FAR":int(np.sum(B[positions]>0)),
      "original_initial_FAR_more_aligned_than_NEAR":int(np.sum(B[positions]<0)),
      "original_initial_NEAR_equal_FAR":int(np.sum(B[positions]==0)),
      "equal_original_bird_mean_initial_NEAR_minus_FAR_alignment":float(np.mean([
          np.mean(B[admitted[b]]) for b in birds])),
      "equal_original_bird_mean_absolute_turn_angle_radians":float(np.mean([
          np.mean(np.arccos(np.clip(c[admitted[b]],-1,1))) for b in birds])),
      "original_episode_mean_absolute_turn_angle_radians":float(angle.mean())}
    sham=symmetric_handedness_sham(before,c,near,far,admitted)
    sham["observed_original_minus_mean_symmetric_handedness_sham"]=\
       estimates[NAMES[4]]["equal_whole_bird_mean"]-sham["mean_sham_C_NF_OBSERVED"]
    years=sorted({int(str(pinned["start"][idx[i]])[:4]) for i in positions})
    annual=[]
    for yr in years:
        subset=[];n=0
        for b in birds:
            chosen=[p for p in admitted[b] if int(str(pinned["start"][idx[p]])[:4])==yr]
            if chosen:subset.append(matrix[chosen].mean(axis=0));n+=len(chosen)
        y=np.array(subset)
        annual.append({"year":yr,"original_birds":len(y),"source_direction_episodes":n,
           "equal_bird_observed_C_NF":float(y[:,4].mean()),
           "equal_bird_geometric_expected_C_NF":float(y[:,3].mean()),
           "equal_bird_PRIMARY_excess_C_NF":float(y[:,0].mean())})
    months=sorted({str(pinned["start"][idx[i]])[:7] for i in positions})
    mv=np.array([float(np.mean(matrix[[p for p in positions
                   if str(pinned["start"][idx[p]])[:7]==month],0])) for month in months])
    ms=np.random.default_rng(RNG).integers(0,len(mv),size=(BOOTS,len(mv)))
    temporal={"years_all_not_independent":annual,
       "calendar_months":len(months),
       "equal_month_excess_different_from_primary_equal_bird":float(mv.mean()),
       "naive_month_bootstrap95_nonindependent":list(map(float,np.quantile(mv[ms].mean(axis=1),[.025,.975])))}
    return {"status":"EXPLORATORY_WILD_DIRECTIONAL_TURN_EXCESS_OVER_INERTIAL_GEOMETRIC_NULL",
        "source_birds":len(birds),"source_original_directional_episodes":len(positions),
        "fixed_directional_components_and_all_signed_effects":estimates,
        "source_initial_bearing_and_turn_magnitude_audit":audit,
        "fixed_1000_source_free_handedness_sham":sham,
        "all_year_month_diagnostics":temporal,
        "anonymous_original_bird_all_components":{
          f"bird_{i+1:03d}":{"source_directional_episodes":len(admitted[b]),
             "excess_NF":float(rows[i,0]),"excess_NEAR":float(rows[i,1]),
             "excess_FAR":float(rows[i,2]),"symmetric_turn_geometric_expected_NF":float(rows[i,3]),
             "original_v45_observed_NF":float(rows[i,4])} for i,b in enumerate(birds)},
        "only_one_original_coastal_bird_population":True,
        "no_social_force_or_COGNITIVE_memory_proven":True}

def run():
    astronomy,tideQA=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as tmp:
        files=source.original_files_to_temp(Path(tmp))
        pinned,idx,before,after,n,f,admitted,positions,old_receipt,frozen=original_replay(files,astronomy,tideQA)
    scored=score(pinned,idx,before,after,n,f,admitted,positions,frozen)
    return {"status":scored["status"],"protocol":PROTOCOL,
       "complete_original_v41_to_v45_source_score_replay":old_receipt,
       "observed_original_directional_geometric_null":scored,
       "source_original":"SHA/MD5-pinned 2008–2014 Zenodo 10053970 v4 GPS and RWS astronomical Schiermonnikoog WATHTE",
       "NO_original_bird_ID_coords_UTC_tidal_arrays_or_per_episode_movement_exported":True,
       "earlier_v29_to_v45_original_results_UNCHANGED":True,
       "limitations":[
           "This study was specified after seeing v45 negative convergence on the same wild birds",
           "Symmetric handedness conditioned on true observed turn angle tests geometric mean-regression only",
           "Residual turning asymmetry can result from wind, coastline and preferred routes without social attraction or repulsion",
           "Same bird repeated episodes and one study site: bootstrap is not independent habitat replication",
           "No true 3D bird altitude, food intake or causal Reynolds Boids alignment observed"]}
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",type=Path,
      default=Path("validation_v46/results/original_wild_inertial_geometric_turning_null.json"))
    args=a.parse_args()
    res=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(res,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,prefix=".v46-",delete=False) as t:
        t.write(text);dest=Path(t.name)
    os.replace(dest,args.out)
    print("V46_OLD_V45_FULL_ORIGINAL_RECEIPT",json.dumps(res["complete_original_v41_to_v45_source_score_replay"],sort_keys=True))
    print("V46_STATUS",res["status"])
    x=res["observed_original_directional_geometric_null"]
    if x.get("fixed_directional_components_and_all_signed_effects"):
        print("V46_GEO_OBSERVED_AND_EXCESS",json.dumps(x["fixed_directional_components_and_all_signed_effects"],sort_keys=True))
        print("V46_SYMMETRIC_SHAM",json.dumps(x["fixed_1000_source_free_handedness_sham"],sort_keys=True))
        print("V46_YEAR_SIGN",json.dumps(x["all_year_month_diagnostics"]["years_all_not_independent"],sort_keys=True))
    else: print("V46_NO_NEW_SCORE",json.dumps(x,sort_keys=True))
    print("V46_COMPLETE_ANON_JSON",json.dumps(res,sort_keys=True,separators=(",",":")))
if __name__=="__main__":
    main()
