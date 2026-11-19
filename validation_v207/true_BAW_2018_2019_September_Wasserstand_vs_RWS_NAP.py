"""v207 September 1 genuine original public RWS measured NAP gauge vs BAW modeled WMS Wasserstand
on 36 PREDECLARED public site-times (3 station reference locations x 2 years x 6).

For source/pipeline consistency only. Unit of GeoServer WMS Wasserstand not verified
in original NetCDF and station instrument exact positions not verified. Never
call this an independent model evaluation, 2018->19 real-time forecast, GPS-local
water exposure or animal Boids/tide-by-sun effect. Raw tide arrays stay in RAM.
"""
from __future__ import annotations
import hashlib,json,math,ssl,urllib.parse,urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from pyproj import Transformer

from rws_roompot_2020_source import (
    publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop
)
from original_RWS_two_gauge_comparison import original_nap_series
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
    OFFICIAL_YEAR_WMS, FIXED_CAPABILITIES_SHA256,
    FIXED_PUBLICATION_RD_POINTS, NATIVE_HEIGHT_LAYERS,
    fetch_verified_original_WMS,validate_capability_and_layer,
    make_fixed_feature_request, RestrictFeatureRedirect
)
from true_BAW_WMS_24_timestamp_NoData_source import (
    classify_original_Wasserstand_response
)

STATION_SOURCE_CODES={
    "VlielandHaven":"vlieland.haven",
    "WestTerschelling":"terschelling.west",
    "Wierumergronden":"wierumergronden",
}
YEARS=("2018","2019")
UTC_HOURS=(0,4,8,12,16,20)
MIN_NATIVE_RWS_READINGS=200
MIN_PAIRS_DESCRIPTIVE=3
MAX_JSON_BYTES=10_000
OUT=Path(__file__).resolve().parent/"results/BAW_original_WMS_2018_2019_vs_measured_RWS_3gauge_36point_v207.json"

def frozen_UTC(year,hour):
    if year not in YEARS or hour not in UTC_HOURS:
        raise ValueError("STOP_NONFROZEN_RWS_WMS_YEAR_OR_UTC_HOUR")
    return datetime(int(year),9,1,hour,tzinfo=timezone.utc)

def frozen_WMS_model_request(year,site,hour):
    if site not in STATION_SOURCE_CODES or site not in FIXED_PUBLICATION_RD_POINTS:
        raise ValueError("STOP_UNKNOWN_OFFICIAL_PUBLIC_REFERENCE_STATION")
    t=frozen_UTC(year,hour)
    e,n=FIXED_PUBLICATION_RD_POINTS[site]
    lon,lat=Transformer.from_crs("EPSG:28992","EPSG:4326",always_xy=True).transform(e,n)
    noon,_=make_fixed_feature_request(year,lon,lat,"application/json")
    parts=urllib.parse.urlsplit(noon)
    query=dict(urllib.parse.parse_qsl(parts.query,keep_blank_values=True))
    query["TIME"]=t.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,
             urllib.parse.urlencode(query),""))

def verified_frozen_WMS_request(url):
    return any(url==frozen_WMS_model_request(year,site,hour)
         for year in YEARS for site in STATION_SOURCE_CODES for hour in UTC_HOURS)

