"""v196 BAW original Wadden intertidal zones 2015-21 WFS metadata source-only.

Annual intertidal polygons are NOT 15-min local wet/dry, GPS exposure, tide
height, proven original field survey dates, or an animal behavior effect.
Never request WFS GetFeature, GeoTIFF or original shape payload in this gate.
"""
from __future__ import annotations
import hashlib
import json
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

WFS_OFFICIAL="https://mdi-dienste.baw.de/geoserver/TrilaWatt_Wattflaechen/wfs?REQUEST=GetCapabilities&SERVICE=WFS"
PUBLISHER_DOI="https://doi.org/10.48437/5a882d-b3a571"
PUBLISHER_METADATA="https://datenrepository.baw.de/trefferanzeige?docuuid=71E27987-B679-4F75-9874-5A882DB3A571"
MAX_SOURCE_XML=4_000_000
OUT=Path(__file__).resolve().parent/"results/authentic_BAW_Wattflaechen_2018_2019_WFS_source_v196.json"

def is_official_WFS_url(url):
    u=urllib.parse.urlsplit(url)
    return u.scheme=="https" and u.hostname=="mdi-dienste.baw.de" and u.port is None and (
        u.path=="/geoserver/TrilaWatt_Wattflaechen/wfs"
    ) and "getcapabilities" in u.query.lower() and "wfs" in u.query.lower()

class ExactWFSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not is_official_WFS_url(newurl):
            raise ValueError("STOP_WFS_REDIRECT_TO_NONPUBLIC_OR_NONCAPABILITY_SOURCE")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def get_native_WFS_capabilities(url=WFS_OFFICIAL):
    if not is_official_WFS_url(url):
        raise ValueError("STOP_WFS_NONOFFICIAL_URL")
    request=urllib.request.Request(url,method="GET",headers={
        "User-Agent":"boids-v196-original-BAW-Wattflaechen-WFS-2018-2019-METADATA-only/1.0",
        "Accept":"text/xml,application/xml"})
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        ExactWFSRedirect())
    with opener.open(request,timeout=36) as resp:
        status=resp.status
        final=resp.geturl()
        blob=resp.read(MAX_SOURCE_XML+1)
        ct=resp.headers.get("Content-Type")
    if not is_official_WFS_url(final) or status!=200 or len(blob)>MAX_SOURCE_XML or not blob:
        raise ValueError("STOP_OFFICIAL_NATIVE_WFS_HTTP_OR_XML_TOO_LARGE")
    return blob,{"official_published_source_url":url,
        "final_original_TLS_verified_URL":final,
        "source_http_status":status,
        "source_content_type":ct,
        "native_original_XML_SHA256":hashlib.sha256(blob).hexdigest(),
        "original_XML_bytes":len(blob),
        "TLS_CA_validation_enabled":True}

def strip(tag):
    return tag.rsplit("}",1)[-1] if "}" in tag else tag.split(":",1)[-1]

def direct_text(node,name):
    for child in node:
        if strip(child.tag).lower()==name.lower():
            return (child.text or "").strip()
    return None

def candidate_original_NL_layer_year(record,year):
    text=(str(record.get("name") or "")+" "+str(record.get("title") or "")).lower()
    contains_year=str(year) in text
    normalized=text.replace("niederlande","nederland").replace("netherlands","nederland")
    contains_NL=bool(re.search(r"(^|[^a-z])nl([^a-z]|$)",normalized)) or "nederland" in normalized
    return contains_year and contains_NL

