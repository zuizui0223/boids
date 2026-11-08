"""v85: original oystercatcher GPS mid/high WMR ecotope SOURCE SUPPORT only.

Uses genuine 2010 wild positions from 2 source-distinct Wadden islands
and independent published 2008–12 WMR mid3/high4 intertidal polygons.
Each original native model center can be classified by polygons, excluding
code2 low-littoral version-uncertain boundary. June/July NIOZ original
latitude is entirely MISSING and its original static numerical model grid
is explicitly inferred as in v80/v81, NEVER called original observation.
No original NIOZ used-location \`time_expo\` ranks or ecological effect scored.
"""
from __future__ import annotations

from collections import Counter,defaultdict
from datetime import timedelta
import json
import numpy as np
import shapely
from shapely import STRtree

from native_monthly_exposure_source import _haversine_m
from wild_2010_modelled_tidal_exposure_rank import _locxy
from wmr_original_complete_unfiltered_mid_high_source import (
    _original_full_site,PUBLISHER_FULL_WFS_UNFILTERED_MATCHED)
from wmr_original_midhigh_native_nioz_grid_source import (
    FIXED_SITE_BBOX)
from tide_solar_four_way_source_and_effect import (
    fourway_source_only)

MONTHS=(6,7,8,9,10,11,12)
CODE3_MID=3
CODE4_HIGH=4
ORIGINAL_V84C_NATIVE_SOURCE={
    "Schier":(4235,316),
    "Ameland":(3130,70)}
PUBLIC_WMR_SITE={
    "Schier":"Schiermonnikoog",
    "Ameland":"Ameland_Nes"}
ORIGINAL_GPS_SOURCE_MONTH_COUNTS={
    "Schier":{
        6:(8874,19),7:(12250,19),8:(11427,16),9:(9572,16),
        10:(9508,15),11:(7975,14),12:(6656,14)},
    "Ameland":{
        6:(6450,15),7:(5321,8),8:(5106,7),9:(4581,7),
        10:(3629,7),11:(3220,6),12:(3076,6)}}
NATIVE_TOTAL=486*820
SOURCE_MIN_GPS_PER_MONTH=200
SOURCE_MIN_BIRDS_PER_MONTH=5
SOURCE_MIN_BIRD_GPS_IN_MIDHIGH=20
GPS_NATIVE_MAX_M=300.
SOURCE_MIN_NATIVE_1KM_MIDHIGH_CELLS=20
GPS_NATIVE_SOURCE_MIN_FRACTION=.8
SOURCE_STATUS="SOURCE_ADMITTED_V85_WMR_MIDHIGH_GENUINE_BIRD_GPS_AND_NEARBY_SOURCE"

def static_WMR_grid_classification(site,native_lat,native_lon,*,get_polygons=_original_full_site):
    """Native SOURCE-only original WMR polygons, 2D code array; NO birds."""
    name=PUBLIC_WMR_SITE.get(site)
    if name is None:raise ValueError("SOURCE_STOP_V85_WRONG_WADDEN_SITE")
    bbox=FIXED_SITE_BBOX[name]
    polygons,report=get_polygons(name,bbox)
    if report["original_full_WFS_GetFeature_NO_CQL_source_count"]!=(
        PUBLISHER_FULL_WFS_UNFILTERED_MATCHED[name]):
        raise ValueError("SOURCE_STOP_V85_WMR_FULL_ORIGINAL_SOURCE_COUNTS_DRIFT")
    if len(native_lat)!=NATIVE_TOTAL or len(native_lon)!=NATIVE_TOTAL:
        raise ValueError("SOURCE_STOP_V85_NATIVE_2010_NIOZ_TEMPLATE_SIZE")
    nlat=np.asarray(native_lat,dtype=float)
    nlon=np.asarray(native_lon,dtype=float)
    in_box=(nlon>=bbox[0])&(nlon<=bbox[2])&(
        nlat>=bbox[1])&(nlat<=bbox[3])
    active=np.flatnonzero(in_box)
    px=shapely.points(_locxy(nlat[active],nlon[active]))
    tree=STRtree([x for x,code in polygons])
    pairs=tree.query(px,predicate="intersects")
    sub=np.zeros(len(active),dtype=np.uint8)
    ambiguous=np.zeros(len(active),dtype=bool)
    for point_idx,polygon_idx in zip(*pairs):
        code=polygons[int(polygon_idx)][1]
        if code not in (CODE3_MID,CODE4_HIGH):
            raise ValueError("SOURCE_STOP_V85_NATIVE_OUTSIDE_MID_HIGH_SOURCE")
        prior=int(sub[point_idx])
        if prior and prior!=code:ambiguous[point_idx]=True
        elif not prior:sub[point_idx]=code
    sub[ambiguous]=0
    full=np.zeros(NATIVE_TOTAL,dtype=np.uint8)
    full[active]=sub
    n3=int(np.sum(full==CODE3_MID))
    n4=int(np.sum(full==CODE4_HIGH))
    if (n3,n4)!=ORIGINAL_V84C_NATIVE_SOURCE[site]:
        raise ValueError("SOURCE_STOP_V85_V84C_ORIGINAL_MIDHIGH_PIXEL_COUNTS_DRIFT")
    return full,{
        "original_WMR_site":name,
        "original_WMR_all_features_certified":report[
            "original_full_WFS_GetFeature_NO_CQL_source_count"],
        "source_fixed_strict_mid_littoral_model_grid_cells":n3,
        "source_fixed_strict_high_littoral_model_grid_cells":n4,
        "native_reference_pixel_count_ALL_YEAR_ORIGINAL_MESH":NATIVE_TOTAL,
        "original_midhigh_ecotope_polygon_version_corrected_v2_UNVERIFIED":True,
        "original_native_low_littoral_code2_deliberately_excluded":True,
        "original_GPS_positions_or_used_model_index_not_inspected":True}

