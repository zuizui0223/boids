"""v219: original BAW WCS2 generated NetCDF4 *nearest native grid point*
versus original BAW WMS1.3 GetFeatureInfo at same 2011 public reference/time.

8 PREDECLARED WCS and 8 WMS calls: year 2018/19, June1 UTC 00 or 12,
Vlieland Haven and Wierumergronden. All data from SAME BAW MODEL; this is
a provider-interface and missingness consistency QA, NOT independent physics.

Native nearest WCS gridpoint and WMS image-centre query need not sample the
same effective grid cell. Negative results are preserved, never cherry-picked.
No original full-year NetCDF, raw binary, original RWS time-series, bird GPS/ACC.
"""
from __future__ import annotations
import hashlib
import json
import math
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
import numpy as np
from netCDF4 import Dataset

from BAW_original_timed_NL_2018_2019_small_WCS_NetCDF4_source import (
    FROZEN_SOURCE_RD,FROZEN_YEARS,FROZEN_FORMAT,SPATIAL_HALF_WIDTH_DEG,
    HDF5_MAGIC,MAX_NATIVE_NETCDF4_BYTES,BAW_WCS_NATIVE_NIL,
    fixed_public_wgs84,only_four_frozen_WCS_getcoverage_urls,DoNotFollow
)
from BAW_ncHydro_2018_2019_WCS_supported_formats_axes_source import (
    FROZEN_WCS_CAP_SHA,FROZEN_DESCRIBE_SHA,FROZEN_COVERAGE_IDS,
    source_native_formats,source_native_description_axes
)
from original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
    CANDIDATE,original_GET,describe_URL
)
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
    OFFICIAL_YEAR_WMS,FIXED_CAPABILITIES_SHA256,NATIVE_HEIGHT_LAYERS,
    fetch_verified_original_WMS,validate_capability_and_layer
)
from true_BAW_2018_2019_Wasserstand_vs_RWS_gauge_NAP import (
    frozen_WMS_model_request,get_approved_original_WMS_Wasserstand
)

FROZEN_HOURS=(0,12)
FROZEN_DATE_MONTH_DAY="06-01"
MAX_NEAREST_ANGULAR_DEGREES=0.012
FROZEN_NUMERIC_APPROX_TOLERANCE_M=0.05
MAX_SOURCE_CELLS=10_000
OUT=Path(__file__).resolve().parent/"results/v219_original_BAW_NC4_grid_vs_WMS_point_2018_2019_June1_00_12.json"

def frozen_year_UTC(year,hour):
    if year not in FROZEN_YEARS or hour not in FROZEN_HOURS:
        raise ValueError("SOURCE_STOP_UNFROZEN_YEAR_OR_HOUR")
    return f"{year}-06-01T{hour:02d}:00:00.000Z"

def exact_bounded_WCS_query(year,site,hour):
    if year not in FROZEN_YEARS or site not in FROZEN_SOURCE_RD or hour not in FROZEN_HOURS:
        raise ValueError("SOURCE_STOP_OUTSIDE_EIGHT_FROZEN_WCS_SOURCE_QUERIES")
    base=only_four_frozen_WCS_getcoverage_urls(year,site)
    parts=urllib.parse.urlsplit(base)
    parameters=urllib.parse.parse_qsl(parts.query,keep_blank_values=True)
    swapped=[]
    found=0
    for key,value in parameters:
        if key=="subset" and value.startswith("time("):
            value='time("'+frozen_year_UTC(year,hour)+'")'
            found+=1
        swapped.append((key,value))
    if found!=1:
        raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NATIVE_TIME_AXIS_REQUEST_WRONG")
    return urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,
                                    urllib.parse.urlencode(swapped),""))

def fixed_native_WCS_url_is_approved(url,year,site,hour):
    return bool(year in FROZEN_YEARS and site in FROZEN_SOURCE_RD and
                hour in FROZEN_HOURS and
                url==exact_bounded_WCS_query(year,site,hour))

