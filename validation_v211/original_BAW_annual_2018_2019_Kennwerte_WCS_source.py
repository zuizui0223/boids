"""v211: original BAW annual Kennwerte WCS 2018/19 source COVERAGE metadata only.
Annual always-flooded filter, no_filter and valid-count are product-level facts.
They do not establish raw 20min WMS 1e31 _FillValue or physical dry-cell cause.
No WCS GetCoverage, raw TIFF, bird GPS, ACC or individual RWS measurements.
"""
from __future__ import annotations
import hashlib
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OFFICIAL_SOURCE_URLS = {
 "2018":"https://mdi-dienste.baw.de/geoserver/TrilaWatt_Hydrodynamik_2018/ows?service=WCS&version=2.0.1&request=GetCapabilities&REQUEST=GetCapabilities&SERVICE=WCS",
 "2019":"https://mdi-dienste.baw.de/geoserver/TrilaWatt_Hydrodynamik_2019/ows?service=WCS&version=2.0.1&request=GetCapabilities&REQUEST=GetCapabilities&SERVICE=WCS",
}
OFFICIAL_BAW_RECORDS={
 "2018":"FE9AA7AE-7BAC-45E8-8918-A55BC6EEA645",
 "2019":"49CA8C6A-A6F2-4847-91D6-77D01C0CDDBD",
}
MAX_SOURCE_BYTES=8_000_000
OUT=Path(__file__).resolve().parent/"results/original_2018_2019_BAW_annual_Kennwerte_no_filter_validcount_WCS_v211.json"

class RefuseUnverifiedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None

def is_approved_original_year_url(url,year,host):
    if year not in OFFICIAL_SOURCE_URLS:
        return False
    p=urllib.parse.urlsplit(url)
    if not (p.scheme=="https" and p.hostname==host and p.port is None
        and p.username is None and p.password is None and not p.fragment
        and p.path==f"/geoserver/TrilaWatt_Hydrodynamik_{year}/ows"):
        return False
    pairs=urllib.parse.parse_qsl(p.query,keep_blank_values=True)
    values={}
    for k,v in pairs:
        k=k.lower()
        v=v.lower()
        if k in values and values[k]!=v:
            return False
        values[k]=v
    return values=={"service":"wcs","version":"2.0.1","request":"getcapabilities"}

def original_baw_https_one_response(url,year,host):
    if not is_approved_original_year_url(url,year,host):
        raise ValueError("STOP_NONFROZEN_ORIGINAL_BAW_YEAR_WCS_URL")
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v211-original-BAW-annual-2018-2019-valid-count-source/1.0",
       "Accept":"application/xml,text/xml"})
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        RefuseUnverifiedRedirect())
    try:
        with opener.open(req,timeout=35) as response:
            original=response.read(MAX_SOURCE_BYTES+1)
            status=response.status
            final=response.geturl()
            ct=response.headers.get("Content-Type")
        if status!=200 or final!=url or not original or len(original)>MAX_SOURCE_BYTES:
            raise ValueError("STOP_BAW_ANNUAL_WCS_ORIGINAL_BAD_HTTP_OR_SIZE")
        return original,{"status":"SOURCE_WCS_CAPABILITIES_HTTP200_TLS_VERIFIED",
          "native_url":url,"original_SHA256":hashlib.sha256(original).hexdigest(),
          "native_xml_bytes":len(original),"original_http_status":status,
          "original_content_type":ct,"HTTPS_default_CA_enabled":True}
    except urllib.error.HTTPError as exc:
        loc=exc.headers.get("Location")
        destination=urllib.parse.urljoin(url,loc) if loc else None
        return None,{"status":"SOURCE_UNFOLLOWED_REDIRECT" if exc.code in
             (301,302,303,307,308) else "SOURCE_STOP_NATIVE_WCS_HTTP_ERROR",
             "original_http_status":exc.code,"original_Location":destination,
             "source_redirect_not_followed":True,
             "native_url":url}

