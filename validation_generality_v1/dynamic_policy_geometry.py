"""Generality v1: a minimal mechanistic sufficient-condition demonstration.

This module uses only mathematically specified resource options (synthetic
known truth). It does not turn a positive synthetic test into real wild
animal movement confirmation or estimate social Reynolds alignment.
"""
from __future__ import annotations
from math import exp,fsum,isfinite

def phase_policy(resource_states,environmental_rates,travel_costs,*,phase:int,
                 response_horizon:float,sensitivity:float=1.0,reachable=None):
    """Softmax resource-target choice for (state + horizon * phase * rate).

    For each accessible option j:
       log utility = sensitivity*(R_j + tau*phase*dR_j/dt) - cost_j
    A spatially uniform rate cancels out of softmax and cannot cause a
    phase-specific choice. In the absence of an alternative, no switch.
    """
    n=len(resource_states)
    if n<1 or len(environmental_rates)!=n or len(travel_costs)!=n:
        raise ValueError("POLICY_INVALID_OPTIONS")
    if phase not in (-1,1):
        raise ValueError("POLICY_PHASE_MUST_BE_OPPOSITE_SIGN")
    if response_horizon<0 or not isfinite(response_horizon) or not isfinite(sensitivity):
        raise ValueError("POLICY_INVALID_HORIZON_OR_SENSITIVITY")
    if reachable is None:
        reachable=[True]*n
    if len(reachable)!=n or not any(reachable):
        raise ValueError("POLICY_NO_ACTUALLY_REACHABLE_STATE")
    if not all(isfinite(float(x)) for seq in
               (resource_states,environmental_rates,travel_costs) for x in seq):
        raise ValueError("POLICY_NONFINITE_ORIGINAL_STATE")
    utilities=[sensitivity*(resource_states[i]+phase*response_horizon*environmental_rates[i])
               -travel_costs[i] if reachable[i] else float("-inf") for i in range(n)]
    center=max(utilities)
    weights=[exp(x-center) if reachable[i] else 0.0
             for i,x in enumerate(utilities)]
    den=fsum(weights)
    return [w/den for w in weights]

def phase_switch_total_variation(*args,response_horizon,sensitivity=1.,reachable=None):
    positive=phase_policy(*args,phase=1,response_horizon=response_horizon,
                          sensitivity=sensitivity,reachable=reachable)
    negative=phase_policy(*args,phase=-1,response_horizon=response_horizon,
                          sensitivity=sensitivity,reachable=reachable)
    return .5*sum(abs(a-b) for a,b in zip(positive,negative))
