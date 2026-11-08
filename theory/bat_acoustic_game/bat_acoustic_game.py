"""SYNTHETIC two-bat sonar and 3D-route game. NOT calibrated to animals."""
from __future__ import annotations
from dataclasses import dataclass, replace
import math
import json

ACTIONS = ("EMIT", "STAGGER", "LISTEN", "JAM", "DETOUR")
EMISSION = {"EMIT":1.0, "STAGGER":.70, "LISTEN":.05,"JAM":1.15,"DETOUR":1.0}
PUBLIC_SIGNAL = {"EMIT":1.0,"STAGGER":.72,"LISTEN":.04,"JAM":.01,"DETOUR":1.0}
RECEPTIVITY = {"EMIT":.45,"STAGGER":.55,"LISTEN":1.60,"JAM":.10,"DETOUR":0.0}
VULNERABILITY = {"EMIT":1.0,"STAGGER":.28,"LISTEN":.12,"JAM":1.0,"DETOUR":0.0}
SELF_SENSOR_COST = {"EMIT":0.0,"STAGGER":.18,"LISTEN":1.0,"JAM":.23,"DETOUR":0.0}
ENERGY_COST = {"EMIT":0.0,"STAGGER":.035,"LISTEN":.015,"JAM":.070,"DETOUR":.10}

@dataclass(frozen=True)
class Environment:
    public_info: float = 1.0
    masking: float = 1.3
    contestability: float = 0.2
    jam_strength: float = 1.4
    detour_quality: float = .85
    routes: int = 4
    base_logit: float = 1.3
    detour_cost: float = ENERGY_COST["DETOUR"]

    def __post_init__(self):
        if self.routes < 1:
            raise ValueError("routes must be >=1")
        for key in ("public_info","masking","jam_strength","detour_cost"):
            if getattr(self,key) < 0:
                raise ValueError(key+" must be nonnegative")
        for key in ("contestability","detour_quality"):
            if not 0 <= getattr(self,key) <= 1:
                raise ValueError(key+" must lie in [0,1]")

def actions(env: Environment):
    return ACTIONS if env.routes >= 2 else ACTIONS[:-1]

def sigmoid(x):
    if x >= 0:
        return 1.0/(1.0+math.exp(-x))
    return math.exp(x)/(1.0+math.exp(x))

def success(own: str, other: str, env: Environment):
    """Arbitrary detectability response. Joint acoustic terms require co-location."""
    if own not in actions(env) or other not in actions(env):
        raise ValueError("Unadmitted action")
    x = env.base_logit-SELF_SENSOR_COST[own]
    if own != "DETOUR" and other != "DETOUR":
        x += env.public_info*RECEPTIVITY[own]*PUBLIC_SIGNAL[other]
        x -= env.masking*VULNERABILITY[own]*EMISSION[other]
        if other == "JAM":
            x -= env.jam_strength
    return sigmoid(x)

def payoff(own: str, other: str, env: Environment):
    """Toy consumption return; not a measured bat prey-capture law."""
    p=success(own,other,env)
    if own == "DETOUR":
        return env.detour_quality*p-env.detour_cost
    if other == "DETOUR":
        return p-ENERGY_COST[own]
    q=success(other,own,env)
    c=env.contestability
    return (1-c)*p+c*(2*p*p/(p+q))-ENERGY_COST[own]

def pure_nash(env: Environment):
    aa=actions(env)
    u={(a,b):payoff(a,b,env) for a in aa for b in aa}
    return [(a,b) for a in aa for b in aa
            if u[a,b]>=max(u[t,b] for t in aa)-1e-10
            and u[b,a]>=max(u[t,a] for t in aa)-1e-10]

def quantal_response(env: Environment, beta=8.0, alpha=.10,
                    tolerance=1e-11, max_iterations=15000, starting_action=None):
    """Damped logit best response, NOT a fitted behavior or Nash guarantee."""
    aa=actions(env)
    if beta<=0 or not 0<alpha<=1:
        raise ValueError("beta>0 and 0<alpha<=1 required")
    n=len(aa)
    matrix=[[payoff(a,b,env) for b in aa] for a in aa]
    x=[1/n]*n if starting_action is None else [float(a==starting_action) for a in aa]
    if starting_action is not None and starting_action not in aa:
        raise ValueError("Unknown initial action")
    for it in range(1,max_iterations+1):
        expected=[sum(matrix[i][j]*x[j] for j in range(n)) for i in range(n)]
        zmax=max(expected)
        w=[math.exp(beta*(v-zmax)) for v in expected]
        total=sum(w)
        nx=[(1-alpha)*x[i]+alpha*w[i]/total for i in range(n)]
        err=max(abs(nx[i]-x[i]) for i in range(n))
        x=nx
        if err<tolerance:
            break
    return {"actions":list(aa),"probabilities":dict(zip(aa,x)),
            "iterations":it,"converged":err<tolerance,"last_step_error":err,
            "pure_nash":[list(pair) for pair in pure_nash(env)]}

def jammer_indifference_contestability(env: Environment):
    """Pairwise threshold c* for JAM versus EMIT against an EMIT competitor.
    Does NOT guarantee JAM best response or any pure Nash equilibrium.
    """
    src=replace(env,contestability=0)
    pe=success("EMIT","EMIT",src)
    pj=success("JAM","EMIT",src)
    pr=success("EMIT","JAM",src)
    slope=pj*(pj-pr)/(pj+pr)
    if slope<=0:
        return None
    return (pe-pj+ENERGY_COST["JAM"])/slope

def run_examples():
    cases={
      "weak_social_info_low_mask":Environment(public_info=0,masking=0,contestability=0),
      "high_mask_low_info_one_route":Environment(public_info=0,masking=4,contestability=.2,routes=1),
      "high_mask_low_info_four_routes":Environment(public_info=0,masking=4,contestability=.2,routes=4),
      "high_mask_high_info_four_routes":Environment(public_info=1,masking=4,contestability=.2,routes=4),
      "scarce_prey_low_mask":Environment(public_info=.2,masking=.2,contestability=.9,jam_strength=3),
      "plentiful_prey_low_mask":Environment(public_info=.2,masking=.2,contestability=0,jam_strength=3),
    }
    out={"schema":1,"status":"SYNTHETIC_ONLY_NOT_FITTED","beta":8.0,"scenarios":{}}
    for name,env in cases.items():
        starts=[None,*actions(env)]
        runs=[quantal_response(env,starting_action=s) for s in starts]
        primary=runs[0]
        spread=max(abs(v["probabilities"][a]-primary["probabilities"][a])
                   for v in runs for a in actions(env))
        out["scenarios"][name]={
          "settings":env.__dict__,"logit_response":primary,
          "across_initial_conditions_max_delta":spread,
          "all_starts_converged":all(v["converged"] for v in runs),
          "best_reply_to_EMIT":max(actions(env),key=lambda a:payoff(a,"EMIT",env)),
          "response_to_EMIT":{a:round(payoff(a,"EMIT",env),8) for a in actions(env)}
        }
    return out

if __name__ == "__main__":
    print(json.dumps(run_examples(),indent=2,sort_keys=True))