def fetch_true_bounded_WCS(year,site,hour):
    url=exact_bounded_WCS_query(year,site,hour)
    if not fixed_native_WCS_url_is_approved(url,year,site,hour):
        raise ValueError("SOURCE_STOP_WCS_URL_NOT_PREDECLARED")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v219-original-BAW-WCS-vs-WMS-nearest-native-grid-QA/1.0",
        "Accept":FROZEN_FORMAT})
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        DoNotFollow())
    with op.open(req,timeout=65) as response:
        blob=response.read(MAX_NATIVE_NETCDF4_BYTES+1)
        status=response.status
        final=response.geturl()
        ctype=response.headers.get("Content-Type","")
    if status!=200 or final!=url or not blob or len(blob)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("SOURCE_STOP_BAW_NATIVE_WCS_NOT_HTTP200_OR_TOO_LARGE")
    if not blob.startswith(HDF5_MAGIC) or "netcdf" not in ctype.lower():
        raise ValueError("SOURCE_STOP_BAW_NATIVE_WCS_NOT_NC4")
    return blob,{
        "original_provider_WCS_generated_NC4_SHA256":hashlib.sha256(blob).hexdigest(),
        "original_WCS_HTTP_status":status,
        "original_content_type":ctype,
        "original_bounded_bytes":len(blob),
        "source_HTTPS_CA_validation_ON":True,
        "no_raw_source_NC4_persisted":True}

def nearest_original_WCS_grid_point(native_binary,site):
    if not native_binary.startswith(HDF5_MAGIC) or len(native_binary)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("SOURCE_STOP_NOT_BOUNDED_HDF5_BINARY")
    lon_ref,lat_ref=fixed_public_wgs84(site)
    with Dataset("source_wcs219_in_RAM.nc",mode="r",memory=native_binary) as ds:
        if not {"time","lat","lon"}.issubset(set(ds.dimensions)):
            raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NC4_REQUIRED_LAT_LON_TIME_MISSING")
        for dim in ("time","lat","lon"):
            if dim not in ds.variables:
                raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NC4_COORDINATE_VARIABLE_MISSING_"+dim)
        lat=np.asarray(ds.variables["lat"][:],dtype=float)
        lon=np.asarray(ds.variables["lon"][:],dtype=float)
        if (lat.ndim!=1 or lon.ndim!=1 or lat.size>1000 or lon.size>1000 or
            not lat.size or not lon.size or not np.all(np.isfinite(lat)) or
            not np.all(np.isfinite(lon))):
            raise ValueError("SOURCE_STOP_ORIGINAL_WCS_INVALID_NATIVE_COORDINATES")
        if not (np.all(np.diff(lat)>0) or np.all(np.diff(lat)<0)):
            raise ValueError("SOURCE_STOP_LAT_NATIVE_COORDINATE_NOT_MONOTONIC")
        if not (np.all(np.diff(lon)>0) or np.all(np.diff(lon)<0)):
            raise ValueError("SOURCE_STOP_LON_NATIVE_COORDINATE_NOT_MONOTONIC")
        iy=int(np.argmin(np.abs(lat-lat_ref)))
        ix=int(np.argmin(np.abs(lon-lon_ref)))
        delta_lat=abs(float(lat[iy]-lat_ref))
        delta_lon=abs(float(lon[ix]-lon_ref))
        if delta_lat>MAX_NEAREST_ANGULAR_DEGREES or delta_lon>MAX_NEAREST_ANGULAR_DEGREES:
            raise ValueError("SOURCE_STOP_NO_NATIVE_GRID_CENTRE_NEAR_PUBLIC_REFERENCE_POINT")
        names=[k for k in ds.variables if "sea_surface_height" in k.lower() or k.lower()=="wasserstand"]
        if len(names)!=1:
            raise ValueError("SOURCE_STOP_AMBIGUOUS_SOURCE_NC4_HEIGHT_VARIABLE")
        var=ds.variables[names[0]]
        if (var.dimensions!=("time","lat","lon") or var.shape[0]!=1 or
            var.shape[1]!=lat.size or var.shape[2]!=lon.size or
            int(np.prod(var.shape))>MAX_SOURCE_CELLS):
            raise ValueError("SOURCE_STOP_NATIVE_NC4_TIME_OR_SPACE_NOT_SLICED")
        if "units" not in var.ncattrs() or str(var.getncattr("units"))!="m":
            raise ValueError("SOURCE_STOP_SOURCE_NATIVE_WCS_NC4_UNIT_CHANGED")
        if "_FillValue" not in var.ncattrs():
            raise ValueError("SOURCE_STOP_WCS_NATIVE_NETCDF4_MISSING_FILLVALUE")
        fill=float(var.getncattr("_FillValue"))
        if not math.isfinite(fill) or not np.isclose(fill,BAW_WCS_NATIVE_NIL,rtol=1e-6):
            raise ValueError("SOURCE_STOP_WCS_NETCDF4_SOURCE_FILLVALUE_CHANGED")
        var.set_auto_maskandscale(False)
        grid=np.asarray(var[:],dtype=float)
        value=float(grid[0,iy,ix])
        if np.isfinite(value) and np.isclose(value,fill,rtol=1e-6):
            classification="SOURCE_NC4_OFFICIAL_FILLVALUE"
            valid=None
        elif np.isfinite(value) and abs(value)<=10:
            classification="SOURCE_NC4_NUMERIC_MODEL_HEIGHT_M"
            valid=value
        else:
            classification="SOURCE_NC4_OTHER_UNRESOLVED_VALUE"
            valid=None
        nfill=int(np.sum(np.isfinite(grid)&np.isclose(grid,fill,rtol=1e-6)))
        nnormal=int(np.sum(np.isfinite(grid)&(np.abs(grid)<=10)))
        coordtime=ds.variables["time"]
        if coordtime.size!=1:
            raise ValueError("SOURCE_STOP_WCS_OUTPUT_TIME_DIM_NOT_ONE")
        return {
            "source_nearest_gridpoint_class":classification,
            "source_nearest_gridpoint_model_value_m_if_numeric":round(valid,7) if valid is not None else None,
            "source_nearest_native_lat":round(float(lat[iy]),7),
            "source_nearest_native_lon":round(float(lon[ix]),7),
            "source_reference_delta_lat_deg":round(delta_lat,8),
            "source_reference_delta_lon_deg":round(delta_lon,8),
            "source_nearest_native_gridrow_col":[iy,ix],
            "source_native_nc4_shape":[int(v) for v in grid.shape],
            "source_native_nc4_total_cells":int(grid.size),
            "source_native_nc4_official_fillvalue_cell_n":nfill,
            "source_native_nc4_plausible_numeric_cell_n":nnormal,
            "original_WCS_NC4_time_units":str(getattr(coordtime,"units","NOT_DECLARED"))[:220],
            "original_WCS_NC4_time_value":round(float(np.asarray(coordtime[:]).ravel()[0]),6),
            "WCS_nearest_vs_WMS_query_need_not_be_exact_same_source_cell":True,
            "raw_original_model_grid_not_persisted":True}