def get_approved_original_WMS_Wasserstand(url):
    if not verified_frozen_WMS_request(url):
        raise ValueError("STOP_NOT_ONE_OF_36_PREDECLARED_ORIGINAL_WMS_URLS")
    req=urllib.request.Request(url,method="GET",headers={
       "User-Agent":"boids-v207-BAW-WMS-RWS-native-NAP-source-consistency/1.0",
       "Accept":"application/json"})
    op=urllib.request.build_opener(
       urllib.request.HTTPSHandler(context=ssl.create_default_context()),
       RestrictFeatureRedirect())
    with op.open(req,timeout=32) as resp:
        raw=resp.read(MAX_JSON_BYTES+1)
        status=resp.status
        final=resp.geturl()
        ct=resp.headers.get("Content-Type","")
    if (status!=200 or final!=url or not raw or len(raw)>MAX_JSON_BYTES
        or "json" not in ct.lower()):
        raise ValueError("STOP_NATIVE_ORIGINAL_WMS_WASSERSTAND_BAD_HTTP_OR_BYTES")
    try:
        doc=json.loads(raw)
    except (ValueError,UnicodeError) as exc:
        raise ValueError("STOP_BAW_ORIGINAL_WMS_NOT_PARSEABLE_GEOJSON") from exc
    classification,value=classify_original_Wasserstand_response(doc)
    return value,{"source_status":"ORIGINAL_BAW_WMS_GETFEATUREINFO_SOURCE_READ",
         "source_original_HTTP_JSON_SHA256":hashlib.sha256(raw).hexdigest(),
         "source_original_http_bytes":len(raw),
         "native_GeoJSON_Wasserstand_classification":classification,
         "native_source_numeric_candidate_not_meter_datum_calibrated":True}

def validate_three_pinned_native_stations(catalog):
    if catalog.get("Succesvol") is False:raise SourceStop("OFFICIAL_RWS_STATION_CATALOGUE_REJECTED")
    all_stations=catalog.get("LocatieLijst") or []
    if len(all_stations)<50:raise SourceStop("OFFICIAL_RWS_STATION_CATALOGUE_TOO_SMALL")
    result={}
    for name,code in STATION_SOURCE_CODES.items():
        match=[v for v in all_stations if str(v.get("Code","")).lower()==code]
        if len(match)!=1:
            raise SourceStop("RWS_ORIGINAL_STATION_CODE_MISSING_OR_AMBIGUOUS_"+name)
        if not any(term in str(match[0].get("Naam","")).lower()
                 for term in (
                   ("vlieland",) if name=="VlielandHaven" else
                   ("terschelling",) if name=="WestTerschelling" else
                   ("wierumergronden",))):
            raise SourceStop("RWS_OFFICIAL_STATION_NATIVE_NAME_MISMATCH_"+name)
        result[name]={"native_source_code":code,
                      "native_source_name":match[0].get("Naam"),
                      "original_coordinate_system":match[0].get("Coordinatenstelsel"),
                      "native_catalogue_XY_may_be_null":(
                          match[0].get("X") is None or match[0].get("Y") is None),
                      "2011_RD_reference_not_RWS_2018_instrument_position":True}
    return result

def retrieve_original_RWS_48h(year,site):
    code=STATION_SOURCE_CODES[site]
    request={"Locatie":{"Code":code},
       "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
       "Periode":{"Begindatumtijd":f"{year}-09-01T00:00:00.000+01:00",
                  "Einddatumtijd":f"{year}-09-03T00:00:00.000+01:00"}}
    native,raw_sha=publisher_post(DATA_ROUTE,request)
    readings,excluded=original_nap_series(native)
    if len(readings)<MIN_NATIVE_RWS_READINGS:
        raise SourceStop("SOURCE_STOP_ORIGINAL_RWS_48H_LESS_THAN_200")
    return readings,{"original_RWS_publisher_JSON_SHA256":raw_sha,
         "native_publisher_station_code":code,
         "native_48h_WATHTE_cmNAP_unique_10min_n":len(readings),
         "original_QA_exclusions":excluded,
         "native_RWS_height_was_cm_NAP_converted_m_without_fit":True}

def descriptive_matched_model_vs_RWS(pairs):
    if len(pairs)<MIN_PAIRS_DESCRIPTIVE:
        return {"status":"NOT_EVALUABLE_LESS_THAN_3_PAIRED_NUMERIC",
                "n_native_exact_time_paired":len(pairs)}
    m=[p[0] for p in pairs]
    w=[p[1] for p in pairs]
    deviations=[a-b for a,b in pairs]
    mx=mean(m);wx=mean(w)
    a=sum((x-mx)**2 for x in m)
    b=sum((y-wx)**2 for y in w)
    corr=(sum((x-mx)*(y-wx) for x,y in pairs)/math.sqrt(a*b)
           if a*b>1e-12 else None)
    return {"status":"DESCRIPTIVE_MODEL_GAUGE_NUMERIC_CONSISTENCY_UNDER_METER_ASSUMPTION",
       "n_native_exact_time_paired":len(pairs),
       "numeric_model_minus_RWS_NAP_bias_under_meter_assumption":round(mean(deviations),8),
       "numeric_model_RWS_NAP_MAE_under_meter_assumption":round(mean(abs(d) for d in deviations),8),
       "numeric_model_RWS_NAP_RMSE_under_meter_assumption":round(
           math.sqrt(mean(d*d for d in deviations)),8),
       "native_pairs_Pearson_r_no_significance_claim":round(corr,8) if corr is not None else None,
       "native_WMS_model_unit_and_exact_gauge_position_UNVERIFIED":True,
       "not_an_independent_model_forcing_validation":True}

