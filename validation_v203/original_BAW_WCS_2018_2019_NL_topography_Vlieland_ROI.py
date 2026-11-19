"""v203: genuine original BAW year 2018/19 WCS2 NL topography 10km ROI metadata only.

WCS GetCoverage downloads only bounded public reference region into RAM, reports
native raster source SHA, grid coverage and descriptive pixels, never raw raster.
This is not year-specific original field survey day or instantaneous intertidal area.
"""
from __future__ import annotations
import hashlib,io,json,math,ssl,urllib.parse,urllib.request
from pathlib import Path
import numpy as np
from rasterio.io import MemoryFile
from original_BAW_year_NL_WFS_WCS_schema_envelope import (
    CAP_SHA,WCS_IDS,tag,native_metadata_gate)
from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
    DESTINATIONS,verified_direct_baw_OGC_GET)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import NeverFollowHTTPRedirects
from true_BAW_WFS_Vlieland_2018_2019_highlow_boundary_HITS import fixed_roi

COVERS={
    "2018":"TrilaWatt_Wattflaechen__topography_inter_supratidal_2018_nl",
    "2019":"TrilaWatt_Wattflaechen__topography_inter_supratidal_2019_nl",
}
MAX_ORIGINAL_TIFF_BYTES=20_000_000
OUT=Path(__file__).resolve().parent/"results/BAW_original_WCS_2018_2019_Vlieland_inter_supratidal_topography_ROI_v203.json"

def make_native_original_WCS_ROI_request(year):
    if year not in COVERS or COVERS[year] not in WCS_IDS:
        raise ValueError("STOP_NONFROZEN_YEAR_COVERAGE")
    x0,y0,x1,y1=fixed_roi()
    fields=[
        ("service","WCS"),("version","2.0.1"),("request","GetCoverage"),
        ("coverageId",COVERS[year]),
        ("format","image/tiff"),
        ("subset",f"E({x0:.3f},{x1:.3f})"),
        ("subset",f"N({y0:.3f},{y1:.3f})")
    ]
    base=urllib.parse.urlsplit(DESTINATIONS["WCS"])
    return urllib.parse.urlunsplit((base.scheme,base.netloc,base.path,
                                   urllib.parse.urlencode(fields),""))

def fixed_native_WCS_original_request(url):
    p=urllib.parse.urlsplit(url)
    parts=urllib.parse.parse_qsl(p.query)
    d={k:v for k,v in parts if k!="subset"}
    subs=[v for k,v in parts if k=="subset"]
    roi=fixed_roi()
    expected=[f"E({roi[0]:.3f},{roi[2]:.3f})",
              f"N({roi[1]:.3f},{roi[3]:.3f})"]
    return (p.scheme=="https" and p.hostname=="coast.baw.de"
        and p.path=="/geoserver/TrilaWatt_Wattflaechen/wcs"
        and d.get("service")=="WCS" and d.get("version")=="2.0.1"
        and d.get("request")=="GetCoverage" and d.get("coverageId") in COVERS.values()
        and d.get("format")=="image/tiff" and subs==expected)

def original_secure_WCS_data_bytes(url):
    if not fixed_native_WCS_original_request(url):
        raise ValueError("STOP_WRONG_OR_UNFROZEN_WCS_ROI_2018_2019_URL")
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NeverFollowHTTPRedirects())
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v203-original-BAW-bounded-2018-2019-topography-source-only/1.0",
        "Accept":"image/tiff"})
    with op.open(req,timeout=70) as resp:
        raw=resp.read(MAX_ORIGINAL_TIFF_BYTES+1)
        status=resp.status
        final=resp.geturl()
        ct=resp.headers.get("Content-Type")
    if status!=200 or final!=url or not raw or len(raw)>MAX_ORIGINAL_TIFF_BYTES:
        raise ValueError("STOP_WCS_NATIVE_ORIGINAL_RESPONSE_TOO_LARGE_OR_HTTP")
    if not(raw[:4] in (b"II\x2a\x00",b"MM\x00\x2a",b"II\x2b\x00",b"MM\x00\x2b")):
        raise ValueError("STOP_NATIVE_WCS_RESPONSE_NOT_TIFF_OR_IS_OGC_EXCEPTION")
    return raw,{"original_WCS_GeoTIFF_bytes_SHA256":hashlib.sha256(raw).hexdigest(),
        "original_WCS_GeoTIFF_bytes_in_memory_only":len(raw),
        "original_WCS_http_status":status,
        "original_WCS_Content_Type":ct,
        "HTTPS_CA_verified_original_source":True,
        "original_raw_raster_pixels_never_persisted":True}

