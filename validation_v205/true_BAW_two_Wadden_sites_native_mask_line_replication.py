"""v205 original BAW 2018/19 WCS-mask and WFS-boundary pattern replication
at TWO independently published WEBTICS public reference sites, in-source only.

Both target 10km squares and original 2018/19 source layers are frozen in
docs/V205 before querying. No bird GPS or field erosion claims. Raw WFS
coordinates and native WCS pixel values are NEVER written to source artifacts.
"""
from __future__ import annotations
import hashlib
import json
import math
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
from pyproj import Transformer
from scipy.ndimage import distance_transform_edt
from rasterio.features import rasterize
from rasterio.io import MemoryFile
from shapely.geometry import box,shape

from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
    DESTINATIONS, verified_direct_baw_OGC_GET
)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import (
    NeverFollowHTTPRedirects
)
from original_BAW_year_NL_WFS_WCS_schema_envelope import (
    CAP_SHA, WFS_TYPES, WCS_IDS, native_metadata_gate
)
from true_BAW_WFS_Vlieland_2018_2019_highlow_boundary_HITS import (
    SOURCE_WFS_NATIVE_CRS,
    parse_original_native_hits,
)
from authentic_BAW_mask_turnover_near_annual_tide_lines import (
    semantic_original_geojson_fingerprint,
    canonical_classes,
    bin_source_masks,
    risk_ratio_near_far,
    quadrants,
)

# Independent 2011 WEBTICS study station reference coordinates, NOT native
# 2018/19 station instrument positions and NOT bird GPS tracks.
PUBLIC_ROI_RD = {
    "WestTerschelling":(143870,597420),
    "Wierumergronden":(192882,614562),
}
FROZEN_YEARS=("2018","2019")
FOUR_WFS_NAMES=tuple(
    f"TrilaWatt_Wattflaechen:{level}_water_boundary_{year}_nl"
    for year in FROZEN_YEARS for level in ("high","low")
)
TWO_WCS_IDS={
    year:f"TrilaWatt_Wattflaechen__topography_inter_supratidal_{year}_nl"
    for year in FROZEN_YEARS
}
MAX_ORIGINAL_WCS_TIFF=20_000_000
MAX_ORIGINAL_WFS_GEOJSON=15_000_000
MAX_WFS_FEATURE_COUNT=500
FIXED_RADIUS_M=5000
MIN_VALID_PER_YEAR=1000
MIN_BOTH_YEAR_VALID=1000
MIN_DISAPPEARED=100
MIN_APPEARED=100
FIXED_REPLICATION_THRESHOLD=0.90
OUT=Path(__file__).resolve().parent/"results/genuine_2018_2019_two_new_Wadden_sites_mask_boundaries_v205.json"

def frozen_site_roi(site):
    if site not in PUBLIC_ROI_RD:
        raise ValueError("SOURCE_STOP_UNFROZEN_PUBLIC_WADDEN_SITE")
    e,n=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
        *PUBLIC_ROI_RD[site])
    return (e-FIXED_RADIUS_M,n-FIXED_RADIUS_M,e+FIXED_RADIUS_M,n+FIXED_RADIUS_M)