def inspect_authentic_WFS_source(xml:bytes):
    if b"<!DOCTYPE" in xml.upper() or b"<!ENTITY" in xml.upper():
        raise ValueError("STOP_WFS_XML_UNTRUSTED_DTD_OR_ENTITY")
    try:
        root=ET.fromstring(xml)
    except ET.ParseError as err:
        raise ValueError("STOP_NOT_PARSEABLE_NATIVE_WFS_XML") from err
    rootname=strip(root.tag)
    if rootname.lower()!="wfs_capabilities":
        raise ValueError("STOP_NOT_ORIGINAL_WFS_CAPABILITIES")
    ver=root.attrib.get("version")
    if not ver:raise ValueError("STOP_ORIGINAL_WFS_VERSION_MISSING")
    records=[]
    ops=[]
    for item in root.iter():
        if strip(item.tag)=="Operation":
            nm=item.attrib.get("name")
            if nm and nm not in ops:ops.append(nm[:100])
        elif strip(item.tag)=="FeatureType":
            name=direct_text(item,"Name")
            if not name:continue
            title=direct_text(item,"Title")
            crs=direct_text(item,"DefaultCRS") or direct_text(item,"DefaultSRS")
            low=high=None
            for child in item:
                if strip(child.tag)!="WGS84BoundingBox":continue
                low=direct_text(child,"LowerCorner")
                high=direct_text(child,"UpperCorner")
            records.append({"name":name[:180],"title":(title or "")[:180],
                "native_DefaultCRS":(crs or "")[:120],
                "native_WGS84_lower_corner":(low or "")[:120],
                "native_WGS84_upper_corner":(high or "")[:120]})
    if not records:raise ValueError("STOP_NATIVE_WFS_NO_FEATURE_TYPES")
    candidates={str(year):[r for r in records if candidate_original_NL_layer_year(r,year)]
                for year in (2018,2019)}
    return {"native_WFS_root":rootname,"native_WFS_version":ver,
        "native_WFS_operations":ops[:30],
        "all_original_feature_type_names_capped_150":[r["name"] for r in records[:150]],
        "n_native_feature_types":len(records),
        "native_2018_2019_NL_feature_type_candidates":candidates,
        "original_native_NL_year_exactly_one_candidate_each":
             all(len(r)==1 for r in candidates.values()),
        "native_annual_intertidal_geography_NOT_instantaneous_exposure":True,
        "native_feature_geometry_and_time_of_survey_not_retrieved":True}

def run(output=OUT):
    out={"version":"v196-BAW-original-intertidal-2018-2019-featureType-WFS-source-only",
        "original_BAW_dataset_DOI":PUBLISHER_DOI,
        "original_BAW_metadata_page":PUBLISHER_METADATA,
        "original_published_WFS_URL":WFS_OFFICIAL,
        "BAW_published_annual_high_low_water_boundary_model_uncertainty_cm":25,
        "published_years":"2015-2021",
        "publisher_stated_annual_mean_intertidal_zone_NOT_event_exposure":True,
        "native_original_wet_dry_or_bird_GPS_not_downloaded":True,
        "status":"SOURCE_STOP"}
    try:
        raw,receipt=get_native_WFS_capabilities()
        metadata=inspect_authentic_WFS_source(raw)
        out["original_native_WFS_download_receipt"]=receipt
        out["original_native_WFS_featureType_metadata"]=metadata
        if metadata["original_native_NL_year_exactly_one_candidate_each"]:
            out["status"]="ORIGINAL_2018_2019_NL_INTERTIDAL_FEATURE_TYPE_METADATA_ADMITTED_NO_FEATURE_GEOMETRY"
        else:
            out["status"]="ORIGINAL_WFS_AUTHENTIC_NL_YEAR_FEATURE_TYPE_AMBIGUOUS_OR_MISSING"
    except Exception as exc:
        out["status"]="SOURCE_STOP_ORIGINAL_WFS_UNAVAILABLE_OR_INVALID"
        out["source_error_kind"]=type(exc).__name__
        out["source_error_summary"]=str(exc)[:220]
    out["scientific_gates"]={
        "original_TLS_verified_official_WFS_XML":bool(out.get("original_native_WFS_download_receipt")),
        "native_unambiguous_2018_and_2019_NL_intertidal_features":
            bool(out.get("original_native_WFS_featureType_metadata",{}).get("original_native_NL_year_exactly_one_candidate_each")),
        "original_annual_polygon_geometry_retrieved":False,
        "exact_published_2018_and_2019_GPS_cell_intertidal_overlap":False,
        "quarterhour_true_local_dryflat_exposure_from_annual_polygon":False,
        "native_hydrodynamic_height_and_historical_DEM_vertical_datum_calibrated":False,
        "bird_ACC_Boids_tide_solar_effect_estimated":False,
    }
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(out,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V196_NATIVE_BAW_INTERTIDAL_SOURCE_SCOPE="+json.dumps({
        "status":out["status"],
        "source_error":out.get("source_error_summary"),
        "gates":out["scientific_gates"],
        "source_NL_year_layer_candidates":
            out.get("original_native_WFS_featureType_metadata",{}).get("native_2018_2019_NL_feature_type_candidates"),
        "source_native_feature_type_count":
            out.get("original_native_WFS_featureType_metadata",{}).get("n_native_feature_types"),
        "no_bird_or_event_dryflat_result":True
    },sort_keys=True),flush=True)
    return out

if __name__=="__main__":run()
