"""v212: SOURCE-only 2018/2019 native BAW annual valid-data-point coverage schemas.

Exact annual BAW Kennwerte WCS2 CoverageIds fixed from TWO genuine v211
GetCapabilities source runs. No GetCoverage, TIFF, raw WMS 20min water heights,
RWS time series, bird GPS/ACC, or original DEM.
"""
from __future__ import annotations
import hashlib,json,ssl,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path
from original_BAW_annual_2018_2019_Kennwerte_WCS_source import (
    fetch_year_native_WCS,parse_native_original_annual_WCS,
    is_approved_original_year_url,RefuseUnverifiedRedirect,lname,
)
FROZEN_VALID_COUNTS={
    "2018":"TrilaWatt_Hydrodynamik_2018__nof_valid_data_points_2018_nl",
    "2019":"TrilaWatt_Hydrodynamik_2019__nof_valid_data_points_2019_nl"
}
FROZEN_NATIVE_WCS_CAP_SHA={
    "2018":"b22c4571435b5da1d4cc11dfcca985d536f447337a0bf869780b77d4360a6f28",
    "2019":"af18e4a3280e5bfaef58e525b7079f5e4c4d9b57beea6c7743ae9f2ac16143e4",
}
MAX_DESCRIBE_BYTES=2_000_000
OUT=Path(__file__).resolve().parent/"results/original_BAW_2018_2019_NL_validpoints_DescribeCoverage_v212.json"

def native_doc(raw,expected=None):
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("STOP_ORIGINAL_WCS_UNTRUSTED_XML")
    try:root=ET.fromstring(raw)
    except ET.ParseError as e:raise ValueError("STOP_ORIGINAL_WCS_UNPARSEABLE_XML") from e
    if expected and lname(root).lower()!=expected.lower():
        raise ValueError("STOP_WRONG_NATIVE_WCS_DOCUMENT_ROOT")
    return root

def native_coverage_describe_URL(year,final_original_cap_url):
    if year not in FROZEN_VALID_COUNTS:
        raise ValueError("STOP_UNFROZEN_YEAR")
    if not is_approved_original_year_url(final_original_cap_url,year,"coast.baw.de") and not (
        is_approved_original_year_url(final_original_cap_url,year,"mdi-dienste.baw.de")):
        raise ValueError("STOP_ORIGINAL_BAW_URL_NOT_SOURCE_AUTHENTICATED")
    p=urllib.parse.urlsplit(final_original_cap_url)
    parts=[
      ("service","WCS"),("version","2.0.1"),
      ("request","DescribeCoverage"),("coverageId",FROZEN_VALID_COUNTS[year])]
    return urllib.parse.urlunsplit(
      (p.scheme,p.netloc,p.path,urllib.parse.urlencode(parts),""))

def only_frozen_describe_URL(url,year,cap_url):
    return url==native_coverage_describe_URL(year,cap_url)

def fetch_original_coverage_description(year,cap_url):
    url=native_coverage_describe_URL(year,cap_url)
    if not only_frozen_describe_URL(url,year,cap_url):
        raise ValueError("STOP_NOT_FROZEN_ORIGINAL_DESCRIBE_URL")
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v212-original-BAW-annual-WCS-DescribeCoverage-source-only/1.0",
       "Accept":"application/xml,text/xml"})
    opener=urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
        RefuseUnverifiedRedirect())
    with opener.open(req,timeout=35) as response:
        raw=response.read(MAX_DESCRIBE_BYTES+1)
        http=response.status
        final=response.geturl()
        ct=response.headers.get("Content-Type")
    if http!=200 or final!=url or not raw or len(raw)>MAX_DESCRIBE_BYTES:
        raise ValueError("STOP_ORIGINAL_DESCRIBE_WCS_BAD_HTTP_REDIRECT_OR_BYTES")
    doc=native_doc(raw,"CoverageDescriptions")
    return doc,{"source_request":url,
       "native_DescribeCoverage_XML_SHA256":hashlib.sha256(raw).hexdigest(),
       "source_response_bytes":len(raw),"source_content_type":ct,
       "source_status":http,"native_TLS_default_CA_enabled":True,
       "no_original_annual_raster_values_read":True}

def text_from_first(node,name):
    for n in node.iter():
        if lname(n)==name:
            return " ".join(" ".join(n.itertext()).split())
    return None

def inspect_native_coverage_description(root,year):
    all_ids=[" ".join(" ".join(x.itertext()).split()) for x in root.iter()
             if lname(x)=="CoverageId"]
    if all_ids!=[FROZEN_VALID_COUNTS[year]]:
        raise ValueError("STOP_NATIVE_WCS_COVERAGEID_NOT_EXACT_OR_MULTIPLE")
    envelopes=[]
    grids=[]
    fields=[]
    nilvalues=[]
    for node in root.iter():
        tag=lname(node)
        if tag=="Envelope" and len(envelopes)<10:
            envelopes.append({
                "native_srsName":node.attrib.get("srsName"),
                "native_axisLabels":node.attrib.get("axisLabels"),
                "original_lowerCorner":text_from_first(node,"lowerCorner"),
                "original_upperCorner":text_from_first(node,"upperCorner"),
                "native_uomLabels":node.attrib.get("uomLabels")})
        elif tag=="RectifiedGrid" and len(grids)<10:
            origin=text_from_first(node,"pos")
            offsets=[" ".join(" ".join(x.itertext()).split()) for x in node.iter()
                     if lname(x)=="offsetVector"]
            grids.append({"native_dimension":node.attrib.get("dimension"),
               "native_grid_origin":origin,
               "native_offsetVector_strings":offsets[:6],
               "native_grid_low_high":[text_from_first(node,"low"),text_from_first(node,"high")]})
        elif tag=="field" and len(fields)<30:
            fields.append({"name":node.attrib.get("name"),
                           "uom":text_from_first(node,"uom")})
        elif tag.lower()=="nilvalue" and len(nilvalues)<25:
            nilvalues.append({"native_value":(node.text or "").strip()[:70],
                              "reason":node.attrib.get("reason")})
    if not envelopes:
        raise ValueError("STOP_ORIGINAL_COVERAGE_HAS_NO_SPATIAL_ENVELOPE")
    return {
       "native_CoverageId":FROZEN_VALID_COUNTS[year],
       "original_envelopes":envelopes,
       "original_rectified_grids":grids,
       "native_rangeType_fields":fields,
       "native_nilValues":nilvalues,
       "is_original_annual_summary_nof_valid_data_points_not_raw_20min_Wasserstand":True,
       "native_yearly_sampling_denominator_maybe_requires_separate_metadata":True,
       "raw_WMS_1e31_FillValue_NOT_derived_from_annual_data":True,
       "annual_Coverage_no_true_GPS_bird_spatial_overlap_or_inundation_proven":True}