def compare_WCS_nearest_vs_WMS(wcs,wms_numeric,wms_receipt):
    raw=wms_receipt.get("native_GeoJSON_Wasserstand_classification")
    valid="PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED"
    sent="EXTREME_NODATA_SENTINEL_CANDIDATE"
    if raw not in (valid,sent):
        return {"status":"SOURCE_UNRESOLVED_WMS_RESPONSE_CLASS",
                "WMS_source_class":raw,"categorical_agreement":False}
    wcs_class=wcs["source_nearest_gridpoint_class"]
    if wcs_class=="SOURCE_NC4_NUMERIC_MODEL_HEIGHT_M" and raw==valid:
        if wms_numeric is None:
            raise ValueError("SOURCE_STOP_NATIVE_WMS_VALID_CLASS_BUT_NONUMERIC")
        delta=wcs["source_nearest_gridpoint_model_value_m_if_numeric"]-float(wms_numeric)
        return {"status":"BOTH_NATIVE_WCS_WMS_NUMERIC",
                "WMS_source_class":raw,"categorical_agreement":True,
                "WMS_numeric_model_source_value_m":round(float(wms_numeric),7),
                "source_nc4_nearest_minus_WMS_model_difference_m":round(delta,8),
                "source_numeric_abs_delta_lte_0p05m":abs(delta)<=FROZEN_NUMERIC_APPROX_TOLERANCE_M,
                "same_physical_model_not_independent_validation":True}
    if wcs_class=="SOURCE_NC4_OFFICIAL_FILLVALUE" and raw==sent:
        return {"status":"BOTH_NATIVE_WCS_WMS_FILL_NO_DATA",
                "WMS_source_class":raw,"categorical_agreement":True,
                "WMS_numeric_model_source_value_m":None,
                "same_physical_model_not_independent_validation":True}
    return {"status":"SOURCE_INTERFACE_WMS_VS_WCS_NEAREST_CLASS_DIFFERENCE",
            "WMS_source_class":raw,"WCS_source_class":wcs_class,
            "categorical_agreement":False,
            "WMS_numeric_model_source_value_m":
                 round(float(wms_numeric),7) if wms_numeric is not None else None,
            "native_nearest_grid_and_WMS_51px_image_point_are_not_guaranteed_same_cell":True}

