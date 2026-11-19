"""v213: bounded BAW original annual nof_valid_data_points 2018/19 NL WCS
at three prespecified public WEBTICS2011 reference stations, same fixed 1km ROI.

This is an ANNUAL model-derived valid-sample-count product, NOT original 20min
WMS Wasserstand or an independent dry-hour, inundation probability or bird-GPS
occupancy measure. No raw raster TIFF or full water-level series saved to GitHub.
"""
from __future__ import annotations
import hashlib,json,math,ssl,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
from pyproj import Transformer
from rasterio.io import MemoryFile

from original_BAW_annual_2018_2019_Kennwerte_WCS_source import (
    fetch_year_native_WCS,parse_native_original_annual_WCS,
)
from original_BAW_2018_2019_NL_validpoints_DescribeCoverage import (
    FROZEN_VALID_COUNTS,FROZEN_NATIVE_WCS_CAP_SHA,
    fetch_original_coverage_description,
    inspect_native_coverage_description
)

PUBLIC_SITE_RD={
 "VlielandHaven":(135280,590000),
 "WestTerschelling":(143870,597420),
 "Wierumergronden":(192882,614562),
}
DESCRIBE_SHA={
 "2018":"5a878c6b2920e2e7a24d608553bd4264a426227ac86867a47e86b834f492e5fb",
 "2019":"db2e57532ec6c7378dc1b7ff31fc18ea88f5820eb3290a6474d171fda9949dcf",
}
HALF_KM=500.0
MAX_NATIVE_TIFF_BYTES=5_000_000
OUT=Path(__file__).resolve().parent/"results/original_BAW_2018_2019_NL_annual_nof_valid_points_three_1km_sources_v213.json"

def frozen_public_ROI(site):
    if site not in PUBLIC_SITE_RD:
        raise ValueError("STOP_BAW_NOT_ONE_OF_FROZEN_3_PUBLIC_REFERENCE_SITES")
    e,n=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
        *PUBLIC_SITE_RD[site])
    return (e-HALF_KM,n-HALF_KM,e+HALF_KM,n+HALF_KM)

def source_annual_WCS_GetCoverage(year,site,original_verified_cap_url):
    if year not in FROZEN_VALID_COUNTS or site not in PUBLIC_SITE_RD:
        raise ValueError("STOP_ANNUAL_WCS_UNKNOWN_YEAR_OR_PUBLIC_SITE")
    cap=urllib.parse.urlsplit(original_verified_cap_url)
    if (cap.scheme!="https" or cap.hostname not in ("coast.baw.de","mdi-dienste.baw.de")
        or cap.path!=f"/geoserver/TrilaWatt_Hydrodynamik_{year}/ows"):
        raise ValueError("STOP_BAW_GETCOVERAGE_FROM_UNVERIFIED_ORIGINAL_SOURCE")
    e0,n0,e1,n1=frozen_public_ROI(site)
    args=[("service","WCS"),("version","2.0.1"),
          ("request","GetCoverage"),("coverageId",FROZEN_VALID_COUNTS[year]),
          ("format","image/tiff"),("subset",f"E({e0:.3f},{e1:.3f})"),
          ("subset",f"N({n0:.3f},{n1:.3f})")]
    return urllib.parse.urlunsplit(
        (cap.scheme,cap.netloc,cap.path,urllib.parse.urlencode(args),""))

def exact_frozen_source_WCS_query(url,year,site,cap_url):
    return url==source_annual_WCS_GetCoverage(year,site,cap_url)

class NoUnapprovedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None

