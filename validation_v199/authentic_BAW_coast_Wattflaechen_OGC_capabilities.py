"""v199: direct original verified BAW coast.baw.de WFS/WMS/WCS capabilities.

Exact destination URLs copied from v198 genuine official HTTP308 Location headers.
Never auto follow other redirects, bypass HTTPS CA, or get features/coverages.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request,urllib.error
from pathlib import Path
from original_BAW_Wattflaechen_no_redirect_WFS_WMS_WCS_probe import (
    URLS as OLD_BAW_ORIGINAL, NeverFollowHTTPRedirects,inspect_ogc_metadata
)

DESTINATIONS={
    "WFS":"https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS",
    "WMS":"https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wms?REQUEST=GetCapabilities&SERVICE=WMS",
    "WCS":"https://coast.baw.de/geoserver/TrilaWatt_Wattflaechen/wcs?REQUEST=GetCapabilities&SERVICE=WCS&VERSION=2.0.1",
}
EVIDENCE_308_RUNS=(44429348878,44429376545)
MAX_RESPONSE_BYTES=4_000_000
OUT=Path(__file__).resolve().parent/"results/authentic_BAW_coast_Wattflaechen_WFS_WMS_WCS_source_v199.json"

def only_pinned_original_destination(url,service):
    if service not in DESTINATIONS or url!=DESTINATIONS[service]:
        raise ValueError("STOP_UNPINNED_ORIGINAL_BAW_REDIRECT_TARGET")
    p=urllib.parse.urlsplit(url)
    return (p.scheme=="https" and p.hostname=="coast.baw.de"
        and p.port is None and p.username is None and p.password is None
        and p.path==f"/geoserver/TrilaWatt_Wattflaechen/{service.lower()}")

def verified_direct_baw_OGC_GET(url,service):
    if not only_pinned_original_destination(url,service):
        raise ValueError("STOP_NOT_BAW_OFFICIAL_ORIGINAL_DIRECT_ENDPOINT")
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v199-exact-official-BAW-original-Wattflaechen-redirect-destination/1.0",
        "Accept":"application/xml,text/xml"})
    op=urllib.request.build_opener(
      urllib.request.HTTPSHandler(context=ssl.create_default_context()),
      NeverFollowHTTPRedirects())
    try:
        with op.open(req,timeout=33) as r:
            status=r.status
            original=r.read(MAX_RESPONSE_BYTES+1)
            final=r.geturl()
            ct=r.headers.get("Content-Type")
        if status!=200 or final!=url or not original or len(original)>MAX_RESPONSE_BYTES:
            raise ValueError("SOURCE_STOP_ORIGINAL_BAW_NOT200_OR_TOO_LARGE")
        return original,{"original_response_status":status,
                "original_XML_SHA256":hashlib.sha256(original).hexdigest(),
                "original_XML_bytes":len(original),
                "original_response_content_type":ct,
                "original_direct_TLS_CA_verified":True,
                "any_redirect_auto_followed":False}
    except urllib.error.HTTPError as e:
        return None,{"original_response_status":e.code,
           "redirect_Location_header_UNFOLLOWED":e.headers.get("Location"),
           "original_source_HTTP_error_type":"redirect" if e.code in (301,302,303,307,308) else "HTTP_error",
           "any_redirect_auto_followed":False}

def run(out=OUT):
    data={"analysis":"v199-original-direct-official-coast-BAW-Wattflaechen-WFS-WMS-WCS",
          "official_original_308_location_sources":EVIDENCE_308_RUNS,
          "frozen_original_HTTP308_locations":DESTINATIONS,
          "insecure_TLS_or_unapproved_redirects_never_used":True,
          "status":"SOURCE_STOP_METADATA"}
    sources={}
    for service,url in DESTINATIONS.items():
        try:
            xml,receipt=verified_direct_baw_OGC_GET(url,service)
            src={"status":"ORIGINAL_VERIFIED_CAPABILITIES" if xml else "SOURCE_STOP_NO_ORIGINAL_XML",
                 "native_verified_source_HTTP":receipt}
            if xml:
                src["native_OGC_metadata"]=inspect_ogc_metadata(xml,service)
        except Exception as err:
            src={"status":"SOURCE_STOP_ORIGINAL_BAW_METADATA_INVALID",
                "error_type":type(err).__name__,"error_summary":str(err)[:210]}
        sources[service]=src
    data["source_results"]=sources
    data["scientific_gates"]={
       "genuine_original_WFS_native_featuretypes_admitted":sources["WFS"]["status"]=="ORIGINAL_VERIFIED_CAPABILITIES",
       "genuine_original_WMS_native_layers_admitted":sources["WMS"]["status"]=="ORIGINAL_VERIFIED_CAPABILITIES",
       "genuine_original_WCS_native_coverages_admitted":sources["WCS"]["status"]=="ORIGINAL_VERIFIED_CAPABILITIES",
       "2018_2019_NL_intertidal_polygon_original_geometry_admitted":False,
       "native_raster_or_vector_feature_get_downloaded":False,
       "event_specific_local_bird_GPS_tide_or_dryflat_admitted":False,
       "animal_Boids_or_sun_tide_foraging_effect_estimated":False,
    }
    if data["scientific_gates"]["genuine_original_WFS_native_featuretypes_admitted"]:
        data["status"]="ORIGINAL_BAW_WFS_FEATURETYPE_CAPABILITIES_ADMITTED_YEAR_GEOGRAPHY_NOT_VERIFIED"
    else:
        data["status"]="SOURCE_STOP_BAW_ORIGINAL_WFS_CAPABILITIES_NOT_VERIFIED"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V199_BAW_COAST_WATTFLAECHEN_CAPABILITIES="+json.dumps({
       "status":data["status"],"gates":data["scientific_gates"],
       "services":{key:{"status":r["status"],
         "HTTP":r.get("native_verified_source_HTTP",{}).get("original_response_status"),
         "SHA":r.get("native_verified_source_HTTP",{}).get("original_XML_SHA256"),
         "n_layers":r.get("native_OGC_metadata",{}).get("original_layer_count"),
         "layers":r.get("native_OGC_metadata",{}).get("native_original_layer_names_cap100"),
         "2018_names":r.get("native_OGC_metadata",{}).get("2018_NL_candidate_layer_names"),
         "2019_names":r.get("native_OGC_metadata",{}).get("2019_NL_candidate_layer_names"),
         "error":r.get("error_summary"),
         "new_redirect_NOT_followed":r.get("native_verified_source_HTTP",{}).get("redirect_Location_header_UNFOLLOWED")}
         for key,r in sources.items()},
       "no_model_polygons_or_local_bird_behavior_downloaded":True
    },sort_keys=True))
    return data

if __name__=="__main__":
    run()
