"""v85 true 2010 oystercatcher tidal-light GPS source within WMR mid/high littoral.

All WMR polygon and NIOZ sources are independently publisher-authenticated;
WMR's exact corrected-2021 v2 version remains UNVERIFIED. Only native 3/4.
GPS used on mid/high source geometry is compared to native mid/high background
(no class2, saltmarsh, deep water). Compare original all-cell background on
the IDENTICAL source-qualified GPS points only after both 4-way source gates.
The monthly native NIOZ time_expo unit is UNKNOWN. No bird tags, exact
GPS times, trajectories, model pixels or RWS measured arrays ever published.
"""
from __future__ import annotations

from collections import Counter
import numpy as np
import shapely
from shapely import STRtree
from scipy.spatial import cKDTree

from wmr_original_complete_unfiltered_mid_high_source import (
    _original_full_site, PUBLISHER_FULL_WFS_UNFILTERED_MATCHED)
from wmr_original_midhigh_native_nioz_grid_source import (
    FIXED_SITE_BBOX, METRIC_X, METRIC_Y)
from wild_2010_modelled_tidal_exposure_rank import _locxy
from two_island_common_month_bird_contrast import (
    SOURCE_MONTHS,SCHIER_SOURCE,AMELAND_SOURCE,
    independent_bird_site_contrast,_private_original_bird_means)
from matched_tide_state_day_night_native_ranks import tide_light_source_groups
from tide_solar_four_way_source_and_effect import (
    ADMIT,fourway_source_only,score_fourway_difference_in_differences)

FROZEN_WMR_SHA={
    "Schier":"b77e38c7f60ef5daa8c205b99161fca3ab6c94fa4d75cb49d92c31ae169cd6b1",
    "Ameland":"a52b24afd0b26b12dd8f7ab3373c4e418382bd1d9f01087c2350c85d42fe0531"}
FROZEN_MODEL_SOURCE_CLASS_COUNTS={
    "Schier":{3:4235,4:316},
    "Ameland":{3:3130,4:70}}
FROZEN_PUBLISHER_WFS_COUNT={"Schier":345,"Ameland":280}
GEO_INDEX_CODES=(3,4)
MODEL_NATIVE_SOURCE_N=398520
MAX_GEO_DISTANCE_M=300
REFERENCE_RADIUS_M=1000
MIN_SOURCE_LITTORAL_1KM_CELLS=20
MIN_ORIGINAL_BIRD_MONTH_SOURCE_FIXES=20
SOURCE_COMMON_MONTH_MIN=3
SOURCE_MONTH_SOURCE_BIRDS_MIN=5
SOURCE_MONTH_SOURCE_FIXES_MIN=100
SOURCE_ADMIT="SOURCE_ADMITTED_V85_WMR_MIDHIGH_CLASS_AND_FULL_NATIVE_MODEL_GEOMETRY"
RESULT_STOP="NOT_ESTIMATED_V85_HABITAT_SOURCE_GATE"
MODEL_MONTHS=tuple(SOURCE_MONTHS)
FIXED_TRUE_RWS_TIDAL_HEIGHT_BIN=.20

