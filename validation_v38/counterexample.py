#!/usr/bin/env python3
"""v38: memoryless tide×phase counterexample for a source-free 3D Boids toy.

An analytic scalar speed interaction and fixed 3D inertial heading motion can
produce the three already-known wild-GPS signs without private ROOST/FORAGE
states or explicit commute. This is NOT an animal model fit or field evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
V37=ROOT/"validation_v37"/"simulation.py"
V37_GIT_BLOB_SHA="b4920aa6014306b7e776393db6ee7f469a892f8f"
sys.path.insert(0,str(V37.parent))
import simulation as old

PROTOCOL="docs/V38_MEMORYLESS_TIDAL_INTERACTION_IDENTIFIABILITY_PROTOCOL.md"
MODELS=(
    "C0_ADDITIVE_H_PLUS_PHASE",
    "C1_SMOOTH_INTERACTION_NO_SOCIAL",
    "C2_SMOOTH_INTERACTION_WITH_3D_BOIDS",
    "C3_WRONG_CLOCK_HALF_TIDE_SHIFT",
)
N_AGENTS=old.AGENTS
SEEDS=old.SEEDS
TIMESTEP=old.DT_HOURS
TOTAL_DAYS=old.DAYS
BURNIN_HOURS=old.WARMUP_HOURS
HEIGHT_THRESHOLD=.50
BASE=.30
ALPHA=.48
BETA=.12
WIDTH=.30
HALF_CYCLE_HOURS=old.PERIOD_HOURS/2
ALPHAS=(.20,.48,.80)
BETAS=(.06,.12,.20)
WIDTHS=(.15,.30)
SPEED_NOISE_SD=old.LOG_SPEED_NOISE
PARAM_GRID_COUNT=len(ALPHAS)*len(BETAS)*len(WIDTHS)
NO_ORIGINAL_BIOLOGICAL_DATA=True
MOTIF_KEYS=old.MOTIF_KEYS

def assert_original_v37_code():
    """Pin exact original reference code, not merely six declared model names."""
    blob=V37.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(blob)).encode()+b"\0"+blob).hexdigest()
    if actual!=V37_GIT_BLOB_SHA:
        raise ValueError("Original v37 reference simulation source Git blob changed")
    if (old.MODELS[4]!="A4_TIDE_STATE_GATE_NO_SOCIAL"
        or old.MODELS[5]!="A5_TIDE_STATE_GATE_WITH_3D_BOIDS"
        or old.MOTIF_KEYS!=("high_minus_low","low_ebb_minus_flood","high_ebb_minus_flood")
        or old.PERIOD_HOURS!=12.4206
        or old.AGENTS!=30
        or tuple(old.SEEDS)!=tuple(range(24))):
        raise ValueError("Original v37 source or registered estimands drift")
    return {"reference_v37_Git_blob_SHA":actual,"source_protocol_unchanged":True}

def phase_sign(slope):
    """+1 for ebb, -1 for flood, 0 only at exact stationary astronomical water."""
    s=np.asarray(slope,dtype=float)
    return np.sign(-s)

def direct_speed_at_tide(height,slope,mode,alpha=ALPHA,beta=BETA,width=WIDTH):
    if mode not in MODELS:raise ValueError("Unexpected synthetic variant")
    if not (math.isfinite(alpha) and math.isfinite(beta) and
            math.isfinite(width) and alpha>=0 and beta>=0 and width>0):
        raise ValueError("Toy parameter outside physical positive specification")
    h=np.asarray(height,dtype=float)
    d=np.asarray(slope,dtype=float)
    exposure=old.available_fraction(h)
    direct=BASE+alpha*exposure
    if mode=="C0_ADDITIVE_H_PLUS_PHASE":
        val=direct+beta*phase_sign(d)
    else:
        val=direct+beta*phase_sign(d)*np.tanh((HEIGHT_THRESHOLD-h)/width)
    if np.any(np.asarray(val)<=0) or not np.all(np.isfinite(val)):
        raise ValueError("Nonpositive or nonfinite synthetic speed")
    return val

def one_3d_step(mode,positions,headings,rng,t):
    """3D kinematics, original v37 heading-only Reynolds motor where enabled."""
    if mode not in MODELS:raise ValueError("Unregistered original toy control")
    social=mode=="C2_SMOOTH_INTERACTION_WITH_3D_BOIDS"
    h,slope=old.tide_height_slope(float(t))
    if mode=="C3_WRONG_CLOCK_HALF_TIDE_SHIFT":
        source_h,source_slope=old.tide_height_slope(float(t)+HALF_CYCLE_HOURS)
    else:
        source_h,source_slope=h,slope
    v=float(direct_speed_at_tide(source_h,source_slope,mode))
    new_heading,neighbors=old.heading_update(headings,positions,rng,social=social)
    speed=v*np.exp(rng.normal(0.,SPEED_NOISE_SD,N_AGENTS))
    delta=new_heading*(speed[:,None]*TIMESTEP)
    newpos=np.mod(positions+delta,old.WORLD_BOX_KM)
    log_horizontal_speed=np.log1p(np.linalg.norm(delta[:,:2],axis=1)/TIMESTEP)
    if not np.isfinite(log_horizontal_speed).all():raise ValueError("Toy 3D position nonfinite")
    return newpos,new_heading,log_horizontal_speed,float(neighbors)

def trajectory_one_seed(mode,seed):
    if mode not in MODELS or seed not in SEEDS:
        raise ValueError("Unregistered toy mode or seed")
    rng=np.random.default_rng(seed)
    p=rng.uniform(0,old.WORLD_BOX_KM,size=(N_AGENTS,3))
    heading=rng.normal(size=(N_AGENTS,3))
    heading[:,2]*=.15
    heading=old.normalize3(heading)
    steps=int(TOTAL_DAYS*24/TIMESTEP)
    burn=int(BURNIN_HOURS/TIMESTEP)
    times=np.arange(steps,dtype=float)*TIMESTEP
    heights,slopes=old.tide_height_slope(times)
    response=np.empty((steps-burn,N_AGENTS),dtype=float)
    mean_neighbor=0.
    for i,t in enumerate(times):
        p,heading,log_speed,neighbors=one_3d_step(mode,p,heading,rng,t)
        if i>=burn:
            response[i-burn]=log_speed
            mean_neighbor+=neighbors
    contrasts,bins=old.signed_bin_effects(heights[burn:],slopes[burn:],response)
    return {"seed":seed,"signed_contrasts":contrasts,
            "motif_all_three_signed":bins["registered_three_sign_motif_all_met"],
            "all_height_bin_directions":bins["fixed_0p5m_height_bin_ebb_minus_flood"],
            "mean_source_free_3D_neighbor_count":mean_neighbor/(steps-burn),
            "social_heading_only":mode=="C2_SMOOTH_INTERACTION_WITH_3D_BOIDS",
            "no_latent_ROOST_FORAGE_COMMUTE_state":True,
            "no_source_animal_or_raster_data_used":True}

def analytic_grid():
    """The same source-free sign targets, but no 3D motor direction attenuation.

    The 18 fixed parameter combinations are NOT fit, and noise is common across
    combinations for a given seed. Full signed values/positive and failures kept.
    """
    steps=int(TOTAL_DAYS*24/TIMESTEP)
    burn=int(BURNIN_HOURS/TIMESTEP)
    times=np.arange(burn,steps,dtype=float)*TIMESTEP
    h,slope=old.tide_height_slope(times)
    eps={seed:np.random.default_rng(seed).normal(0.,SPEED_NOISE_SD,
                                     (len(times),N_AGENTS))
         for seed in SEEDS}
    data=[]
    for alpha in ALPHAS:
        for beta in BETAS:
            for width in WIDTHS:
                speed=np.asarray(direct_speed_at_tide(h,slope,MODELS[1],
                                    alpha=alpha,beta=beta,width=width),dtype=float)
                seeds=[]
                for seed in SEEDS:
                    response=np.log1p(speed[:,None]*np.exp(eps[seed]))
                    signed,flags=old.signed_bin_effects(h,slope,response)
                    seeds.append({"seed":seed,"signed_contrasts":signed,
                       "all_three_signs":flags["registered_three_sign_motif_all_met"]})
                data.append({"alpha":alpha,"beta":beta,"width_m":width,
                   "n_seeds":len(seeds),
                   "seeds_with_three_sign_motif":sum(x["all_three_signs"] for x in seeds),
                   "full_registered_seed_signs":seeds})
    return data

def source_free_history_intervention():
    """Two possible toy causal policies give different predictions at same H,Hdot.

    A state-free direct model has one instantaneous speed. A v37 stateful
    model retains externally initialized ROOST vs FORAGE when no crossing.
    This is a model-identifiability illustration, NOT an animal experiment.
    """
    h=0.
    dh=0.
    no_state=float(direct_speed_at_tide(h,dh,MODELS[1]))
    states=np.array([0,2],dtype=np.int16)
    timers=np.zeros(2,dtype=float)
    old.state_policy(states,timers,float(old.available_fraction(h)),dh,commute=True)
    if tuple(states)!=(0,2):
        raise ValueError("v37 original state intervention did not preserve histories")
    by_state=old.SPEEDS[states]
    return {"identical_present_water_height_m":h,
            "identical_present_tidal_derivative_m_per_h":dh,
            "memoryless_direct_both_histories_speed_km_h":[no_state,no_state],
            "stateful_v37_ROOST_vs_FORAGE_speed_km_h":list(map(float,by_state)),
            "only_model_constructs_not_observed_birds":True,
            "field_discriminator":"conditional prior habitat/state/phase effect after fixing current H,dH,clock and GPS effort"}

def run():
    original=assert_original_v37_code()
    variants={}
    for mode in MODELS:
        results=[trajectory_one_seed(mode,seed) for seed in SEEDS]
        metric_names=(
         "high_minus_low","low_ebb_minus_flood",
         "high_ebb_minus_flood","low_minus_high_phase_difference",
         "bin_0_to_plus_0p5_ebb_minus_flood","bin_plus_0p5_to_plus_1_ebb_minus_flood",
        )
        means={k:float(np.mean([r["signed_contrasts"][k] for r in results]))
               for k in metric_names}
        variants[mode]={"n_artificial_seeds":len(results),
            "all_three_signs_seed_count":sum(r["motif_all_three_signed"] for r in results),
            "equal_seed_signed_means":means,
            "all_24_seed_full_signed_results":results}
        print("V38_MODE",mode,json.dumps({
               "n_seeds":len(results),
               "motif_seeds":variants[mode]["all_three_signs_seed_count"],
               "signed_means":means},sort_keys=True),flush=True)
    sensitivity=analytic_grid()
    count=sum(x["seeds_with_three_sign_motif"] for x in sensitivity)
    return {"status":"COMPLETE_SOURCE_FREE_TIDAL_MECHANISM_IDENTIFIABILITY_COUNTEREXAMPLES",
       "protocol":PROTOCOL,
       "v37_original_source_sha_pinned":original,
       "no_original_animal_GPS_RWS_tide_or_bathymetric_data_used":True,
       "motif_selected_after_v33_v34_wild_GPS_observations":True,
       "registered_models":list(MODELS),
       "fixed_toy_parameters":{
          "base_speed_km_h":BASE,"alpha_exposure":ALPHA,
          "beta_height_times_tide_direction":BETA,
          "tanh_width_m":WIDTH,"height_flip_location_m":HEIGHT_THRESHOLD,
          "half_tidal_period_misalignment_hours":HALF_CYCLE_HOURS,
          "same_v37_tide_period_hours":old.PERIOD_HOURS,
          "toy_world_3D_km":list(map(float,old.WORLD_BOX_KM)),
          "agents":N_AGENTS,"timesteps_hours":TIMESTEP,
          "simulation_days":TOTAL_DAYS,"burnin_hours":BURNIN_HOURS,
          "independent_artificial_RNG_seeds_not_biological_population_count":len(SEEDS),
          "source_free_heading_noise":old.HEADING_NOISE,
          "source_free_speed_noise_log_sd":SPEED_NOISE_SD},
       "four_mechanistic_3D_variants":variants,
       "sensitivity_fixed_alpha":list(ALPHAS),
       "sensitivity_fixed_beta":list(BETAS),
       "sensitivity_fixed_width_m":list(WIDTHS),
       "sensitivity_analytic_no_3D_direction_projection":True,
       "sensitivity_total_18_fixed_parameter_combinations":len(sensitivity),
       "sensitivity_total_24_seed_runs":len(sensitivity)*len(SEEDS),
       "sensitivity_motif_seeds_among_all_fixed_runs":count,
       "all_sensitivity_combinations_and_seed_signs":sensitivity,
       "identical_H_and_derivative_state_memory_intervention":source_free_history_intervention(),
       "logical_result_scope":[
          "Any memoryless direct positive motif is a counterexample to universal necessity of state memory/commute for these already selected three signs",
          "v37 latent state and v38 direct smooth interaction are alternative sufficient constructed models",
          "Social heading forces not demonstrated necessary for the scalar tide-speed signs",
          "No wild field causal mechanism, food exposure, latent learning or 3D ecological niche was identified",
          "A discriminating field test needs habitat/behavioral state, observation process and out-of-time/space independent evaluation",
          "Parameter sweep explores only a deliberately limited sign-conforming family selected after seeing original field signs"]}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,
       default=Path("validation_v38/results/tide_memoryless_direct_identifiability_v38.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    payload=json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
              prefix=".v38-synthetic-",delete=False) as f:
        f.write(payload);tmp=Path(f.name)
    os.replace(tmp,args.out)
    summary={"model_sign_counts":{
          k:v["all_three_signs_seed_count"]
          for k,v in result["four_mechanistic_3D_variants"].items()},
       "number_of_grid_combinations":len(result["all_sensitivity_combinations_and_seed_signs"]),
       "full_parameter_grid_motif_seed_count":result["sensitivity_motif_seeds_among_all_fixed_runs"],
       "grid_total_runs":result["sensitivity_total_24_seed_runs"],
       "no_original_observations":result["no_original_animal_GPS_RWS_tide_or_bathymetric_data_used"]}
    print("V38_SYNTHETIC_STATUS",result["status"])
    print("V38_FIXED_COMPLETE_SUMMARY",json.dumps(summary,sort_keys=True))
    print("V38_FULL_SOURCE_FREE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":
    main()
