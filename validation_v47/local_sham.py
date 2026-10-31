#!/usr/bin/env python3
"""v47 post-v46 local source location/tide matching of corrected other-bird headings.

Read-only original wild GPS/RWS replay; no causality or independent birds.
"""
from __future__ import annotations
import argparse,collections,datetime as dt,json,math,os,sys,tempfile
from pathlib import Path
import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
for path in ("validation_v46","validation_v45","validation_v44","validation_v43",
             "validation_v40","validation_v42","validation_v41","validation_v39",
             "validation_v34","validation_v33","validation_v32"):
    sys.path.insert(0,str(ROOT/path))
import geometric_null as v46
import turning_convergence as v45
import conditional_history as v39
import ebb_flood_height_matched as validator
import phase_response as gpssource
import tidal_forecast as tide
import forecast as source

PREVIOUS=ROOT/"validation_v46/results/original_wild_inertial_geometric_turning_null.json"
PROTOCOL="docs/V47_LOCATION_MATCHED_TIDAL_HEADING_SHAM_PROTOCOL.md"
GRID_M=2000.
PERM=500
BIRD_BOOT=10000
SEED=20261031
MIN_BIRDS=10
MIN_EPISODES_PER_BIRD=10
MIN_EPISODES=1000
MIN_MONTHS=4
MIN_YEARS=2
GAUGE_LON=6.202908
GAUGE_LAT=53.468937

def frozen_wild_replay(files,astro,quality):
    pinned,idx,before,after,near,far,admitted,positions,receipt,frozen45=\
        v46.original_replay(files,astro,quality)
    scored=v46.score(pinned,idx,before,after,near,far,admitted,positions,frozen45)
    saved=json.loads(PREVIOUS.read_text(encoding="utf-8"))
    required={
        "status":scored["status"],
        "protocol":v46.PROTOCOL,
        "complete_original_v41_to_v45_source_score_replay":receipt,
        "observed_original_directional_geometric_null":scored,
        "source_original":"SHA/MD5-pinned 2008–2014 Zenodo 10053970 v4 GPS and RWS astronomical Schiermonnikoog WATHTE",
        "NO_original_bird_ID_coords_UTC_tidal_arrays_or_per_episode_movement_exported":True,
        "earlier_v29_to_v45_original_results_UNCHANGED":True,
    }
    for key,value in required.items():
        if not validator.nested_close(value,saved.get(key),1e-12):
            raise ValueError("Original v46 full field result drift: "+key)
    if len(admitted)!=17 or len(positions)!=4660 or len(idx)!=4667:
        raise ValueError("Frozen original v46 17-bird/4660-episode cohort drift")
    return pinned,idx,before,after,near,far,admitted,positions,{
        "status":"COMPLETE_ORIGINAL_V41_TO_V46_ALL_SOURCE_AND_ANONYMOUS_NUMERIC_REPLAY",
        "original_v46_birds":17,"original_v46_directional_episodes":4660,
        "prior_shams_and_all_original_bird_source_scores_match_to_abs":1e-12,
        "previous_GitHub_source_and_outcome_UNCHANGED":True}

def source_start_coordinates(files,pinned,idx,positions):
    points,qa=gpssource.read_original_valid_gps(files)
    ids={b:i for i,b in enumerate(sorted({p[0] for p in points}))}
    needed={}
    for p in positions:
        target=int(idx[p])
        t=pinned["start"][target].astype("datetime64[us]").astype(dt.datetime)
        key=(int(pinned["bird"][target]),t)
        if key in needed:raise ValueError("Duplicate GPS original focal start key")
        needed[key]=int(p)
    coords=np.full((len(idx),2),np.nan)
    found=0
    for bird,t,lat,lon in points:
        key=(ids[bird],t)
        if key in needed:
            q=needed[key]
            if np.isfinite(coords[q]).all():raise ValueError("Duplicate original GPS source fix after QC")
            coords[q]=[lon,lat]
            found+=1
    if found!=len(positions) or not np.isfinite(coords[positions]).all():
        raise ValueError("Original focal GPS future-start source did not match exact record")
    return coords,{
       "original_source_valid_GPS_fixes":len(points),
       "original_source_bird_ID_count":len(ids),
       "frozen_4660_focal_START_source_coordinates_exactly_found":found,
       "no_focal_future_GPS_used_in_source_spatial_cell":True}

def spatial_cell(x,y):
    if not np.isfinite([x,y]).all():raise ValueError("Invalid source projected GPS")
    return math.floor(x/GRID_M),math.floor(y/GRID_M)

def fixed_group_key(bird,utc,slope,relative_x,relative_y):
    if not isinstance(utc,dt.datetime) or utc.tzinfo is not None:
        raise ValueError("Original GPS UTC key is not naive UTC datetime")
    if slope==0:return None
    if not math.isfinite(slope):raise ValueError("Nonfinite original astronomical tide slope")
    gx,gy=spatial_cell(relative_x,relative_y)
    return (int(bird),utc.year,(utc.month-1)//3,utc.hour//6,
            "rising" if slope>0 else "falling",gx,gy)

