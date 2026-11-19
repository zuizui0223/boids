"""v220: 24 predeclared genuine BAW 2018/19 time-resolved WCS NetCDF4
nearest source gridpoint Nil classifications vs previous SHA-pinned v209 original
WMS response classes across 3 public sites, 2 months (Jun/Sep), 2 UTC hours.

This is observational source QA within ONE BAW MODEL, not true physical
wetted/dry habitat, independent gauge validation or animal niche inference.
No original RWS, WMS live timeseries or bird GPS/ACC is fetched in v220.
WCS NetCDF4 raw binary remains only in GitHub Actions RAM.
"""
from __future__ import annotations
import argparse,hashlib,json,math,ssl,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
from netCDF4 import Dataset
from pyproj import Transformer

from original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
    CANDIDATE,original_GET,describe_URL)
from BAW_ncHydro_2018_2019_WCS_supported_formats_axes_source import (
    FROZEN_WCS_CAP_SHA,FROZEN_DESCRIBE_SHA,FROZEN_COVERAGE_IDS,
    source_native_formats,source_native_description_axes)
from BAW_original_timed_NL_2018_2019_small_WCS_NetCDF4_source import (
    SPATIAL_HALF_WIDTH_DEG,FROZEN_FORMAT,
    MAX_NATIVE_NETCDF4_BYTES,HDF5_MAGIC,BAW_WCS_NATIVE_NIL,DoNotFollow)
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
    OFFICIAL_YEAR_WMS,FIXED_CAPABILITIES_SHA256,
    FIXED_PUBLICATION_RD_POINTS,fetch_verified_original_WMS,
    validate_capability_and_layer)
from validation_v210.sha_verified_v209_source_WMS_selection_bias import (
    exact_original_source,SENTINEL,PLAUSIBLE)

FROZEN_PUBLIC_SITES={
  "VlielandHaven":(135280,590000),
  "WestTerschelling":(143870,597420),
  "Wierumergronden":(192882,614562)
}
FROZEN_YEARS=("2018","2019")
FROZEN_MONTHS={"June":"06","September":"09"}
FROZEN_UTC_HOURS=(0,12)
MAX_COORD_DELTA_DEG=0.012
MAX_NATIVE_GRID_CELLS=10000
OUT=Path(__file__).resolve().parent/"results/v220_original_WCS_NC4_Nil_vs_72WMS_archive_24_public_site_times.json"

def strict_public_coordinate(site):
    if site not in FROZEN_PUBLIC_SITES or (
        FROZEN_PUBLIC_SITES[site]!=FIXED_PUBLICATION_RD_POINTS.get(site)):
        raise ValueError("SOURCE_STOP_NATIVE_WEBTICS_REFERENCE_SITE_CHANGED")
    lon,lat=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True).transform(
        *FROZEN_PUBLIC_SITES[site])
    if not(4.1769<lon<7.3397 and 52.8632<lat<53.9412):
        raise ValueError("SOURCE_STOP_WEBTICS_REFERENCE_OUTSIDE_NATIVE_BAW_COVERAGE")
    return lon,lat

def fixed_timestamp(year,month,hour):
    if year not in FROZEN_YEARS or month not in FROZEN_MONTHS or hour not in FROZEN_UTC_HOURS:
        raise ValueError("SOURCE_STOP_NONFROZEN_YEAR_MONTH_OR_UTC_HOUR")
    return f"{year}-{FROZEN_MONTHS[month]}-01T{hour:02d}:00:00.000Z"