def classify_native_2010_model_sites(all_xy,site,*,source_getter=_original_full_site,
                                     source_only_diagnostic_waive_RAW_sha=False):
    """Source-only static WMR ecotope class codes, NO original bird GPS."""
    if site not in FROZEN_WMR_SHA:
        raise ValueError("SOURCE_STOP_V85_UNFROZEN_ISLAND")
    if all_xy.shape!=(MODEL_NATIVE_SOURCE_N,2) or not np.isfinite(all_xy).all():
        raise ValueError("SOURCE_STOP_V85_MODEL_GRID_NOT_PREVIOUS_V84C_STATIC")
    original_name="Schiermonnikoog" if site=="Schier" else "Ameland_Nes"
    polygons,receipt=source_getter(original_name,FIXED_SITE_BBOX[original_name])
    raw_same=(receipt["original_full_provider_WFS_response_SHA256_COMPUTED_NOT_PUBLISHER"]==
              FROZEN_WMR_SHA[site])
    if (receipt["original_full_WFS_GetFeature_NO_CQL_source_count"]!=
            FROZEN_PUBLISHER_WFS_COUNT[site] or
        (not raw_same and not source_only_diagnostic_waive_RAW_sha)):
        raise ValueError("SOURCE_STOP_V85_ORIGINAL_V84C_WMR_POLYGON_SHA_DRIFT")
    coords_lon=all_xy[:,0]/METRIC_X
    coords_lat=all_xy[:,1]/METRIC_Y
    xmin,ymin,xmax,ymax=FIXED_SITE_BBOX[original_name]
    selected=np.flatnonzero(
        (coords_lon>=xmin)&(coords_lon<=xmax)&
        (coords_lat>=ymin)&(coords_lat<=ymax))
    if not len(selected):
        raise ValueError("SOURCE_STOP_V85_NO_ORIGINAL_SOURCE_MODEL_CELLS_IN_SITE")
    geos=shapely.points(all_xy[selected])
    tree=STRtree([g for g,_ in polygons])
    hit=tree.query(geos,predicate="intersects")
    classes=np.zeros(len(selected),np.uint8)
    clashes=np.zeros(len(selected),bool)
    for pt,poly in zip(hit[0],hit[1]):
        code=int(polygons[int(poly)][1])
        if code not in GEO_INDEX_CODES:
            raise ValueError("SOURCE_STOP_V85_LOWER_LITTORAL_OR_OTHER_SOURCE_CLASS_USED")
        prev=int(classes[pt])
        if prev and prev!=code:
            clashes[pt]=True
        elif not prev:
            classes[pt]=code
    if clashes.any():
        raise ValueError("SOURCE_STOP_V85_SOURCE_WMR_MIDHIGH_NATIVE_CLASS_CONFLICT")
    full=np.zeros(MODEL_NATIVE_SOURCE_N,dtype=np.uint8)
    full[selected]=classes
    actual=Counter(full.tolist())
    if any(actual[c]!=FROZEN_MODEL_SOURCE_CLASS_COUNTS[site][c]
           for c in GEO_INDEX_CODES):
        raise ValueError("SOURCE_STOP_V85_ORIGINAL_V84C_NATIVE_CLASS_COUNTS_DRIFT")
    admitted=np.flatnonzero((full==3)|(full==4))
    return {
        "source_site":site,
        "class":full,
        "native_reference_xy":all_xy,
        "admitted_native_cell_indices":admitted,
        "native_allowed_center_tree":cKDTree(all_xy[admitted]),
        "source_record":{
           "source_v84C_old_original_WMR_RAW_GeoJSON_sha256":FROZEN_WMR_SHA[site],
           "source_current_original_WMR_RAW_GeoJSON_sha256":
               receipt["original_full_provider_WFS_response_SHA256_COMPUTED_NOT_PUBLISHER"],
           "source_WMR_older_original_RAW_response_SHA_matches":raw_same,
           "source_original_WMR_ALL_CODE0_TO6_canonical_geometry_SHA256":
               receipt["original_all_0_6_native_litoralcode_normalized_geometry_SHA256"],
           "source_WMR_all_original_features_canonically_hashed":
               receipt["original_normalized_source_all_features_count"],
           "source_true_native_2010_mid_high_class_grid_vector_SHA256":
               __import__("hashlib").sha256(full.tobytes()).hexdigest(),
           "source_diagnostic_raw_sha_mismatch_waiver_used_before_GPS_outcomes":
               bool(source_only_diagnostic_waive_RAW_sha),
           "original_WMR_publisher_polygon_count":FROZEN_PUBLISHER_WFS_COUNT[site],
           "native_model_center_count_mid3":actual[3],
           "native_model_center_count_high4":actual[4],
           "source_mid_high_combined_model_center_count":len(admitted),
           "all_other_native_model_centers_excluded_from_strict_reference":
               actual[0],
           "original_WMR_corrected_2021_v2_version_UNVERIFIED":True,
           "low_littoral2_is_NOT_assigned_to_strict_reference":True,
           "source_native_intertidal_pixels_not_observed_bird_accessible_prey":True}}

