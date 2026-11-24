"""v40 ORIGINAL stickleback within-recording speed and turning category moments.

Exact unchanged v33 source G14/global/nearest3/rotation model and future Y.
Each first/second half defined ONLY by at-or-before-t own kinematics.
NO novel original fish response/Y values exported.
"""
from __future__ import annotations
import numpy as np

from validation_fish_school_v30.harmonized_forecast import SourceStop
from validation_fish_school_v32.moment_loo import file_moment
from validation_fish_school_v33.neighbor_panels import original_panels

MODELS=("G_geometry","GLOBAL","NEAR_TRUE","NEAR_ROT1")
CATEGORIES=("ALL","speed_low","speed_high","turn_low","turn_high")
MIN_PER_BIN=1000
EPS_SPEED_PRODUCT=1e-10


def stable_two_half_masks(values,eligible):
    v=np.asarray(values,dtype=float)
    ok=np.asarray(eligible,dtype=bool)
    if v.ndim!=1 or ok.shape!=v.shape or np.any(~np.isfinite(v[ok])):
        raise SourceStop("V40_BAD_KINEMATIC_ONLY_SOURCE_PARTITION")
    good=np.flatnonzero(ok)
    if len(good)<2*MIN_PER_BIN:
        raise SourceStop("V40_SOURCE_FILE_TOO_FEW_ELIGIBLE_KINEMATIC_ROWS")
    order=good[np.argsort(v[good],kind="stable")]
    low=np.zeros(len(v),dtype=bool)
    high=np.zeros(len(v),dtype=bool)
    low[order[:len(order)//2]]=True
    high[order[len(order)//2:]]=True
    if int(np.sum(low))<MIN_PER_BIN or int(np.sum(high))<MIN_PER_BIN:
        raise SourceStop("V40_SOURCE_KINEMATIC_QUANTILE_CATEGORY_TOO_SMALL")
    if np.any(low&high) or not np.array_equal(low|high,ok):
        raise SourceStop("V40_NON_DISJOINT_OR_NONCOMPREHENSIVE_KINEMATIC_CATEGORY")
    return low,high


def pure_source_now_own_motion(G):
    g=np.asarray(G,dtype=float)
    if g.ndim!=2 or g.shape[1]!=14:
        raise SourceStop("V40_SOURCE_NOT_UNMODIFIED_V33_G14")
    cur=g[:,2:4]
    prev=g[:,4:6]
    own_speed=np.linalg.norm(cur,axis=1)
    if not np.allclose(own_speed,g[:,8],atol=1e-9,rtol=1e-11):
        raise SourceStop("V40_CURRENT_OWN_SPEED_NOT_FROZEN_G14_COL8")
    prev_speed=np.linalg.norm(prev,axis=1)
    defined=own_speed*prev_speed>EPS_SPEED_PRODUCT
    cross=prev[:,0]*cur[:,1]-prev[:,1]*cur[:,0]
    dot=np.sum(prev*cur,axis=1)
    turn=np.abs(np.arctan2(cross,dot))
    if np.any(~np.isfinite(turn)) or np.any(turn<0) or np.any(turn>np.pi+1e-10):
        raise SourceStop("V40_KINEMATIC_200MS_HEADING_CHANGE_OUTSIDE_VALID_RANGE")
    return own_speed,turn,defined


def source_trial_stratified_moments(src):
    if set(src["X"]) != {
         "G_geometry","GLOBAL","NEAR_TRUE","FAR_TRUE","NEAR_ROT1","NEAR_STALE_0.2S"}:
        raise SourceStop("V40_V33_SOURCE_ORIGINAL_SIX_COMMON_PANELS_CHANGED")
    g=src["X"]["G_geometry"]
    y=src["Y"]
    if y.ndim!=2 or y.shape[1]!=4 or len(y)!=len(g):
        raise SourceStop("V40_SOURCE_ORIGINAL_Y_HAS_CHANGED")
    own_speed,turn,turn_valid=pure_source_now_own_motion(g)
    speed_lo,speed_hi=stable_two_half_masks(own_speed,np.ones(len(y),dtype=bool))
    turn_lo,turn_hi=stable_two_half_masks(turn,turn_valid)
    category_mask={
      "ALL":np.ones(len(y),dtype=bool),
      "speed_low":speed_lo,
      "speed_high":speed_hi,
      "turn_low":turn_lo,
      "turn_high":turn_hi
    }
    stats={}
    for key,mask in category_mask.items():
        stats[key]={}
        for model in MODELS:
            stats[key][model]=file_moment(src["X"][model][mask],y[mask])
    for model in MODELS:
        whole=stats["ALL"][model]
        a,b=stats["speed_low"][model],stats["speed_high"][model]
        if whole["n"]!=a["n"]+b["n"]:
            raise SourceStop("V40_SPEED_LOW_HIGH_NOT_EXACT_ORIGINAL_PARTITION")
        for k in ("sx","sxx","sxy","sy","syy"):
            if not np.allclose(whole[k],a[k]+b[k],rtol=1e-9,atol=1e-3):
                raise SourceStop("V40_SPEED_HALF_MOMENT_NOT_EXACT_FULL_SOURCE_"+model+"_"+k)
        if not (stats["turn_low"][model]["n"]+stats["turn_high"][model]["n"]==
                np.sum(turn_valid)):
            raise SourceStop("V40_TURN_HALF_SUBSET_NOT_EXACT_OWN_PREV_VALID_FRAMES")
    if len(y)!=src["n_original_test_fish_frame_rows"]:
        raise SourceStop("V40_ORIGINAL_SOURCE_FOCAL_FRAME_COUNT_CHANGED")
    return {
      "moments":stats,
      "n_original_focal_fish_frame_rows":len(y),
      "n_original_turn_well_defined_rows":int(np.sum(turn_valid)),
      "n_original_turn_undefined_speed_product_rows":int(np.sum(~turn_valid)),
      "n_speed_low_fish_frame_rows":int(speed_lo.sum()),
      "n_speed_high_fish_frame_rows":int(speed_hi.sum()),
      "n_turn_low_fish_frame_rows":int(turn_lo.sum()),
      "n_turn_high_fish_frame_rows":int(turn_hi.sum()),
      "mean_current_focal_speed_source_units_per_s":float(np.mean(own_speed)),
      "source_focal_speed_median":float(np.median(own_speed)),
      "median_defined_angular_change_rad_over_200ms":float(np.median(turn[turn_valid])),
      "original_kinematic_stratum_assignments_NOT_exported":True,
      "original_focal_velocity_future_Y_or_XY_NOT_exported":True,
      "stratification_source_only_v33_G14_present_prev_velocity":True
    }
