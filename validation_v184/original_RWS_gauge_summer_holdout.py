"""v184: frozen original 2018 June two-gauge calibration → untouched Jul–Sep 2018/2019.
Only measured official water height; never read bird GPS, ACC, DEM or local access.
"""
from __future__ import annotations
from datetime import datetime,timezone,timedelta
from pathlib import Path
from collections import Counter
import json,math
from rws_roompot_2020_source import publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop
from original_RWS_two_gauge_comparison import freeze_sites,original_nap_series

TRAIN=(2018,6)
HOLDOUT=((2018,7),(2018,8),(2018,9),(2019,7),(2019,8),(2019,9))
SHIFTS=(0,30,-30,90)
MIN_SHARED_ALL_SHIFT=200
OUT=Path(__file__).resolve().parent/"results/original_summer_heldout_two_gauge_transfer_v184.json"

def matched_rows(v: dict,w: dict):
    """Use exactly the same official West-station response instants in every model."""
    rows=[]
    for t in sorted(w):
        if all(t-timedelta(minutes=m) in v for m in SHIFTS):
            rows.append((t,tuple(v[t-timedelta(minutes=m)] for m in SHIFTS),w[t]))
    if len(rows)<MIN_SHARED_ALL_SHIFT:
        raise SourceStop("RWS_ORIGINAL_ALL_FOUR_LAG_SHARED_INSTANCES_LT200")
    return rows

def least_squares_xy(pairs: list[tuple[float,float]]):
    if len(pairs)<MIN_SHARED_ALL_SHIFT:raise SourceStop("TRAINING_TOO_FEW")
    ax=sum(x for x,y in pairs)/len(pairs)
    ay=sum(y for x,y in pairs)/len(pairs)
    denom=sum((x-ax)**2 for x,y in pairs)
    if denom<1e-6:raise SourceStop("NEAR_CONSTANT_ORIGINAL_RWS_HEIGHT")
    b=sum((x-ax)*(y-ay) for x,y in pairs)/denom
    a=ay-b*ax
    return a,b

def fit_models(rows):
    return {str(shift):least_squares_xy([(x[i],y) for _,x,y in rows])
            for i,shift in enumerate(SHIFTS)}

def evaluate_models(rows,coef):
    sse={str(s):0.0 for s in SHIFTS}
    for _,x,y in rows:
        for i,s in enumerate(SHIFTS):
            a,b=coef[str(s)]
            sse[str(s)]+=(y-a-b*x[i])**2
    n=len(rows)
    mse={str(s):round(sse[str(s)]/n,9) for s in SHIFTS}
    return {"native_same_target_timestamps":n,"MSE_m2":mse,
        "primary_gain_MSE_same_time_minus_frozen_30min":round(mse["0"]-mse["30"],9),
        "negative_control_minus_30_gain_MSE":round(mse["0"]-mse["-30"],9),
        "alternate_shift_90_gain_MSE":round(mse["0"]-mse["90"],9),
        "sse_unrounded":sse}

def original_pair_window(year,month,sites):
    a={}; receipts={}
    for site in sites:
        req={"Locatie":{"Code":site["code"]},
             "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
             "Periode":{"Begindatumtijd":f"{year}-{month:02d}-01T00:00:00.000+01:00",
                        "Einddatumtijd":f"{year}-{month:02d}-03T00:00:00.000+01:00"}}
        response,sha=publisher_post(DATA_ROUTE,req)
        data,rejections=original_nap_series(response)
        a[site["code"]]=data
        receipts[site["name"]]={"original_response_SHA256":sha,
            "n_true_WATHTE_cmNAP":len(data),"rejected_source_rows":rejections}
    return matched_rows(a[sites[0]["code"]],a[sites[1]["code"]]),receipts

def run(out=OUT):
    result={"analysis":"v184_frozen_original_RWS_two_station_outmonth_transfer",
        "training_original_2018_June_1_3":TRAIN,
        "never_seen_holdout_months":HOLDOUT,
        "fixed_lags_minutes":SHIFTS,
        "status":"SOURCE_STOP",
        "only_original_two_gauges_no_bird_or_habitat":True}
    try:
        c,catsha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        sites=freeze_sites(c)
        result["official_station_catalog_SHA256"]=catsha
        result["two_original_station_identities"]=sites
        tr,tsha=original_pair_window(*TRAIN,sites)
        coeff=fit_models(tr)
        result["2018_June_only_fitted_coefficients_by_lag"]=coeff
        result["2018_June_n_common_original_timestamps"]=len(tr)
        result["2018_June_original_source_receipts"]=tsha
        blocks={}
        pooled_sse={str(s):0 for s in SHIFTS};n_all=0
        for year,month in HOLDOUT:
            rows,source=original_pair_window(year,month,sites)
            ev=evaluate_models(rows,coeff)
            for s in SHIFTS:pooled_sse[str(s)]+=ev["sse_unrounded"][str(s)]
            n_all+=ev["native_same_target_timestamps"]
            del ev["sse_unrounded"]
            blocks[f"{year}-{month:02d}"]={"physical_predictive_test":ev,
                "official_RWS_publisher_hashes":source}
        result["unopened_six_holdout_windows"]=blocks
        n_pos=sum(v["physical_predictive_test"]["primary_gain_MSE_same_time_minus_frozen_30min"]>0
                  for v in blocks.values())
        pooled={s:round(x/n_all,9) for s,x in pooled_sse.items()}
        gain=round(pooled["0"]-pooled["30"],9)
        result["heldout_summary"]={
            "n_exact_heldout_targets_all_lags":n_all,
            "n_positive_heldout_windows_out_of_6":n_pos,
            "pooled_MSE_by_lag_m2":pooled,
            "pooled_MSE_gain_same_time_minus_30min":gain,
            "frozen_descriptive_support_4of6_AND_pooledpositive":n_pos>=4 and gain>0,
            "no_independent_six_block_pvalue_claim":True,
            "no_local_GPS_h_x_t_or_bird_ecology_identified":True}
        result["status"]="REAL_ORIGINAL_GAUGE_TRANSFER_HOLDOUT_SCORED_NOT_BIRD_MECHANISM"
    except (SourceStop,ValueError,TypeError,OSError,TimeoutError) as err:
        result["source_stop_reason"]=str(err)[:260]
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V184_HELDOUT_GAUGE_SCOPE="+json.dumps({
        "status":result["status"],
        "source_stop_reason":result.get("source_stop_reason"),
        "holdout_summary":result.get("heldout_summary"),
        "block_gains":{k:v["physical_predictive_test"]["primary_gain_MSE_same_time_minus_frozen_30min"]
                       for k,v in result.get("unopened_six_holdout_windows",{}).items()}
    },sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    run()
