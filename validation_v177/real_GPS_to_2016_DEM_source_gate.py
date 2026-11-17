"""v177: REAL source-only 2018/19 O_VLIELAND GPS -> original 2016-labelled RWS DEM pixel match.

Original native GPS/ACC and RWS are re-fetched with publisher MD5/response
SHA using v128/129/126/127 -> v168 proven cohort: 2018 157,863 and
2019 125,241 true previous-quarterhour bird source records. The original
2016-labelled z/isource grids are sourced from 10 official Deltares native
20m historical Vaklodingen tiles, their time index and source quality frozen
in v175/v176. We compute source-eligible overlap, WITHOUT exposing
individual GPS, ACC event times or grid pixel values in GitHub.

"2016 time layer with z + isource non-fill" is NOT proof each pixel was
field measured during 2016, nor proof its vertical datum is calibrated NAP.
The RWS Vlieland Haven measured tide is a harbour gauge, not the animal's
local water level. Therefore this is a GEOGRAPHIC SOURCE GATE only; no
per-bird wet/dry state, habitat accessibility, ecology score, tidal causal
effect or Reynolds Boids interaction is estimated.

The 2018/2019 coordinates are the actual same-bird GPS fix matched to
earliest classified ACC event within an original 15min window, not every
GPS location at all times; sub-cells and source-missing locations stay
missing, never receive zero-height or interpolated fabricated terrain.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,time
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
for d in ("validation_v125","validation_v126","validation_v127","validation_v128",
          "validation_v129","validation_v130","validation_v165","validation_v166",
          "validation_v167","validation_v168"):
    sys.path.insert(0,str(ROOT/d))
from v168_true_year_transfer import (
    source_receipts_exact,source_input_and_replay,verified_2019_source,corrected_previous_bin
)

V173=ROOT/"validation_v173/results/genuine_vlieland_historical_tiles_shortlist_v173.json"
V174=ROOT/"validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
V175=ROOT/"validation_v175/results/original_ten_vlieland_survey_time_source_v175.json"
V176=ROOT/"validation_v176/results/true_vlie_2016_z_isource_valid_cell_support_v176.json"
V168=ROOT/"validation_v168/results/frozen_true_year_transfer_receipt_v168.json"
RESULT=ROOT/"validation_v177/results/original_birdGPS_2016_dem_source_overlap_v177.json"
RECEIPT=ROOT/"validation_v177/results/frozen_original_birdGPS_DEM_source_receipt_v177.json"
TARGET_SOURCE_YEAR=2016
EXPECTED_N_TILES=10
EXPECTED_COVERED_CELLS=1_881_902
EXPECTED_PREVIOUS_BINS={2018:157_863,2019:125_241}
EXPECTED_GPS_BIN_SOURCE={2018:193_088,2019:155_387}
EXPECTED_MONTHS=(6,7,8,9)
MIN_SOURCE_BINS_FOR_ADMISSION={2018:20_000,2019:20_000}
MIN_SOURCE_BIRDS_FOR_ADMISSION=10
MIN_VALID_MONTHS_PER_YEAR=3
MAX_ALLOWED_GRID_GAP_M=10.00001
MAX_GEO_ABS_HEIGHT_M=1000
RAW_TILE_DOMAIN="https://opendap.deltares.nl/"
EXPECTED_CRS="EPSG:28992"
EXPECTED_GRID_SHAPE=(625,500)
TARGET_YEAR_LABEL="2016-01-01"
SOURCE_PIXEL_SPACING_M=20.0

def nearest_index(grid,query):
    """Original 20m grid CENTER matching, no fill or multi-cell interpolation."""
    coord=np.asarray(grid,dtype=float)
    q=np.asarray(query,dtype=float)
    if coord.ndim!=1 or coord.size<2 or not np.isfinite(coord).all():
        raise AssertionError("Real native DEM x/y axis malformed")
    step=float(coord[1]-coord[0])
    if not np.isfinite(step) or abs(abs(step)-SOURCE_PIXEL_SPACING_M)>1e-4:
        raise AssertionError("Original 20m native pixel spacing changed")
    if not np.allclose(np.diff(coord),step,rtol=0,atol=1e-5):
        raise AssertionError("Real original x/y must be an unwarped monotonic 20m grid")
    good=np.isfinite(q)
    raw=np.zeros(q.shape,dtype=np.int64)
    raw[good]=np.rint((q[good]-coord[0])/step).astype(np.int64)
    raw_clipped=np.clip(raw,0,len(coord)-1)
    valid=(good & (raw>=0)&(raw<len(coord)) &
           (np.abs(q-coord[raw_clipped])<=MAX_ALLOWED_GRID_GAP_M))
    return raw_clipped,valid

def source_frame_metadata(src_v175,src_v176):
    if src_v175["status"]!="REAL_NATIVE_TIME_COORDINATES_VERIFIED":
        raise AssertionError("Original native 2016 source timestamp never verified")
    if src_v176["status"]!="REAL_2016_NATIVE_LAYER_HAS_NONFILL_Z_SUPPORT":
        raise AssertionError("Original 2016 native z source support never verified")
    idx=src_v175["original_indices_for_2016_native_time_label"]
    if len(idx)!=1 or src_v175["native_time_coordinate_labels_not_proven_field_days"][idx[0]]!=TARGET_YEAR_LABEL:
        raise AssertionError("Original source year 2016 index mismatch")
    if idx[0]!=src_v176["original_2016_native_TIME_index"]:
        raise AssertionError("Original 2016 source year z/isource time index mismatch")
    if src_v176["native_2016_grid_shape_y_x"]!=list(EXPECTED_GRID_SHAPE):
        raise AssertionError("Original source original 2016 grid dimensions changed")
    return idx[0]

def query_2016_grid(tile,source_time,source_z,projected):
    """Source original 2016 z and isource matched to actual projected GPS.

    Returns source QC masks and raw matched z only transiently in process RAM.
    """
    index=source_frame_metadata(source_time,source_z)
    name=tile["source_tile_basename"]
    if name!=source_time["tile"] or name!=source_z["tile"]:
        raise AssertionError("Original 2016 coastal tile identity differs across frozen references")
    url=tile["source_original_native_tile_url"].replace("http://","https://",1)
    if not url.startswith(RAW_TILE_DOMAIN) or not url.endswith(".nc"):
        raise AssertionError("Source original provider tile URL not trusted")
    with Dataset(url,mode="r") as nc:
        for field in ("x","y","time","z","isource","crs"):
            if field not in nc.variables:
                raise AssertionError("Original tile source no longer contains "+field)
        xx=np.asarray(nc.variables["x"][:],dtype=float)
        yy=np.asarray(nc.variables["y"][:],dtype=float)
        zvar=nc.variables["z"]; svar=nc.variables["isource"]
        if zvar.dimensions!=("time","y","x") or svar.dimensions!=zvar.dimensions:
            raise AssertionError("Source original z/isource native grid dimensions drift")
        if zvar.shape[1:]!=EXPECTED_GRID_SHAPE or index>=zvar.shape[0]:
            raise AssertionError("Original source time slice invalid")
        if str(getattr(zvar,"units",""))!="m" or str(getattr(nc.variables["crs"],"EPSG_code",""))!=EXPECTED_CRS:
            raise AssertionError("Original provider tile source z units / horizontal coordinate system drift")
        # Remote read SINGLE 2016 snapshot per candidate; no future-year
        # or current 2025 topography allowed.
        z=np.ma.asarray(zvar[index,:,:],dtype=float).filled(np.nan)
        isrc=np.ma.asarray(svar[index,:,:],dtype=float).filled(np.nan)
    finite_z=np.isfinite(z)&(np.abs(z)<MAX_GEO_ABS_HEIGHT_M)
    finite_source=(np.isfinite(isrc)&(isrc>=0)&(isrc<10000)&
                   (np.abs(isrc-np.rint(isrc))<1e-5))
    if int(finite_z.sum())!=source_z["native_2016_time_label_z_nonfill_finite_cells"] or (
        int((finite_z&finite_source).sum())!=source_z["native_2016_valid_z_AND_source_code_cells"]
    ):
        raise AssertionError("Re-fetched native 2016 DEM z/isource nonfill pixels differ from v176")
    nx,okx=nearest_index(xx,projected[:,0])
    ny,oky=nearest_index(yy,projected[:,1])
    oncenter=okx & oky
    selected_z=z[ny,nx]
    selected_source=isrc[ny,nx]
    actual_z=oncenter & np.isfinite(selected_z) & (np.abs(selected_z)<MAX_GEO_ABS_HEIGHT_M)
    actual=actual_z & np.isfinite(selected_source)&(selected_source>=0)&(selected_source<10000)&(
        np.abs(selected_source-np.rint(selected_source))<1e-5)
    return {
        "grid_center_covered":oncenter,
        "valid_2016_layer_source_z":actual_z,
        "valid_2016_layer_source_z_and_isource":actual,
        "matched_z_source_only":np.where(actual,selected_z,np.nan),
        "matched_source_code_source_only":np.where(actual,selected_source,np.nan),
        "tile_source_original_grid_n_valid":int(finite_z.sum()),
        "tile_original_2016_source_index":index,
        "tile_native_x_y_original_minmax":[
            round(float(xx.min()),3),round(float(yy.min()),3),
            round(float(xx.max()),3),round(float(yy.max()),3)]
    }

def assemble_source_gps(common,idx,year,expected_n):
    if len(idx)!=expected_n:
        raise AssertionError("v168 original eligible previous 15min GPS/ACC count changed")
    rows=[common[int(i)][0] for i in idx]
    if any(e["source_utc_event"].year!=year or e["source_month"] not in EXPECTED_MONTHS for e in rows):
        raise AssertionError("2018 or 2019 original source event year and four months changed")
    ll=np.asarray([(float(e["source_lon"]),float(e["source_lat"])) for e in rows],dtype=float)
    if ll.shape!=(expected_n,2) or not np.isfinite(ll).all():
        raise AssertionError("Original GPS sources malformed")
    tr=Transformer.from_crs("EPSG:4326",EXPECTED_CRS,always_xy=True)
    xs,ys=tr.transform(ll[:,0],ll[:,1])
    projected=np.column_stack((xs,ys))
    if not np.isfinite(projected).all():
        raise AssertionError("Original real bird GPS cannot be projected into RD New")
    month=np.asarray([e["source_month"] for e in rows],dtype=np.int8)
    isbird=np.asarray([hashlib.sha256(str(e["private_bird"]).encode()).digest()[:8] for e in rows],dtype="|S8")
    # SHA-based transient anonymization only for counting different birds;
    # nothing per-bird exported to GitHub, including hashes.
    return projected,month,isbird

def run(v128,v129,v126gps,v126rws,v127):
    old=json.loads(V168.read_text())
    if (old["source_opportunity"]["genuine_train_2018_prev15_state_windows"]!=EXPECTED_PREVIOUS_BINS[2018] or
        old["source_opportunity"]["genuine_full_2019_test_prev15_state_windows"]!=EXPECTED_PREVIOUS_BINS[2019]):
        raise AssertionError("Original v168 2018/2019 real source denominators drift")
    prior173=json.loads(V173.read_text())
    prior175=json.loads(V175.read_text())
    prior176=json.loads(V176.read_text())
    tiles=prior173["all_original_intersecting_native_tile_source_metadata"]
    ttimes={r["tile"]:r for r in prior175["all_ten_true_source_tile_time_or_explicit_STOP"]}
    tgrid={r["tile"]:r for r in prior176["all_ten_original_source_validity_or_STOP"]}
    if (len(tiles)!=EXPECTED_N_TILES or len(ttimes)!=EXPECTED_N_TILES or len(tgrid)!=EXPECTED_N_TILES or
        sum(x["native_2016_time_label_z_nonfill_finite_cells"] for x in tgrid.values())!=EXPECTED_COVERED_CELLS):
        raise AssertionError("Official ten historical native DEM source cells changed")
    # These original methods verify publisher source MD5 and official RWS
    # provider response SHA before exposing ephemeral GPS source coordinates.
    source_receipts_exact()
    c18,check18=source_input_and_replay(v128,v129)
    c19,check19=verified_2019_source(v126gps,v126rws,v127)
    if len(c18)!=EXPECTED_GPS_BIN_SOURCE[2018] or len(c19)!=EXPECTED_GPS_BIN_SOURCE[2019]:
        raise AssertionError("Original full 2018/2019 bird×ACC source windows drift")
    i18,_,_=corrected_previous_bin(c18)
    i19,_,_=corrected_previous_bin(c19)
    d18=assemble_source_gps(c18,i18,2018,EXPECTED_PREVIOUS_BINS[2018])
    d19=assemble_source_gps(c19,i19,2019,EXPECTED_PREVIOUS_BINS[2019])
    coords=np.vstack((d18[0],d19[0]))
    months=np.concatenate((d18[1],d19[1]))
    birds=np.concatenate((d18[2],d19[2]))
    years=np.concatenate((
        np.full(len(d18[0]),2018,dtype=np.int16),
        np.full(len(d19[0]),2019,dtype=np.int16)))
    n=len(coords)
    sourcecoverage=np.zeros(n,dtype=np.int8)
    validcoverage=np.zeros(n,dtype=np.int8)
    z_values=np.full(n,np.nan,dtype=float)
    src_values=np.full(n,np.nan,dtype=float)
    tileindex=np.full(n,-1,dtype=np.int8)
    row_qc=[]
    for j,t in enumerate(sorted(tiles,key=lambda x:x["source_tile_basename"])):
        name=t["source_tile_basename"]
        matched=query_2016_grid(t,ttimes[name],tgrid[name],coords)
        sourcecoverage+=matched["grid_center_covered"].astype(np.int8)
        validcoverage+=matched["valid_2016_layer_source_z_and_isource"].astype(np.int8)
        new_mask=matched["valid_2016_layer_source_z_and_isource"] & (validcoverage==1)
        z_values[new_mask]=matched["matched_z_source_only"][new_mask]
        src_values[new_mask]=matched["matched_source_code_source_only"][new_mask]
        tileindex[new_mask]=j
        per_yr={}
        for year in (2018,2019):
            mask=(years==year)
            per_yr[str(year)]={
                "original_bins_whose_location_is_within_half_pixel_native_grid":
                    int(np.count_nonzero(matched["grid_center_covered"]&mask)),
                "original_bins_at_valid_z_and_isource_2016_label":
                    int(np.count_nonzero(matched["valid_2016_layer_source_z_and_isource"]&mask)),
            }
        row_qc.append({
            "tile":name,
            "source_original_2016_valid_z_pixels_already_cryptographically_verified_v176":
                matched["tile_source_original_grid_n_valid"],
            "source_native_2016_time_index":matched["tile_original_2016_source_index"],
            "source_original_xy_bounds_RD_m":matched["tile_native_x_y_original_minmax"],
            "original_tagged_GPS_source_overlap_by_year":per_yr,
            "absolute_bird_GPS_and_2016_raster_pixels_not_exported":True,
        })
    if np.any(sourcecoverage>1) or np.any(validcoverage>1):
        # Do not randomly choose one of several overlapping source native
        # raster cells. Mark ambiguous source, not ecology.
        amb=int(np.count_nonzero(sourcecoverage>1))
        multivalid=int(np.count_nonzero(validcoverage>1))
    else:amb=multivalid=0
    eligible=(validcoverage==1)&(sourcecoverage==1)
    usable_z=np.where(eligible,z_values,np.nan)
    source_status={}
    for year in (2018,2019):
        mask=years==year
        finite=eligible&mask
        valid_n=int(np.count_nonzero(finite))
        source_n=int(np.count_nonzero(mask))
        valid_months={str(m):{
            "original_source_GPS_quarterhours":int(np.count_nonzero(mask&(months==m))),
            "original_source_quarterhours_valid_native_2016_z_isource":
                int(np.count_nonzero(finite&(months==m)))
        } for m in EXPECTED_MONTHS}
        source_status[str(year)]={
            "original_true_prev15_qualified_GPS_ACC_quarterhour_bins":source_n,
            "GPS_in_any_2016_label_native_grid_halfpixel_coverage":
                int(np.count_nonzero((sourcecoverage>=1)&mask)),
            "GPS_with_unique_2016_label_valid_native_z_and_isource_cells":valid_n,
            "source_source_z_link_fraction":round(valid_n/source_n,8),
            "source_GPS_outside_all_10_original_native_20m_grid_tiles":
                int(np.count_nonzero((sourcecoverage==0)&mask)),
            "source_GPS_in_tile_but_2016_layer_z_is_missing":
                int(np.count_nonzero((sourcecoverage>=1)&(validcoverage==0)&mask)),
            "source_GPS_ambiguous_multiple_tile_grid_pixels":
                int(np.count_nonzero((sourcecoverage>1)&mask)),
            "source_original_quarterhours_by_month":valid_months,
            "n_unique_tagged_birds_at_valid_native_source_z":
                int(len(set(birds[finite].tolist()))),
            "source_original_z_m_unverified_vertical_datum_median":
                round(float(np.nanmedian(usable_z[finite])),5) if valid_n else None,
            "source_original_z_m_unverified_vertical_datum_05_95":[
                round(float(z),5) for z in np.nanquantile(usable_z[finite],[.05,.95])
            ] if valid_n else None,
            "no_source_bird_ID_GPS_lonlat_or_perpoint_z_published":True,
        }
    pass_gates={}
    for year in (2018,2019):
        d=source_status[str(year)]
        pass_gates[str(year)]={
            "original_quarterhour_count_match_v168":d["original_true_prev15_qualified_GPS_ACC_quarterhour_bins"]==EXPECTED_PREVIOUS_BINS[year],
            "valid_original_historical_z_20k_bird_quarterhours":
                d["GPS_with_unique_2016_label_valid_native_z_and_isource_cells"]>=MIN_SOURCE_BINS_FOR_ADMISSION[year],
            "at_least_ten_distinct_tagged_birds_with_valid_source_z":
                d["n_unique_tagged_birds_at_valid_native_source_z"]>=MIN_SOURCE_BIRDS_FOR_ADMISSION,
            "at_least_three_months_with_source_valid_historical_z":sum(
                d["source_original_quarterhours_by_month"][str(m)]["original_source_quarterhours_valid_native_2016_z_isource"]>0
                for m in EXPECTED_MONTHS)>=MIN_VALID_MONTHS_PER_YEAR,
            "no_ambiguous_native_source_tile_assignments":
                d["source_GPS_ambiguous_multiple_tile_grid_pixels"]==0,
        }
    result={
        "version":"v177_real_Vlieland_2018_2019_birdGPS_to_2016label_DEM_geographic_source_gate_1",
        "original_source_2018_and_2019_genuine_Zenodo_RWS_MD5_SHA_replayed":True,
        "original_source_v168_first_run_full_SHA256":old["first_full_original_source_model_SHA256"],
        "original_native_2016_layer_data_from_frozen_v176":True,
        "original_source_n_2016label_valid_native_z_pixels_off_bird_sample":EXPECTED_COVERED_CELLS,
        "source_2018_2019_observed_GPS_native_grid_coverage_and_valid_cells":source_status,
        "source_all_10_tile_original_GPS_overlap_by_year":row_qc,
        "real_original_2016_source_admission_by_year":pass_gates,
        "all_predeclared_GPS_to_DEM_geographic_support_gates_pass":
            all(all(q.values()) for q in pass_gates.values()),
        "original_2016_time_label_may_be_annual_source_mosaic":"UNRESOLVED",
        "original_DEM_vertical_NAP_equal_harbor_RWS_NAP":"NOT_VERIFIED",
        "original_local_tidal_phase_diff_from_harbor":"NOT_CALIBRATED",
        "original_intertidal_exposure_or_behavior_ecological_effect":"NOT_ESTIMATED",
        "individual_bird_ID_XY_timestamps_and_remote_grid_pixels_not_distributed":True,
        "global_tide_solar_and_interbird_Reynolds_effects":"NOT_IDENTIFIED",
    }
    return result

def main():
    p=argparse.ArgumentParser()
    for name in ("v128","v129","v126-gps","v126-rws","v127"):
        p.add_argument("--"+name,required=True)
    args=p.add_mutually_exclusive_group(required=True)
    args.add_argument("--emit",action="store_true")
    args.add_argument("--check",action="store_true")
    x=p.parse_args()
    r=run(x.v128,x.v129,x.v126_gps,x.v126_rws,x.v127)
    RESULT.parent.mkdir(parents=True,exist_ok=True)
    if x.check:
        if not RECEIPT.exists():raise AssertionError("Missing source-verified first geographic GHA receipt")
        old=json.loads(RECEIPT.read_text())
        if r!=old:
            raise AssertionError("Original true tagged GPS/native 2016 survey cell geographical source differs")
        print("V177_ORIGINAL_REAL_GPS_2016_LAYER_Z_SOURCE_GEO_REPLAY_PASS")
    else:
        RESULT.write_text(json.dumps(r,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("V177_ORIGINAL_GPS_GEO_SOURCE_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V177_ORIGINAL_GPS_GEO_SOURCE_END")
    print("V177_SOURCE_MAIN="+json.dumps({
        "gates":r["real_original_2016_source_admission_by_year"],
        "all_pass":r["all_predeclared_GPS_to_DEM_geographic_support_gates_pass"],
        "years":r["source_2018_2019_observed_GPS_native_grid_coverage_and_valid_cells"]
    },sort_keys=True))
if __name__=="__main__":main()