def source_month_bird_mid_high(site,month,source_fixes,model,native_codes):
    if site not in ORIGINAL_GPS_SOURCE_MONTH_COUNTS or month not in MONTHS:
        raise ValueError("SOURCE_STOP_V85_GPS_SITE_MONTH_NOT_FIXED")
    n=len(source_fixes)
    ids=len({r[0] for r in source_fixes})
    if (n,ids)!=ORIGINAL_GPS_SOURCE_MONTH_COUNTS[site][month]:
        raise ValueError("SOURCE_STOP_V85_PRIOR_ORIGINAL_GPS_MONTH_SOURCE_DRIFT")
    if (model["n_native"]!=NATIVE_TOTAL or
        not np.isin(native_codes,[0,3,4]).all()):
        raise ValueError("SOURCE_STOP_V85_ORIGINAL_MODEL_OR_CORRECTED_CODE_SOURCE_DRIFT")
    pts=_locxy([r[2] for r in source_fixes],[r[3] for r in source_fixes])
    distances,nearest=model["tree"].query(pts,k=1)
    mapped=distances<=GPS_NATIVE_MAX_M
    code=np.where(mapped,native_codes[nearest],0)
    source3=int(np.sum(code==CODE3_MID))
    source4=int(np.sum(code==CODE4_HIGH))
    chosen=np.flatnonzero((code==3)|(code==4))
    total_midhigh=len(chosen)
    if total_midhigh:
        around=model["tree"].query_ball_point(pts[chosen],r=1000.)
        usable_n=np.asarray([sum(native_codes[z]>0) for z in around],dtype=int)
        good=np.asarray(usable_n>=SOURCE_MIN_NATIVE_1KM_MIDHIGH_CELLS)
    else:
        around=[]
        good=np.zeros(0,dtype=bool)
    qualified_indices=[int(chosen[i]) for i in np.flatnonzero(good)]
    birds=Counter(source_fixes[i][0] for i in qualified_indices)
    eligible_birds={b for b,v in birds.items()
                    if v>=SOURCE_MIN_BIRD_GPS_IN_MIDHIGH}
    only_source=[source_fixes[i] for i in qualified_indices
                 if source_fixes[i][0] in eligible_birds]
    report={
        "original_Wadden_site":site,
        "original_2010_month":month,
        "original_hourly_GPS_all_prior_visible_location_sources":n,
        "original_actual_distinct_birds":ids,
        "original_GPS_geocoded_to_native_NIOZ_at_most_300m":int(mapped.sum()),
        "source_original_GPS_native_geocoding_fraction":float(np.mean(mapped)),
        "original_GPS_source_at_mid_littoral_model_cell3":source3,
        "original_GPS_source_at_high_littoral_model_cell4":source4,
        "original_GPS_source_at_mid_or_high_littoral_native_cell":total_midhigh,
        "source_GPS_mid_high_with_20plus_mid_high_native_cells_in_local_1km":
            len(qualified_indices),
        "source_original_true_birds_with_ge20_eligible_mid_high_GPS":len(eligible_birds),
        "source_mid_high_original_GPS_after_ge20_bird_gate":len(only_source),
        "JuneJuly_original_NIOZ_lat_MISSING_explicit_static_model_lat_INFERRED":
            month in (6,7),
        "no_bird_model_used_index_read_for_source_eligibility":True}
    eligible=(mapped.mean()>=GPS_NATIVE_SOURCE_MIN_FRACTION and
        len(qualified_indices)>=SOURCE_MIN_GPS_PER_MONTH and
        len(eligible_birds)>=SOURCE_MIN_BIRDS_PER_MONTH and
        len(only_source)>=SOURCE_MIN_GPS_PER_MONTH)
    report["source_month_admission"]=(
        SOURCE_STATUS if eligible else
        "NOT_ADMITTED_V85_GENUINE_GPS_MIDHIGH_SOURCE_MONTH")
    # Private original GPS stays in RAM only, never exported.
    return only_source,report

def source_only_tide_fourcell(site,geo_source,tide):
    """Call genuine RWS physical phase and astronomy; no used NIOZ model index."""
    from matched_tide_state_day_night_native_ranks import tide_light_source_groups
    if sorted(geo_source)!=list(MONTHS):
        raise ValueError("SOURCE_STOP_V85_BIRD_MONTHS_NOT_ALL_SEVEN")
    for m in MONTHS:
        if geo_source[m]["source_receipt"]["fixed_source_admission"]!=SOURCE_STATUS:
            return {},{"admission":"NOT_ADMITTED_V85_MID_HIGH_MONTH_SOURCE"}
    paired,qa=tide_light_source_groups(
        geo_source,tide,
        required_geo_status=SOURCE_STATUS,
        required_months=MONTHS,
        height_bin=.2,shift_seconds=0)
    four,source=fourway_source_only(paired,qa,verify_original_replay=False)
    return four,{
        "source_previous_tide_daynight_real_RWS":qa,
        "all_four_TRUE_tide_phase_by_solar_source_groups":source,
        "original_model_used_at_GPS_numeric_INDEX_UNREAD":True}
