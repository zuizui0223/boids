"""v197: 24 frozen BAW WMS public-site/time numerical-response QA (NOT mNAP validation).
Original layer and bytewise GetCapabilities SHA pinned to v194-v195 source evidence.
"""
from __future__ import annotations
import hashlib,json,math,ssl,urllib.parse,urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from pyproj import Transformer
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
    OFFICIAL_YEAR_WMS, FIXED_PUBLICATION_RD_POINTS, FIXED_CAPABILITIES_SHA256,
    NATIVE_HEIGHT_LAYERS, fetch_verified_original_WMS, validate_capability_and_layer,
    make_fixed_feature_request, RestrictFeatureRedirect
)

FIXED_HOURS_UTC=("00","06","12","18")
FIXED_DAYS=("2018-06-01","2019-06-01")
OUT=Path(__file__).resolve().parent/"results/BAW_original_2018_2019_24_fixed_featureinfo_NoData_source_v197.json"
MAX_BYTES=10_000
ORIGINAL_FROZEN_COUNT=24

def utc_timestamp(day,hour):
    assert day in FIXED_DAYS and hour in FIXED_HOURS_UTC
    return f"{day}T{hour}:00:00.000Z"

def feature_query(year,lon,lat,stamp):
    if stamp not in (utc_timestamp(f"{year}-06-01",h) for h in FIXED_HOURS_UTC):
        raise ValueError("SOURCE_STOP_NONFROZEN_WMS_TIME")
    original,_=make_fixed_feature_request(year,lon,lat,"application/json")
    parts=urllib.parse.urlsplit(original)
    query=dict(urllib.parse.parse_qsl(parts.query,keep_blank_values=True))
    query["TIME"]=stamp
    return urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,
                                    urllib.parse.urlencode(query),""))

def classify_original_Wasserstand_response(data):
    if not isinstance(data,dict) or data.get("type")!="FeatureCollection":
        return "REJECTED_NOT_GEOJSON_FEATURE_COLLECTION",None
    records=data.get("features")
    if not isinstance(records,list) or len(records)!=1:
        return "REJECTED_MISSING_OR_MULTIPLE_FEATURES",None
    props=records[0].get("properties") if isinstance(records[0],dict) else None
    if not isinstance(props,dict) or set(props)!={"Wasserstand"}:
        return "REJECTED_UNEXPECTED_OR_MISSING_WASSERSTAND_PROPERTY",None
    value=props["Wasserstand"]
    if type(value) not in (float,int) or not math.isfinite(value):
        return "REJECTED_NONFINITE_OR_NONNUMERIC",None
    if abs(value)>=1e6:
        return "EXTREME_NODATA_SENTINEL_CANDIDATE",None
    if abs(value)>10:
        return "OUTSIDE_PLAUSIBILITY_BUT_NOT_PROVEN_FILL",None
    return "PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED",float(value)

def original_secure_GET_featureinfo(url):
    parts=urllib.parse.urlsplit(url)
    if not (parts.scheme=="https" and parts.hostname=="coast.baw.de"
      and parts.path.startswith("/geoserver/TrilaWatt_ncHydro_")
      and dict(urllib.parse.parse_qsl(parts.query)).get("REQUEST")=="GetFeatureInfo"):
        raise ValueError("SOURCE_STOP_NONOFFICIAL_GETFEATUREINFO")
    opener=urllib.request.build_opener(
      urllib.request.HTTPSHandler(context=ssl.create_default_context()),
      RestrictFeatureRedirect())
    req=urllib.request.Request(url,method="GET",headers={
      "User-Agent":"boids-v197-original-BAW-WMS-public-station-NoData-source-only/1.0",
      "Accept":"application/json"})
    with opener.open(req,timeout=33) as response:
        raw=response.read(MAX_BYTES+1)
        content_type=response.headers.get("Content-Type","")
        http=response.status
        final=response.geturl()
    if len(raw)>MAX_BYTES or not raw or http!=200 or urllib.parse.urlsplit(final).hostname!="coast.baw.de":
        raise ValueError("SOURCE_STOP_WMS_ORIGINAL_GETFEATUREINFO_HTTP_OR_SIZE")
    if "json" not in content_type.lower():
        raise ValueError("SOURCE_STOP_WMS_NONJSON_NATIVE_RESPONSE")
    try:
        d=json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise ValueError("SOURCE_STOP_WMS_GEOJSON_UNREADABLE") from exc
    classification,plausible=classify_original_Wasserstand_response(d)
    return {"original_response_SHA256":hashlib.sha256(raw).hexdigest(),
            "native_HTTP_status":http,
            "native_Content_Type":content_type,
            "original_JSON_structure_qa":classification,
            "candidate_physical_value_in_plausible_range":plausible is not None,
            "native_scalar_Wasserstand_not_calibrated_mNAP":True}

