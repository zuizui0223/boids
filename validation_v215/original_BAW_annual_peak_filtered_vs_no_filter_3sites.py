"""v215: original 2018/2019 BAW ANNUAL sea_surface_height_peak masked vs no_filter.
Three frozen public WEBTICS reference 1km squares, genuine 20m WCS TIFFs.
This is NOT the separate 500m/20min WMS sea_surface_height_2d nor bird habitat.
"""
from __future__ import annotations
import json,hashlib,ssl,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
from rasterio.io import MemoryFile
from original_BAW_annual_2018_2019_Kennwerte_WCS_source import (
    fetch_year_native_WCS,parse_native_original_annual_WCS)
from original_BAW_2018_2019_NL_validpoints_DescribeCoverage import FROZEN_NATIVE_WCS_CAP_SHA
from original_BAW_annual_validpoints_2018_2019_three_public_sites import PUBLIC_SITE_RD,frozen_public_ROI

FROZEN={
 "2018":{
  "filtered":"TrilaWatt_Hydrodynamik_2018__sea_surface_height_peak_2018_nl",
  "no_filter":"TrilaWatt_Hydrodynamik_2018__sea_surface_height_peak_2018_nl_no_filter"},
 "2019":{
  "filtered":"TrilaWatt_Hydrodynamik_2019__sea_surface_height_peak_2019_nl",
  "no_filter":"TrilaWatt_Hydrodynamik_2019__sea_surface_height_peak_2019_nl_no_filter"},
}
MAX_BYTES=5_000_000
OUT=Path(__file__).resolve().parent/"results/BAW_original_2018_2019_annual_peak_filtered_vs_no_filter_3sites_v215.json"
class NoUnapprovedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def frozen_source_coverage_url(year,site,variant,cap_url):
    if year not in FROZEN or site not in PUBLIC_SITE_RD or variant not in FROZEN[year]:
        raise ValueError("STOP_UNFROZEN_YEAR_SITE_OR_FILTER")
    p=urllib.parse.urlsplit(cap_url)
    if p.scheme!="https" or p.hostname not in ("coast.baw.de","mdi-dienste.baw.de") or (
         p.path!=f"/geoserver/TrilaWatt_Hydrodynamik_{year}/ows"):
        raise ValueError("STOP_NOT_AUTHENTIC_ORIGINAL_ANNUAL_YEAR_ENDPOINT")
    x0,y0,x1,y1=frozen_public_ROI(site)
    args=[("service","WCS"),("version","2.0.1"),("request","GetCoverage"),
          ("coverageId",FROZEN[year][variant]),("format","image/tiff"),
          ("subset",f"E({x0:.3f},{x1:.3f})"),
          ("subset",f"N({y0:.3f},{y1:.3f})")]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(args),""))

def original_source_GET(year,site,variant,cap_url):
    url=frozen_source_coverage_url(year,site,variant,cap_url)
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NoUnapprovedRedirect())
    req=urllib.request.Request(url,method="GET",headers={
      "User-Agent":"boids-v215-original-BAW-annual-peak-two-variants-source-only/1.0",
      "Accept":"image/tiff"})
    with op.open(req,timeout=65) as r:
        raw=r.read(MAX_BYTES+1)
        status=r.status
        final=r.geturl()
        ct=r.headers.get("Content-Type")
    if status!=200 or final!=url or not raw or len(raw)>MAX_BYTES:
        raise ValueError("STOP_NATIVE_ANNUAL_PEAK_HTTP_OR_UNBOUNDED_TIFF")
    if raw[:4] not in (b"II\x2a\x00",b"MM\x00\x2a",b"II\x2b\x00",b"MM\x00\x2b"):
        raise ValueError("STOP_ORIGINAL_WCS_IS_NOT_TRUE_TIFF")
    return raw,{"original_native_TIFF_SHA256":hashlib.sha256(raw).hexdigest(),
       "original_response_bytes":len(raw),"native_content_type":ct,
       "original_raw_TIFF_not_persisted":True}

