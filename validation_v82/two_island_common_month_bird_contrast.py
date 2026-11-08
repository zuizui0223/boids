"""v82 common-month real wild Schier and Ameland tidal light site contrast.

This is post-v81 EXPLORATORY. Both sites have same exact 2010 June-Dec
model months and true independently observed 10minute RWS tide, same
four-cell height/phase/solar matching and same 1-km local NIOZ ordinal rank.
June/July original model latitude is MISSING; only source-certified static
NIOZ *model* coordinate template is explicitly inferred in both sites.
Original bird values never leave the process: output contains cluster
aggregates only and no animal IDs, exact times, locations, model pixels.
"""
from __future__ import annotations
from collections import Counter,defaultdict

import numpy as np
from scipy.spatial import cKDTree

from wild_2010_modelled_tidal_exposure_rank import _locxy,_rank
from matched_tide_state_day_night_native_ranks import tide_light_source_groups
from tide_solar_four_way_source_and_effect import (
    fourway_source_only,score_fourway_difference_in_differences,ADMIT)

SOURCE_MONTHS=(6,7,8,9,10,11,12)
LATE_MONTHS=(8,9,10,11,12)
SCHIER_SOURCE={
    6:(8874,19),7:(12250,19),8:(11427,16),9:(9572,16),
    10:(9508,15),11:(7975,14),12:(6656,14)}
AMELAND_SOURCE={
    6:(6450,15),7:(5321,8),8:(5106,7),9:(4581,7),
    10:(3629,7),11:(3220,6),12:(3076,6)}
STATUS="SOURCE_ADMITTED_V82_SITE_TRUE_GPS_JUN_DEC_NATIVE_OR_EXPLICIT_MODEL_GRID"
SOURCE_MODEL_EXPECTED_CELLS=398520
REFERENCE_RADIUS_METRES=1000
MIN_MODEL_NEIGHBORS=20
MAX_GPS_TO_MODEL_CENTER_METRES=300
MIN_MONTH_SOURCE_FIXES=200
MIN_MONTH_SOURCE_BIRDS=5
MIN_BIRD_MONTH_SOURCE_GPS=20
MIN_SOURCE_GEOGRAPHIC_COVER=.80
EXPECTED_V77_LATE_SCHIER=(655,16,.03803110272968872)
EXPECTED_V81_FULL_AMELAND=(381,10,.0052737884296153855)
EXPECTED_V78_NATIVE_AMELAND=(267,7)
SITE_BOOT_SEED=20261108
SITE_BOOT_DRAWS=10000

