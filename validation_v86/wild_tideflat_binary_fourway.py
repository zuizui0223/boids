"""v86 original wild oystercatcher GPS binary mid/high tideflat-use 4-way test.

Outcome Y=1 iff the ORIGINAL GPS nearest *all* NIOZ model native center
(<=300m, source-verified) falls within independent published WMR ecotope
litoralcode3/4. Y=0 means any other mapped/unmapped class incl low2.
Use all original Schier/Ameland 2010 Jun-Dec native bird×hour GPS and same
true RWS measured waterheight + physical flood/ebb × DAY/NIGHT matches
from v82. Source 4-cell labels are fixed BEFORE GPS Y is examined.
Only 2008-12 public WMR map source, exact corrected v2 version UNVERIFIED,
no true 2010 per-tide exposure, food or recorded foraging.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import numpy as np
from two_island_common_month_bird_contrast import (
    independent_bird_site_contrast)
from tide_solar_four_way_source_and_effect import ADMIT

FROZEN_SOURCE_REAL_2010={
    "Schier":(857,18,41734),
    "Ameland":(381,10,19407)}
ORIGINAL_NATIVE_SOURCE_CELLS=398520
MIN_CLASS4_SOURCE_GPS_FIXES=100
SEED=20261108
BOOT=10000
SITES=("Schier","Ameland")
FROZEN_SOURCE_STATUS=ADMIT
MAIN_NAME="real_GPS_mid_high_WMR_intertidal_habitat_use_binary_fourway_fraction"

def hard_before_outcome_both_sites(matched):
    """Source-only original 2010 RWS/solar GPS group replay, not Y."""
    if set(matched)!=set(SITES):
        raise ValueError("SOURCE_STOP_V86_BOTH_ORIGINAL_GPS_SITES_REQUIRED")
    output={}
    for site in SITES:
        four,qa=matched[site]
        original=qa["all_four_conditions_same_real_bird_month_height_source"]
        expected=FROZEN_SOURCE_REAL_2010[site]
        observed=(len(four),
                  original.get("original_birds_in_all_four_tide_and_light_conditions"),
                  original.get("original_four_way_source_fix_count"))
        if original.get("admission")!=FROZEN_SOURCE_STATUS or observed!=expected:
            raise ValueError("SOURCE_STOP_V86_ORIGINAL_V82_2010_RWS_SOLAR_SOURCE_DRIFT")
        output[site]={
            "original_same_individual_month_0p2m_level_all4_tide_solar_strata":
                observed[0],
            "original_identified_real_birds_in_source":observed[1],
            "original_gps_locations_in_matching":observed[2],
            "source_confirmed_before_examining_WMR_GPS_ecotope_Y":True}
    return output

def _real_bird_aggregate(perbird):
    """One array element per ORIGINAL bird; equal months then bird mean."""
    arr=[]
    for bird,month_dict in sorted(perbird.items()):
        month_means=[np.mean(z) for _,z in sorted(month_dict.items()) if len(z)]
        if month_means:arr.append(float(np.mean(month_means)))
    v=np.asarray(arr,dtype=float)
    if not len(v) or not np.isfinite(v).all():
        raise ValueError("ESTIMAND_STOP_V86_ORIGINAL_BIRD_BLOCKS_EMPTY")
    return v

def _boot_site(v,seed=SEED):
    rng=np.random.default_rng(seed)
    choices=rng.integers(0,len(v),size=(BOOT,len(v)))
    return [float(x) for x in np.quantile(v[choices].mean(1),[.025,.975])]

def _score_original_site(site,original_four,preflights,class_array,*,positive_codes=(3,4)):
    if site not in SITES:
        raise ValueError("ESTIMAND_STOP_V86_UNKNOWN_ORIGINAL_SITE")
    if (class_array.shape!=(ORIGINAL_NATIVE_SOURCE_CELLS,) or
        np.any(~np.isin(class_array,[0,3,4]))):
        raise ValueError("ESTIMAND_STOP_V86_WRONG_PINNED_WMR_NATIVE_CLASS_SOURCE")
    if not set(positive_codes)<=set((3,4)):
        raise ValueError("ESTIMAND_STOP_V86_UNREGISTERED_WMR_CLASS")
    blocks=defaultdict(lambda:defaultdict(list))
    ebb=defaultdict(lambda:defaultdict(list))
    flood=defaultdict(lambda:defaultdict(list))
    props=defaultdict(list)
    total=Counter()
    eligible=Counter()
    group_signs=Counter()
    for (bird,month,heightbin),conditions in original_four.items():
        def fraction(phase,light):
            selected=conditions[phase][light]
            value=[]
            for m,i in selected:
                if m!=month:
                    raise ValueError("ESTIMAND_STOP_V86_ORIGINAL_MONTH_MISMATCH")
                model_index=int(preflights[m]["closest"][i])
                if model_index<0 or model_index>=ORIGINAL_NATIVE_SOURCE_CELLS:
                    raise ValueError("ESTIMAND_STOP_V86_BAD_GPS_TO_NIOZ_SOURCE_INDEX")
                # THIS is the first contact with actual GPS ecotope Y after
                # hard replay of full ORIGINAL bird×RWS height×phase×solar
                # fourway source groups at both islands.
                code=int(class_array[model_index])
                value.append(1.0 if code in positive_codes else 0.0)
                total[f"{'flood' if phase>0 else 'ebb'}_{light.lower()}"]+=1
                if code in positive_codes:
                    eligible[f"{'flood' if phase>0 else 'ebb'}_{light.lower()}"]+=1
            if not value:
                raise ValueError("ESTIMAND_STOP_V86_EMPTY_TRUE_ORIGINAL_GPS_TIDE_SOLAR_CELL")
            avg=float(np.mean(value))
            props[(phase,light)].append(avg)
            return avg
        ef=fraction(-1,"NIGHT")-fraction(-1,"DAY")
        ff=fraction( 1,"NIGHT")-fraction( 1,"DAY")
        d=ff-ef
        blocks[bird][month].append(d)
        ebb[bird][month].append(ef)
        flood[bird][month].append(ff)
        group_signs["positive" if d>0 else "nonpositive"]+=1
    bird=_real_bird_aggregate(blocks)
    bird_ebb=_real_bird_aggregate(ebb)
    bird_flood=_real_bird_aggregate(flood)
    if len(bird_ebb)!=len(bird) or len(bird_flood)!=len(bird):
        raise ValueError("ESTIMAND_STOP_V86_NOT_SAME_BIRD_PHASE_SUPPORT")
    mean=float(bird.mean())
    ci=_boot_site(bird)
    if mean>0 and ci[0]>0:
        status="EXPLORATORY_POSITIVE_RWS_TIDE_PHASE_BY_SOLAR_INTERTIDAL_POSITION_PROBABILITY"
    elif mean<0 and ci[1]<0:
        status="EXPLORATORY_NEGATIVE_RWS_TIDE_PHASE_BY_SOLAR_INTERTIDAL_POSITION_PROBABILITY"
    else:
        status="WMR_MIDHIGH_TIDE_BY_SOLAR_POSITION_FOURWAY_NOT_ESTABLISHED"
    summary={
        "site":site,
        "source_original_birds":len(bird),
        "original_full_four_way_RWS_tide_solar_strata":len(original_four),
        "outcome_positive_WMR_litoralcode_classes":list(positive_codes),
        "primary_binary_GPS_position_in_intertidal_probability_D":{
            "site_original_true_bird_equal_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY":
                mean,
            "true_bird_10000_bootstrap95":ci,
            "original_birds_positive_D":int((bird>0).sum()),
            "original_strata_positive_D":group_signs["positive"],
            "original_strata_nonpositive_D":group_signs["nonpositive"],
            "fixed_exploratory_class_status":status},
        "real_source_original_gps_fix_count_by_tide_and_solar":dict(total),
        "real_native_mid_high_class_GPS_fix_count_by_tide_solar":dict(eligible),
        "group_mean_GPS_mid_high_fraction_DESCRIPTIVE_not_bird_equal":{
            ("flood" if phase>0 else "ebb")+"_"+light.lower():
                float(np.mean(z))
            for (phase,light),z in props.items()},
        "secondary_same_4way_sample_separate_ebb_night_minus_day":{
            "original_bird_mean":float(bird_ebb.mean()),
            "bird_bootstrap95":_boot_site(bird_ebb,SEED+1)},
        "secondary_same_4way_sample_separate_flood_night_minus_day":{
            "original_bird_mean":float(bird_flood.mean()),
            "bird_bootstrap95":_boot_site(bird_flood,SEED+2)},
        "original_per_bird_D_or_GPS_location_not_exported":True,
        "not_measured_feeding_or_wet_dry_habitat_availability":True}
    return bird,summary

def score_binary_original_two_sites_if_source_gated(
    matched,preflights,class_source):
    source=hard_before_outcome_both_sites(matched)
    for site in SITES:
        if (site not in class_source or
            class_source[site]["class"].shape!=(ORIGINAL_NATIVE_SOURCE_CELLS,)):
            raise ValueError("SOURCE_STOP_V86_STATIC_WMR_SOURCE_CLASS_MASK_UNAVAILABLE")
    original={}
    values={}
    for site in SITES:
        full,qa=matched[site]
        a,r=_score_original_site(
            site,full,preflights[site],class_source[site]["class"],
            positive_codes=(3,4))
        values[site]=a
        original[site]=r
    contrast=independent_bird_site_contrast(values["Schier"],values["Ameland"])
    mid_only={}
    for site in SITES:
        _,r=_score_original_site(
            site,matched[site][0],preflights[site],class_source[site]["class"],
            positive_codes=(3,))
        mid_only[site]=r
    count_high={
        s:sum(int(v["class"][int(preflights[s][m]["closest"][i])]==4)
               for key,group in matched[s][0].items()
               for p in (-1,1)
               for light in ("DAY","NIGHT")
               for m,i in group[p][light])
        for s,v in class_source.items()}
    if all(count_high[s]>=MIN_CLASS4_SOURCE_GPS_FIXES for s in SITES):
        high_only={}
        for site in SITES:
            _,r=_score_original_site(
                site,matched[site][0],preflights[site],class_source[site]["class"],
                positive_codes=(4,))
            high_only[site]=r
    else:
        high_only={
            "status":"ORIGINAL_WMR_NATIVE_HIGH_ONLY_GPS_SOURCE_TOO_SPARSE",
            "source_class4_GPS_fix_counts":count_high}
    return {
        "new_original_wild_source_replayed_BEFORE_binary_GPS_habitat_Y":source,
        "binary_mid_high_2010_true_wild_RWS_tidal_solar_by_site":original,
        "main_binary_mid_high_GPS_position_two_site_bird_cluster_CONTRAST":
            contrast,
        "secondary_mid_littoral3_only_same_bird_fourway":mid_only,
        "secondary_high_littoral4_only_if_source_100GPS_each":high_only,
        "original_classes_source":"WMR_PUBLISHED_2008_2012_COMPOSITE_2021_MENDELEY_V2_NOT_VERIFIED",
        "response_is_fraction_of_original_recorded_GPS_positions_NOT_STATIONARY_OCCUPANCY_HOURS":True,
        "this_is_a_NEW_binary_habitat_response_not_old_NIOZ_time_expo_ordinal_use_effect":True,
        "no_real_food_feeding_or_true_tide_exposure_observed":True}
