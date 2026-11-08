"""v70: fixed 2010-trained wild 2011 next-heading forecast, tide-light coexistence.

M0 controls raw tide level/phase, own past speed/bearing, full solar main
effects, *total* past 12h low-water hours and sunlit hours. New M1 contains
only their REAL source-measured coexistence. Mghost is a lagged-source check.
This is not measured prey/mudflat exposure or a field social Boids test.
"""
from __future__ import annotations

from collections import Counter,defaultdict
import numpy as np

from original_heading_tide import vector
from tide_daylight_interaction import _equal_bird_comparison,_boot
from physical_low_tide_sun_overlap import source_only_GPS_window_gate

SEED_BIRD=20261108
SEED_MONTH=20261109
MODELS=("M0","M1","M2","Mghost")

def features(r,model):
    if model not in MODELS:
        raise ValueError("SOURCE_STOP_V70_UNREGISTERED_MODEL")
    x=list(vector(r,1))
    if len(x)!=14:
        raise ValueError("SOURCE_STOP_V70_ORIGINAL_TIDE_VECTOR_CHANGED")
    x.extend([r["solar"],r["daylen"],r["low12"]/6.,r["sun12"]/6.])
    if model in ("M1","M2"):
        x.append(r["joint12"]/6.)
    if model=="Mghost":
        x.append(r["ghostjoint12"]/6.)
    if model=="M2":
        x.append(r["phase"]*r["joint12"]/6.)
    return x

def forecast(train,test,model):
    if not train or not test:raise ValueError("SOURCE_STOP_V70_NO_GPS_MODEL_DATA")
    xx=np.asarray([features(row,model) for row in train],dtype=float)
    zz=np.asarray([features(row,model) for row in test],dtype=float)
    yy=np.asarray([[r["target_e"],r["target_n"]] for r in train],dtype=float)
    if (not np.isfinite(xx).all() or not np.isfinite(zz).all()
        or not np.isfinite(yy).all() or yy.shape!=(len(train),2)):
        raise ValueError("ESTIMAND_STOP_V70_NONFINITE_SOURCE_MODEL_OR_TARGET")
    avg=xx[:,1:].mean(axis=0)
    std=xx[:,1:].std(axis=0)
    std[std<1e-9]=1
    xx[:,1:]=(xx[:,1:]-avg)/std
    zz[:,1:]=(zz[:,1:]-avg)/std
    n=Counter(r["id"] for r in train)
    weights=np.asarray([1/n[r["id"]] for r in train],dtype=float)
    weights*=len(train)/weights.sum()
    ridge=np.eye(xx.shape[1])*10
    ridge[0,0]=0
    coef=np.linalg.solve(xx.T@(xx*weights[:,None])+ridge,
                         xx.T@(weights[:,None]*yy))
    out=zz@coef
    if out.shape!=(len(test),2) or not np.isfinite(out).all():
        raise ValueError("ESTIMAND_STOP_V70_REAL_DIRECTION_MODEL_OUTPUT")
    return out

def score_field_opportunity(train,test,*,strict=True):
    before=source_only_GPS_window_gate(train,test,strict=strict)
    obs=np.asarray([[r["target_e"],r["target_n"]] for r in test],dtype=float)
    if obs.shape!=(len(test),2) or not np.isfinite(obs).all():
        raise ValueError("ESTIMAND_STOP_V70_SOURCE_FUTURE_UNIT_HEADING")
    errors={}
    for name in MODELS:
        p=forecast(train,test,name)
        errors[name]=.5*np.square(obs-p).sum(axis=1)
    v={
        "primary_M1_minus_M0_12h_overlap_beyond_marginal_hours":_equal_bird_comparison(
            test,errors["M0"],errors["M1"],seed=SEED_BIRD),
        "secondary_M2_minus_M0_phase_x_opportunity":_equal_bird_comparison(
            test,errors["M0"],errors["M2"],seed=SEED_BIRD+1),
        "secondary_M2_minus_M1_phase_increment":_equal_bird_comparison(
            test,errors["M1"],errors["M2"],seed=SEED_BIRD+2),
        "negative_control_M1_minus_Mghost_actual_vs_6h_earlier_window":_equal_bird_comparison(
            test,errors["Mghost"],errors["M1"],seed=SEED_BIRD+3)}
    monthly=defaultdict(lambda:defaultdict(list))
    for idx,row in enumerate(test):
        monthly[(row["t"].year,row["t"].month)][row["id"]].append(idx)
    gain=errors["M0"]-errors["M1"]
    groups=[float(np.mean([float(np.mean(gain[idx]))
                            for idx in birds.values()]))
            for month,birds in sorted(monthly.items())]
    time={
        "observed_calendar_months":len(groups),
        "month_equal_bird_then_month_gain":float(np.mean(groups)),
        "month_block_bootstrap_95_DESCRIPTIVE":_boot(groups,4000,SEED_MONTH)}
    main=v["primary_M1_minus_M0_12h_overlap_beyond_marginal_hours"]
    good=(main["bird_equal_gain_half_MSE"]>0 and
          main["whole_bird_cluster_bootstrap_95"][0]>0)
    return {
        "analysis":"V70_WADDEN_OBSERVED_LOW_TIDE_SUN_OVERLAP_ADDED_HEADING_PREDICTION",
        "frozen_original_source_support_before_model_fit":before,
        "original_field_nested_model_definition":{
            "M0":"v41 true tide + v69 solar main effects + last12h separately low-water and sunlit totals",
            "M1":"M0 plus last12h measured joint low-water AND sunlight hours",
            "M2":"M1 plus current real tide phase x joint low-water-sun hours",
            "Mghost":"M0 plus joint low-water-sun measured six hours earlier (past 18h to 6h)"},
        "2010_disjoint_training_and_2011_original_bird_equal_heldout":v,
        "same_original_calendar_month_field_sensitivity":time,
        "frozen_primary_source_and_bird_interval_decision":
          ("POSITIVE_GAUGE_LOW_WATER_SUN_OVERLAP_EXPLORATORY_DIRECTION_GAIN"
           if good else
           "JOINT_LOW_WATER_DAYLIGHT_ADDED_DIRECTION_GAIN_NOT_ESTABLISHED"),
        "original_available_physical_gauge_not_real_exposed_prey_patch":True,
        "no_future_gauge_or_2011_heading_entered_training_features":True,
        "post_v69_exploratory_same_species_region":True,
        "no_social_reynolds_or_causal_illumination_claim":True}