def fixed_WCS_GetCoverage_URL(year,month,site,hour):
    if year not in FROZEN_YEARS or site not in FROZEN_PUBLIC_SITES or (
      month not in FROZEN_MONTHS or hour not in FROZEN_UTC_HOURS):
        raise ValueError("SOURCE_STOP_NONFROZEN_THREE_SITE_TWO_MONTH_WCS_CASE")
    lon,lat=strict_public_coordinate(site)
    base=urllib.parse.urlsplit(CANDIDATE[year])
    params=[
      ("service","WCS"),("version","2.0.1"),("request","GetCoverage"),
      ("coverageId",FROZEN_COVERAGE_IDS[year]),
      ("format",FROZEN_FORMAT),
      ("subset",f"Lat({lat-SPATIAL_HALF_WIDTH_DEG:.6f},{lat+SPATIAL_HALF_WIDTH_DEG:.6f})"),
      ("subset",f"Long({lon-SPATIAL_HALF_WIDTH_DEG:.6f},{lon+SPATIAL_HALF_WIDTH_DEG:.6f})"),
      ("subset",'time("'+fixed_timestamp(year,month,hour)+'")')]
    return urllib.parse.urlunsplit((base.scheme,base.netloc,base.path,
                                    urllib.parse.urlencode(params),""))

def source_bounded_24_query_admitted(url,year,month,site,hour):
    return (year in FROZEN_YEARS and month in FROZEN_MONTHS and
            site in FROZEN_PUBLIC_SITES and hour in FROZEN_UTC_HOURS and
            url==fixed_WCS_GetCoverage_URL(year,month,site,hour))

def secure_official_BAW_bounded_NC4(year,month,site,hour):
    url=fixed_WCS_GetCoverage_URL(year,month,site,hour)
    if not source_bounded_24_query_admitted(url,year,month,site,hour):
        raise ValueError("STOP_NOT_ONE_OF_24_FROZEN_BAW_WCS_QUERIES")
    request=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v220-BAW-original-NL-threeSITE-twoMONTH-WCS-Nil-source-replication/1.0",
        "Accept":FROZEN_FORMAT})
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        DoNotFollow())
    with opener.open(request,timeout=65) as r:
        raw=r.read(MAX_NATIVE_NETCDF4_BYTES+1)
        status=r.status
        final=r.geturl()
        ct=r.headers.get("Content-Type","")
    if status!=200 or final!=url or not raw or len(raw)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("SOURCE_STOP_BAW_ORIGINAL_NC4_RESPONSE_HTTP_OR_SIZE")
    if not raw.startswith(HDF5_MAGIC) or "netcdf" not in ct.lower():
        raise ValueError("SOURCE_STOP_NOT_TRUE_SOURCE_NATIVE_NETCDF4_HDF5")
    return raw,{
        "original_HTTP_NC4_SHA256":hashlib.sha256(raw).hexdigest(),
        "original_source_NC4_bytes_only_in_runner":len(raw),
        "original_source_Content_Type":ct,
        "source_http_status":status,
        "source_TLS_default_CA_ON":True,
        "native_generated_NC4_raw_data_NOT_written_to_artifact":True}