def fetch_year_native_WCS(year):
    url=OFFICIAL_SOURCE_URLS[year]
    raw,receipt=original_baw_https_one_response(url,year,"mdi-dienste.baw.de")
    trail=[receipt]
    if receipt["status"]=="SOURCE_UNFOLLOWED_REDIRECT":
        dest=receipt.get("original_Location")
        if not dest or not is_approved_original_year_url(dest,year,"coast.baw.de"):
            raise ValueError("STOP_ORIGINAL_BAW_REDIRECT_NOT_SAME_YEAR_COAST_WCS")
        raw,new=original_baw_https_one_response(dest,year,"coast.baw.de")
        trail.append(new)
    if raw is None or trail[-1].get("status")!="SOURCE_WCS_CAPABILITIES_HTTP200_TLS_VERIFIED":
        raise ValueError("STOP_ORIGINAL_BAW_NATIVE_ANNUAL_WCS_NOT_HTTP200")
    return raw,{"original_HTTP_source_chain":trail,
                "native_WCS_Capabilities_XML_SHA256":hashlib.sha256(raw).hexdigest(),
                "original_xml_bytes":len(raw),
                "n_verified_BAW_legacy_to_coast_redirects":len(trail)-1}

def lname(x):
    return x.tag.rsplit("}",1)[-1] if isinstance(x.tag,str) else ""

def child_text(node,name):
    for c in node:
        if lname(c).lower()==name.lower():
            return " ".join(" ".join(c.itertext()).split())
    return ""

def is_native_count_coverage(s):
    s=s.lower()
    return bool(re.search(r"(?:valid|gueltig|gültig|datenpunkte|number_of_valid|n_valid)",s) and
        re.search(r"(?:count|anzahl|number|datenpunkte|n_valid|valid)",s))

def parse_native_original_annual_WCS(raw):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_NATIVE_WCS_XXE_OR_DTD")
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:
        raise ValueError("STOP_NATIVE_WCS_XML_PARSE_ERROR") from e
    if lname(root).lower() not in ("capabilities","wcs_capabilities") or root.attrib.get("version")!="2.0.1":
        raise ValueError("STOP_NOT_OFFICIAL_WCS2_CAPABILITIES")
    summaries=[]
    for row in root.iter():
        if lname(row)!="CoverageSummary":
            continue
        key=child_text(row,"CoverageId")
        if key:
            summaries.append({"original_CoverageId":key[:250],
              "native_Title":child_text(row,"Title")[:200],
              "native_Abstract":child_text(row,"Abstract")[:200]})
    keys=[x["original_CoverageId"] for x in summaries]
    if not keys or len(keys)>4000 or len(set(keys))!=len(keys):
        raise ValueError("STOP_MISSING_DUPLICATE_NATIVE_COVERAGE_NAMES")
    count=[x for x in summaries if is_native_count_coverage(
        x["original_CoverageId"]+" "+x["native_Title"]+" "+x["native_Abstract"])]
    nofilter=[x for x in summaries if "no_filter" in (
        x["original_CoverageId"]+" "+x["native_Title"]).lower()]
    water=[x for x in summaries if any(t in (
        x["original_CoverageId"]+" "+x["native_Title"]).lower()
        for t in ("wasserstand","waterstand","sea_surface_height","water_level"))]
    return {
      "native_WCS_root":lname(root),
      "native_version":root.attrib["version"],
      "n_original_CoverageSummary":len(summaries),
      "original_names_sample_cap200":keys[:200],
      "native_valid_count_candidates":count[:100],
      "native_no_filter_candidates":nofilter[:100],
      "native_waterlevel_candidates":water[:60],
      "n_native_valid_count_candidates":len(count),
      "n_native_no_filter_candidates":len(nofilter),
      "n_native_waterlevel_candidates":len(water),
      "raw_time_resolved_20min_WMS_FillValue_NOT_derived_from_annual_Coverages":True,
      "yearly_product_and_raw_20min_WMS_not_identical":True}

