"""v195: six predeclared public-location/time BAW yearly WMS GetFeatureInfo SOURCE probes.

Not a hydrodynamic model validation: a WMS render value is not proven mNAP
or a true water level at a tagged bird's original GPS position.
Original year-specific 2018/19 GetCapabilities byte SHA must match v194.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from pyproj import Transformer

from original_BAW_2018_2019_verified_WMS_capabilities import (
    OFFICIAL_YEAR_WMS,fetch_verified_original_WMS,bare_tag
)

FIXED_CAPABILITIES_SHA256={
  "2018":"386af7c9a75b66ef23017dfd49abe3afb71a530011e9f7bedbf3904281b7484f",
  "2019":"a52bf61de7bc50495ea75782a6e4bc5b4762ce3174e29a961cec1f697fe9b20a",
}
NATIVE_HEIGHT_LAYERS={y:f"sea_surface_height_2d_{y}_NL" for y in ("2018","2019")}
FIXED_PUBLICATION_RD_POINTS={
  "VlielandHaven":(135280,590000),
  "WestTerschelling":(143870,597420),
  "Wierumergronden":(192882,614562),
}
FIXED_TARGET_UTC={y:f"{y}-06-01T12:00:00.000Z" for y in ("2018","2019")}
ALLOWED_INFO_FORMATS=("application/json","text/plain","text/xml")
MAX_FEATURE_BYTES=100_000
TARGET_GRID_PX=51
TARGET_GRID_CENTER=25
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_v195/results/authentic_BAW_2018_2019_NL_WMS_time_point_feature_info_v195.json"

def strip_tag(node):
    return bare_tag(node.tag)

def validate_capability_and_layer(raw,year):
    if hashlib.sha256(raw).hexdigest()!=FIXED_CAPABILITIES_SHA256[year]:
        raise ValueError("STOP_ORIGINAL_YEAR_CAPABILITIES_SHA_CHANGED_AFTER_v194")
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_DTD_ENTITY_IN_OFFICIAL_WMS")
    root=ET.fromstring(raw)
    if strip_tag(root).lower() not in ("wms_capabilities","wmt_ms_capabilities"):
        raise ValueError("STOP_NOT_WMS_CAPABILITIES")
    if root.attrib.get("version")!="1.3.0":
        raise ValueError("STOP_NATIVE_WMS_NOT_1_3_0")
    capability=next((x for x in root if strip_tag(x)=="Capability"),None)
    if capability is None:raise ValueError("STOP_WMS_MISSING_CAPABILITY")
    request=next((x for x in capability if strip_tag(x)=="Request"),None)
    infoformats=[]
    if request is not None:
        for op in request:
            if strip_tag(op)!="GetFeatureInfo":continue
            for fmt in op:
                if strip_tag(fmt)=="Format" and fmt.text:
                    infoformats.append(fmt.text.strip().lower())
    format_used=next((fmt for fmt in ALLOWED_INFO_FORMATS if fmt in infoformats),None)
    target=NATIVE_HEIGHT_LAYERS[year]
    layer_nodes=[]
    def visit(node,queryable=False,crs=frozenset(),time_values=()):
        if strip_tag(node)!="Layer":
            for child in node:
                if strip_tag(child)=="Layer":
                    visit(child,queryable,crs,time_values)
            return
        native_q=str(node.attrib.get("queryable",str(int(queryable)))).lower()
        q=native_q in ("1","true")
        child_crs=set(crs)
        dims=list(time_values)
        name=None
        for child in node:
            tag=strip_tag(child)
            if tag=="Name":name=(child.text or "").strip()
            elif tag=="CRS" and child.text:child_crs.add(child.text.strip())
            elif tag in ("Dimension","Extent") and child.attrib.get("name","").lower()=="time" and child.text:
                dims.append(child.text.strip())
        if name==target:
            layer_nodes.append({"original_layer_name":name,
               "original_WMS_queryable":q,
               "inherited_source_CRS_sorted":sorted(child_crs),
               "original_time_dimension_strings":dims})
        for child in node:
            if strip_tag(child)=="Layer":
                visit(child,q,frozenset(child_crs),tuple(dims))
    visit(capability)
    if len(layer_nodes)!=1:raise ValueError("STOP_MISSING_OR_AMBIGUOUS_ORIGINAL_YEAR_NL_HEIGHT_LAYER")
    native=layer_nodes[0]
    time_in_layer=any(FIXED_TARGET_UTC[year][:10] in v or
       (f"{year}-01-01" in v and f"{int(year)+1}-01-01" in v) for v in native["original_time_dimension_strings"])
    return {"original_layer_name":target,
      "original_WMS_queryable":native["original_WMS_queryable"],
      "supported_original_feature_info_MIME":infoformats[:15],
      "chosen_predeclared_feature_info_format":format_used,
      "original_inherited_CRS_supports_EPSG_4326":("EPSG:4326" in native["inherited_source_CRS_sorted"]),
      "original_layer_declares_target_UTC_time":time_in_layer,
      "time_dimension_expression_count":len(native["original_time_dimension_strings"]),
      "original_time_dimension_example":native["original_time_dimension_strings"][-1][:180] if native["original_time_dimension_strings"] else None,
      "source_admissible_for_feature_info_probe":bool(native["original_WMS_queryable"] and format_used and
          "EPSG:4326" in native["inherited_source_CRS_sorted"] and time_in_layer),
      "raw_original_WMS_file_sha256":FIXED_CAPABILITIES_SHA256[year]}

def make_fixed_feature_request(year,lon,lat,fmt):
    if year not in OFFICIAL_YEAR_WMS or fmt not in ALLOWED_INFO_FORMATS:
        raise ValueError("STOP_NONFROZEN_YEAR_OR_INFO_FORMAT")
    if not (3.0<lon<10.0 and 52.0<lat<56.0):
        raise ValueError("STOP_COORDINATE_OUTSIDE_PUBLISHED_WADDEN_REGION")
    delta=0.01
    # WMS 1.3.0 with EPSG:4326 ALWAYS [lat,lon,lat,lon], not [lon,lat...].
    params={
     "SERVICE":"WMS","VERSION":"1.3.0","REQUEST":"GetFeatureInfo",
     "LAYERS":NATIVE_HEIGHT_LAYERS[year],
     "QUERY_LAYERS":NATIVE_HEIGHT_LAYERS[year],
     "STYLES":"","CRS":"EPSG:4326",
     "BBOX":",".join(f"{v:.6f}" for v in (lat-delta,lon-delta,lat+delta,lon+delta)),
     "WIDTH":str(TARGET_GRID_PX),"HEIGHT":str(TARGET_GRID_PX),
     "I":str(TARGET_GRID_CENTER),"J":str(TARGET_GRID_CENTER),
     "INFO_FORMAT":fmt,"FEATURE_COUNT":"1",
     "TIME":FIXED_TARGET_UTC[year]
    }
    base=urllib.parse.urlsplit(OFFICIAL_YEAR_WMS[year])
    url=urllib.parse.urlunsplit((base.scheme,base.netloc,base.path,
            urllib.parse.urlencode(params),""))
    return url,params

class RestrictFeatureRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        p=urllib.parse.urlsplit(newurl)
        if not (p.scheme=="https" and p.hostname=="coast.baw.de" and
                p.path.startswith("/geoserver/TrilaWatt_ncHydro_") and
                "GetFeatureInfo" in urllib.parse.unquote(p.query)):
            raise ValueError("SOURCE_STOP_UNAPPROVED_FEATUREINFO_REDIRECT")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def verified_feature_info_source(url):
    p=urllib.parse.urlsplit(url)
    if not (p.scheme=="https" and p.hostname=="coast.baw.de"
            and p.path.startswith("/geoserver/TrilaWatt_ncHydro_") and
            "GetFeatureInfo" in urllib.parse.unquote(p.query)):
        raise ValueError("SOURCE_STOP_NONOFFICIAL_OR_NONFEATURE_WMS_QUERY")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v195-BAW-original-2018-2019-WMS-GetFeatureInfo/1.0",
        "Accept":"application/json,text/plain,text/xml"})
    op=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        RestrictFeatureRedirect())
    with op.open(req,timeout=28) as resp:
        data=resp.read(MAX_FEATURE_BYTES+1)
        h=resp.headers
        status=resp.status
        final=resp.geturl()
    if status!=200 or len(data)>MAX_FEATURE_BYTES or not data:
        raise ValueError("SOURCE_STOP_BAD_OR_TOO_LARGE_WMS_GETFEATUREINFO_RESPONSE")
    if urllib.parse.urlsplit(final).hostname!="coast.baw.de":
        raise ValueError("SOURCE_STOP_FEATURE_INFO_REDIRECTED_OUTSIDE_OFFICIAL_HOST")
    decoded=data.decode("utf-8",errors="replace")
    if ("ServiceException" in decoded[:5000] or "<ExceptionReport" in decoded[:5000]
        or "InvalidParameter" in decoded[:5000]):
        raise ValueError("SOURCE_STOP_WMS_NATIVE_FEATUREINFO_SERVICE_EXCEPTION")
    return {"verified_TLS_and_200_http":True,
        "native_content_type":h.get("Content-Type"),
        "native_original_feature_info_response_SHA256":hashlib.sha256(data).hexdigest(),
        "native_original_feature_info_response_bytes":len(data),
        "response_contains_no_data_indicator":any(s in decoded.lower() for s in (
            "no features", "null","no data","nodata","empty")),
        "native_WMS_response_first_260_chars_UNINTERPRETED":re.sub(r"\s+"," ",decoded[:260]),
        "physically_calibrated_height_m_NAP_verified":False,
        "native_NetCDF_units_and_vertical_datum_NOT_OPENED":True}

def run(out=OUT):
    report={"version":"v195-yearly-original-BAW-WMS-public-site-timepoint-source",
        "v194_original_TLS_capability_success_run":44306236367,
        "source_original_capability_expected_SHA":FIXED_CAPABILITIES_SHA256,
        "source_public_WEBTICS_2011_RD_stations":FIXED_PUBLICATION_RD_POINTS,
        "source_original_NL_height_layers":NATIVE_HEIGHT_LAYERS,
        "fixed_original_UTC_time":FIXED_TARGET_UTC,
        "no_raw_GPS_ACC_RWS_timeseries_or_native_NC_downloaded":True,
        "source_original_2011_station_coordinates_not_2018_instrument_location":True,
        "status":"SOURCE_STOP"}
    transformer=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True)
    records={}
    for year in FIXED_TARGET_UTC:
        yr={"status":"SOURCE_STOP_CAPABILITIES_UNVERIFIED"}
        try:
            original_xml,receipt=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            source=validate_capability_and_layer(original_xml,year)
            yr={"status":"ORIGINAL_WMS_SOURCE_ONLY_CAPABILITIES_VERIFIED",
                "capability_SHA_verified":receipt["original_WMS_xml_SHA256"],
                "native_original_layer_source":source,
                "public_fixed_points":{}}
            if source["source_admissible_for_feature_info_probe"]:
                for name,(x,y) in FIXED_PUBLICATION_RD_POINTS.items():
                    lon,lat=transformer.transform(x,y)
                    entry={"source_public_RD_reference_xy_m":[x,y],
                       "source_reprojected_lonlat_2011_reference":[round(lon,6),round(lat,6)],
                       "not_tagged_bird_GPS":True}
                    query,_=make_fixed_feature_request(year,lon,lat,
                        source["chosen_predeclared_feature_info_format"])
                    try:
                        entry["original_source_response"]=verified_feature_info_source(query)
                        entry["status"]="ORIGINAL_WMS_FEATUREINFO_RETURNED_NOT_PHYSICAL_HEIGHT_ADMITTED"
                    except Exception as exc:
                        entry["status"]="SOURCE_STOP_FEATUREINFO_SITE_RESPONSE"
                        entry["error_kind"]=type(exc).__name__
                        entry["error_summary"]=str(exc)[:200]
                    yr["public_fixed_points"][name]=entry
                yr["status"]="FEATUREINFO_SOURCE_PROBED_NO_HEIGHT_PHYSICS_ADMITTED"
            else:
                yr["status"]="SOURCE_STOP_WMS_LAYER_NOT_QUERYABLE_OR_CRS_OR_TIME"
        except Exception as exc:
            yr["error_kind"]=type(exc).__name__
            yr["error_summary"]=str(exc)[:200]
        records[year]=yr
    report["two_original_years"]=records
    report["source_gates"]={
      "both_year_capabilities_pinned_sha_still_exact":all(
          v.get("capability_SHA_verified")==FIXED_CAPABILITIES_SHA256[y] for y,v in records.items()),
      "both_year_original_NL_height_queryable_time_CRSEligible":all(
          bool(v.get("native_original_layer_source",{}).get("source_admissible_for_feature_info_probe"))
          for v in records.values()),
      "all_six_predeclared_WMS_point_response_retrieved":all(
          len(v.get("public_fixed_points",{}))==len(FIXED_PUBLICATION_RD_POINTS) and
          all(x.get("status")=="ORIGINAL_WMS_FEATUREINFO_RETURNED_NOT_PHYSICAL_HEIGHT_ADMITTED"
          for x in v.get("public_fixed_points",{}).values())
          for v in records.values()),
      "native_original_NetCDF_units_vertical_datum_verified":False,
      "site_specific_model_height_mNAP_reliably_extracted":False,
      "local_tide_at_original_bird_GPS_and_historical_z_dryflat_verified":False,
      "tide_sun_biology_or_Boids_movement_mechanism_estimated":False}
    if report["source_gates"]["all_six_predeclared_WMS_point_response_retrieved"]:
        report["status"]="SIX_ORIGINAL_WMS_FEATUREINFO_SOURCE_RESPONSES_RETRIEVED_PHYSICAL_HEIGHT_STOP"
    else:
        report["status"]="SOURCE_STOP_WMS_FEATUREINFO_NOT_SIX_ORIGINAL_RESPONSES"
    o=Path(out);o.parent.mkdir(parents=True,exist_ok=True)
    o.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V195_BAW_NATIVE_POINT_SOURCE="+json.dumps({
      "status":report["status"],
      "source_gates":report["source_gates"],
      "years":{y:{"year_status":v["status"],
        "layer_source":v.get("native_original_layer_source"),
        "points":{name:{"status":entry["status"],
           "content_type":entry.get("original_source_response",{}).get("native_content_type"),
           "response_bytes":entry.get("original_source_response",{}).get("native_original_feature_info_response_bytes"),
           "response_excerpt":entry.get("original_source_response",{}).get("native_WMS_response_first_260_chars_UNINTERPRETED"),
           "error":entry.get("error_summary")}
           for name,entry in v.get("public_fixed_points",{}).items()},
        "error":v.get("error_summary")} for y,v in records.items()},
      "not_a_field_observation_or_animal_effect":True
    },sort_keys=True),flush=True)
    return report

if __name__=="__main__":run()