def native_annual_peak_mask(raw,site):
    box=frozen_public_ROI(site)
    with MemoryFile(raw) as mem:
        with mem.open() as tif:
            if tif.crs is None or tif.crs.to_epsg()!=25832 or tif.count!=1:
                raise ValueError("STOP_ORIGINAL_ANNUAL_PEAK_CRS_OR_BAND_NOT_NATIVE")
            if tif.width*tif.height>250000 or min(tif.width,tif.height)<8:
                raise ValueError("STOP_UNBOUNDED_ANNUAL_PEAK_GRID")
            rx,ry=map(abs,tif.res)
            if not 10<=rx<=40 or not 10<=ry<=40:
                raise ValueError("STOP_NOT_BAW_YEARLY_20M_CLASS_RESOLUTION")
            b=tif.bounds
            if not (b.left>=box[0]-40 and b.right<=box[2]+40 and
                    b.bottom>=box[1]-40 and b.top<=box[3]+40):
                raise ValueError("STOP_ORIGINAL_PEAK_SITE_ROI_MISMATCH")
            arr=tif.read(1,masked=True)
            vals=np.asarray(arr.data,dtype=float)
            nodata=np.ma.getmaskarray(arr)
            mask=(~nodata)&np.isfinite(vals)&(np.abs(vals)<=100)
            extreme=(~nodata)&np.isfinite(vals)&(np.abs(vals)>100)
            finite=vals[mask]
            meta={"original_CRS":tif.crs.to_string(),
              "original_grid_height_width":[int(tif.height),int(tif.width)],
              "source_resolution_m":[float(rx),float(ry)],
              "original_nodata_literal":repr(tif.nodata),
              "n_original_pixel_total":int(vals.size),
              "n_original_numeric_candidate_pixels":int(mask.sum()),
              "n_original_masked_or_nonfinite_pixels":int(np.sum(nodata|~np.isfinite(vals))),
              "n_source_extreme_uninterpretable_pixels":int(extreme.sum()),
              "source_numeric_annual_peak_p05_p50_p95_not_units_calibrated":[
                  round(float(z),7) for z in np.quantile(finite,[.05,.5,.95])
                  ] if len(finite) else None,
              "not_an_independent_actual_model_drycell_or_field_habitat":True}
            return mask,tif.transform,meta

def compare_masks(normal,unfiltered):
    a,aa,_=normal
    b,bb,_=unfiltered
    if a.shape!=b.shape or aa!=bb:
        raise ValueError("STOP_FILTERED_NOFILTER_NATIVE_CELL_ALIGNMENT_INVALID")
    out={"original_source_pixel_count":int(a.size),
        "n_numeric_both_variants":int(np.sum(a&b)),
        "n_numeric_filtered_only":int(np.sum(a&~b)),
        "n_numeric_no_filter_only":int(np.sum(~a&b)),
        "n_numeric_neither_variant":int(np.sum(~a&~b)),
        "no_filter_minus_filtered_numeric_source_pixel_n":int(b.sum()-a.sum()),
        "annual_product_only_not_model_20min_WMS_missing_reason":True}
    if sum(out[k] for k in ("n_numeric_both_variants","n_numeric_filtered_only",
        "n_numeric_no_filter_only","n_numeric_neither_variant"))!=a.size:
        raise ValueError("STOP_ORIGINAL_MASK_CROSS_PRODUCT_NOT_EXHAUSTIVE")
    return out