def native_WCS_nearest_grid_class(raw,site):
    if not raw.startswith(HDF5_MAGIC) or len(raw)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("SOURCE_STOP_NOT_BOUNDED_NC4")
    lon0,lat0=strict_public_coordinate(site)
    with Dataset("source_v220_RAM_only.nc",mode="r",memory=raw) as nc:
        if not {"time","lat","lon"}.issubset(set(nc.variables)):
            raise ValueError("STOP_NETCDF4_MISSING_TIME_LAT_LON_COORDINATES")
        lat=np.asarray(nc.variables["lat"][:],dtype=float)
        lon=np.asarray(nc.variables["lon"][:],dtype=float)
        if (lat.ndim!=1 or lon.ndim!=1 or lat.size<1 or lon.size<1
           or not np.all(np.isfinite(lat)) or not np.all(np.isfinite(lon))):
            raise ValueError("SOURCE_STOP_NC4_COORDINATE_AXIS_NOT_1D_FINITE")
        yi=int(np.argmin(abs(lat-lat0)))
        xi=int(np.argmin(abs(lon-lon0)))
        dlat=abs(float(lat[yi]-lat0))
        dlon=abs(float(lon[xi]-lon0))
        if dlat>MAX_COORD_DELTA_DEG or dlon>MAX_COORD_DELTA_DEG:
            raise ValueError("SOURCE_STOP_NOT_NEAREST_SOURCE_CELL_TO_PUBLIC_POINT")
        hits=[name for name in nc.variables if "sea_surface_height" in name.lower() or
              name.lower()=="wasserstand"]
        if len(hits)!=1:
            raise ValueError("SOURCE_STOP_AMBIGUOUS_NATIVE_WCS_SSH_VARIABLE")
        v=nc.variables[hits[0]]
        if (v.dimensions!=("time","lat","lon") or v.shape[0]!=1 or
           v.shape[1]!=lat.size or v.shape[2]!=lon.size or
           int(np.prod(v.shape))>MAX_NATIVE_GRID_CELLS):
            raise ValueError("SOURCE_STOP_NATIVE_WCS_OUTPUT_NOT_ONE_TIME_SMALL_GRID")
        if not (str(getattr(v,"units",None))=="m" and "_FillValue" in v.ncattrs()):
            raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NC4_UOM_OR_FILL_NOT_DECLARED")
        fill=float(v.getncattr("_FillValue"))
        if not math.isfinite(fill) or not np.isclose(fill,BAW_WCS_NATIVE_NIL,rtol=1e-6):
            raise ValueError("SOURCE_STOP_WCS_NC4_NOT_PRIOR_VERIFIED_FILLVALUE")
        v.set_auto_maskandscale(False)
        height=np.asarray(v[:],dtype=float)
        value=float(height[0,yi,xi])
        if np.isfinite(value) and np.isclose(value,fill,rtol=1e-6):
            classification="NC4_OFFICIAL_NIL"
        elif np.isfinite(value) and abs(value)<=10:
            classification="NC4_NUMERIC_SOURCE"
        else:
            classification="NC4_OTHER_VALUE_UNRESOLVED"
        nil=np.isfinite(height)&np.isclose(height,fill,rtol=1e-6)
        numeric=np.isfinite(height)&(np.abs(height)<=10)
        return {
          "nearest_native_WCS_class":classification,
          "nearest_source_lat_long_deviation_deg":[round(dlat,8),round(dlon,8)],
          "native_grid_total_cells":int(height.size),
          "native_grid_official_Nil_cells":int(np.sum(nil)),
          "native_grid_numeric_cells":int(np.sum(numeric)),
          "native_grid_other_unresolved_cells":int(height.size-np.sum(nil)-np.sum(numeric)),
          "native_grid_type":"BAW time-resolved WCS generated NetCDF4; no true local field dryflat",
          "original_NetCDF_full_year_not_downloaded":True}

def archived_model_class_for_case(authentic_v209,month,year,site,hour):
    ts=f"{year}-{FROZEN_MONTHS[month]}-01T{hour:02d}:00:00+00:00"
    key=f"{month}_{year}_{site}"
    groups=authentic_v209.get("all_12_official_model_validity_vs_measured_tide_level_cohorts",{})
    if key not in groups:
        raise ValueError("SOURCE_STOP_MISSING_AUTHENTIC_V209_WMS_COHORT")
    receipts=groups[key].get("original_SIX_WMS_source_replies_SHA_only",[])
    matched=[v for v in receipts if v.get("original_fixed_UTC")==ts]
    if len(matched)!=1:
        raise ValueError("SOURCE_STOP_ORIGINAL_WMS_TIME_MATCH_NOT_UNIQUE")
    cls=matched[0]["source_model_value_class"]
    if cls not in (SENTINEL,PLAUSIBLE):
        raise ValueError("SOURCE_STOP_NONFROZEN_ORIGINAL_WMS_CLASS")
    return {
        "archived_original_WMS_class":cls,
        "original_WMS_source_response_SHA256":matched[0]["source_original_WMS_reply_SHA256"],
        "original_WMS_UTC":matched[0]["original_fixed_UTC"],
        "native_original_WMS_raw_time_series_NOT_requeried":True}

def source_same_time_class_agreement(wcs_status,prior_wms):
    if wcs_status=="NC4_OFFICIAL_NIL":
        return prior_wms==SENTINEL
    if wcs_status=="NC4_NUMERIC_SOURCE":
        return prior_wms==PLAUSIBLE
    return False

