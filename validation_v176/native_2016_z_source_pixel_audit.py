"""v176 genuine original 2016-labeled Vlieland elevation-cell/source-mask audit.

After v173 official 165-tile spatial shortlist, v174 true remote DDS/DAS,
v175 actual 2016 native TIME label (annual 2016-01-01) in all 10 tiles,
read each tile's single original 2016 layer z(time,y,x) and matching
isource(time,y,x) to assess ORIGINAL valid bathymetric observation support.

The native TIME label may be a YEAR marker rather than literal field date;
a valid raster cell in layer 2016 is not yet the bird's actual GPS
position/habitat and isource code is source-file index, NOT a per-cell
measured timestamp or tagged bird identity.

DO NOT estimate dry mudflat access, animal GPS-specific z, local water
depth, tidal-solar interaction or Boids forces. Original full z/isource
arrays stay in ephemeral GitHub Action RAM, NEVER committed or uploaded.
"""
from __future__ import annotations
import argparse,hashlib,json,math,time
from collections import Counter
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v175/results/original_ten_vlieland_survey_time_source_v175.json"
DDS=ROOT/"validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
OUT=ROOT/"validation_v176/results/true_vlie_2016_z_isource_valid_cell_support_v176.json"
EXPECTED_TILES=10
TARGET_YEAR="2016"
TARGET_TIME_LABEL="2016-01-01"
MIN_VALID_CELLS_FOR_TILE=1000
MAX_TILE_CELLS=800000
MAX_RETRIEVAL_ATTEMPTS=2
GEO_Z_FINITE_MAGNITUDE_BOUND=1000.0
NATIVE_DDS_DOMAIN="https://opendap.deltares.nl/"
EXPECTED_CRS="EPSG:28992"
EXPECTED_DIMS=("time","y","x")

def finite_valid_z(masked):
    """Validate native z with _FillValue mask, never assume missing is z=0."""
    m=np.ma.asarray(masked,dtype=np.float64)
    z=m.filled(np.nan)
    good=np.isfinite(z)&(np.abs(z)<GEO_Z_FINITE_MAGNITUDE_BOUND)
    return z,good

def source_counts(z_raw,source_raw):
    z,good=finite_valid_z(z_raw)
    src=np.ma.asarray(source_raw,dtype=np.float64).filled(np.nan)
    if z.ndim!=2 or src.shape!=z.shape:
        raise AssertionError("Original 2016 z/isource must be aligned 2D native pixels")
    validSrc=np.isfinite(src)&(src>=0)&(src<10000)&(np.abs(src-np.rint(src))<1e-5)
    n=int(z.size)
    nz=int(np.count_nonzero(good))
    ns=int(np.count_nonzero(validSrc))
    both=good&validSrc
    nboth=int(np.count_nonzero(both))
    stats={
        "original_native_grid_cells_total":n,
        "native_2016_time_label_z_nonfill_finite_cells":nz,
        "native_2016_time_label_z_valid_fraction":round(nz/n,8),
        "native_isource_source_index_cells_numeric_valid":ns,
        "native_2016_valid_z_AND_source_code_cells":nboth,
        "native_2016_z_without_valid_source_index":int(np.count_nonzero(good&(~validSrc))),
        "native_source_index_without_valid_2016_z":int(np.count_nonzero(validSrc&(~good))),
        "native_2016_z_validity_not_inferred_as_bird_foraging_habitat":True,
    }
    if nz:
        data=z[good]
        stats["nonfill_z_m_original_native_min"]=round(float(np.min(data)),5)
        stats["nonfill_z_m_original_native_max"]=round(float(np.max(data)),5)
        stats["nonfill_z_m_original_native_quantiles_05_50_95"]=[
            round(float(v),5) for v in np.quantile(data,[.05,.50,.95])]
        stats["native_z_relative_zero_or_greater_cells"]=int(np.count_nonzero(data>=0))
    if nboth:
        rawcodes=src[both]
        codes=Counter(int(v) for v in rawcodes)
        stats["source_file_index_counts_in_valid_z"]={
            str(k):int(v) for k,v in sorted(codes.items())}
        stats["original_isource_code_does_NOT_directly_prove_year_or_bird_identity"]=True
    return stats

