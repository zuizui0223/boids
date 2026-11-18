"""v190: original RWS physical gauge-to-gauge phase-transfer, 2018 June fit to 2018/19 heldouts.

Calibrated known target stations: target's 2018-June tide is USED to learn
edge phase lag. NOT leave-one-station-out extrapolation or local bird GPS h(s,t).
"""
from __future__ import annotations
from datetime import timedelta
from pathlib import Path
import json,math,time
from collections import Counter
from statistics import mean,median
from rws_roompot_2020_source import publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop
from original_RWS_two_gauge_comparison import original_nap_series
from original_Wadden13_RWS_tide_LOO import STATIONS,geometry_for_target
from original_RWS_15_fixed_seaward_sites import CODE

TRAIN=(2018,6)
HOLDS=((2018,9),(2019,6),(2019,9))
GRID_MIN=tuple(range(-120,121,10))
MIN_PAIRS=200
OUT=Path(__file__).resolve().parent/"results/original_RWS_Wadden13_2018fit_2019_holdout_phase_transfer_v190.json"

def authentic_post(route,data):
    for attempt in range(3):
        try:return publisher_post(route,data)
        except SourceStop as e:
            if ("SOURCE_UNAVAILABLE_OR_RATE_LIMITED_OFFICIAL_RWS_" not in str(e)
                or attempt==2):raise
            time.sleep(2**attempt)
    raise SourceStop("OFFICIAL_RWS_UNREACHABLE")

def source_window(year,month):
    series={};sources={}
    for site in STATIONS:
        code=CODE[site]
        req={"Locatie":{"Code":code},
             "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
             "Periode":{"Begindatumtijd":f"{year}-{month:02d}-01T00:00:00.000+01:00",
                        "Einddatumtijd":f"{year}-{month:02d}-03T00:00:00.000+01:00"}}
        original,sha=authentic_post(DATA_ROUTE,req)
        levels,excluded=original_nap_series(original)
        series[site]=levels
        sources[site]={"official_RWS_code":code,"original_response_SHA256":sha,
                       "n_native_true_cmNAP":len(levels),
                       "source_exclusion_reasons":excluded}
    return series,sources

def pair_pearson_for_lag(target,neighbor,lag):
    dt=timedelta(minutes=lag)
    pairs=[(target[t],neighbor[t-dt]) for t in target if t-dt in neighbor]
    if len(pairs)<MIN_PAIRS:raise SourceStop("INSUFFICIENT_EDGE_ORIGINAL_TRAIN_PAIRS")
    xbar=mean(a for a,b in pairs);ybar=mean(b for a,b in pairs)
    sxy=sum((a-xbar)*(b-ybar) for a,b in pairs)
    sx=sum((a-xbar)**2 for a,b in pairs)
    sy=sum((b-ybar)**2 for a,b in pairs)
    if sx*sy<=1e-8:raise SourceStop("NEAR_CONSTANT_ORIGINAL_GAUGE_TRAINING")
    return sxy/math.sqrt(sx*sy),len(pairs)

def fit_lag_one_edge(target,neighbor):
    found=[]
    for lag in GRID_MIN:
        rho,n=pair_pearson_for_lag(target,neighbor,lag)
        found.append((lag,rho,n))
    chosen=min(found,key=lambda x:(-x[1],abs(x[0]),x[0]))
    return {"trained_2018_June_lag_min":chosen[0],
            "training_max_pearson_r":round(chosen[1],8),
            "training_native_pairs_for_selected_lag":chosen[2],
            "searched_frozen_25_lags":len(GRID_MIN),
            "target_2018_June_gauge_used_to_calibrate_NOT_LOO":True}

def fit_all_edges(training):
    if set(training)!=set(STATIONS):raise SourceStop("TRAIN_NOT_ALL_FIXED_THIRTEEN_SITES")
    return {target:{
        neigh:fit_lag_one_edge(training[target],training[neigh])
        for neigh in geometry_for_target(target)["idw3_sites"]}
        for target in STATIONS}

