"""v41 explicitly post-v40 exploratory original fish speed×turn joint bins.

Source-only test strata determined by focal G14 present/past kinematics,
never future Y. Exact original v40 five marginal categories also retained.
No data-dependent bin boundary retuning; no new model feature tuning.
"""
from __future__ import annotations
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v32.moment_loo import file_moment
from validation_fish_school_v40.source_speed_turn_strata import (
    MODELS,CATEGORIES as MARGINAL_CATEGORIES,MIN_PER_BIN,
    pure_source_now_own_motion,stable_two_half_masks,
    source_trial_stratified_moments
)

JOINT_CATEGORIES=("SLOW_TLOW","SLOW_THIGH","SHIGH_TLOW","SHIGH_THIGH")
ALL_CATEGORIES=MARGINAL_CATEGORIES+JOINT_CATEGORIES

def original_joint_speed_turn_source_moments(source):
    old=source_trial_stratified_moments(source)
    g=source["X"]["G_geometry"]
    y=source["Y"]
    speed,turn,turn_valid=pure_source_now_own_motion(g)
    s_low,s_high=stable_two_half_masks(speed,np.ones(len(y),dtype=bool))
    t_low,t_high=stable_two_half_masks(turn,turn_valid)
    masks={
        "SLOW_TLOW":s_low&t_low,
        "SLOW_THIGH":s_low&t_high,
        "SHIGH_TLOW":s_high&t_low,
        "SHIGH_THIGH":s_high&t_high
    }
    seen=np.zeros(len(y),dtype=bool)
    for name,mask in masks.items():
        if int(mask.sum())<MIN_PER_BIN:
            raise SourceStop("V41_JOINT_SOURCE_SUPPORT_STOP_"+name)
        if np.any(seen&mask):
            raise SourceStop("V41_ORIGINAL_JOINT_SPEED_TURN_FISH_FRAME_OVERLAP")
        seen|=mask
    if not np.array_equal(seen,turn_valid):
        raise SourceStop("V41_JOINT_SPEED_TURN_NOT_PARTITION_OF_V40_VALID_TURNS")
    result={name:old["moments"][name] for name in MARGINAL_CATEGORIES}
    for name,mask in masks.items():
        result[name]={model:file_moment(source["X"][model][mask],y[mask])
                      for model in MODELS}
    for model in MODELS:
        for key in ("n","sx","sxx","sxy","sy","syy"):
            got=result["turn_low"][model][key]
            derived=(result["SLOW_TLOW"][model][key]+result["SHIGH_TLOW"][model][key])
            if key=="n":
                if got!=derived:
                    raise SourceStop("V41_SOURCE_TURNLOW_JOINT_PARTITION_COUNT_CHANGED")
            elif not np.allclose(got,derived,rtol=1e-9,atol=1e-3):
                raise SourceStop("V41_SOURCE_TURNLOW_JOINT_PARTITION_MOMENT_CHANGED_"+key)
            got=result["turn_high"][model][key]
            derived=(result["SLOW_THIGH"][model][key]+result["SHIGH_THIGH"][model][key])
            if key=="n":
                if got!=derived:
                    raise SourceStop("V41_SOURCE_TURNHIGH_JOINT_PARTITION_COUNT_CHANGED")
            elif not np.allclose(got,derived,rtol=1e-9,atol=1e-3):
                raise SourceStop("V41_SOURCE_TURNHIGH_JOINT_PARTITION_MOMENT_CHANGED_"+key)
    return {
       "stratum_sufficient_statistics":result,
       "source_original_focal_rows":len(y),
       "source_original_turning_undefined_rows":int((~turn_valid).sum()),
       "source_original_4_joint_categories_rows":{
         k:int(np.sum(m)) for k,m in masks.items()},
       "source_original_speed_and_turn_bins_unchanged_v40":True,
       "source_test_condition_assignment_never_uses_future_y":True,
       "original_XY_Y_or_individual_source_times_not_exported":True,
       "source_future_targets_identical_across_all_nine_categories":True,
       "source_collinear_speed_turning_4_conditions_are_NOT_randomized":True,
       "original_v40_marginal_category_counts":{
         k:int(old["moments"][k]["G_geometry"]["n"])
         for k in MARGINAL_CATEGORIES}
    }