def one_year_source_QA(year,site):
    record={"fixed_original_NL_model_layer":NATIVE_HEIGHT_LAYERS[year],
       "fixed_original_RWS_native_code":STATION_SOURCE_CODES[site],
       "fixed_UTC_hours":list(UTC_HOURS),
       "rws_source_status":"SOURCE_STOP",
       "WMS_source_response_counts":{},
       "status":"SOURCE_STOP"}
    gauge={}
    try:
        readings,origin=retrieve_original_RWS_48h(year,site)
        gauge=readings
        record["official_RWS_source_receipt"]=origin
        record["rws_source_status"]="RWS_TRUE_WATHTE_CM_NAP_ADMITTED"
    except Exception as e:
        record["rws_source_error_type"]=type(e).__name__
        record["rws_source_error_summary"]=str(e)[:180]
    classifications=Counter()
    source_stamps=[]
    pairs=[]
    wms_ok=0
    for hour in UTC_HOURS:
        stamp=frozen_UTC(year,hour)
        entry={"fixed_UTC_time":stamp.isoformat()}
        try:
            numeric,receipt=get_approved_original_WMS_Wasserstand(
               frozen_WMS_model_request(year,site,hour))
            entry.update(receipt)
            entry["source_gauge_exact_UTC_match"]=stamp in gauge
            if entry["native_GeoJSON_Wasserstand_classification"]==(
                 "PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED") and numeric is not None and stamp in gauge:
                pairs.append((numeric,gauge[stamp]))
            classifications[entry["native_GeoJSON_Wasserstand_classification"]]+=1
            wms_ok+=1
        except Exception as e:
            entry["source_status"]="SOURCE_STOP_ORIGINAL_MODEL_WMS_REQUEST"
            entry["source_error_kind"]=type(e).__name__
            entry["source_error_summary"]=str(e)[:140]
            classifications["ORIGINAL_MODEL_WMS_SOURCE_ERROR"]+=1
        source_stamps.append(entry)
    record["native_original_WMS_time_receipts_without_values"]=source_stamps
    record["WMS_source_response_counts"]=dict(classifications)
    record["n_WMS_original_HTTPS_JSON_success"]=wms_ok
    record["descriptive_NAP_model_numeric_consistency"]=descriptive_matched_model_vs_RWS(pairs)
    record["status"]="ORIGINAL_MEASURED_RWS_AND_WMS_FIXED_TIMES_AUDITED_NO_UNIT_CALIBRATION" if (
        record["rws_source_status"]=="RWS_TRUE_WATHTE_CM_NAP_ADMITTED" and wms_ok==len(UTC_HOURS)
    ) else "SOURCE_INCOMPLETE_RWS_OR_WMS"
    return record

