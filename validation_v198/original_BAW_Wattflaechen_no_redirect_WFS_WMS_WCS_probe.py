"""BAW TrilaWatt Wattflächen official source-only HTTP redirects for WFS/WMS/WCS.
Verified default CA only, redirects NEVER followed, no raw WFS features or WCS coverages.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request,urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter

URLS={
"WFS":"https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS",
"WMS":"https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wms?REQUEST=GetCapabilities&SERVICE=WMS",
"WCS":"https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs?REQUEST=GetCapabilities&SERVICE=WCS&VERSION=2.0.1",
}
MAX_XML_BYTES=4_000_000
OUT=Path(__file__).resolve().parent/"results/native_BAW_Wattflaechen_WFS_WMS_WCS_verified_redirect_source_v198.json"

class NeverFollowHTTPRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def validate_original_url(original,service):
    if original!=URLS[service]:raise ValueError("NOT_EXACT_BAW_PUBLISHED_SERVICE_URL")
    x=urllib.parse.urlsplit(original)
    return (x.scheme=="https" and x.hostname=="mdi-dienste.baw.de"
        and x.path==f"/geoserver/TrilaWatt_Wattflaechen/{service.lower()}"
        and x.port is None and x.username is None and x.password is None)

def direct_original_verified_https_get(url,service):
    if service not in URLS or not validate_original_url(url,service):
        raise ValueError("STOP_BAD_OFFICIAL_WATTFLAECHEN_SERVICE_URL")
    handler=urllib.request.HTTPSHandler(context=ssl.create_default_context())
    op=urllib.request.build_opener(handler,NeverFollowHTTPRedirects())
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v198-original-BAW-Wattflaechen-REDIRECT-DIAGNOSTIC/1.0",
        "Accept":"application/xml,text/xml"})
    try:
        with op.open(req,timeout=38) as r:
            status=r.status
            final=r.geturl()
            raw=r.read(MAX_XML_BYTES+1)
            ct=r.headers.get("Content-Type")
        if final!=url or status!=200 or len(raw)>MAX_XML_BYTES or not raw:
            raise ValueError("SOURCE_STOP_UNEXPECTED_OR_OVERSIZED_ORIGINAL_RESPONSE")
        return raw,{"status":"SOURCE_HTTP200_DIRECT_ORIGINAL_TLS_CA_VERIFIED",
           "native_response_http_status":status,
           "original_byte_length":len(raw),
           "original_XML_SHA256":hashlib.sha256(raw).hexdigest(),
           "source_content_type":ct,
           "no_original_geofeatures_or_rasters_downloaded":True}
    except urllib.error.HTTPError as exc:
        native_location=exc.headers.get("Location")
        next_absolute=urllib.parse.urljoin(url,native_location) if native_location else None
        next_parts=urllib.parse.urlsplit(next_absolute or "")
        redirect=exc.code in (301,302,303,307,308)
        return None,{"status":"SOURCE_STOP_UNFOLLOWED_OFFICIAL_HTTP_REDIRECT" if redirect
                     else "SOURCE_STOP_OFFICIAL_NATIVE_HTTP_ERROR",
            "native_response_http_status":exc.code,
            "original_HTTP_Location_header":native_location,
            "unfollowed_absolute_location":next_absolute,
            "destination_https":next_parts.scheme=="https",
            "destination_host":next_parts.hostname,
            "redirect_was_NOT_followed":True,
            "native_content_type":exc.headers.get("Content-Type"),
            "original_XML_SHA256":None,
            "no_original_geofeatures_or_rasters_downloaded":True}

def local_name(n):
    return n.rsplit("}",1)[-1].split(":")[-1]

def get_direct_child(node,name):
    for child in node:
        if local_name(child.tag).lower()==name.lower():
            return (child.text or "").strip()
    return None

def inspect_ogc_metadata(raw,service):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_XML_DTD_OR_ENTITY_FORBIDDEN")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("STOP_ORIGINAL_SERVICE_CAPABILITIES_XML_INVALID") from exc
    rt=local_name(root.tag).lower()
    accepted={
        "WFS":("wfs_capabilities",),
        "WMS":("wms_capabilities","wmt_ms_capabilities"),
        "WCS":("wcs_capabilities","capabilities"),
    }
    if rt not in accepted[service]:
        raise ValueError("STOP_ORIGINAL_SERVICE_MISMATCH_OR_XML_ERROR")
    tag={"WFS":"FeatureType","WMS":"Layer","WCS":"CoverageSummary"}[service]
    found=[]
    for node in root.iter():
        if local_name(node.tag)!=tag:continue
        nm=get_direct_child(node,"Name") or get_direct_child(node,"CoverageId")
        title=get_direct_child(node,"Title")
        if nm:
            found.append({"name":nm[:190],"title":(title or "")[:190]})
    if not found: raise ValueError("STOP_SOURCE_ORIGINAL_WATTFLAECHEN_NO_NAMED_LAYER")
    years={str(y):[r["name"] for r in found if str(y) in (
           r["name"]+" "+r["title"])] for y in (2018,2019)}
    return {
       "service":service,
       "root":local_name(root.tag),
       "native_version":root.attrib.get("version"),
       "original_layer_count":len(found),
       "native_original_layer_names_cap100":found[:100],
       "2018_NL_candidate_layer_names":years["2018"][:30],
       "2019_NL_candidate_layer_names":years["2019"][:30],
       "no_original_feature_geom_or_WMS_height_grid_or_NC_native_datum":True,
    }

def run(out=OUT):
    result={"version":"v198-original-BAW-Wattflaechen-WFS-WMS-WCS-direct-verified-HTTPS-diagnostic",
        "published_sources":URLS,
        "native_source_redirects_NEVER_followed":True,
        "v196_WFS_original_authentication_stopped_before_feature_metadata":True,
        "no_raw_model_or_original_birdGPS_ACC_DEM":True,
        "status":"SOURCE_DIAGNOSTIC_NOT_PHYSICAL_ADMISSION"}
    stats={}
    for service,url in URLS.items():
        try:
            body,receipt=direct_original_verified_https_get(url,service)
            if body is not None:
                receipt["native_Capabilities_metadata"]=inspect_ogc_metadata(body,service)
            stats[service]=receipt
        except Exception as err:
            stats[service]={"status":"SOURCE_STOP_TLS_OR_NATIVE_XML_REJECTED",
                "error_kind":type(err).__name__,
                "error_summary":str(err)[:220]}
    result["three_official_service_diagnostics"]=stats
    result["source_gates"]={
        "n_official_verified_TLS_HTTP200_with_original_metadata":sum(
            s.get("status")=="SOURCE_HTTP200_DIRECT_ORIGINAL_TLS_CA_VERIFIED" and
            "native_Capabilities_metadata" in s for s in stats.values()),
        "n_original_redirects_refused":sum(
            s.get("status")=="SOURCE_STOP_UNFOLLOWED_OFFICIAL_HTTP_REDIRECT" for s in stats.values()),
        "all_original_WFS_WMS_WCS_metadata_verified":all(
            s.get("status")=="SOURCE_HTTP200_DIRECT_ORIGINAL_TLS_CA_VERIFIED"
            and "native_Capabilities_metadata" in s for s in stats.values()),
        "original_2018_2019_annual_intertidal_NL_shape_admitted":False,
        "local_bird_GPS_tide_event_specific_wetdry_admitted":False,
        "native_original_WFS_GetFeature_downloaded":False,
    }
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V198_OFFICIAL_WATTFLAECHEN_REDIRECT="+json.dumps({
        "status":result["status"],"gates":result["source_gates"],
        "services":{k:{"status":v.get("status"),"http":v.get("native_response_http_status"),
          "Location":v.get("unfollowed_absolute_location"),
          "https_dest":v.get("destination_https"),
          "target_host":v.get("destination_host"),
          "source_layer_count":v.get("native_Capabilities_metadata",{}).get("original_layer_count"),
          "source_layer_names":v.get("native_Capabilities_metadata",{}).get("native_original_layer_names_cap100")
          } for k,v in stats.items()},
        "never_followed_unknown_redirect_or_used_insecure_TLS":True,
    },sort_keys=True))
    return result

if __name__=="__main__":
    run()