def run(out=OUT):
    report={"analysis":"v219-genuine-original-BAW-WCS-NC4-nearest-vs-WMS-point-8-fixed",
        "original_2011_published_RD_site_references":FROZEN_SOURCE_RD,
        "frozen_two_UTC_hours":FROZEN_HOURS,
        "frozen_June1_years":FROZEN_YEARS,
        "original_same_BAW_model_not_independent_RWS_gauge_validation":True,
        "source_WCS_Cap_SHA":FROZEN_WCS_CAP_SHA,
        "source_WCS_Describe_SHA":FROZEN_DESCRIBE_SHA,
        "source_WMS_Cap_SHA":FIXED_CAPABILITIES_SHA256,
        "no_original_full_year_BAW_NC_or_GPS_ACC_RWS_DEM_retrieved":True,
        "status":"SOURCE_STOP"}
    years={}
    for year in FROZEN_YEARS:
        entry={"status":"SOURCE_STOP_ORIGINAL_YEAR_META","sites":{}}
        try:
            wms,wms_receipt=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            layer=validate_capability_and_layer(wms,year)
            if (wms_receipt["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year] or
                not layer["source_admissible_for_feature_info_probe"] or
                layer["chosen_predeclared_feature_info_format"]!="application/json"):
                raise ValueError("SOURCE_STOP_ORIGINAL_YEAR_WMS_SHA_OR_NATIVE_LAYER_CHANGED")
            cap,cr=original_GET(year,CANDIDATE[year],"GetCapabilities")
            if cap is None or cr["original_SHA256"]!=FROZEN_WCS_CAP_SHA[year]:
                raise ValueError("SOURCE_STOP_ORIGINAL_YEAR_WCS_SHA_CHANGED")
            formats=source_native_formats(cap)
            if "application/x-netcdf4" not in formats["native_explicit_NetCDF_output_format_if_any"]:
                raise ValueError("SOURCE_STOP_WCS_NATIVE_NETCDF4_NO_LONGER_ADVERTISED")
            rawdesc,dr=original_GET(year,describe_URL(year,FROZEN_COVERAGE_IDS[year]),
               "DescribeCoverage",FROZEN_COVERAGE_IDS[year],max_bytes=2_000_000)
            if rawdesc is None or dr["original_SHA256"]!=FROZEN_DESCRIBE_SHA[year]:
                raise ValueError("SOURCE_STOP_ORIGINAL_YEAR_WCS_DESCRIBE_SOURCE_CHANGED")
            axes=source_native_description_axes(rawdesc,FROZEN_COVERAGE_IDS[year])
            if len(axes["source_native_envelopes"])!=1 or (
              axes["source_native_envelopes"][0]["native_axisLabels"]!="Lat Long time"):
                raise ValueError("SOURCE_STOP_WCS_NATIVE_LAT_LONG_TIME_AXIS_CHANGED")
            entry["source_original_WCS_SHA"]=cr["original_SHA256"]
            entry["source_original_WMS_SHA"]=wms_receipt["original_WMS_xml_SHA256"]
            entry["status"]="BOTH_NATIVE_WCS_WMS_YEAR_SOURCE_GATES_PASS"
            for site in FROZEN_SOURCE_RD:
                cohorts={}
                for hour in FROZEN_HOURS:
                    case={"status":"SOURCE_STOP_BAW_TWO_INTERFACES_NOT_BOTH_ADMITTED"}
                    try:
                        raw,receipt=fetch_true_bounded_WCS(year,site,hour)
                        wcs=nearest_original_WCS_grid_point(raw,site)
                        modelnumeric,wmsreceipt=get_approved_original_WMS_Wasserstand(
                             frozen_WMS_model_request(year,site,hour))
                        comparison=compare_WCS_nearest_vs_WMS(wcs,modelnumeric,wmsreceipt)
                        case={"status":"ORIGINAL_BAW_TWO_SERVICE_SOURCE_VALUES_AUDITED",
                            "UTC":frozen_year_UTC(year,hour),
                            "original_bounded_WCS_NetCDF4_receipt":receipt,
                            "native_nearest_WCS_NC4_source":wcs,
                            "original_WMS_point_response_sha":wmsreceipt["source_original_HTTP_JSON_SHA256"],
                            "source_WCS_vs_WMS_class_or_value_comparison":comparison}
                    except Exception as e:
                        case["error_kind"]=type(e).__name__
                        case["error_summary"]=str(e)[:230]
                    cohorts[str(hour)]=case
                entry["sites"][site]=cohorts
        except Exception as e:
            entry["error_kind"]=type(e).__name__
            entry["error_summary"]=str(e)[:230]
        years[year]=entry
    report["genuine_original_BAW_year_site_hour_results"]=years
    cases=[d for r in years.values() for s in r["sites"].values() for d in s.values()]
    verified=[d for d in cases if d["status"]=="ORIGINAL_BAW_TWO_SERVICE_SOURCE_VALUES_AUDITED"]
    numeric=[d for d in verified if d["source_WCS_vs_WMS_class_or_value_comparison"].get(
          "status")=="BOTH_NATIVE_WCS_WMS_NUMERIC"]
    report["scientific_gates"]={
       "all_eight_fixed_original_WCS_and_WMS_2018_2019_source_pairs_retrieved":len(verified)==8,
       "n_predeclared_eight_source_pairs_verifiably_read":len(verified),
       "n_original_two_interface_categorical_agreements":sum(bool(
           d["source_WCS_vs_WMS_class_or_value_comparison"].get("categorical_agreement"))
           for d in verified),
       "n_original_both_service_Nil_agreements":sum(
           d["source_WCS_vs_WMS_class_or_value_comparison"].get("status")==
             "BOTH_NATIVE_WCS_WMS_FILL_NO_DATA" for d in verified),
       "n_original_both_service_numeric_cases":len(numeric),
       "n_numeric_pairs_abs_difference_lte_0p05m":sum(
           d["source_WCS_vs_WMS_class_or_value_comparison"].get(
               "source_numeric_abs_delta_lte_0p05m",False) for d in numeric),
       "n_class_mismatch_or_source_unresolved":sum(
           not d["source_WCS_vs_WMS_class_or_value_comparison"].get("categorical_agreement")
           for d in verified),
       "model_WCS_nearest_equals_WMS_51px_center_exact_same_grid_cell_proven":False,
       "BAW_original_full_year_publisher_NetCDF_variable_attrs_read":False,
       "model_Nil_is_causally_physical_dry_cell_proven":False,
       "bird_GPS_cell_tide_sun_social_Boids_ecological_effect_estimated":False}
    report["status"]=("EIGHT_BAW_NATIVE_WCS_VS_WMS_SOURCE_PAIR_VALUES_AUDITED_NO_CAUSAL_PHYSICS"
        if len(verified)==8 else "SOURCE_STOP_INCOMPLETE_EIGHT_WCS_VS_WMS_NATIVE_SOURCE_PAIRS")
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V219_ORIGINAL_WCS_VS_WMS_8PAIR="+json.dumps({
       "status":report["status"],"gates":report["scientific_gates"],
       "cases":{y:{site:{h:{
           "status":a["status"],
           "WCS_class":a.get("native_nearest_WCS_NC4_source",{}).get("source_nearest_gridpoint_class"),
           "WMS_class":a.get("source_WCS_vs_WMS_class_or_value_comparison",{}).get("WMS_source_class"),
           "native_WCS_Nil_n":a.get("native_nearest_WCS_NC4_source",{}).get("source_native_nc4_official_fillvalue_cell_n"),
           "native_WCS_total_cells":a.get("native_nearest_WCS_NC4_source",{}).get("source_native_nc4_total_cells"),
           "source_delta_m":a.get("source_WCS_vs_WMS_class_or_value_comparison",{}).get(
                "source_nc4_nearest_minus_WMS_model_difference_m"),
           "match":a.get("source_WCS_vs_WMS_class_or_value_comparison",{}).get("categorical_agreement"),
           "error":a.get("error_summary")}
          for h,a in hours.items()} for site,hours in row["sites"].items()}
          for y,row in years.items()},
       "NO_real_GPS_cell_or_ecological_cause":True
    },sort_keys=True))
    return report

if __name__=="__main__":
    run()
