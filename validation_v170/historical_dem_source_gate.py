"""v170: authentic historical Vlie/Vlieland Vaklodingen survey source gate.

Scientific need: link real bird GPS locations and sea-level NAP to historical
coastal bathymetry WITHOUT silently assigning current or another bay's
20m bathymetric surface to original 2018/2019 Vlieland birds.

Source candidates: Rijkswaterstaat / Deltares OpenEarth public
'kustgenese2/bathymetrie/Vaklodingen' original downloadable NetCDFs:
  20160912_vaklodingen.nc (2016 historical candidate)
  20190712_vaklodingen.nc (2019 historical candidate)
FILENAME YEAR DOES NOT GUARANTEE per-cell survey date. It must be verified
in the NetCDF variable/source metadata and footprint.

This is SOURCE-ONLY, pre-outcome, no selection by bird behavior, no raw
GPS/tide values or gridded DEM redistributed. A file that downloads but
does not cover Vlieland or lacks valid NAP/CRS/source dating is STOP, NOT
empirical proof of access at the birds' foraging patches.
"""
from __future__ import annotations
import argparse,hashlib,io,json,math,os,re,urllib.request
from pathlib import Path
from collections import Counter
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_v170/results/original_vlie_2016_2019_vaklodingen_source_gate.json"
BASE="https://rwsprojectarchief.openearth.nl/downloads/kustgenese2/bathymetrie/Vaklodingen/"
FILES=("20160912_vaklodingen.nc","20190712_vaklodingen.nc")
MAX_FILE_BYTES=14_000_000
RWS_GAUGE_APPROX_LONLAT=(5.098,53.298)
# This coarse public bounding box is for metadata inspection ONLY.
# It does not substitute for actual tagged-bird GPS point footprints.
EXPLORATORY_VLIE_REGION_LL=(4.70,53.15,5.30,53.53)
TARGET_GRID_RDN=(120000,150000,575000,615000)
EXPECTED_SOURCE_RELEASE_YEARS=(2016,2019)
MIN_SUITABLE_REAL_BATHY_CELLS=50

def acquire_bytes(url,max_bytes=MAX_FILE_BYTES):
    req=urllib.request.Request(url,headers={
        "User-Agent":"OpenScienceBoidsResearch/1.0 (noncommercial original-source attribution Rijkswaterstaat)",
        "Accept":"application/x-netcdf,application/octet-stream,*/*"
    })
    with urllib.request.urlopen(req,timeout=60) as r:
        source_url=r.geturl()
        content=r.read(max_bytes+1)
        content_type=r.headers.get("Content-Type","")
    if len(content)>max_bytes:raise ValueError("STOP_2016_SURVEY_DOWNLOAD_EXCEEDS_MAX_BYTES")
    if len(content)<10000:raise ValueError("STOP_NO_NETCDF_SOURCE_BINARY")
    if not (content[:3]==b"CDF" or content[:4]==b"\x89HDF"):
        raise ValueError("STOP_SOURCE_RESPONSE_IS_NOT_A_NETCDF")
    return content,{"original_source_requested_url":url,
                    "source_response_resolved_url":source_url,
                    "original_native_binary_SHA256":hashlib.sha256(content).hexdigest(),
                    "original_native_binary_bytes":len(content),
                    "source_content_type":content_type}

