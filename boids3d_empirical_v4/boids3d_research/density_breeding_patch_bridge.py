"""Independent density-dependent settlement model for the mina-inspired bridge.

Abundance is externally supplied, not predicted. Annual component counts result
from patch-quality choice subject to within-patch crowding. No bat Boids dynamics.
The fixed-composition null retains initial latent shares, annual expected total,
and Gamma-Poisson count observation noise (CV=.20 by default).
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json
import numpy as np

@dataclass(frozen=True)
class BreedingRules:
    n_patches: int=10
    n_years: int=12
    initial_n: int=600
    final_n: int=60
    patch_quality_sd: float=.80
    capacity_mean: float=90.
    crowding_strength: float=4.
    cv: float=.20
    seed: int=17
    n_null: int=1499


def effective_components(counts):
    p=np.asarray(counts,dtype=float);p=p/max(p.sum(),1)
    return float(1/max((p*p).sum(),1e-9))


def draw_count(rng,expected,cv):
    if cv==0:return rng.poisson(expected)
    latent=rng.gamma(shape=1/cv**2,scale=np.asarray(expected)*cv**2)
    return rng.poisson(latent)


def settlement(rng,N,quality,capacity,strength):
    n=np.zeros(len(quality),dtype=int)
    for _ in range(int(N)):
        score=quality-strength*n/capacity
        p=np.exp(score-score.max());p/=p.sum()
        n[rng.choice(len(n),p=p)]+=1
    return n


def run(r:BreedingRules):
    rng=np.random.default_rng(r.seed)
    quality=rng.normal(size=r.n_patches)*r.patch_quality_sd
    capacities=np.exp(rng.normal(np.log(r.capacity_mean),.25,size=r.n_patches))
    totals=np.rint(np.geomspace(r.initial_n,r.final_n,r.n_years)).astype(int)
    latent=np.stack([settlement(rng,N,quality,capacities,r.crowding_strength) for N in totals])
    observed=np.stack([draw_count(rng,latent[t],r.cv) for t in range(r.n_years)])
    p0=latent[0]/latent[0].sum()
    eff=np.array([effective_components(x) for x in observed])
    obs_delta=float(eff[-1]-eff[0]);null=[]
    for _ in range(r.n_null):
        first=draw_count(rng,totals[0]*p0,r.cv)
        last=draw_count(rng,totals[-1]*p0,r.cv)
        null.append(effective_components(last)-effective_components(first))
    null=np.array(null)
    return {'settings':asdict(r),'annual_expected_totals':totals.tolist(),
            'annual_simulated_latent_counts':latent.tolist(),
            'annual_observed_counts':observed.tolist(),
            'annual_observed_effective_components':eff.tolist(),
            'start_effective_components':float(eff[0]),
            'end_effective_components':float(eff[-1]),
            'percent_change':float((eff[-1]/eff[0]-1)*100),
            'observed_change':obs_delta,
            'null_change_mean':float(null.mean()),
            'null_change_95pct':np.quantile(null,[.025,.975]).tolist(),
            'null_centered_change':float(obs_delta-null.mean()),
            'lower_tail_p':float((1+sum(null<=obs_delta))/(len(null)+1)),
            'null_reps':len(null)}


def main():
    scenarios={'fixed_quality_proportional':0.,'weak_density':.8,
               'strong_density':4.,'very_strong_density':8.}
    seeds=(17,23,47,71,101,131,173,199,229,257)
    rows=[]
    for name,crowding in scenarios.items():
        for seed in seeds:
            metrics=run(BreedingRules(seed=seed,crowding_strength=crowding))
            rows.append({'arm':name,'seed':seed,'metrics':metrics})
    summary={}
    for name in scenarios:
        q=[z['metrics'] for z in rows if z['arm']==name]
        summary[name]={'mean_percent_change':float(np.mean([r['percent_change'] for r in q])),
        'range_percent_change':[float(min(r['percent_change'] for r in q)),float(max(r['percent_change'] for r in q))],
        'mean_null_centered_change':float(np.mean([r['null_centered_change'] for r in q])),
        'stronger_contraction_than_null_p_005_of_10':sum(r['lower_tail_p']<=.05 for r in q),
        'mean_end_effective_components':float(np.mean([r['end_effective_components'] for r in q]))}
    out={'status':'synthetic_separate_colony_demography_no_bat_flight_data',
         'purpose':'mina-inspired fixed-composition null and demographic redistribution',
         'scenarios':scenarios,'seeds':seeds,'summary':summary,'raw':rows,
         'claim_boundary':'Conditioned on simulated annual totals and known-truth initial shares; not matched to mina counts, not real penguin causal inference. No spatial GIS polygons or demography-driven movement dynamics inferred.'}
    dest=Path(__file__).with_name('breeding_patch_bridge.json')
    dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    for name,s in summary.items():print(name,s)
    print('SAVED',dest)

if __name__=='__main__':main()
