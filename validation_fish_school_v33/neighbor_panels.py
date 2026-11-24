"""v33 source-locked near/far/one-rotation neighbor-identity prediction panels.

Published original 2021 EIDC eight-fish XY, 25 fps, 84 trials / 12 shoals.
Exactly reuse v30 G14/global and shared outcome. No local velocity signal
may be described as a causal social force or observed fish sound.
"""
from __future__ import annotations
import numpy as np
from validation_fish_school_v30.harmonized_forecast import (
    build_original_recording,SourceStop,FEAT_DIM
)

PANELS=(
    "G_geometry","GLOBAL","NEAR_TRUE","FAR_TRUE",
    "NEAR_ROT1","NEAR_STALE_0.2S"
)
FPS=25
DT=.2
N_FISH=8
FROZEN_AGES=(0.,.2,.4,1.,2.)

def frozen_original_source_clock_and_cohort(frame,pos):
    f=np.asarray(frame,dtype=float)
    p=np.asarray(pos,dtype=float)
    if p.ndim!=3 or p.shape[1:]!=(8,2) or len(f)!=len(p) or len(p)<4000:
        raise SourceStop("V33_ORIGINAL_8_FISH_NATIVE_TIME_SHAPE_STOP")
    if not np.isfinite(f).all() or not np.array_equal(np.diff(f),np.ones(len(f)-1)):
        raise SourceStop("V33_ORIGINAL_FRAME_ONE_STEP_SOURCE_STOP")
    s=5
    offsets=np.array([-11*s,-10*s,-6*s,-5*s,-3*s,-2*s,-s,0,s,3*s,4*s],dtype=int)
    current=np.arange(11*s,len(p)-4*s,s,dtype=int)
    picked=current[:,None]+offsets[None,:]
    valid=np.isfinite(p[picked]).all(axis=(1,2,3))
    valid&=((f[picked]-f[current,None])==offsets[None,:]).all(axis=1)
    out=current[valid]
    if len(out)<300:
        raise SourceStop("V33_ORIGINAL_COMPLETE_SOURCE_COHORT_TOO_FEW")
    return out


def original_panels(frame,pos,source_name="SOURCE"):
    base=build_original_recording(frame,pos,FPS,source_name)
    idx=frozen_original_source_clock_and_cohort(frame,pos)
    if len(idx)!=base["n_original_eligible_group_times"]:
        raise SourceStop("V33_V30_FROZEN_ORIGINAL_COHORT_REPLAY_FAILED")
    p=np.asarray(pos,dtype=float)
    now=p[idx]
    vel=(p[idx]-p[idx-5])/DT
    stale=(p[idx-5]-p[idx-10])/DT
    d2=np.sum((now[:,None,:,:]-now[:,:,None,:])**2,axis=-1)
    d2[:,np.arange(N_FISH),np.arange(N_FISH)]=np.inf
    ranking=np.argsort(d2,axis=2)[:,:,:7]
    near=ranking[:,:,:3]
    far=ranking[:,:,-3:]
    focal=np.arange(N_FISH)
    if (np.any(near==focal[None,:,None]) or
        np.any(far==focal[None,:,None]) or
        not np.all(np.take_along_axis(d2,near,axis=2)[:,:,-1] <=
                   np.take_along_axis(d2,far,axis=2)[:,:,0])):
        raise SourceStop("V33_ORIGINAL_NEAR_FAR_POSITION_MAP_STOP")
    allothers=(vel.sum(axis=1,keepdims=True)-vel)/7
    global_rel=allothers-vel
    curr_near=vel[np.arange(len(idx))[:,None,None],near].mean(axis=2)-allothers
    curr_far=vel[np.arange(len(idx))[:,None,None],far].mean(axis=2)-allothers
    oldall=(stale.sum(axis=1,keepdims=True)-stale)/7
    stale_near=stale[np.arange(len(idx))[:,None,None],near].mean(axis=2)-oldall
    assigned=np.zeros_like(curr_near)
    for focus in range(N_FISH):
        rest=np.array([j for j in range(N_FISH) if j!=focus],dtype=int)
        old_source_values=vel[:,rest,:]
        surrogate=np.roll(old_source_values,1,axis=1)
        if not np.allclose(surrogate.sum(axis=1),old_source_values.sum(axis=1),atol=1e-9,rtol=0):
            raise SourceStop("V33_ROT1_ORIGINAL_GLOBAL_VELOCITY_NOT_PRESERVED")
        ranks=near[:,focus,:]-(near[:,focus,:]>focus).astype(int)
        assignment=np.take_along_axis(surrogate,ranks[:,:,None],axis=1)
        assigned[:,focus,:]=assignment.mean(axis=1)-allothers[:,focus,:]
    G=base["X"]["G_geometry"]
    globe=base["X"]["age_0s"]
    if G.shape!=(len(idx)*N_FISH,FEAT_DIM) or globe.shape!=(len(idx)*N_FISH,FEAT_DIM+2):
        raise SourceStop("V33_V30_ORIGINAL_FOCAL_SOURCE_MATRIX_SHAPE_STOP")
    if not np.array_equal(globe[:,:FEAT_DIM],G) or not np.allclose(
            globe[:,FEAT_DIM:],global_rel.reshape(-1,2),atol=1e-10,rtol=0):
        raise SourceStop("V33_V30_GLOBAL_ALL_OTHERS_VELOCITY_REPLAY_STOP")
    out={
        "G_geometry":G,
        "GLOBAL":globe,
        "NEAR_TRUE":np.concatenate((globe,curr_near.reshape(-1,2)),axis=1),
        "FAR_TRUE":np.concatenate((globe,curr_far.reshape(-1,2)),axis=1),
        "NEAR_ROT1":np.concatenate((globe,assigned.reshape(-1,2)),axis=1),
        "NEAR_STALE_0.2S":np.concatenate((globe,stale_near.reshape(-1,2)),axis=1)
    }
    if tuple(out)!=PANELS or any(not np.isfinite(z).all() for z in out.values()):
        raise SourceStop("V33_ORIGINAL_NEAR_FAR_SURROGATE_NONFINITE")
    if any(not np.array_equal(out[x][:,:16],globe) for x in PANELS[2:]):
        raise SourceStop("V33_LOCAL_PANELS_CHANGED_FROZEN_CURRENT_GLOBAL_OR_GEOMETRY")
    if any(out[x].shape!=(len(base["Y"]),18) for x in PANELS[2:]):
        raise SourceStop("V33_NON_MATCHED_TWO_VECTOR_EXTRA_FEATURES_STOP")
    return {
        "X":out,"Y":base["Y"],
        "n_source_rows":base["n_source_rows"],
        "n_original_eligible_group_times":base["n_original_eligible_group_times"],
        "n_original_test_fish_frame_rows":base["n_original_eligible_fish_frames"],
        "n_discarded_original_source_group_times":base["n_original_rows_excluded_nonfinite_or_noncontiguous"],
        "same_source_frozen_Y_and_G14_and_GLOBAL":True,
        "source_velocity_to_position_original_or_rotated":"CURRENT_NEAREST_NEIGHBOR_IDS_WITH_FIXED_ONE_STEP_ROTATION",
        "source_native_fps":FPS,
        "source_original_animal_XY_exported":False
    }