def inspect_original_netcdf(raw,prov,expected_year):
    from netCDF4 import Dataset,num2date
    import pyproj
    with Dataset("source.nc",memory=raw) as nc:
        attrs={name:str(nc.getncattr(name))[:400] for name in nc.ncattrs()
               if name.lower() in ("title","summary","source","history","institution","references",
                                  "geospatial_vertical_datum","geospatial_vertical_units",
                                  "crs","projection","time_coverage_start","time_coverage_end",
                                  "projectionname","datum","date_created","date_modified",
                                  "description")}
        dims={name:len(dim) for name,dim in nc.dimensions.items()}
        fieldnames=sorted(nc.variables)
        variables={}
        for name,var in nc.variables.items():
            va={k:str(var.getncattr(k))[:400] for k in var.ncattrs()
                if k.lower() in ("units","long_name","standard_name","_fillvalue","grid_mapping",
                                 "coordinates","epsg_code","proj4_params","vertical_datum",
                                 "datum","positive","flag_meanings")}
            variables[name]={"dims":list(var.dimensions),"dtype":str(var.dtype),"attributes":va}
        # Robust inspect several projected coordinate naming systems.
        coord={}
        for name in ("x","y","lon","lat","longitude","latitude","time","z","depth","height","altitude","isource"):
            if name not in nc.variables:continue
            v=nc.variables[name]
            info={"dims":list(v.dimensions),"size":int(v.size)}
            # For larger data, don't export arrays, only min/max/count.
            if v.ndim<=1 or (v.ndim>=2 and v.size<1_500_000):
                try:
                    values=np.ma.asarray(v[:])
                    compressed=values.compressed()
                    if compressed.size:
                        finite=compressed[np.isfinite(compressed)]
                        if finite.size:
                            info["finite_original_values"]=int(len(finite))
                            info["min"]=float(np.min(finite))
                            info["max"]=float(np.max(finite))
                        if name in ("x","y","time") and values.ndim==1 and values.size<100:
                            info["first_source_values"]=[float(x) for x in compressed[:10]]
                except (RuntimeError,ValueError,TypeError,IndexError) as e:
                    info["read_probe_error_class"]=type(e).__name__
            coord[name]=info
        rd_extent=None
        if "x" in coord and "y" in coord and all(k in coord["x"] for k in ("min","max")) and all(k in coord["y"] for k in ("min","max")):
            x=coord["x"];y=coord["y"]
            rd_extent=[x["min"],y["min"],x["max"],y["max"]]
        # Source's RD New coordinate system to WGS84 bounding projection.
        lonlat_bounds=None
        if rd_extent:
            t=pyproj.Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True)
            corners=[t.transform(px,py) for px in (rd_extent[0],rd_extent[2])
                                           for py in (rd_extent[1],rd_extent[3])]
            lonlat_bounds=[min(a for a,b in corners),min(b for a,b in corners),
                           max(a for a,b in corners),max(b for a,b in corners)]
        # Source 2016 date cannot be established simply by URL filename.
        year_mentions=[y for y in range(2000,2027)
                       if str(y) in str(attrs)+str(variables)+str(coord)]
        source_evidence={
            "filename_suggested_year":expected_year,
            "native_source_attribute_year_mentions":year_mentions,
            "per_cell_original_survey_date":"NOT_VERIFIED_FROM_FILENAME_ONLY",
            "native_NAP_vertical_datum_strict_verification":"NOT_VERIFIED_FROM_FILENAME_ONLY",
            "projected_original_RD_New_bounds_m":rd_extent,
            "projected_original_WGS84_lonlat_bounds":lonlat_bounds,
            "source_extent_intersects_broad_Vlieland_region":bool(lonlat_bounds and not (
                lonlat_bounds[2]<EXPLORATORY_VLIE_REGION_LL[0] or
                lonlat_bounds[0]>EXPLORATORY_VLIE_REGION_LL[2] or
                lonlat_bounds[3]<EXPLORATORY_VLIE_REGION_LL[1] or
                lonlat_bounds[1]>EXPLORATORY_VLIE_REGION_LL[3]
            )),
            "source_extent_contains_approx_harbor_point":bool(lonlat_bounds and
                lonlat_bounds[0]<=RWS_GAUGE_APPROX_LONLAT[0]<=lonlat_bounds[2] and
                lonlat_bounds[1]<=RWS_GAUGE_APPROX_LONLAT[1]<=lonlat_bounds[3]),
            "source_exact_tagged_bird_GPS_inside_footprint":"NOT_YET_TESTED",
        }
    return {**prov,"original_netcdf_title_and_provenance_attributes":attrs,
            "original_netcdf_dimensions":dims,
            "original_netcdf_original_variable_names":fieldnames,
            "original_netcdf_variables_schema":variables,
            "original_netcdf_coordinate_metadata":coord,
            "source_geographic_coverage_and_admission":source_evidence}

def run():
    result={
        "version":"v170_original_2016_2019_vlie_vaklodingen_netcdf_source_admission_1",
        "source_owner":"Rijkswaterstaat / Deltares OpenEarth",
        "data_access":"Official public archival native NetCDF, not current merged DEM",
        "year_in_filename_not_a_true_dem_cell_time_or_datum":True,
        "SOURCE_scope_is_not_bird_acc_behavior_model":True,
        "genuine_historical_candidate_downloads":[],
        "suitability_for_GPS_local_mudflat_water_depth":"SOURCE_GATE_PENDING"
    }
    for year,file in zip(EXPECTED_SOURCE_RELEASE_YEARS,FILES):
        raw,prov=acquire_bytes(BASE+file)
        check=inspect_original_netcdf(raw,prov,year)
        result["genuine_historical_candidate_downloads"].append(check)
    if len(result["genuine_historical_candidate_downloads"])!=2:
        raise AssertionError("Missing one historical survey release")
    if not all(x["source_geographic_coverage_and_admission"]["source_extent_intersects_broad_Vlieland_region"]
               for x in result["genuine_historical_candidate_downloads"]):
        result["suitability_for_GPS_local_mudflat_water_depth"]="SOURCE_STOP_ARCHIVAL_SURVEY_FOOTPRINT_NOT_VLIELAND"
    else:
        result["suitability_for_GPS_local_mudflat_water_depth"]="SOURCE_ONLY_REGION_MATCH_GPS_AND_NAP_STILL_UNVERIFIED"
    result["not_a_verified_tidalflat_exposure_or_causal_tide_solar_effect"]=True
    return result

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=run()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        old=json.loads(OUT.read_text())
        if result!=old:
            raise AssertionError("Native historical NetCDF source byte checksums/metadata changed")
        print("V170_HISTORICAL_ORIGINAL_VLIE_NATIVE_NETCDF_SOURCE_REPLAY_PASS")
    else:
        OUT.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
        print("V170_SOURCE_AUDIT_START")
        print(json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V170_SOURCE_AUDIT_END")
    print("V170_SOURCE_SCOPE="+json.dumps([
        {"source_native_SHA256":f["original_native_binary_SHA256"],
         "source_year":f["source_geographic_coverage_and_admission"]["filename_suggested_year"],
         "source_size":f["original_native_binary_bytes"],
         "bounds_RD":f["source_geographic_coverage_and_admission"]["projected_original_RD_New_bounds_m"],
         "bounds_WGS84":f["source_geographic_coverage_and_admission"]["projected_original_WGS84_lonlat_bounds"],
         "intersects_Vlieland":f["source_geographic_coverage_and_admission"]["source_extent_intersects_broad_Vlieland_region"]}
        for f in result["genuine_historical_candidate_downloads"]],sort_keys=True))

if __name__=="__main__":
    main()
