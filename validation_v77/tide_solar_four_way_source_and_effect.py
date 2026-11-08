"""v77 original tide × solar four-way interaction using genuine 2010 bird locations.

After v76: 0.2m original measured tide height bin, same bird/month,
FOUR original combinations ebb/flood × day/night each >=5 positions.
No modeled exposure rank is read before whole v77 source gate.
Original NIOZ model \`time_expo\` is unknown-unit monthly numeric index, not
observed instantaneous foraging area/time.
"""
from __future__ import annotations

from collections import Counter,defaultdict
import numpy as np

from wild_2010_modelled_tidal_exposure_rank import _rank
from matched_tide_state_day_night_native_ranks import (
    _aggregate_original_bird_months)

MIN_FOUR_WAY_STRATA=100
MIN_FOUR_WAY_BIRDS=8
MIN_FOUR_WAY_MONTHS=3
MIN_FOUR_WAY_FIXES=2000
MIN_BIRDS_GE3_GROUPS=5
MIN_EACH_OF_FOUR_SOURCE_FIXES=5
ORIGINAL_PRIOR_V76_PAIRED=1495
ORIGINAL_PRIOR_V76_DAY=16125
ORIGINAL_PRIOR_V76_NIGHT=18535
ORIGINAL_PRIOR_V76_BIRDS=16
ORIGINAL_PRIOR_V76_MONTHS=5
ORIGINAL_PRIOR_V76_EBB=786
ORIGINAL_PRIOR_V76_FLOOD=709
PRIMARY_GAUGE_HEIGHT_BIN_METRES=.2
PRIMARY_CLOCK_SHIFT_SECONDS=0
ADMIT="SOURCE_ADMITTED_V77_FULL_SAME_BIRD_MONTH_HEIGHT_FOUR_WAY_TIDE_LIGHT"

def fourway_source_only(prior_pairs,prior_source,*,verify_original_replay=True):
    """Actual RWS source + solar/GPS only; NEVER inspect used model index."""
    if verify_original_replay:
        expected={
            "admission":"SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE",
            "original_paired_condition_groups_ge5_day_and_night":
                ORIGINAL_PRIOR_V76_PAIRED,
            "original_genuine_day_GPS_positions_in_matched_tide_conditions":
                ORIGINAL_PRIOR_V76_DAY,
            "original_genuine_night_GPS_positions_in_matched_tide_conditions":
                ORIGINAL_PRIOR_V76_NIGHT,
            "original_distinct_birds_in_tide_matched_groups":
                ORIGINAL_PRIOR_V76_BIRDS,
            "original_distinct_months_in_paired_conditions":
                ORIGINAL_PRIOR_V76_MONTHS,
            "original_physical_RWS_ebb_strata":ORIGINAL_PRIOR_V76_EBB,
            "original_physical_RWS_flood_strata":ORIGINAL_PRIOR_V76_FLOOD,
            "true_RWS_height_bin_metres":PRIMARY_GAUGE_HEIGHT_BIN_METRES,
            "original_native_GPS_clock_shift_seconds":PRIMARY_CLOCK_SHIFT_SECONDS
        }
        if any(prior_source.get(k)!=v for k,v in expected.items()):
            raise ValueError("SOURCE_STOP_V77_UNCHANGED_V76_SOURCE_COUNTS_OR_TIDE_CHANGED")
    if prior_source.get("admission")!=(
            "SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE"):
        return {},{"admission":"NOT_ADMITTED_V77_PREVIOUS_RWS_TIDE_SOURCE"}
    grid=defaultdict(dict)
    for k,s in prior_pairs.items():
        if len(k)!=4 or k[2] not in (-1,1):
            raise ValueError("SOURCE_STOP_V77_MALFORMED_ORIGINAL_PHASE_MATCH")
        if (len(s["DAY"])<MIN_EACH_OF_FOUR_SOURCE_FIXES or
            len(s["NIGHT"])<MIN_EACH_OF_FOUR_SOURCE_FIXES):
            raise ValueError("SOURCE_STOP_V77_PRIOR_PER_PHASE_LIGHT_MINIMUM")
        bird,month,phase,heightbin=k
        group=(bird,month,heightbin)
        if phase in grid[group]:
            raise ValueError("SOURCE_STOP_V77_DUPLICATE_GENUINE_PHASE")
        grid[group][phase]=s
    four={key:v for key,v in grid.items()
          if set(v)=={-1,1} and all(
             len(v[p][light])>=MIN_EACH_OF_FOUR_SOURCE_FIXES
             for p in (-1,1) for light in ("DAY","NIGHT"))}
    animals=Counter(k[0] for k in four)
    samples_by_cell=Counter()
    unique=set()
    for key,phase in four.items():
        for p in (-1,1):
            for light in ("DAY","NIGHT"):
                refs=phase[p][light]
                samples_by_cell[f"{'ebb' if p<0 else 'flood'}_{light.lower()}"]+=len(refs)
                for original_month,i in refs:
                    unique.add((original_month,i))
    n_samples=sum(samples_by_cell.values())
    if n_samples!=len(unique):
        raise ValueError("SOURCE_STOP_V77_ORIGINAL_FOUR_WAY_GPS_FIX_REUSED")
    meta={
        "original_candidate_same_bird_month_height_groups_from_v76":len(grid),
        "original_four_way_exact_same_bird_month_RWS_height_groups":len(four),
        "original_birds_in_all_four_tide_and_light_conditions":len(animals),
        "original_birds_with_ge3_four_way_height_groups":
            sum(k>=3 for k in animals.values()),
        "original_2010_months_with_complete_four_way_conditions":
            len({k[1] for k in four}),
        "original_source_GPS_fix_counts_by_true_ebb_flood_and_astronomical_light":
            dict(samples_by_cell),
        "original_four_way_source_fix_count":n_samples,
        "original_no_GPS_fix_reused_in_multiple_condition_groups":True,
        "original_native_GPS_CLOCK_UTC_CALIBRATION_UNVERIFIED":True,
        "physically_measured_RWS_height_bin_metres":
            prior_source.get("true_RWS_height_bin_metres"),
        "fixed_no_future_heading_or_monthly_used_model_index_for_source":True}
    feasible=(
        len(four)>=MIN_FOUR_WAY_STRATA and
        len(animals)>=MIN_FOUR_WAY_BIRDS and
        meta["original_2010_months_with_complete_four_way_conditions"]>=MIN_FOUR_WAY_MONTHS and
        n_samples>=MIN_FOUR_WAY_FIXES and
        meta["original_birds_with_ge3_four_way_height_groups"]>=MIN_BIRDS_GE3_GROUPS)
    meta["admission"]=(ADMIT if feasible else
                       "NOT_ADMITTED_V77_FOUR_WAY_TIDE_LIGHT_SOURCE")
    return four,meta

