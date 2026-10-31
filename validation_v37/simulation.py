#!/usr/bin/env python3
"""v37 -- synthetic 3D Boids motor and tide-gated motion-state sufficiency.

NO ORIGINAL ANIMAL OBSERVATIONS OR RWS TIDE. All output is synthetic;
observed v33/v34 sign motifs motivated this constructed model. Every ablation,
including failure, is retained without an empirical p-value.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np

PROTOCOL="docs/V37_SYNTHETIC_TIDE_GATED_3D_BOIDS_PROTOCOL.md"
STATE_NAMES=("ROOST","OUTBOUND","FORAGE","INBOUND")
MODELS=(
    "A0_NO_TIDE_NO_SOCIAL",
    "A1_HEIGHT_ONLY_NO_SOCIAL",
    "A2_PHASE_ONLY_NO_SOCIAL",
    "A3_HYSTERESIS_NO_COMMUTE_NO_SOCIAL",
    "A4_TIDE_STATE_GATE_NO_SOCIAL",
    "A5_TIDE_STATE_GATE_WITH_3D_BOIDS",
)
SEEDS=tuple(range(24))
AGENTS=30
DAYS=24
WARMUP_HOURS=48.
DT_HOURS=1/6
PERIOD_HOURS=12.4206
SPRING_NEAP_PERIOD_HOURS=14.77*24.
ELEVATION_MIN=-1.15
ELEVATION_MAX=1.25
ENTRY_WATER_H=.35
EXIT_WATER_H=.85
ENTER_EXPOSED_FRAC=(ELEVATION_MAX-ENTRY_WATER_H)/(ELEVATION_MAX-ELEVATION_MIN)
EXIT_EXPOSED_FRAC=(ELEVATION_MAX-EXIT_WATER_H)/(ELEVATION_MAX-ELEVATION_MIN)
COMMUTE_HOURS=.65
SPEEDS=np.array([.09,4.,1.1,4.],dtype=float)
FIXED_SPEED=.60
HEIGHT_ONLY_BASE=.09
HEIGHT_ONLY_GAIN=1.10
PHASE_ONLY_BASE=.40
PHASE_ONLY_EBB_BONUS=.70
LOG_SPEED_NOISE=.03
HEADING_NOISE=.04
NEIGHBOR_RADIUS_KM=.60
SEPARATION_RADIUS_KM=.12
ALIGNMENT=.14
COHESION=.08
SEPARATION=.20
WORLD_BOX_KM=np.array([3.,3.,.30],dtype=float)
TIDE_HEIGHT_BIN_M=.50
MOTIF_LOW_HIGH_BOUNDARY_M=.50
EXTREME_LOW_WATER_M=-.75
EXTREME_HIGH_WATER_M=.75
MOTIF_KEYS=("high_minus_low","low_ebb_minus_flood","high_ebb_minus_flood")
LABELS={"H(t)":"sinusoidal original synthetic tide; never original RWS WATHTE"}
INITIAL_STATE=0  # ROOST
NO_BIOLOGICAL_DATA=True

def tide_height_slope(t_hours):
    a=2*np.pi/PERIOD_HOURS
    b=2*np.pi/SPRING_NEAP_PERIOD_HOURS
    h=1.2*np.sin(a*t_hours)+.09*np.sin(b*t_hours)
    slope=1.2*a*np.cos(a*t_hours)+.09*b*np.cos(b*t_hours)
    return h,slope

def available_fraction(height):
    """Fraction of a manufactured uniform bed shelf exposed above toy height."""
    return np.clip((ELEVATION_MAX-np.asarray(height,dtype=float))/
                   (ELEVATION_MAX-ELEVATION_MIN),0.,1.)

def normalize3(vec):
    norms=np.linalg.norm(vec,axis=-1,keepdims=True)
    return vec/np.maximum(norms,1e-12)

def state_policy(states,timers,exposed,slope,dt_hours=DT_HOURS,commute=True):
    """Update state using PRESENT synthetic tide only; no future response.

    states and timers are private mutable arrays, no original animal states.
    Transit timers begin in OUTBOUND/INBOUND then finish after finite duration.
    """
    if dt_hours<=0:raise ValueError("Invalid numerical time step")
    # State-memory: broad resource hysteresis, enter/exits at different A(H).
    go=(states==0)&(slope<0)&(exposed>=ENTER_EXPOSED_FRAC)
    back=(states==2)&(slope>0)&(exposed<=EXIT_EXPOSED_FRAC)
    if commute:
        states[go]=1;timers[go]=COMMUTE_HOURS
        states[back]=3;timers[back]=COMMUTE_HOURS
    else:
        states[go]=2
        states[back]=0
    return states,timers

def finish_transits(states,timers,dt_hours=DT_HOURS):
    move=(states==1)|(states==3)
    timers[move]-=dt_hours
    arrived=move&(timers<=0)
    states[arrived&(states==1)]=2
    states[arrived&(states==3)]=0
    timers[arrived]=0
    return states,timers

def heading_update(heading,positions,rng,social=False):
    """Actual 3D Reynolds-like heading forces, NEVER change speed policy."""
    n=heading.shape[0]
    if positions.shape!=(n,3):raise ValueError("Original toy positions require 3D")
    force=np.zeros_like(heading)
    n_mean=0.
    if social:
        delta=positions[None,:,:]-positions[:,None,:]
        # 3D toroidal synthetic world; no target- or field-derived positions.
        delta=delta-WORLD_BOX_KM*np.rint(delta/WORLD_BOX_KM)
        d2=np.sum(delta*delta,axis=2)
        rad=(d2>1e-14)&(d2<NEIGHBOR_RADIUS_KM**2)
        counts=rad.sum(axis=1)
        n_mean=float(np.mean(counts))
        den=np.maximum(counts[:,None],1)
        alignment=normalize3(np.sum(rad[:,:,None]*heading[None,:,:],axis=1)/den)
        cohesion=normalize3(np.sum(rad[:,:,None]*delta,axis=1)/den)
        separation_mask=rad&(d2<SEPARATION_RADIUS_KM**2)
        sep=normalize3(np.sum(-separation_mask[:,:,None]*delta/(d2[:,:,None]+1e-6),axis=1))
        active=(counts>0)[:,None]
        force=active*(ALIGNMENT*alignment+COHESION*cohesion+SEPARATION*sep)
    candidate=heading+force+rng.normal(0.,HEADING_NOISE,heading.shape)
    # Toy movement mostly horizontal but genuinely 3D.
    candidate[:,2]*=.15
    return normalize3(candidate),n_mean

def mode_speeds(mode,states,exposed,slope):
    if mode in ("A0_NO_TIDE_NO_SOCIAL",):
        return np.full_like(states,FIXED_SPEED,dtype=float)
    if mode=="A1_HEIGHT_ONLY_NO_SOCIAL":
        return np.full_like(states,HEIGHT_ONLY_BASE+HEIGHT_ONLY_GAIN*float(exposed),dtype=float)
    if mode=="A2_PHASE_ONLY_NO_SOCIAL":
        return np.full_like(states,PHASE_ONLY_BASE+PHASE_ONLY_EBB_BONUS*float(slope<0),dtype=float)
    if mode=="A3_HYSTERESIS_NO_COMMUTE_NO_SOCIAL":
        return np.where(states==2,SPEEDS[2],SPEEDS[0]).astype(float)
    if mode in ("A4_TIDE_STATE_GATE_NO_SOCIAL","A5_TIDE_STATE_GATE_WITH_3D_BOIDS"):
        return SPEEDS[states]
    raise ValueError("Unregistered source-free ablation "+str(mode))

def trajectory_one_seed(mode,seed):
    """Positions are 3D, response is 2D horizontal step from those positions."""
    if mode not in MODELS or seed not in SEEDS:
        raise ValueError("Only previously fixed model and RNG seeds admitted")
    rng=np.random.default_rng(seed)
    positions=rng.uniform(0,WORLD_BOX_KM,size=(AGENTS,3))
    headings=rng.normal(size=(AGENTS,3))
    headings[:,2]*=.15
    headings=normalize3(headings)
    states=np.zeros(AGENTS,dtype=np.int16)
    transit_timers=np.zeros(AGENTS,dtype=float)
    steps=int(DAYS*24/DT_HOURS)
    start=int(WARMUP_HOURS/DT_HOURS)
    times=np.arange(steps,dtype=float)*DT_HOURS
    heights,slopes=tide_height_slope(times)
    response=np.empty((steps-start,AGENTS),dtype=float)
    state_fractions=np.zeros(4,dtype=float)
    neighbor_counts=0.
    v3_sum=0.
    for step in range(steps):
        h=float(heights[step]); dh=float(slopes[step])
        exposed=float(available_fraction(h))
        commute=mode in ("A4_TIDE_STATE_GATE_NO_SOCIAL","A5_TIDE_STATE_GATE_WITH_3D_BOIDS")
        gate=commute or mode=="A3_HYSTERESIS_NO_COMMUTE_NO_SOCIAL"
        if gate:state_policy(states,transit_timers,exposed,dh,commute=commute)
        social=mode=="A5_TIDE_STATE_GATE_WITH_3D_BOIDS"
        headings,n_mean=heading_update(headings,positions,rng,social=social)
        speed=mode_speeds(mode,states,exposed,dh)*np.exp(rng.normal(0.,LOG_SPEED_NOISE,AGENTS))
        deltas=headings*(speed[:,None]*DT_HOURS)
        positions=np.mod(positions+deltas,WORLD_BOX_KM)
        if step>=start:
            horizontal_speed=np.linalg.norm(deltas[:,:2],axis=1)/DT_HOURS
            response[step-start]=np.log1p(horizontal_speed)
            state_fractions+=np.bincount(states,minlength=4)/AGENTS
            neighbor_counts+=n_mean
            v3_sum+=float(speed.mean())
        if commute:finish_transits(states,transit_timers)
    return (heights[start:],slopes[start:],response,{
        "state_fraction":{label:float(v/(steps-start)) for label,v in zip(STATE_NAMES,state_fractions)},
        "mean_neighbor_count":neighbor_counts/(steps-start),
        "mean_original_toy_3D_speed_km_h":v3_sum/(steps-start),
        "motor_social_on":mode=="A5_TIDE_STATE_GATE_WITH_3D_BOIDS",
    })

def signed_bin_effects(heights,slopes,response):
    """Equal 0.5m H-bin weight; no cherry-picked +.5m threshold tuning."""
    heights=np.asarray(heights,float)
    slopes=np.asarray(slopes,float)
    vals=np.asarray(response,float)
    if vals.ndim!=2 or vals.shape[0]!=len(heights):
        raise ValueError("Toy response must be time × synthetic agent")
    if not np.all(np.isfinite(vals)):raise ValueError("Nonfinite synthetic motility")
    bands=np.floor(heights/TIDE_HEIGHT_BIN_M).astype(int)
    each={}
    for k in sorted(set(bands)):
        pos=(bands==k)&(slopes>0)
        neg=(bands==k)&(slopes<0)
        if np.sum(pos)<5 or np.sum(neg)<5:continue
        by_agent=vals[neg].mean(axis=0)-vals[pos].mean(axis=0)
        each[int(k)]=float(by_agent.mean())
    if not each or not any(k<=0 for k in each) or not any(k>=1 for k in each):
        raise ValueError("Synthetic tide does not cover registered sign targets")
    low=float(np.mean([v for k,v in each.items() if k<=0]))
    high=float(np.mean([v for k,v in each.items() if k>=1]))
    high_minus_low=float(vals[heights>=EXTREME_HIGH_WATER_M].mean()
                         -vals[heights<=EXTREME_LOW_WATER_M].mean())
    target={
        "high_minus_low":high_minus_low,
        "low_ebb_minus_flood":low,
        "high_ebb_minus_flood":high,
        "low_minus_high_phase_difference":low-high,
        "bin_0_to_plus_0p5_ebb_minus_flood":each.get(0),
        "bin_plus_0p5_to_plus_1_ebb_minus_flood":each.get(1),
    }
    motif=(high_minus_low<0 and low>0 and high<0)
    return target,{"fixed_0p5m_height_bin_ebb_minus_flood":{
        str(k):float(v) for k,v in each.items()},
        "registered_three_sign_motif_all_met":bool(motif),
        "height_bin_count":len(each),
        "low_height_bin_count":sum(k<=0 for k in each),
        "high_height_bin_count":sum(k>=1 for k in each)}

def run():
    outputs={}
    for mode in MODELS:
        runs=[]
        for seed in SEEDS:
            h,dh,response,mechanics=trajectory_one_seed(mode,seed)
            contrasts,bin_stats=signed_bin_effects(h,dh,response)
            runs.append({"seed":seed,**contrasts,**bin_stats,"3D_motor_diagnostics":mechanics})
        keys=tuple(runs[0][k] for k in ()) # Keep an explicit result field order instead of model selection.
        mean={}
        ranges={}
        for k in ("high_minus_low","low_ebb_minus_flood","high_ebb_minus_flood",
                  "low_minus_high_phase_difference",
                  "bin_0_to_plus_0p5_ebb_minus_flood",
                  "bin_plus_0p5_to_plus_1_ebb_minus_flood"):
            values=np.array([r[k] for r in runs],float)
            mean[k]=float(values.mean())
            ranges[k]={"min":float(values.min()),"max":float(values.max())}
        signs=sum(x["registered_three_sign_motif_all_met"] for x in runs)
        outputs[mode]={"synthetic_seeds":len(runs),
               "seeds_with_all_three_registered_signs":signs,
               "seed_count_not_biological_independent_sites":True,
               "equal_seed_mean_metrics":mean,"full_seed_metric_ranges":ranges,
               "all_source_free_seed_reports":runs}
        print("V37_ABLATION",mode,json.dumps({
             "motif_seeds":signs,"total_seeds":len(runs),
             "signed_means":mean},sort_keys=True),flush=True)
    return {"status":"COMPLETE_ORIGINAL_SYNTHETIC_MODEL_SUFFICIENCY_ABLATIONS",
      "science_design":"Post-v33/v34 empirical sign-targeted mechanistic toy experiment; never biological validation",
      "protocol":PROTOCOL,"source":"No original animal/GPS/RWS sea levels or seabed DEM read",
      "NO_EMPIRICAL_DATA_used":True,
      "policy_parameters":{
         "original_source_free_tide_period_hours":PERIOD_HOURS,
         "source_free_spring_neap_hours":SPRING_NEAP_PERIOD_HOURS,
         "synthetic_water_amplitude_m":1.2,
         "spring_neap_additive_amplitude_m":.09,
         "synthetic_uniform_bed_range_m":[ELEVATION_MIN,ELEVATION_MAX],
         "resource_exposure_A_enter":ENTER_EXPOSED_FRAC,
         "resource_exposure_A_exit":EXIT_EXPOSED_FRAC,
         "motor_3D_hardcoded_alignment":ALIGNMENT,
         "motor_3D_hardcoded_cohesion":COHESION,
         "motor_3D_hardcoded_separation":SEPARATION,
         "motor_neighbor_radius_km":NEIGHBOR_RADIUS_KM,
         "roost_commute_forage_transit_speed_km_h":list(map(float,SPEEDS)),
         "toy_3D_periodic_world_size_km":list(map(float,WORLD_BOX_KM)),
         "synthetic_agents_not_field_sample_size":AGENTS,
         "synthetic_RNG_seeds":len(SEEDS),
         "synthetic_simulation_days":DAYS,
         "burnin_hours":WARMUP_HOURS,
         "source_free_timestep_hours":DT_HOURS,
      },
      "registered_motif":{
         "high_minus_low":"negative",
         "low_ebb_minus_flood":"positive",
         "high_ebb_minus_flood":"negative",
         "motif_chosen_AFTER_observed_v33_v34_results":True,
      },
      "ablation_order":list(MODELS),
      "all_ablation_signed_results":outputs,
      "interpretation_limits":[
          "This is a constructed 3D movement policy, NOT a fitted oystercatcher model",
          "No actual seabed DEM, tide gauge, prey, foraging states or original wild GPS used",
          "Motor-on Boids alignment/cohesion/separation may be unnecessary for the fixed signs even if important in field movement",
          "Synthetic threshold values were fixed after viewing earlier empirical signs; no discovery or independent confirmation",
          "Synthetic 24 seeds are repeated computation trials, not n=24 independent biological populations",
          "3D model z is an arbitrary periodized coordinate, NOT measured bird altitude or vertical ecological niche",
      ]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,default=Path("validation_v37/results/synthetic_tide_3D_boids_v37.json"))
    args=parser.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
          prefix=".v37-synthetic-",delete=False) as f:
        f.write(text);tmp=Path(f.name)
    os.replace(tmp,args.out)
    print("V37_SYNTHETIC_STATUS",result["status"])
    print("V37_SYNTHETIC_FULL_ABLATIONS",json.dumps({
        k:{"motif_seeds":v["seeds_with_all_three_registered_signs"],
           "signed_means":v["equal_seed_mean_metrics"]}
        for k,v in result["all_ablation_signed_results"].items()},sort_keys=True))
    print("V37_NO_BIOLOGICAL_OBSERVATIONS_USED")
if __name__=="__main__":main()
