"""v201 original WFS2 GetFeature resultType=hits ONLY in frozen Vlieland 10km ROI.

No raw polygons, line coordinates, actual bird GPS, RWS tide series or ecology.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request
from pathlib import Path
from pyproj import Transformer
from original_BAW_year_NL_WFS_WCS_schema_envelope import (
 CAP_SHA,WFS_TYPES,PUBLISHED_VLIE_RD,tag,native_metadata_gate,source_xml)
from authentic_BAW_coast_Wattflaechen_OGC_capabilities import (
 DESTINATIONS,verified_direct_baw_OGC_GET)
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import NeverFollowHTTPRedirects

DISTANCE_M=5000
SOURCE_WFS_NATIVE_CRS="urn:ogc:def:crs:EPSG::25832"
OUT=Path(__file__).resolve().parent/"results/BAW_WFS_2018_2019_high_low_Vlieland_10km_original_hits_v201.json"
MAX_BYTES=250_000

def fixed_roi():
    east,north=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
       *PUBLISHED_VLIE_RD)
    return (east-DISTANCE_M,north-DISTANCE_M,east+DISTANCE_M,north+DISTANCE_M)

def make_hits_request(name,roi):
    if name not in WFS_TYPES or len(roi)!=4 or (
      max(abs(a-b) for a,b in zip(roi,fixed_roi()))>1e-6):
        raise ValueError("SOURCE_STOP_NONFROZEN_WFS_TYPE_OR_ROI")
    fields={"service":"WFS","version":"2.0.0","request":"GetFeature",
      "typeNames":name,"resultType":"hits",
      "srsName":SOURCE_WFS_NATIVE_CRS,
      "bbox":",".join(f"{v:.3f}" for v in roi)+","+SOURCE_WFS_NATIVE_CRS}
    base=urllib.parse.urlsplit(DESTINATIONS["WFS"])
    return urllib.parse.urlunsplit((base.scheme,base.netloc,base.path,
      urllib.parse.urlencode(fields),""))

def only_native_WFS_hits_request(url):
    p=urllib.parse.urlsplit(url)
    q=dict(urllib.parse.parse_qsl(p.query))
    return (p.scheme=="https" and p.hostname=="coast.baw.de"
      and p.path=="/geoserver/TrilaWatt_Wattflaechen/wfs"
      and q.get("service")=="WFS" and q.get("version")=="2.0.0"
      and q.get("request")=="GetFeature" and q.get("resultType")=="hits"
      and q.get("srsName")==SOURCE_WFS_NATIVE_CRS
      and q.get("typeNames") in WFS_TYPES
      and q.get("bbox","").endswith(SOURCE_WFS_NATIVE_CRS))

def parse_original_native_hits(raw):
    root=source_xml(raw)
    if tag(root.tag)!="FeatureCollection":
        raise ValueError("SOURCE_STOP_NOT_ORIGINAL_WFS_HITS_FEATURECOLLECTION")
    n=root.attrib.get("numberMatched")
    ret=root.attrib.get("numberReturned")
    if not isinstance(n,str) or not n.isdigit():
        raise ValueError("SOURCE_STOP_WFS_NUMBERMATCHED_NOT_EXACT_INTEGER")
    if ret not in (None,"0"):
        raise ValueError("SOURCE_STOP_HITS_RETURNED_REAL_GEOMETRY")
    if any(tag(child.tag) in ("member","featureMember","featureMembers") for child in root):
        raise ValueError("SOURCE_STOP_HITS_HAS_GEOMETRY_MEMBER")
    return int(n)

def original_WFS_verified_hits(url):
    if not only_native_WFS_hits_request(url):
        raise ValueError("SOURCE_STOP_UNAPPROVED_OR_MODIFIED_WFS_HITS")
    op=urllib.request.build_opener(
       urllib.request.HTTPSHandler(context=ssl.create_default_context()),
       NeverFollowHTTPRedirects())
    request=urllib.request.Request(url,method="GET",headers={
      "User-Agent":"boids-v201-BAW-original-WFS-hits-no-geometry/1.0",
      "Accept":"application/xml,text/xml"})
    with op.open(request,timeout=42) as response:
        raw=response.read(MAX_BYTES+1)
        status=response.status
        final=response.geturl()
        ct=response.headers.get("Content-Type")
    if status!=200 or final!=url or not raw or len(raw)>MAX_BYTES:
        raise ValueError("SOURCE_STOP_ORIGINAL_WFS_HTTP_OR_OVERSIZE")
    n=parse_original_native_hits(raw)
    return {"original_fixed_ROI_numberMatched":n,
       "original_WFS_response_SHA256":hashlib.sha256(raw).hexdigest(),
       "original_response_bytes":len(raw),
       "original_response_Content_Type":ct,
       "native_http_status":status,
       "native_CA_TLS_verified":True,
       "no_actual_feature_curve_geometry_downloaded":True}

def run(out=OUT):
    roi=fixed_roi()
    result={"analysis":"v201-original_WFS2_high_low_2018_2019_Vlieland_10km_HITS",
       "source_capabilities_SHA256_frozen":CAP_SHA["WFS"],
       "source_published_reference_RD":PUBLISHED_VLIE_RD,
       "source_bbox_EPSG25832_m":[round(x,3) for x in roi],
       "frozen_half_width_m":DISTANCE_M,
       "source_native_crs":SOURCE_WFS_NATIVE_CRS,
       "four_original_layer_names":WFS_TYPES,
       "no_bird_GPS_or_annual_intertidal_area_calculated":True,
       "status":"SOURCE_STOP"}
    items={}
    try:
        raw,receipt=verified_direct_baw_OGC_GET(DESTINATIONS["WFS"],"WFS")
        if raw is None:raise ValueError("SOURCE_STOP_ORIGINAL_CAP_NOT_200")
        root,layers,operations=native_metadata_gate(raw,"WFS")
        if receipt["original_XML_SHA256"]!=CAP_SHA["WFS"] or "GetFeature" not in operations:
            raise ValueError("SOURCE_STOP_NATIVE_WFS_CAP_CHANGED_OR_GETFEATURE_NOT_ADVERTISED")
        for name in WFS_TYPES:
            crs=next((c.text for c in layers[name] if tag(c.tag)=="DefaultCRS"),None)
            if crs!=SOURCE_WFS_NATIVE_CRS:
                raise ValueError("SOURCE_STOP_ORIGINAL_WFS_CRS_NOT_EXPECTED")
            try:
                entry=original_WFS_verified_hits(make_hits_request(name,roi))
                entry["source_status"]="ORIGINAL_WFS2_FIXED_ROI_HITS_COUNT_RETRIEVED"
            except Exception as err:
                entry={"source_status":"SOURCE_STOP_WFS_HITS",
                   "error_kind":type(err).__name__,"error_summary":str(err)[:200]}
            items[name]=entry
        result["source_Capabilities_SHA256_reverified"]=receipt["original_XML_SHA256"]
    except Exception as err:
        result["source_error_kind"]=type(err).__name__
        result["source_error_summary"]=str(err)[:210]
    result["four_year_high_low_native_source_HITS"]=items
    complete=sum(x["source_status"]=="ORIGINAL_WFS2_FIXED_ROI_HITS_COUNT_RETRIEVED"
                 for x in items.values())
    positive=sum(x.get("original_fixed_ROI_numberMatched",0)>0 for x in items.values())
    result["scientific_gates"]={
      "four_fixed_original_year_high_low_WFS_HITS_counts_retrieved":complete==4,
      "n_counted_original_types":complete,
      "n_types_with_one_or_more_actual_line_features_in_fixed_ROI":positive,
      "all_four_types_have_positive_native_HITS_in_ROI":positive==4 and complete==4,
      "actual_line_coordinates_downloaded":False,
      "actual_bird_GPS_dryflat_area_or_exposure_admitted":False,
      "tide_solar_ACC_Boids_mechanism_inferred":False}
    result["status"]="FOUR_ORIGINAL_10KM_ROI_WFS_HITS_COUNTS_RETRIEVED_NO_GEOMETRY" if complete==4 else "SOURCE_STOP_INCOMPLETE_ORIGINAL_WFS_FIXED_ROI_HITS"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V201_ORIGINAL_VLIELAND_WFS_HITS="+json.dumps({
      "status":result["status"],"gates":result["scientific_gates"],
      "counts":{name:{"status":v["source_status"],
             "n":v.get("original_fixed_ROI_numberMatched"),
             "error":v.get("error_summary")} for name,v in items.items()},
      "source_error":result.get("source_error_summary"),
      "no_GPS_or_instantaneous_dryflat":True},sort_keys=True))
    return result

if __name__=="__main__":
    run()