def check_original_tile(t,dds):
    tile=t["tile"]
    if not tile.startswith("vaklodingenKB") or not tile.endswith(".nc"):
        raise AssertionError("Unknown candidate original coastal DEM tile")
    old=dds[tile]
    if old["dds"]["status"]!="AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA":
        raise AssertionError("Original provider tile native DDS has not been admitted")
    if t["status"]!="REAL_NATIVE_TIME_COORDINATES_VERIFIED":
        return {"tile":tile,"status":"SOURCE_STOP_NO_NATIVE_SURVEY_TIME"}
    if t["native_time_coordinate_labels_not_proven_field_days"].count(TARGET_TIME_LABEL)!=1:
        return {"tile":tile,"status":"SOURCE_STOP_NO_UNIQUE_NATIVE_2016_TIME_LABEL"}
    idx=t["native_time_coordinate_labels_not_proven_field_days"].index(TARGET_TIME_LABEL)
    prior_indices=t["original_indices_for_2016_native_time_label"]
    if prior_indices!=[idx]:
        raise AssertionError("Frozen exact native year/time index changed")
    url=old["dds"]["original_provider_provenance"]["source_uri_requested"]
    if not url.startswith(NATIVE_DDS_DOMAIN) or not url.endswith(".nc.dds"):
        raise AssertionError("Original native tile URL not authenticated to Deltares")
    sourceurl=url[:-4]
    last_error=None
    for attempt in range(MAX_RETRIEVAL_ATTEMPTS):
        try:
            with Dataset(sourceurl,mode="r") as nc:
                for name in ("z","isource","time","x","y","crs"):
                    if name not in nc.variables:
                        raise AssertionError("Real native time grid variable missing: "+name)
                z=nc.variables["z"];src=nc.variables["isource"]
                if z.dimensions!=EXPECTED_DIMS or src.dimensions!=EXPECTED_DIMS or z.shape!=src.shape:
                    raise AssertionError("Historical native z and isource grid shapes changed")
                if idx>=z.shape[0] or z.shape[0]!=t["original_time_length"]:
                    raise AssertionError("2016 source index no longer matches original time dimension")
                if z.shape[1]*z.shape[2]>MAX_TILE_CELLS:
                    raise AssertionError("Original 2016 tile exceeds fixed grid cell cap")
                if str(getattr(z,"units",""))!="m":
                    raise AssertionError("Native source 2016 z units not meters")
                if str(getattr(nc.variables["crs"],"EPSG_code",""))!=EXPECTED_CRS:
                    raise AssertionError("Native horizontal 2016 geographic reference changed")
                # Read only the single predeclared 2016 layer, not the entire
                # 1948-2025 source DEM time series. Keep ephemeral in RAM.
                z_2016=z[idx,:,:]
                isource_2016=src[idx,:,:]
                out=source_counts(z_2016,isource_2016)
                out["native_2016_grid_shape_y_x"]=[int(z.shape[1]),int(z.shape[2])]
                out["original_2016_native_TIME_index"]=idx
                out["original_native_year_label"]=TARGET_TIME_LABEL
                out["time_label_does_NOT_prove_actual_2016_field_measurement_day"]=True
                out["native_horizontal_crs"]=EXPECTED_CRS
                out["native_vertical_datum_same_as_RWS_NAP"]="NOT_VERIFIED"
                valid=out["native_2016_time_label_z_nonfill_finite_cells"]
                out["status"]=(
                    "REAL_2016_NATIVE_LAYER_HAS_NONFILL_Z_SUPPORT"
                    if valid>=MIN_VALID_CELLS_FOR_TILE else
                    "SOURCE_STOP_2016_NATIVE_LAYER_TOO_FEW_VALID_Z"
                )
                return {"tile":tile,**out}
        except (OSError,TimeoutError,ConnectionError) as e:
            last_error=e
            if attempt+1<MAX_RETRIEVAL_ATTEMPTS:
                time.sleep(2)
        except Exception:
            raise
    return {"tile":tile,"status":"SOURCE_STOP_2016_RASTER_REMOTE_ACCESS",
            "source_error_class":type(last_error).__name__ if last_error else "Unknown",
            "source_error_excerpt":str(last_error)[:210] if last_error else ""}