def run(out=OUT):
    result={"version":"v212-source-only-exact-original-NL-yearly-validpoints-DescribeCoverage",
      "v211_two_success_runs":[44456179353,44456220003],
      "pinned_v211_original_WCS_Capabilities_SHA":FROZEN_NATIVE_WCS_CAP_SHA,
      "native_exact_yearly_coverage_names":FROZEN_VALID_COUNTS,
      "no_WCS_GetCoverage_or_native_WMS_or_GPS_or_RWS_source_read":True,
      "status":"SOURCE_STOP"}
    years={}
    for year in ("2018","2019"):
        try:
            raw,cap=fetch_year_native_WCS(year)
            if cap["native_WCS_Capabilities_XML_SHA256"]!=FROZEN_NATIVE_WCS_CAP_SHA[year]:
                raise ValueError("STOP_ORIGINAL_V211_YEAR_WCS_CAPABILITIES_SHA_DRIFT")
            native=parse_native_original_annual_WCS(raw)
            ids=native["original_names_sample_cap200"]
            if FROZEN_VALID_COUNTS[year] not in ids and not any(
                x["original_CoverageId"]==FROZEN_VALID_COUNTS[year] for x in
                native["native_valid_count_candidates"]):
                raise ValueError("STOP_NATIVE_VALID_DATA_COUNT_COVERAGE_NOT_IN_ORIGINAL_CAPABILITIES")
            rootcap=native_doc(raw)
            ops={node.attrib.get("name") for node in rootcap.iter()
                 if lname(node)=="Operation" and node.attrib.get("name")}
            if "DescribeCoverage" not in ops:
                raise ValueError("STOP_BAW_ORIGINAL_WCS_DOES_NOT_ADVERTISE_DESCRIBECOVERAGE")
            capurl=cap["original_HTTP_source_chain"][-1]["native_url"]
            source,receipt=fetch_original_coverage_description(year,capurl)
            meta=inspect_native_coverage_description(source,year)
            years[year]={"status":"ORIGINAL_ANNUAL_NL_VALIDPOINTS_DESCRIBECOVERAGE_SOURCE_ADMITTED",
              "original_capabilities_SHA256":cap["native_WCS_Capabilities_XML_SHA256"],
              "original_describe_source":receipt,
              "original_native_metadata":meta}
        except Exception as e:
            years[year]={"status":"SOURCE_STOP_YEARLY_NATIVE_DESCRIBECOVERAGE",
                         "error_kind":type(e).__name__,
                         "error_message":str(e)[:240]}
    result["two_original_year_descriptions"]=years
    result["scientific_source_gates"]={
       "both_years_native_annual_valid_count_coverages_original_DescribeCoverage_read":all(
           x["status"]=="ORIGINAL_ANNUAL_NL_VALIDPOINTS_DESCRIBECOVERAGE_SOURCE_ADMITTED"
           for x in years.values()),
       "both_years_annual_validpoint_native_rangeType_uom_reported":all(
           bool(x.get("original_native_metadata",{}).get("native_rangeType_fields"))
           for x in years.values()),
       "native_raster_values_or_actual_yearly_temporal_sample_counts_observed":False,
       "raw_time_resolved_20min_WMS_Wasserstand_units_FillValue_NAP_verified":False,
       "geographic_BAW_annual_count_cell_matches_2011_public_station":False,
       "true_original_bird_GPS_h_s_t_and_intertidal_access_identified":False,
       "animal_tide_sun_social_Boids_causal_effect_estimated":False}
    if result["scientific_source_gates"]["both_years_native_annual_valid_count_coverages_original_DescribeCoverage_read"]:
        result["status"]="ORIGINAL_TWO_YEAR_NL_ANNUAL_VALIDCOUNT_COVERAGE_METADATA_VERIFIED_NO_VALUES"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V212_BAW_NATIVE_ANNUAL_VALIDCOUNT_DESCRIBE="+json.dumps({
      "status":result["status"],"source_gates":result["scientific_source_gates"],
      "years":{y:{"status":v["status"],
           "native_meta":v.get("original_native_metadata"),
           "error":v.get("error_message"),
           "original_describe_sha":v.get("original_describe_source",{}).get("native_DescribeCoverage_XML_SHA256")}
           for y,v in years.items()},
      "no_bird_or_true_WMS_source_fillvalue":True
    },sort_keys=True))
    return result

if __name__=="__main__":
    run()
