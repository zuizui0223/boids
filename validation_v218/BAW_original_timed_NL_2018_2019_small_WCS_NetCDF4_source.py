"""v218 original BAW year-2018/19 WCS2 narrow single-time NetCDF4 source audit.

Inputs: TWO original BAW ncHydro2 NL water level Coverages, two public 2011
WEBTICS RD reference sites; June1 noon UTC, each Lat/Long +/- 0.015 deg.
Read WCS-RENDERED subset NetCDF4 attrs, NOT publisher full-year NetCDF.
Never save raw array, full NetCDF, original RWS water level, GPS/ACC or DEM.
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
from pyproj import Transformer

from original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
    CANDIDATE,original_GET,parse_native_WCS_capabilities,describe_URL
)
from BAW_ncHydro_2018_2019_WCS_supported_formats_axes_source import (
    FROZEN_WCS_CAP_SHA,FROZEN_DESCRIBE_SHA,FROZEN_COVERAGE_IDS,
    source_native_formats,source_native_description_axes
)

FROZEN_SOURCE_RD={
   "VlielandHaven":(135280,590000),
   "Wierumergronden":(192882,614562)
}
FROZEN_YEARS=("2018","2019")
SPATIAL_HALF_WIDTH_DEG=0.015
FROZEN_FORMAT="application/x-netcdf4"
FROZEN_UTC={year:f"{year}-06-01T12:00:00.000Z" for year in FROZEN_YEARS}
HDF5_MAGIC=b"\x89HDF\r\n\x1a\n"
MAX_NATIVE_NETCDF4_BYTES=8_000_000
MAX_RAW_CELLS=10_000
BAW_WCS_NATIVE_NIL=9.999999848243207e30
OUT=Path(__file__).resolve().parent/"results/BAW_2018_2019_WCS2_NL_2site_single_time_NetCDF4_attrs_v218.json"

class DoNotFollow(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def fixed_public_wgs84(site):
    if site not in FROZEN_SOURCE_RD:
        raise ValueError("SOURCE_STOP_NONFROZEN_WEBTICS_REFERENCE_POINT")
    lon,lat=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True).transform(
        *FROZEN_SOURCE_RD[site])
    if not (4.1769<lon<7.3397 and 52.8632<lat<53.9412):
        raise ValueError("SOURCE_STOP_PUBLIC_SITE_OUTSIDE_ORIGINAL_NL_WCS_ENVELOPE")
    return lon,lat

def only_four_frozen_WCS_getcoverage_urls(year,site):
    if year not in FROZEN_COVERAGE_IDS or site not in FROZEN_SOURCE_RD:
        raise ValueError("SOURCE_STOP_NOT_PREDECLARED_2YEAR_2SITE_NATIVE_SOURCE")
    lon,lat=fixed_public_wgs84(site)
    split=urllib.parse.urlsplit(CANDIDATE[year])
    params=[
      ("service","WCS"),
      ("version","2.0.1"),
      ("request","GetCoverage"),
      ("coverageId",FROZEN_COVERAGE_IDS[year]),
      ("format",FROZEN_FORMAT),
      ("subset",f"Lat({lat-SPATIAL_HALF_WIDTH_DEG:.6f},{lat+SPATIAL_HALF_WIDTH_DEG:.6f})"),
      ("subset",f"Long({lon-SPATIAL_HALF_WIDTH_DEG:.6f},{lon+SPATIAL_HALF_WIDTH_DEG:.6f})"),
      ("subset",'time("'+FROZEN_UTC[year]+'")')
    ]
    return urllib.parse.urlunsplit((
        split.scheme,split.netloc,split.path,urllib.parse.urlencode(params),""))

def source_bounded_authorized_query(url,year,site):
    if year not in FROZEN_YEARS or site not in FROZEN_SOURCE_RD:
        return False
    return url==only_four_frozen_WCS_getcoverage_urls(year,site)

def source_GET_small_netCDF4(year,site):
    url=only_four_frozen_WCS_getcoverage_urls(year,site)
    if not source_bounded_authorized_query(url,year,site):
        raise ValueError("SOURCE_STOP_UNAUTHORIZED_NATIVE_BAW_4_SOURCE_QUERIES")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v218-BAW-original-ncHydro-WCS2-2site-single-time-netcdf4-attributes/1.0",
        "Accept":"application/x-netcdf4"})
    opener=urllib.request.build_opener(
         urllib.request.HTTPSHandler(context=ssl.create_default_context()),
         DoNotFollow())
    try:
        with opener.open(req,timeout=65) as response:
            data=response.read(MAX_NATIVE_NETCDF4_BYTES+1)
            status=response.status
            final=response.geturl()
            content_type=response.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        raise ValueError("SOURCE_STOP_ORIGINAL_NETCDF4_GETCOVERAGE_HTTP_"+str(e.code)) from e
    if status!=200 or final!=url or not data or len(data)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("SOURCE_STOP_ORIGINAL_BAW_NETCDF4_TOO_LARGE_OR_REDIRECT")
    if not data.startswith(HDF5_MAGIC):
        first=data[:16].hex()
        raise ValueError("SOURCE_STOP_WCS_GETCOVERAGE_NOT_NETCDF4_HDF5_MAGIC_"+first)
    return data,{"source_status":"SOURCE_BAW_WCS_ORIGINAL_NARROW_NETCDF4_RETRIEVED",
        "original_year":year,"original_site":site,
        "original_WCS_subset_netCDF4_SHA256":hashlib.sha256(data).hexdigest(),
        "original_WCS_subset_netCDF4_bytes":len(data),
        "original_native_content_type":content_type,
        "original_native_http_status":status,
        "native_default_TLS_CA_enabled":True,
        "source_binary_data_NOT_persisted_in_GitHub_artifacts":True}

def attr_to_safe_json(value):
    if isinstance(value,(np.ndarray,list,tuple)):
        return [attr_to_safe_json(x) for x in list(value)[:12]]
    if isinstance(value,(np.floating,float)):
        if not math.isfinite(float(value)):
            return str(value)
        return float(value)
    if isinstance(value,(np.integer,int)):
        return int(value)
    if isinstance(value,(bytes,bytearray)):
        return value.decode("utf8",errors="replace")[:180]
    return str(value)[:220]

def inspect_WCS_generated_NC4(native_binary):
    if not native_binary.startswith(HDF5_MAGIC) or len(native_binary)>MAX_NATIVE_NETCDF4_BYTES:
        raise ValueError("STOP_NOT_SMALL_NATIVE_NETCDF4_BINARY")
    with Dataset("wcs_source_memory.nc",mode="r",memory=native_binary) as ds:
        dims={k:len(v) for k,v in ds.dimensions.items()}
        if not dims or any(int(x)>30000 for x in dims.values()):
            raise ValueError("STOP_NATIVE_NC4_NO_DIMS_OR_UNBOUNDED_DIMENSION")
        candidates=[name for name in ds.variables if (
           name.lower()=="wasserstand" or "sea_surface_height" in name.lower())]
        if len(candidates)!=1:
            raise ValueError("STOP_NC4_NO_UNIQUE_NATIVE_WASSERSTAND_VARIABLE")
        var=ds.variables[candidates[0]]
        if int(np.prod(var.shape))>MAX_RAW_CELLS:
            raise ValueError("STOP_NC4_TIME_OR_SPACE_SUBSET_NOT_BOUNDED")
        for dim in var.dimensions:
            if "time" in dim.lower() and len(ds.dimensions[dim])>2:
                raise ValueError("STOP_NC4_TIME_SUBSET_RETURNED_MULTIPLE_TIMES")
        attr_names=var.ncattrs()
        attrs={name:attr_to_safe_json(var.getncattr(name))
               for name in attr_names if name in (
                "_FillValue","missing_value","units","coordinates","standard_name",
                "long_name","grid_mapping","calendar","scale_factor","add_offset")}
        # Avoid CF automatic masking/scaling, preserving original WCS subset values.
        var.set_auto_maskandscale(False)
        x=np.asarray(var[:],dtype=float)
        if x.size>MAX_RAW_CELLS:
            raise ValueError("STOP_NC4_SUBSET_UNEXPECTEDLY_TOO_LARGE")
        finite=np.isfinite(x)
        extreme=finite&(np.abs(x)>=1e6)
        plausible=finite&(np.abs(x)<=10)
        number_valid=int(np.sum(plausible))
        all_info={
         "native_generated_NetCDF4_dimension_sizes":dims,
         "native_variable_names":list(ds.variables.keys())[:50],
         "native_surface_height_variable":candidates[0],
         "native_surface_height_dtype":str(var.dtype),
         "native_surface_height_dimensions":list(var.dimensions),
         "native_surface_height_shape":[int(a) for a in var.shape],
         "native_surface_height_original_WCS_subset_attributes":attrs,
         "native_ncattrs_present_original_service_output":attr_names[:40],
         "n_subset_total_source_pixels":int(x.size),
         "n_finite_and_plausible_model_height_numeric":number_valid,
         "n_finite_extreme_sentinel_candidates":int(np.sum(extreme)),
         "n_other_finite_unresolved_source_values":int(np.sum(finite&(~extreme)&(~plausible))),
         "n_nonfinite_source_values":int(np.sum(~finite)),
         "source_plausible_model_height_median_not_validated_mNAP":round(float(np.median(x[plausible])),7)
             if number_valid else None,
         "original_WCS_nil_m_matches_NetCDF4_output__FillValue_if_present":bool(
             "_FillValue" in attrs and
             isinstance(attrs["_FillValue"],(float,int)) and
             np.isclose(attrs["_FillValue"],BAW_WCS_NATIVE_NIL,rtol=1e-6)),
         "ORIGINAL_FULL_YEAR_BAW_DOWNLOAD_NETCDF_ATTRIBUTES_NOT_DIRECTLY_READ":True,
         "original_single_time_subset_does_not_validate_GPS_or_field_wetdry":True}
        if len(ds.variables)>50:raise ValueError("STOP_NATIVE_NETCDF4_VARIABLE_LIST_TOO_LARGE")
        return all_info

def run(out=OUT):
    d={"version":"v218-authentic-narrow-WCS-NetCDF4-attrs-not-original-Baw-annual-file",
       "frozen_source_sites_2011_PUBLIC_RD":FROZEN_SOURCE_RD,
       "frozen_year_time_UTC":FROZEN_UTC,
       "frozen_spatial_halfwidth_deg":SPATIAL_HALF_WIDTH_DEG,
       "native_OGC_output_format_selected_predata":FROZEN_FORMAT,
       "prior_authentic_original_source_year_WCS2_Cap_SHA":FROZEN_WCS_CAP_SHA,
       "prior_authentic_original_source_Describe_SHA":FROZEN_DESCRIBE_SHA,
       "not_native_original_full_year_downloaded":True,
       "status":"SOURCE_STOP"}
    years={}
    for year in FROZEN_YEARS:
        y={"status":"SOURCE_STOP_YEAR_WCS_SOURCE","sites":{}}
        try:
            xml,cr=original_GET(year,CANDIDATE[year],"GetCapabilities")
            if xml is None or cr["original_SHA256"]!=FROZEN_WCS_CAP_SHA[year]:
                raise ValueError("SOURCE_STOP_YEAR_WCS2_CAP_SHA_CHANGED")
            native=source_native_formats(xml)
            if FROZEN_FORMAT not in native["native_explicit_NetCDF_output_format_if_any"]:
                raise ValueError("SOURCE_STOP_NC4_FORMAT_NOT_NATIVE_SUPPORTED")
            descr,dr=original_GET(year,describe_URL(year,FROZEN_COVERAGE_IDS[year]),
                "DescribeCoverage",FROZEN_COVERAGE_IDS[year],max_bytes=2000000)
            if descr is None or dr["original_SHA256"]!=FROZEN_DESCRIBE_SHA[year]:
                raise ValueError("SOURCE_STOP_YEAR_NL_HEIGHT_DESC_SOURCE_SHA_CHANGED")
            axes=source_native_description_axes(descr,FROZEN_COVERAGE_IDS[year])
            env=axes["source_native_envelopes"]
            if len(env)!=1 or env[0]["native_axisLabels"]!="Lat Long time":
                raise ValueError("STOP_SOURCE_WCS_YEAR_LAT_LONG_TIME_AXIS_DRIFT")
            t=axes["source_time_positions_if_any"]
            years_str=" ".join(v["source_time"] for v in t)
            if f"{year}-01-01T00:00:00.000Z" not in years_str:
                raise ValueError("SOURCE_STOP_WCS_YEAR_TIME_DOMAIN_CHANGED")
            y["original_WCS_Cap_SHA"]=cr["original_SHA256"]
            y["original_WCS_Describe_SHA"]=dr["original_SHA256"]
            y["status"]="ORIGINAL_YEAR_WCS_METADATA_SOURCE_LOCKED"
            for site in FROZEN_SOURCE_RD:
                s={"status":"SOURCE_STOP_NARROW_NETCDF4_NO_BINARY"}
                try:
                    data,receipt=source_GET_small_netCDF4(year,site)
                    values=inspect_WCS_generated_NC4(data)
                    s={"status":"WCS_PRODUCED_NATIVE_SMALL_NETCDF4_ATTRS_SOURCE_AUDITED",
                       "native_original_WCS_generated_NC4_receipt":receipt,
                       "native_WCS_generated_NC4_attrs_summary":values}
                except Exception as e:
                    s["error_kind"]=type(e).__name__
                    s["error_summary"]=str(e)[:260]
                y["sites"][site]=s
        except Exception as e:
            y["error_kind"]=type(e).__name__
            y["error_summary"]=str(e)[:230]
        years[year]=y
    d["year_site_source_results"]=years
    n_pass=sum(v["status"]=="WCS_PRODUCED_NATIVE_SMALL_NETCDF4_ATTRS_SOURCE_AUDITED"
       for yr in years.values() for v in yr["sites"].values())
    d["scientific_gates"]={
       "n_fixed_four_bounded_year_site_WCS_NetCDF4_outputs_with_attrs":n_pass,
       "all_four_NetCDF4_fixed_year_site_source_success":n_pass==4,
       "n_NetCDF4_outputs_with__FillValue_matching_prior_WCS_Nil":sum(
          v.get("native_WCS_generated_NC4_attrs_summary",{}).get(
           "original_WCS_nil_m_matches_NetCDF4_output__FillValue_if_present",False)
          for yr in years.values() for v in yr["sites"].values()),
       "underlying_original_full_annual_BAW_NetCDF__FillValue_directly_verified":False,
       "original_WCS_vertical_NHN_to_local_RWS_NAP_converted_and_calibrated":False,
       "no_native_full_NetCDF_or_bird_GPS_RWS_DEM_downloaded":True,
       "true_local_dryflat_or_sun_tide_social_Boids_effect_estimated":False}
    if n_pass==4:
        d["status"]="BAW_WCS4_BOUNDED_NETCDF4_NATIVE_ATTRIBUTES_VERIFIED_NO_ORIGINAL_ANNUAL_ATTR_CLAIM"
    else:
        d["status"]="SOURCE_STOP_INCOMPLETE_FOUR_BAW_BOUNDED_WCS_NETCDF4_ATTRS"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V218_TRUE_BAW_BOUND_NC4_SOURCE="+json.dumps({
       "status":d["status"],"gates":d["scientific_gates"],
       "by_year":{year:{site:{
         "status":val["status"],
         "mime":val.get("native_original_WCS_generated_NC4_receipt",{}).get("original_native_content_type"),
         "sha":val.get("native_original_WCS_generated_NC4_receipt",{}).get("original_WCS_subset_netCDF4_SHA256"),
         "values":val.get("native_WCS_generated_NC4_attrs_summary"),
         "error":val.get("error_summary")}
         for site,val in yr["sites"].items()} for year,yr in years.items()},
       "NO_original_yearly_BAW_Download_NetCDF_or_bird_data_read":True
    },sort_keys=True))
    return d

if __name__=="__main__":
    run()
