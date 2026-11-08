"""v69 actual tidal-phase × solar-daylength heldout next-heading model.

No raw wild bird IDs, B positions, source dates, true next directions, official
RWS gauge timeseries, or learned source coefficients are serialized.
Post-v63 exploratory; primary precommitted M2−M0 2010-unseen-bird -> 2011.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from functools import lru_cache
import math

import numpy as np
from astral import Observer
from astral.sun import elevation,sunrise,sunset
from original_heading_tide import vector as original_tide_vector,forecast as original_tide_forecast

PREDECLARED_SCOPED_SEED=20261108
MONTH_SEED=20261109
BOOT_BIRDS=10000
BOOT_MONTHS=4000
REQUIRED_TRAIN=1508
REQUIRED_TEST=4948
REQUIRED_BIRDS_TRAIN=8
REQUIRED_BIRDS_TEST=13
ALLOWED_MODELS=("M0","M1","M2","Mghost")

def solar_features(row):
    """Solar geometry with exact B UTC timestamp and GPS coordinates.

    Astral is used on *source inputs*, never on B->C observed outcome.
    Not local light sensor, lunar phase or actual food-resource exposure.
    """
    t=row["t"]
    if not isinstance(t,datetime) or t.tzinfo is None:
        raise ValueError("SOURCE_STOP_V69_GPS_TIME_NOT_AWARE")
    if not (-90<=row["lat"]<=90 and -180<=row["lon"]<=180):
        raise ValueError("SOURCE_STOP_V69_B_LAT_LONG_OUT_OF_RANGE")
    observer=Observer(latitude=float(row["lat"]),longitude=float(row["lon"]),
                      elevation=0.0)
    elev=float(elevation(observer,t,with_refraction=True))
    rise=sunrise(observer,date=t.date(),tzinfo=timezone.utc)
    set_=sunset(observer,date=t.date(),tzinfo=timezone.utc)
    if not 0<(set_-rise).total_seconds()<24*3600:
        raise ValueError("SOURCE_STOP_V69_SOLAR_DAYLENGTH_INVALID")
    length=(set_-rise).total_seconds()/3600
    # Only the ghost interaction is time-shifted; original source GPS is not.
    ghost=float(elevation(observer,t+timedelta(hours=6),with_refraction=True))
    return {"solar":elev/45.,"daylen":(length-12)/4.,
            "ghost_solar":ghost/45.,
            "sunlit":elev>0,
            "twilight":abs(elev)<=3,
            "day_length_hours":length}

def augment(rows):
    return [{**row,**solar_features(row)} for row in rows]

def source_gate(train,test,*,strict=True):
    if strict and ((len(train),len(test),
                    len({r["id"] for r in train}),
                    len({r["id"] for r in test})) !=
                   (REQUIRED_TRAIN,REQUIRED_TEST,
                    REQUIRED_BIRDS_TRAIN,REQUIRED_BIRDS_TEST)):
        raise ValueError("SOURCE_STOP_V69_UNSEEN_BIRD_YEAR_COUNTS_DRIFT")
    if {r["id"] for r in train}&{r["id"] for r in test}:
        raise ValueError("SOURCE_STOP_V69_TRAIN_TEST_SHARED_BIRD")
    counts={}
    for label,rows,min_n in (("train",train,120),("test",test,240)):
        bybird=defaultdict(Counter)
        sun=Counter()
        for r in rows:
            kind="day" if r["sunlit"] else "night"
            sun[kind]+=1
            bybird[r["id"]][kind]+=1
        n_birds_both=sum(v["day"]>=10 and v["night"]>=10 for v in bybird.values())
        counts[label]={
            "observed_original_GPS_triplets":len(rows),
            "original_source_birds":len(bybird),
            "sun_above_horizon_source_triplets":sun["day"],
            "sun_below_horizon_source_triplets":sun["night"],
            "original_birds_with_ten_both_light_classes":n_birds_both,
            "astronomical_twilight_3deg_source_triplets":sum(r["twilight"] for r in rows),
            "astronomical_daylength_min_h":float(min(r["day_length_hours"] for r in rows)),
            "astronomical_daylength_max_h":float(max(r["day_length_hours"] for r in rows))
        }
        if sun["day"]<min_n or sun["night"]<min_n or n_birds_both<3:
            raise ValueError("SOURCE_NOT_ADMITTED_V69_LIGHT_TIDE_INTERACTION_"+label)
    months=len({(r["t"].year,r["t"].month) for r in test})
    if months<8:
        raise ValueError("SOURCE_NOT_ADMITTED_V69_2011_MONTHS_LT8")
    counts["test"]["original_calendar_months_with_source"]=months
    return counts

def feature_vector(row,model):
    if model not in ALLOWED_MODELS:
        raise ValueError("SOURCE_STOP_V69_UNFROZEN_NESTED_MODEL")
    original=list(original_tide_vector(row,1))
    if len(original)!=14:
        raise ValueError("SOURCE_STOP_V69_V41_FEATURES_CHANGED")
    original.extend([row["solar"],row["daylen"]])
    if model=="M0":return original
    original.append(row["phase"] * (row["ghost_solar"] if model=="Mghost" else row["solar"]))
    if model in ("M2","Mghost"):
        original.append(row["phase"]*row["daylen"])
    return original

def predict(train,test,model):
    if not train or not test:raise ValueError("SOURCE_STOP_V69_NO_ORIGINAL_GPS")
    if model not in ALLOWED_MODELS:raise ValueError("SOURCE_STOP_V69_UNKNOWN_MODEL")
    x=np.asarray([feature_vector(r,model) for r in train],dtype=float)
    z=np.asarray([feature_vector(r,model) for r in test],dtype=float)
    y=np.asarray([[r["target_e"],r["target_n"]] for r in train],dtype=float)
    # Exactly same numerical scaling and source-bird weighting ridge lambda
    # as the existing original v41 forecast; only model feature columns change.
    avg=x[:,1:].mean(axis=0);sd=x[:,1:].std(axis=0)
    sd[sd<1e-9]=1
    x[:,1:]=(x[:,1:]-avg)/sd
    z[:,1:]=(z[:,1:]-avg)/sd
    n=Counter(r["id"] for r in train)
    weight=np.asarray([1/n[r["id"]] for r in train],dtype=float)
    weight*=len(train)/weight.sum()
    reg=np.eye(x.shape[1])*10.
    reg[0,0]=0.
    coef=np.linalg.solve(x.T@(x*weight[:,None])+reg,
                         x.T@(weight[:,None]*y))
    out=z@coef
    if out.shape!=(len(test),2) or not np.isfinite(out).all():
        raise ValueError("ESTIMAND_STOP_V69_INVALID_PREDICTION")
    return out

def _boot(v,n,seed):
    a=np.asarray(v,float)
    if a.ndim!=1 or not np.isfinite(a).all() or not len(a):
        raise ValueError("ESTIMAND_STOP_V69_BAD_BIRD_CLUSTER")
    gen=np.random.default_rng(seed)
    draws=gen.integers(0,len(a),size=(n,len(a)))
    means=a[draws].mean(axis=1)
    return [float(k) for k in np.quantile(means,[.025,.975])]

def _equal_bird_comparison(test,loss_baseline,loss_new,*,seed):
    by=defaultdict(list)
    for i,r in enumerate(test):
        by[r["id"]].append(i)
    bird_gains=[float(np.mean((loss_baseline-loss_new)[idx])) for b,idx
                in sorted(by.items())]
    err0=float(np.mean([np.mean(loss_baseline[idx]) for idx in by.values()]))
    err1=float(np.mean([np.mean(loss_new[idx]) for idx in by.values()]))
    delta=float(np.mean(bird_gains))
    return {
        "original_birds":len(by),
        "original_test_episodes":len(test),
        "bird_equal_gain_half_MSE":delta,
        "percent_half_MSE_reduction_vs_baseline":100*delta/err0 if err0>0 else None,
        "bird_equal_baseline_half_MSE":err0,
        "bird_equal_extended_half_MSE":err1,
        "whole_bird_cluster_bootstrap_95":_boot(bird_gains,BOOT_BIRDS,seed),
        "original_birds_positive":sum(x>0 for x in bird_gains),
        "no_per_bird_scores_serialized":True}

def score_two_clocks(train,test,*,strict=True):
    qa=source_gate(train,test,strict=strict)
    obs=np.asarray([[r["target_e"],r["target_n"]] for r in test],dtype=float)
    if not np.isfinite(obs).all() or obs.shape!=(len(test),2):
        raise ValueError("ESTIMAND_STOP_V69_OBSERVED_HEADING_BAD_SHAPE")
    losses={}
    for m in ALLOWED_MODELS:
        estimate=predict(train,test,m)
        losses[m]=.5*np.square(obs-estimate).sum(axis=1)
    contrasts={
        "primary_M2_vs_M0_phase_by_solar_elevation_and_daylength":_equal_bird_comparison(
            test,losses["M0"],losses["M2"],seed=PREDECLARED_SCOPED_SEED),
        "secondary_M1_vs_M0_phase_by_solar_elevation":_equal_bird_comparison(
            test,losses["M0"],losses["M1"],seed=PREDECLARED_SCOPED_SEED+1),
        "secondary_M2_vs_M1_extra_phase_by_daylength":_equal_bird_comparison(
            test,losses["M1"],losses["M2"],seed=PREDECLARED_SCOPED_SEED+2),
        "misaligned_sun_6hour_ghost_M2_vs_Mghost":_equal_bird_comparison(
            test,losses["Mghost"],losses["M2"],seed=PREDECLARED_SCOPED_SEED+3)}
    # In each calendar month, equally weight original birds with any source
    # data in that month and then month clusters. Temporal dependence within
    # and between months is not presumed absent.
    bymonth=defaultdict(lambda:defaultdict(list))
    for idx,r in enumerate(test):
        bymonth[(r["t"].year,r["t"].month)][r["id"]].append(idx)
    month_deltas=[]
    gain=losses["M0"]-losses["M2"]
    for yearmonth,birds in sorted(bymonth.items()):
        month_deltas.append(float(np.mean([
            np.mean(gain[idx]) for idx in birds.values()])))
    months_out={
        "source_calendar_months":len(month_deltas),
        "equal_month_then_bird_mean_gain":float(np.mean(month_deltas)),
        "calendar_month_bootstrap_95_DESCRIPTIVE":_boot(month_deltas,BOOT_MONTHS,MONTH_SEED)}
    # Prespecified long/short photoperiod observed source split, not model
    # selection; all outcome signs will be reported.
    daylength_splits={}
    for label,selector in (
        ("long_day_ge12h",lambda r:r["day_length_hours"]>=12),
        ("short_day_lt12h",lambda r:r["day_length_hours"]<12),
        ("light_sun_above_horizon",lambda r:r["sunlit"]),
        ("dark_sun_below_horizon",lambda r:not r["sunlit"])):
        idx=[i for i,r in enumerate(test) if selector(r)]
        src=[test[i] for i in idx]
        birds=len({r["id"] for r in src})
        if len(idx)<100 or birds<3:
            daylength_splits[label]={"status":"INSUFFICIENT_FIXED_SOURCE",
                "original_episodes":len(idx),"original_birds":birds}
            continue
        src0=losses["M0"][idx];src2=losses["M2"][idx]
        q=_equal_bird_comparison(src,src0,src2,
                                 seed=PREDECLARED_SCOPED_SEED+10+len(daylength_splits))
        daylength_splits[label]={"status":"DESCRIPTIVE_SOURCE_SUPPORTED",**q}
    primary=contrasts["primary_M2_vs_M0_phase_by_solar_elevation_and_daylength"]
    status=("EXPLORATORY_POSITIVE_TIDE_X_SOLAR_HELDOUT_GAIN"
            if primary["bird_equal_gain_half_MSE"]>0 and
               primary["whole_bird_cluster_bootstrap_95"][0]>0
            else "DAYLIGHT_TIDE_INTERACTION_INCREMENTAL_FORECAST_NOT_ESTABLISHED")
    return {
        "analysis":"V69_ORIGINAL_2010_2011_SCHIER_WILD_TIDE_X_DAYLIGHT_NESTED_HEADING",
        "frozen_source_only_solar_illumination_qa":qa,
        "source_models":{"M0":"v41 tide+sun/daylength mains",
                         "M1":"M0+phase×solar elevation",
                         "M2":"M1+phase×daylength",
                         "Mghost":"M0+phase×solar+6h misalignment and true phase×daylength"},
        "original_2011_equal_bird_heldout_next_heading_2D_half_MSE":contrasts,
        "primary_month_cluster_descriptive_sensitivity":months_out,
        "frozen_solar_and_photoperiod_strata":daylength_splits,
        "primary_status":status,
        "not_new_cross_species_or_unseen_coast_validation":True,
        "not_causal_tide_or_photoperiod_solar_effect":True,
        "no_social_Reynolds_force_or_live_illumination_sensor":True,
        "not_2011_2012_future_test_or_new_GPS":True}
