"""v91 authentic 2010 Wadden original GPS two-stage rank×tideflat decomposition.

Schier and Ameland real original wild bird 2010 Jun-Dec, NIOZ model native
source with explicit missing Jun/Jul model latitude IMPLICATION from
source-authenticated static grid, real RWS 10minute tide stations and
Astral day/night, original WMR historical mid/high ecotope class3+4.
All old v82/v86 true individual-score and bootstrap results MUST replay
before actual new environment-versus-GPS-composition terms score.
Never export private original animal tag IDs, GPS location, source model
pixels, tide measured rows, individual coefficients or exact datetimes.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from original_nioz_static_2010_grid import original_manifest
from authenticated_nioz_static_template_model import (
    authenticated_template_and_model_months)
from original_rws_cached_transport import OriginalRwsCache
from run_original_two_site_tide_solar_common_months import (
    _fetch_original_two_site_GPS,_original_gauge,GAUGE_CODES)
from two_island_common_month_bird_contrast import (
    SOURCE_MONTHS,prepare_whole_site,true_fourcell_source)
from midhigh_intertidal_source_and_fourway import (
    classify_native_2010_model_sites)
from wild_tideflat_binary_fourway import (
    hard_before_outcome_both_sites)
from two_stage_gps_tide_solar_mixture import (
    original_site_old_outcome_replays,
    decompose_real_original_site,
    summarize_original_two_site_mixture,
    SITES,SEED_NEW)

def run(output,cache_dir):
    model,native_source=authenticated_template_and_model_months(
        original_manifest())
    if sorted(model)!=list(SOURCE_MONTHS):
        raise ValueError("SOURCE_STOP_V91_ORIGINAL_MODEL_7MONTH_FRAME_CHANGED")
    native_original=model[8]["xy"]
    if native_original.shape!=(398520,2):
        raise ValueError("SOURCE_STOP_V91_ORIGINAL_MODEL_NATIVE_GEO_SOURCE")
    for m in SOURCE_MONTHS:
        if not (model[m]["xy"]==native_original).all():
            raise ValueError("SOURCE_STOP_V91_NIOZ_NATIVE_SOURCE_INDEX_DIFFERENT_MONTH")
    classes={}
    wmr_proof={}
    for site in SITES:
        q=classify_native_2010_model_sites(native_original,site)
        classes[site]=q["class"]
        wmr_proof[site]=q["source_record"]
    print("V91_ORIGINAL_SOURCE_NIOZ_AND_WMR_CANONICAL_SHAS_ALL_PASSED "+
          json.dumps({
            "native_model_source_year":2010,
            "original_NIOZ_used_index_physical_units":"UNKNOWN_MONTHLY_MODEL",
            "2010_JuneJuly_lat_source_is_EXPLICIT_STATIC_MODEL_GRID_INFERENCE":True,
            "verified_WMR_model_published_midhigh_source":{
                s:{"WMR_canonical_all_class_SHA":wmr_proof[s][
                   "source_original_WMR_ALL_CODE0_TO6_canonical_geometry_SHA256"],
                   "original_native_model_index_class_sha":wmr_proof[s][
                   "source_true_native_2010_mid_high_class_grid_vector_SHA256"]}
                for s in SITES}},
            sort_keys=True),flush=True)
    (schier,ameland),gps_receipts=_fetch_original_two_site_GPS()
    native_pre={}
    original_source_receipt={}
    for site,rawmonth in (("Schier",schier),("Ameland",ameland)):
        pre,qa=prepare_whole_site(site,rawmonth,model)
        if not qa["all_seven_original_model_and_bird_sources_admitted"]:
            raise ValueError("SOURCE_STOP_V91_PRIOR_V82_ORIGINAL_GPS_MONTH_QA_FAILED")
        native_pre[site]=pre
        original_source_receipt[site]=qa
    four={}
    rws_source={}
    for site in SITES:
        cache=OriginalRwsCache(str(Path(cache_dir)/site.lower()),
                               sleeper=time.sleep)
        tide,manifest=_original_gauge(GAUGE_CODES[site],cache)
        new,meta=true_fourcell_source(native_pre[site],tide)
        four[site]=(new,meta)
        rws_source[site]={
            "true_2010_RWS_official_measured_WATHTE_NAP_source":manifest,
            "source_original_UTC_tide_solar_fourway":meta,
            "publisher_transport_cache_aggregate":cache.snapshot()}
    replay=hard_before_outcome_both_sites(four)
    print("V91_ORIGINAL_V82_AND_V86_RWS_TRUE_TIDE_SOURCE_EXACTLY_REPLAYED "+
          json.dumps(replay,sort_keys=True),flush=True)

    # Both native original bird/RWS/tidal astronomy source gates pass here.
    # Calculate OLD ORIGINAL estimands only; require their bird-level and
    # bootstrap numeric values match previous frozen v82/v86 publications.
    old_scores={}
    old_private={}
    for site in SITES:
        groups=four[site][0]
        out,rank,binary=original_site_old_outcome_replays(
            site,groups,native_pre[site],classes[site])
        old_scores[site]=out
        old_private[site]=(rank,binary)
    print("V91_PREVIOUS_ORIGINAL_V82_RANK_AND_V86_BINARY_EXACT_REPLAY_BEFORE_NEW_COMPONENTS "+
          json.dumps(old_scores,sort_keys=True),flush=True)

    # Only here may the genuinely NEW within-habitat-vs-outside model-rank
    # mixture terms be evaluated at the actual recorded GPS positions.
    value={}
    data={}
    for site in SITES:
        private,summary=decompose_real_original_site(
            site,four[site][0],native_pre[site],classes[site],
            *old_private[site])
        value[site]=private
        data[site]=summary
        public=summary["new_two_channel_tide_solar_mixture_components"]
        print("V91_ORIGINAL_GPS_TIDAL_SOLAR_EXACT_MIXTURE_SOURCE_RESULT "+
              json.dumps({
                "site":site,
                "D_rank_original":public["D_rank"][
                    "original_bird_equal_component_value"],
                "D_mid_high_GPS_fraction_original":public["D_flatP"][
                    "original_bird_equal_component_value"],
                "D_mixture_entry":public["D_entry"][
                    "original_bird_equal_component_value"],
                "D_mixture_entry_original_bird95":public["D_entry"][
                    "10k_original_whole_bird_bootstrap95"],
                "D_conditional_residual":public["D_resid"][
                    "original_bird_equal_component_value"],
                "D_conditional_residual_original_bird95":public["D_resid"][
                    "10k_original_whole_bird_bootstrap95"],
                "original_source_4cell_groups_both_classes":summary[
                    "original_true_source_fourway_habitat_class_support_counts"][
                    "both_habitat_classes"],
                "exact_identity_max_error":summary[
                    "source_max_per_fourcell_algebra_identity_error"],
                "original_bird_data_not_exported":True},
                sort_keys=True),flush=True)
    mix=summarize_original_two_site_mixture(value,data)
    report={
        "analysis":"V91_GENUINE_2010_WADDEN_ORIGINAL_BIRDS_EXACT_MIXTURE_TIDAL_SUNLIGHT_MODEL_RANK_AND_MIDHIGH_GPS_PROPORTION",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_protocol":"docs/V91_FROZEN_ORIGINAL_TWO_STAGE_TIDE_SOLAR_GPS_MIXTURE_DECOMPOSITION.md",
        "original_2010_NIOZ_model_2009_2010_native_grid_provider_source":native_source,
        "source_original_WMR_published_ALL_geometry_class_static_model_sha":wmr_proof,
        "source_true_original_2010_Schier_Ameland_Zenodo_GPS":gps_receipts,
        "source_frozen_old_original_2010_monthly_GPS_native_geography":original_source_receipt,
        "source_two_official_real_2010_RWS_measured_gauges_true_tide_solar":rws_source,
        "frozen_prior_original_source_2010_both_site_4way_replay":replay,
        "frozen_prior_original_bird_bootstrapped_v82_and_v86_effects_REPRODUCED":old_scores,
        "new_post_v86_exploratory_exact_two_component_mixture":mix,
        "mathematical_identity_is_not_new_independent_species_or_causal_habitat_choice":True,
        "NIOZ_native_2010_June_July_missing_lat_inferred_computational_model_only":True,
        "WMR_2021_corrected_v2_exact_identity_UNKNOWN_and_low_littoral2_excluded":True,
        "original_WATLAS_v90_two_other_species_true_fourcell_source_NOT_ADMITTED_unchanged":True,
        "no_true_prey_bird_feeding_active_choice_or_internal_tidal_clock_measured":True,
        "original_bird_tags_GPS_exact_locations_times_RWS_rows_model_pixel_values_NOT_EXPORTED":True}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("V91_ORIGINAL_2010_TWO_STAGE_GPS_EXPOSURE_MODEL_MIXTURE_FINISHED "+
          json.dumps({
            "source_original_true_bird_replay":True,
            "exact_identity_post_v86_hypothesis_supported":mix[
                "post_v86_exploratory_falsifiable_Schier_entry_negative_residual_positive_supported"],
            "source_groups_Schier":data["Schier"][
                "original_true_source_fourway_habitat_class_support_counts"][
                "total_original_fourcell_height_groups"],
            "source_groups_Ameland":data["Ameland"][
                "original_true_source_fourway_habitat_class_support_counts"][
                "total_original_fourcell_height_groups"],
            "no_animal_GPS_or_native_tide_rows_exported":True},
            sort_keys=True),flush=True)
    return report

if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--output",required=True)
    arg.add_argument("--source-cache-dir",
        default=os.environ.get("BOIDS_ORIGINAL_RWS_CACHE_DIR",
                               "/tmp/boids_original_RWS_v91"))
    opts=arg.parse_args();run(opts.output,opts.source_cache_dir)