def original_fixed_URL(site,year,kind,level=None):
    if site not in PUBLIC_ROI_RD or year not in FROZEN_YEARS:
        raise ValueError("SOURCE_STOP_UNKNOWN_SITE_OR_YEAR")
    xmin,ymin,xmax,ymax=frozen_site_roi(site)
    if kind=="WCS":
        if TWO_WCS_IDS[year] not in WCS_IDS:
            raise ValueError("SOURCE_STOP_BAD_NATIVE_WCS_COVERAGE")
        params=[("service","WCS"),("version","2.0.1"),
                ("request","GetCoverage"),
                ("coverageId",TWO_WCS_IDS[year]),
                ("format","image/tiff"),
                ("subset",f"E({xmin:.3f},{xmax:.3f})"),
                ("subset",f"N({ymin:.3f},{ymax:.3f})")]
        orig=urllib.parse.urlsplit(DESTINATIONS["WCS"])
    elif kind in ("WFS_HITS","WFS_GEOJSON"):
        if level not in ("high","low"):
            raise ValueError("SOURCE_STOP_NONFROZEN_WFS_BOUNDARY_LEVEL")
        name=f"TrilaWatt_Wattflaechen:{level}_water_boundary_{year}_nl"
        if name not in WFS_TYPES:
            raise ValueError("SOURCE_STOP_BAW_ORIGINAL_NATIVE_FEATURE_TYPE_NOT_FROZEN")
        params=[("service","WFS"),("version","2.0.0"),("request","GetFeature"),
                ("typeNames",name),("srsName",SOURCE_WFS_NATIVE_CRS),
                ("bbox",",".join(f"{v:.3f}" for v in (xmin,ymin,xmax,ymax))+
                 ","+SOURCE_WFS_NATIVE_CRS)]
        if kind=="WFS_HITS":
            params.append(("resultType","hits"))
        else:
            params.extend([("count",str(MAX_WFS_FEATURE_COUNT)),
                           ("outputFormat","application/json")])
        orig=urllib.parse.urlsplit(DESTINATIONS["WFS"])
    else:
        raise ValueError("SOURCE_STOP_UNKNOWN_ORIGINAL_BAW_OGC_QUERY_TYPE")
    return urllib.parse.urlunsplit((orig.scheme,orig.netloc,orig.path,
                                   urllib.parse.urlencode(params),""))

def approved_exact_source_query(url,kind):
    return any(url==original_fixed_URL(site,year,kind,level)
       for site in PUBLIC_ROI_RD
       for year in FROZEN_YEARS
       for level in (("high","low") if kind!="WCS" else (None,)))

def fetch_original_verified_source(url,kind):
    if not approved_exact_source_query(url,kind):
        raise ValueError("SOURCE_STOP_NOT_EXACT_PREDECLARED_BAW_OGC_SOURCE_URL")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v205-original-BAW-two-fixed-Wadden-points-source-replication/1.0",
        "Accept":"image/tiff" if kind=="WCS"
            else ("application/json" if kind=="WFS_GEOJSON" else "text/xml")})
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        NeverFollowHTTPRedirects())
    limit=MAX_ORIGINAL_WCS_TIFF if kind=="WCS" else (
        MAX_ORIGINAL_WFS_GEOJSON if kind=="WFS_GEOJSON" else 200_000)
    with op.open(req,timeout=75) as response:
        raw=response.read(limit+1)
        http=response.status
        final=response.geturl()
        ct=response.headers.get("Content-Type")
    if http!=200 or final!=url or len(raw)>limit or not raw:
        raise ValueError("SOURCE_STOP_ORIGINAL_BAW_SOURCE_RESPONSE_HTTP_OR_BYTES")
    return raw,{"original_source_response_SHA256":hashlib.sha256(raw).hexdigest(),
               "original_source_response_bytes":len(raw),
               "original_source_native_content_type":ct,
               "native_http_status":http,"HTTPS_CA_verification_enabled":True}

def read_native_TIFF_source(raw,site):
    if raw[:4] not in (b"II\x2a\x00",b"MM\x00\x2a",b"II\x2b\x00",b"MM\x00\x2b"):
        raise ValueError("SOURCE_STOP_ORIGINAL_WCS_NOT_NATIVE_TIFF")
    with MemoryFile(raw) as mem:
        with mem.open() as ds:
            if ds.crs is None or ds.crs.to_epsg()!=25832 or ds.count!=1:
                raise ValueError("SOURCE_STOP_NATIVE_BAW_TIFF_CRS_OR_BANDS")
            if ds.width*ds.height>1_100_000:
                raise ValueError("SOURCE_STOP_LARGE_OR_UNCROPPED_ORIGINAL_WCS")
            rx,ry=map(abs,ds.res)
            if not(5<=rx<=100 and 5<=ry<=100):
                raise ValueError("SOURCE_STOP_ORIGINAL_GRID_UNEXPECTED_SPATIAL_RESOLUTION")
            xmin,ymin,xmax,ymax=frozen_site_roi(site)
            bounds=ds.bounds
            if not(bounds.left>=xmin-100 and bounds.right<=xmax+100
               and bounds.bottom>=ymin-100 and bounds.top<=ymax+100):
                raise ValueError("SOURCE_STOP_WCS_NATIVE_BOUNDING_NOT_FROZEN_SITE_10KM")
            raster=ds.read(1,masked=True)
            arr=np.asarray(raster.data)
            masked=np.ma.getmaskarray(raster)
            valid=(~masked)&np.isfinite(arr)&(np.abs(arr)<=100)
            metadata={"original_NL_WCS_CRS":ds.crs.to_string(),
                      "native_resolution_m":[float(rx),float(ry)],
                      "native_raster_width_height":[ds.width,ds.height],
                      "native_original_nodata_literal":repr(ds.nodata),
                      "n_total_native_grid_cells":int(arr.size),
                      "n_plausible_numeric_source_pixels":int(valid.sum()),
                      "fixed_source_bbox_EPSG25832_m":[round(x,3) for x in (
                          bounds.left,bounds.bottom,bounds.right,bounds.top)],
                      "original_numeric_support_NOT_verified_intertidal_area":True}
            return valid,ds.transform,metadata