def score_fourway_difference_in_differences(four,source,source_preflights,*,seed=20261108):
    if source.get("admission")!=ADMIT:
        return {
            "original_fourway_source_gate":source,
            "flood_minus_ebb_of_NIGHT_minus_DAY":
                "NOT_ESTIMATED_SOURCE_GATE"}
    cache={}
    contrast=defaultdict(lambda:defaultdict(list))
    ebb=defaultdict(lambda:defaultdict(list))
    flood=defaultdict(lambda:defaultdict(list))
    group_sign=Counter()
    for (bird,month,heightbin),phases in four.items():
        def avg(source_refs):
            values=[]
            for m,i in source_refs:
                if m!=month:
                    raise ValueError("SOURCE_STOP_V77_ORIGINAL_MONTH_MISMATCH")
                k=(m,i)
                if k not in cache:
                    q=source_preflights[m]
                    cache[k]=_rank(q["model_expo"],
                                  int(q["closest"][i]),
                                  q["circles"][i])-.5
                values.append(cache[k])
            return float(np.mean(values))
        d_ebb=avg(phases[-1]["NIGHT"])-avg(phases[-1]["DAY"])
        d_flood=avg(phases[1]["NIGHT"])-avg(phases[1]["DAY"])
        difference=d_flood-d_ebb
        contrast[bird][month].append(difference)
        ebb[bird][month].append(d_ebb)
        flood[bird][month].append(d_flood)
        group_sign["positive" if difference>0 else "nonpositive"]+=1
    main=_aggregate_original_bird_months(contrast,seed=seed)
    low,high=main["whole_original_bird_10000_bootstrap95"]
    v=main["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"]
    if v>0 and low>0:
        status="EXPLORATORY_POSITIVE_TIDE_PHASE_BY_SOLAR_FOUR_WAY_DIFFERENCE_IN_DIFFERENCES"
    elif v<0 and high<0:
        status="EXPLORATORY_NEGATIVE_TIDE_PHASE_BY_SOLAR_FOUR_WAY_DIFFERENCE_IN_DIFFERENCES"
    else:
        status="FOUR_WAY_TIDE_LIGHT_INTERACTION_NOT_ESTABLISHED"
    return {
        "original_fourway_source_gate":source,
        "original_2010_Schier_RWS_tide_phase_by_astro_light_interaction":{
            "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY":main,
            "original_four_way_height_groups_positive_interaction":
                group_sign["positive"],
            "original_four_way_height_groups_nonpositive_interaction":
                group_sign["nonpositive"],
            "original_genuinely_used_GPS_positions_scored":len(cache),
            "frozen_exploratory_primary_status":status},
        "secondary_same_four_way_sample_separate_night_day_effect":{
            "measured_RWS_ebb":_aggregate_original_bird_months(ebb,seed=seed+1),
            "measured_RWS_flood":_aggregate_original_bird_months(flood,seed=seed+2)},
        "post_v76_exploratory_hypothesis_after_viewing_separate_flood_ebb_results":True,
        "original_NIOZ_habitat_source_monthly_model_UNKNOWN_EXPOSURE_UNIT":True,
        "no_original_wild_actual_prey_foraging_or_causal_anticipation_measured":True,
        "no_original_bird_ID_GPS_coordinates_or_tide_times_saved":True}
