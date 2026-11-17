"""v178: genuine historical as-of DEM per REAL 2018/2019 oystercatcher GPS fix.

SCIENTIFIC SOURCE FIX after v177 STOP:
v177 validated all 10 native 2016-labelled z/isource grids but only 8,311
of 157,863 2018 true-previous-15min bird GPS bins, and 6,681 of 125,241
2019 bins, mapped to nonmissing native elevations (5.3%). The historical
Vaklodingen survey programme cycles every 3 or 6 years, and single-year
native z layers are spatially sparse.

Pre-fix now: For each actual original tagged-bird GPS matched to an ACC
15-minute observation, choose the MOST RECENT genuine source DEM z+isource
layer whose ORIGINAL NATIVE TIME LABEL is strictly earlier than January 1
of the bird observation calendar year, and no more than SIX calendar years
earlier (2018->2012..2017, 2019->2013..2018). No 2019 or 2025 source
future elevation for 2018/19 observations. In a missing year/layer/cell,
fall back to another actually observed OLD layer at that SAME native cell
within six years, NEVER a neighboring interpolated valid cell.

"Year on original time axis" may be an archival snapshot/nominal year
rather than a direct field survey date of every source pixel; isource is
an origin-file code not an independent GPS bird ID/survey timestamp.
Vertical datum NAP vs harbor RWS not yet independently reconciled.
Therefore output is SOURCE GEOGRAPHICAL COVERAGE only, no wet/dry state,
physical exposure effect, prey accessibility, or biological test/p-value.

The exact same authenticated Zenodo/RWS sources and native prior-bin
cohorts from v168 are required before data source admission. No raw bird
tags, individual geographic points/times, DEM arrays or tide levels exported.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,re
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from real_GPS_to_2016_DEM_source_gate import (
    assemble_source_gps,nearest_index,EXPECTED_PREVIOUS_BINS,EXPECTED_GPS_BIN_SOURCE,
    EXPECTED_GRID_SHAPE,EXPECTED_CRS,MAX_GEO_ABS_HEIGHT_M
)
from v168_true_year_transfer import (
    source_receipts_exact,source_input_and_replay,verified_2019_source,
    corrected_previous_bin
)

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v177/results/frozen_original_birdGPS_DEM_source_receipt_v177.json"
V173=ROOT/"validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json"
V175=ROOT/"validation_v175/results/original_ten_vlieland_survey_time_source_v175.json"
V176=ROOT/"validation_v176/results/true_vlie_2016_z_isource_valid_cell_support_v176.json"
FULL=ROOT/"validation_v179/results/real_native_origin_filename_provenance_v179.json"
RECEIPT=ROOT/"validation_v179/results/frozen_real_native_origin_filename_provenance_v179.json"

TARGET_YEARS=(2018,2019)
MAX_SOURCE_LABEL_AGE_YEARS=6
PUBLISHED_SURVEY_ROTATION=(3,6)
EXPECTED_V177_2016_MATCH={2018:8311,2019:6681}
EXPECTED_V179_MATCH={2018:149446,2019:119778}
EXPECTED_TILES=10
MIN_GPS_BINS_PER_YEAR=20000
MIN_BIRDS_PER_YEAR=10
MIN_MONTHS_PER_YEAR=3
EXPECTED_MONTHS=(6,7,8,9)
DATA_ROOT="https://opendap.deltares.nl/"
MAX_TILE_PIXELS=625*500
EXPECTED_NATIVE_DIMS=("time","y","x")

def native_time_label_allowed(original_label,observed_year):
    """No future data, and no source older than six CALENDAR years.

    A time LABEL is not a guarantee of original field collection date.
    """
    if not isinstance(original_label,str) or len(original_label)<10:
        return False
    try:
        date=datetime.strptime(original_label[:10],"%Y-%m-%d").date()
    except ValueError:
        return False
    return observed_year-MAX_SOURCE_LABEL_AGE_YEARS <= date.year < observed_year

def native_z_and_source_at_points(z,sources,yi,xi):
    """Finite non-fill z AND valid integer isource; legitimate z=0 is valid."""
    if z.shape!=EXPECTED_GRID_SHAPE or sources.shape!=z.shape:
        raise AssertionError("Genuine original native z/isource source grid shapes changed")
    zvalues=np.ma.asarray(z,dtype=float).filled(np.nan)[yi,xi]
    srcvalues=np.ma.asarray(sources,dtype=float).filled(np.nan)[yi,xi]
    valid=(np.isfinite(zvalues)&(np.abs(zvalues)<MAX_GEO_ABS_HEIGHT_M)&
           np.isfinite(srcvalues)&(srcvalues>=0)&(srcvalues<10000)&
           (np.abs(srcvalues-np.rint(srcvalues))<1e-5))
    return zvalues,srcvalues,valid

def verify_original_time_vector(values,expected_dates,original_source_SHA):
    original=np.ma.asarray(values,dtype=np.float64).filled(np.nan)
    if original.ndim!=1 or not np.isfinite(original).all() or len(original)!=len(expected_dates):
        raise AssertionError("Original provider time coordinate invalid")
    actual_SHA=hashlib.sha256(original.astype("<f8").tobytes()).hexdigest()
    if actual_SHA!=original_source_SHA:
        raise AssertionError("Original native time coordinates changed since v175 original-byte source audit")
    origin=datetime(1970,1,1,tzinfo=timezone.utc)
    observed=[(origin+timedelta(days=float(x))).strftime("%Y-%m-%d") for x in original]
    if observed!=expected_dates:
        raise AssertionError("Actual native time labels do not match original published v175 dates")
    return observed


def filename_upper_year(name):
    """Conservative upper year explicitly encoded in ORIGINAL source file name.

    Return None if no four-digit year can be recovered. Filename dates are
    provenance labels, NOT independently verified survey/measurement dates.
    Mixed date labels choose the newest to avoid future-source leakage.
    """
    if not isinstance(name,str) or not name:
        return None
    years=[]
    for m in re.finditer(r"(?<!\d)((?:19|20)\d{2}[01]\d[0-3]\d)(?!\d)",name):
        try:
            years.append(datetime.strptime(m.group(1),"%Y%m%d").year)
        except ValueError:
            pass
    years.extend(int(m.group(1)) for m in re.finditer(
        r"(?<!\d)((?:19|20)\d{2})(?!\d)",name))
    # Explicit abbreviated range e.g. 2015_16tmp means at least 2016,
    # NOT 2015; disallow 2016->20 being mistaken for 2020.
    for m in re.finditer(r"(?<!\d)((?:19|20)\d{2})[_-](\d{2})(?!\d)",name):
        first=int(m.group(1))
        second=(first//100)*100+int(m.group(2))
        if 0<=second-first<=2:
            years.append(second)
    return max(years) if years else None

def native_isource_flag_names(src):
    """Read provider-native CF flag_values/flag_meanings without guessing IDs."""
    try:
        codes=np.ma.asarray(getattr(src,"flag_values"),dtype=float).filled(np.nan)
        names=getattr(src,"flag_meanings")
        if isinstance(names,bytes):
            names=names.decode("utf-8")
        labels=str(names).split()
    except (AttributeError,ValueError,TypeError,UnicodeDecodeError):
        return {}
    if codes.ndim!=1 or len(codes)!=len(labels) or not len(codes):
        return {}
    if not np.isfinite(codes).all() or not np.allclose(codes,np.rint(codes)):
        return {}
    integral=[int(v) for v in codes]
    if len(integral)!=len(set(integral)):
        return {}
    return dict(zip(integral,labels))

def read_tile_asof(tile,dates,original_time_SHA,projected,obsyears,selected_time,selected_z,
                   source_harbor_era,sel_tile,origin_years,origin_flag_known):
    """Assign each original source point only first genuine valid past z.

    Original years traversed newest->oldest; a single GPS point cannot be
    filled by future source data and is not resampled to a different cell.
    """
    name=tile["source_tile_basename"]
    url=tile["source_original_native_tile_url"].replace("http://","https://",1)
    if not url.startswith(DATA_ROOT) or not url.endswith(".nc"):
        raise AssertionError("Untrusted original coastal source URL")
    source_before=int(np.count_nonzero(sel_tile>=0))
    perlayer=[]
    with Dataset(url,mode="r") as nc:
        for var in ("x","y","z","isource","time","crs"):
            if var not in nc.variables:
                raise AssertionError("Real original source tile missing "+var)
        xx=np.asarray(nc.variables["x"][:],dtype=float)
        yy=np.asarray(nc.variables["y"][:],dtype=float)
        verify_original_time_vector(
            nc.variables["time"][:],dates,original_time_SHA)
        z=nc.variables["z"]; src=nc.variables["isource"]
        native_source_file_map=native_isource_flag_names(src)
        if z.dimensions!=EXPECTED_NATIVE_DIMS or src.dimensions!=EXPECTED_NATIVE_DIMS or z.shape!=src.shape:
            raise AssertionError("Original chronological z/source time,y,x dimensions differ")
        if z.shape[1:]!=EXPECTED_GRID_SHAPE or np.prod(z.shape[1:])!=MAX_TILE_PIXELS:
            raise AssertionError("Original 20m native source grid dimensions differ")
        if z.shape[0]!=len(dates) or str(getattr(z,"units",""))!="m" or str(getattr(nc.variables["crs"],"EPSG_code",""))!=EXPECTED_CRS:
            raise AssertionError("Original source time length, m units or RD horizontal CRS changed")
        xt,inx=nearest_index(xx,projected[:,0])
        yt,iny=nearest_index(yy,projected[:,1])
        inside=inx&iny
        # Reject any same original GPS point that fell in another tile
        # as well: parent aggregate tracks and excludes ambiguities.
        label_rows=[
            (i,label) for i,label in enumerate(dates)
            if any(native_time_label_allowed(label,year) for year in TARGET_YEARS)
        ]
        label_rows.sort(key=lambda p:p[1],reverse=True)
        for ti,label in label_rows:
            yearlabel=int(label[:4])
            eligible_year=np.zeros(len(obsyears),dtype=bool)
            for target_year in TARGET_YEARS:
                if native_time_label_allowed(label,target_year):
                    eligible_year |= (obsyears==target_year)
            which=(inside&(sel_tile<0)&(selected_time<0)&eligible_year)
            n=int(np.count_nonzero(which))
            if not n:continue
            original_indices=np.flatnonzero(which)
            # Provider 2016-label layer among many others: load only
            # needed source time slice, not 1948..2025 archive.
            raw_z=z[ti,:,:]
            raw_src=src[ti,:,:]
            zh,sh,good=native_z_and_source_at_points(
                raw_z,raw_src,yt[original_indices],xt[original_indices])
            chosen=original_indices[good]
            if chosen.size:
                selected_time[chosen]=yearlabel
                selected_z[chosen]=zh[good]
                source_harbor_era[chosen]=sh[good]
                sel_tile[chosen]=int(tile["_source_tile_index"])
                original_names=[native_source_file_map.get(int(k)) for k in
                                np.rint(sh[good]).astype(np.int64)]
                origin_flag_known[chosen]=[v is not None for v in original_names]
                origin_years[chosen]=[
                    (year if (year:=filename_upper_year(v)) is not None else -1)
                    for v in original_names]
            perlayer.append({
                "original_native_time_label":label,
                "source_native_time_index":ti,
                "original_tagged_GPS_positions_candidate_before_this_layer":n,
                "original_native_valid_z_and_isource_locations_added":int(chosen.size),
            })
    return {
        "tile":name,
        "original_20m_native_RD_xy_bbox":tile["original_projected_xy_RD_NAP_search_bbox_m"],
        "original_valid_native_survey_time_labels_2012_2018":len(label_rows),
        "original_native_isource_CF_filename_flag_count":len(native_source_file_map),
        "original_gps_positions_inside_20m_cell_center_range":int(inside.sum()),
        "original_source_GPS_positions_first_admitted_in_this_tile":
             int(np.count_nonzero(sel_tile==int(tile["_source_tile_index"]))),
        "source_time_label_admitted_true_original_by_layer":perlayer,
        "original_DEM_native_values_not_distributed":True
    },inside

def run(v128,v129,v126gps,v126rws,v127):
    previous=json.loads(PRIOR.read_text())
    if (previous["all_predeclared_GPS_to_DEM_geographic_support_gates_pass"] is not False or
        previous["source_2018_2019_observed_GPS_native_grid_coverage_and_valid_cells"]["2018"]["GPS_with_unique_2016_label_valid_native_z_and_isource_cells"]!=EXPECTED_V177_2016_MATCH[2018] or
        previous["source_2018_2019_observed_GPS_native_grid_coverage_and_valid_cells"]["2019"]["GPS_with_unique_2016_label_valid_native_z_and_isource_cells"]!=EXPECTED_V177_2016_MATCH[2019]):
        raise AssertionError("Prior verified 2016-only source STOP not reproduced")
    v173=json.loads(V173.read_text())
    v175=json.loads(V175.read_text())
    v176=json.loads(V176.read_text())
    oldtime={x["tile"]:x for x in v175["all_ten_true_source_tile_time_or_explicit_STOP"]}
    oldz={x["tile"]:x for x in v176["all_ten_original_source_validity_or_STOP"]}
    originaltiles=v173["all_original_intersecting_native_tile_source_metadata"]
    if len(originaltiles)!=EXPECTED_TILES or set(oldtime)!=set(oldz) or set(oldtime)!={x["source_tile_basename"] for x in originaltiles}:
        raise AssertionError("Ten original 2016 geocorrect native tile identities changed")
    source_receipts_exact()
    original18,receipt18=source_input_and_replay(v128,v129)
    original19,receipt19=verified_2019_source(v126gps,v126rws,v127)
    if len(original18)!=EXPECTED_GPS_BIN_SOURCE[2018] or len(original19)!=EXPECTED_GPS_BIN_SOURCE[2019]:
        raise AssertionError("Original year 2018/19 source common animal quarterhours drifted")
    idx18,_,_=corrected_previous_bin(original18)
    idx19,_,_=corrected_previous_bin(original19)
    p18=assemble_source_gps(original18,idx18,2018,EXPECTED_PREVIOUS_BINS[2018])
    p19=assemble_source_gps(original19,idx19,2019,EXPECTED_PREVIOUS_BINS[2019])
    points=np.vstack((p18[0],p19[0]))
    months=np.concatenate((p18[1],p19[1]))
    birds=np.concatenate((p18[2],p19[2]))
    years=np.concatenate((
        np.full(len(p18[0]),2018,dtype=np.int16),
        np.full(len(p19[0]),2019,dtype=np.int16)))
    n=len(points)
    selected_year=np.full(n,-1,dtype=np.int16)
    selected_elev=np.full(n,np.nan,dtype=float)
    selected_isource=np.full(n,np.nan,dtype=float)
    selected_tile=np.full(n,-1,dtype=np.int16)
    origin_years=np.full(n,-1,dtype=np.int16)
    origin_flag_known=np.full(n,False,dtype=bool)
    geometric_coverage=np.zeros(n,dtype=np.int8)
    per_tile=[]
    for idx,tile in enumerate(sorted(originaltiles,key=lambda x:x["source_tile_basename"])):
        name=tile["source_tile_basename"]
        if oldtime[name]["status"]!="REAL_NATIVE_TIME_COORDINATES_VERIFIED" or oldz[name]["status"]!="REAL_2016_NATIVE_LAYER_HAS_NONFILL_Z_SUPPORT":
            raise AssertionError("Frozen original target tile absent or source date unreachable")
        if oldtime[name]["native_time_coordinate_labels_not_proven_field_days"].count("2016-01-01")!=1:
            raise AssertionError("Original v176 year-label source not unique")
        copy=dict(tile)
        copy["_source_tile_index"]=idx
        result,sourceinside=read_tile_asof(
            copy,oldtime[name]["native_time_coordinate_labels_not_proven_field_days"],
            oldtime[name]["true_time_coordinate_values_SHA256"],
            points,years,selected_year,selected_elev,selected_isource,selected_tile,
            origin_years,origin_flag_known)
        geometric_coverage+=sourceinside.astype(np.int8)
        per_tile.append(result)
        print("V179_TILE_SOURCE="+json.dumps({
            "tile":name,
            "source_geographic_orig_bird_bins":result["original_gps_positions_inside_20m_cell_center_range"],
            "admitted_by_valid_historic_snapshots":result["original_source_GPS_positions_first_admitted_in_this_tile"],
            "native_history_time_layers_considered":result["original_valid_native_survey_time_labels_2012_2018"]
        },sort_keys=True),flush=True)
    ambiguous=(geometric_coverage>1)
    selected=(selected_year>=0)&(selected_tile>=0)&(~ambiguous)
    years_d={}
    gates={}
    provenance_gates={}
    for yr in TARGET_YEARS:
        mask=(years==yr)
        valid=mask&selected
        nvalid=int(valid.sum())
        age=(yr-selected_year[valid]).astype(int)
        age_counts=dict(sorted((str(k),int(v)) for k,v in Counter(age).items()))
        latest_counts=dict(sorted((str(k),int(v)) for k,v in Counter(selected_year[valid]).items()))
        per_month={str(m):{
            "source_quarterhour_bins":int((mask&(months==m)).sum()),
            "source_original_with_valid_preobservation_6yr_native_z_isource":
                int((valid&(months==m)).sum())
            } for m in EXPECTED_MONTHS}
        years_d[str(yr)]={
            "original_source_true_previous_quarterhour_bins":int(mask.sum()),
            "source_within_one_or_more_historical_native_dem_tile_grid":
                int((mask&(geometric_coverage>=1)).sum()),
            "source_valid_latest_historical_z_isource_6year_preobservation":nvalid,
            "source_valid_historical_fraction":round(nvalid/int(mask.sum()),8),
            "source_not_in_any_original_native_tile":
                int((mask&(geometric_coverage==0)).sum()),
            "source_inside_original_tiles_but_NO_valid_prior_6year_native_z":
                int((mask&(geometric_coverage>=1)&(selected_year<0)).sum()),
            "source_ambiguous_geographical_multi_tile_points":
                int((mask&ambiguous).sum()),
            "n_distinct_original_tagged_birds_with_valid_historical_z":
                len(set(birds[valid].tolist())),
            "original_native_source_snapshot_label_year_counts_not_verified_survey_date":
                latest_counts,
            "original_native_label_age_years_counts_not_actual_field_data_age":
                age_counts,
            "source_valid_snapshot_within_3calendar_years":
                int((age<=3).sum()),
            "source_valid_snapshot_between_4_and_6calendar_years":
                int(((age>=4)&(age<=6)).sum()),
            "original_source_month_by_month_historical_z_support":per_month,
            "source_native_matched_historical_z_m_unverified_vertical_datum_median":
                round(float(np.median(selected_elev[valid])),5) if nvalid else None,
            "source_native_matched_historical_z_m_unverified_vertical_datum_quantiles05_95":
                [round(float(x),5) for x in np.quantile(selected_elev[valid],[.05,.95])] if nvalid else None,
            "source_empty_pixels_not_automatically_set_sea_or_forage_zero":True
        }
        d=years_d[str(yr)]
        if nvalid!=EXPECTED_V179_MATCH[yr]:
            raise AssertionError("Previously certified v178 true source matches changed")
        # Audit only the FIRST actual latest source selected at this cell.
        # Never search an older layer to rescue a future/unknown provenance.
        proper=valid&(origin_years>=1900)&(origin_years<yr)
        future=valid&(origin_years>=yr)
        unknown=valid&(origin_years<1900)
        if int(proper.sum()+future.sum()+unknown.sum())!=nvalid:
            raise AssertionError("Source-origin year categories do not partition v178")
        d["native_isource_filename_origin_preobservation_year"]=int(proper.sum())
        d["native_isource_filename_origin_observation_year_or_later_REJECTED"]=int(future.sum())
        d["native_isource_filename_origin_unknown_REJECTED"]=int(unknown.sum())
        d["original_CF_code_missing_for_valid_z"]=int((valid&(~origin_flag_known)).sum())
        d["native_isource_preobservation_filename_birds"]=len(set(birds[proper].tolist()))
        d["native_isource_preobservation_filename_months"]={
            str(m):int((proper&(months==m)).sum()) for m in EXPECTED_MONTHS}
        d["origin_provenance_is_filename_date_NOT_field_survey_day"]=True
        d["origin_audit_does_not_reselect_older_layers_on_failure"]=True
        provenance_gates[str(yr)]={
            "v178_replayed_original_valid_GPS_to_z_counts":nvalid==EXPECTED_V179_MATCH[yr],
            "origin_filename_preyear_GPS_20k_plus":int(proper.sum())>=MIN_GPS_BINS_PER_YEAR,
            "origin_filename_preyear_ten_birds_plus":d["native_isource_preobservation_filename_birds"]>=MIN_BIRDS_PER_YEAR,
            "origin_filename_preyear_three_months_plus":sum(v>0 for v in d["native_isource_preobservation_filename_months"].values())>=MIN_MONTHS_PER_YEAR,
            "no_ambiguous_multitile_source":d["source_ambiguous_geographical_multi_tile_points"]==0,
            "original_native_yearlabel_is_older_than_bird":bool(not nvalid or (selected_year[valid]<yr).all()),
        }
        gates[str(yr)]={
            "original_quarterhour_n_preserved":
                d["original_source_true_previous_quarterhour_bins"]==EXPECTED_PREVIOUS_BINS[yr],
            "source_real_historical_z_20k_plus":
                nvalid>=MIN_GPS_BINS_PER_YEAR,
            "source_ten_plus_bird_IDs_with_valid_z":
                d["n_distinct_original_tagged_birds_with_valid_historical_z"]>=MIN_BIRDS_PER_YEAR,
            "source_three_plus_source_months":
                sum(x["source_original_with_valid_preobservation_6yr_native_z_isource"]>0
                    for x in per_month.values())>=MIN_MONTHS_PER_YEAR,
            "no_native_tile_ambiguities":
                d["source_ambiguous_geographical_multi_tile_points"]==0,
            "all_nonmissing_source_labels_strictly_older_than_observation_year":
                bool(not nvalid or (selected_year[valid]<yr).all()),
            "all_source_native_label_years_within_max_six":
                bool(not nvalid or ((yr-selected_year[valid])<=MAX_SOURCE_LABEL_AGE_YEARS).all()),
        }
    return {
        "version":"v179_native_isource_original_origin_filename_year_vs_original_bird_GPS_1",
        "original_source_year2018_2019_genuine_Zenodo_and_RWS_MD5_SHA_replayed":True,
        "original_v177_source_only_STOP_preserved":True,
        "source_select_cell_history_rule":{
            "GPS_actual_location_crs":"Original WGS84 projected to EPSG:28992",
            "original_native_DEM_spatial_cell":"Nearest original 20m center within half-cell, no fill over missing z",
            "source_time":"Actual native original date LABEL earlier than January 1 of observation YEAR",
            "source_calendar_age_max":MAX_SOURCE_LABEL_AGE_YEARS,
            "source_accepted_calendar_years_2018":[2012,2013,2014,2015,2016,2017],
            "source_accepted_calendar_years_2019":[2013,2014,2015,2016,2017,2018],
            "most_recent_nonmissing_valid_z_and_isource_per_identical_cell":True,
            "later_label_than_bird_observation_year_never_retrojected":True,
            "full_native_source_time_label_may_be_composite_not_true_survey_day":True,
            "datum_NAP_vs_harbor_RWS": "UNVERIFIED",
            "actual_local_tide_height_not_measured":True,
        },
        "source_by_observation_year":years_d,
        "source_admission_gates_by_year":gates,
        "native_origin_provenance_filename_gates_by_year":provenance_gates,
        "all_origin_filename_preobservation_source_coverage_gates_PASS":all(all(z.values()) for z in provenance_gates.values()),
        "all_source_coverage_gates_PASS":all(all(q.values()) for q in gates.values()),
        "source_TEN_original_native_geographic_tile_history_counts":per_tile,
        "gps_individuals_UTC_raw_positions_and_native_z_2D_NOT_exported":True,
        "genuine_physical_exposed_mudflat_area_or_depth":"NOT_ESTIMATED",
        "animal_social_Boids_force":"NOT_IDENTIFIED",
        "global_tide_by_solar_biological_cause":"NOT_ESTIMATED",
        "origin_filename_year_is_not_verified_actual_survey_date":True,
        "local_harbor_vs_GPS_terrain_vertical_datum":"UNVERIFIED"
    }

def main():
    p=argparse.ArgumentParser()
    for name in ("v128","v129","v126-gps","v126-rws","v127"):
        p.add_argument("--"+name,required=True)
    args=p.add_mutually_exclusive_group(required=True)
    args.add_argument("--emit",action="store_true")
    args.add_argument("--check",action="store_true")
    x=p.parse_args()
    r=run(x.v128,x.v129,x.v126_gps,x.v126_rws,x.v127)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    if x.check:
        if not RECEIPT.exists():raise AssertionError("Original historical per-cell latest-source receipt absent")
        old=json.loads(RECEIPT.read_text())
        if old!=r:
            raise AssertionError("Genuine historical source latest-prior-year per-cell GPS counts changed")
        print("V179_GENUINE_ASOF6Y_DEM_CELL_SOURCE_AND_BIRDGPS_REPLAY_PASS")
    else:
        FULL.write_text(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
        print("V179_TRUE_HISTORICAL_SOURCE_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V179_TRUE_HISTORICAL_SOURCE_END")
    print("V179_SOURCE_SCOPE="+json.dumps({
        "gates":r["source_admission_gates_by_year"],
        "pass":r["all_source_coverage_gates_PASS"],
        "year":r["source_by_observation_year"],
    },sort_keys=True))
if __name__=="__main__":
    main()