def evaluate_window(original,trained):
    if set(original)!=set(STATIONS) or set(trained)!=set(STATIONS):
        raise SourceStop("HELDOUT_OR_TRAIN_NOT_FROZEN_STATIONS")
    all_ticks=set.intersection(*(set(v.keys()) for v in original.values()))
    rows={}
    for target in STATIONS:
        g=geometry_for_target(target)
        others=g["idw3_sites"]
        weights=g["idw3_weights"]
        if set(trained[target])!=set(others):
            raise SourceStop("UNEXPECTED_TRAINED_EDGE_KEYS")
        lag={s:int(trained[target][s]["trained_2018_June_lag_min"]) for s in others}
        if any(l not in GRID_MIN for l in lag.values()):
            raise SourceStop("LAG_OUTSIDE_FROZEN_TRAIN_GRID")
        times=[t for t in sorted(all_ticks) if all(
             t-timedelta(minutes=lag[s]) in original[s] and
             t+timedelta(minutes=lag[s]) in original[s] for s in others)]
        if len(times)<MIN_PAIRS:
            raise SourceStop("INSUFFICIENT_IDENTICAL_HELDOUT_TARGET_TIMES_"+target)
        sse={"same_time_IDW3":0.0,"phase_IDW3":0.0,"reversed_phase_IDW3":0.0,
             "nearest_same_time":0.0}
        for t in times:
            y=original[target][t]
            baseline=sum(w*original[s][t] for s,w in zip(others,weights))
            phase=sum(w*original[s][t-timedelta(minutes=lag[s])]
                      for s,w in zip(others,weights))
            reversed_phase=sum(w*original[s][t+timedelta(minutes=lag[s])]
                               for s,w in zip(others,weights))
            nearest=original[g["nearest_name"]][t]
            for key,value in (("same_time_IDW3",baseline),("phase_IDW3",phase),
                ("reversed_phase_IDW3",reversed_phase),("nearest_same_time",nearest)):
                sse[key]+=(y-value)**2
        mse={k:round(v/len(times),9) for k,v in sse.items()}
        rows[target]={"n_exact_common_native_heldout_times_all_models":len(times),
                      "source_same_target_UTC_for_every_model":True,
                      "MSE_m2":mse,
                      "primary_same_time_minus_frozen_phase_MSE_gain_m2":
                        round(mse["same_time_IDW3"]-mse["phase_IDW3"],9),
                      "reverse_phase_control_same_time_minus_reverse_MSE_gain_m2":
                        round(mse["same_time_IDW3"]-mse["reversed_phase_IDW3"],9),
                      "trained_lags_minutes_from_2018_June_only":lag}
    values=[r["primary_same_time_minus_frozen_phase_MSE_gain_m2"] for r in rows.values()]
    med=median(values)
    means={k:round(mean(r["MSE_m2"][k] for r in rows.values()),9)
           for k in ("same_time_IDW3","phase_IDW3","reversed_phase_IDW3",
                     "nearest_same_time")}
    return {"n_frozen_gauge_targets":len(rows),
            "n_source_station_windows":len(rows),
            "equal_station_MSE_m2":means,
            "equal_station_mean_primary_phase_gain_m2":round(mean(values),9),
            "median_station_primary_phase_gain_m2":round(med,9),
            "n_targets_frozen_phase_better":sum(g>0 for g in values),
            "all_original_station_level_results":rows}

