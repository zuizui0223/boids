#!/usr/bin/env python3
"""v42 source geometry: actual ≤200m other-bird PAST GPS fixes at focal start.

REPLAYS entire v41 ID/UTC source-only result BEFORE opening any original
positions. Spatial distance availability only, not neighbor direction effects
or social Reynolds/Boids causal identification.
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import itertools
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v41"))
sys.path.insert(0,str(ROOT/"validation_v33"))
sys.path.insert(0,str(ROOT/"validation_v32"))
import source_timestamps as timing
import phase_response as geom
import forecast as source

PROTOCOL="docs/V42_REAL_SPATIAL_NEIGHBOR_SOURCE_ADMISSION_PROTOCOL.md"
FROZEN_V41=ROOT/"validation_v41/results/original_conspecific_past_heading_timing_v41.json"
STATION_LAT=53.468937
STATION_LON=6.202908
STUDY_GAUGE_RADIUS_KM=25.
PAST_PAIR_MIN=5.
PAST_PAIR_MAX=30.
START_GAP_MIN=5.
START_GAP_MAX=360.
ORIGINAL_FUTURE_PAIR_MIN=5.
ORIGINAL_FUTURE_PAIR_MAX=30.
NEIGHBOR_MAX_PREVIOUS_FIX_AGE_MIN=5.
RADII_KM=(.1,.2,1.)
PRIMARY_RADIUS_KM=.2
EXPECTED_SOURCE_VALID_FIXES=602380
EXPECTED_SOURCE_BIRDS=39
TARGET_YEARS=(2010,2011,2012)
MIN_FOCAL_BIRDS=20
MIN_SPATIAL_TARGETS=10000
MIN_SOURCE_MONTHS=12
PASS="SOURCE_SPATIALLY_COTIMED_NEIGHBORS_AVAILABLE_BEHAVIOR_NOT_TESTED"
STOP="NOT_ADMITTED_ORIGINAL_SPATIALLY_CLOSE_OTHER_BIRD_GPS_SUPPORT"

def minutes(a,b):
    return (a-b).total_seconds()/60.

def source_original_v41_replay(paths):
    bybird,qa=timing.source_timestamps_only(paths)
    observed=timing.co_observation_opportunities(bybird)
    saved=json.loads(FROZEN_V41.read_text(encoding="utf-8"))
    if (saved.get("status")!=timing.STATUS_PASS or
        observed!=saved.get("registered_source_support") or
        qa!=saved.get("source_original_GPS_ID_and_UTC_only_quality")):
        raise ValueError("Frozen original v41 21 bird 276946 source-only ID/UTC receipt drift")
    target=observed["registered_2010_2012_test_source_support"]
    if (target["test_years_potential_focal_with_one_other_past_heading"]!=276946 or
        target["test_years_original_focal_bird_IDs_with_one_other_past_heading"]!=21):
        raise ValueError("Frozen original v41 source support changed")
    return {"status":"COMPLETE_FROZEN_V41_SOURCE_ID_UTC_NO_LOCATION_RECEIPT_MATCH",
        "original_source_birds":qa["source_original_birds_with_valid_ID_UTC"],
        "original_valid_source_ID_UTC_events":qa["original_visible_distinct_bird_UTC_rows"],
        "previous_time_only_2010_2012_other_heading_upper_bound":target["test_years_potential_focal_with_one_other_past_heading"],
        "previous_time_only_2010_2012_focal_birds":target["test_years_original_focal_bird_IDs_with_one_other_past_heading"],
        "no_GPS_coordinates_read_during_this_prior_source_replay":True}

def coordinate_source_support(points):
    """Original source 4fix focal and other bird PREVIOUS movement endpoint only."""
    bybird={}
    for b,rows in itertools.groupby(sorted(points,key=lambda p:(p[0],p[1])),key=lambda p:p[0]):
        bybird[b]=list(rows)
    if len(bybird)!=EXPECTED_SOURCE_BIRDS or len(points)!=EXPECTED_SOURCE_VALID_FIXES:
        raise ValueError("Original GPS coordinate source count/IDs drifted")
    starts=[]
    heading_endpoints=[]
    counts=collections.Counter()
    for bird,fixes in bybird.items():
        local=[geom.haversine_km(lat,lon,STATION_LAT,STATION_LON)<=STUDY_GAUGE_RADIUS_KM
               for _,_,lat,lon in fixes]
        for i in range(1,len(fixes)):
            delta=minutes(fixes[i][1],fixes[i-1][1])
            if PAST_PAIR_MIN<=delta<=PAST_PAIR_MAX and local[i] and local[i-1]:
                b,t,lat,lon=fixes[i]
                heading_endpoints.append((t,b,lat,lon))
                counts["original_local_other_bird_candidate_heading_endpoints"]+=1
        for i in range(2,len(fixes)-1):
            prev=minutes(fixes[i-1][1],fixes[i-2][1])
            gap=minutes(fixes[i][1],fixes[i-1][1])
            future=minutes(fixes[i+1][1],fixes[i][1])
            if not (PAST_PAIR_MIN<=prev<=PAST_PAIR_MAX and
                START_GAP_MIN<=gap<=START_GAP_MAX and
                ORIGINAL_FUTURE_PAIR_MIN<=future<=ORIGINAL_FUTURE_PAIR_MAX):
                continue
            counts["original_time_only_4fix_focal_candidates_before_local_filter"]+=1
            if not all(local[i-2:i+2]):
                counts["source_4fix_focal_excluded_25km_study_gauge"]+=1
                continue
            b,t,lat,lon=fixes[i]
            starts.append((t,b,lat,lon))
            counts["original_focal_four_fix_starts_all_local_25km"]+=1
    starts.sort(key=lambda q:q[0])
    heading_endpoints.sort(key=lambda q:q[0])
    annual={str(y):collections.Counter() for y in range(2008,2015)}
    yearly_birds={r:collections.defaultdict(set) for r in RADII_KM}
    test_birds={r:set() for r in RADII_KM}
    test_months={r:set() for r in RADII_KM}
    # Each source bird's latest already-observed valid past-pair END at or
    # before focal start. Keeping just the latest avoids correlated duplicate
    # endpoints from the SAME OTHER bird.
    latest={}
    right=0
    for t,b,lat,lon in starts:
        yr=str(t.year)
        if yr not in annual:raise ValueError("Source unexpected GPS year")
        annual[yr]["source_local_25km_potential_focal_start"]+=1
        while right<len(heading_endpoints) and heading_endpoints[right][0]<=t:
            obtime,ob,oblat,oblon=heading_endpoints[right]
            latest[ob]=(obtime,oblat,oblon)
            right+=1
        nearby={radius:0 for radius in RADII_KM}
        for other,(last,olat,olon) in latest.items():
            if other==b:continue
            age=minutes(t,last)
            if not 0<=age<=NEIGHBOR_MAX_PREVIOUS_FIX_AGE_MIN:continue
            d=geom.haversine_km(lat,lon,olat,olon)
            for radius in RADII_KM:
                if d<=radius:nearby[radius]+=1
        for radius,n in nearby.items():
            key=f"focal_with_other_PAST_heading_within_{radius:g}_km"
            if n>=1:
                annual[yr][key]+=1
                yearly_birds[radius][t.year].add(b)
                if t.year in TARGET_YEARS:
                    test_birds[radius].add(b)
                    test_months[radius].add((t.year,t.month))
            if radius==PRIMARY_RADIUS_KM and n>=2:
                annual[yr]["focal_with_two_or_more_other_PAST_heading_within_0.2_km"]+=1
    for yr in range(2008,2015):
        for radius in RADII_KM:
            annual[str(yr)][f"focal_birds_with_other_within_{radius:g}_km"]=len(yearly_birds[radius][yr])
    original2010=sum(annual[str(y)]["source_local_25km_potential_focal_start"] for y in TARGET_YEARS)
    support={}
    for r in RADII_KM:
        key=f"focal_with_other_PAST_heading_within_{r:g}_km"
        n=sum(annual[str(y)][key] for y in TARGET_YEARS)
        support[f"{r:g}_km"]={
          "original_local_4fix_future_starts":original2010,
          "potential_spatially_cotimed_focal_starts":n,
          "source_focal_birds_with_neighbor_candidate":len(test_birds[r]),
          "source_UTC_months_with_neighbor_candidate":len(test_months[r]),
          "proportion_of_local_4fix_starts":n/original2010 if original2010 else 0.,
        }
    main=support[f"{PRIMARY_RADIUS_KM:g}_km"]
    admitted=(main["source_focal_birds_with_neighbor_candidate"]>=MIN_FOCAL_BIRDS and
        main["potential_spatially_cotimed_focal_starts"]>=MIN_SPATIAL_TARGETS and
        main["source_UTC_months_with_neighbor_candidate"]>=MIN_SOURCE_MONTHS)
    return {"status":PASS if admitted else STOP,
      "original_frozen_25km_local_source_support":dict(counts),
      "all_2008_2014_yearly_spatial_time_opportunity_counts":{
          year:dict(annual[year]) for year in sorted(annual)},
      "original_fixed_radii_km":list(RADII_KM),
      "PRIMARY_radius_km":PRIMARY_RADIUS_KM,
      "2010_2012_support_all_fixed_radii":support,
      "required_min_spatial_200m_focal_birds":MIN_FOCAL_BIRDS,
      "required_min_spatial_200m_focal_starts":MIN_SPATIAL_TARGETS,
      "required_min_spatial_200m_source_UTC_months":MIN_SOURCE_MONTHS,
      "original_future_next_fix_outcome_speed_bearing_NOT_read_or_modeled":True,
      "nearby_at_latest_original_other_bird_past_fix_ONLY":True,
      "source_200m_neighbor_time_space_availability_NOT_social_steering_effect":True,
      "original_private_ID_coordinates_and_UTC_data_NOT_exported":True}

def run():
    with tempfile.TemporaryDirectory() as folder:
        gpsfiles=source.original_files_to_temp(Path(folder))
        previous=source_original_v41_replay(gpsfiles)
        # Source-only time audit above MUST pass before opening positions.
        points,gps_qa=geom.read_original_valid_gps(gpsfiles)
    current=coordinate_source_support(points)
    return {"study":"v42 original co-timed AND 200m spatially near wild GPS source gate",
        "status":current["status"],
        "protocol":PROTOCOL,
        "source":"Zenodo 10053970 v4 original seven MD5/SHA gated GPS years",
        "previous_source_only_v41_time_AUDIT_replay":previous,
        "original_v33_GPS_quality_602380":gps_qa,
        "source_only_spatial_neighbor_opportunities_NOT_effects":current,
        "no_animal_GPS_coordinates_ID_or_real_UTC_timestamps_exported":True,
        "no_social_alignment_Boids_effect_or_causal_mechanism_tested":True,
        "source_notes":[
          "Other bird has valid 5-30 minute PAST original GPS pair and latest fix no later than focal source start",
          "Co-location within fixed 200m is an observable proximity proxy, not social heading alignment",
          "Time-only v41 replay performed before original location data opened",
          "Original GPS target presence used solely for source-cohort support",
          "A future predictive comparison must intersect exact original v40 heldout and close-neighbor episode support",
          "Same one source Schiermonnikoog wild oystercatcher, not 20 independent field sites",
        ]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,
          default=Path("validation_v42/results/wild_gps_cotimed_200m_source_geometry_v42.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
                prefix=".v42-",delete=False) as f:
        f.write(payload);tmp=Path(f.name)
    os.replace(tmp,args.out)
    print("V42_SOURCE_PREVIOUS_V41_NO_POSITION_REPLAY",json.dumps(result["previous_source_only_v41_time_AUDIT_replay"],sort_keys=True))
    print("V42_2010_2012_RADIUS_SUPPORT",json.dumps(result["source_only_spatial_neighbor_opportunities_NOT_effects"]["2010_2012_support_all_fixed_radii"],sort_keys=True))
    print("V42_SOURCE_GEOGRAPHIC_GATE",result["status"])
    print("V42_COMPLETE_SOURCE_SAFE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))
    print("V42_NO_EMPIRICAL_SOCIAL_BEHAVIOR_SCORE")
if __name__=="__main__":main()
