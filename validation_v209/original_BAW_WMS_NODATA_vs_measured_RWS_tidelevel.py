"""v209: original BAW 2018/19 WMS extreme-NoData candidates vs measured RWS cmNAP level.

Frozen 72 public model reply times from v206 (June) + v207 (September), paired
exact UTC with original official RWS WATHTE cmNAP gauge. No WMS model height
units needed for classification. No new bird, GPS, actual mudflat, or social Boids.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean, median

from rws_roompot_2020_source import publisher_post,META_ROUTE
from true_BAW_2018_2019_Wasserstand_vs_RWS_gauge_NAP import (
    STATION_SOURCE_CODES,UTC_HOURS,
    frozen_UTC as june_timestamp,
    frozen_WMS_model_request as june_model_request,
    get_approved_original_WMS_Wasserstand as june_get_original_WMS,
    retrieve_original_RWS_48h as june_retrieve_RWS,
    validate_three_pinned_native_stations,
)
from true_BAW_2018_2019_September_Wasserstand_vs_RWS_NAP import (
    frozen_UTC as september_timestamp,
    frozen_WMS_model_request as september_model_request,
    get_approved_original_WMS_Wasserstand as september_get_original_WMS,
    retrieve_original_RWS_48h as september_retrieve_RWS,
)
from original_BAW_two_year_NL_WMS_public_stations_featureinfo import (
    OFFICIAL_YEAR_WMS,FIXED_CAPABILITIES_SHA256,
    fetch_verified_original_WMS,validate_capability_and_layer
)

YEARS=("2018","2019")
MONTHS=("June","September")
EXPECTED_EXTREME_SENTINEL_N={
  "June_2018_VlielandHaven":3,
  "June_2018_WestTerschelling":2,
  "June_2018_Wierumergronden":0,
  "June_2019_VlielandHaven":4,
  "June_2019_WestTerschelling":2,
  "June_2019_Wierumergronden":0,
  "September_2018_VlielandHaven":3,
  "September_2018_WestTerschelling":3,
  "September_2018_Wierumergronden":0,
  "September_2019_VlielandHaven":3,
  "September_2019_WestTerschelling":2,
  "September_2019_Wierumergronden":0,
}
SENTINEL="EXTREME_NODATA_SENTINEL_CANDIDATE"
PLAUSIBLE="PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED"
MIN_N_BOTH_WMS_CLASSES=2
MIN_SUPPORT_GROUPS=7
EXPECTED_GROUPS=12
EXPECTED_WMS_TIMES=72
OUT=Path(__file__).resolve().parent/"results/original_RWS_tide_mNAP_vs_BAW_WMS_extreme_NoData_72points_v209.json"

def paired_date_api(month):
    if month=="June":
        return june_timestamp,june_model_request,june_get_original_WMS,june_retrieve_RWS
    if month=="September":
        return september_timestamp,september_model_request,september_get_original_WMS,september_retrieve_RWS
    raise ValueError("STOP_UNFROZEN_NODATA_MONTH")

def describe_original_observed_height_by_model_class(levels):
    if not isinstance(levels,dict) or set(levels)!={PLAUSIBLE,SENTINEL}:
        raise ValueError("SOURCE_STOP_UNEXPECTED_MODEL_VALIDITY_CLASSES")
    if any(not math.isfinite(z) for values in levels.values() for z in values):
        raise ValueError("SOURCE_STOP_NONFINITE_RWS_MEASURED_HEIGHT")
    nvalid=len(levels[PLAUSIBLE])
    nbad=len(levels[SENTINEL])
    result={
      "n_original_WMS_plausible_source_candidates":nvalid,
      "n_original_WMS_extreme_NoData_candidates":nbad,
      "n_original_measured_RWS_exact_UTC_paired":nvalid+nbad,
      "original_RWS_WATHTE_was_cmNAP_not_model_undocumented_units":True,
      "native_WMS_original_FillValue_not_proven":True}
    if min(nvalid,nbad)<MIN_N_BOTH_WMS_CLASSES:
        result["status"]="NOT_EVALUABLE_SPARSE_ONE_OR_BOTH_MODEL_CLASSES"
        result["observed_RWS_sentinel_minus_plausible_mean_NAP_m"]=None
        result["observed_RWS_sentinel_minus_plausible_median_NAP_m"]=None
        result["low_observed_tide_direction_supported"]=None
        return result
    difference=mean(levels[SENTINEL])-mean(levels[PLAUSIBLE])
    meddiff=median(levels[SENTINEL])-median(levels[PLAUSIBLE])
    result.update({
      "status":"MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE",
      "observed_RWS_sentinel_minus_plausible_mean_NAP_m":round(difference,8),
      "observed_RWS_sentinel_minus_plausible_median_NAP_m":round(meddiff,8),
      "low_observed_tide_direction_supported":difference<0,
      "this_is_original_wms_availability_not_bird_or_habitat_exposure":True})
    return result

def one_official_original_source_cohort(month,year,site):
    stamp,query,getmodel,getRWS=paired_date_api(month)
    key=f"{month}_{year}_{site}"
    if key not in EXPECTED_EXTREME_SENTINEL_N:
        raise ValueError("SOURCE_STOP_UNFROZEN_NODATA_COHORT")
    source={"source_cohort":key,
            "original_RWS_source_status":"SOURCE_STOP",
            "original_BAW_WMS_source_status":"SOURCE_STOP",
            "source_status":"SOURCE_STOP"}
    try:
        gauge,receipt=getRWS(year,site)
        source["original_RWS_native_source_receipt"]=receipt
        source["original_RWS_source_status"]="OFFICIAL_NATIVE_CM_NAP_GAUGE_SOURCE_ADMITTED"
        classes={PLAUSIBLE:[],SENTINEL:[]}
        wms_receipts=[]
        for hour in UTC_HOURS:
            instant=stamp(year,hour)
            if instant not in gauge:
                raise ValueError("SOURCE_STOP_NO_RWS_MEASURED_LEVEL_AT_FROZEN_UTC")
            modeled,origin=getmodel(query(year,site,hour))
            label=origin.get("native_GeoJSON_Wasserstand_classification")
            if label not in classes:
                raise ValueError("SOURCE_STOP_WMS_HAS_OTHER_OR_UNPARSEABLE_NATIVE_CLASS_"+str(label))
            if (label==PLAUSIBLE and modeled is None) or (label==SENTINEL and modeled is not None):
                raise ValueError("SOURCE_STOP_INCONSISTENT_NODATA_CLASS_AND_NUMERIC_RETURN")
            classes[label].append(gauge[instant])
            wms_receipts.append({
              "original_fixed_UTC":instant.isoformat(),
              "source_original_WMS_reply_SHA256":origin["source_original_HTTP_JSON_SHA256"],
              "source_model_value_class":label,
              "model_Wasserstand_raw_value_NOT_republished":True,
              "RWS_cmNAP_observed_raw_height_NOT_republished":True})
        if len(wms_receipts)!=len(UTC_HOURS):
            raise ValueError("SOURCE_STOP_NOT_ALL_SIX_FROZEN_UTC_OBSERVATIONS")
        if len(classes[SENTINEL])!=EXPECTED_EXTREME_SENTINEL_N[key]:
            raise ValueError("SOURCE_STOP_BAW_WMS_NODATA_COUNTS_CHANGED_FROM_V206_V207")
        stats=describe_original_observed_height_by_model_class(classes)
        source["source_RWS_levels_by_original_model_validity_class"]=stats
        source["original_SIX_WMS_source_replies_SHA_only"]=wms_receipts
        source["original_BAW_WMS_source_status"]="SIX_AUTHENTIC_ORIGINAL_WMS_FIXED_TIMES_ADMITTED"
        source["source_status"]="RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED"
    except Exception as e:
        source["source_error_kind"]=type(e).__name__
        source["source_error_summary"]=str(e)[:210]
    return source

def classify_frozen_12_group_criterion(groups):
    if set(groups)!=set(EXPECTED_EXTREME_SENTINEL_N):
        raise ValueError("SOURCE_STOP_UNBALANCED_12_SOURCE_COHORTS")
    if any(x.get("source_status")!="RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED"
           for x in groups.values()):
        return {"status":"SOURCE_STOP_ONE_OR_MORE_ORIGINAL_RWS_WMS_GROUPS_UNVERIFIED",
                "n_groups_full_source_admitted":sum(x.get("source_status")==
                    "RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED"
                    for x in groups.values())}
    eligible=[]
    negative_control=[]
    for key,group in groups.items():
        stat=group["source_RWS_levels_by_original_model_validity_class"]
        if stat["n_original_WMS_extreme_NoData_candidates"]==0:
            negative_control.append(key)
        if stat["status"]=="MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE":
            eligible.append((key,stat))
    if len(negative_control)!=4 or len(eligible)!=8:
        raise ValueError("SOURCE_STOP_FROZEN_NODATA_ELIGIBILITY_COHORT_NOT_8_PLUS_4")
    measured_deltas=[x["observed_RWS_sentinel_minus_plausible_mean_NAP_m"]
                     for k,x in eligible]
    directional=sum(x<0 for x in measured_deltas)
    med=median(measured_deltas)
    return {
      "status":"ALL_12_ORIGINAL_SOURCE_SITE_YEAR_MONTH_CLASSIFIED_NO_BIRD",
      "n_frozen_site_month_year_groups":EXPECTED_GROUPS,
      "n_eligible_frozen_mixed_NODATA_and_plausible_groups":len(eligible),
      "n_original_always_plausible_Wierumergronden_control_groups":len(negative_control),
      "n_groups_extreme_NoData_at_lower_original_RWS_height":directional,
      "group_equal_median_sentinel_minus_plausible_RWS_mNAP_m":round(med,8),
      "frozen_directional_criterion_at_least7of8_and_median_negative":(
          directional>=MIN_SUPPORT_GROUPS and med<0),
      "WMS_native_FillValue_and_missingness_mechanism_NOT_VERIFIED":True,
      "posthoc_model_quality_not_independent_animal_response":True}

def run(out=OUT):
    output={
        "analysis":"v209-authentic-BAW-WMS-source-extreme-NoData-vs-RWS-native-cmNAP-level",
        "source_frozen_72_UTC_site_times_reused_from_v206_v207":True,
        "source_fixed_2018_2019_WMS_capabilities_SHA":FIXED_CAPABILITIES_SHA256,
        "source_frozen_12_original_WMS_NODATA_candidate_counts":EXPECTED_EXTREME_SENTINEL_N,
        "prior_v208_model_boundary_gauge_forcing_and_ICON2019_dependence":True,
        "not_original_bird_GPS_or_foraging_behavior":True,
        "status":"SOURCE_STOP"}
    try:
        cat,sha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        # RWS original native catalogue: use the same AquoMeta keys as v206.
        stations=validate_three_pinned_native_stations(cat)
        output["original_RWS_catalogue_SHA256"]=sha
        output["native_RWS_3_stations_rechecked"]=stations
        for year in YEARS:
            raw,receipt=fetch_verified_original_WMS(OFFICIAL_YEAR_WMS[year])
            native=validate_capability_and_layer(raw,year)
            if (receipt["original_WMS_xml_SHA256"]!=FIXED_CAPABILITIES_SHA256[year] or
                not native["source_admissible_for_feature_info_probe"] or
                native["chosen_predeclared_feature_info_format"]!="application/json"):
                raise ValueError("SOURCE_STOP_ORIGINAL_WMS_CAPABILITIES_YEAR_SHA_OR_METADATA")
        groups={}
        for month in MONTHS:
            for year in YEARS:
                for site in STATION_SOURCE_CODES:
                    key=f"{month}_{year}_{site}"
                    groups[key]=one_official_original_source_cohort(month,year,site)
        output["all_12_official_model_validity_vs_measured_tide_level_cohorts"]=groups
        output["descriptive_frozen_8_eligible_plus_4_controls"]=(
            classify_frozen_12_group_criterion(groups))
        output["status"]=output["descriptive_frozen_8_eligible_plus_4_controls"]["status"]
    except Exception as e:
        output["source_failure_kind"]=type(e).__name__
        output["source_failure_summary"]=str(e)[:220]
    output["scientific_source_gates"]={
      "all_72_original_BAW_and_12_RWS_source_cohorts_verified":(
          output["status"]=="ALL_12_ORIGINAL_SOURCE_SITE_YEAR_MONTH_CLASSIFIED_NO_BIRD"),
      "directional_source_low_tide_missingness_criterion_supported":bool(
          output.get("descriptive_frozen_8_eligible_plus_4_controls",{}).get(
            "frozen_directional_criterion_at_least7of8_and_median_negative",False)),
      "native_1e31_value_indeed__FillValue_proven":False,
      "missing_model_Wasserstand_value_proven_dry_ground":False,
      "bird_GPS_15min_tide_and_environmental_occupancy_inferred":False,
      "2018_2019_atmospheric_forcing_change_adjusted":False,
      "bird_ACC_sun_tide_or_social_Boids_ecological_effect_newly_tested":False}
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    safe_summary={}
    for key,g in output.get("all_12_official_model_validity_vs_measured_tide_level_cohorts",{}).items():
        s=g.get("source_RWS_levels_by_original_model_validity_class",{})
        safe_summary[key]={
            "status":g["source_status"],
            "n_extreme":s.get("n_original_WMS_extreme_NoData_candidates"),
            "n_plausible":s.get("n_original_WMS_plausible_source_candidates"),
            "measured_RWS_sentinel_minus_plausible_mean_mNAP_m":
                s.get("observed_RWS_sentinel_minus_plausible_mean_NAP_m"),
            "low_tide_direction_supported":s.get("low_observed_tide_direction_supported"),
            "source_error":g.get("source_error_summary")}
    print("V209_ORIGINAL_LOW_TIDE_NODATA_SOURCE="+json.dumps({
        "status":output["status"],
        "source_global_error":output.get("source_failure_summary"),
        "scientific_source_gates":output["scientific_source_gates"],
        "frozen_group_result":output.get("descriptive_frozen_8_eligible_plus_4_controls"),
        "site_month_year":safe_summary,
        "native_FillValue_and_bird_local_tide_not_proven":True
    },sort_keys=True))
    return output

if __name__=="__main__":
    run()
