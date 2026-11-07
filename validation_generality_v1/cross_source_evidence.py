"""Generality v1: reproduce only source-backed, incomparable ecological evidence strata.

Downloads public *aggregate* documents only. Exact Git blob SHA1 pins fail closed
on modifications. NEVER downloads animal-level GPS, camera event rows, tag IDs,
raw source location, or future held-out wildlife outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
PUBLIC={
    "RSDS_12_ORIGINAL_DOIS":(
        "zuizui0223/RSDS",
        "research/RSDS_12_STUDY_22_NATIVE_TEMPORAL_MACRO_FIRST_RESULT_20261031.json",
        "af0574c6bb6383402a97b5bebadb8cf0408e9740"),
    "RSDS_FOUR_COMMON_CALENDARS":(
        "zuizui0223/RSDS",
        "research/RSDS_FOUR_COOOBSERVED_CALENDAR_NICHE_V1_FIRST_RESULT_20261031.json",
        "a15bdf0a6edf9e5d632ddd2b46983af7948355b0"),
    "RSDS_SERENGETI_AND_IRELAND_CAMERA":(
        "zuizui0223/RSDS",
        "docs/solar_seasonal_real_exploratory_results_20261015.md",
        "9a717e010ddbf6a0282d68225f80c3285fa557f2"),
    "LOUIS_KING_RAIL_STATE_PORTFOLIO":(
        "zuizui0223/louis","README.md",
        "e1b1e915bce9893fbe203ee57a4c99e759ea6a32"),
}
LOCAL={
    "BOIDS_V63_WILD_TIDAL_PAIRED_DIRECTION":(
        "docs/V63_OBSERVED_TRAIN_TEST_BIRD_UNCERTAINTY_RESULT_JA.md",
        "c04cc2b3a392313d0ab430f0f6d7a5f4ede10bff"),
    "BOIDS_V66_INDEPENDENT_RWS_SOURCE_STOP":(
        "docs/V66_ORIGINAL_RWS_WATLAS_TIME_LAG_VALIDATION_JA.md",
        "95367c2f6f5e0f45236271ac7e72efb4c87e5e98"),
}
NEGATIVE_LONG="NEGATIVE_DIRECTION_NOT_REPLICATED_IN_HELDOUT_SOURCE_SAMPLE"
CLAIM_LEVELS={
    "FIELD_PREDICTIVE_HISTORICAL",
    "FIELD_DESCRIPTIVE_GPS_TIME_USE",
    "FIELD_DESCRIPTIVE_RECORDED_CAMERA_TIME",
    "FIELD_DESCRIPTIVE_HABITAT_STATE_BUFFERING",
    "SOURCE_ONLY_NOT_ADMITTED",
}

def blob_sha(raw:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()

def verify_pin(raw:bytes,expected:str,name:str)->str:
    digest=blob_sha(raw)
    if digest!=expected:
        raise ValueError(f"SOURCE_STOP_GENERALITY_CHANGED_GIT_BLOB_{name}")
    return digest

def remote_aggregate(name,*,getter=None):
    repo,path,hash_=PUBLIC[name]
    url=f"https://raw.githubusercontent.com/{repo}/main/{path}"
    if getter is None:
        def getter(url):
            req=Request(url,headers={"User-Agent":"boids-generality-audit-v1/1.0"})
            with urlopen(req,timeout=40) as resp:
                raw=resp.read(2_000_001)
            if len(raw)>2_000_000:
                raise ValueError("SOURCE_STOP_GENERALITY_AGGREGATE_TOO_LARGE")
            return raw
    raw=getter(url)
    verify_pin(raw,hash_,name)
    return raw

def _assert_contains(document, required, marker):
    for needle in required:
        if needle not in document:
            raise ValueError(f"SOURCE_STOP_GENERALITY_DOCUMENT_RECEIPT_{marker}")

def summarize_rsds_twelve(raw:bytes):
    a=json.loads(raw)
    rows=a["all_original_study_native_taxon_rows_including_HOLD"]
    studies=defaultdict(list)
    for row in rows:
        studies[row["original_study_doi"]].append(row)
    if (a["all_original_studies"]!=12 or len(rows)!=22 or
        a["distinct_native_species_labels"]!=20 or len(studies)!=12):
        raise ValueError("SOURCE_STOP_RSDS_STUDY_NATIVE_OR_SPECIES_COUNT")
    qs=Counter(r["q"]["status"] for r in rows)
    slopes=Counter(r["daylength"]["status"] for r in rows)
    if (qs!={"NEGATIVE":11,"POSITIVE":4,"UNAVAILABLE":7}
            or slopes!={"POSITIVE":5,"NEGATIVE":2,"INCLUDES_ZERO":8,"UNAVAILABLE":7}):
        raise ValueError("SOURCE_STOP_RSDS_NATIVE_SIGN_COUNTS_DRIFT")
    by_study=[]
    study_signs=Counter()
    n_est=0
    for doi in sorted(studies):
        value=[r["q"]["mean"] for r in studies[doi] if r["q"]["mean"] is not None]
        if not value:
            study_signs["UNAVAILABLE"]+=1
            continue
        m=sum(value)/len(value)
        study_signs["POSITIVE" if m>0 else "NEGATIVE" if m<0 else "ZERO"]+=1
        n_est+=1
        by_study.append(m)
    study_mean=sum(by_study)/len(by_study)
    old=a["temporal_q_original_study_equal_inference"]
    if (n_est!=9 or len(by_study)!=9 or
        study_signs!={"POSITIVE":4,"NEGATIVE":5,"UNAVAILABLE":3}
        or not math.isclose(study_mean,old["source_DOI_equal_mean"],abs_tol=1e-12)
        or old["source_DOI_bootstrap95_DESCRIPTIVE_NONPROBABILITY"]!=
            [-0.04923231149820311,0.07674246171695534]):
        raise ValueError("SOURCE_STOP_RSDS_ORIGINAL_DOI_EQUAL_INFERENCE_DRIFT")
    if a.get("external_48_source_negative_shortwave_direction_nonreplication_UNCHANGED") is None:
        raise ValueError("SOURCE_STOP_RSDS_HISTORIC_EXTERNAL_NULL_ERASED")
    return {
        "original_study_DOIs_total":len(studies),
        "original_native_study_taxon_rows":len(rows),
        "distinct_named_taxa":a["distinct_native_species_labels"],
        "original_DOIs_with_estimable_diel_q":n_est,
        "native_taxon_rows_with_estimable_diel_q":qs["POSITIVE"]+qs["NEGATIVE"],
        "native_diel_q_sign_counts":dict(qs),
        "native_daylength_association_sign_counts":dict(slopes),
        "study_equal_diel_q_sign_counts_including_all_HOLD":dict(study_signs),
        "study_equal_diel_q_mean":study_mean,
        "study_cluster_descriptive_95":old["source_DOI_bootstrap95_DESCRIPTIVE_NONPROBABILITY"],
        "study_95_includes_zero":(
            old["source_DOI_bootstrap95_DESCRIPTIVE_NONPROBABILITY"][0]<=0<=
            old["source_DOI_bootstrap95_DESCRIPTIVE_NONPROBABILITY"][1]),
        "native_q_outcome":"observed log1p night minus day GPS straight-line displacement speed, not behavior time",
        "timing_and_direction_heterogeneity_supported":True,
        "no_physical_environment_rate_predictive_increment_estimated":True,
        "all_7_unavailable_native_sources_preserved_not_zeroed":True,
        "old_shortwave_direction_external_nonreplication_preserved":True,
    }

def summarize_rsds_four(raw:bytes,dois_in_twelve:set[str]):
    x=json.loads(raw)
    if (x["original_source_studies_with_identical_native_source_calendar_days"]!=4
        or x["original_studies_with_at_least_one_resolved_native_relative_q_rank"]!=4
        or x["original_studies_with_opposite_supported_native_daylength_slope_signs"]!=3
        or x["four_calendar_study_DOIs_already_in_twelve_study_full_source_macro"]!=3
        or not x["Illinois_original_DOI_is_NOT_part_of_twelve_full_source_study_frame"]):
        raise ValueError("SOURCE_STOP_RSDS_FOUR_COMMON_CALENDAR_DOI_OVERLAP")
    return {
        "original_shared_calendar_DOIs":4,
        "study_with_source_supported_at_least_one_native_q_rank":4,
        "study_with_source_supported_opposite_native_daylength_slopes":3,
        "already_nested_within_twelve_DOIs":3,
        "additional_DOI_outside_twelve":"Illinois observational study (not added to 12-study homogeneous q sample)",
        "coobserved_calendar_not_same_microhabitat_or_true_sun_exposure":True,
        "no_second_independent_four_DOI_pool_allowed":True,
    }

def _document_receipts(serengeti:str,louis:str,boids_v63:str,boids_v66:str):
    _assert_contains(serengeti,[
        "186 source sites","24,290 site×date pairs",
        "38,792 recorded mammal/other-taxon detections",
        "43 source taxon labels","15 source labels",
        "2.6284","0.7917","353 source photograph-date pairs",
        "988 original camera detection rows",
        "camera ON-days"],"RSDS_SEASONAL_CAMERA")
    _assert_contains(louis,["10/10 birds","83.8%","0.162","1.001"],
                     "LOUIS_KING_RAIL")
    _assert_contains(boids_v63,[
        "211","204","1,024","0.176419",
        "0.038154","0.033282","0.304653","0.016655","0.065092"],
        "BOIDS_TIDE_PREDICTION")
    _assert_contains(boids_v66,[
        "4,465","373","423","75.12%","431","433","99.54%","NOT_ADMITTED"],
        "BOIDS_OFFICIAL_RWS_GAUGE")
    return {
        "serengeti":{
            "independent_landscapes":1,
            "original_camera_sites":186,
            "same_site_near_equal_daylength_date_pairs":24290,
            "original_camera_detection_rows":38792,
            "source_taxon_labels_any":43,
            "source_taxon_labels_eligible_for_descriptive_odds":15,
            "example_source_detected_hyena_night_day_falling_vs_rising_OR":2.6284,
            "example_source_detected_Thomsons_gazelle_OR":0.7917,
            "observation_ceiling":"detected photo-time distribution only, no independent camera on-hours or detector q"},
        "northern_ireland":{
            "independent_other_landscape_projects":1,
            "original_site_year_pairable_units":13,
            "event_selected_date_pairs":353,
            "event_rows_in_matched_source":988,
            "largest_site_year_fraction_of_pairs":.5156,
            "observation_ceiling":"source event-selected dates and unverified camera effort; weak external support"},
        "louis":{
            "region_projects":1,
            "original_king_rail_birds":10,
            "birds_positive_temporal_state_retention":10,
            "used_on_available_hydrological_slope":.162,
            "pseudo_use_reference_slope":1.001,
            "observed_coupling_reduction_vs_reference_fraction":.838,
            "response":"used hydrological state retention, NOT tide-derivative heading"},
        "wadden":{
            "original_field_species_count":1,
            "nearby_original_local_sites":2,
            "ameland_real_pairs":168,
            "ameland_matched_original_birds":5,
            "ameland_observed_paired_heading_T":.1676872981,
            "schier_real_pairs":211,
            "schier_matched_original_birds":10,
            "unseen_2010_source_birds":8,
            "v62_identity_disjoint_T":.1764191203,
            "v62_support_qualified_204_pairs_T":.0381544259,
            "v63_train_and_test_bird_interval_all_211":[.033282,.304653],
            "v63_train_and_test_bird_interval_qualified_204":[.016655,.065092],
            "response":"genuinely observed 2011 next-heading unit-vector phase contrast; prior-2010-fitted phase policy direction, not tide-causal turn"},
        "watlas":{
            "sanderling_public_2018_3fix_gauge_phase_rising_falling_source":434,
            "independent_official_RWS_2018_August_10min_gauge_count":4465,
            "unshifted_primary_official_falling_agreement_fraction":.7512,
            "zero_shift_official_source_gate":"NOT_ADMITTED",
            "minus_30min_gauge_companion_agreement_fraction":.9954,
            "minus30_is_not_independent_new_species_heading_gain":True,
        }}

def build_evidence(macro_raw,coobserved_raw,serengeti_doc,louis_doc,boids_v63_doc,boids_v66_doc):
    original=json.loads(macro_raw)
    dois={z["original_study_doi"] for z in
          original["all_original_study_native_taxon_rows_including_HOLD"]}
    macro=summarize_rsds_twelve(macro_raw)
    four=summarize_rsds_four(coobserved_raw,dois)
    others=_document_receipts(serengeti_doc,louis_doc,boids_v63_doc,boids_v66_doc)
    strata=[
        {"source":"BOIDS_V63","environment_forcing":"physical_tide_level_direction",
         "response":"original observed next-step compass heading",
         "claim_level":"FIELD_PREDICTIVE_HISTORICAL",
         "independent_regions":1,"independent_taxa":1,"independent_sites_within_region":2,
         "field_status":"POSITIVE_ASSOCIATIONAL_DIRECTIONAL_CONCORDANCE",
         "not_independent_new_taxon_or_region":True},
        {"source":"RSDS_12_DOI","environment_forcing":"diel_and_astronomical_daylength",
         "response":"observed GPS night-minus-day displacement speed",
         "claim_level":"FIELD_DESCRIPTIVE_GPS_TIME_USE",
         "original_study_DOIs_total":12,"original_studies_q_admitted":9,
         "field_status":"TEMPORAL_DIFFERENTIATION_SIGN_HETEROGENEITY",
         "not_direct_phase_predictive_forecast":True},
        {"source":"RSDS_SERENGETI","environment_forcing":"matched_daylength_opposite_seasonal_branch",
         "response":"original recorded photo timestamps relative to solar light zones",
         "claim_level":"FIELD_DESCRIPTIVE_RECORDED_CAMERA_TIME",
         "independent_landscapes":1,
         "field_status":"RECORDED_TIME_ODDS_NONUNIFORM_BETWEEN_SEASONAL_BRANCHES",
         "source_detection_coverage_unknown":True},
        {"source":"LOUIS_KING_RAIL","environment_forcing":"local_fluctuating_water_depth",
         "response":"hydrological environmental state experienced relative to locally available",
         "claim_level":"FIELD_DESCRIPTIVE_HABITAT_STATE_BUFFERING",
         "independent_regions":1,
         "field_status":"POSITIVE_EXPERIENCED_STATE_BUFFERING",
         "not_tide_direction_or_photoperiod":True},
        {"source":"BOIDS_V66","environment_forcing":"2018_WATLAS_tide_source_clock_alignment",
         "response":"SOURCE-ONLY waterheight phase signed clock agreement",
         "claim_level":"SOURCE_ONLY_NOT_ADMITTED",
         "field_status":"PHASE_GAUGE_CLOCK_CORROBORATION_BUT_PREDECLARED_MAIN_GATE_FAIL",
         "no_new_species_heading_prediction":True},
    ]
    for s in strata:
        if s["claim_level"] not in CLAIM_LEVELS:
            raise ValueError("SOURCE_STOP_UNKNOWN_CLAIM_LEVEL")
    return {
        "analysis":"GENERALITY_V1_AUTHENTIC_CROSS_REPOSITORY_EVIDENCE_SEPARATED_BY_ENDPOINT",
        "scientific_question":"When does environmental change phase add information beyond environment state, conditioned by reachable habitat alternatives?",
        "research_stage":"POST_RESULT_INSPECTABLE_HETEROGENEOUS_EVIDENCE_SYNTHESIS",
        "new_original_individual_GPS_or_camera_outcomes_analyzed":False,
        "original_cross_source_aggregate_GPS":macro,
        "original_RSDS_four_shared_calendar_studies":four,
        "other_noncommensurate_original_field_source_receipts":others,
        "distinct_endpoint_evidence_strata":strata,
        "meta_pooled_effect_across_incompatible_responses":None,
        "single_animal_movement_rate_derivative_estimator_shared_across_forcing_classes":False,
        "cross_species_independent_rate_derivative_predictive_generality_established":False,
        "universal_signed_night_or_tide_coefficient_established":False,
        "prospective_hypothesis_still_untested_across_independent_forcings":True,
        "historical_BOIDS_social_partner_frozen_primary_unconfirmed":True,
        "prior_RSDS_48_shortwave_signed_direction_external_replication_negative_retained":True,
        "source_based_next_test_priority":"source-admitted original GPS daylength spring/fall matched environment value across independent species/year studies with genuine holdout, original source QC first",
        "no_raw_track_event_ids_locations_or_timestamp_released":True,
    }

def run(output):
    remote={name:remote_aggregate(name)
            for name in PUBLIC}
    local={}
    for name,(file,expected) in LOCAL.items():
        raw=(ROOT/file).read_bytes()
        verify_pin(raw,expected,name)
        local[name]=raw.decode("utf-8")
    result=build_evidence(remote["RSDS_12_ORIGINAL_DOIS"],
        remote["RSDS_FOUR_COMMON_CALENDARS"],
        remote["RSDS_SERENGETI_AND_IRELAND_CAMERA"].decode("utf-8"),
        remote["LOUIS_KING_RAIL_STATE_PORTFOLIO"].decode("utf-8"),
        local["BOIDS_V63_WILD_TIDAL_PAIRED_DIRECTION"],
        local["BOIDS_V66_INDEPENDENT_RWS_SOURCE_STOP"])
    result["source_git_blob_sha1"]={
        **{k:hash_ for k,(*_,hash_) in PUBLIC.items()},
        **{k:sha for k,(_,sha) in LOCAL.items()}}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("GENERALITY_V1_SOURCE_BACKED_COMPARATIVE_EVIDENCE "+json.dumps({
        "original_RSDS_DOIs":result["original_cross_source_aggregate_GPS"]["original_study_DOIs_total"],
        "RSDS_taxon_rows":result["original_cross_source_aggregate_GPS"]["original_native_study_taxon_rows"],
        "RSDS_q_positive_native":result["original_cross_source_aggregate_GPS"]["native_diel_q_sign_counts"]["POSITIVE"],
        "RSDS_q_negative_native":result["original_cross_source_aggregate_GPS"]["native_diel_q_sign_counts"]["NEGATIVE"],
        "RSDS_original_DOI_mean95":result["original_cross_source_aggregate_GPS"]["study_cluster_descriptive_95"],
        "RSDS_shared_calendar_support_DOIs":result["original_RSDS_four_shared_calendar_studies"]["study_with_source_supported_at_least_one_native_q_rank"],
        "serengeti_independent_landscapes":result["other_noncommensurate_original_field_source_receipts"]["serengeti"]["independent_landscapes"],
        "historical_tide_observed_direction_support":"POSITIVE",
        "cross_taxon_dynamic_phase_universal_predictive_gain":"NOT_ESTABLISHED"
    },sort_keys=True),flush=True)
    print("GENERALITY_V1_SOURCE_INSPECTABLE_COMPLETED",flush=True)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    run(a.output)
