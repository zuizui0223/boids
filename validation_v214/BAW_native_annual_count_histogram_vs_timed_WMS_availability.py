"""v214: source-verified 2018/19 BAW annual valid-count pixel VALUE distribution
vs verified original 72 BAW 20min WMS numeric/NoData source reply classifications.

Different products and resolutions: annual 20m Kennwerte nof_valid_data_points
and time-resolved 500m WMS Wasserstand. This does NOT estimate inundation rate.
No raw RWS, WMS time series, bird GPS/ACC, old DEM or WCS pixels are persisted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from pyproj import Transformer
from rasterio.transform import rowcol

from original_BAW_annual_2018_2019_Kennwerte_WCS_source import (
    fetch_year_native_WCS,parse_native_original_annual_WCS
)
from original_BAW_2018_2019_NL_validpoints_DescribeCoverage import (
    FROZEN_VALID_COUNTS,FROZEN_NATIVE_WCS_CAP_SHA,
    fetch_original_coverage_description,inspect_native_coverage_description
)
from original_BAW_annual_validpoints_2018_2019_three_public_sites import (
    PUBLIC_SITE_RD,DESCRIBE_SHA,frozen_public_ROI,
    source_annual_WCS_GetCoverage,source_native_GetCoverage_bytes,
    summarize_native_annual_count_TIFF
)
from validation_v210.sha_verified_v209_source_WMS_selection_bias import (
    exact_original_source,EXPECTED_SOURCE_GROUP_NODATA
)

FROZEN_TIFF_SHA={
    "2018":{
       "VlielandHaven":"2788e1f14a4c13fe779f744126faf238a8b5bf7168e0b8267ec349b7949c1ceb",
       "WestTerschelling":"e298f1c71672588a5b46f6a04392728c21ad58ce6b332190fe1c8ac4571ccffd",
       "Wierumergronden":"0814f98bf4599c652a9d0f5441ae625b92537f1c9beea510ecfcb96a0cc43755"},
    "2019":{
       "VlielandHaven":"2788e1f14a4c13fe779f744126faf238a8b5bf7168e0b8267ec349b7949c1ceb",
       "WestTerschelling":"fafc08190faff51edb724c00e0ac7c9956038ad45d73ea000ecfc3a65d11d10d",
       "Wierumergronden":"0814f98bf4599c652a9d0f5441ae625b92537f1c9beea510ecfcb96a0cc43755"}
}
FROZEN_NUMERIC_PIXEL_N={
    "VlielandHaven":1621,
    "WestTerschelling":1283,
    "Wierumergronden":2500
}
EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR=26281  # candidate, NOT independently documented interval count
OUT=Path(__file__).resolve().parent/"results/source_BAW_2018_2019_annualcount_pixel_fullness_vs_WMS_numeric_v214.json"

def fail_unless(condition,reason):
    if not condition:
        raise ValueError(reason)

def source_native_annual_histogram(valid,values,affine,site):
    """Nonnegative integer validity was SOURCE checked by v213 parser."""
    fail_unless(site in PUBLIC_SITE_RD,"SOURCE_STOP_UNKNOWN_PUBLIC_SITE")
    fail_unless(valid.shape==values.shape and valid.ndim==2,
                "SOURCE_STOP_INVALID_NATIVE_ANNUAL_PIXEL_SHAPE")
    finite=values[valid]
    fail_unless(np.all(np.isfinite(finite)) and np.all(finite>=0) and
                np.all(np.abs(finite-np.rint(finite))<=.001),
                "SOURCE_STOP_INVALID_NATIVE_ANNUAL_COUNT_PIXEL_VALUES")
    ints=np.rint(finite).astype(np.int64)
    unique,counts=np.unique(ints,return_counts=True)
    e,n=Transformer.from_crs("EPSG:28992","EPSG:25832",always_xy=True).transform(
         *PUBLIC_SITE_RD[site])
    row,col=rowcol(affine,e,n)
    fail_unless(0<=row<values.shape[0] and 0<=col<values.shape[1],
                "SOURCE_STOP_PUBLIC_REFERENCE_CENTRE_NOT_IN_ORIGINAL_ROI")
    centre=int(np.rint(values[row,col])) if valid[row,col] else None
    if centre is not None:
        fail_unless(centre>=0,"SOURCE_STOP_NATIVE_CENTRE_NEGATIVE_COUNT")
    return {
      "n_native_pixels_total":int(valid.size),
      "n_native_pixels_with_annual_count_value":int(valid.sum()),
      "n_native_pixels_without_annual_count_value":int(valid.size-valid.sum()),
      "native_spatial_count_value_fraction":round(float(valid.mean()),8),
      "n_native_count_pixels_equal_26281":int(np.sum(ints==EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR)),
      "n_native_count_pixels_below_26281":int(np.sum(ints<EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR)),
      "n_native_count_pixels_above_26281":int(np.sum(ints>EXPECTED_ORIGINAL_MODELED_STEPS_PER_YEAR)),
      "n_native_count_pixels_zero":int(np.sum(ints==0)),
      "minimum_native_count_value":int(unique[0]) if len(unique) else None,
      "maximum_native_count_value":int(unique[-1]) if len(unique) else None,
      "n_distinct_source_annual_count_values":len(unique),
      "source_histogram_capped20":[{"count_value":int(u),"native_pixel_n":int(n)}
          for u,n in zip(unique[:20],counts[:20])],
      "source_histogram_includes_all_distinct_counts":len(unique)<=20,
      "public_reference_centre_floor_rule":"rasterio.transform.rowcol affine nearest-containing pixel deterministic floor, may be on grid edge",
      "native_public_reference_centre_pixel_row_col":[int(row),int(col)],
      "native_public_reference_centre_pixel_has_annual_count":bool(valid[row,col]),
      "native_public_reference_centre_pixel_annual_count_value":centre,
      "modelled_26281_matches_365d_x_72_steps_plus_1_mathematically_only":True,
      "native_product_temporal_sampling_denominator_UNVERIFIED":True,
    }

def original_WMS_source_availability_by_site(original):
    """True original v209 source-safe receipts; never reopen modeled water levels."""
    groups=original["all_12_official_model_validity_vs_measured_tide_level_cohorts"]
    fail_unless(set(groups)==set(EXPECTED_SOURCE_GROUP_NODATA),
                "SOURCE_STOP_ORIGINAL_V209_SITE_GROUP_SCOPE_CHANGED")
    source={}
    for site in PUBLIC_SITE_RD:
        validcount=0
        sentinelcount=0
        years={}
        for year in ("2018","2019"):
            valid_year=0
            sent_year=0
            for month in ("June","September"):
                k=f"{month}_{year}_{site}"
                g=groups[k]["source_RWS_levels_by_original_model_validity_class"]
                p=int(g["n_original_WMS_plausible_source_candidates"])
                s=int(g["n_original_WMS_extreme_NoData_candidates"])
                fail_unless(p+s==6 and s==EXPECTED_SOURCE_GROUP_NODATA[k],
                            "SOURCE_STOP_WMS_FROZEN_DAY_SIX_REPLY_CLASS_COUNT_INVALID")
                valid_year+=p
                sent_year+=s
            fail_unless(valid_year+sent_year==12,"SOURCE_STOP_WMS_YEAR_BOTH_MONTHS_NOT_EXACT_12")
            years[year]={"n_original_time_model_numeric_candidates":valid_year,
              "n_original_time_extreme_NoData_candidates":sent_year,
              "n_frozen_UTC_time_source_replies":12,
              "original_numeric_reply_fraction_12":round(valid_year/12,8)}
            validcount+=valid_year;sentinelcount+=sent_year
        fail_unless(validcount+sentinelcount==24,"SOURCE_STOP_NOT_24_FROZEN_MODEL_REPLIES_PER_SITE")
        source[site]={"by_year":years,"n_original_WMS_plausible_24":validcount,
             "n_original_WMS_extreme_NoData_candidate_24":sentinelcount,
             "original_24_time_numeric_candidate_fraction":round(validcount/24,8),
             "raw_WMS_1e31_is_NATIVE_FillValue_PROVEN":False,
             "not_a_20m_spatial_pixel_fraction":True}
    fail_unless(sum(x["n_original_WMS_plausible_24"] for x in source.values())==50,
                "SOURCE_STOP_ORIGINAL_V209_MODEL_50_OF72_NOT_REPRODUCED")
    return source

def compare_products(native,annual,original_wms):
    pairwise={}
    for site in PUBLIC_SITE_RD:
        y18=annual["2018"][site]
        y19=annual["2019"][site]
        spatial=(y18["native_spatial_count_value_fraction"]+
                 y19["native_spatial_count_value_fraction"])/2
        temporal=original_wms[site]["original_24_time_numeric_candidate_fraction"]
        pairwise[site]={
          "native_annual_WCS_mean_2018_2019_spatial_count_presence_fraction":round(spatial,8),
          "separate_20min_WMS_public_reference_24time_numeric_reply_fraction":temporal,
          "difference_spatial_minus_temporal_NOT_estimate_of_habitat_flooding":round(spatial-temporal,8),
          "these_fractions_HAVE_DIFFERENT_DENOMINATORS":True}
    return {"three_published_sites":pairwise,
            "number_of_sites":len(pairwise),
            "number_of_independent_source_PRODUCTS":2,
            "different_model_products_spatial_cell_vs_temporal_sample":True,
            "frozen_sites_not_an_independent_species_meta_analysis":True,
            "not_a_valid_correlation_or_new_causal_test":True}

def run(original_v209_json,out=OUT):
    original,sha=exact_original_source(original_v209_json,"44452986729")
    wms=original_WMS_source_availability_by_site(original)
    result={"version":"v214-native-annual-count-20m-versus-20min-WMS-source-only-availability",
      "original_v209_source_run_id":44452986729,
      "original_v209_json_verified_SHA256":sha,
      "frozen_native_2018_2019_six_original_annual_WCS_TIFF_SHA256":FROZEN_TIFF_SHA,
      "frozen_2011_published_RD_reference_sites":PUBLIC_SITE_RD,
      "real_time_WMS_and_derived_annual_WCS_not_the_same_product":True,
      "no_bird_GPS_ACC_RWS_source_timeseries_or_new_WMS_request":True,
      "status":"SOURCE_STOP"}
    years={}
    memory={}
    for year in ("2018","2019"):
        entry={"status":"SOURCE_STOP_ORIGINAL_ANNUAL_WCS_YEAR","sites":{}}
        try:
            rawcap,cap=fetch_year_native_WCS(year)
            fail_unless(cap["native_WCS_Capabilities_XML_SHA256"]==
                        FROZEN_NATIVE_WCS_CAP_SHA[year],
                        "SOURCE_STOP_V211_ORIGINAL_CAP_SHA_DRIFT")
            names=parse_native_original_annual_WCS(rawcap)
            fail_unless(FROZEN_VALID_COUNTS[year] in
                [x["original_CoverageId"] for x in names["native_valid_count_candidates"]],
                "SOURCE_STOP_V211_NATIVE_YEAR_COVERAGE_NAME_DRIFT")
            capurl=cap["original_HTTP_source_chain"][-1]["native_url"]
            rawdesc,dreceipt=fetch_original_coverage_description(year,capurl)
            fail_unless(dreceipt["native_DescribeCoverage_XML_SHA256"]==DESCRIBE_SHA[year],
                        "SOURCE_STOP_V212_NATIVE_DESCRIBE_SHA_DRIFT")
            metadata=inspect_native_coverage_description(rawdesc,year)
            fail_unless(any(x.get("native_axisLabels")=="E N" and "25832" in
                  str(x.get("native_srsName")) for x in metadata["original_envelopes"]),
                  "SOURCE_STOP_ORIGINAL_WCS_NATIVE_AXES_NOT_E_N_25832")
            entry["status"]="ORIGINAL_WCS_ANNUAL_YEAR_SOURCE_HEADER_RECHECKED"
            for site in PUBLIC_SITE_RD:
                x={"status":"SOURCE_STOP_ORIGINAL_ANNUAL_SITE"}
                try:
                    url=source_annual_WCS_GetCoverage(year,site,capurl)
                    raw,receipt=source_native_GetCoverage_bytes(url,year,site,capurl)
                    fail_unless(receipt["native_original_HTTP_response_SHA256"]==
                        FROZEN_TIFF_SHA[year][site],
                        "SOURCE_STOP_V213_ORIGINAL_ANNUAL_TIFF_BYTE_SHA_CHANGED")
                    stat,valid,values,transform=summarize_native_annual_count_TIFF(raw,site)
                    fail_unless(stat["n_original_native_numeric_valid_sample_count_pixels"]==
                                FROZEN_NUMERIC_PIXEL_N[site] and stat["n_source_pixels_in_public_ROI"]==2500,
                                "SOURCE_STOP_V213_NATIVE_PUBLIC_SITE_COUNTS_CHANGED")
                    dist=source_native_annual_histogram(valid,values,transform,site)
                    x={"status":"ORIGINAL_NATIVE_YEAR_PUBLIC_COUNT_DISTRIBUTION_AUDITED",
                       "source_original_TIFF_SHA256":receipt["native_original_HTTP_response_SHA256"],
                       "native_annual_valid_count_full_distribution":dist}
                    memory[(year,site)]=(valid,values,transform)
                except Exception as err:
                    x["error_kind"]=type(err).__name__
                    x["error_summary"]=str(err)[:210]
                entry["sites"][site]=x
        except Exception as err:
            entry["error_kind"]=type(err).__name__
            entry["error_summary"]=str(err)[:210]
        years[year]=entry
    result["annual_WCS_source_by_year_site"]=years
    same_year={}
    for site in PUBLIC_SITE_RD:
        a=memory.get(("2018",site))
        b=memory.get(("2019",site))
        if a is None or b is None:
            same_year[site]={"status":"SOURCE_STOP_MISSING_ANNUAL_YEAR_COUNT_SOURCE"}
            continue
        if a[0].shape!=b[0].shape or a[2]!=b[2]:
            same_year[site]={"status":"SOURCE_STOP_NATIVE_WCS_YEARLY_COUNT_CELL_GRID_UNALIGNED"}
            continue
        common=a[0]&b[0]
        changed=common & (np.abs(a[1]-b[1])>0.001)
        same_year[site]={
          "status":"NATIVE_TWO_YEAR_COUNT_MASK_AND_VALUES_COMPARED_WITHOUT_RESAMPLING",
          "original_both_year_numeric_pixel_n":int(common.sum()),
          "original_only_2018_numeric_pixel_n":int((a[0]&~b[0]).sum()),
          "original_only_2019_numeric_pixel_n":int((~a[0]&b[0]).sum()),
          "n_common_annual_count_pixels_with_different_value_in_2019_vs2018":int(changed.sum()),
          "native_same_count_values_source_is_not_original_field_wetting_drying":True}
    result["native_2018_2019_annual_count_mask_and_value_comparison"]=same_year
    result["original_source_verified_v209_WMS_24time_model_availability_by_site"]=wms
    source_ok=all(years[year]["sites"].get(site,{}).get("status")==
          "ORIGINAL_NATIVE_YEAR_PUBLIC_COUNT_DISTRIBUTION_AUDITED"
          for year in years for site in PUBLIC_SITE_RD)
    if source_ok:
        result["source_cross_product_descriptive_comparison"]=compare_products(
            memory, {y:{s:years[y]["sites"][s][
                  "native_annual_valid_count_full_distribution"]
                  for s in PUBLIC_SITE_RD} for y in years},wms)
        result["status"]="V214_SIX_SHA_VERIFIED_ANNUAL_COUNT_HISTOGRAMS_VS_WMS_TIME_AVAILABILITY_SOURCE_ONLY"
    else:
        result["status"]="SOURCE_STOP_SIX_ORIGINAL_ANNUAL_WCS_TIFFS_NOT_FULLY_ADMITTED"
    result["scientific_source_gates"]={
      "all_six_exact_SHA_annual_20m_derived_Count_TIFF_QA_admitted":source_ok,
      "n_source_year_site_count_distribution_verified":sum(years[y]["sites"].get(s,{}).get(
          "status")=="ORIGINAL_NATIVE_YEAR_PUBLIC_COUNT_DISTRIBUTION_AUDITED"
          for y in years for s in PUBLIC_SITE_RD),
      "original_v209_model_50of72_20min_UTC_source_classes_source_verified":True,
      "native_annual_count_temporal_denominator_verified":False,
      "native_20min_BAW_WMS_missing_1e31_actual_FillValue_verified":False,
      "time_resolved_BAW_WMS_drycell_physical_mechanism_proven":False,
      "original_RWS_instrument_and_tagged_bird_GPS_same_pixel":False,
      "original_bird_ACC_sun_tide_social_Boids_effect_newly_estimated":False}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V214_ANNUAL_VS_TIMED_ORIGINAL_AVAILABILITY="+json.dumps({
      "status":result["status"],"scientific_source_gates":result["scientific_source_gates"],
      "annual_year_site_counts":{y:{s:{
          "status":years[y]["sites"][s]["status"],
          "error":years[y]["sites"][s].get("error_summary"),
          "summary":years[y]["sites"][s].get("native_annual_valid_count_full_distribution")}
          for s in PUBLIC_SITE_RD} for y in years},
      "native_year_change":same_year,
      "timed_WMS_valid_share":{s:x["original_24_time_numeric_candidate_fraction"]
             for s,x in wms.items()},
      "cross_product_summary":result.get("source_cross_product_descriptive_comparison"),
      "no_annual_wet_fraction_or_animal_ecology":True
    },sort_keys=True))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--v209-original",required=True,type=Path)
    parser.add_argument("--output",default=OUT,type=Path)
    p=parser.parse_args()
    run(p.v209_original,p.output)