def source_native_GetCoverage_bytes(url,year,site,cap_url):
    if not exact_frozen_source_WCS_query(url,year,site,cap_url):
        raise ValueError("STOP_NOT_AN_EXACT_PREDECLARED_ORIGINAL_WCS_ANNUAL_COUNT_QUERY")
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v213-BAW-original-annual-valid-count-NL-public-1km-source/1.0",
       "Accept":"image/tiff"})
    op=urllib.request.build_opener(
       urllib.request.HTTPSHandler(context=ssl.create_default_context()),
       NoUnapprovedRedirect())
    with op.open(req,timeout=65) as response:
        data=response.read(MAX_NATIVE_TIFF_BYTES+1)
        status=response.status
        final=response.geturl()
        ct=response.headers.get("Content-Type")
    if status!=200 or final!=url or not data or len(data)>MAX_NATIVE_TIFF_BYTES:
        raise ValueError("STOP_ORIGINAL_ANNUAL_NL_COUNT_WCS_NOT_HTTP200_OR_BOUNDED")
    if data[:4] not in (b"II\x2a\x00",b"MM\x00\x2a",b"II\x2b\x00",b"MM\x00\x2b"):
        raise ValueError("STOP_ORIGINAL_WCS_ANNUAL_COUNT_NOT_NATIVE_TIFF")
    return data,{"native_original_HTTP_response_SHA256":hashlib.sha256(data).hexdigest(),
                 "native_original_response_bytes":len(data),
                 "native_Content_Type":ct,
                 "native_TLS_verified":True,
                 "native_GeoTIFF_never_persisted":True}

def summarize_native_annual_count_TIFF(raw,site):
    roi=frozen_public_ROI(site)
    with MemoryFile(raw) as mf:
        with mf.open() as ds:
            if ds.crs is None or ds.crs.to_epsg()!=25832 or ds.count!=1:
                raise ValueError("STOP_NATIVE_ANNUAL_COUNT_CRS_OR_BAND_NOT_UTM25832")
            if ds.width*ds.height>250_000 or min(ds.width,ds.height)<8:
                raise ValueError("STOP_ANNUAL_COUNT_GRID_NOT_BOUNDED_PUBLIC_1KM")
            rx,ry=map(abs,ds.res)
            if not (10<=rx<=40 and 10<=ry<=40):
                raise ValueError("STOP_NATIVE_ANNUAL_COUNT_RESOLUTION_NOT_20M_CLASS")
            b=ds.bounds
            if not(b.left>=roi[0]-40 and b.right<=roi[2]+40 and
                   b.bottom>=roi[1]-40 and b.top<=roi[3]+40):
                raise ValueError("STOP_ORIGINAL_ANNUAL_COUNT_GEO_CROP_NOT_FIXED_PUBLIC_ROI")
            arr=ds.read(1,masked=True)
            v=np.asarray(arr.data,dtype=float)
            numeric=(~np.ma.getmaskarray(arr))&np.isfinite(v)
            invalid_physical=numeric & ((v<0)|(np.abs(v-np.rint(v))>0.001))
            if np.any(invalid_physical):
                raise ValueError("STOP_ORIGINAL_ANNUAL_VALID_DATA_POINTS_NONINTEGER_OR_NEGATIVE")
            values=v[numeric]
            stat={
                "native_grid_shape_height_width":[ds.height,ds.width],
                "native_resolution_m":[float(rx),float(ry)],
                "native_source_UTM25832_bounds_m":[round(q,3) for q in (
                   b.left,b.bottom,b.right,b.top)],
                "native_AnnualCoverage_dtype":ds.dtypes[0],
                "native_original_nodata_metadata_literal":repr(ds.nodata),
                "n_source_pixels_in_public_ROI":int(v.size),
                "n_original_native_numeric_valid_sample_count_pixels":int(numeric.sum()),
                "n_original_native_no_count_masked_or_nonfinite_pixels":int(v.size-numeric.sum()),
                "n_original_native_zero_annual_valid_count_pixels":int(np.sum(values==0)),
                "source_valid_count_min":int(np.min(values)) if len(values) else None,
                "source_valid_count_median":float(np.median(values)) if len(values) else None,
                "source_valid_count_p05_p95":[float(a) for a in np.quantile(values,[.05,.95])]
                     if len(values) else None,
                "source_valid_count_max":int(np.max(values)) if len(values) else None,
                "SOURCE_DOES_NOT_DEFINE_A_365DAY_WET_TIME_DENOMINATOR":True,
                "raw_time_resolved_WMS_fillvalue_and_flooding_fraction_not_verified":True}
            return stat,numeric,v,ds.transform

