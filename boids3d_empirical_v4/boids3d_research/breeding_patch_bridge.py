"""A separate YEAR-SCALE demographic/breeding-site gate inspired by mina.

This is NOT Boids motion and it is NOT fitted to the Palmer or Signy penguins.
Population total is conditioned on, as in an abundance-conditional null. A
spatial substrate filter changes patch choice; count noise alone must not be
mistaken for redistribution. Six synthetic monitored components are not actual
georeferenced island polygons.
"""
from dataclasses import dataclass,asdict
from pathlib import Path
import json
import numpy as np

@dataclass(frozen=True)
class PatchDesign:
    population_totals: tuple[int,...]=(900,710,530,360,215,120)
    patch_shares: tuple[float,...]=(.26,.23,.20,.15,.10,.06)
    habitat_pressure: tuple[float,...]=(0.,.25,.50,.70,.9,1.2)
    vulnerability: tuple[float,...]=(0.,.25,.60,1.2,2.4,3.5)
    simulations: int=20
    null_replicates: int=4999


def effective_components(counts):
    p=np.asarray(counts,dtype=float)
    p=p/np.maximum(p.sum(axis=-1,keepdims=True),1e-20)
    return 1/np.maximum(np.sum(p*p,axis=-1),1e-20)


def weights(design,retargeting,heterogeneous):
    p0=np.array(design.patch_shares)
    p0=p0/p0.sum()
    vuln=np.array(design.vulnerability)
    if not heterogeneous:vuln[:]=np.mean(vuln)
    out=[]
    for pressure in design.habitat_pressure:
        quality=np.exp(-pressure*vuln)
        habitat=p0*quality
        habitat/=habitat.sum()
        # A declared mixture of retained natal-site shares and accessible
        # state-targeted patch choices. m=0 is a fixed-share null.
        share=(1-retargeting)*p0+retargeting*habitat
        out.append(share/share.sum())
    return np.stack(out)


def one_world(design,retargeting,heterogeneous,seed):
    rng=np.random.default_rng(seed)
    p0=np.asarray(design.patch_shares,dtype=float);p0/=p0.sum()
    prob=weights(design,retargeting,heterogeneous)
    observed=np.stack([rng.multinomial(N,p) for N,p in zip(design.population_totals,prob)])
    observed_eff=effective_components(observed)
    # Null conditions on the exactly same abundance endpoints and constant
    # shares; it includes the finite-count disappearance of small components.
    b=design.null_replicates
    first=rng.multinomial(design.population_totals[0],p0,size=b)
    last=rng.multinomial(design.population_totals[-1],p0,size=b)
    null_change=effective_components(last)-effective_components(first)
    observed_change=float(observed_eff[-1]-observed_eff[0])
    return {'seed':seed,'n_initial':design.population_totals[0],
            'n_final':design.population_totals[-1],
            'baseline_effective_components':float(observed_eff[0]),
            'final_effective_components':float(observed_eff[-1]),
            'change_effective_components':observed_change,
            'fraction_change_effective_components':float(observed_eff[-1]/observed_eff[0]-1),
            'fixed_share_null_mean_change':float(null_change.mean()),
            'excess_change_vs_null':float(observed_change-null_change.mean()),
            'null_lower_tail_p':float((1+np.sum(null_change<=observed_change))/(b+1)),
            'expected_patch_probabilities':prob.tolist(),
            'observed_patch_counts':observed.tolist()}


ARMS={
 'fixed_share_downsampling':{'retargeting':0.,'heterogeneous':False},
 'homogeneous_habitat_high_mobility':{'retargeting':.85,'heterogeneous':False},
 'heterogeneous_habitat_low_mobility':{'retargeting':.25,'heterogeneous':True},
 'heterogeneous_habitat_high_mobility':{'retargeting':.85,'heterogeneous':True},
}
SEEDS=[17,23,47,71,101,131,151,181,191,211,241,271,307,337,367,397,419,449,479,503]


def main():
    design=PatchDesign()
    report={}
    for arm,kwargs in ARMS.items():
        result=[one_world(design,seed=seed,**kwargs) for seed in SEEDS]
        f=np.array([r['fraction_change_effective_components'] for r in result])
        excess=np.array([r['excess_change_vs_null'] for r in result])
        report[arm]={'results':result,
                     'mean_relative_change':float(f.mean()),
                     'mean_excess_effective_number_change_vs_null':float(excess.mean()),
                     'significant_excess_contraction_count':int(sum(r['null_lower_tail_p']<=.05 for r in result)),
                     'n_runs':len(result)}
        print(arm,'relative',round(f.mean(),3),'excess',round(excess.mean(),3),
              'tail_small',report[arm]['significant_excess_contraction_count'],'/',len(result),flush=True)
    out={'status':'synthetic_annual_patch_scenario_NOT_boids_and_NOT_penguin_fitted',
         'design':asdict(design),'predeclared_SEEDS':SEEDS,'arms':ARMS,'summary':report,
         'ecological_caveats':['Patch shares and vulnerability are invented scenario values',
                               'Annual total N is conditioned on, not predicted from climate or marine food',
                               'Retargeting is an imposed patch-choice mechanism, not emergent from bat Boids',
                               'Simulated monitored components are not validated physical GIS patches']}
    path=Path(__file__).with_name('annual_breeding_patch_bridge.json')
    path.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print('SAVED',path)
    return out

if __name__=='__main__':main()