def run(archived_v209_path,out=OUT):
    archived,archive_sha=exact_original_source(archived_v209_path,"44452986729")
    data={
       "version":"v220-authentic-BAW-WCS-NC4-Nil-vs-v209-archived-WMS-threeSITE-twoMONTH",
       "source_archived_v209_GitHubActions_run_id":44452986729,
       "source_archived_v209_JSON_exact_SHA256":archive_sha,
       "frozen_three_original_2011_WEBTICS_reference_RD":FROZEN_PUBLIC_SITES,
       "frozen_years":FROZEN_YEARS,
       "frozen_months":FROZEN_MONTHS,
       "frozen_UTC_hours":FROZEN_UTC_HOURS,
       "no_original_WMS_RWS_again_retrieved":True,
       "no_original_bird_GPS_ACC_native_fullyear_NetCDF_downloaded":True,
       "status":"SOURCE_STOP"}
    years={}
    for year in FROZEN_YEARS:
        yr={"status":"SOURCE_STOP_ORIGINAL_YEAR_NATIVE_WCS_META","months":{}}
        try:
            wms,wrc=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            layer=validate_capability_and_layer(wms,year)
            if (wrc["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year]
                or not layer["source_admissible_for_feature_info_probe"]):
                raise ValueError("SOURCE_STOP_ORIGINAL_PUBLISHED_YEAR_WMS_CAP_SHA_CHANGED")
            cap,crc=original_GET(year,CANDIDATE[year],"GetCapabilities")
            if cap is None or crc["original_SHA256"]!=FROZEN_WCS_CAP_SHA[year]:
                raise ValueError("SOURCE_STOP_BAW_YEAR_WCS2_CAPABILITIES_SHA_CHANGED")
            formats=source_native_formats(cap)
            if FROZEN_FORMAT not in formats["native_explicit_NetCDF_output_format_if_any"]:
                raise ValueError("SOURCE_STOP_NATIVE_BAW_WCS2_NETCDF4_FORMAT_NOT_SUPPORTED")
            desc,drc=original_GET(year,describe_URL(year,FROZEN_COVERAGE_IDS[year]),
                  "DescribeCoverage",FROZEN_COVERAGE_IDS[year],max_bytes=2000000)
            if desc is None or drc["original_SHA256"]!=FROZEN_DESCRIBE_SHA[year]:
                raise ValueError("SOURCE_STOP_ORIGINAL_BAW_NL_HEIGHT_DESCRIPTION_SHA_CHANGED")
            axes=source_native_description_axes(desc,FROZEN_COVERAGE_IDS[year])
            if (len(axes["source_native_envelopes"])!=1 or
                axes["source_native_envelopes"][0]["native_axisLabels"]!="Lat Long time"):
                raise ValueError("SOURCE_STOP_NATIVE_MODEL_WCS_SOURCE_LAT_LONG_TIME_AXES_CHANGED")
            yr["status"]="OFFICIAL_WMS_AND_WCS_NATIVE_SOURCE_YEAR_SHA_LOCKED"
            yr["original_WCS_source_SHA"]=crc["original_SHA256"]
            yr["original_WMS_source_SHA"]=wrc["original_WMS_xml_SHA256"]
            for month in FROZEN_MONTHS:
                ym={}
                for site in FROZEN_PUBLIC_SITES:
                    cases={}
                    for hour in FROZEN_UTC_HOURS:
                        case={"status":"SOURCE_STOP_NATIVE_WCS_OR_ARCHIVED_WMS"}
                        try:
                            wms_origin=archived_model_class_for_case(
                               archived,month,year,site,hour)
                            raw,receipt=secure_official_BAW_bounded_NC4(
                               year,month,site,hour)
                            nc= native_WCS_nearest_grid_class(raw,site)
                            agrees=source_same_time_class_agreement(
                                nc["nearest_native_WCS_class"],
                                wms_origin["archived_original_WMS_class"])
                            case={"status":"BAW_NATIVE_NC4_VS_SHA_VERIFIED_ARCHIVED_WMS_CASE_AUDITED",
                                  "original_predeclared_UTC":fixed_timestamp(year,month,hour),
                                  "original_WCS_response":receipt,
                                  "native_bounded_WCS_grid_classification":nc,
                                  "original_prior_WMS_source_class":wms_origin,
                                  "original_model_interface_class_agreement":bool(agrees)}
                        except Exception as e:
                            case["error_kind"]=type(e).__name__
                            case["error_summary"]=str(e)[:240]
                        cases[str(hour)]=case
                    ym[site]=cases
                yr["months"][month]=ym
        except Exception as e:
            yr["error_kind"]=type(e).__name__
            yr["error_summary"]=str(e)[:240]
        years[year]=yr
    data["source_year_month_site_time_results"]=years
    cases=[s for y in years.values() for months in y["months"].values()
            for h in months.values() for s in h.values()]
    admitted=[s for s in cases if s["status"]=="BAW_NATIVE_NC4_VS_SHA_VERIFIED_ARCHIVED_WMS_CASE_AUDITED"]
    cls_agree=sum(s["original_model_interface_class_agreement"] for s in admitted)
    n_wcs_nil=sum(s["native_bounded_WCS_grid_classification"]["nearest_native_WCS_class"]==
         "NC4_OFFICIAL_NIL" for s in admitted)
    n_archive_nil=sum(s["original_prior_WMS_source_class"]["archived_original_WMS_class"]==
         SENTINEL for s in admitted)
    data["source_gates"]={
      "all_24_predeclared_original_WCS2_and_archived_WMS_source_pairs_completed":len(admitted)==24,
      "n_source_pairs_read":len(admitted),
      "n_source_pairs_Nil_numeric_class_agreement":cls_agree,
      "n_source_pairs_class_disagreement":len(admitted)-cls_agree,
      "n_source_NC4_nearest_official_Nil_cases":n_wcs_nil,
      "n_original_archived_WMS_Nil_cases":n_archive_nil,
      "same_provider_two_model_interfaces_not_independent_physical_validation":True,
      "native_1e31_Nil_reason_causally_dry_ground_proven":False,
      "original_RWS_true_instrument_to_public_2011_RD_same_site_verified":False,
      "bird_GPS_tide_sun_social_Boids_behavior_effect_newly_tested":False}
    data["status"]=("ALL_24_ORIGINAL_BAW_WCS_NC4_VS_ARCHIVED_WMS_CLASSES_SOURCE_AUDITED"
       if len(admitted)==24 else "SOURCE_STOP_INCOMPLETE_24_ORIGINAL_BAW_WCS_TIMES")
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V220_BAW_24_NATIVE_WCS_VS_ARCHIVE_WMS="+json.dumps({
       "status":data["status"],"gates":data["source_gates"],
       "by_year_month_site":{year:{m:{site:{
          "status00":hrs["0"]["status"],"status12":hrs["12"]["status"],
          "wcs_nil_at00":hrs["0"].get("native_bounded_WCS_grid_classification",{}).get("nearest_native_WCS_class"),
          "wcs_nil_at12":hrs["12"].get("native_bounded_WCS_grid_classification",{}).get("nearest_native_WCS_class"),
          "WMS_nil_at00":hrs["0"].get("original_prior_WMS_source_class",{}).get("archived_original_WMS_class"),
          "WMS_nil_at12":hrs["12"].get("original_prior_WMS_source_class",{}).get("archived_original_WMS_class"),
          "model_NC4_crop_Nil_count00":hrs["0"].get("native_bounded_WCS_grid_classification",{}).get("native_grid_official_Nil_cells"),
          "model_NC4_crop_Nil_count12":hrs["12"].get("native_bounded_WCS_grid_classification",{}).get("native_grid_official_Nil_cells"),
          "error00":hrs["0"].get("error_summary"),"error12":hrs["12"].get("error_summary")}
          for site,hrs in sites.items()} for m,sites in r["months"].items()}
          for year,r in years.items()},
       "NO_independent_field_erosion_or_bird_behavior":True
    },sort_keys=True))
    return data

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-v209",required=True,type=Path)
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    run(args.original_v209,args.output)