def run(out=OUT):
    result={"analysis":"v213-original-BAW-2018-2019-NL-annual-validpoints-20m-three-public-1km-ROI",
       "v211_two_source_success_runs":[44456179353,44456220003],
       "v212_source_success_run":44456836252,
       "frozen_original_validcount_CoverageIds":FROZEN_VALID_COUNTS,
       "frozen_2011_WEBTICS_public_RD_points":PUBLIC_SITE_RD,
       "frozen_1km_ROI_halfwidth_m":HALF_KM,
       "no_original_20min_WMS_or_animal_GPS_or_RWS_sources_retrieved":True,
       "status":"SOURCE_STOP"}
    source={}
    for year in ("2018","2019"):
        yr={"source_status":"SOURCE_STOP_ORIGINAL_ANNUAL_WCS","sites":{}}
        try:
            capXML,receipt=fetch_year_native_WCS(year)
            if receipt["native_WCS_Capabilities_XML_SHA256"]!=FROZEN_NATIVE_WCS_CAP_SHA[year]:
                raise ValueError("STOP_ANNUAL_COUNT_V211_GETCAPABILITIES_SHA_CHANGED")
            capnative=parse_native_original_annual_WCS(capXML)
            if FROZEN_VALID_COUNTS[year] not in (
                  x["original_CoverageId"] for x in capnative["native_valid_count_candidates"]):
                raise ValueError("STOP_ORIGINAL_YEAR_NOF_VALID_DATA_POINTS_NOT_AUTHORIZED")
            capurl=receipt["original_HTTP_source_chain"][-1]["native_url"]
            description,dreceipt=fetch_original_coverage_description(year,capurl)
            if dreceipt["native_DescribeCoverage_XML_SHA256"]!=DESCRIBE_SHA[year]:
                raise ValueError("STOP_ORIGINAL_V212_DESCRIBE_COVERAGE_SHA_CHANGED")
            native_meta=inspect_native_coverage_description(description,year)
            if not any(x.get("native_axisLabels")=="E N" and
               "25832" in str(x.get("native_srsName")) for x in native_meta["original_envelopes"]):
                raise ValueError("STOP_WCS_YEAR_NATIVE_AXES_NOT_25832_E_N")
            yr["source_capabilities_SHA256"]=receipt["native_WCS_Capabilities_XML_SHA256"]
            yr["source_native_DescribeCoverage_SHA256"]=dreceipt["native_DescribeCoverage_XML_SHA256"]
            yr["source_status"]="ORIGINAL_YEAR_WCS_CAP_AND_DESCRIBE_SHA_PASS"
            for site in PUBLIC_SITE_RD:
                s={"source_status":"SOURCE_STOP_NATIVE_YEAR_PUBLIC_SITE"}
                try:
                    data,http=source_native_GetCoverage_bytes(
                        source_annual_WCS_GetCoverage(year,site,capurl),
                        year,site,capurl)
                    meta,valid,values,transform=summarize_native_annual_count_TIFF(data,site)
                    s={"source_status":"ORIGINAL_BAW_ANNUAL_NL_VALIDPOINT_COUNT_TIFF_QA_ADMITTED",
                       "original_WCS_GeoTIFF_SHA_and_HTTP":http,
                       "original_native_grid_count_summary":meta,
                       "original_raw_pixel_values_NOT_published":True}
                    # arrays are needed only for same-cell annual comparison, and stay in RAM
                    s["_MEMORY_ONLY"]=(valid,values,transform)
                except Exception as err:
                    s["source_error_kind"]=type(err).__name__
                    s["source_error_summary"]=str(err)[:200]
                yr["sites"][site]=s
        except Exception as err:
            yr["source_error_kind"]=type(err).__name__
            yr["source_error_summary"]=str(err)[:220]
        source[year]=yr
    # Compare native cell coordinates in-memory, never impute or resample source counts.
    common={}
    for site in PUBLIC_SITE_RD:
        a=source["2018"]["sites"].get(site,{}).get("_MEMORY_ONLY")
        b=source["2019"]["sites"].get(site,{}).get("_MEMORY_ONLY")
        if a is None or b is None:
            common[site]={"status":"SOURCE_NOT_EVALUABLE_TWO_ORIGINAL_YEAR_GRID_COHORTS"}
            continue
        if a[0].shape!=b[0].shape or a[2]!=b[2]:
            common[site]={"status":"SOURCE_NOT_EVALUABLE_DIFFERENT_ORIGINAL_YEAR_CELL_GRIDS"}
            continue
        mask=a[0]&b[0]
        diff=b[1][mask]-a[1][mask]
        common[site]={
          "status":"ORIGINAL_YEARLY_VALID_DATA_COUNT_SAME_CELL_CANDIDATE_DELTA",
          "n_same_cell_numeric_both_years":int(mask.sum()),
          "n_only_2018_numeric":int(np.sum(a[0]&~b[0])),
          "n_only_2019_numeric":int(np.sum(~a[0]&b[0])),
          "difference_2019_minus_2018_source_count_median":float(np.median(diff)) if len(diff) else None,
          "difference_2019_minus_2018_source_count_p05_p95":
              [float(z) for z in np.quantile(diff,[.05,.95])] if len(diff) else None,
          "source_annual_count_difference_not_causal_wet_hours":True}
    for year in source:
        for site in source[year]["sites"]:
            source[year]["sites"][site].pop("_MEMORY_ONLY",None)
    result["yearly_source_site_original_NL_count_replies"]=source
    result["original_same_cell_2018_2019_annual_validcount_candidate_comparison"]=common
    n=sum(x.get("source_status")=="ORIGINAL_BAW_ANNUAL_NL_VALIDPOINT_COUNT_TIFF_QA_ADMITTED"
          for year in source.values() for x in year["sites"].values())
    result["scientific_gates"]={
       "all_six_fixed_public_site_year_20m_annual_validcount_source_rasters_retrieved":n==6,
       "n_true_original_source_GeoTIFFs_passed":n,
       "n_fixed_sites_with_exact_two_year_cell_aligned_count_data":sum(
          x["status"]=="ORIGINAL_YEARLY_VALID_DATA_COUNT_SAME_CELL_CANDIDATE_DELTA"
          for x in common.values()),
       "annual_count_denominator_baW_publication_verified":False,
       "time_resolved_20min_WMS_1e31_is_true_original_FillValue_verified":False,
       "annual_source_data_establishes_wet_time_fraction":False,
       "true_original_RWS_sensor_and_bird_GPS_cell_overlap":False,
       "tide_sun_ACC_social_Boids_new_ecological_effect":False}
    result["status"]="ORIGINAL_SIX_YEAR_SITE_BAW_ANNUAL_NL_VALIDPOINT_COUNT_RASTERS_SOURCE_AUDITED_NO_INUNDATION_INFERENCE" if n==6 else "SOURCE_STOP_ORIGINAL_YEARLY_PUBLIC_SITE_COUNT_RASTERS_NOT_ALL_ADMITTED"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V213_ANNUAL_VALIDCOUNT_SOURCE="+json.dumps({
       "status":result["status"],
       "source_gates":result["scientific_gates"],
       "year_site":{y:{site:{
          "status":v["source_status"],
          "n_valid_count_pixels":v.get("original_native_grid_count_summary",{}).get(
              "n_original_native_numeric_valid_sample_count_pixels"),
          "median_count":v.get("original_native_grid_count_summary",{}).get("source_valid_count_median"),
          "range":v.get("original_native_grid_count_summary",{}).get("source_valid_count_p05_p95"),
          "max_count":v.get("original_native_grid_count_summary",{}).get("source_valid_count_max"),
          "raw_native_source_sha":v.get("original_WCS_GeoTIFF_SHA_and_HTTP",{}).get(
              "native_original_HTTP_response_SHA256"),
          "error":v.get("source_error_summary")}
          for site,v in yr["sites"].items()} for y,yr in source.items()},
       "same_cell_count_delta":common,
       "not_raw_WMS_fillvalue_or_animal_habitat":True},sort_keys=True))
    return result

if __name__=="__main__":
    run()
