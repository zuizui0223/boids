"""v194: independently published BAW official yearly TrilaWatt WMS capabilities, HTTPS verified.

NOT a native NetCDF download, not a numeric tide field, and not a GPS local tide model.
Do NOT bypass TLS verification, downgrade to HTTP, or assume WMS image equals water level.
"""
from __future__ import annotations
import hashlib
import json
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

OFFICIAL_YEAR_WMS={
    "2018":"https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2018/wms?service=WMS&version=1.3.0&request=GetCapabilities",
    "2019":"https://coast.baw.de/geoserver/TrilaWatt_ncHydro_2019/wms?service=WMS&version=1.3.0&request=GetCapabilities",
}
OFFICIAL_CENTRAL_WMS="https://mdi-dienste.baw.de/ncWMS2_Trilawatt/wms?REQUEST=GetCapabilities&SERVICE=WMS"
# Listed by BAW official metadata pages, not guessed via year substitutions.
ALLOWED_HOSTS=frozenset({"coast.baw.de","mdi-dienste.baw.de"})
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"validation_v194/results/original_BAW_2018_2019_verified_WMS_capabilities_v194.json"
MAX_XML_BYTES=4_000_000

def official_verified_endpoint(url):
    x=urllib.parse.urlsplit(url)
    return (x.scheme=="https" and x.hostname in ALLOWED_HOSTS
            and x.username is None and x.password is None and x.port is None
            and not x.fragment and ("GetCapabilities" in urllib.parse.unquote(x.query)
                                    or "getcapabilities" in x.query.lower())
            and (x.path.startswith("/geoserver/TrilaWatt_ncHydro_")
                 or x.path=="/ncWMS2_Trilawatt/wms"))

class StrictBAWRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not official_verified_endpoint(newurl):
            raise ValueError("SOURCE_STOP_TLS_REDIRECT_TO_UNAPPROVED_HOST_OR_WMS")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def fetch_verified_original_WMS(url):
    if not official_verified_endpoint(url):
        raise ValueError("SOURCE_STOP_UNAUTHORIZED_OR_NONHTTPS_BAW_ENDPOINT")
    context=ssl.create_default_context()  # verified default CAs ONLY
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context),
        StrictBAWRedirect(),
    )
    req=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v194-original-BAW-TrilaWatt-2018-2019-WMS-source-audit/1.0",
        "Accept":"application/xml,text/xml,*/*"})
    with opener.open(req,timeout=32) as response:
        raw=response.read(MAX_XML_BYTES+1)
        final=response.geturl()
        status=response.status
        content_type=response.headers.get("Content-Type")
    if not official_verified_endpoint(final):
        raise ValueError("SOURCE_STOP_POSTREDIRECT_UNTRUSTED_FINAL_WMS_ENDPOINT")
    if status!=200 or len(raw)>MAX_XML_BYTES or not raw:
        raise ValueError("SOURCE_STOP_ORIGINAL_WMS_HTTP_BODY_TOO_BIG_EMPTY_OR_NOT200")
    return raw,{"original_published_url":url,"final_verified_original_url":final,
                "verified_https_CA_default":True,
                "http_status":status,"content_type":content_type,
                "original_WMS_xml_bytes":len(raw),
                "original_WMS_xml_SHA256":hashlib.sha256(raw).hexdigest()}

