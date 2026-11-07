"""Exact memory-vs-masking availability frontier for SYNTHETIC bat echo histories.

Enumerate all 2^K Bernoulli echo-availability patterns, K<=10.
No source animal data, no BAT-specific fitted p/q/r and no author MATLAB replay.
"""
from __future__ import annotations
import json,math
from pathlib import Path

from bat_echo_memory_static_dynamic_v1 import mse_exact

OUT=Path(__file__).resolve().parent/"BAT_ECHO_MASKING_AVAILABILITY_V1.json"
CONTRACT=Path(__file__).resolve().parent/"BAT_ECHO_MASKING_AVAILABILITY_PREOUTPUT_2026_11_07.md"
AVAILABILITY=(1.0,.75,.50,.25)
RHO=(0.,.25,.50,1.,2.,4.)
K_RANGE=tuple(range(1,11))
TOL=1e-12

def exact_conditional_memory(k,p,q,r=1.0):
    """Returns probability of no echoes, MSE conditional on >=1 usable echo."""
    if not isinstance(k,int) or k<1 or k>10:
        raise ValueError("Supported prespecified K=1..10")
    if not 0<=p<=1 or r<=0 or q<0:
        raise ValueError("p in 0..1, q>=0, r>0")
    none=(1-p)**k
    if p==0:return {"all_missing_probability":1.,"conditional_MSE":None,
                       "possible_nonempty_subsets":(1<<k)-1}
    total=0.
    weighted=0.
    for mask in range(1,1<<k):
        n=mask.bit_count()
        probability=(p**n)*((1-p)**(k-n))
        if probability==0:continue
        staleness=sum(((mask>>h).bit_count())**2 for h in range(1,k))
        condition=r/n+q*staleness/(n*n)
        total+=probability*condition
        weighted+=probability
    if not math.isclose(weighted,1-none,rel_tol=1e-11,abs_tol=1e-11):
        raise ValueError("SOURCE_THEORY_WEIGHT_SUM_NOT_ONE")
    return {"all_missing_probability":none,
            "conditional_MSE":total/weighted,
            "possible_nonempty_subsets":(1<<k)-1}

def pareto_memory(rows):
    best=[]
    for a in rows:
        if a["conditional_MSE"] is None:continue
        x,y=a["all_missing_probability"],a["conditional_MSE"]
        dominated=False
        for b in rows:
            if b["K"]==a["K"] or b["conditional_MSE"] is None:continue
            xb,yb=b["all_missing_probability"],b["conditional_MSE"]
            if xb<=x+TOL and yb<=y+TOL and (xb<x-TOL or yb<y-TOL):
                dominated=True;break
        if not dominated:best.append(a["K"])
    return best

def run():
    if not CONTRACT.exists():raise ValueError("STOP_PREOUTPUT_SOURCE_CONTRACT_MISSING")
    worlds=[]
    for p in AVAILABILITY:
        for rho in RHO:
            entries=[]
            for k in K_RANGE:
                v=exact_conditional_memory(k,p,rho)
                entries.append({"K":k,**v})
            worlds.append({
              "usable_echo_probability_per_pulse":p,
              "target_change_to_obs_error_q_over_r":rho,
              "memory_K_1_to_10":entries,
              "nondominated_K_without_arbitrary_reward":pareto_memory(entries),
              "memory_five":{
                "probability_all_missing":entries[4]["all_missing_probability"],
                "conditional_MSE":entries[4]["conditional_MSE"],
                "conditional_MSE_minus_one_call":entries[4]["conditional_MSE"]-entries[0]["conditional_MSE"],
                "difference_all_missing_probability":entries[4]["all_missing_probability"]-entries[0]["all_missing_probability"]}
            })
    p1=[x for x in worlds if x["usable_echo_probability_per_pulse"]==1.]
    maximum_error=max(
       abs(z["conditional_MSE"]-mse_exact(z["K"],1.,w["target_change_to_obs_error_q_over_r"]))
       for w in p1 for z in w["memory_K_1_to_10"])
    if maximum_error>1e-10:raise ValueError("STOP_ANALYTIC_SOURCE_NO_DROPOUT_FORMULA_DISAGREEMENT")
    return {
      "schema":1,
      "status":"EXACT_SOURCE_MOTIVATED_ECHO_DROP_OUT_PARETO_NOT_REAL_BAT_MODEL",
      "original_study_prior":"Mazar and Yovel 2026 eLife 10.7554/eLife.105571",
      "upstream_source_commit":"a74fb61a8efb57ca37693893c3bd7b35fa94fa89",
      "new_bat_measurements":False,
      "authentic_MATLAB_model_rerun":False,
      "original_moving_bat_echo_geometry_reproduced":False,
      "emitted_call_availability_independent_bernoulli":True,
      "all_emitted_pulses_K_included_even_if_masked":True,
      "source_default_memory_calls_five_only_as_reference":True,
      "observation_noise_scale_r":1.,
      "p_grid":list(AVAILABILITY),"q_over_r_grid":list(RHO),
      "memory_K_range":[1,10],
      "fixed_exact_cases":len(worlds)*10,
      "analytic_formula_earlier_all_echoes_recovered":maximum_error,
      "worlds":worlds,
      "interpretation":"Accuracy conditional on >=1 echo and risk of 0 available echoes are separate outcomes; memory cannot be optimized without a cost for zero detections.",
      "limitations":[
         "Generic Kalman/filtering-style accuracy versus latency trade-off; not novel bat neurophysiology.",
         "All missing echoes are ignored rather than scored with an arbitrary risk/fitness cost.",
         "Source sonar masking is spatially correlated, not independent Bernoulli per emitted call.",
         "Equal-average accepted echo positions is not original Mazar 2026 multi-call clustering.",
         "Real bat measurement error r, environmental mobility q, availability p are not measured by source here.",
         "One original source cannot establish new colony/predator task generality or prey capture success."
      ]
    }

if __name__=="__main__":
    x=run()
    OUT.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n")
    print("ECHO_DROPOUT_MEMORY_THEORY",x["status"],"FIXED_CASES",x["fixed_exact_cases"],
          "RECOVERY_MAX_ERROR",x["analytic_formula_earlier_all_echoes_recovered"])
    for w in x["worlds"]:
        print("THEORY_FRONTIER","p",w["usable_echo_probability_per_pulse"],
              "q_over_r",w["target_change_to_obs_error_q_over_r"],
              "K_PARETO",w["nondominated_K_without_arbitrary_reward"],
              "five_memory_no_echo",round(w["memory_five"]["probability_all_missing"],6),
              "five_memory_delta_MSE",round(w["memory_five"]["conditional_MSE_minus_one_call"],6))
