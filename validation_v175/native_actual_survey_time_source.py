"""v175: authentic original DAP time and isource VALUES for 10 Vlieland tiles.

Native original Deltares RWS bathymetry tile data hold time, isource and
z(time,y,x). The original catalog TIME RANGE spanning 2016 (v173) is
not proof that the tile has an ACTUAL 2016 survey date/slice. Obtain
real provider time coordinate values and zero-based survey source codes
without downloading/sampling z or any bird GPS/tide/behavior data.

The 2018/19 tagged-bird exposure must later use a real valid original
z value surveyed BEFORE the behavior time at that GPS position, a
compatible NAP water-level datum, and uncertainty in 2016-2019 terrain.

No years or source mask fabricated from index alone. If native time data
inaccessible, record SOURCE_STOP per tile; do not impute a 2016 layer.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,urllib.request
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
PRIOR=ROOT/"validation_v174/results/genuine_ten_vlie_tile_DDS_DAS_schema_v174.json"
OUT=ROOT/"validation_v175/results/original_ten_vlieland_survey_time_source_v175.json"
MAX_TIMES_PER_TILE=125
MAX_ASCII_BYTES=250_000
REAL_YEAR_WINDOW=(2014,2019)
TARGET_SURVEY_YEAR=2016
EXPLICIT_URL_DOMAIN="opendap.deltares.nl"
EXPECTED_TILES=10

def true_source_time_days_to_dates(days):
    d=np.asarray(days,dtype=np.float64)
    if d.ndim!=1 or not d.size or d.size>MAX_TIMES_PER_TILE:
        raise ValueError("Unexpected original native time-coordinate dimension")
    if not np.isfinite(d).all() or np.max(np.abs(d))>55000:
        raise ValueError("Missing/nonfinite/out-of-range original native time")
    origin=datetime(1970,1,1,tzinfo=timezone.utc)
    return [(origin+timedelta(days=float(x))).strftime("%Y-%m-%d") for x in d]

def native_dataset_time(url,expected_length):
    from netCDF4 import Dataset
    # Native DAP2 transfer opens source dimensions/metadata and retrieves
    # only the 8-39 element 1D TIME/ISOURCE variables; z grid is NOT opened.
    with Dataset(url,mode="r") as nc:
        if "time" not in nc.variables or "isource" not in nc.variables or "z" not in nc.variables:
            raise AssertionError("True original native survey time/isource/z variables missing")
        t=nc.variables["time"]
        units=str(getattr(t,"units",""))
        if not units.startswith("days since 1970-01-01"):
            raise AssertionError("Unexpected original survey calendar units")
        if t.ndim!=1 or t.shape[0]!=expected_length:
            raise AssertionError("Original survey time dimension disagrees with source DDS")
        tv=np.ma.asarray(t[:]).filled(np.nan)
        v=nc.variables["isource"]
        isource_info={
            "original_source_index_dimensions":list(v.dimensions),
            "original_source_index_shape":list(v.shape),
            "original_isource_not_bird_identity":"YES_NATIVE_SURVEY_FILE_INDEX"
        }
        if v.ndim==1 and v.shape[0]==len(tv) and v.size<=MAX_TIMES_PER_TILE:
            iv=np.ma.asarray(v[:]).filled(-32768)
            try:
                val=np.asarray(iv,dtype=float)
                if np.isfinite(val).all():
                    c=Counter(int(x) for x in val)
                    isource_info["source_index_counts"]={str(k):int(n) for k,n in sorted(c.items())}
                    isource_info["source_index_order_by_time"]=[int(x) for x in val]
            except (ValueError,TypeError):pass
        z=nc.variables["z"]
        data_info={
            "native_z_dimensions":list(z.dimensions),
            "native_z_shape":list(z.shape),
            "native_z_units":str(getattr(z,"units","")),
            "native_z_not_downloaded":"YES_SOURCE_TIME_ONLY"
        }
        crs=nc.variables.get("crs")
        crsEPSG=str(getattr(crs,"EPSG_code","")) if crs is not None else ""
        global_vertical=str(getattr(nc,"geospatial_vertical_datum",""))
        # NAP must be validated by cross-source known vertical datum;
        # EPSG horizontal projection is not itself a vertical datum.
        return np.asarray(tv,dtype=float),{
            "real_original_time_units":units,
            "source_isource_metadata":isource_info,
            "source_z_metadata":data_info,
            "real_source_horizontal_EPSG":crsEPSG,
            "original_global_vertical_datum_attribute":global_vertical[:160],
            "native_source_time_access":"NETCDF4_OPENDAP_TIME_COORDINATE_ONLY"
        }

def ascii_fallback_time(url,expected_length):
    # OPeNDAP DAP2 .ascii permits a tiny source-only projected 1D time
    # data fetch when system netCDF client cannot read the remote server.
    req=urllib.request.Request(url+".ascii?time",headers={
        "User-Agent":"OpenScienceBoids/1.0 noncommercial RWS Deltares historical survey",
        "Accept":"text/plain,*/*"
    })
    with urllib.request.urlopen(req,timeout=50) as f:
        raw=f.read(MAX_ASCII_BYTES+1)
    if not 100<len(raw)<=MAX_ASCII_BYTES:
        raise ValueError("Invalid source .ascii time payload size")
    body=raw.decode("utf-8","replace")
    if "Dataset {" not in body or "time" not in body:
        raise ValueError("Source .ascii not valid native DAP dataset")
    data={}
    for line in body.splitlines():
        m=re.match(r"^\s*time\s*\[\s*(\d+)\s*\]\s*,\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*$",line,re.I)
        if m:
            index=int(m.group(1))
            if index in data:raise AssertionError("Duplicate original source time coordinate index")
            data[index]=float(m.group(2))
    if len(data)!=expected_length or sorted(data)!=list(range(expected_length)):
        raise ValueError("Cannot validate all source original time samples from DAP ASCII")
    values=np.asarray([data[i] for i in range(expected_length)],dtype=float)
    return values,{
        "native_source_time_access":"Genuine_DAP2_ASCII_time_ONLY",
        "raw_DAP2_time_response_SHA256":hashlib.sha256(raw).hexdigest(),
        "raw_DAP2_time_response_bytes":len(raw),
        "native_isource_time_y_x_grid":"NOT_READ_FROM_SOURCE_ASCII_FALLBACK",
        "native_z_grid":"NOT_DOWNLOADED",
        "real_original_time_units":"days since 1970-01-01 (original DAS only)"
    }

def source_tile(t):
    label=t["tile"]
    if not label.startswith("vaklodingenKB") or not label.endswith(".nc"):
        raise AssertionError("Unknown original Deltares tile label")
    dds=t["dds"]
    das=t["das"]
    if dds["status"]!="AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA" or das["status"]!="AUTHENTIC_ORIGINAL_OPENDAP_SOURCE_METADATA":
        return {"tile":label,"status":"STOP_PRIOR_NATIVE_DDS_OR_DAS_UNAVAILABLE"}
    lengths=dds["original_source_schema"]["native_time_dimension_lengths"]
    if len(lengths)!=1 or not 1<=lengths[0]<=MAX_TIMES_PER_TILE:
        raise AssertionError("Original native tile time length source unknown")
    n=lengths[0]
    original_url=t["dds"]["original_provider_provenance"]["source_uri_requested"]
    if not original_url.startswith("https://"+EXPLICIT_URL_DOMAIN+"/") or not original_url.endswith(".nc.dds"):
        raise AssertionError("Original tile provenance not from authorized official host")
    url=original_url[:-4]
    errs=[]
    try:
        values,meta=native_dataset_time(url,n)
    except Exception as e:
        errs.append("NETCDF4_"+type(e).__name__+":"+str(e)[:140])
        try:
            values,meta=ascii_fallback_time(url,n)
        except Exception as ex:
            errs.append("ASCII_"+type(ex).__name__+":"+str(ex)[:140])
            return {"tile":label,"status":"SOURCE_STOP_NATIVE_TIME_VALUES_UNAVAILABLE",
                    "error_codes":errs,"native_time_length_expected":n}
    dates=true_source_time_days_to_dates(values)
    years=[int(x[:4]) for x in dates]
    if len(set(dates))!=len(dates):
        raise AssertionError("Duplicate native survey dates in source time vector")
    # Source chronology is about survey snapshots only, not actual GPS pixels.
    index2016=[i for i,year in enumerate(years) if year==TARGET_SURVEY_YEAR]
    before2018=[(d,i) for i,d in enumerate(dates) if d<"2018-01-01"]
    before2019=[(d,i) for i,d in enumerate(dates) if d<"2019-01-01"]
    return {
        "tile":label,
        "status":"REAL_NATIVE_TIME_COORDINATES_VERIFIED",
        "original_time_length":n,
        "native_time_coordinate_labels_not_proven_field_days":dates,
        "2016_native_time_label_is_Jan01_index_NOT_verified_measurement_day":
           (not index2016 or all(dates[i].endswith("-01-01") for i in index2016)),
        "actual_source_time_year_counts":dict(sorted(Counter(map(str,years)).items())),
        "has_2016_native_time_coordinate_label":bool(index2016),
        "original_indices_for_2016_native_time_label":index2016,
        "latest_source_time_label_before_2018":max(before2018,default=None),
        "latest_source_time_label_before_2019":max(before2019,default=None),
        "true_time_coordinate_values_SHA256":hashlib.sha256(values.astype("<f8").tobytes()).hexdigest(),
        "historical_original_source_metadata":meta,
        "source_initial_netCDF4_error_if_ascii_used":errs,
        "actual_valid_2016_z_elevation_cells_at_bird_GPS":"NOT_YET_AUDITED",
        "same_NAP_as_2018_2019_RWS_harbor":"NOT_YET_VERIFIED",
    }

def run():
    old=json.loads(PRIOR.read_text())
    if old["n_real_original_candidate_tiles"]!=EXPECTED_TILES or old["original_tiles_with_both_authentic_DDS_DAS_schemas"]!=EXPECTED_TILES:
        raise AssertionError("Frozen original ten tile real DDS/DAS scope changed")
    rows=[]
    for source in sorted(old["all_original_tile_source_schema_or_STOP"],key=lambda x:x["tile"]):
        r=source_tile(source)
        rows.append(r)
        print("V175_SOURCE_TILE="+json.dumps({
            "tile":r["tile"],"status":r["status"],
            "years":r.get("actual_source_time_year_counts"),
            "has_2016":r.get("has_2016_native_time_coordinate_label")
        },sort_keys=True),flush=True)
    good=[r for r in rows if r["status"]=="REAL_NATIVE_TIME_COORDINATES_VERIFIED"]
    return {
        "version":"v175_true_original_10_vlieland_2016_survey_time_isource_source_gate_1",
        "n_original_candidate_tiles":len(rows),
        "n_real_native_time_coordinate_tiles_read":len(good),
        "n_tiles_with_2016_native_time_label":sum(x["has_2016_native_time_coordinate_label"] for x in good),
        "n_tiles_without_2016_native_time_label":sum(not x["has_2016_native_time_coordinate_label"] for x in good),
        "2016_Jan01_time_coordinate_may_be_annual_index_not_actual_field_date":True,
        "source_isource_is_grid_time_y_x_not_1D_and_is_not_downloaded":True,
        "all_ten_true_source_tile_time_or_explicit_STOP":rows,
        "catalog_time_range_does_NOT_mean_2016_true_measurement":True,
        "actual_2016_valid_z_measurements_at_individual_bird_GPS":"NOT_YET_AUDITED",
        "no_local_NAP_datum_calibration_or_habitat_exposure":"NOT_YET_ESTIMATED",
        "no_independent_2018_2019_tide_by_solar_causal_or_social_Boids_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--emit",action="store_true")
    m.add_argument("--check",action="store_true")
    args=p.parse_args()
    data=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if not OUT.exists():raise AssertionError("No frozen historical time survey receipt")
        if json.loads(OUT.read_text())!=data:
            raise AssertionError("Real original survey times/source codes changed")
        print("V175_GENUINE_ORIGINAL_VLIELAND_TEN_TILE_SURVEY_TIME_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("V175_TRUE_SOURCE_TIMES_START")
        print(json.dumps(data,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V175_TRUE_SOURCE_TIMES_END")
    print("V175_TRUE_SURVEY_YEAR_SUMMARY="+json.dumps({
        "n_time_read":data["n_real_native_time_coordinate_tiles_read"],
        "n_exact2016":data["n_tiles_with_2016_native_time_label"],
        "tiles":[{
            "tile":x["tile"],"status":x["status"],
            "survey_years":x.get("actual_source_time_year_counts"),
            "2016":x.get("original_indices_for_2016_native_time_label")
        } for x in data["all_ten_true_source_tile_time_or_explicit_STOP"]]
    },sort_keys=True))
if __name__=="__main__":main()