def geographic_month_source(site,month,fixes,model):
    """Original GPS–native source model spatial opportunity; NO use rank read."""
    if site not in ("Schier","Ameland") or month not in SOURCE_MONTHS:
        raise ValueError("SOURCE_STOP_V82_WRONG_STUDY_SITE_OR_MONTH")
    expected=(SCHIER_SOURCE if site=="Schier" else AMELAND_SOURCE)[month]
    n=len(fixes);birds=len({row[0] for row in fixes})
    if (n,birds)!=expected:
        raise ValueError("SOURCE_STOP_V82_PREVIOUS_SOURCE_MONTH_COUNT_DRIFT")
    if model["n_native"]!=SOURCE_MODEL_EXPECTED_CELLS:
        raise ValueError("SOURCE_STOP_V82_SOURCE_ORIGINAL_NIOZ_GRID_SHAPE")
    xy=_locxy([r[2] for r in fixes],[r[3] for r in fixes])
    tree=model["tree"]
    nearest,index=tree.query(xy,k=1)
    geo=nearest<=MAX_GPS_TO_MODEL_CENTER_METRES
    circles=tree.query_ball_point(xy,r=REFERENCE_RADIUS_METRES)
    hasgeo=np.asarray([geo[i] and len(circles[i])>=MIN_MODEL_NEIGHBORS
                       for i in range(n)],dtype=bool)
    source_bird_counts=Counter(fixes[i][0] for i in np.flatnonzero(hasgeo))
    eligible_birds={bird for bird,count in source_bird_counts.items()
                    if count>=MIN_BIRD_MONTH_SOURCE_GPS}
    qa={
        "site":site,
        "original_2010_month":month,
        "original_hourly_GPS_source_positions":n,
        "original_real_bird_IDs_in_month":birds,
        "original_NIOZ_month_model_grid_cells":model["n_native"],
        "genuine_GPS_source_nearest_model_grid_within300m":int(geo.sum()),
        "genuine_GPS_source_nearest_model_grid_fraction":float(geo.mean()),
        "original_GPS_source_positions_with_full_1km_geographic_reference":
            int(hasgeo.sum()),
        "original_real_birds_ge20_GPS_source_positions_with_native_reference":
            len(eligible_birds),
        "source_eligible_native_GPS_after_bird_month_gate":
            sum(source_bird_counts[b] for b in eligible_birds),
        "original_model_used_index_values_NOT_READ_FOR_SOURCE":True,
        "original_native_JunJul_lat_missing_requires_labelled_static_template":
            month in (6,7)}
    good=(n>=MIN_MONTH_SOURCE_FIXES and birds>=MIN_MONTH_SOURCE_BIRDS and
          geo.mean()>=MIN_SOURCE_GEOGRAPHIC_COVER and
          hasgeo.sum()>=MIN_MONTH_SOURCE_FIXES and
          len(eligible_birds)>=MIN_MONTH_SOURCE_BIRDS)
    qa["fixed_source_admission"]=STATUS if good else (
        "NOT_ADMITTED_V82_ORIGINAL_2010_GPS_NATIVE_MODEL_MONTH_SOURCE")
    return {
        "source_receipt":qa,
        "fixes":fixes,
        "xy":xy,
        "closest":index,
        "circles":circles,
        "valid":hasgeo,
        "valid_birds":eligible_birds,
        "model_expo":model["index"],
        "tree":tree}

def prepare_whole_site(site,monthly,models):
    """Gate all seven before any bird used-model numeric value is scored."""
    if sorted(monthly)!=list(SOURCE_MONTHS) or sorted(models)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V82_UNBALANCED_OR_FAVORABLE_MONTH_SUBSET")
    result={month:geographic_month_source(site,month,monthly[month],models[month])
            for month in SOURCE_MONTHS}
    ok=all(r["source_receipt"]["fixed_source_admission"]==STATUS
           for r in result.values())
    return result,{
        "original_source_site":site,
        "predeclared_original_2010_common_calendar_months":list(SOURCE_MONTHS),
        "all_seven_original_model_and_bird_sources_admitted":ok,
        "original_month_source_receipts":{
           str(m):result[m]["source_receipt"] for m in SOURCE_MONTHS},
        "no_model_used_at_GPS_index_score_done_before_gate":True}

def true_fourcell_source(source,tide,*,months=SOURCE_MONTHS):
    if sorted(source)!=list(months):
        raise ValueError("SOURCE_STOP_V82_FOURCELL_MONTHS_NOT_SHARED")
    pair,qa=tide_light_source_groups(
        source,tide,required_geo_status=STATUS,required_months=months,
        height_bin=.2,shift_seconds=0)
    four,meta=fourway_source_only(pair,qa,verify_original_replay=False)
    months_inferred={6,7}
    n_inferred=sum(k[1] in months_inferred for k in four)
    fixes_inferred=sum(
        len(phase[light])
        for (bird,month,height),phases in four.items()
        if month in months_inferred
        for side,phase in phases.items()
        for light in ("DAY","NIGHT"))
    receipt={
        "prior_matched_tide_source":qa,
        "all_four_conditions_same_real_bird_month_height_source":meta,
        "original_source_four_condition_groups_using_INFERRED_JunJul_mesh":n_inferred,
        "original_source_four_condition_groups_using_GENUINE_native_AugDec_model_coords":
           len(four)-n_inferred,
        "original_source_four_condition_GPS_positions_in_JunJul_INFERRED_mesh":
            fixes_inferred,
        "scientific_no_actual_original_JunJul_native_lat_values":True}
    return four,receipt