def original_spatial_groups(pinned,idx,positions,coords):
    transform=Transformer.from_crs("EPSG:4326","EPSG:25832",always_xy=True)
    sx,sy=transform.transform(GAUGE_LON,GAUGE_LAT)
    x,y=transform.transform(coords[positions,0],coords[positions,1])
    slope_col=v39.ENV_FIELDS.index("current_dH_m_per_h")
    grouped=collections.defaultdict(list)
    zero=0
    for k,p in enumerate(positions):
        src=int(idx[p])
        utc=pinned["start"][src].astype("datetime64[us]").astype(dt.datetime)
        key=fixed_group_key(int(pinned["bird"][src]),utc,
                float(pinned["X"][src,slope_col]),x[k]-sx,y[k]-sy)
        if key is None:
            zero+=1
            continue
        grouped[key].append(int(p))
    matched=[np.asarray(group,dtype=int) for group in grouped.values() if len(group)>=2]
    size_hist=collections.Counter(map(len,matched))
    return matched,{
       "original_grid": "ETRS89/UTM32 EPSG:25832, 2km square anchored at official gauge",
       "source_grouping":"focal bird×UTC year×calendar quarter×UTC 6h×rising/falling×2km local cell",
       "original_v46_episodes":len(positions),
       "exact_zero_original_tide_slope_sham_excluded":zero,
       "original_location_time_tide_cells":len(grouped),
       "source_cells_with_2plus_episodes":len(matched),
       "potential_original_permutable_episodes":sum(len(g) for g in matched),
       "source_cell_size_histogram_no_geographic_coordinates":dict(sorted(size_hist.items())),
       "no_animal_locations_UTC_grid_keys_exported":True}

def local_sham_score(pinned,idx,before,after,near,far,groups,qa):
    matrix,B,cosine=v46.geometry(before,after,near,far)
    signed_turn=after-cosine[:,None]*before
    checked=np.sum(signed_turn*(near-far),axis=1)
    if not np.allclose(checked,matrix[:,0],atol=1e-12,rtol=0):
        raise ValueError("Exact previous v46 per-episode corrected turning identity drift")
    matched=collections.defaultdict(list)
    for g in groups:
        birdset={int(pinned["bird"][int(idx[p])]) for p in g}
        if len(birdset)!=1:raise ValueError("Grouped sham illegally interchanges source birds")
        matched[next(iter(birdset))].extend(int(p) for p in g)
    accepted={b:np.asarray(p,dtype=int) for b,p in matched.items()
              if len(p)>=MIN_EPISODES_PER_BIRD}
    supported=np.concatenate(list(accepted.values())) if accepted else np.array([],dtype=int)
    months=sorted({str(pinned["start"][int(idx[p])])[:7] for p in supported})
    years=sorted({int(str(pinned["start"][int(idx[p])])[:4]) for p in supported})
    support={**qa,
        "birds_10plus_original_local_sham_events":len(accepted),
        "original_permutable_episodes_after_whole_bird_min":len(supported),
        "source_calendar_months":len(months),"source_years":years,
        "required_birds":MIN_BIRDS,"required_episodes":MIN_EPISODES,
        "required_months":MIN_MONTHS,"required_years":MIN_YEARS}
    if (len(accepted)<MIN_BIRDS or len(supported)<MIN_EPISODES
        or len(months)<MIN_MONTHS or len(years)<MIN_YEARS):
        return {"status":"NOT_ADMITTED_LOCAL_MATCHED_SHAM_SUPPORT",
                "support":support,"any_new_time_specific_heading_effect_exported":False}
    valid=np.zeros(len(before),bool);valid[supported]=True
    paired_groups=[g for g in groups if valid[g].all()]
    birds=sorted(accepted)
    obs=np.array([float(np.mean(matrix[accepted[b],0])) for b in birds])
    rng=np.random.default_rng(SEED)
    shuffled=np.empty((PERM,len(birds)),dtype=float)
    for rep in range(PERM):
        assignment=np.arange(len(before))
        for group in paired_groups:
            assignment[group]=rng.permutation(group)
        diff=near[assignment]-far[assignment]
        event=np.sum(signed_turn*diff,axis=1)
        shuffled[rep]=[float(np.mean(event[accepted[b]])) for b in birds]
    baseline=shuffled.mean(axis=0)
    gain=obs-baseline
    draw=np.random.default_rng(SEED).integers(0,len(birds),size=(BIRD_BOOT,len(birds)))
    expected=np.full(len(before),np.nan)
    for group in paired_groups:
        expected[group]=signed_turn[group]@np.mean(near[group]-far[group],axis=0)
    analytic=np.array([float(np.mean(expected[accepted[b]])) for b in birds])
    count=int((gain>0).sum())
    years_summary=[]
    for year in years:
        vals=[];n=0
        for b in birds:
            ii=np.asarray([p for p in accepted[b]
                           if int(str(pinned["start"][int(idx[p])])[:4])==year],dtype=int)
            if len(ii):
                vals.append(float(np.mean(matrix[ii,0]-expected[ii])))
                n+=len(ii)
        years_summary.append({
            "source_year":year,"source_original_birds":len(vals),
            "original_source_episodes":n,
            "observed_minus_analytic_location_sham":float(np.mean(vals))})
    return {"status":"EXPLORATORY_LOCAL_SPATIAL_CLOCK_TIDE_MATCHED_OTHER_BIRD_HEADING_SHAM",
       "support":support,
       "frozen_primary_observed_minus_500_matched_shams":float(np.mean(gain)),
       "whole_bird_bootstrap95_of_observed_minus_fixed_mean_sham":list(
             map(float,np.quantile(gain[draw].mean(axis=1),[.025,.975]))),
       "positive_source_birds":count,"negative_source_birds":int((gain<0).sum()),
       "exact_one_sided_positive_bird_sign_p":v39.sign_tail(count,len(birds)),
       "observed_original_v46_excess_on_exact_sham_population":float(obs.mean()),
       "empirical_mean_500_local_cell_sham":float(shuffled.mean()),
       "500_sham_equal_bird_mean_percentiles_5_95":list(
             map(float,np.quantile(shuffled.mean(axis=1),[.05,.95]))),
       "exact_analytic_local_group_mean_sham":float(analytic.mean()),
       "empirical_minus_analytic_sham_bias":float((baseline-analytic).mean()),
       "yearwise_original_source_diagnostic":years_summary,
       "anonymous_whole_original_bird_effects":{
         f"bird_{i+1:03d}":{"source_permutable_episodes":len(accepted[b]),
            "observed_geometric_excess":float(obs[i]),
            "location_tide_matched_sham":float(baseline[i]),
            "observed_minus_sham":float(gain[i])}
           for i,b in enumerate(birds)},
       "source_500_permutations_NOT_independent_original_birds":True,
       "one_nonrandom_coastal_population_no_identified_Reynolds_social_force":True}