def original_WFS_source_curves(site,year,level):
    url=original_fixed_URL(site,year,"WFS_HITS",level)
    hitsraw,hitsreceipt=fetch_original_verified_source(url,"WFS_HITS")
    n=parse_original_native_hits(hitsraw)
    if n>MAX_WFS_FEATURE_COUNT:
        raise ValueError("SOURCE_STOP_ORIGINAL_WFS_BBOX_MATCHES_EXCEED_FIXED_COUNT500")
    h={"original_source_WFS_HITS_n":n,
       "original_WFS_HITS_source_response_SHA256":
           hitsreceipt["original_source_response_SHA256"],
       "true_original_geometries_retrieved_not_persisted":False}
    if n==0:
        h["source_original_geometry_semantic_SHA256"]=None
        return [],h
    gjson,receipt=fetch_original_verified_source(
        original_fixed_URL(site,year,"WFS_GEOJSON",level),"WFS_GEOJSON")
    try:
        obj=json.loads(gjson)
    except (ValueError,UnicodeError) as err:
        raise ValueError("SOURCE_STOP_ORIGINAL_BAW_WFS_UNREADABLE_GEOJSON") from err
    if (obj.get("type")!="FeatureCollection"
        or not isinstance(obj.get("features"),list)
        or len(obj["features"])!=n):
        raise ValueError("SOURCE_STOP_NATIVE_GEOJSON_FEATURES_NOT_EQUAL_FIXED_HITS")
    if obj.get("numberReturned") is not None and int(obj["numberReturned"])!=n:
        raise ValueError("SOURCE_STOP_NATIVE_GEOJSON_NUMBERRETURNED_NOT_ORIGINAL_HITS")
    roi=box(*frozen_site_roi(site))
    curves=[]
    n_intersects=0
    for feature in obj["features"]:
        if feature.get("type")!="Feature" or not isinstance(feature.get("geometry"),dict):
            raise ValueError("SOURCE_STOP_ORIGINAL_WFS_NOT_A_GEOJSON_CURVE_FEATURE")
        line=shape(feature["geometry"])
        if line.geom_type not in ("LineString","MultiLineString"):
            raise ValueError("SOURCE_STOP_ORIGINAL_NATIVE_WFS_BOUNDARY_NOT_MULTICURVE")
        if line.is_empty:continue
        x0,y0,x1,y1=line.bounds
        if not (100000<x0<x1<800000 and 5e6<y0<y1<7e6):
            raise ValueError("SOURCE_STOP_NATIVE_WFS_GEOJSON_NOT_EPSG25832_METRIC")
        part=line.intersection(roi)
        if not part.is_empty and part.length>0:
            curves.append(part)
            n_intersects+=1
    h["true_original_geometries_retrieved_not_persisted"]=True
    h["original_source_WFS_GeoJSON_raw_HTTP_SHA256"]=receipt["original_source_response_SHA256"]
    h["original_source_WFS_geometry_semantic_SHA256_excludes_top_timeStamp"]=(
        semantic_original_geojson_fingerprint(obj))
    h["n_true_multicurves_intersect_site_ROI"]=n_intersects
    h["n_original_bbox_matches_without_true_positive_curve_length"]=n-n_intersects
    h["original_clipped_curve_length_km"]=round(
        sum(x.length for x in curves)/1000,6)
    return curves,h

