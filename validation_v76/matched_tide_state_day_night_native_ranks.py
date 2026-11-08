"""v76 real bird-month tidal-phase/height matched day-vs-night model index ranks.

POST-v75 exploratory. Source-only genuine RWS tide and solar classes
are matched BEFORE any modelled habitat-use ranks are inspected.
"""
from collections import Counter,defaultdict
from datetime import timedelta,timezone
import math
import numpy as np
from astral import Observer
from astral.sun import elevation
from wild_2010_modelled_tidal_exposure_rank import (
    MONTHS,_rank,_whole_bird_bootstrap)

PRIMARY_BIN_METRES=.2
OTHER_BINS=(.1,.4)
TWILIGHT_DEGREES=3.
DAY_NIGHT_MIN_PER_CONDITION=5
SOURCE_MIN_STRATA=50
SOURCE_MIN_FIXES=1000
SOURCE_MIN_BIRDS=5
SOURCE_MIN_MONTHS=3
SOURCE_MIN_STRATA_EACH_PHASE=10
SOURCE_MIN_BIRDS_GE2_STRATA=5
SOURCE_ORIGINAL_GPS_CLOCK_SHIFT=-15

def tide_light_source_groups(preflights,tide,*,height_bin=.2,
                             shift_seconds=0,synthetic_labels=None,
                             required_geo_status="SOURCE_ADMITTED_V75_ORIGINAL_GPS_2010_MONTH_NATIVE_MODEL_1KM",
                             required_months=MONTHS):
    """Return source groups; physically original measured tide, no index values."""
    if height_bin not in (PRIMARY_BIN_METRES,)+OTHER_BINS:
        raise ValueError("SOURCE_STOP_V76_UNFROZEN_HEIGHT_BIN")
    if shift_seconds not in (0,SOURCE_ORIGINAL_GPS_CLOCK_SHIFT):
        raise ValueError("SOURCE_STOP_V76_UNFROZEN_GPS_CLOCK_SHIFT")
    if sorted(preflights)!=list(required_months):
        raise ValueError("SOURCE_STOP_V76_UNFROZEN_MONTH_SUBSET")
    for m in required_months:
        if preflights[m]["source_receipt"]["fixed_source_admission"]!=required_geo_status:
            return {},{"admission":"NOT_ADMITTED_V76_PRIOR_SPATIAL_SOURCE",
                       "model_used_index_not_read":True}
    events=defaultdict(lambda:{"DAY":[],"NIGHT":[]})
    exclusions=Counter()
    source_geofixes=0
    for month in required_months:
        p=preflights[month]
        for i,(bird,dt,lat,lon) in enumerate(p["fixes"]):
            if not p["valid"][i] or bird not in p["valid_birds"]:
                exclusions["v75_source_geographic_or_bird_month"]+=1;continue
            source_geofixes+=1
            observed=dt.replace(tzinfo=timezone.utc)+timedelta(seconds=shift_seconds)
            if synthetic_labels is None:
                try:
                    height,phase,_=tide.at_with_phase(
                        observed,lookback_minutes=20,
                        tolerance_m_per_hour=.012)
                except ValueError:
                    exclusions["original_measured_RWS_tide_gap"]+=1;continue
                if phase not in (-1,1):
                    exclusions["original_measured_RWS_slack"]+=1;continue
                altitude=float(elevation(
                    Observer(latitude=lat,longitude=lon,elevation=0),
                    observed,with_refraction=True))
                if altitude>TWILIGHT_DEGREES:light="DAY"
                elif altitude< -TWILIGHT_DEGREES:light="NIGHT"
                else:
                    exclusions["original_astronomical_twilight_plus_minus3deg"]+=1
                    continue
            else:
                height,phase,light=synthetic_labels(bird,month,i)
                if phase not in (-1,1) or light not in ("DAY","NIGHT"):
                    raise ValueError("SOURCE_STOP_V76_SYNTHETIC_LABEL_INVALID")
            key=(bird,month,int(phase),math.floor(height/height_bin))
            events[key][light].append((month,i))
    paired={key:x for key,x in events.items()
            if len(x["DAY"])>=DAY_NIGHT_MIN_PER_CONDITION and
               len(x["NIGHT"])>=DAY_NIGHT_MIN_PER_CONDITION}
    phases=Counter(key[2] for key in paired)
    birds=Counter(key[0] for key in paired)
    nday=sum(len(x["DAY"]) for x in paired.values())
    nnight=sum(len(x["NIGHT"]) for x in paired.values())
    admitted=(len(paired)>=SOURCE_MIN_STRATA
              and nday+nnight>=SOURCE_MIN_FIXES
              and len(birds)>=SOURCE_MIN_BIRDS
              and len({k[1] for k in paired})>=SOURCE_MIN_MONTHS
              and phases[-1]>=SOURCE_MIN_STRATA_EACH_PHASE
              and phases[1]>=SOURCE_MIN_STRATA_EACH_PHASE
              and sum(x>=2 for x in birds.values())>=SOURCE_MIN_BIRDS_GE2_STRATA)
    source={
        "original_valid_2010_GPS_hourly_fix_candidates":source_geofixes,
        "true_RWS_height_bin_metres":height_bin,
        "original_native_GPS_clock_shift_seconds":shift_seconds,
        "astronomical_solar_excluded_twilight_degrees":TWILIGHT_DEGREES,
        "original_all_candidate_same_bird_month_phase_height_groups":len(events),
        "original_paired_condition_groups_ge5_day_and_night":len(paired),
        "original_genuine_day_GPS_positions_in_matched_tide_conditions":nday,
        "original_genuine_night_GPS_positions_in_matched_tide_conditions":nnight,
        "original_distinct_birds_in_tide_matched_groups":len(birds),
        "original_birds_with_ge2_matched_groups":sum(x>=2 for x in birds.values()),
        "original_distinct_months_in_paired_conditions":len({k[1] for k in paired}),
        "original_physical_RWS_ebb_strata":phases[-1],
        "original_physical_RWS_flood_strata":phases[1],
        "original_source_excluded_GPS_reasons":dict(exclusions),
        "no_model_index_or_next_heading_used_in_pair_matching":True,
        "admission":(
          "SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE"
          if admitted else "NOT_ADMITTED_V76_TIDE_MATCHED_DAY_NIGHT_SOURCE")}
    return paired,source