def run(out=OUT):
    d={"version":"v215-original-Baw-annual-sea_surface_height_peak-filter-vs-no_filter",
       "fixed_yearly_original_CoverageIds":FROZEN,
       "frozen_public_WEBTICS_2011_RD_1km_sites":PUBLIC_SITE_RD,
       "pinned_v211_original_WCS_year_SHA":FROZEN_NATIVE_WCS_CAP_SHA,
       "no_2018_2019_bird_GPS_ACC_or_RWS_or_original_waterlevel_timeseries":True,
       "status":"SOURCE_STOP"}
    years={}
    for year in ("2018","2019"):
        yr={"status":"SOURCE_STOP_ORIGINAL_WCS_YEAR","sites":{}}
        try:
            rawcap,original=fetch_year_native_WCS(year)
            if original["native_WCS_Capabilities_XML_SHA256"]!=FROZEN_NATIVE_WCS_CAP_SHA[year]:
                raise ValueError("STOP_ORIGINAL_YEAR_WCS_CAPABILITIES_SHA_CHANGED")
            catalogue=parse_native_original_annual_WCS(rawcap)
            known=set(catalogue["original_names_sample_cap200"])
            if any(name not in known for name in FROZEN[year].values()):
                raise ValueError("STOP_ANNUAL_NATIVE_WCS_SOURCE_LAYER_NOT_LISTED")
            original_url=original["original_HTTP_source_chain"][-1]["native_url"]
            yr["status"]="ORIGINAL_ANNUAL_YEAR_CATALOGUE_VERIFIED"
            yr["source_cap_sha"]=original["native_WCS_Capabilities_XML_SHA256"]
            for site in PUBLIC_SITE_RD:
                row={"status":"SOURCE_STOP_ORIGINAL_SITE_PAIR","variants":{}}
                memory={}
                for variant in ("filtered","no_filter"):
                    try:
                        raw,receipt=original_source_GET(year,site,variant,original_url)
                        mask,transform,metadata=native_annual_peak_mask(raw,site)
                        memory[variant]=(mask,transform,metadata)
                        row["variants"][variant]={
                           "source_status":"AUTHENTIC_YEARLY_NATIVE_PEAK_TIFF_READ",
                           "native_original_response_SHA256":receipt["original_native_TIFF_SHA256"],
                           "native_source_QA":metadata}
                    except Exception as exc:
                        row["variants"][variant]={"source_status":"SOURCE_STOP_VARIANT",
                            "error_type":type(exc).__name__,
                            "error_summary":str(exc)[:180]}
                if len(memory)==2:
                    try:
                        row["native_filtered_vs_no_filter_source_masks"]=compare_masks(
                            memory["filtered"],memory["no_filter"])
                        row["status"]="ORIGINAL_ANNUAL_TWO_FILTER_VARIANTS_SOURCE_AUDITED"
                    except Exception as exc:
                        row["error_type"]=type(exc).__name__
                        row["error_summary"]=str(exc)[:180]
                yr["sites"][site]=row
        except Exception as exc:
            yr["error_type"]=type(exc).__name__
            yr["error_summary"]=str(exc)[:200]
        years[year]=yr
    d["original_year_site_results"]=years
    n=sum(row.get("status")=="ORIGINAL_ANNUAL_TWO_FILTER_VARIANTS_SOURCE_AUDITED"
          for year in years.values() for row in year["sites"].values())
    d["scientific_gates"]={
       "all_six_original_year_site_filtered_and_no_filter_native_raster_pairs_admitted":n==6,
       "n_year_site_original_source_pairs_success":n,
       "n_source_year_site_pairs_no_filter_adds_native_pixels":sum(
          row.get("native_filtered_vs_no_filter_source_masks",{}).get(
              "n_numeric_no_filter_only",0)>0
          for year in years.values() for row in year["sites"].values()),
       "filtered_vs_no_filter_annual_raster_gives_raw_20min_WMS_fillvalue":False,
       "native_yearly_peak_values_calibrated_true_mNAP_height":False,
       "bird_GPS_tide_sun_social_Boids_causal_behavior_estimated":False}
    if n==6:
        d["status"]="ORIGINAL_SIX_YEAR_SITE_ANNUAL_PEAK_FILTERED_NOFILTER_NATIVE_MASK_COMPARISONS_SOURCE_AUDITED"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V215_BAW_ORIGINAL_ANNUAL_FILTERED_NOFILTER="+json.dumps({
       "status":d["status"],"gates":d["scientific_gates"],
       "sites":{y:{s:{"status":r["status"],
          "filtered":r.get("variants",{}).get("filtered",{}).get("native_source_QA",{}).get(
             "n_original_numeric_candidate_pixels"),
          "no_filter":r.get("variants",{}).get("no_filter",{}).get("native_source_QA",{}).get(
             "n_original_numeric_candidate_pixels"),
          "overlap":r.get("native_filtered_vs_no_filter_source_masks"),
          "errors":[x.get("error_summary") for x in r.get("variants",{}).values() if x.get("error_summary")]}
          for s,r in yr["sites"].items()} for y,yr in years.items()},
       "this_is_annual_model_filter_not_timed_WMS_or_animal_habitat":True
    },sort_keys=True))
    return d
if __name__=="__main__":
    run()