def bare_tag(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag.split(":",1)[-1]

def text_of(parent,name):
    for child in parent:
        if bare_tag(child.tag).lower()==name.lower():
            return (child.text or "").strip()
    return None

def inspect_WMS_xml(raw:bytes,target_year=None):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("SOURCE_STOP_WMS_XML_EXTERNAL_DTD_OR_ENTITY")
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError("SOURCE_STOP_WMS_NOT_VALID_XML") from exc
    rootname=bare_tag(root.tag)
    if rootname.lower() not in ("wms_capabilities","wmt_ms_capabilities"):
        raise ValueError("SOURCE_STOP_NOT_AUTHENTIC_OGC_WMS_CAPABILITIES")
    version=root.attrib.get("version")
    layer_names=[]
    water_layers=[]
    time_dimensions=[]
    declared_years=set()
    for layer in root.iter():
        if bare_tag(layer.tag)!="Layer":continue
        name=text_of(layer,"Name")
        title=text_of(layer,"Title")
        if name and len(layer_names)<75:
            layer_names.append(name[:200])
        if name:
            n=(name+" "+str(title or "")).lower()
            if (any(w in n for w in (
                "sea_surface_height","sea surface height",
                "water_level","water level","waterstand","waterhoogte",
                "water_elevation","surface_elevation","ssh","zeta"))
                and len(water_layers)<45):
                water_layers.append({"name":name[:200],"title":(title or "")[:200]})
        for child in layer:
            if bare_tag(child.tag).lower() not in ("dimension","extent"):continue
            if str(child.attrib.get("name","")).lower()!="time":continue
            t=(child.text or "").strip()
            if not t:continue
            declared_years.update(re.findall(r"\b(20(?:1[5-9]|2[0-2]))[-/]",t))
            if len(time_dimensions)<15:
                time_dimensions.append({"layer_name":(name or "")[:160],
                   "original_time_expression_prefix":t[:160],
                   "expression_length":len(t),
                   "original_time_expression_SHA256":hashlib.sha256(t.encode()).hexdigest()})
    if not version or not layer_names:
        raise ValueError("SOURCE_STOP_WMS_NO_VALID_VERSION_OR_NAMED_LAYER")
    combined=(" ".join(layer_names)+" "+ " ".join(
        t["original_time_expression_prefix"] for t in time_dimensions))
    native_target_year_evident=(target_year is not None and
        (target_year in declared_years or target_year in combined))
    return {"native_OGC_WMS_root":rootname,"native_WMS_version":version,
        "named_layers_retained_cap75":layer_names,
        "n_named_layers_at_least":len(layer_names),
        "source_layer_time_dimensions_cap15":time_dimensions,
        "source_tide_water_height_named_layers_cap45":water_layers,
        "native_service_metadata_declares_target_year":native_target_year_evident,
        "does_not_verify_native_model_water_level_or_vertical_datum":True,
        "does_not_verify_model_GPS_cell_or_independence_from_RWS_gauges":True}

def run(output=OUT):
    results={"version":"v194-official-BAW-yearly-WMS-native-TLS-source-only",
        "status":"SOURCE_STOP_ORIGINAL_YEAR_WMS_CAPABILITIES",
        "official_yearly_WMS":OFFICIAL_YEAR_WMS,
        "official_multiannual_WMS":OFFICIAL_CENTRAL_WMS,
        "v193_failed_verified_certificate_chain_for_download_hostname":True,
        "ssl_verification_disabled":False,
        "local_bird_GPS_tide_and_bathymetric_exposure_admitted":False,
        "no_annual_netCDF_or_original_gauge_or_bird_data_downloaded":True,
        "system_CA_openSSL_version":ssl.OPENSSL_VERSION}
    year_records={}
    for year,url in OFFICIAL_YEAR_WMS.items():
        try:
            raw,receipt=fetch_verified_original_WMS(url)
            native=inspect_WMS_xml(raw,target_year=year)
            year_records[year]={"status":"VERIFIED_OFFICIAL_ORIGINAL_WMS_CAPABILITIES",
                               "original_TLS_verified_source":receipt,
                               "native_WMS_metadata":native}
        except Exception as exc:
            year_records[year]={"status":"SOURCE_STOP_WMS_OR_TLS_UNVERIFIED",
                "error_kind":type(exc).__name__,
                "error_message":str(exc)[:240]}
    try:
        raw,receipt=fetch_verified_original_WMS(OFFICIAL_CENTRAL_WMS)
        central={"status":"VERIFIED_OFFICIAL_ORIGINAL_CENTRAL_WMS_CAPABILITIES",
            "original_TLS_verified_source":receipt,
            "native_WMS_metadata":inspect_WMS_xml(raw)}
    except Exception as exc:
        central={"status":"SOURCE_STOP_CENTRAL_WMS_OR_TLS_UNVERIFIED",
            "error_kind":type(exc).__name__,"error_message":str(exc)[:240]}
    results["year_specific_original_WMS_source_evidence"]=year_records
    results["official_central_WMS_source_evidence"]=central
    results["scientific_source_gates"]={
       "both_year_original_WMS_TLS_XML_verified":all(
         x["status"]=="VERIFIED_OFFICIAL_ORIGINAL_WMS_CAPABILITIES" for x in year_records.values()),
       "both_year_metadata_exposes_tide_height_named_layer":all(
         bool(x.get("native_WMS_metadata",{}).get("source_tide_water_height_named_layers_cap45"))
         for x in year_records.values()),
       "both_year_native_metadata_discloses_requested_year":all(
         bool(x.get("native_WMS_metadata",{}).get("native_service_metadata_declares_target_year"))
         for x in year_records.values()),
       "native_NetCDF_binary_source_admitted":False,
       "numerical_sea_surface_height_2d_from_GPS_site_verified":False,
       "vertical_datum_model_to_original_DEM_NAP_harmonized":False,
       "true_survey_day_and_historical_terrain_change_verified":False,
       "bird_foraging_or_sun_by_tide_mechanism_estimated":False,
    }
    gate=results["scientific_source_gates"]
    if gate["both_year_original_WMS_TLS_XML_verified"]:
        results["status"]="ORIGINAL_TWO_YEAR_BAW_WMS_CAPABILITIES_TLS_VERIFIED_ONLY"
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(results,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V194_OFFICIAL_WMS_SOURCE_SCOPE="+json.dumps({
        "status":results["status"],
        "scientific_source_gates":gate,
        "yearly_sources":{year:{
          "status":r["status"],
          "error":r.get("error_message"),
          "named_height_layers":r.get("native_WMS_metadata",{}).get("source_tide_water_height_named_layers_cap45"),
          "native_year":r.get("native_WMS_metadata",{}).get("native_service_metadata_declares_target_year"),
          "capability_sha":r.get("original_TLS_verified_source",{}).get("original_WMS_xml_SHA256")
        } for year,r in year_records.items()},
        "central_status":central["status"],
        "central_error":central.get("error_message"),
        "no_local_GPS_tide_or_ecology":True
    },sort_keys=True),flush=True)
    return results

if __name__=="__main__":run()