def _aggregate_original_bird_months(per_bird_month,seed=20261108):
    original=[]
    units=0
    for bird,months in sorted(per_bird_month.items()):
        group=[float(np.mean(x)) for _,x in sorted(months.items())]
        if not group:continue
        original.append(float(np.mean(group)))
        units+=len(group)
    if not original:return None
    estimate=float(np.mean(original))
    return {
        "original_independent_birds":len(original),
        "original_bird_months_with_true_tide_day_night_match":units,
        "bird_equal_month_equal_matched_tide_NIGHT_minus_DAY":estimate,
        "whole_original_bird_10000_bootstrap95":_whole_bird_bootstrap(
            original,seed=seed,draws=10000),
        "original_birds_with_night_higher":sum(x>0 for x in original),
        "original_individual_deltas_NOT_serialized":True}

def score_matched_tide_day_night(paired,qa,preflights,seed=20261108):
    if qa.get("admission")!=(
        "SOURCE_ADMITTED_V76_ORIGINAL_REAL_SAME_BIRD_MONTH_TIDE_STATE"):
        return {"source_only_original_tide_light_support":qa,
                "original_wild_day_night_exposure_rank_effect":
                    "NOT_ESTIMATED_SOURCE_GATE"}
    # This is the first moment the ORIGINAL model used-cell values are read.
    private_ranks={}
    all_birds=defaultdict(lambda:defaultdict(list))
    byphase={
        -1:defaultdict(lambda:defaultdict(list)),
         1:defaultdict(lambda:defaultdict(list))}
    strata_signs=Counter()
    for (bird,month,phase,heightbin),solar in paired.items():
        def rank_mean(elements):
            v=[]
            for m,i in elements:
                key=(m,i)
                if key not in private_ranks:
                    p=preflights[m]
                    private_ranks[key]=_rank(p["model_expo"],
                        int(p["closest"][i]),p["circles"][i])-.5
                v.append(private_ranks[key])
            return float(np.mean(v))
        d=rank_mean(solar["NIGHT"])-rank_mean(solar["DAY"])
        all_birds[bird][month].append(d)
        byphase[phase][bird][month].append(d)
        strata_signs["positive" if d>0 else "nonpositive"]+=1
    primary=_aggregate_original_bird_months(all_birds,seed)
    delta=primary["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"]
    low,high=primary["whole_original_bird_10000_bootstrap95"]
    if delta>0 and low>0:
        status="EXPLORATORY_MATCHED_RWS_TIDE_NIGHT_HIGHER_MODELED_SPATIAL_INDEX"
    elif delta<0 and high<0:
        status="EXPLORATORY_MATCHED_RWS_TIDE_NIGHT_LOWER_MODELED_SPATIAL_INDEX"
    else:
        status="MATCHED_DAY_NIGHT_TIDAL_MODEL_INDEX_DIFFERENCE_NOT_ESTABLISHED"
    return {
        "original_source_matched_tide_height_phase_solar_gate":qa,
        "primary_original_wild_same_bird_month_rws_tide_matched_ordinal_rank":{
            **primary,
            "original_stratum_level_night_higher_count":strata_signs["positive"],
            "original_stratum_level_night_not_higher_count":strata_signs["nonpositive"],
            "original_GPS_positions_used_for_matched_rank":len(private_ranks),
            "frozen_exploratory_main_status":status},
        "secondary_original_ebb_and_flood_stratum_comparisons":{
            "ebb":_aggregate_original_bird_months(byphase[-1],seed+1),
            "flood":_aggregate_original_bird_months(byphase[1],seed+2)},
        "this_is_POST_v75_known_unmatched_night_day_result_not_new_confirmation":True,
        "NIOZ_exposure_is_modelled_monthly_unit_UNKNOWN":True,
        "native_GPS_timestamp_absolute_UTC_not_independently_calibrated":True,
        "no_observed_feeding_prey_habitat_accessibility_or_social_tidal_control":True}
