"""Bat echo memory horizon under static vs moving environmental targets.

This is an independent, EXACT Gaussian filtering-theory illustration,
NOT the original Mazar/Yovel 2026 sonar simulator, not a new bat observation,
and NOT a calibration from Krivoruchko 2024 attack/capture data.

State x_t=x_(t-1)+eta_t, eta~N(0,q); accepted echo y_t=x_t+epsilon_t,
epsilon~N(0,r). Equal-memory K accepted observations target CURRENT x_t.
"""
from __future__ import annotations
import json,math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"BAT_ECHO_MEMORY_STATIC_DYNAMIC_V1.json"
CONTRACT=ROOT/"BAT_ECHO_MEMORY_STATIC_VS_MOVING_PREOUTPUT_2026_11_07.md"
GRID=(0.0,0.10,0.25,0.50,1.0,2.0,4.0)
K_GRID=tuple(range(1,11))
SOURCE_PAPER_DEFAULT_MEMORY_K=5
R=1.0
N_SYNTHETIC=40_000
SEED=20261107
MC_REL_TOL=.05

def mse_exact(k,r=R,q=0.0):
    if not isinstance(k,int) or k<1 or r<=0 or q<0:
        raise ValueError("K integer>=1, r>0, q>=0 required")
    return r/k+q*(k-1)*(2*k-1)/(6*k)

def continuous_optimum(r=R,q=0.0):
    if r<=0 or q<0:raise ValueError("Invalid variance inputs")
    return None if q==0 else math.sqrt(3*r/q+.5)

def integer_optimum(r=R,q=0.0,maxk=10):
    if maxk<1:raise ValueError("maxk<1")
    return min(range(1,maxk+1),key=lambda k:mse_exact(k,r,q))

def gain_boundary_ratio(k):
    """For k>1, q/r < 6/(2k-1) iff memory k beats one call."""
    if not isinstance(k,int) or k<=1:raise ValueError("K needs >1")
    return 6/(2*k-1)

def one_scenario(rho,rng):
    # r=1, q=rho; one synth target state per independent trial.
    # x_t=0 sets a reference origin; past x_(t-j)=-sum past innovations.
    epsilon=rng.normal(0,math.sqrt(R),size=(N_SYNTHETIC,10))
    eta=rng.normal(0,math.sqrt(rho),size=(N_SYNTHETIC,9))
    past=-np.cumsum(eta,axis=1)
    x=np.concatenate((np.zeros((N_SYNTHETIC,1)),past),axis=1)
    y=x+epsilon
    means=np.cumsum(y,axis=1)/np.arange(1,11)[None,:]
    observed=np.mean(means**2,axis=0)
    theory=np.array([mse_exact(k,R,rho) for k in K_GRID])
    relative=np.abs(observed-theory)/theory
    return {
       "q_over_r":rho,
       "continuous_optimal_K":continuous_optimum(R,rho),
       "integer_optimal_K_1_to_10":integer_optimum(R,rho,10),
       "analytic_MSE_for_K_1":float(theory[0]),
       "analytic_MSE_for_K_5":float(theory[4]),
       "analytic_MSE_for_K_10":float(theory[9]),
       "five_call_MSE_minus_one_call":float(theory[4]-theory[0]),
       "five_call_better_than_one_call":bool(theory[4]<theory[0]-1e-12),
       "maximum_relative_MC_vs_analytic_error":float(np.max(relative)),
       "errors_by_history_K":[{"K":k,
         "analytic_mse":float(v),
         "synthetic_MC_mse":float(est),
         "relative_simulation_error":float(err)}
        for k,v,est,err in zip(K_GRID,theory,observed,relative)]
    }

def run():
    if not CONTRACT.exists():raise ValueError("STOP_PREOUTPUT_CONTRACT_MISSING")
    rng=np.random.default_rng(SEED)
    worlds=[one_scenario(rho,rng) for rho in GRID]
    errors=[a["maximum_relative_MC_vs_analytic_error"] for a in worlds]
    return {
       "schema":1,
       "status":"SOURCE_MOTIVATED_EXACT_FILTERING_THEORY_NO_BAT_MODEL_REPLAY",
       "source_prior_paper":"Mazar & Yovel 2026 eLife DOI 10.7554/eLife.105571",
       "source_original_repo_commit":"a74fb61a8efb57ca37693893c3bd7b35fa94fa89",
       "original_MATLAB_source_code_replayed":False,
       "source_original_bat_echoes_measured":False,
       "new_bat_measurements":False,
       "source_2024_Molossus_capture_prediction_replayed":False,
       "original_Mazar_memory_rule_identical_to_gaussian_mean":False,
       "source_default_memory_calls":SOURCE_PAPER_DEFAULT_MEMORY_K,
       "test_length_scale":"dimensionless variances; r=1; q/r is source-UNMEASURED target-drift-to-noise ratio",
       "observation_assumptions":"all accepted calls; independent Gaussian sensory noise; random-walk target; perfect self-motion compensation",
       "formula":"MSE(K)=r/K + q*(K-1)*(2*K-1)/(6*K)",
       "continuous_optimum_formula":"sqrt(3*r/q+1/2) if q>0; no finite optimum if q=0",
       "boundary_q_over_r_for_5_vs_1":gain_boundary_ratio(5),
       "boundary_q_over_r_for_10_vs_1":gain_boundary_ratio(10),
       "prespecified_q_over_r":list(GRID),
       "prespecified_K_range":[1,10],
       "n_synthetic_independent_histories_per_rho":N_SYNTHETIC,
       "source_seed":SEED,
       "monte_carlo_relative_tolerance":MC_REL_TOL,
       "max_relative_mc_error_all_70":max(errors),
       "monte_carlo_check_pass":max(errors)<=MC_REL_TOL,
       "worlds":worlds,
       "limits":[
         "Standard filtering-theory speed/accuracy trade-off, not a newly discovered mathematical theorem.",
         "Original cave-exit authors have already established benefit of multi-call integration under masking.",
         "Original 2026 MATLAB clustering uses discrete echoes, memory and movement; this is not that simulator.",
         "Real moving prey drift q and admitted receiver noise r not observed in source 2024 capture data.",
         "Real source cave-wall stability is allocentric only with successful own-motion compensation.",
         "Dropped/jammed echoes and collision avoidance with latency are not modeled by a complete Gaussian window.",
         "No actual bat foraging, physical masking, fitness or across-species predictive generality established."
       ]
    }

if __name__=="__main__":
    obj=run()
    OUT.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print("THEORY_GATE",obj["status"],"MC_PASS",obj["monte_carlo_check_pass"],
          "MAX_MC_ERROR",obj["max_relative_mc_error_all_70"])
    print("EXACT_BOUNDARY_K5",obj["boundary_q_over_r_for_5_vs_1"],
          "EXACT_BOUNDARY_K10",obj["boundary_q_over_r_for_10_vs_1"])
    for x in obj["worlds"]:
        print("TARGET_DYNAMIC_RATIO",x["q_over_r"],
              "best_K",x["integer_optimal_K_1_to_10"],
              "MSE_K1",round(x["analytic_MSE_for_K_1"],6),
              "MSE_K5",round(x["analytic_MSE_for_K_5"],6),
              "five_call_gain",round(x["five_call_MSE_minus_one_call"],6),
              "MC_err",round(x["maximum_relative_MC_vs_analytic_error"],6))