def parse_original_NL_grid(raw):
    with MemoryFile(raw) as mem:
        with mem.open() as tiff:
            if tiff.crs is None or tiff.crs.to_epsg()!=25832:
                raise ValueError("STOP_SOURCE_TIFF_GEO_CRS_NOT_NATIVE_25832")
            if tiff.count!=1 or tiff.width*tiff.height>1_000_000:
                raise ValueError("STOP_WCS_NOT_SINGLE_BAND_BOUNDED_PUBLIC_ROI")
            resx,resy=map(abs,tiff.res)
            if not (5<=resx<=100 and 5<=resy<=100):
                raise ValueError("STOP_NATIVE_PIXEL_RESOLUTION_OUTSIDE_PUBLISHED_TOPOGRAPHY_RANGE")
            bounds=tiff.bounds
            roi=fixed_roi()
            if not (bounds.left>=roi[0]-100 and bounds.right<=roi[2]+100
                and bounds.bottom>=roi[1]-100 and bounds.top<=roi[3]+100):
                raise ValueError("STOP_NL_GEO_SOURCE_CROP_NOT_FIXED_VLIELAND_10KM")
            array=tiff.read(1,masked=True)
            z=np.asarray(array.data)
            mask=np.ma.getmaskarray(array)
            fin=np.isfinite(z)
            extreme=fin & (~mask) & (np.abs(z)>100)
            valid=(~mask)&fin&(np.abs(z)<=100)
            count=int(np.sum(valid))
            values=np.asarray(z[valid],dtype=float)
            result={"original_CRS":tiff.crs.to_string(),
                "original_raster_width_height":[tiff.width,tiff.height],
                "original_native_resolution_m":[round(resx,7),round(resy,7)],
                "original_nodata_metadata_literal":repr(tiff.nodata),
                "original_boundingBox_EPSG25832_m":[round(v,3) for v in (
                    bounds.left,bounds.bottom,bounds.right,bounds.top)],
                "original_dtype":tiff.dtypes[0],
                "n_native_total_raster_cells":int(z.size),
                "n_native_masked_or_nonfinite_cells":int(np.sum(mask|(~fin))),
                "n_native_extreme_z_gt100m_candidate":int(np.sum(extreme)),
                "n_plausible_numeric_topography_pixels_NOT_surveyday_calibrated":count,
                "plausible_numeric_fraction":round(count/z.size,8),
                "plausible_numeric_topography_native_median":round(float(np.median(values)),7) if count else None,
                "plausible_numeric_topography_native_p05_p95":[
                    round(float(v),7) for v in np.quantile(values,[.05,.95])] if count else None,
                "source_native_grid_has_no_independent_survey_date":True,
                "native_GeoTIFF_value_datum_to_DEM_RWS_NOT_verified":True}
            transform=tiff.transform
            return result,valid,np.asarray(z,dtype=float),transform