def _private_original_bird_means(four,source_preflights):
    """Exactly v77 4-way individual→month→height hierarchy. NEVER export."""
    per_bird_month=defaultdict(lambda:defaultdict(list))
    cached={}
    for (bird,month,heightbin),phases in four.items():
        def group_mean(gps_source):
            values=[]
            for m,i in gps_source:
                if m!=month:raise ValueError("SOURCE_STOP_V82_SOURCE_MONTH_MISMATCH")
                k=(m,i)
                if k not in cached:
                    p=source_preflights[m]
                    cached[k]=_rank(
                        p["model_expo"],int(p["closest"][i]),p["circles"][i])-.5
                values.append(cached[k])
            return float(np.mean(values))
        down=group_mean(phases[-1]["NIGHT"])-group_mean(phases[-1]["DAY"])
        up=group_mean(phases[1]["NIGHT"])-group_mean(phases[1]["DAY"])
        per_bird_month[bird][month].append(up-down)
    values=np.asarray([
        float(np.mean([float(np.mean(groups))
                        for month,groups in sorted(months.items())]))
        for bird,months in sorted(per_bird_month.items())],float)
    if len(values)==0 or not np.isfinite(values).all():
        raise ValueError("ESTIMAND_STOP_V82_NO_PRIVATE_ORIGINAL_BIRDS")
    return values

def _site_bird_boot(values,seed):
    rng=np.random.default_rng(seed)
    inds=rng.integers(0,len(values),size=(SITE_BOOT_DRAWS,len(values)))
    estimates=values[inds].mean(axis=1)
    return [float(t) for t in np.quantile(estimates,[.025,.975])]

def independent_bird_site_contrast(schier,ameland):
    """Source-site conditional, separately resample original birds by island."""
    s=np.asarray(schier,dtype=float)
    a=np.asarray(ameland,dtype=float)
    if (s.ndim!=1 or a.ndim!=1 or not len(s) or not len(a)
        or not np.isfinite(s).all() or not np.isfinite(a).all()):
        raise ValueError("ESTIMAND_STOP_V82_INVALID_BIRD_SITE_BLOCKS")
    point=float(s.mean()-a.mean())
    rng=np.random.default_rng(SITE_BOOT_SEED)
    sampled_s=rng.integers(0,len(s),size=(SITE_BOOT_DRAWS,len(s)))
    sampled_a=rng.integers(0,len(a),size=(SITE_BOOT_DRAWS,len(a)))
    draws=s[sampled_s].mean(axis=1)-a[sampled_a].mean(axis=1)
    interval=[float(x) for x in np.quantile(draws,[.025,.975])]
    label=("SITE_BIRD_CONDITIONAL_POSITIVE_SCHIER_GREATER_THAN_AMELAND"
           if point>0 and interval[0]>0 else
           "SITE_BIRD_CONDITIONAL_NEGATIVE_SCHIER_LESS_THAN_AMELAND"
           if point<0 and interval[1]<0 else
           "SITE_BIRD_CONDITIONAL_DIFFERENCE_NOT_ESTABLISHED")
    return {
        "site_contrast_original_2_sites_not_random_ocean_samples":True,
        "original_true_birds_in_Schier":len(s),
        "original_true_birds_in_Ameland":len(a),
        "Schier_bird_equal_minus_Ameland_bird_equal":point,
        "original_site_independent_whole_bird_10000_bootstrap95":interval,
        "point_positive_or_negative_status":label,
        "original_site_independent_bird_draws":SITE_BOOT_DRAWS,
        "model_index_unit":"UNKNOWN_NATIVE_MONTHLY_ORDINAL_ONLY",
        "template_original_JunJul_lat_NEVER_observed":True}

