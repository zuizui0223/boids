"""Post-v43 descriptive control contrasts. Usage: python this.py v43_reaggregation.json output.json"""
import hashlib,json,sys
from pathlib import Path
import numpy as np
p=Path(sys.argv[1]); source=p.read_bytes(); d=json.loads(source)
expected={'tetra':6,'ayu':7,'stickleback':12}
assert set(d['studies'])==set(expected)
rng=np.random.default_rng(20261125)
out={'status':'POSTRESULT_V43_CONTROL_SPECIFICITY_DESCRIPTIVE','source_sha256':hashlib.sha256(source).hexdigest(),'definition':'Each signed loss contrast / mean G_geometry minus GLOBAL loss, or / mean G_geometry loss as sensitivity. Equal heldout unit. Paired 10000 bootstrap, 20261125. Overlapping folds and possible reuse; no causal claims.','studies':{}}
for s,o in d['studies'].items():
 rows=o['source_safe_per_unit_scores']; assert len(rows)==expected[s]
 a=np.array([[[v[h][k] for k in ['G_geometry','GLOBAL','NEAR_TRUE','FAR_TRUE','NEAR_ROT1','NEAR_STALE_0.2S']] for h in ['short','delayed']] for v in rows.values()]); assert np.isfinite(a).all() and (a>0).all()
 b,g,n,f,r,t=a.transpose(2,0,1); D=b-g; assert (D>0).all()
 metrics={'near':g-n,'far':g-f,'rotation':g-r,'stale':g-t,'mapping':r-n,'proximity':f-n,'freshness':t-n}
 inds=rng.integers(len(rows),size=(10000,len(rows))); res={}
 for k,x in metrics.items():
  res[k]={}
  for scale,den in [('global_increment',D),('geometry_baseline',b)]:
   v=100*x.mean(0)/den.mean(0); delta=100*np.diff(x/den,axis=1).ravel(); boot=100*np.diff(x[inds].mean(1)/den[inds].mean(1),axis=1).ravel()
   loo=[float(100*np.diff(np.delete(x,i,0).mean(0)/np.delete(den,i,0).mean(0))[0]) for i in range(len(rows))]
   res[k][scale]={'short_delayed_pct':v.tolist(),'change_pp':float(v[1]-v[0]),'negative_units':int((delta<0).sum()),'positive_units':int((delta>0).sum()),'zero_units':int((delta==0).sum()),'descriptive_paired_bootstrap95_pp':np.quantile(boot,[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)]}
 out['studies'][s]={'n':len(rows),'metrics':res}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
