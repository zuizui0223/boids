"""v84B WMR original WFS HTTP500 request-shape diagnostics (source-only).

No source polygon geometry is saved, no wild GPS, no RWS observations,
no NIOZ native model indexed animal use, and no claim WMR layer equals
2021 corrected Mendeley v2. Never silently use a truncated feature list.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from xml.etree import ElementTree as ET
import json,re

from wmr_geoserver_ecotope_source_probe import BASE,MAIN
# These literal geographic bounds are copied from the frozen source-only
# v84 protocol; this network-error probe must not require numerical GIS.
FIXED_SITE_BBOX={
    "Schiermonnikoog":(5.70,53.20,6.60,53.70),
    "Ameland_Nes":(5.30,53.20,6.10,53.60)}

QUERY_SETTINGS=(
    ("CQL_hits",{"resultType":"hits","CQL_FILTER":"litoralcode IN (3,4)"}),
    ("CQL10",{"count":"10","CQL_FILTER":"litoralcode IN (3,4)"}),
    ("UNFILTERED10",{"count":"10"}),
    ("CQL3_10",{"count":"10","CQL_FILTER":"litoralcode=3"}),
    ("CQL100",{"count":"100","CQL_FILTER":"litoralcode IN (3,4)"}))
MAX_BYTES=5_000_000
EXPECTED_CLASSES=(3,4)

def _request(params,fetch=None):
    if fetch is not None:
        return fetch(params)
    request={
        "service":"WFS","version":"2.0.0",
        "request":"GetFeature",
        "typeNames":MAIN,
        "outputFormat":"application/json",
        "srsName":"CRS:84",
        **params}
    req=Request(BASE+"?"+urlencode(request),
        headers={"User-Agent":"boids-v84b-WMR-GIS-shape-diagnostic/1.0",
                 "Accept":"application/json,application/xml,*/*"})
    try:
        with urlopen(req,timeout=40) as resp:
            data=resp.read(MAX_BYTES+1)
            return resp.status,data,None
    except HTTPError as ex:
        return int(ex.code),b"",ex.read(300).decode("utf-8","replace")[:300]
    except (URLError,TimeoutError) as ex:
        return None,b"",str(ex)[:300]

def parse_native_return(status,data,error):
    out={"http_status":status,
         "source_error_excerpt_if_any":error,
         "original_source_SHA256_local_not_publisher":sha256(data).hexdigest()
             if data else None,
         "source_bytes_capped_and_only_metadata_released":True}
    if error or status!=200:
        out["status"]="SOURCE_HTTP_OR_NETWORK_ERROR"
        return out
    if len(data)>MAX_BYTES:
        out["status"]="SOURCE_RESPONSE_EXCEEDS_5MB_DIAGNOSTIC_CAP"
        return out
    try:
        q=json.loads(data)
        if not isinstance(q,dict) or not isinstance(q.get("features"),list):
            out["status"]="SOURCE_NOT_ORIGINAL_WFS_FEATURE_COLLECTION"
            return out
        feature=q["features"]
        classes=Counter()
        for r in feature:
            p=r.get("properties") or {}
            c=p.get("litoralcode")
            if c is not None:classes[str(c)]+=1
        out.update({
            "status":"SOURCE_WFS_ORIGINAL_GEOJSON_SAMPLE",
            "source_native_returned_features":len(feature),
            "reported_numberMatched":q.get("numberMatched"),
            "actual_original_class_sample_counts":dict(classes),
            "no_raw_polygon_geometry_published":True})
        return out
    except (ValueError,TypeError):
        try:
            root=ET.fromstring(data)
            matched=root.attrib.get("numberMatched")
            if root.tag.endswith("ExceptionReport"):
                out["status"]="SOURCE_WFS_EXCEPTION"
            else:
                out["status"]="SOURCE_WFS_NON_GEOJSON_HITS"
            out["reported_numberMatched"]=matched
            return out
        except ET.ParseError:
            out["status"]="SOURCE_RESPONSE_NOT_READABLE"
            out["source_non_geometry_prefix"]=data[:140].decode("utf8","replace")
            return out

def diagnostic_one_site(site,bbox,fetch=None):
    if site not in FIXED_SITE_BBOX or tuple(bbox)!=FIXED_SITE_BBOX[site]:
        raise ValueError("SOURCE_STOP_V84B_UNFROZEN_SITE_BBOX")
    base={
        "bbox":",".join(f"{x:.5f}" for x in bbox)+",CRS:84"}
    attempts={}
    for name,extra in QUERY_SETTINGS:
        status,data,error=_request({**base,**extra},fetch=fetch)
        attempts[name]=parse_native_return(status,data,error)
    return attempts

def run(output):
    report={
        "analysis":"V84B_WMR_NATIVE_WFS_HTTP_500_SHAPE_FILTER_PAGINATION_SOURCE_DIAGNOSTIC",
        "published_original_WMR_source":BASE,
        "original_fixed_native_feature_layer":MAIN,
        "original_2021_corrected_v2_source_NOT_VERIFIED":True,
        "original_bird_GPS_or_tide_model_likelihood_NOT_EXAMINED":True,
        "source_requests":{}}
    for site,bbox in FIXED_SITE_BBOX.items():
        attempts=diagnostic_one_site(site,bbox)
        report["source_requests"][site]=attempts
        print("V84B_WMR_WFS_QUERY_SHAPE_DIAGNOSTICS "+json.dumps({
            "site":site,
            "original_native_source_conditions":{
                q:{"status":a["status"],"http":a["http_status"],
                   "features":a.get("source_native_returned_features"),
                   "reported_hits":a.get("reported_numberMatched"),
                   "error":a.get("source_error_excerpt_if_any")}
                for q,a in attempts.items()}},
            sort_keys=True),flush=True)
    public=report["source_requests"]
    cql_any=all(any(x["status"]=="SOURCE_WFS_ORIGINAL_GEOJSON_SAMPLE"
        for label,x in src.items() if label.startswith("CQL"))
        for src in public.values())
    unfiltered=all(src["UNFILTERED10"]["status"]==
                   "SOURCE_WFS_ORIGINAL_GEOJSON_SAMPLE"
                   for src in public.values())
    if cql_any:
        status="ORIGINAL_WMR_CQL_FILTER_PARTIAL_SAMPLE_WORKS_NO_FULL_GIS_ADMISSION"
    elif unfiltered:
        status="ORIGINAL_WMR_UNFILTERED_SOURCE_AVAILABLE_CQL_UNSUPPORTED_NO_FULL_GIS_ADMISSION"
    else:
        status="ORIGINAL_WMR_WFS_ORIGINAL_GEOMETRIES_NOT_ACCESSIBLE_NO_GIS_ADMISSION"
    report["source_diagnostic_conclusion"]=status
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V84B_WMR_ORIGINAL_GEOSERVER_SOURCE_QUERY_CONCLUSION "+json.dumps({
        "result":status,"no_bird_or_published_corrected_v2_claim":True},
        sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    run(p.parse_args().output)
