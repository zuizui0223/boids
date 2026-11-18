"""v188 original RWS Wadden13 source-only leave-one-gauge-out spatial interpolation.

Frozen station codes from v187 source admission, 2011 WEBTICS approximate RD coords.
NO calibrated local GPS-cell h(s,t), DEM datum, bird ACC, or individual positions.
"""
from __future__ import annotations
import json,math
from pathlib import Path
from rws_roompot_2020_source import publisher_post,DATA_ROUTE,META_ROUTE,NATIVE_META,SourceStop
from original_RWS_two_gauge_comparison import original_nap_series
from original_fifteen_wadden_gauge_inventory import ATLAS
from original_RWS_15_fixed_seaward_sites import CODE
import numpy as np
from scipy.spatial import Delaunay, QhullError

WINDOWS=((2018,6),(2018,9),(2019,6),(2019,9))
EXCLUDED_UNAVAILABLE=("DenOever","Nieuwstatenzijl")
STATIONS=tuple(s[0] for s in ATLAS if s[0] not in EXCLUDED_UNAVAILABLE)
REFERENCE_RD={s[0]:(float(s[1]),float(s[2])) for s in ATLAS}
MIN_GAUGE=200
MIN_COMMON=190
OUT=Path(__file__).resolve().parent/"results/genuine_Wadden13_2018_2019_spatial_LOO_v188.json"

def geometry_for_target(site):
    """Build geometric weights using reference locations, not target water data."""
    if site not in STATIONS:raise ValueError("UNKNOWN_OR_WITHHELD_SITE_NOT_IN_FROZEN_13")
    tx,ty=REFERENCE_RD[site]
    others=[s for s in STATIONS if s!=site]
    dist={s:math.hypot(REFERENCE_RD[s][0]-tx,REFERENCE_RD[s][1]-ty) for s in others}
    nearest=sorted(others,key=lambda s:(dist[s],s))
    if len(nearest)!=12 or min(dist.values())<=0:
        raise SourceStop("INVALID_OR_DUPLICATED_REFERENCE_STATION_GEOMETRY")
    three=nearest[:3]
    ww=[1/(dist[s]*dist[s]) for s in three];total=sum(ww)
    idw=[round(w/total,15) for w in ww]
    pts=np.asarray([REFERENCE_RD[s] for s in others],dtype=float)
    triangle=None
    try:
        tri=Delaunay(pts)
        simplex=int(tri.find_simplex(np.asarray([[tx,ty]],dtype=float))[0])
        if simplex>=0:
            ds=np.asarray([tx,ty])-tri.transform[simplex,2]
            first2=np.dot(tri.transform[simplex,:2],ds)
            ws=np.append(first2,1-first2.sum())
            if np.min(ws)>=-1e-8 and abs(ws.sum()-1)<1e-8:
                triangle=[(others[int(i)],float(w)) for i,w in zip(tri.simplices[simplex],ws)]
    except QhullError:
        triangle=None
    return {"nearest_name":nearest[0],"nearest_distance_RD_m":round(dist[nearest[0]],2),
            "idw3_sites":three,"idw3_weights":idw,
            "reference_geometry_triangle":triangle,
            "triangle_only_if_inside_remaining_12_station_hull":True}

def source_at_window(year,month):
    levels={};receipts={}
    for name in STATIONS:
        code=CODE[name]
        req={"Locatie":{"Code":code},
            "AquoPlusWaarnemingMetadata":{"AquoMetadata":NATIVE_META},
            "Periode":{"Begindatumtijd":f"{year}-{month:02d}-01T00:00:00.000+01:00",
                       "Einddatumtijd":f"{year}-{month:02d}-03T00:00:00.000+01:00"}}
        payload,sha=publisher_post(DATA_ROUTE,req)
        z,qa=original_nap_series(payload)
        if len(z)<MIN_GAUGE:raise SourceStop("NATIVE_STATION_FEWER_THAN_200_"+name)
        levels[name]=z
        receipts[name]={"native_RWS_code":code,"native_response_SHA256":sha,
                        "n_real_cmNAP_timestamps":len(z),"rejected_source_counts":qa}
    ticks=sorted(set.intersection(*(set(z) for z in levels.values())))
    if len(ticks)<MIN_COMMON:
        raise SourceStop(f"NATIVE_THIRTEEN_COMMON_UTC_TIMESTAMPS_LT190_{year}_{month}")
    return levels,ticks,receipts

def score_source_only(levels,times):
    if set(levels)!=set(STATIONS):raise SourceStop("NOT_THE_FROZEN_THIRTEEN_ORIGINAL_SITES")
    target_scores={}
    for target in STATIONS:
        g=geometry_for_target(target)
        actual=[levels[target][t] for t in times]
        nearest=[levels[g["nearest_name"]][t] for t in times]
        idw=[sum(w*levels[s][t] for s,w in zip(g["idw3_sites"],g["idw3_weights"]))
             for t in times]
        tri=None
        if g["reference_geometry_triangle"] is not None:
            tri=[sum(w*levels[s][t] for s,w in g["reference_geometry_triangle"])
                for t in times]
        def mse(pred):return sum((a-b)**2 for a,b in zip(actual,pred))/len(times)
        near=mse(nearest);i3=mse(idw)
        item={"mse_nearest_m2":round(near,9),
              "mse_IDW3_m2":round(i3,9),
              "nearest_minus_IDW3_MSE_gain_m2":round(near-i3,9),
              "mse_triangle_m2":round(mse(tri),9) if tri is not None else None,
              "webtics_2011_RD_geometry":g,
              "target_original_station_solely_scored_not_an_input":True}
        target_scores[target]=item
    gains=[x["nearest_minus_IDW3_MSE_gain_m2"] for x in target_scores.values()]
    tri_scores=[x for x in target_scores.values() if x["mse_triangle_m2"] is not None]
    return {"n_frozen_station_target_holdouts":len(target_scores),
        "n_common_original_UTC_timestamps":len(times),
        "n_reference_triangle_inside_hull_targets":len(tri_scores),
        "n_sites_positive_IDW3_vs_nearest":sum(v>0 for v in gains),
        "equal_station_mean_nearest_MSE_m2":round(sum(
            x["mse_nearest_m2"] for x in target_scores.values())/len(target_scores),9),
        "equal_station_mean_IDW3_MSE_m2":round(sum(
            x["mse_IDW3_m2"] for x in target_scores.values())/len(target_scores),9),
        "equal_station_mean_nearest_minus_IDW3_MSE_gain_m2":round(sum(gains)/len(gains),9),
        "equal_interior_triangle_MSE_m2":round(sum(
            x["mse_triangle_m2"] for x in tri_scores)/len(tri_scores),9) if tri_scores else None,
        "station_source_only_LOO":target_scores}