def run(out=OUT):
    output={"analysis":"v203-original-BAW-WCS-2018-2019-NL-inter-supratidal-bounded-topo",
       "original_native_WCS_Capabilities_SHA256_frozen":CAP_SHA["WCS"],
       "source_WCS_original_endpoint":DESTINATIONS["WCS"],
       "source_published_2011_public_Vlieland10km_UTM25832":[
           round(x,3) for x in fixed_roi()],
       "source_fixed_year_coverage_ids":COVERS,
       "not_original_bird_GPS_or_native_surveyday":True,
       "status":"SOURCE_STOP"}
    info={}
    arrays={}
    try:
        rawcap,src=verified_direct_baw_OGC_GET(DESTINATIONS["WCS"],"WCS")
        if rawcap is None:raise ValueError("STOP_WCS_ORIGINAL_GETCAPABILITIES_NOT_200")
        native,names,ops=native_metadata_gate(rawcap,"WCS")
        if src["original_XML_SHA256"]!=CAP_SHA["WCS"] or "GetCoverage" not in ops:
            raise ValueError("STOP_FROZEN_ORIGINAL_BAW_WCS_SHA_OR_OPERATION_NOT_ADMITTED")
        for year in COVERS:
            request=make_native_original_WCS_ROI_request(year)
            try:
                raw,provenance=original_secure_WCS_data_bytes(request)
                stat,valid,arr,transform=parse_original_NL_grid(raw)
                info[year]={"source_status":"ORIGINAL_YEAR_BAW_NL_TOPOGRAPHY_BOUNDED_TIFF_SOURCE_ADMITTED",
                             "original_provider_source_receipt":provenance,
                             "original_native_grid_data_quality":stat}
                arrays[year]=(valid,arr,transform)
            except Exception as err:
                info[year]={"source_status":"SOURCE_STOP_ORIGINAL_NATIVE_WCS_ROI_GRID",
                    "source_error_kind":type(err).__name__,
                    "source_error_summary":str(err)[:250]}
        output["original_WCS_Capabilities_SHA256_reverified"]=src["original_XML_SHA256"]
    except Exception as err:
        output["source_error_kind"]=type(err).__name__
        output["source_error_summary"]=str(err)[:220]
    output["original_two_year_native_grid_source_qa"]=info
    source_ok=len(arrays)==2
    cross={"status":"SOURCE_STOP_ORIGINAL_TWO_YEAR_GRID_NOT_VALID_OR_IDENTICAL"}
    if source_ok:
        a,b=arrays["2018"],arrays["2019"]
        one=a[0];two=b[0]
        if one.shape==two.shape and a[2]==b[2]:
            common=one&two
            d=b[1][common]-a[1][common]
            cross={"status":"ORIGINAL_GRID_SAME_CELL_COMPARISON_METADATA",
              "n_same_native_cells_numeric_both_years":int(np.sum(common)),
              "n_2018_only_numeric_cells":int(np.sum(one&(~two))),
              "n_2019_only_numeric_cells":int(np.sum(two&(~one))),
              "2019_minus_2018_native_topo_median_candidate":round(float(np.median(d)),8) if len(d) else None,
              "2019_minus_2018_native_topo_p05_p95_candidate":[
                 round(float(x),8) for x in np.quantile(d,[.05,.95])] if len(d) else None,
              "not_a_direct_original_field_survey_change_or_intertidal_area":True}
        else:
            cross={"status":"SOURCE_STOP_TWO_NATIVE_YEAR_WCS_GRID_NOT_SAME_CELLS",
                   "same_shape":one.shape==two.shape,
                   "same_transform":a[2]==b[2]}
    output["native_same_cell_year_comparison"]=cross
    output["scientific_gates"]={
       "both_year_native_WCS_original_ROI_grid_read_and_metadata_verified":source_ok,
       "n_native_years_with_plausible_numeric_topography_support":sum(
          v.get("original_native_grid_data_quality",{}).get(
          "n_plausible_numeric_topography_pixels_NOT_surveyday_calibrated",0)>0
          for v in info.values()),
       "two_year_original_grid_cells_exact_aligned":cross["status"]=="ORIGINAL_GRID_SAME_CELL_COMPARISON_METADATA",
       "actual_annual_intertidal_area_from_native_valid_pixel_count":False,
       "true_native_vertical_NAP_and_surveyday_verified":False,
       "event_specific_tide_height_at_original_bird_GPS_verified":False,
       "tide_sun_Boids_bird_ACC_causal_effect_estimated":False}
    output["status"]="ORIGINAL_TWO_YEAR_BAW_NL_TOPOGRAPHY_ROI_GRID_SOURCE_ADMITTED_NOT_INTERTIDAL_AREA" if source_ok else "SOURCE_STOP_ORIGINAL_BAW_TWO_YEAR_NL_TOPOGRAPHY_GRID_INCOMPLETE"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V203_BAW_NL_ORIGINAL_TOPOROI="+json.dumps({
       "status":output["status"],"gates":output["scientific_gates"],
       "years":{year:{"source_status":v["source_status"],
          "data":v.get("original_native_grid_data_quality"),
          "error":v.get("source_error_summary")}
          for year,v in info.items()},
       "source_same_cell_two_year_comparison":cross,
       "not_an_original_bird_GPS_wet_dry_habitat_or_mechanism":True},sort_keys=True))
    return output

if __name__=="__main__":
    run()
