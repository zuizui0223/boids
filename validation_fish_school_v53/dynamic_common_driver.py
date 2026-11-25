"""Exact population loss on a no-interindividual-edge stationary Gaussian process.
All parameters from frozen v53 grid; no fish data used. Two identical independent
coordinate components would yield the same coordinate-averaged MSE.
"""
import itertools,json,sys
from pathlib import Path
import numpy as np

N=8
# Latent columns A, Z_patch1, Z_patch2, E_0,...,E_7.
W=np.zeros((N,11));W[:,0]=1
for i in range(N):W[i,1+i//4]=1;W[i,3+i]=1
F=W[0];G=W[1:].mean(0);L=W[1:4].mean(0)
A=np.eye(11)[0];Z=np.eye(11)[1]
PANEL={"B":[(F,0),(F,-1)],"BG":[(F,0),(F,-1),(G,0)],"BL":[(F,0),(F,-1),(L,0)],"BGL":[(F,0),(F,-1),(G,0),(L,0)],"oracle":[(F,0),(F,-1),(A,0),(Z,0)],"oracle_social":[(F,0),(F,-1),(A,0),(Z,0),(G,0),(L,0)]}

def evaluate(ra,rz,va,vz):
    r=np.array([ra,rz,rz]+[.2]*N);v=np.array([va,vz,vz]+[1.]*N)
    def cov(x,y):
        wx,tx=x;wy,ty=y
        return float(np.dot(wx*wy,v*r**abs(tx-ty)))
    def loss(x,h):
        y=(F,h);C=np.array([[cov(i,j) for j in x] for i in x]);c=np.array([cov(i,y) for i in x]);return cov(y,y)-float(c@np.linalg.solve(C,c))
    out={}
    for name,h in [('short',1),('delayed',4)]:
        m={k:loss(x,h) for k,x in PANEL.items()};b,g,n,gn=(m[k] for k in ('B','BG','BL','BGL'))
        T=b-gn;ul=g-gn;ug=n-gn;overlap=b-g-n+gn
        assert np.isclose(T,ul+ug+overlap,atol=1e-12,rtol=1e-12)
        assert abs(m['oracle']-m['oracle_social'])<1e-12
        out[name]={'losses':m,'joint_gain':T,'conditional_local_gain':ul,'conditional_global_gain':ug,'signed_overlap':overlap,'conditional_local_share_pct':100*ul/T if T>1e-12 else None,'base_normalized_local_gain_pct':100*ul/b,'oracle_extra_gain':m['oracle']-m['oracle_social']}
    u,v=out['short']['conditional_local_share_pct'],out['delayed']['conditional_local_share_pct']
    return {'rho_global':ra,'rho_local':rz,'variance_global':va,'variance_local':vz,'results':out,'share_change_pp':v-u if u is not None and v is not None else None}

def main():
    rows=[evaluate(*p) for p in itertools.product((.3,.6,.9),(.3,.6,.9),(.5,1.,2.),(.5,1.,2.))]
    assert len(rows)==81
    groups={}
    for label,condition in [('global_slower',lambda r:r['rho_global']>r['rho_local']),('equal_persistence',lambda r:r['rho_global']==r['rho_local']),('global_faster',lambda r:r['rho_global']<r['rho_local'])]:
        subset=[r for r in rows if condition(r)];changes=[r['share_change_pp'] for r in subset if r['share_change_pp'] is not None];a=np.array(changes)
        groups[label]={'cases':len(subset),'admitted':len(a),'decrease':int((a< -1e-10).sum()),'increase':int((a>1e-10).sum()),'no_change':int((abs(a)<=1e-10).sum()),'mean_change_pp':float(a.mean()),'min_change_pp':float(a.min()),'max_change_pp':float(a.max())}
    central=next(r for r in rows if (r['rho_global'],r['rho_local'],r['variance_global'],r['variance_local'])==(.9,.3,1.,1.))
    out={'status':'EXACT_SYNTHETIC_NO_SOCIAL_EDGE_POPULATION_PROJECTION','scope':'Fixed sampling sites, independent latent external processes and individual noise; not physical fish trajectories; no interindividual causal edges. No empirical confirmation or estimate of fish parameters. Exact Gaussian linear prediction with no sampling error.','grid':groups,'central':central,'max_abs_oracle_additional_gain':max(abs(r['results'][h]['oracle_extra_gain']) for r in rows for h in ('short','delayed')),'cases':rows}
    path=Path(sys.argv[1]) if len(sys.argv)>1 else Path('dynamic_common_driver.json');path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
if __name__=='__main__':main()