def source_site_mask_pattern(site):
    data={"site":site,
          "original_2011_WEBTICS_public_RD_xy_m":PUBLIC_ROI_RD[site],
          "source_UTM25832_fixed_10km_ROI_m":[round(x,3) for x in frozen_site_roi(site)],
          "site_source_status":"SOURCE_STOP",
          "source_2018_2019_tiff":{},"source_original_boundary_curves":{}}
    try:
        grids={}
        for year in FROZEN_YEARS:
            raw,receipt=fetch_original_verified_source(
                original_fixed_URL(site,year,"WCS"),"WCS")
            valid,transform,native=read_native_TIFF_source(raw,site)
            grids[year]=(valid,transform)
            data["source_2018_2019_tiff"][year]={"source_receipt":receipt,
               "native_numeric_support_metadata":native}
        if (grids["2018"][0].shape!=grids["2019"][0].shape or
            grids["2018"][1]!=grids["2019"][1]):
            raise ValueError("SOURCE_STOP_ORIGINAL_WCS_TWO_YEARS_NOT_SAME_NATIVE_CELLS")
        geom=[]
        for year in FROZEN_YEARS:
            for level in ("high","low"):
                curves,receipt=original_WFS_source_curves(site,year,level)
                geom.extend(curves)
                data["source_original_boundary_curves"][f"{year}_{level}"]=receipt
        if not geom:
            raise ValueError("SOURCE_STOP_NO_GENUINE_ORIGINAL_CURVES_IN_FIXED_SITE_ROI")
        v18=grids["2018"][0]
        v19=grids["2019"][0]
        if any(int(v.sum())<MIN_VALID_PER_YEAR for v in (v18,v19)):
            raise ValueError("SOURCE_STOP_NATIVE_YEAR_PIXEL_SUPPORT_LT1000")
        classes=canonical_classes(v18,v19)
        if int(classes["both"].sum())<MIN_BOTH_YEAR_VALID:
            raise ValueError("SOURCE_STOP_NATIVE_COMMON_TWO_YEAR_SUPPORT_LT1000")
        bitmap=rasterize(((line,1) for line in geom),
            out_shape=v18.shape,transform=grids["2018"][1],
            fill=0,all_touched=True,dtype="uint8")
        n_boundary=int(np.count_nonzero(bitmap))
        if n_boundary<10:
            raise ValueError("SOURCE_STOP_AUTHENTIC_ORIGINAL_LINES_NOT_RASTERIZED")
        t=grids["2018"][1]
        distance=distance_transform_edt(bitmap==0,sampling=(abs(t.e),abs(t.a)))
        totals={name:int(mask.sum()) for name,mask in classes.items()}
        lost=totals["2018_only"]
        gained=totals["2019_only"]
        n_lost_near=int(np.sum(classes["2018_only"]&(distance<100)))
        n_gained_near=int(np.sum(classes["2019_only"]&(distance<100)))
        share_lost=round(n_lost_near/lost,8) if lost else None
        share_gained=round(n_gained_near/gained,8) if gained else None
        evaluable=lost>=MIN_DISAPPEARED and gained>=MIN_APPEARED
        replicate=bool(evaluable and share_lost>=FIXED_REPLICATION_THRESHOLD and
                       share_gained>=FIXED_REPLICATION_THRESHOLD)
        data["source_site_mask_turnover"]=totals
        data["distance_original_boundary_raster_pixels"]=n_boundary
        data["source_native_distance_band_classes"]=bin_source_masks(classes,distance)
        data["source_near_far_conditional_loss_rate"]=risk_ratio_near_far(classes,distance)
        data["source_quadrant_mask_support_classes"]=quadrants(classes)
        data["frozen_geographic_replication_gate"]={
            "n_lost_near_100m":n_lost_near,
            "n_gained_near_100m":n_gained_near,
            "share_lost_original_2018_only_near_100m":share_lost,
            "share_gained_original_2019_only_near_100m":share_gained,
            "minimum_source_loss_and_gain_each_100_met":evaluable,
            "threshold_near_100m_each_ge90percent":FIXED_REPLICATION_THRESHOLD,
            "exploratory_source_mask_turnover_pattern_replicated":replicate,
            "not_true_field_intertidal_habitat_erosion_or_animals":True}
        data["site_source_status"]="ORIGINAL_SOURCE_SITE_MASK_AND_LINE_DISTANCE_AUDITED"
    except Exception as err:
        data["source_error_kind"]=type(err).__name__
        data["source_error_summary"]=str(err)[:250]
    return data