def source_class_restricted_gps_month(site,month,fixes,native_model,mask):
    """GPS source and WMR-native geometry ONLY; no NIOZ used-index values."""
    if site not in ("Schier","Ameland") or month not in SOURCE_MONTHS:
        raise ValueError("SOURCE_STOP_V85_UNREGISTERED_SOURCE_MONTH")
    observed=(len(fixes),len({f[0] for f in fixes}))
    expected=(SCHIER_SOURCE if site=="Schier" else AMELAND_SOURCE)[month]
    if observed!=expected:
        raise ValueError("SOURCE_STOP_V85_ORIGINAL_V82_WILD_GPS_SOURCE_DRIFT")
    if (native_model["n_native"]!=MODEL_NATIVE_SOURCE_N or
        native_model["xy"].shape!=(MODEL_NATIVE_SOURCE_N,2)):
        raise ValueError("SOURCE_STOP_V85_ORIGINAL_STATIC_NIOZ_NATIVE_PIXELS_DRIFT")
    if mask["class"].shape!=(MODEL_NATIVE_SOURCE_N,):
        raise ValueError("SOURCE_STOP_V85_WMR_NATIVE_MASK_SHAPE")
    # Independently verified static mesh equals both real original source
    # months (June/July geographic template explicitly inferred by v81).
    if not np.array_equal(native_model["xy"],mask["native_reference_xy"]):
        raise ValueError("SOURCE_STOP_V85_NATIVE_MODEL_STATIC_GRID_MONTH_DRIFT")
    xy=_locxy([fix[2] for fix in fixes],[fix[3] for fix in fixes])
    near,close_idx=native_model["tree"].query(xy,k=1)
    within=near<=MAX_GEO_DISTANCE_M
    original_used_ecotope_codes=mask["class"][close_idx]
    in_class=within&np.isin(original_used_ecotope_codes,GEO_INDEX_CODES)
    positions=np.flatnonzero(in_class)
    geo_neighbors=mask["native_allowed_center_tree"].query_ball_point(
        xy[positions],r=REFERENCE_RADIUS_M) if len(positions) else []
    eligible=np.zeros(len(fixes),dtype=bool)
    nearby=[[] for _ in fixes]
    allowed=mask["admitted_native_cell_indices"]
    for i,ns in zip(positions,geo_neighbors):
        if len(ns)>=MIN_SOURCE_LITTORAL_1KM_CELLS:
            eligible[int(i)]=True
            nearby[int(i)]=allowed[np.asarray(ns,dtype=np.int32)]
    perbird=Counter(fixes[int(i)][0] for i in np.flatnonzero(eligible))
    admissible_birds={bird for bird,n in perbird.items()
                     if n>=MIN_ORIGINAL_BIRD_MONTH_SOURCE_FIXES}
    monthly={
        "2010_month":month,
        "original_gps_hourly_source_records":len(fixes),
        "original_genuine_birds_before_WMR_filter":observed[1],
        "original_gps_nearest_full_model_within_300m":int(within.sum()),
        "original_gps_used_native_model_code3_before_neighborhood":
            int(np.sum(within&(original_used_ecotope_codes==3))),
        "original_gps_used_native_model_code4_before_neighborhood":
            int(np.sum(within&(original_used_ecotope_codes==4))),
        "original_gps_outside_mid_high_WMR_mask_or_300m_geocoding":
            int(np.sum(~in_class)),
        "original_gps_used_on_mid_high_with_at_least20_nearby_mid_high_pixels":
            int(eligible.sum()),
        "original_birds_with_ge20_strict_intertidal_GPS_this_month":
            len(admissible_birds),
        "original_gps_after_bird_month20_and_WMR_neighborhood20":
            int(sum(perbird[b] for b in admissible_birds)),
        "JunJul_NIOZ_native_lat_unobserved_TEMPLATE_INFERRED":
            month in (6,7),
        "source_original_NIOZ_used_index_value_NOT_INSPECTED":True}
    return {
        "source_receipt":{
          "fixed_source_admission":SOURCE_ADMIT,
          "source_original_month":month,
          "all_original_model_static_and_WMR_geo_masks_verified":True},
        "fixes":fixes,
        "closest":close_idx,
        "circles":nearby,
        "valid":eligible,
        "valid_birds":admissible_birds,
        "model_expo":native_model["index"],
        "tree":native_model["tree"],
        "xy":xy,
        "source_qa":monthly}