def run():
    old=json.loads(PRIOR.read_text())
    ds=json.loads(DDS.read_text())
    if old["n_tiles_with_2016_native_time_label"]!=EXPECTED_TILES or old["n_real_native_time_coordinate_tiles_read"]!=EXPECTED_TILES:
        raise AssertionError("Frozen true 2016 native time source eligibility changed")
    rows=old["all_ten_true_source_tile_time_or_explicit_STOP"]
    native={r["tile"]:r for r in ds["all_original_tile_source_schema_or_STOP"]}
    if len(rows)!=EXPECTED_TILES or set(native)!={r["tile"] for r in rows}:
        raise AssertionError("Original 10 native geo/time tile identities changed")
    results=[]
    for tile in sorted(rows,key=lambda x:x["tile"]):
        r=check_original_tile(tile,native)
        results.append(r)
        print("V176_SOURCE_TILE="+json.dumps({
            "tile":r["tile"],"status":r["status"],
            "n_valid_z2016":r.get("native_2016_time_label_z_nonfill_finite_cells"),
            "n_isource":r.get("native_2016_valid_z_AND_source_code_cells")
        },sort_keys=True),flush=True)
    admitted=[r for r in results if r["status"]=="REAL_2016_NATIVE_LAYER_HAS_NONFILL_Z_SUPPORT"]
    return {
        "version":"v176_genuine_2016_time_layer_z_and_isource_source_support_1",
        "n_native_original_tiles_considered":len(results),
        "n_native_original_2016_layers_with_1000plus_valid_z_cells":len(admitted),
        "n_source_tiles_with_no_2016_grid_data_or_remote_STOP":len(results)-len(admitted),
        "original_total_valid_native_z2016_pixels_across_tiles":sum(r["native_2016_time_label_z_nonfill_finite_cells"] for r in results if "native_2016_time_label_z_nonfill_finite_cells" in r),
        "all_ten_original_source_validity_or_STOP":results,
        "min_valid_native_z_source_cells_per_tile":MIN_VALID_CELLS_FOR_TILE,
        "no_actual_bird_GPS_elevation_sampling_YET":True,
        "no_local_RWS_NAP_same_datum_proven_YET":True,
        "2016_native_grid_not_guarantee_every_pixel_surveyed_in_2016":True,
        "source_isource_zero_based_origin_code_not_bird_ID_or_survey_date":True,
        "no_tide_solar_causal_or_social_Boids_effect":"NOT_ESTIMATED"
    }

def main():
    p=argparse.ArgumentParser()
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--emit",action="store_true")
    m.add_argument("--check",action="store_true")
    args=p.parse_args()
    r=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if not OUT.is_file():raise AssertionError("Frozen original 2016 z/source valid pixel receipt missing")
        previous=json.loads(OUT.read_text())
        if r!=previous:raise AssertionError("Original native 2016 pixel-count/source indices changed")
        print("V176_ORIGINAL_2016_Z_ISOURCE_PIXEL_SOURCE_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(r,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
        print("V176_ORIGINAL_SOURCE_START")
        print(json.dumps(r,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V176_ORIGINAL_SOURCE_END")
    print("V176_SOURCE_SCOPE="+json.dumps({
        "n_tiles":r["n_native_original_tiles_considered"],
        "n_usable":r["n_native_original_2016_layers_with_1000plus_valid_z_cells"],
        "total_valid_z":r["original_total_valid_native_z2016_pixels_across_tiles"],
        "tile_counts":[{
            "tile":v["tile"],"status":v["status"],
            "valid_z":v.get("native_2016_time_label_z_nonfill_finite_cells"),
            "valid_source":v.get("native_2016_valid_z_AND_source_code_cells")
        } for v in r["all_ten_original_source_validity_or_STOP"]]
    },sort_keys=True))
if __name__=="__main__":
    main()
