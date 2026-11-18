"""v191: offline posthoc influence on verified v188 original RWS source-safe receipt.

No raw gauge times, RWS network, bird GPS/ACC, DEM, fit, optimization or new biology.
The original JSON content SHA is frozen from genuine source-success run #44249870280.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from statistics import mean, median

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_CONTENT_NAME="genuine_Wadden13_2018_2019_spatial_LOO_v188.json"
ORIGINAL_JSON_SHA256="e249bd99dcb91c9a8eaf74d82820e1a90212fa721e8f9860563323a5aeb5a2b1"
ORIGINAL_GITHUB_ACTIONS_RUN_ID=44249870280
ORIGINAL_ARTIFACT_ID=14403970497
ORIGINAL_ARCHIVE_ZIP_SHA256="49603b18df9cf6b791b6fe2a5e640e245bba4c8771f481243532d4dc30580380"
EXPECTED_WINDOWS=("2018-06","2018-09","2019-06","2019-09")
EXPECTED_SITES=(
 "DenHelder","Kornwerderzand","Harlingen","Lauwersoog","Eemshaven","Delfzijl",
 "Huibertgat","Schiermonnikoog","Wierumergronden","Nes","WestTerschelling",
 "VlielandHaven","Oudeschild"
)
EXPECTED_STATUS="REAL_WADDEN13_SPATIAL_STATION_LOO_SCORED_NOT_LOCAL_BIRD_TIDE"
OUTPUT=ROOT/"validation_v191/results/verified_v188_source_only_site_influence_v191.json"

class SourceGateError(ValueError):
    pass

def require(condition: bool, msg: str) -> None:
    if not condition:
        raise SourceGateError(msg)

def close(x: float, y: float, tolerance: float=0.000000025) -> bool:
    return math.isfinite(float(x)) and math.isfinite(float(y)) and abs(float(x)-float(y)) <= tolerance

def read_exact_original(path: str | Path) -> dict:
    raw=Path(path).read_bytes()
    sha=hashlib.sha256(raw).hexdigest()
    require(sha==ORIGINAL_JSON_SHA256,"STOP_V188_ARCHIVED_SOURCE_JSON_SHA256_NOT_FROZEN")
    return json.loads(raw)

def valid_source_receipt(r: dict) -> bool:
    return (
      isinstance(r,dict)
      and isinstance(r.get("native_RWS_code"),str)
      and bool(re.fullmatch(r"[0-9a-f]{64}",str(r.get("native_response_SHA256",""))))
      and isinstance(r.get("n_real_cmNAP_timestamps"),int)
      and r["n_real_cmNAP_timestamps"] >= 200
    )

def validate_original_source_aggregate(d: dict) -> dict:
    require(d.get("status")==EXPECTED_STATUS,"STOP_V188_ORIGINAL_SOURCE_STATUS")
    require(d.get("v185_original_failed_5of15_source_gate_preserved") is True,
            "STOP_V185_FAILURE_HISTORY_NOT_PRESERVED")
    require(d.get("v187_13of15_is_POST_failure_exploratory_site_name_repair") is True,
            "STOP_V187_SOURCE_REPAIR_NOT_MARKED_EXPLORATORY")
    require(d.get("no_bird_GPS_ACC_or_DEM_exposure_loaded") is True,
            "STOP_UNKNOWN_RAW_BIOLOGICAL_PAYLOAD")
    require(tuple(d.get("predeclared_sites",()))==EXPECTED_SITES,"STOP_FROZEN_13_SITES_CHANGED")
    require(set(d.get("true_original_heldout_windows",{}))==set(EXPECTED_WINDOWS),
            "STOP_FROZEN_FOUR_ORIGINAL_SOURCE_WINDOWS_CHANGED")
    all_set=set(EXPECTED_SITES)
    report={}
    for year_month in EXPECTED_WINDOWS:
        scope=d["true_original_heldout_windows"][year_month]
        receipts=scope.get("original_RWS_SHA_receipts",{})
        score=scope.get("spatial_holdout_evaluation",{})
        require(set(receipts)==all_set,"STOP_MISSING_OR_SUBSTITUTED_ORIGINAL_NATIVE_STATION_SHA")
        require(all(valid_source_receipt(x) for x in receipts.values()),"STOP_BAD_ORIGINAL_RWS_SHA_OR_N")
        require(score.get("n_frozen_station_target_holdouts")==13,
                "STOP_FROZEN_13_TARGETS_NOT_SCORED")
        require(isinstance(score.get("n_common_original_UTC_timestamps"),int)
                and score["n_common_original_UTC_timestamps"]>=190,
                "STOP_ORIGINAL_COHORT_INSUFFICIENT")
        site_rows=score.get("station_source_only_LOO",{})
        require(set(site_rows)==all_set,"STOP_UNBALANCED_STATION_ROWS")
        site_gain=[]
        site_nearest=[]
        site_idw=[]
        triangles=0
        for target in EXPECTED_SITES:
            r=site_rows[target]
            geom=r["webtics_2011_RD_geometry"]
            names=geom["idw3_sites"]
            weights=geom["idw3_weights"]
            require(len(names)==len(set(names))==3 and all(x in all_set-{target} for x in names),
                    "STOP_TARGET_LEAK_OR_UNFROZEN_NEIGHBOR")
            require(geom["nearest_name"] in all_set-{target},
                    "STOP_TARGET_LEAK_NEAREST")
            require(len(weights)==3 and all(math.isfinite(float(w)) and w>=0 for w in weights)
                    and abs(sum(weights)-1)<1e-9,
                    "STOP_ORIGINAL_NONNORMALIZED_OR_NONFINITE_WEIGHTS")
            require(r.get("target_original_station_solely_scored_not_an_input") is True,
                    "STOP_UNVERIFIED_LEAVE_ONE_SITE_EXCLUSION")
            tri=geom.get("reference_geometry_triangle")
            mse_tri=r.get("mse_triangle_m2")
            if tri is None:
                require(mse_tri is None,"STOP_EXTRAPOLATED_TRIANGLE")
            else:
                require(isinstance(tri,list) and len(tri)==3,
                        "STOP_INVALID_TRIANGLE_GEOMETRY")
                require(all(x in all_set-{target} for x,w in tri),
                        "STOP_TRIANGLE_TARGET_LEAK")
                require(all(float(w)>=-1e-8 and math.isfinite(float(w)) for x,w in tri)
                        and abs(sum(float(w) for x,w in tri)-1)<1e-8,
                        "STOP_INVALID_TRIANGLE_WEIGHTS")
                require(mse_tri is not None and float(mse_tri)>=0,
                        "STOP_MISSING_TRIANGLE_MSE")
                triangles+=1
            n=float(r["mse_nearest_m2"])
            i=float(r["mse_IDW3_m2"])
            g=float(r["nearest_minus_IDW3_MSE_gain_m2"])
            require(n>=0 and i>=0 and close(g,n-i),
                    "STOP_ORIGINAL_STATION_MSE_ARITHMETIC_MISMATCH")
            site_nearest.append(n)
            site_idw.append(i)
            site_gain.append(g)
        require(close(mean(site_nearest),score["equal_station_mean_nearest_MSE_m2"]),
                "STOP_FROZEN_WINDOW_NEAREST_MEAN_RECONCILIATION")
        require(close(mean(site_idw),score["equal_station_mean_IDW3_MSE_m2"]),
                "STOP_FROZEN_WINDOW_IDW_MEAN_RECONCILIATION")
        require(close(mean(site_gain),score["equal_station_mean_nearest_minus_IDW3_MSE_gain_m2"]),
                "STOP_FROZEN_WINDOW_GAIN_MEAN_RECONCILIATION")
        require(triangles==score["n_reference_triangle_inside_hull_targets"],
                "STOP_TRIANGLE_ELIGIBILITY_COUNT")
        require(sum(g>0 for g in site_gain)==score["n_sites_positive_IDW3_vs_nearest"],
                "STOP_FROZEN_SOURCE_POSITIVE_SITE_COUNT")
        report[year_month]={
            "n_original_native_source_SHA_valid":len(receipts),
            "n_common_native_UTC_10min_timestamps":score["n_common_original_UTC_timestamps"],
            "n_target_stations":13,
            "n_positive_stations":sum(g>0 for g in site_gain),
            "equal_station_nearest_mse_m2":round(mean(site_nearest),9),
            "equal_station_idw_mse_m2":round(mean(site_idw),9),
            "equal_station_gain_m2":round(mean(site_gain),9),
            "n_reference_triangles_inside_other_12_hull":triangles,
        }
    summary=d["original_spatial_validation_summary"]
    require(close(mean(report[w]["equal_station_nearest_mse_m2"] for w in EXPECTED_WINDOWS),
                  summary["station_window_equal_mean_nearest_MSE_m2"]),
            "STOP_ORIGINAL_FOUR_WINDOW_NEAREST_MEAN_MISMATCH")
    require(close(mean(report[w]["equal_station_idw_mse_m2"] for w in EXPECTED_WINDOWS),
                  summary["station_window_equal_mean_IDW3_MSE_m2"]),
            "STOP_ORIGINAL_FOUR_WINDOW_IDW_MEAN_MISMATCH")
    require(close(mean(report[w]["equal_station_gain_m2"] for w in EXPECTED_WINDOWS),
                  summary["station_window_equal_nearest_minus_IDW3_MSE_m2"]),
            "STOP_ORIGINAL_FOUR_WINDOW_GAIN_MEAN_MISMATCH")
    return report

def analyze_site_influence(d: dict) -> dict:
    """All 13 sites included in frozen mean. Only remove one for posthoc diagnostic."""
    all_sites={}
    for target in EXPECTED_SITES:
        near=[]
        idw=[]
        gains=[]
        for win in EXPECTED_WINDOWS:
            r=d["true_original_heldout_windows"][win]["spatial_holdout_evaluation"]["station_source_only_LOO"][target]
            near.append(float(r["mse_nearest_m2"]))
            idw.append(float(r["mse_IDW3_m2"]))
            gains.append(float(r["nearest_minus_IDW3_MSE_gain_m2"]))
        first=d.get("site_equalwindow_summary",{}).get(target)
        require(first is not None and close(mean(gains),first["site_equalwindow_mean_gain_m2"]),
                "STOP_ORIGINAL_PRESERVED_13_SITE_SUMMARY_MISMATCH")
        all_sites[target]={"mean_nearest_mse_m2":round(mean(near),9),
          "mean_idw3_mse_m2":round(mean(idw),9),
          "mean_gain_m2":round(mean(gains),9),
          "positive_windows_out_of_four":sum(x>0 for x in gains),
          "window_gain_m2":{win:round(val,9) for win,val in zip(EXPECTED_WINDOWS,gains)}}
    means={s:d["mean_gain_m2"] for s,d in all_sites.items()}
    deletion={s:round(mean(v for site,v in means.items() if site!=s),9)
              for s in EXPECTED_SITES}
    allmean=mean(means.values())
    out={
      "all_site_mean_gain_m2":round(allmean,9),
      "all_site_median_gain_m2":round(median(means.values()),9),
      "n_improved_sites":sum(x>0 for x in means.values()),
      "n_worsened_sites":sum(x<0 for x in means.values()),
      "n_zero_sites":sum(x==0 for x in means.values()),
      "largest_positive_site":max(means,key=means.get),
      "largest_positive_site_gain_m2":max(means.values()),
      "all_13_site_raw_original_MSE_aggregates":all_sites,
      "all_13_delete_one_site_mean_gain_m2":deletion,
      "n_positive_delete_one_site_means":sum(x>0 for x in deletion.values()),
      "n_negative_delete_one_site_means":sum(x<0 for x in deletion.values()),
      "mean_if_largest_positive_site_excluded_m2":
         deletion[max(means,key=means.get)],
      "all_site_mean_sign_changes_if_highest_gain_site_excluded":
         allmean*deletion[max(means,key=means.get)]<0,
      "percent_of_total_positive_net_gain_explained_by_top_site":
         round(100*max(means.values())/sum(means.values()),3) if sum(means.values())!=0 else None,
      "posthoc_influence_exploration_NOT_confirmatory_test":True,
      "no_independent_site_p_value_or_causal_inference":True
    }
    return out

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",default=str(OUTPUT),type=Path)
    opts=ap.parse_args()
    source=read_exact_original(opts.input)
    checked=validate_original_source_aggregate(source)
    influence=analyze_site_influence(source)
    output={
      "version":"v191-frozen-archived-original-v188-source-safe-offline",
      "original_source_run_id":ORIGINAL_GITHUB_ACTIONS_RUN_ID,
      "original_artifact_id":ORIGINAL_ARTIFACT_ID,
      "original_archived_zip_SHA256":ORIGINAL_ARCHIVE_ZIP_SHA256,
      "original_JSON_verified_SHA256":ORIGINAL_JSON_SHA256,
      "source_checked_without_RWS_network":True,
      "scientific_scope":"POSTHOC_SOURCE_SAFE_STATION_INFLUENCE_NOT_NEW_TIDE_OR_BIOLOGY",
      "original_2018_2019_station_year_month_validation":checked,
      "posthoc_site_influence":influence,
      "initial_v185_five_of_fifteen_source_fail_retained":True,
      "historical_DEM_NAP_survey_day_and_GPS_local_tide_gate":"SOURCE_STOP",
      "status":"SOURCE_RECEIPT_CRYPTOGRAPHIC_PASS_AND_POSTHOC_INFLUENCE_REPRODUCED",
    }
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V191_SIGNED_OFFLINE_SCOPE="+json.dumps({
      "status":output["status"],
      "original_JSON_verified_SHA256":ORIGINAL_JSON_SHA256,
      "site_mean_gain_m2":influence["all_site_mean_gain_m2"],
      "site_median_gain_m2":influence["all_site_median_gain_m2"],
      "positive_vs_negative_stations":[influence["n_improved_sites"],influence["n_worsened_sites"]],
      "largest_positive_site":influence["largest_positive_site"],
      "deleting_top_gain_site_mean_m2":influence["mean_if_largest_positive_site_excluded_m2"],
      "delete_one_site_positive_vs_negative":[influence["n_positive_delete_one_site_means"],
                                            influence["n_negative_delete_one_site_means"]],
      "n_physical_original_source_station_windows":sum(v["n_original_native_source_SHA_valid"] for v in checked.values()),
      "no_new_RWS_or_bird_raw_source":True,
      "native_DEM_and_local_GPS_tide":"STOP"
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