def run(out=OUT):
    data={"version":"v197-original-WMS-pinned-source-NoData-24-point-audit",
        "v195_previous_2019_harbor_WMS_huge_values_are_NODATA_CANDIDATE":True,
        "fixed_3_public_2011_reference_sites":list(FIXED_PUBLICATION_RD_POINTS),
        "fixed_year_day":FIXED_DAYS,
        "fixed_hour_grid_UTC":FIXED_HOURS_UTC,
        "original_WMS_GetCapabilities_SHA_frozen":FIXED_CAPABILITIES_SHA256,
        "not_original_bird_GPS_or_actual_station_instrument_positions":True,
        "not_actual_NetCDF_units_or_FillValue_verified":True,
        "no_raw_Wasserstand_timeseries_published":True,
        "status":"SOURCE_STOP"}
    convert=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True)
    results={}
    source_issues=[]
    for year in ("2018","2019"):
        year_out={"status":"SOURCE_STOP_YEAR", "sites":{}}
        try:
            capabilities,receipt=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            native=validate_capability_and_layer(capabilities,year)
            if (receipt["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year] or
                not native["source_admissible_for_feature_info_probe"] or
                native["chosen_predeclared_feature_info_format"]!="application/json"):
                raise ValueError("SOURCE_STOP_ORIGINAL_CAPABILITY_SHA_OR_JSON_QUERYABLE")
            year_out["source_original_capabilities_SHA_rechecked"]=receipt["original_WMS_xml_SHA256"]
            year_out["status"]="PINNED_SOURCE_LAYER_VERIFIED"
            for name,rd in FIXED_PUBLICATION_RD_POINTS.items():
                lon,lat=convert.transform(*rd)
                entries=[]
                for hour in FIXED_HOURS_UTC:
                    stamp=utc_timestamp(f"{year}-06-01",hour)
                    source={"time_UTC":stamp}
                    try:
                        req=feature_query(year,lon,lat,stamp)
                        source.update(original_secure_GET_featureinfo(req))
                        source["source_status"]="HTTPS_JSON_RESPONSE_PARSED_NOT_PHYSICAL_HEIGHT_ADMITTED"
                    except Exception as err:
                        source["source_status"]="SOURCE_STOP_ORIGINAL_FEATUREINFO_RESPONSE"
                        source["error_kind"]=type(err).__name__
                        source["error_summary"]=str(err)[:170]
                        source_issues.append(f"{year}:{name}:{hour}:{type(err).__name__}")
                    entries.append(source)
                counts=Counter(z.get("original_JSON_structure_qa","NO_ORIGINAL_RESPONSE") for z in entries)
                year_out["sites"][name]={
                  "n_fixed_original_HHMM":len(entries),
                  "source_valid_JSON_or_error_counts":dict(counts),
                  "n_plausible_numeric_model_response_not_mNAP":counts.get(
                     "PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED",0),
                  "n_extreme_NoData_sentinel_candidate":counts.get(
                     "EXTREME_NODATA_SENTINEL_CANDIDATE",0),
                  "original_WMS_sha_at_each_time":[
                      {"UTC":e["time_UTC"],
                       "response_status":e["source_status"],
                       "native_json_classification":e.get("original_JSON_structure_qa"),
                       "original_response_SHA256":e.get("original_response_SHA256")}
                      for e in entries],
                  "no_raw_water_heights_retained":True}
        except Exception as err:
            year_out["source_error_kind"]=type(err).__name__
            year_out["source_error_summary"]=str(err)[:180]
            source_issues.append(f"{year}:capabilities:{type(err).__name__}")
        results[year]=year_out
    data["original_two_year_source_qa"]=results
    n_http=sum(sum(sum(v["source_valid_JSON_or_error_counts"].values())
             for v in year["sites"].values()) for year in results.values())
    n_native=sum(sum(sum(n for k,n in v["source_valid_JSON_or_error_counts"].items()
                 if k!="NO_ORIGINAL_RESPONSE") for v in year["sites"].values())
             for year in results.values())
    n_p=sum(sum(v["n_plausible_numeric_model_response_not_mNAP"]
               for v in year["sites"].values()) for year in results.values())
    n_s=sum(sum(v["n_extreme_NoData_sentinel_candidate"]
               for v in year["sites"].values()) for year in results.values())
    data["source_gates"]={
       "all24_fixed_year_site_time_original_WMS_responses_QA_complete":
           not source_issues and n_native==ORIGINAL_FROZEN_COUNT,
       "n_frozen_site_time_queries":ORIGINAL_FROZEN_COUNT,
       "n_native_source_responses_parsed":n_native,
       "n_plausible_numeric_source_candidates_not_calibrated_water":n_p,
       "n_extreme_nodata_sentinel_candidates":n_s,
       "n_original_source_issues":len(source_issues),
       "native_NetCDF_fillValue_value_verified":False,
       "native_Wasserstand_units_vertical_datum_verified":False,
       "original_bird_GPS_local_h_s_t_admitted":False,
       "annual_intertidal_and_20m_z_datum_original_admitted":False,
       "tide_solar_Boids_animal_mechanism_verified":False}
    data["source_error_counts_by_year_site_time"]=source_issues
    data["status"]=("V197_ALL_24_OFFICIAL_WMS_SOURCE_RESPONSES_PARSED_QA_ONLY"
        if data["source_gates"]["all24_fixed_year_site_time_original_WMS_responses_QA_complete"]
        else "SOURCE_STOP_INCOMPLETE_24_ORIGINAL_WMS_RESPONSES")
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V197_WMS_NODATA_SOURCE_SCOPE="+json.dumps({
      "status":data["status"],"gates":data["source_gates"],
      "source_year_site_counts":{
          year:{name:{k:v[k] for k in (
              "n_plausible_numeric_model_response_not_mNAP",
              "n_extreme_NoData_sentinel_candidate")}
              for name,v in group["sites"].items()} for year,group in results.items()},
      "source_errors":source_issues,"no_bird_or_local_wet_dry":True},sort_keys=True))
    return data

if __name__=="__main__":
    run()