def inspect_source_and_match_tide(preflights,tide):
    """Original bird/month/real RWS source only, model rank never inspected."""
    if sorted(preflights)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V85_HABITAT_SOURCE_FAVORABLE_MONTH_SET")
    paired,previous=tide_light_source_groups(
        preflights,tide,required_geo_status=SOURCE_ADMIT,
        required_months=SOURCE_MONTHS,height_bin=FIXED_TRUE_RWS_TIDAL_HEIGHT_BIN,
        shift_seconds=0)
    four,qa=fourway_source_only(paired,previous,verify_original_replay=False)
    return four,{
        "original_tide_astro_same_bird_month_height_strata":qa,
        "original_paired_real_phase_day_night_source":previous,
        "only_true_WMR_code3_4_observed_GPS_entered":True}

def shared_source_gates(sources,match):
    """No NIOZ model-used spatial ranks until both entire islands qualify."""
    if sorted(sources)!=["Ameland","Schier"] or sorted(match)!=["Ameland","Schier"]:
        raise ValueError("SOURCE_STOP_V85_NEED_TWO_ORIGINAL_SITES")
    supported=[]
    for m in SOURCE_MONTHS:
        if all(
            sources[s][m]["source_qa"]["original_birds_with_ge20_strict_intertidal_GPS_this_month"]>=
                SOURCE_MONTH_SOURCE_BIRDS_MIN and
            sources[s][m]["source_qa"]["original_gps_after_bird_month20_and_WMR_neighborhood20"]>=
                SOURCE_MONTH_SOURCE_FIXES_MIN
            for s in ("Schier","Ameland")):
            supported.append(m)
    site_source={}
    original_four_monthsets={}
    for site in ("Schier","Ameland"):
        four,meta=match[site]
        qa=meta["original_tide_astro_same_bird_month_height_strata"]
        original_four_monthsets[site]={key[1] for key in four}
        site_source[site]={
            "source_site":site,
            "source_fourway_status":qa["admission"],
            "source_fourway_groups":len(four),
            "actual_birds_in_full_fourway":qa.get(
                "original_birds_in_all_four_tide_and_light_conditions",0),
            "source_original_fixes_in_fourway":qa.get(
                "original_four_way_source_fix_count",0),
            "source_original_months_with_full4way":sorted(original_four_monthsets[site])}
    common_four=sorted(set(supported)&
        original_four_monthsets["Schier"]&
        original_four_monthsets["Ameland"])
    allowed=len(supported)>=SOURCE_COMMON_MONTH_MIN and len(common_four)>=SOURCE_COMMON_MONTH_MIN and all(
        site_source[s]["source_fourway_status"]==ADMIT
        for s in ("Schier","Ameland"))
    result={
        "all_2010_JuneDecember_original_months_audited_without_outcome_selection":True,
        "source_supported_shared_months_from_original_littoral_GPS_only":supported,
        "source_both_sites_fourway_months_shared":common_four,
        "original_sources_by_site":site_source,
        "all_fixed_original_source_gates_admitted_BEFORE_model_use_rank":
            bool(allowed),
        "source_gate_status":(
            "ADMITTED_V85_BOTH_ISLANDS_WMR_MIDHIGH_REAL_RWS_FOURWAY"
            if allowed else
            "NOT_ADMITTED_V85_BOTH_ISLANDS_MIDHIGH_GPS_TIDE_LIGHT_SUPPORT")}
    return result

