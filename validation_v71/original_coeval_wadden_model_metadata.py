"""v71 original NIOZ coeval 2010/2011 gridded hydrodynamics SOURCE ONLY.

Read published provider metadata; check original bytes MD5/size and report
variable/dimension/units + whether genuine subtidal cadence and geospatial
support exist. NO raw raster, bird GPS, individual headings or movement effects.
Source original is *model output*, NEVER mislabeled measured exposure.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import re
import tempfile
from pathlib import Path
from urllib.parse import quote,urljoin,urlparse
from urllib.request import Request,urlopen

DOI="10.25850/nioz/7b.b.n"
PACKAGE="39e92b6c-3980-4489-8fc8-27c5d1974b69"
CKAN="https://doi.nioz.nl/api/3/action/package_show?id="+PACKAGE
DATAVERSE=("https://dataverse.nioz.nl/api/datasets/:persistentId/"
           "?persistentId=doi%3A10.25850%2Fnioz%2F7b.b.n")
FILE_NAMES=("README.txt","eco_av.201001.nc","eco_av.201101.nc")
MODEL_MONTHS=("201001","201101")
MAX_BYTES=25_000_000
STUDY_SITE_POINTS={
    "schiermonnikoog_gauge_lat_lon":(53.46894,6.20291),
    "ameland_nes_gauge_lat_lon":(53.42977,5.75945)}
CANDIDATE_TIDAL_VARIABLES=("waterlevel","water_level","sea_surface",
    "elevation","zeta","ssh","water_depth","waterdepth","bathym","bedlevel",
    "wet","dry","h0","depth")
CANONICAL_LICENSE="CC0 1.0"

def _get(url,*,cap=3_000_000):
    if urlparse(url).scheme!="https":
        raise ValueError("SOURCE_STOP_V71_EXTERNAL_SOURCE_NOT_HTTPS")
    req=Request(url,headers={"User-Agent":"boids-v71-authentic-NIOZ-source-audit/1.0",
                            "Accept":"application/json, application/octet-stream, */*"})
    with urlopen(req,timeout=60) as stream:
        size=stream.headers.get("Content-Length")
        if size is not None and int(size)>cap:
            raise ValueError("SOURCE_STOP_V71_PUBLISHER_FILE_TOO_LARGE")
        b=stream.read(cap+1)
    if len(b)>cap:
        raise ValueError("SOURCE_STOP_V71_ORIGINAL_FILE_TOO_LARGE")
    return b

def _url_from_publisher(base,url):
    """No guessed opaque file identifier nor untrusted external host."""
    if not url:raise ValueError("SOURCE_STOP_V71_PUBLISHER_DOWNLOAD_URL_MISSING")
    u=urljoin(base,url)
    p=urlparse(u)
    if p.scheme!="https" or not (p.hostname=="nioz.nl" or
                                  p.hostname.endswith(".nioz.nl")):
        raise ValueError("SOURCE_STOP_V71_NON_NIOZ_PUBLISHER_URL")
    return u

def _publisher_ckan(fetch):
    data=json.loads(fetch(CKAN,cap=5_000_000))
    if not data.get("success"):
        raise ValueError("SOURCE_STOP_V71_NIOZ_CKAN_NOT_SUCCESS")
    source=data["result"]
    if source.get("id")!=PACKAGE:
        raise ValueError("SOURCE_STOP_V71_WRONG_NIOZ_DATASET_ID")
    urls={}
    for resource in source.get("resources",[]):
        name=resource.get("name") or resource.get("filename") or ""
        if name in FILE_NAMES:
            if name in urls:raise ValueError("SOURCE_STOP_V71_DUPLICATE_ORIGINAL_RESOURCE")
            urls[name]={
                "name":name,
                "size":int(resource.get("size") or 0),
                "md5":str(resource.get("hash") or "").lower(),
                "url":_url_from_publisher("https://doi.nioz.nl/",resource.get("url"))}
    return {"method":"CKAN_ORIGINAL_PROVIDER",
            "dataset_persistent_doi":DOI,
            "package_identifier":source.get("id"),
            "total_original_netcdf_monthly_resources":sum(
                (r.get("name") or "").startswith("eco_av.") and
                (r.get("name") or "").endswith(".nc")
                for r in source.get("resources",[])),
            "source_original_resources":urls}

def _publisher_dataverse(fetch):
    data=json.loads(fetch(DATAVERSE,cap=5_000_000))
    if data.get("status")!="OK" or not data.get("data"):
        raise ValueError("SOURCE_STOP_V71_NIOZ_DATAVERSE_BAD_META")
    version=data["data"]["latestVersion"]
    files=version.get("files") or []
    urls={}
    for r in files:
        f=r.get("dataFile") or {}
        name=r.get("label") or f.get("filename") or ""
        if name not in FILE_NAMES:continue
        if name in urls:raise ValueError("SOURCE_STOP_V71_DUPLICATE_DATAVERSE_FILE")
        identifier=f.get("id")
        if not identifier:raise ValueError("SOURCE_STOP_V71_MISSING_ORIGINAL_FILE_ID")
        checksum=f.get("checksum") or {}
        if checksum.get("type","MD5").upper()!="MD5":
            raise ValueError("SOURCE_STOP_V71_EXPECT_MD5_ORIGINAL_SOURCE")
        urls[name]={
            "name":name,
            "size":int(f.get("filesize") or 0),
            "md5":str(checksum.get("value") or "").lower(),
            # This is a documented, provider-declared file ID from original
            # API, never guessed or discovered by scanning unrelated hosts.
            "url":_url_from_publisher("https://dataverse.nioz.nl/",
                                     f"/api/access/datafile/{identifier}")}
    return {"method":"DATAVERSE_ORIGINAL_PROVIDER",
            "dataset_persistent_doi":DOI,
            "package_identifier":PACKAGE,
            "total_original_netcdf_monthly_resources":sum(
                (r.get("label") or "").startswith("eco_av.") and
                (r.get("label") or "").endswith(".nc") for r in files),
            "source_original_resources":urls}

def original_metadata(fetch=_get):
    failure={}
    for label,loader in (("ckan",_publisher_ckan),
                         ("dataverse",_publisher_dataverse)):
        try:
            meta=loader(fetch)
            resources=meta["source_original_resources"]
            if not all(k in resources for k in FILE_NAMES):
                raise ValueError("SOURCE_STOP_V71_ORIGINAL_FIXED_FILE_NAMES_MISSING")
            if meta["total_original_netcdf_monthly_resources"]!=36:
                raise ValueError("SOURCE_STOP_V71_36_NATIVE_MONTHS_NOT_PRESENT")
            for name in FILE_NAMES:
                f=resources[name]
                if (not re.fullmatch("[0-9a-f]{32}",f["md5"]) or
                    not (0<f["size"]<=MAX_BYTES)):
                    raise ValueError("SOURCE_STOP_V71_PROVIDER_MD5_OR_SIZE_BAD_"+name)
            return meta
        except (OSError,TimeoutError,ValueError,KeyError,TypeError) as e:
            # Retry only API transport/discovery source, not the file bytes.
            failure[label]=str(e)[:180]
    raise RuntimeError("SOURCE_STOP_V71_NO_AUTHENTIC_MONTHLY_NIOZ_MANIFEST "+str(failure))

def authenticated_provider_file(entry,fetch=_get):
    raw=fetch(entry["url"],cap=MAX_BYTES)
    if len(raw)!=entry["size"]:
        raise ValueError("SOURCE_STOP_V71_ORIGINAL_PROVIDER_SIZE_MISMATCH")
    if hashlib.md5(raw).hexdigest()!=entry["md5"]:
        raise ValueError("SOURCE_STOP_V71_ORIGINAL_PROVIDER_MD5_MISMATCH")
    return raw,{"source_file_name":entry["name"],
                "original_bytes":len(raw),
                "original_provider_MD5_verified":True,
                "publisher_original_md5":entry["md5"],
                "original_computed_sha256":hashlib.sha256(raw).hexdigest()}

def netcdf_source_structure(raw,*,source_month):
    """Inspect original netCDF header+coordinate variables, never archive pixel fields."""
    if source_month not in MODEL_MONTHS:
        raise ValueError("SOURCE_STOP_V71_ORIGINAL_MONTH_NOT_LOCKED")
    from netCDF4 import Dataset,num2date
    with tempfile.NamedTemporaryFile(suffix=".nc",mode="wb") as tmp:
        tmp.write(raw);tmp.flush()
        with Dataset(tmp.name,"r") as ds:
            dims={name:len(dim) for name,dim in ds.dimensions.items()}
            descriptions={}
            for name,var in ds.variables.items():
                descriptions[name]={
                    "dimensions":list(var.dimensions),
                    "dtype":str(var.dtype),
                    "units":str(getattr(var,"units",""))[:90],
                    "standard_name":str(getattr(var,"standard_name",""))[:90],
                    "long_name":str(getattr(var,"long_name",""))[:130]}
            time_candidates=[]
            for name,var in ds.variables.items():
                units=str(getattr(var,"units",""))
                is_time=("time" in name.lower() or
                    "time" in str(getattr(var,"standard_name","")).lower())
                if not is_time:
                    continue
                if var.ndim!=1 or var.size>100_000:
                    continue
                if "since" not in units:
                    time_candidates.append({"name":name,"n":var.size,
                        "units":units[:90],"source_delta_seconds_median":None})
                    continue
                vals=var[:]
                import numpy as np
                arr=np.asarray(vals,dtype=float)
                if arr.size>=2 and np.isfinite(arr).all():
                    dates=num2date(arr[:],units,
                        calendar=getattr(var,"calendar","standard"),
                        only_use_cftime_datetimes=False,
                        only_use_python_datetimes=True)
                    secs=np.asarray([(d-dates[0]).total_seconds()
                                     for d in dates],dtype=float)
                    step=np.diff(secs)
                    median_step=float(np.median(step))
                    consecutive=bool(np.all(step>0))
                else:
                    median_step=None;consecutive=False
                time_candidates.append({"name":name,
                    "n":int(var.size),"units":units[:90],
                    "source_delta_seconds_median":median_step,
                    "strictly_increasing":consecutive})
            temporally_ok=any(
                c["n"]>=24 and c.get("strictly_increasing") and
                c.get("source_delta_seconds_median") is not None and
                0<c["source_delta_seconds_median"]<=3600
                for c in time_candidates)
            physics_vars=[]
            for name,info in descriptions.items():
                detail=(name+" "+info["standard_name"]+" "+info["long_name"]).lower()
                if any(x in detail for x in CANDIDATE_TIDAL_VARIABLES):
                    physics_vars.append(name)
            # Do not guess the CRS. Claim geographic coverage only if two
            # separately named native latitude and longitude coordinate vars
            # with trustworthy degree unit strings exist and clearly bound.
            geographic_candidates={}
            for name,var in ds.variables.items():
                if not (
                    name.lower() in ("lat","latitude","lon","longitude") or
                    str(getattr(var,"standard_name","")) in ("latitude","longitude")
                ):continue
                if var.size>1_000_000 or var.ndim not in (1,2):continue
                unit=str(getattr(var,"units","")).lower()
                if not ("degree" in unit):
                    continue
                import numpy as np
                a=np.asarray(var[:],dtype=float)
                a=a[np.isfinite(a)]
                if not a.size:continue
                geographic_candidates[name]={"units":unit[:90],
                    "minimum":float(a.min()),"maximum":float(a.max()),
                    "n_finite":int(len(a))}
            latitude=next((d for n,d in geographic_candidates.items()
                           if "lat" in n.lower()),None)
            longitude=next((d for n,d in geographic_candidates.items()
                            if "lon" in n.lower()),None)
            bbox_ok=(latitude is not None and longitude is not None and
                     all(latitude["minimum"]<=lat<=latitude["maximum"]
                         and longitude["minimum"]<=lon<=longitude["maximum"]
                         for lat,lon in STUDY_SITE_POINTS.values()))
            return {
                "source_month":source_month,
                "file_original_netcdf_dimensions":dims,
                "native_variable_headers_not_array_values":descriptions,
                "original_numeric_time_coordinate_candidates":time_candidates,
                "source_temporal_within_tide_resolution_supported":temporally_ok,
                "original_marine_hydrodynamic_variable_names_candidates":physics_vars,
                "native_degree_lat_lon_coordinate_aggregate_extent":geographic_candidates,
                "both_wadden_site_reference_points_inside_native_lat_lon_bounding_box":bbox_ok,
                "spatial_source_claim_requires_actual_original_CRS_and_nap_datum":True,
                "no_wave_model_OR_bathy_cells_or_2010_bird_GPS_read_or_exported":True}

def run(output):
    # One strictly fixed January sample in each original GPS cohort.
    meta=original_metadata()
    safe={"analysis":"V71_NIOZ_COEVAL_ORIGINAL_MODEL_NETCDF_SOURCE_ONLY",
          "original_public_doi":DOI,
          "source_hydro_is_200m_NUMERICAL_HINDCAST_NOT_FIELD_MEASURED":True,
          "publisher_manifest_method":meta["method"],
          "publisher_total_monthly_netcdf_resources":
              meta["total_original_netcdf_monthly_resources"],
          "original_files":{}}
    for name in FILE_NAMES:
        raw,receipt=authenticated_provider_file(
            meta["source_original_resources"][name])
        if name.endswith(".nc"):
            month=name.split(".")[1]
            receipt["original_netcdf_source_structure"]=netcdf_source_structure(
                raw,source_month=month)
        else:
            # Safe receipt only: README raw text not published.
            receipt["README_original_bytes_verified_only"]=True
        safe["original_files"][name]=receipt
        print("V71_ORIGINAL_NIOZ_PUBLISHER_RETRIEVAL "+json.dumps({
            "name":name,"original_provider_MD5_verified":True,
            "source_sha256":receipt["original_computed_sha256"],
            "original_bytes":receipt["original_bytes"]},sort_keys=True),flush=True)
    candidate=[safe["original_files"][name]["original_netcdf_source_structure"]
               for name in FILE_NAMES if name.endswith(".nc")]
    time_ok=all(x["source_temporal_within_tide_resolution_supported"]
                for x in candidate)
    physics_ok=all(bool(x["original_marine_hydrodynamic_variable_names_candidates"])
                   for x in candidate)
    extent_ok=all(x["both_wadden_site_reference_points_inside_native_lat_lon_bounding_box"]
                  for x in candidate)
    safe["predeclared_source_temporal_two_month_support"]=time_ok
    safe["predeclared_physical_variable_metadata_support"]=physics_ok
    safe["predeclared_native_geographic_point_bbox_support"]=extent_ok
    safe["admission"]=(
        "SOURCE_CANDIDATE_ONLY_REQUIRES_GAUGE_AND_NAP_PHYSICAL_CROSSCALIBRATION"
        if time_ok and physics_ok and extent_ok
        else "NOT_ADMITTED_SOURCE_TIME_VARIABLE_OR_VERIFIED_GEOSPATIAL_SUPPORT")
    safe["no_original_bird_trajectory_outcome_or_usable_exposed_area_estimated"]=True
    safe["WadGrid_2009_2014_POST_2010_survey_leakage_unresolved"]=True
    target=Path(output);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(safe,sort_keys=True,indent=2)+"\n")
    print("V71_ORIGINAL_NIOZ_SOURCE_GATE "+json.dumps({
        "official_provider_method":meta["method"],
        "original_native_netcdf_months":meta["total_original_netcdf_monthly_resources"],
        "within_tide_time_support":time_ok,"physics_variable_metadata":physics_ok,
        "native_lat_lon_bounds_support":extent_ok,
        "admission":safe["admission"]},sort_keys=True),flush=True)
    print("V71_ORIGINAL_COEVAL_HYDRO_SOURCE_AUDIT_COMPLETED",flush=True)
    return safe

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    arg=ap.parse_args()
    run(arg.output)
