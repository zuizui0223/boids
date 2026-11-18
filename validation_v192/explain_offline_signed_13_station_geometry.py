"""v192: exact-SHA original-source-only posthoc geographic falsification.

Use frozen 2011 WEBTICS geometry of 13 target gauges, original verified v188
gauge LOO errors. Predict station-specific IDW3-vs-nearest gain with train-only
standardization and ridge alpha 1. No raw RWS series, GPS, ACC, DEM, site
selection, ecological mechanism, or station instrument geolocation claims.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, median

import numpy as np
from scipy.stats import spearmanr

from validation_v191.reanalyse_signed_v188_source_artifact import (
    EXPECTED_SITES, EXPECTED_WINDOWS, ORIGINAL_JSON_SHA256, ROOT,
    analyze_site_influence, read_exact_original, require,
    validate_original_source_aggregate
)

OUT=ROOT/"validation_v192/results/verified_geometry_station_LOSO_v192.json"
RIDGE_ALPHA=1.0

def geometry_and_station_gain(data: dict) -> tuple[list[dict],np.ndarray,np.ndarray]:
    """One row per station; metadata must not vary by source window."""
    base=data["true_original_heldout_windows"][EXPECTED_WINDOWS[0]]["spatial_holdout_evaluation"]["station_source_only_LOO"]
    rows=[]
    features=[]
    gains=[]
    for site in EXPECTED_SITES:
        first=base[site]["webtics_2011_RD_geometry"]
        for win in EXPECTED_WINDOWS[1:]:
            other=data["true_original_heldout_windows"][win]["spatial_holdout_evaluation"]["station_source_only_LOO"][site]["webtics_2011_RD_geometry"]
            require(first==other,"STOP_STATION_REFERENCE_GEOMETRY_DIFFERS_BETWEEN_SOURCE_WINDOWS")
        nearest=float(first["nearest_distance_RD_m"])
        weights=np.asarray(first["idw3_weights"],dtype=float)
        require(np.isfinite(nearest) and nearest>0,"STOP_INVALID_SOURCE_GEOGRAPHIC_DISTANCE")
        require(weights.shape==(3,) and np.all(np.isfinite(weights)) and
                np.all(weights>0) and abs(np.sum(weights)-1)<1e-9,
                "STOP_INVALID_SOURCE_IDW3_GEO_WEIGHTS")
        geo1=math.log(nearest/1000)
        geo2=1.0/float(np.dot(weights,weights))
        tri=first["reference_geometry_triangle"] is not None
        period_gain=[float(data["true_original_heldout_windows"][win]["spatial_holdout_evaluation"]["station_source_only_LOO"][site]["nearest_minus_IDW3_MSE_gain_m2"])
                     for win in EXPECTED_WINDOWS]
        gain=mean(period_gain)
        require(math.isfinite(gain),"STOP_STATION_GAIN_NONFINITE")
        rows.append({"original_source_site":site,
          "nearest_other_2011_reference_RD_km":round(nearest/1000,8),
          "log_nearest_other_2011_reference_RD_km":round(geo1,8),
          "IDW3_effective_neighbor_count":round(geo2,8),
          "triangle_interior_of_remaining_12_reference_points":tri,
          "source_four_period_gains_m2":dict(zip(EXPECTED_WINDOWS,[round(x,9) for x in period_gain])),
          "source_four_period_equal_mean_gain_m2":round(gain,9),
          "no_original_2018_2019_instrument_geolocation_claim":True})
        features.append([geo1,geo2])
        gains.append(gain)
    return rows,np.asarray(features,dtype=float),np.asarray(gains,dtype=float)

def predict_ridge_train_only(xtrain:np.ndarray,ytrain:np.ndarray,xtest:np.ndarray,alpha=RIDGE_ALPHA) -> float:
    """Fixed two-parameter ridge; training fold owns scale and intercept."""
    require(len(xtrain)>=5 and xtrain.shape[1]==2 and xtest.shape==(2,),
            "STOP_MALFORMED_GEOMETRY_PREDICTION_INPUT")
    mu=np.mean(xtrain,axis=0)
    sd=np.std(xtrain,axis=0,ddof=0)
    sd=np.where(sd>1e-10,sd,1.)
    xx=(xtrain-mu)/sd
    zz=(xtest-mu)/sd
    b=np.linalg.solve(xx.T@xx + alpha*np.eye(2),xx.T@(ytrain-np.mean(ytrain)))
    return float(np.mean(ytrain)+zz@b)

def leave_one_station_out(x:np.ndarray,y:np.ndarray) -> dict:
    require(x.shape==(13,2) and y.shape==(13,) and
            np.all(np.isfinite(x)) and np.all(np.isfinite(y)),
            "STOP_NOT_FROZEN_13_BY_2_SOURCE_GEO_LOSO")
    ridge=[]
    baseline=[]
    baseline_sign=[]
    for i in range(len(y)):
        mask=np.arange(len(y))!=i
        xx=x[mask]
        yy=y[mask]
        yp=predict_ridge_train_only(xx,yy,x[i])
        ridge.append(yp)
        baseline.append(float(np.mean(yy)))
        positive=int(np.sum(yy>0))
        negative=int(np.sum(yy<0))
        baseline_sign.append(1 if positive>=negative else -1)
    ridge=np.asarray(ridge)
    baseline=np.asarray(baseline)
    signs=np.where(y>0,1,-1)
    rsign=np.where(ridge>0,1,-1)
    bs=np.asarray(baseline_sign)
    ridge_mse=float(np.mean(np.square(ridge-y)))
    base_mse=float(np.mean(np.square(baseline-y)))
    return {"ridge_station_LOSO_gain_predictions_m2":np.round(ridge,9).tolist(),
       "training_only_mean_station_LOSO_gain_predictions_m2":np.round(baseline,9).tolist(),
       "station_LOSO_geometry_ridge_MSE_m4":round(ridge_mse,10),
       "station_LOSO_training_only_mean_baseline_MSE_m4":round(base_mse,10),
       "station_LOSO_baseline_minus_geometry_ridge_MSE_gain_m4":round(base_mse-ridge_mse,10),
       "geometry_MSE_improvement_fraction_over_baseline":round((base_mse-ridge_mse)/base_mse,8) if base_mse>0 else None,
       "geometry_LOSO_sign_correct_out_of_13":int(np.sum(rsign==signs)),
       "train_majority_sign_baseline_correct_out_of_13":int(np.sum(bs==signs)),
       "ridge_alpha_fixed_no_tuning":RIDGE_ALPHA,
       "train_only_scaling_per_hidden_station":True,
       "each_station_mean_over_four_month_windows_one_independent_unit":True}

def geometrical_descriptives(rows:list[dict],x:np.ndarray,y:np.ndarray) -> dict:
    rnear=float(spearmanr(x[:,0],y).statistic)
    reff=float(spearmanr(x[:,1],y).statistic)
    interior=np.asarray([r["triangle_interior_of_remaining_12_reference_points"] for r in rows])
    require(np.sum(interior)>0 and np.sum(~interior)>0,
            "STOP_MISSING_REFERENCE_TRIANGLE_COMPARISON_GROUP")
    return {
      "site_n_13":len(y),
      "spearman_log_nearest_RD_distance_vs_gain":round(rnear,7),
      "spearman_IDW3_effective_n_vs_gain":round(reff,7),
      "inside_triangle_n":int(np.sum(interior)),
      "outside_triangle_n":int(np.sum(~interior)),
      "inside_triangle_site_median_gain_m2":round(float(np.median(y[interior])),9),
      "outside_triangle_site_median_gain_m2":round(float(np.median(y[~interior])),9),
      "inside_minus_outside_median_gain_m2":round(float(np.median(y[interior])-np.median(y[~interior])),9),
      "both_correlations_EXPLORATORY_no_pvalues":True,
      "not_original_RWS_native_instrument_geometry":True,
    }

def run(source_path:Path,out_path=OUT) -> dict:
    data=read_exact_original(source_path)
    original=validate_original_source_aggregate(data)
    influence=analyze_site_influence(data)
    rows,x,y=geometry_and_station_gain(data)
    prediction=leave_one_station_out(x,y)
    desc=geometrical_descriptives(rows,x,y)
    require(abs(mean(y)-influence["all_site_mean_gain_m2"])<2e-8,
            "STOP_SITE_GAIN_DISAGREES_WITH_PRIOR_SOURCE_VERIFIED_INFLUENCE")
    for i,row in enumerate(rows):
        row["geometry_LOSO_predicted_gain_m2"]=prediction["ridge_station_LOSO_gain_predictions_m2"][i]
        row["training_mean_LOSO_baseline_predicted_gain_m2"]=prediction["training_only_mean_station_LOSO_gain_predictions_m2"][i]
        row["observed_sign_positive"]=bool(y[i]>0)
        row["predicted_sign_positive"]=bool(prediction["ridge_station_LOSO_gain_predictions_m2"][i]>0)
    output={
      "analysis":"v192_source_signed_original_13_station_geometry_LOSO_POSTHOC",
      "original_v188_JSON_exact_SHA256":ORIGINAL_JSON_SHA256,
      "n_frozen_source_station_windows":sum(
         k["n_original_native_source_SHA_valid"] for k in original.values()),
      "source_validation":"EXACT_SHA_NATIVE_RWS_13_BY_4_STATION_LOO_VERIFIED_OFFLINE",
      "reference_geography":"WEBTICS_2011_RD_not_2018_or_2019_original_instrument_verification",
      "site_level_source_safe_geometry_gain_rows":rows,
      "fixed_two_feature_station_prediction":prediction,
      "geometric_posthoc_descriptives":desc,
      "original_station_influence_from_v191":{
         "n_positive_stations":influence["n_improved_sites"],
         "n_negative_stations":influence["n_worsened_sites"],
         "all_site_station_mean_m2":influence["all_site_mean_gain_m2"],
         "without_Eemshaven_station_mean_m2":influence["all_13_delete_one_site_mean_gain_m2"]["Eemshaven"]},
      "inference_warning":"Posthoc source-only station-level exploration after v188, not independent confirmation. No new original RWS heights and no 2018/19 survey geolocation verified.",
      "bird_GPS_local_water_depth_exposure_tide_solar_boids":"SOURCE_STOP",
      "status":"V192_ORIGINAL_SIGNED_OFFLINE_STATION_GEOMETRY_LOSO_SCORED_EXPLORATORY"
    }
    p=Path(out_path)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(output,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V192_SIGNED_GEOMETRY_SCOPE="+json.dumps({
      "status":output["status"],
      "site_LOSO":prediction,
      "geometry":desc,
      "n_station_windows":output["n_frozen_source_station_windows"],
      "posthoc_not_causal":True,
      "local_bird_GPS_exposure":"STOP"
    },sort_keys=True),flush=True)
    return output

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",default=OUT,type=Path)
    args=parser.parse_args()
    run(args.input,args.output)
