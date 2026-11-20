"""v10c uncertainty sensitivity for genuinely observed 3D fish-sound localizations.

AFTER v10b results (explicit exploratory stress test). All six authenticated
original OSF source files, same fixed time-adjacent pairs. Independent
within-span uniform jitter is a scenario, not an author's posterior/likelihood.
"""
import json,math,random,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_fish_chorus_v10"))
from osf_time_space import FILE_IDS,get_original,parse_events,pair_indices,meddist,MIN_PAIRS,MIN_ROWS
JITTER_DRAWS=500
PERM_PER_DRAW=299
SEED=20261121
def simulate_uniform_positions(events,rng):
    vals=[]
    for z in events:
        xyz=z["xyz"]
        span=z["uncert"]
        if not all(u is not None and u>=0 for u in span):
            raise ValueError("SOURCE_MISSING_3D_SPAN_STOP")
        vals.append(tuple(c+rng.uniform(-u/2.,u/2.) for c,u in zip(xyz,span)))
    return vals
def evaluate(events,seed):
    pairs=pair_indices(events)
    if len(events)<MIN_ROWS or len(pairs)<MIN_PAIRS:
        return {"status":"STOP_FEW_EVENTS_OR_120S_PAIRS",
                "source_n_events":len(events),"source_adjacent_pairs":len(pairs)}
    if any(not all(u is not None for u in z["uncert"]) for z in events):
        return {"status":"STOP_MISSING_SPAN",
                "source_n_events":len(events),"source_adjacent_pairs":len(pairs)}
    rng=random.Random(seed)
    observed_nominal=meddist([z["xyz"] for z in events],pairs)
    widths=np.array([z["uncert"] for z in events],float)
    nominal_ratio=[]
    nominal_perm=[]
    # Make each independent event coordinate uncertain in an explicit
    # rectangular interval with half-width = half the reported axis span.
    # This is an ASSUMED scenario, not credible posterior sampling.
    per_draw=[]
    for rep in range(JITTER_DRAWS):
        xyz=simulate_uniform_positions(events,rng)
        obs=meddist(xyz,pairs)
        nulls=[]
        for i in range(PERM_PER_DRAW):
            shuffled=list(xyz);rng.shuffle(shuffled)
            nulls.append(meddist(shuffled,pairs))
        expected=float(np.mean(nulls))
        rank=(1+sum(x<=obs for x in nulls))/(PERM_PER_DRAW+1)
        per_draw.append({"ratio":obs/expected if expected>0 else np.nan,
                         "empirical_tail_p":rank,"observed":obs,"null_expected":expected})
    ratios=np.array([x["ratio"] for x in per_draw],float)
    pvals=np.array([x["empirical_tail_p"] for x in per_draw],float)
    d0=np.array([x["observed"] for x in per_draw],float)
    if not np.isfinite(ratios).all():
        return {"status":"STOP_INVALID_JITTER_RATIO"}
    return {
       "status":"EXPLORATORY_UNCERTAINTY_SCENARIO_RUN",
       "n_original_events":len(events),"n_adjacent_pairs":len(pairs),
       "original_unjittered_median_consecutive_distance_m":observed_nominal,
       "median_3d_reported_span_m":float(np.median(np.linalg.norm(widths,axis=1))),
       "distance_over_span_ratio_nominal":float(observed_nominal/np.median(np.linalg.norm(widths,axis=1))),
       "independent_jitter_scenario":"each original sound event xyz independently Uniform(center +/- reported span / 2), no exchangeability or physical posterior implied",
       "n_simulated_location_scenarios":JITTER_DRAWS,"n_null_shuffles_per_scenario":PERM_PER_DRAW,
       "ratio_observed_to_time_shuffle_median_5_50_95":np.quantile(ratios,[.05,.5,.95]).tolist(),
       "fraction_scenarios_with_shorter_observed_than_null":float((ratios<1).mean()),
       "fraction_scenarios_with_conditional_tail_p_at_most_0p05":float((pvals<=.05).mean()),
       "median_conditional_tail_p":float(np.median(pvals)),
       "jittered_observed_distance_median_5_50_95":np.quantile(d0,[.05,.5,.95]).tolist()
    }
def run():
    out={"version":"v10c_original_OSF_3D_sound_localization_uncertainty_scenarios",
         "status":"AUTHENTIC_SOURCE_WITH_JITTER_SENSITIVITY",
         "author_posterior_used":False,"exploratory_post_v10b":True,
         "individual_fish_identity":"NOT_OBSERVED",
         "results":[]}
    for k,(fid,name) in enumerate(FILE_IDS.items()):
        try:
            # Retry only transient network read timeouts. Keep source SHA and
            # all numeric sensitivity settings identical; never retry digest drift.
            last_error=None
            for attempt in range(3):
                try:
                    raw=get_original(fid)
                    last_error=None
                    break
                except (OSError,TimeoutError) as exc:
                    last_error=exc
            if last_error is not None:
                raise last_error
            events,bad=parse_events(raw)
            res=evaluate(events,SEED+k*100000)
            out["results"].append({"array":name,"source_n_valid":len(events),
              "source_bad_events":bad,"uncertainty_sensitivity":res})
        except (ValueError,OSError,TypeError) as exc:
            out["results"].append({"array":name,"status":"SOURCE_OR_UNCERTAINTY_STOP",
                                   "reason":str(exc)})
    out["n_original_sources_admitted"]=sum("source_valid" in x for x in out["results"])
    out["status"]="ALL_SIX_SOURCE_REPLAY_AND_JITTER_SENSITIVITY" if out["n_original_sources_admitted"]==6 else "PARTIAL_SOURCE_TIMEOUT_STOP"
    return out
if __name__=="__main__":
    o=run()
    p=Path("validation_fish_chorus_v10/results/osf_location_jitter_sensitivity.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":o["status"],"summary":[{"array":r["array"],
        "source_valid":r.get("source_n_valid"),
        "sensitivity":r.get("uncertainty_sensitivity"),"error":r.get("reason")}
        for r in o["results"]]}))
