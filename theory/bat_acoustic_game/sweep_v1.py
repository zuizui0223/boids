"""Small parameter sweeps for SYNTHETIC sonar game; not bat evidence."""
from __future__ import annotations
from dataclasses import replace
from itertools import product
import json
from bat_acoustic_game import Environment, quantal_response

def audit():
    info_delta=[]
    jam_delta=[]
    failures=[]
    rows=[]
    for quality,cost,beta in product((.75,.85,.95),(.05,.10,.15),(4.,8.,12.)):
        e=Environment(public_info=0,masking=4,contestability=.2,
                      detour_quality=quality,detour_cost=cost)
        lo=quantal_response(e,beta=beta)
        hi=quantal_response(replace(e,public_info=1),beta=beta)
        if not lo["converged"] or not hi["converged"]:
            failures.append(["social_info",quality,cost,beta])
        difference=hi["probabilities"]["DETOUR"]-lo["probabilities"]["DETOUR"]
        info_delta.append(difference)
        rows.append({"family":"social_info","quality":quality,
                     "detour_cost":cost,"beta":beta,"delta_detour":difference})
    for strength,quality,beta in product((1.5,2.,3.),(.75,.85,.95),(4.,8.,12.)):
        e=Environment(public_info=.2,masking=.2,contestability=0,
                      jam_strength=strength,detour_quality=quality)
        lo=quantal_response(e,beta=beta)
        hi=quantal_response(replace(e,contestability=.9),beta=beta)
        if not lo["converged"] or not hi["converged"]:
            failures.append(["contestability",strength,quality,beta])
        difference=hi["probabilities"]["JAM"]-lo["probabilities"]["JAM"]
        jam_delta.append(difference)
        rows.append({"family":"contestability","jam_strength":strength,
                     "quality":quality,"beta":beta,"delta_jam":difference})
    return {"schema":1,"status":"SYNTHETIC_ONLY_NOT_EMPIRICAL",
            "tested_count_each":len(info_delta),
            "social_info_delta_detour":{
                "count_negative":sum(x<0 for x in info_delta),
                "range":[min(info_delta),max(info_delta)],
                "mean":sum(info_delta)/len(info_delta)
            },
            "contestability_delta_jam":{
                "count_positive":sum(x>0 for x in jam_delta),
                "range":[min(jam_delta),max(jam_delta)],
                "mean":sum(jam_delta)/len(jam_delta)
            },
            "nonconverged":failures,"rows":rows}

if __name__=="__main__":
    print(json.dumps(audit(),indent=2,sort_keys=True))