def _exact_site_replay(site,four,preflight,*,expected=None):
    """After all two-site source gates: old public v77 scorer == new bird means."""
    legacy=score_fourway_difference_in_differences(
        four,{"admission":ADMIT},preflight)
    a=legacy["original_2010_Schier_RWS_tide_phase_by_astro_light_interaction"][
        "frozen_primary_genuine_flood_NIGHT_DAY_minus_ebb_NIGHT_DAY"]
    original_birds=_private_original_bird_means(four,preflight)
    current=float(original_birds.mean())
    if abs(current-a["bird_equal_month_equal_matched_tide_NIGHT_minus_DAY"])>1e-12:
        raise ValueError("ESTIMAND_STOP_V82_NEW_PRIVATE_BIRD_HIERARCHY_NOT_V77")
    computed95=_site_bird_boot(original_birds,SITE_BOOT_SEED)
    old95=a["whole_original_bird_10000_bootstrap95"]
    if not np.allclose(computed95,old95,rtol=0,atol=1e-12):
        raise ValueError("ESTIMAND_STOP_V82_CLUSTER_BOOTSTRAP_NOT_ORIGINAL_V77")
    if expected is not None:
        n_group,n_birds,estimate=expected
        if (len(four)!=n_group or len(original_birds)!=n_birds or
            abs(current-estimate)>1e-10):
            raise ValueError("SOURCE_STOP_V82_PRIOR_KNOWN_ORIGINAL_SITE_RESULT_DRIFT")
    return original_birds,{
        "source_site":site,
        "original_four_way_tide_light_groups":len(four),
        "original_real_birds":len(original_birds),
        "site_original_bird_equal_D_floodNightDay_minus_ebbNightDay":current,
        "site_true_bird_10000_bootstrap95":computed95,
        "original_birds_positive":int(np.sum(original_birds>0)),
        "reproduces_v77_and_native_source_bird_cluster_exactly":True,
        "no_original_bird_ID_or_individual_estimate_exported":True}

def new_two_site_difference(schier_source,ameland_source,schier_four,ameland_four,
                            schier_meta,ameland_meta):
    """Primary after BOTH source gates: Δ=Schier D_i mean−Ameland D_i mean.

    Cluster intervals condition on two SELECTED sites. Not a random-coast CI.
    """
    gates=(schier_meta["all_four_conditions_same_real_bird_month_height_source"],
           ameland_meta["all_four_conditions_same_real_bird_month_height_source"])
    if any(g["admission"]!=ADMIT for g in gates):
        return {
            "site_comparison_source_gate":"NOT_ADMITTED_V82_BOTH_ISLAND_ORIGINAL_4WAY",
            "common_calendar_bird_site_interaction_difference":
                "NOT_ESTIMATED_SOURCE_GATE"}
    old_schier_four={k:v for k,v in schier_four.items() if k[1] in LATE_MONTHS}
    prior_s,receipt_s=_exact_site_replay(
        "Schier_prior_AugDec",old_schier_four,schier_source,
        expected=EXPECTED_V77_LATE_SCHIER)
    prior_a,receipt_a=_exact_site_replay(
        "Ameland_prior_JunDec",ameland_four,ameland_source,
        expected=EXPECTED_V81_FULL_AMELAND)
    # This explicitly checks previous frozen studies without changing their
    # respective month frames; the NEW primary uses both 7-month frames.
    schier,site_s=_exact_site_replay(
        "Schier_same_JunDec",schier_four,schier_source)
    ameland,site_a=_exact_site_replay(
        "Ameland_same_JunDec",ameland_four,ameland_source)
    contrast=independent_bird_site_contrast(schier,ameland)
    return {
        "site_comparison_source_gate":"ADMITTED_BOTH_SITE_COMMON_JUN_DEC_ORIGINAL_REAL_BIRDS",
        "new_common_month_original_bird_site_effects":{
            "Schier":site_s,"Ameland":site_a},
        "original_site_old_result_replays_separately":{
            "Schier_v77_old_AugDec_original_effect":receipt_s,
            "Ameland_v81_old_JunDec_original_effect":receipt_a,
            "original_Ameland_v78_native_only_7bird_gate_still_UNSCORED":True},
        "primary_same_original_2010_JuneDec_site_CONTRAST_S_minus_A":contrast,
        "no_bird_tags_or_per_bird_Ds_serialized":True}