def run(out=OUT):
    result={"version":"v190_original_gauge_phase_fit_2018June_outyear_tests",
        "physical_source_only_exploratory_after_v188_site_heterogeneity":True,
        "TRAIN_2018_only_June":TRAIN,"never_fit_to_holds":HOLDS,
        "lag_search_grid_fixed_min":GRID_MIN,
        "gauge_target_used_to_train_2018_edge_phase_NOT_SPATIAL_LOOCV":True,
        "native_original_RWS_WATHTE_cmNAP_only":True,
        "original_gauge_2018_2019_instrument_location_not_fully_calibrated":True,
        "local_bird_GPS_h_s_t_DEM_water_depth_Boids_not_estimated":True,
        "status":"SOURCE_STOP"}
    try:
        cat,catsha=authentic_post(META_ROUTE,{"CatalogusFilter":{
          "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        native_codes=[x.get("Code") for x in cat.get("LocatieLijst") or []]
        if cat.get("Succesvol") is False or not all(
            native_codes.count(CODE[s])==1 for s in STATIONS):
            raise SourceStop("OFFICIAL_RWS_FROZEN_NATIVE_CATALOGUE_REJECTED")
        result["original_native_station_catalogue_SHA256"]=catsha
        training,train_sha=source_window(*TRAIN)
        fitted=fit_all_edges(training)
        result["fixed_2018_June_station_edge_lags"]=fitted
        result["original_2018_June_train_source_SHA"]=train_sha
        blocks={}
        for year,month in HOLDS:
            observed,receipts=source_window(year,month)
            score=evaluate_window(observed,fitted)
            blocks[f"{year}-{month:02d}"]={"original_RWS_source_SHA":receipts,
                                          "true_heldout_gauge_physics":score}
        result["heldout_blocks"]=blocks
        station_gain={}
        for site in STATIONS:
            vals=[block["true_heldout_gauge_physics"]["all_original_station_level_results"][site][
                "primary_same_time_minus_frozen_phase_MSE_gain_m2"] for block in blocks.values()]
            station_gain[site]={"n_positive_out_of_3":sum(v>0 for v in vals),
                                "mean_gain_m2":round(mean(vals),9),
                                "median_gain_m2":round(median(vals),9)}
        result["station_gain_analysis"]=station_gain
        allmean={k:round(mean(b["true_heldout_gauge_physics"]["equal_station_MSE_m2"][k]
                 for b in blocks.values()),9) for k in (
                 "same_time_IDW3","phase_IDW3","reversed_phase_IDW3","nearest_same_time")}
        result["physical_phase_transfer_summary"]={
            "n_heldout_2day_months":len(HOLDS),
            "n_station_month_holdouts":len(STATIONS)*len(HOLDS),
            "mean_3_window_equal_station_MSE_m2":allmean,
            "mean_gain_phase_over_same_IDW3_m2":
              round(allmean["same_time_IDW3"]-allmean["phase_IDW3"],9),
            "n_positive_windows":sum(
                b["true_heldout_gauge_physics"]["equal_station_mean_primary_phase_gain_m2"]>0
                for b in blocks.values()),
            "n_station_mean_phase_gain_positive":sum(
                s["mean_gain_m2"]>0 for s in station_gain.values()),
            "median_station_mean_phase_gain_m2":round(median(
                s["mean_gain_m2"] for s in station_gain.values()),9),
            "descriptive_support_2of3_and_positive_pooled":None,
            "not_station_out_of_site_or_bird_site_exposure":True}
        summ=result["physical_phase_transfer_summary"]
        summ["descriptive_support_2of3_and_positive_pooled"]=(summ["n_positive_windows"]>=2
            and summ["mean_gain_phase_over_same_IDW3_m2"]>0)
        result["status"]="REAL_13_GAUGE_PHASE_CALIBRATED_OUTMONTH_TRANSFER_SCORED_NOT_LOCAL_BIRD_TIDE"
    except (SourceStop,ValueError,TypeError,OSError,TimeoutError) as e:
        result["source_stop_reason"]=str(e)[:230]
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V190_REAL_RWS_PHASE_TRANSFER="+json.dumps({
      "status":result["status"],"source_stop_reason":result.get("source_stop_reason"),
      "summary":result.get("physical_phase_transfer_summary"),
      "windows":{k:{name:v["true_heldout_gauge_physics"][name] for name in (
             "equal_station_mean_primary_phase_gain_m2","median_station_primary_phase_gain_m2",
             "n_targets_frozen_phase_better")}
             for k,v in result.get("heldout_blocks",{}).items()},
      "site_mean_phase_gains":result.get("station_gain_analysis"),
      "2018_train_edge_lag_counts":dict(Counter(
          edge["trained_2018_June_lag_min"]
          for sub in result.get("fixed_2018_June_station_edge_lags",{}).values()
          for edge in sub.values())),
      "no_birds_or_local_exposure_analyzed":True
    },sort_keys=True),flush=True)
    return result

if __name__=="__main__":run()