def run(out=OUT):
    data={"analysis":"v207-BAW-2018_2019_NL_WMS_36_fixed_Wasserstand_original_RWS_3stations",
       "frozen_sites":STATION_SOURCE_CODES,
       "frozen_2011_public_RD_positions":FIXED_PUBLICATION_RD_POINTS,
       "source_years":YEARS,"frozen_UTC_hours":list(UTC_HOURS),
       "original_WMS_capabilities_SHA":FIXED_CAPABILITIES_SHA256,
       "prior_v197_site_selection_exploratory_after_source_availability":True,
       "no_original_RWS_model_height_series_or_bird_GPS_saved":True,
       "status":"SOURCE_STOP"}
    years={}
    try:
        cat,catsha=publisher_post(META_ROUTE,{"CatalogusFilter":{
          "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        identity=validate_three_pinned_native_stations(cat)
        data["RWS_native_original_catalogue_SHA256"]=catsha
        data["original_station_source_identity"]=identity
        for year in YEARS:
            rawcap,receipt=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            source=validate_capability_and_layer(rawcap,year)
            if (receipt["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year]
               or not source["source_admissible_for_feature_info_probe"]
               or source["chosen_predeclared_feature_info_format"]!="application/json"):
                raise ValueError("SOURCE_STOP_WMS_GENUINE_NL_YEAR_CAPABILITY_OR_SHA_CHANGED")
            years[year]={"original_WMS_capability_SHA_rechecked":
                         receipt["original_WMS_xml_SHA256"],"sites":{}}
            for site in STATION_SOURCE_CODES:
                years[year]["sites"][site]=one_year_source_QA(year,site)
    except Exception as e:
        data["source_global_error_type"]=type(e).__name__
        data["source_global_error_summary"]=str(e)[:220]
    data["two_native_original_years"]=years
    stats={}
    for year,y in years.items():
        for site,r in y["sites"].items():
            stats[f"{year}_{site}"]={
                "status":r["status"],
                "native_model_HTTPS_success":r["n_WMS_original_HTTPS_JSON_success"],
                "n_plausible_numeric_no_unit":r["WMS_source_response_counts"].get(
                    "PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED",0),
                "n_extreme_sentinel_source":r["WMS_source_response_counts"].get(
                    "EXTREME_NODATA_SENTINEL_CANDIDATE",0),
                "n_matched_exact_time":r["descriptive_NAP_model_numeric_consistency"].get(
                    "n_native_exact_time_paired",0),
                "source_model_RWS_descriptive":r["descriptive_NAP_model_numeric_consistency"],
                "native_RWS_source_n":r.get("official_RWS_source_receipt",{}).get(
                    "native_48h_WATHTE_cmNAP_unique_10min_n"),
                "source_error":r.get("rws_source_error_summary")}
    data["site_year_source_safe_summary"]=stats
    n_siteyear_ok=sum(v["status"]=="ORIGINAL_MEASURED_RWS_AND_WMS_FIXED_TIMES_AUDITED_NO_UNIT_CALIBRATION"
                      for v in stats.values())
    n_siteyear_evaluable=sum(v["source_model_RWS_descriptive"]["status"]==(
        "DESCRIPTIVE_MODEL_GAUGE_NUMERIC_CONSISTENCY_UNDER_METER_ASSUMPTION")
        for v in stats.values())
    data["scientific_gates"]={
        "all_six_original_RWS_site_year_sources_admitted_and_36_WMS_queries_success":
             n_siteyear_ok==6,
        "n_completed_site_year_source_cohorts":n_siteyear_ok,
        "n_candidate_numerical_meter_assumption_comparison_evaluable":n_siteyear_evaluable,
        "native_WMS_Wasserstand_unit_and_vertical_NHN_NAP_not_directly_verified":True,
        "2011_public_site_not_exact_native_RWS_2018_2019_sensor_position":True,
        "model_forcing_independent_external_validation_done":False,
        "local_bird_GPS_tide_and_historical_DEM_datum_surveydate_calibrated":False,
        "animal_tide_solar_Boids_behaviour_effect_estimated":False}
    data["status"]="ORIGINAL_BAW_WMS_VS_RWS_SIX_COHORT_SOURCES_AUDITED_NUMERIC_ONLY" if n_siteyear_ok==6 else "SOURCE_STOP_INCOMPLETE_2018_2019_MODEL_GAUGE_PAIRING"
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V207_BAW_MODEL_RWS_GAUGE_SCOPE="+json.dumps({
       "status":data["status"],"gates":data["scientific_gates"],
       "source_site_year":stats,
       "source_global_error":data.get("source_global_error_summary"),
       "no_model_unit_or_independent_ecology_claim":True},sort_keys=True))
    return data

if __name__=="__main__":
    run()