def run(out=OUT):
    report={
      "version":"v211-original-BAW-annual-Kennwerte-native-WCS-2018-2019-only",
      "frozen_official_yearly_WCS_original_urls":OFFICIAL_SOURCE_URLS,
      "BAW_official_public_record_ID":OFFICIAL_BAW_RECORDS,
      "annual_BAW_Kennwerte_product_not_raw_20min_WMS":True,
      "official_annual_Kennwerte_description_year_round_flooded_mask_and_no_filter":True,
      "original_getcoverage_or_raw_TIFF_called":False,
      "status":"SOURCE_STOP"}
    years={}
    for year in ("2018","2019"):
        try:
            raw,receipt=fetch_year_native_WCS(year)
            native=parse_native_original_annual_WCS(raw)
            years[year]={"status":"ORIGINAL_YEAR_NATIVE_OGC_WCS_COVERAGES_SOURCE_ADMITTED",
                  "source_HTTP_TLS_SHA":receipt,
                  "native_CoverageCatalogue":native}
        except Exception as e:
            years[year]={"status":"SOURCE_STOP_ORIGINAL_YEAR_NATIVE_WCS",
                  "source_error_kind":type(e).__name__,
                  "source_error_summary":str(e)[:230]}
    report["original_year_sources"]=years
    report["scientific_gates"]={
        "two_native_annual_2018_2019_WCS_catalogues_verified":all(
            x["status"]=="ORIGINAL_YEAR_NATIVE_OGC_WCS_COVERAGES_SOURCE_ADMITTED"
            for x in years.values()),
        "both_years_have_source_named_valid_count_candidates":all(
            x.get("native_CoverageCatalogue",{}).get("n_native_valid_count_candidates",0)>0
            for x in years.values()),
        "both_years_have_source_named_no_filter_candidates":all(
            x.get("native_CoverageCatalogue",{}).get("n_native_no_filter_candidates",0)>0
            for x in years.values()),
        "original_annual_valid_count_raster_pixels_loaded":False,
        "raw_time_resolved_WMS_1e31_native__FillValue_verified":False,
        "raw_WMS_model_no_value_is_actual_dry_cell_proven":False,
        "year2018_2019_original_field_survey_or_bird_GPS_tide_verified":False,
        "bird_tide_sun_social_Boids_behaviour_mechanism_estimated":False}
    if report["scientific_gates"]["two_native_annual_2018_2019_WCS_catalogues_verified"]:
        report["status"]="OFFICIAL_TWO_YEAR_2018_2019_ANNUAL_KENNWERTE_WCS_NATIVE_LAYERS_VERIFIED_ONLY"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V211_BAW_ANNUAL_WCS_SOURCE="+json.dumps({
      "status":report["status"],"scientific_gates":report["scientific_gates"],
      "year_data":{y:{"status":x["status"],
           "error":x.get("source_error_summary"),
           "native_n_cov":x.get("native_CoverageCatalogue",{}).get("n_original_CoverageSummary"),
           "valid_count_names":[z["original_CoverageId"] for z in x.get("native_CoverageCatalogue",{}).get("native_valid_count_candidates",[])],
           "no_filter_names":[z["original_CoverageId"] for z in x.get("native_CoverageCatalogue",{}).get("native_no_filter_candidates",[])][:50],
           "sample_names":x.get("native_CoverageCatalogue",{}).get("original_names_sample_cap200",[])[:30],
           "redirect_count":x.get("source_HTTP_TLS_SHA",{}).get("n_verified_BAW_legacy_to_coast_redirects")
         } for y,x in years.items()},
      "raw_20min_FillValue_and_bird_ecology_remain_SOURCE_STOP":True
    },sort_keys=True))
    return report

if __name__=="__main__":
    run()