def score_if_both_source_admitted(sources,match,gate,site_models):
    """Habitat restricted and all-cell SAME true bird GPS, no arbitrary rescue."""
    if not gate["all_fixed_original_source_gates_admitted_BEFORE_model_use_rank"]:
        return {"score":RESULT_STOP,"no_bird_model_index_values_read":True}
    restricted={}
    reference={}
    paired_restr={}
    for site in ("Schier","Ameland"):
        four,source=match[site]
        native_source=sources[site]
        chosen=source["original_tide_astro_same_bird_month_height_strata"]
        # Truly complete ecological source and 4-cell recorded groups first.
        restricted[site]=score_fourway_difference_in_differences(
            four,chosen,native_source)
        vals=_private_original_bird_means(four,native_source)
        # Same exact animal GPS original locations and source conditions,
        # but all pixels within 1km as additional source-matched reference.
        ref={}
        for month in SOURCE_MONTHS:
            m=native_source[month]
            indices=set()
            for (bird,mm,binid),phases in four.items():
                if mm!=month:continue
                for phase in (-1,1):
                    for light in ("DAY","NIGHT"):
                        indices.update(i for _,i in phases[phase][light])
            circles=[[] for _ in m["fixes"]]
            if indices:
                ordered=sorted(indices)
                new=m["tree"].query_ball_point(m["xy"][ordered],r=REFERENCE_RADIUS_M)
                for i,ns in zip(ordered,new):
                    if len(ns)<MIN_SOURCE_LITTORAL_1KM_CELLS:
                        raise ValueError("SOURCE_STOP_V85_SOURCE_GPS_ALLCELL_BACKGROUND_MISSING")
                    circles[i]=ns
            ref[month]={**m,"circles":circles}
        matched_all=_private_original_bird_means(four,ref)
        reference[site]=score_fourway_difference_in_differences(
            four,chosen,ref)
        if len(vals)!=len(matched_all):
            raise ValueError("ESTIMAND_STOP_V85_NOT_SAME_ORIGINAL_BIRD_SAMPLE")
        paired_restr[site]={
            "strict_minus_allcell_same_GPS_bird_cluster":
                original_one_site_rank_delta(vals-matched_all)}
    primary_s=_private_original_bird_means(match["Schier"][0],sources["Schier"])
    primary_a=_private_original_bird_means(match["Ameland"][0],sources["Ameland"])
    c=independent_bird_site_contrast(primary_s,primary_a)
    return {
        "source_gate":"ADMITTED_ONLY_ON_TRUE_WMR_3_4_TIDE_FLAT_GPS",
        "source_WMR_mid_high_restricted_model_midrank_site_results":restricted,
        "source_allcell_1km_rank_with_exact_same_tideflat_GPS_and_fourway_groups":
            reference,
        "within_site_same_true_birds_restricted_minus_allpixel_reference":
            paired_restr,
        "original_bird_site_CONTRAST_restricted_Schier_minus_Ameland":c,
        "not_original_v82_all_GPS_allcell_estimand":True,
        "WMR_2021_corrected_exact_version_NOT_VERIFIED":True,
        "no_real_feeding_or_measured_2010_exposed_area_inference":True}

def original_one_site_rank_delta(values,*,seed=20261108):
    """Bird-level signed contrast of NEW restricted vs same GPS all-cell D."""
    v=np.asarray(values,float)
    if not len(v) or not np.isfinite(v).all():
        raise ValueError("ESTIMAND_STOP_V85_NONFINITE_OR_NO_BIRDS")
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,len(v),size=(10000,len(v)))
    ci=np.quantile(v[idx].mean(axis=1),[.025,.975])
    return {
        "true_original_birds":int(len(v)),
        "original_independent_bird_equal_difference":float(v.mean()),
        "independent_original_bird_bootstrap_95":[float(ci[0]),float(ci[1])],
        "positive_bird_count":int(np.sum(v>0)),
        "original_individual_values_NOT_RELEASED":True}
