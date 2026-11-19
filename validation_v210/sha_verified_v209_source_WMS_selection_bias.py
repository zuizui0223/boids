"""v210: SHA-locked source-safe algebraic low-tide selection audit from TWO genuine
v209 RWS/BAW original source runs. No new gauge/model HTTP; no raw tide or birds.

For each of 12 equally weighted site-month-year groups:
mean(original RWS h | WMS plausible) - mean(original RWS h)
    = - sentinel_n / 6 * (mean(h | WMS sentinel)-mean(h | WMS plausible))
computed EXACTLY from original v209 group summaries.
Does NOT infer overall pooled 50/72 observed water-level mean from group data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from statistics import mean,median

FROZEN_ORIGINALS={
 "44452986729":"5e4a492eae99e17b6f79444ac22a342ce5c88f570181fe44a8cc633b1932a62c",
 "44453025281":"be0d2200f5520a6fe5d670d4b3f856427b1a0b880ea9616b5cc374cfb87d04a9",
}
SOURCE_ARTIFACT_NAME="v209-BAW-WMS-original-NoData-vs-RWS-2018-2019-June-September-lowtide-source"
SOURCE_JSON="original_RWS_tide_mNAP_vs_BAW_WMS_extreme_NoData_72points_v209.json"
EXPECTED_N=6
EXPECTED_SOURCE_GROUP_NODATA={
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
EXPECTED_MODEL_EXTREME_N=22
EXPECTED_WMS_REPLY_N=72
EXPECTED_RWS_COHORTS=12
SENTINEL="EXTREME_NODATA_SENTINEL_CANDIDATE"
PLAUSIBLE="PLAUSIBLE_NUMERIC_MODEL_RESPONSE_UNIT_NOT_VERIFIED"
OUT=Path(__file__).resolve().parent/"results/v210_original_SHA_locked_WMS_NODATA_low_tide_selection_bias.json"

class OriginalSourceIntegrityStop(ValueError):
    pass

def require(condition,reason):
    if not condition:
        raise OriginalSourceIntegrityStop(reason)

def exact_original_source(path,run_id):
    require(run_id in FROZEN_ORIGINALS,"SOURCE_STOP_NOT_FROZEN_GH_ACTIONS_RUN")
    p=Path(path)
    raw=p.read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    require(sha==FROZEN_ORIGINALS[run_id],
        "SOURCE_STOP_MODIFIED_OR_WRONG_ORIGINAL_V209_SOURCE_JSON")
    obj=json.loads(raw)
    require(obj.get("status")=="ALL_12_ORIGINAL_SOURCE_SITE_YEAR_MONTH_CLASSIFIED_NO_BIRD",
        "SOURCE_STOP_V209_ORIGINAL_PHYSICAL_SOURCE_GATE_NOT_ADMITTED")
    require(obj.get("scientific_source_gates",{}).get(
        "all_72_original_BAW_and_12_RWS_source_cohorts_verified") is True,
        "SOURCE_STOP_V209_ORIGINAL_72_WMS_AND_12_RWS_NOT_SOURCE_ADMITTED")
    require(obj.get("scientific_source_gates",{}).get(
        "native_1e31_value_indeed__FillValue_proven") is False,
        "SOURCE_STOP_CANNOT_SILENTLY_UPGRADE_MISSINGNESS_MECHANISM")
    cohorts=obj.get("all_12_official_model_validity_vs_measured_tide_level_cohorts",{})
    require(set(cohorts)==set(EXPECTED_SOURCE_GROUP_NODATA),
        "SOURCE_STOP_ORIGINAL_GROUP_SCOPE_CHANGED")
    for k,g in cohorts.items():
        require(g.get("source_status")==
                "RWS_MODEL_AVAILABILITY_AND_NATIVE_WATERLEVEL_SOURCE_AUDITED",
                "SOURCE_STOP_ORIGINAL_GAUGE_MODEL_COHORT_NOT_SOURCE_ADMITTED")
        s=g.get("source_RWS_levels_by_original_model_validity_class",{})
        n_s=s.get("n_original_WMS_extreme_NoData_candidates")
        n_v=s.get("n_original_WMS_plausible_source_candidates")
        n=s.get("n_original_measured_RWS_exact_UTC_paired")
        require(n_s==EXPECTED_SOURCE_GROUP_NODATA[k] and n_v+n_s==EXPECTED_N and n==EXPECTED_N,
                "SOURCE_STOP_ORIGINAL_FROZEN_NODATA_COUNTS_CHANGED")
        rws=g.get("original_RWS_native_source_receipt",{})
        require(bool(re.fullmatch(r"[0-9a-f]{64}",str(
            rws.get("original_RWS_publisher_JSON_SHA256","")))),
            "SOURCE_STOP_NATIVE_ORIGINAL_RWS_PUBLISHER_SHA_MISSING")
        wms=g.get("original_SIX_WMS_source_replies_SHA_only",[])
        require(len(wms)==EXPECTED_N,"SOURCE_STOP_ORIGINAL_WMS_HAS_NOT_SIX_FROZEN_UTC_REPLIES")
        require(sum(z.get("source_model_value_class")==SENTINEL for z in wms)==n_s,
                "SOURCE_STOP_NATIVE_WMS_SOURCE_CLASS_COUNTS_DISAGREE_WITH_SUMMARY")
        require(sum(z.get("source_model_value_class")==PLAUSIBLE for z in wms)==n_v,
                "SOURCE_STOP_NATIVE_WMS_PLAUSIBLE_CLASS_COUNTS_DISAGREE_WITH_SUMMARY")
        for z in wms:
            require(bool(re.fullmatch(r"[0-9a-f]{64}",str(z.get(
                "source_original_WMS_reply_SHA256","")))),
                "SOURCE_STOP_NATIVE_WMS_RESPONSE_SHA_MISSING")
            require(z.get("RWS_cmNAP_observed_raw_height_NOT_republished") is True,
                "SOURCE_STOP_UNVERIFIED_RWS_RAW_SOURCE_PUBLICATION_POLICY")
    return obj,sha

def ensure_independent_replays_same_source_statistical_content(a,b):
    ga=a["all_12_official_model_validity_vs_measured_tide_level_cohorts"]
    gb=b["all_12_official_model_validity_vs_measured_tide_level_cohorts"]
    identical_model_raw_sha=0
    original_measured_sha_equal=0
    source_class_replay_equal=0
    for key in EXPECTED_SOURCE_GROUP_NODATA:
        x,y=ga[key],gb[key]
        require(x["source_RWS_levels_by_original_model_validity_class"]==
                y["source_RWS_levels_by_original_model_validity_class"],
                "SOURCE_STOP_TWO_V209_REPLAYS_HAVE_CONFLICTING_MEASURED_RWS_CLASS_STATS")
        r1=x["original_RWS_native_source_receipt"]
        r2=y["original_RWS_native_source_receipt"]
        equal=r1["original_RWS_publisher_JSON_SHA256"]==r2["original_RWS_publisher_JSON_SHA256"]
        require(equal,"SOURCE_STOP_ORIGINAL_RWS_RAW_PUBLISHER_SOURCE_SHA_CHANGED")
        original_measured_sha_equal+=1
        replies1=x["original_SIX_WMS_source_replies_SHA_only"]
        replies2=y["original_SIX_WMS_source_replies_SHA_only"]
        for u,v in zip(replies1,replies2):
            require(u["fixed_UTC_time"]==v["fixed_UTC_time"] and
                    u["source_model_value_class"]==v["source_model_value_class"],
                    "SOURCE_STOP_ORIGINAL_TWO_RUNS_WMS_HAS_DIFFERENT_CLASS_OR_UTC")
            source_class_replay_equal+=1
            identical_model_raw_sha+=int(
                u["source_original_WMS_reply_SHA256"]==
                v["source_original_WMS_reply_SHA256"])
    require(source_class_replay_equal==EXPECTED_WMS_REPLY_N and
            original_measured_sha_equal==EXPECTED_RWS_COHORTS,
            "SOURCE_STOP_ORIGINAL_REPLAY_NOT_FROZEN_72_AND_12")
    return {
        "reproduced_native_RWS_provider_SHAs_equal_of_12":original_measured_sha_equal,
        "WMS_original_fixed_UTC_and_source_classes_identical_of_72":source_class_replay_equal,
        "WMS_raw_HTTP_SHA_equal_of_72":identical_model_raw_sha,
        "source_raw_WMS_byte_variability_not_height_value_variability_proof":True,
        "WMS_original_nodata_flags_are_numeric_candidate_only":True}

def exactly_identifiable_group_selection_delta(s):
    n_s=s["n_original_WMS_extreme_NoData_candidates"]
    n_v=s["n_original_WMS_plausible_source_candidates"]
    n=n_s+n_v
    require(n==EXPECTED_N,"SOURCE_STOP_SOURCE_GROUP_NOT_EXACT_SIX")
    if n_s==0:
        require(n_v==EXPECTED_N and
                s["observed_RWS_sentinel_minus_plausible_mean_NAP_m"] is None,
                "SOURCE_STOP_INVALID_ORIGINAL_ALWAYS_NUMERIC_SOURCE_CONTROL")
        return 0.0
    require(n_s>=2 and n_v>=2 and
            s.get("status")=="MEASURED_RWS_LEVEL_VS_MODEL_NODATA_CLASS_CONTRAST_EVALUABLE",
            "SOURCE_STOP_ORIGINAL_RWS_GROUP_CONTRAST_NOT_ADMITTED")
    delta=s["observed_RWS_sentinel_minus_plausible_mean_NAP_m"]
    require(isinstance(delta,(float,int)) and math.isfinite(delta),
            "SOURCE_STOP_NONFINITE_NATIVE_RWS_MEAN_DIFFERENCE")
    return -(n_s/n)*float(delta)

def report_selection_bias(source,hash_a,hash_b,replay):
    rows=[]
    for key,s in source["all_12_official_model_validity_vs_measured_tide_level_cohorts"].items():
        x=s["source_RWS_levels_by_original_model_validity_class"]
        shift=exactly_identifiable_group_selection_delta(x)
        rows.append({"site_month_year":key,
              "n_native_RWS_exact_UTC":x["n_original_measured_RWS_exact_UTC_paired"],
              "WMS_original_extreme_sentinel_candidate_n":x["n_original_WMS_extreme_NoData_candidates"],
              "WMS_original_plausible_numeric_candidate_n":x["n_original_WMS_plausible_source_candidates"],
              "observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped":round(shift,9),
              "source_delta_measured_RWS_unit_m_NAP_not_WMS_unit":True,
              "native_WMS_FillValue_and_missingness_reason_NOT_verified":True})
    mixed=[x for x in rows if x["WMS_original_extreme_sentinel_candidate_n"]>0]
    controls=[x for x in rows if x["WMS_original_extreme_sentinel_candidate_n"]==0]
    require(len(rows)==EXPECTED_RWS_COHORTS and len(mixed)==8 and len(controls)==4,
            "SOURCE_STOP_NATIVE_GROUP_ELIGIBILITY_NOT_FROZEN_EIGHT_PLUS_FOUR")
    mean8=mean(x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"] for x in mixed)
    med8=median(x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"] for x in mixed)
    mean12=mean(x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"] for x in rows)
    med12=median(x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"] for x in rows)
    return {
      "version":"v210-offline-SHA-verified-original-v209-WMS-NoData-selection-shift",
      "original_source_run_JSON_sha256":{"44452986729":hash_a,"44453025281":hash_b},
      "frozen_original_source_artifact_name":SOURCE_ARTIFACT_NAME,
      "two_true_original_source_replay_controls":replay,
      "all_12_group_native_RWS_selection_bias_mNAP":rows,
      "source_selection_summary":{
         "n_original_site_month_year_groups":len(rows),
         "n_coastal_mixed_source_groups":len(mixed),
         "n_always_numeric_Wierumergronden_controls":len(controls),
         "total_source_WMS_plausible_numeric_n":
            sum(x["WMS_original_plausible_numeric_candidate_n"] for x in rows),
         "total_source_WMS_extreme_NoData_candidate_n":
            sum(x["WMS_original_extreme_sentinel_candidate_n"] for x in rows),
         "n_source_coastal_groups_valid_only_RWS_mean_shift_positive":
            sum(x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"]>0 for x in mixed),
         "coastal_eight_group_equal_mean_RWS_mNAP_shift":round(mean8,9),
         "coastal_eight_group_equal_median_RWS_mNAP_shift":round(med8,9),
         "all_twelve_group_equal_mean_RWS_mNAP_shift":round(mean12,9),
         "all_twelve_group_equal_median_RWS_mNAP_shift":round(med12,9),
         "all_eight_source_coastal_group_shift_positive":all(
            x["observed_RWS_mNAP_group_mean_shift_if_WMS_sentinel_dropped"]>0
            for x in mixed),
         "source_bias_is_WMS_valid_only_selection_not_an_actual_bird_outcome":True,
         "NOT_equivalent_to_global_original_72_vs_selected_50_RWS_overall_mean_difference":True,
         "preexisting_v209_contrasts_algebraically_reexpressed_not_independent_retest":True,
      },
      "scientific_source_gates":{
        "both_exact_authentic_v209_source_safe_JSONs_matched_and_replayed":True,
        "recomputed_measured_RWS_low_tide_source_valid_only_shift_groupwise":True,
        "native_BAW_WMS__FillValue_equals_1e31_confirmed":False,
        "raw_original_BAW_or_RWS_tide_retrieved_in_v210":False,
        "native_bird_GPS_local_model_tide_or_wetdry_inferred":False,
        "bird_sun_tide_social_Boids_ecological_causal_effect_newly_estimated":False,
      },
      "status":"V210_ORIGINAL_V209_TWO_SOURCE_REPLAYS_SHA_VERIFIED_GROUPWISE_SELECTION_SHIFT"
    }

def run(original_a,original_b,out=OUT):
    a,hash_a=exact_original_source(original_a,"44452986729")
    b,hash_b=exact_original_source(original_b,"44453025281")
    replay=ensure_independent_replays_same_source_statistical_content(a,b)
    report=report_selection_bias(a,hash_a,hash_b,replay)
    p=Path(out)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    d=report["source_selection_summary"]
    print("V210_ORIGINAL_WMS_SELECTION_SHIFT="+json.dumps({
      "status":report["status"],
      "n_coastal_groups_positive_shift":d["n_source_coastal_groups_valid_only_RWS_mean_shift_positive"],
      "coastal_eight_group_equal_mean_mNAP_shift":d["coastal_eight_group_equal_mean_RWS_mNAP_shift"],
      "coastal_eight_group_equal_median_mNAP_shift":d["coastal_eight_group_equal_median_RWS_mNAP_shift"],
      "all_twelve_group_equal_mean_mNAP_shift":d["all_twelve_group_equal_mean_RWS_mNAP_shift"],
      "all_twelve_group_equal_median_mNAP_shift":d["all_twelve_group_equal_median_RWS_mNAP_shift"],
      "original_source_replay":replay,
      "negative_control_groups_n":d["n_always_numeric_Wierumergronden_controls"],
      "no_actual_bird_behavior_or_model_native_units_verified":True
    },sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original_a",type=Path,required=True)
    p.add_argument("--original_b",type=Path,required=True)
    p.add_argument("--output",type=Path,default=OUT)
    opts=p.parse_args()
    run(opts.original_a,opts.original_b,opts.output)