def run():
    astronomy,tideqa=tide.load_original_astronomy()
    with tempfile.TemporaryDirectory() as tmp:
        files=source.original_files_to_temp(Path(tmp))
        pinned,idx,before,after,near,far,admitted,positions,gate=\
            frozen_wild_replay(files,astronomy,tideqa)
        coords,locqa=source_start_coordinates(files,pinned,idx,positions)
    groups,qa=original_spatial_groups(pinned,idx,positions,coords)
    effect=local_sham_score(pinned,idx,before,after,near,far,groups,{**locqa,**qa})
    return {"status":effect["status"],"protocol":PROTOCOL,
        "original_source":"Source original SHA-pinned Zenodo 10053970 v4 and Schiermonnikoog RWS 2008–2014 astronomy",
        "complete_prior_v41_to_v46_full_source_and_numerical_replay":gate,
        "same_original_v46_full_cohort_directional_steps":len(positions),
        "new_local_sham_source_falsification_result":effect,
        "all_old_v29_to_v46_GitHub_biology_source_and_outcomes_UNCHANGED":True,
        "no_original_GPS_coordinates_bird_ID_times_or_tide_height_series_saved":True,
        "limits":[
          "Post-v46 same original wild population, not independent field replication",
          "2km cells and quarter/6h/rising-falling bins do not fully match wind, habitat or social group identity",
          "The source-only spatial mask is defined at original focal START, never future GPS position",
          "Shuffled near/far heading pairs are not a randomized manipulation of live birds",
          "A positive gain does not identify causal social attraction, Reynolds force, or 3D niche"]}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,
        default=Path("validation_v47/results/location_matched_tidal_near_far_sham_v47.json"))
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",
            dir=args.out.parent,prefix=".v47-",delete=False) as f:
        f.write(content);temp=Path(f.name)
    os.replace(temp,args.out)
    outcome=result["new_local_sham_source_falsification_result"]
    print("V47_ALL_PRIOR_V46_NUMERICAL_SOURCE_REPLAY",json.dumps(
        result["complete_prior_v41_to_v46_full_source_and_numerical_replay"],sort_keys=True))
    print("V47_ORIGINAL_SHAM_SOURCE_SUPPORT",json.dumps(outcome["support"],sort_keys=True))
    print("V47_STATUS",result["status"])
    if outcome.get("frozen_primary_observed_minus_500_matched_shams") is not None:
        print("V47_MATCHED_SPATIOTEMPORAL_SHAM",json.dumps({
           k:v for k,v in outcome.items() if k not in ("support","anonymous_whole_original_bird_effects")
        },sort_keys=True))
    else:print("V47_NO_NEW_SPATIAL_SOCIAL_EFFECT_SCORED")
    print("V47_COMPLETE_SOURCE_SAFE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
