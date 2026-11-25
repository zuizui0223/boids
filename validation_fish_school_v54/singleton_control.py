"""Exact no-social-edge illustration, frozen before evaluation. No empirical data."""
import json
from pathlib import Path
import numpy as np
# Latents A,Z0,Z1,E0,E1,E2 (real); each individual gets its own A,Z,E (pseudo).
W=np.array([[1,1,0,1,0,0],[1,1,0,0,1,0],[1,0,1,0,0,1]],float)
F=np.array([1.,0,0]);G=np.array([-1.,.5,.5]);L=np.array([0.,.5,-.5]);
P={'B':[(F,0),(F,-1)],'GLOBAL':[(F,0),(F,-1),(G,0)],'NEAR':[(F,0),(F,-1),(G,0),(L,0)],'ROT':[(F,0),(F,-1),(G,0),(L,0)]}
def covfactory(var,independent):
 r=np.array([.8,.5,.5,.2,.2,.2]);v=np.array([1.,var,var,1.,1.,1.])
 def cov(x,y):
  a,t=x;b,s=y;lag=abs(t-s)
  C=(np.eye(3)*(.8**lag+var*.5**lag+.2**lag)) if independent else (W*(v*r**lag))@W.T
  return float(a@C@b)
 return cov

def moments(cov,k,h):
 x=P[k];y=(F,h);C=np.array([[cov(i,j) for j in x] for i in x]);c=np.array([cov(i,y) for i in x]);vv=cov(y,y)
 if k=='ROT':
  C[-1,:-1]=0;C[:-1,-1]=0;c[-1]=0
 return C,c,vv

def eval_case(var):
 cr,cp=covfactory(var,False),covfactory(var,True);out={}
 for label,h in [('short',1),('delayed',4)]:
  losses={'real':{},'independent_single':{}}
  for k in P:
   C,c,v=moments(cr,k,h);b=np.linalg.solve(C,c)
   for name,co in [('real',cr),('independent_single',cp)]:
    D,d,w=moments(co,k,h);losses[name][k]=float(w-2*b@d+b@D@b)
  metrics={name:100*(m['ROT']-m['NEAR'])/m['GLOBAL'] for name,m in losses.items()}
  # True current A and focal Z plus current focal velocity determine latent E;
  # independent innovation variance is exact oracle MSE, unchanged by extra velocities.
  oracle_loss=1*(1-.8**(2*h))+var*(1-.5**(2*h))+1*(1-.2**(2*h))
  out[label]={'losses':losses,'assignment_advantage_percent':metrics,'oracle_loss':oracle_loss,'oracle_extra_neighbor_gain':0.0}
 return out
cases={k:eval_case(v) for k,v in [('X',.5),('Y',2.)]}
result={'status':'SYNTHETIC_NO_SOCIAL_EDGE_ONLY','scope':'Fixed sites and external fields; X/Y differ in patch variance only, not actual illumination. Pseudo groups independent and scored by real-trained population coefficients. No causal edges.','cases':cases,'condition_Y_minus_X_assignment_pp':{h:{k:cases['Y'][h]['assignment_advantage_percent'][k]-cases['X'][h]['assignment_advantage_percent'][k] for k in ('real','independent_single')} for h in ('short','delayed')}}
path=Path(__file__).with_name('singleton_control.json');path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2))