def run(out=OUT):
    result={"version":"v188-WEBTICS-reference-location-13-station-original-RWS-LOO",
        "predeclared_sites":STATIONS,"predeclared_windows":WINDOWS,
        "geography":"2011 WEBTICS source reference RD EPSG:28992; native 2018/19 precise location equivalence unverified",
        "original_provider_tide_type":"RWS DDAPI2 WATHTE cm NAP native clock +01",
        "v185_original_failed_5of15_source_gate_preserved":True,
        "v187_13of15_is_POST_failure_exploratory_site_name_repair":True,
        "no_bird_GPS_ACC_or_DEM_exposure_loaded":True,
        "status":"SOURCE_STOP"}
    try:
        if len(STATIONS)!=13 or set(STATIONS)!=set(CODE)-set(EXCLUDED_UNAVAILABLE):
            raise SourceStop("FROZEN_STATION_CODE_COHORT_BROKEN")
        # Original catalogue is requested to verify native source identities before any heights.
        cat,sha=publisher_post(META_ROUTE,{"CatalogusFilter":{
            "Grootheden":True,"Eenheden":True,"Compartimenten":True}})
        if cat.get("Succesvol") is False:raise SourceStop("ORIGINAL_CATALOGUE_FAILED")
        codes=[s.get("Code") for s in cat.get("LocatieLijst") or []]
        if not all(codes.count(CODE[site])==1 for site in STATIONS):
            raise SourceStop("FROZEN_NATIVE_RWS_CODES_NOT_UNIQUE_IN_ORIGINAL_CATALOGUE")
        result["original_station_catalog_SHA256"]=sha
        four={}
        for year,month in WINDOWS:
            levels,ticks,receipts=source_at_window(year,month)
            test=score_source_only(levels,ticks)
            four[f"{year}-{month:02d}"]={"original_RWS_SHA_receipts":receipts,
                                          "spatial_holdout_evaluation":test}
        result["true_original_heldout_windows"]=four
        means=[x["spatial_holdout_evaluation"]["equal_station_mean_nearest_minus_IDW3_MSE_gain_m2"]
               for x in four.values()]
        near=sum(x["spatial_holdout_evaluation"]["equal_station_mean_nearest_MSE_m2"]
                 for x in four.values())/len(four)
        i3=sum(x["spatial_holdout_evaluation"]["equal_station_mean_IDW3_MSE_m2"]
                 for x in four.values())/len(four)
        result["original_spatial_validation_summary"]={
            "n_windows":len(four),"n_original_station_year_month_targets":13*len(four),
            "n_positive_windows_IDW3":sum(x>0 for x in means),
            "station_window_equal_mean_nearest_MSE_m2":round(near,9),
            "station_window_equal_mean_IDW3_MSE_m2":round(i3,9),
            "station_window_equal_nearest_minus_IDW3_MSE_m2":round(near-i3,9),
            "descriptive_frozen_support_3of4_positive_and_pooled_positive":
              sum(x>0 for x in means)>=3 and near>i3,
            "no_spatial_model_fit_or_pvalue":True,
            "2011_reference_RD_not_native_gauge_instrument_coordinates":True,
            "local_GPS_h_s_t_and_exposure_not_source_admitted":True}
        result["status"]="REAL_WADDEN13_SPATIAL_STATION_LOO_SCORED_NOT_LOCAL_BIRD_TIDE"
    except (SourceStop,ValueError,TypeError,OSError,TimeoutError) as exc:
        result["source_stop_reason"]=str(exc)[:220]
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V188_SPATIAL_LOO_SCOPE="+json.dumps({
        "status":result["status"],"reason":result.get("source_stop_reason"),
        "summary":result.get("original_spatial_validation_summary"),
        "window_station_equal_gains":{k:v["spatial_holdout_evaluation"]["equal_station_mean_nearest_minus_IDW3_MSE_gain_m2"]
                                     for k,v in result.get("true_original_heldout_windows",{}).items()},
        "window_positive_station_counts":{k:v["spatial_holdout_evaluation"]["n_sites_positive_IDW3_vs_nearest"]
                                          for k,v in result.get("true_original_heldout_windows",{}).items()},
        "n_triangle_hull_stations":{k:v["spatial_holdout_evaluation"]["n_reference_triangle_inside_hull_targets"]
                                    for k,v in result.get("true_original_heldout_windows",{}).items()},
    },sort_keys=True),flush=True)
    return result

if __name__=="__main__":
    run()
