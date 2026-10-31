#!/usr/bin/env python3
"""v41 original GPS source-only ID×UTC audit of potential conspecific past headings.

Reads provider-SHA-verified original GPS gzip only for original ID, UTC,
visible/outlier flags and headers. NEVER reads lat, lon, speed or heading.
All private bird IDs and original animal timestamps stay ephemeral.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import gzip
import json
import math
import os
from pathlib import Path
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v32"))
import forecast as original

PROTOCOL="docs/V41_CONSPECIFIC_GPS_TIME_SYNCHRONY_SOURCE_PROTOCOL.md"
FIRST_YEAR=2008
LAST_YEAR=2014
TARGET_START_YEARS=(2010,2011,2012)
FORECAST_PAIR_MIN=5.
FORECAST_PAIR_MAX=30.
PREVIOUS_PAIR_MIN=5.
PREVIOUS_PAIR_MAX=30.
PREVIOUS_TO_CURRENT_MIN=5.
PREVIOUS_TO_CURRENT_MAX=360.
OTHER_HEADING_PAIR_MIN=5.
OTHER_HEADING_PAIR_MAX=30.
MAX_OTHER_HEADING_AGE_MIN=5.
MIN_BIRDS_WITH_TIME_SUPPORTED_FOCAL_STARTS=20
MIN_TIME_SUPPORTED_FOCAL_START_EPISODES=10000
MIN_SUPPORTED_SOURCE_MONTHS=12
STATUS_PASS="SOURCE_ONLY_COTIMED_CONSPECIFIC_HEADINGS_POSSIBLE_POSITION_UNKNOWN"
STATUS_STOP="NOT_ADMITTED_SOURCE_SYNCHRONY_FOR_SOCIAL_HEADING"

def minutes(later,earlier):
    return (later-earlier).total_seconds()/60.

def discard_all_duplicate_source_bird_UTC_events(records):
    """Never take first or last GPS fix arbitrarily when identical ID×UTC recurs."""
    count=collections.Counter(records)
    duplicate_keys=sum(v>1 for v in count.values())
    duplicate_rows=sum(v for v in count.values() if v>1)
    bybird=collections.defaultdict(list)
    for (bird,t),freq in count.items():
        if freq==1:bybird[bird].append(t)
    for bird in bybird:bybird[bird].sort()
    return dict(bybird),{"original_duplicate_source_bird_UTC_keys":duplicate_keys,
                         "original_duplicate_rows_all_discarded":duplicate_rows}

def source_timestamps_only(paths):
    counters=collections.Counter()
    events=[]
    for path in paths:
        with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if tuple(reader.fieldnames or ())!=original.EXPECTED_FIELDS:
                raise ValueError("Source original GPS gzip header does not match pinned published schema")
            for row in reader:
                counters["original_physical_GPS_CSV_rows"]+=1
                bird=(row.get("individual-local-identifier") or "").strip()
                if not bird:
                    counters["blank_original_bird_identifier"]+=1;continue
                try:
                    t=original.parse_timestamp(row.get("timestamp"))
                    visible=original.flag_true(row.get("visible"))
                    marked=original.flag_true(row.get("manually-marked-outlier"),blank_false=True)
                except (ValueError,TypeError) as e:
                    raise ValueError("Source original UTC/quality grammar changed") from e
                if visible is not True or marked is True:
                    counters["original_visible_or_manual_QC_excluded"]+=1;continue
                events.append((bird,t))
    if counters["original_physical_GPS_CSV_rows"]!=original.SOURCE_ROWS:
        raise ValueError("Original source physical 7-year GPS count drift")
    birds,duplicates=discard_all_duplicate_source_bird_UTC_events(events)
    if len(birds)!=original.SOURCE_BIRDS:
        raise ValueError("Original 39 source bird IDs changed")
    if sum(len(z) for z in birds.values())!=602380:
        raise ValueError("Original complete source QA / duplicate counts disagree with v32/v33")
    counters.update(duplicates)
    counters["source_original_birds_with_valid_ID_UTC"]=len(birds)
    counters["original_visible_distinct_bird_UTC_rows"]=sum(len(z) for z in birds.values())
    counters["NO_location_speed_heading_or_animal_movement_response_values_accessed"]=True
    return birds,dict(counters)

def co_observation_opportunities(bybird):
    """Upper bound on future bird-to-bird heading availability, NOT spatial neighbors.

    Only time stamps of other birds' two PAST fixes may be used at focal
    prediction time. Future focal fix is inspected solely for candidate count.
    """
    focal=[]
    observed_other_heading=[]
    timeqa=collections.Counter()
    for bird,rawtimes in bybird.items():
        times=sorted(set(rawtimes))
        for i in range(1,len(times)):
            gap=minutes(times[i],times[i-1])
            if OTHER_HEADING_PAIR_MIN<=gap<=OTHER_HEADING_PAIR_MAX:
                observed_other_heading.append((times[i],bird))
                timeqa["potential_other_heading_endpoints_time_only"]+=1
        for i in range(2,len(times)-1):
            past=minutes(times[i-1],times[i-2])
            gap=minutes(times[i],times[i-1])
            future=minutes(times[i+1],times[i])
            if (PREVIOUS_PAIR_MIN<=past<=PREVIOUS_PAIR_MAX and
                PREVIOUS_TO_CURRENT_MIN<=gap<=PREVIOUS_TO_CURRENT_MAX and
                FORECAST_PAIR_MIN<=future<=FORECAST_PAIR_MAX):
                focal.append((times[i],bird))
                timeqa["time_only_original_four_fix_focal_future_candidates"]+=1
    focal.sort(key=lambda x:x[0])
    observed_other_heading.sort(key=lambda x:x[0])
    counts=collections.Counter()
    left=right=0
    yearqa={str(y):collections.Counter() for y in range(FIRST_YEAR,LAST_YEAR+1)}
    source_supported_birds=set()
    source_supported_months=set()
    year_birds=collections.defaultdict(set)
    plus2_birds=collections.defaultdict(set)
    for t,b in focal:
        year=str(t.year)
        if year not in yearqa:raise ValueError("Original source year outside frozen years")
        yearqa[year]["time_only_original_four_fix_focal_future_candidates"]+=1
        # Increment right pointer only on actual other-bird GPS heading endpoints
        # at OR BEFORE focal forecast start; no source future predictor leakage.
        while right<len(observed_other_heading) and observed_other_heading[right][0]<=t:
            counts[observed_other_heading[right][1]]+=1
            right+=1
        lower=t-dt.timedelta(minutes=MAX_OTHER_HEADING_AGE_MIN)
        while left<right and observed_other_heading[left][0]<lower:
            old_b=observed_other_heading[left][1]
            counts[old_b]-=1
            if counts[old_b]<=0:del counts[old_b]
            left+=1
        # Never count self as a conspecific independent other bird.
        number_distinct_other=len(counts)-(1 if counts.get(b,0)>0 else 0)
        if number_distinct_other>=1:
            yearqa[year]["focal_starts_with_prior_other_original_heading_timing"]+=1
            year_birds[t.year].add(b)
            if t.year in TARGET_START_YEARS:
                source_supported_birds.add(b)
                source_supported_months.add((t.year,t.month))
        if number_distinct_other>=2:
            yearqa[year]["focal_starts_with_two_or_more_distinct_prior_other_headings"]+=1
            plus2_birds[t.year].add(b)
    for y in range(FIRST_YEAR,LAST_YEAR+1):
        yr=yearqa[str(y)]
        yr["focal_birds_with_any_prior_other_heading_time_support"]=len(year_birds[y])
        yr["focal_birds_with_two_or_more_other_heading_time_support"]=len(plus2_birds[y])
    heldout_support=sum(yearqa[str(y)]["focal_starts_with_prior_other_original_heading_timing"]
                        for y in TARGET_START_YEARS)
    heldout_total=sum(yearqa[str(y)]["time_only_original_four_fix_focal_future_candidates"]
                      for y in TARGET_START_YEARS)
    source_gate={"test_years":[2010,2011,2012],
       "test_years_potential_focal_four_fix_starts":heldout_total,
       "test_years_potential_focal_with_one_other_past_heading":heldout_support,
       "test_years_original_focal_bird_IDs_with_one_other_past_heading":len(source_supported_birds),
       "test_years_UTC_calendar_months_with_past_other_heading":len(source_supported_months),
       "required_birds":MIN_BIRDS_WITH_TIME_SUPPORTED_FOCAL_STARTS,
       "required_focal_opportunities":MIN_TIME_SUPPORTED_FOCAL_START_EPISODES,
       "required_months":MIN_SUPPORTED_SOURCE_MONTHS,
       "NO_spatial_distance_or_conspecific_neighbor_interaction_claim":True,
       "only_actual_other_original_fix_times_at_or_before_focal_t_in_predictor":True}
    admitted=(len(source_supported_birds)>=MIN_BIRDS_WITH_TIME_SUPPORTED_FOCAL_STARTS and
        heldout_support>=MIN_TIME_SUPPORTED_FOCAL_START_EPISODES and
        len(source_supported_months)>=MIN_SUPPORTED_SOURCE_MONTHS)
    return {"status":STATUS_PASS if admitted else STATUS_STOP,
        "source_temporal_opportunity_QA":dict(timeqa),
        "yearly_source_time_only_opportunities":{y:dict(yearqa[y]) for y in sorted(yearqa)},
        "registered_2010_2012_test_source_support":source_gate,
        "source_provider_original_GPS_temporal_analytical_opportunity_only":True,
        "NO_raw_original_bird_ID_UTC_or_GPS_coordinates_emitted":True}

def run():
    with tempfile.TemporaryDirectory() as d:
        original_files=original.original_files_to_temp(Path(d))
        bybird,quality=source_timestamps_only(original_files)
    temporal=co_observation_opportunities(bybird)
    return {"study":"v41 original source-time-only potential conspecific prior heading",
        "status":temporal["status"],
        "protocol":PROTOCOL,
        "source":"Zenodo 10053970 v4 all 7 SHA-pinned original GPS years 2008-2014",
        "source_published_original_year_MD5_SHA":{str(yr):{
          "bytes":val[0],"original_published_md5":val[1],"pinned_original_sha256":val[2]}
          for yr,val in sorted(original.PINS.items())},
        "source_original_GPS_ID_and_UTC_only_quality":quality,
        "registered_source_support":temporal,
        "no_animal_GPS_position_heading_or_velocity_value_parsed":True,
        "no_tide_numeric_RWS_series_or_synthetic_movement_results_parsed":True,
        "no_actual_spatial_neighbor_or_social_alignment_effect_reported":True,
        "all_previous_v29_to_v40_results_and_model_files_unchanged":True,
        "source_limitations":[
           "Other-bird prior heading time support is an upper bound on neighbor support; no spatial distance or flock membership checked",
           "Original 2008-2014 bird GPS is previously analyzed, so even a future social test is exploratory",
           "Original future GPS schedule used only to identify time-only test opportunity, not model predictor",
           "A co-observed original GPS device does not establish synchronous social interaction or shared 3D ecological niche"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,
      default=Path("validation_v41/results/original_conspecific_past_heading_timing_v41.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
         prefix=".v41-",delete=False) as temp:
        temp.write(data);dest=Path(temp.name)
    os.replace(dest,args.out)
    print("V41_ORIGINAL_SOURCE_ID_UTC_STATUS",out["status"])
    print("V41_SOURCE_2010_2012_ONLY",json.dumps(
         out["registered_source_support"]["registered_2010_2012_test_source_support"],sort_keys=True))
    print("V41_COMPLETE_SOURCE_SAFE_AGGREGATE_JSON",json.dumps(out,sort_keys=True,separators=(",",":")))
    print("V41_NO_BIRD_ORIGINAL_COORDINATE_OR_SOCIAL_BEHAVIOR_RESULT")
if __name__=="__main__":main()