def run(out=OUT):
    report={"analysis":"v205-original-two-independent-public-Wadden10km-sites-source-mask-turnover",
        "frozen_new_source_region_names":list(PUBLIC_ROI_RD),
        "original_WFS_WCS_capabilities_SHA256":CAP_SHA,
        "native_model_is_posthoc_to_v204_original_mask_line_finding":True,
        "initial_v204_Vlieland_loss_and_gain_share_near_100m":[0.9869,0.9974],
        "no_native_raster_or_geojson_coordinates_saved":True,
        "status":"SOURCE_STOP_ORIGINAL_TWO_SITE_REPLICATION"}
    sites={}
    try:
        for service in ("WFS","WCS"):
            xml,receipt=verified_direct_baw_OGC_GET(DESTINATIONS[service],service)
            if xml is None or receipt["original_XML_SHA256"]!=CAP_SHA[service]:
                raise ValueError("SOURCE_STOP_BAW_NATIVE_CAPABILITIES_SHA_CHANGED")
            root,entries,ops=native_metadata_gate(xml,service)
            required="GetFeature" if service=="WFS" else "GetCoverage"
            if required not in ops:
                raise ValueError("SOURCE_STOP_ORIGINAL_BAW_NATIVE_OPERATION_NOT_ADVERTISED")
        for site in PUBLIC_ROI_RD:
            sites[site]=source_site_mask_pattern(site)
    except Exception as exc:
        report["original_catalogue_source_error_kind"]=type(exc).__name__
        report["original_catalogue_source_error_summary"]=str(exc)[:220]
    report["new_two_site_source_results"]=sites
    n_source=sum(v["site_source_status"]==
        "ORIGINAL_SOURCE_SITE_MASK_AND_LINE_DISTANCE_AUDITED" for v in sites.values())
    eligible=sum(v.get("frozen_geographic_replication_gate",{}).get(
        "minimum_source_loss_and_gain_each_100_met",False) for v in sites.values())
    replicated=sum(v.get("frozen_geographic_replication_gate",{}).get(
        "exploratory_source_mask_turnover_pattern_replicated",False)
        for v in sites.values())
    report["scientific_gates"]={
        "both_new_independent_published_reference_site_source_data_admitted":n_source==2,
        "n_new_site_full_source_admission":n_source,
        "n_new_site_evaluable_loss_and_gain_ge100":eligible,
        "n_new_site_exploratory_mask_near_boundary_pattern_replicated":replicated,
        "both_sites_exploratory_source_pattern_replicates_v204":n_source==2 and eligible==2 and replicated==2,
        "any_real_field_erosion_or_annual_intertidal_habitat_loss_proven":False,
        "native_2018_2019_original_surveyday_and_NAP_calibrated":False,
        "GPS_bird_tide_solar_Boids_effect_scored":False}
    report["status"]="ORIGINAL_BAW_TWO_NEW_WADDEN_SITE_MASK_BOUNDARY_SOURCE_REPLICATION_AUDITED" if n_source==2 else "SOURCE_STOP_ONE_OR_BOTH_NEW_WADDEN_SITE_ORIGINAL_SUPPORT"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V205_ORIGINAL_TWO_WADDEN_MASK_SOURCE="+json.dumps({
       "status":report["status"],"gates":report["scientific_gates"],
       "sites":{name:{"source_status":d["site_source_status"],
           "native_numeric_valid_by_year":{year:v["native_numeric_support_metadata"]["n_plausible_numeric_source_pixels"]
              for year,v in d["source_2018_2019_tiff"].items()},
           "source_mask_classes":d.get("source_site_mask_turnover"),
           "replication":d.get("frozen_geographic_replication_gate"),
           "source_error":d.get("source_error_summary")}
           for name,d in sites.items()},
       "not_actual_ecological_or_original_field_erosion":True
    },sort_keys=True))
    return report

if __name__=="__main__":
    run()
