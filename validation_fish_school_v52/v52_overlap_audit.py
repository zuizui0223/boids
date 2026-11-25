"""Post-v51 signed predictive commonality decomposition, no new fit.
Usage: python v52_overlap_audit.py DIRECTORY
Input: 3 original v51 ZIPs and exact executed v51 stickleback JSON.
Outputs per-unit signed contrasts and study-equal-unit summaries, not information-theoretic PID.
"""
import hashlib,json,sys,zipfile
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
pins={'tetra':('406a8366fe63172355b73f2fd555b72c81014234c076b1f285ef599604d148a4','d7f02450acfdafc8b18394d1b4ad35d16235067a27abbfe5b9ebefb07aee9a30',6),
'ayu':('2c788da11ebf374b31d61d399a5b0c110a9b06de575210df6c6faab65ace0278','9b0f55edf2751f4ad0fe434ba236014f65232eaa8964ccb1008c10546b50dd0c',7),
'zebrafish':('0001885ee8914f09f3f778fdeeb66be492e860b0fd664b56ab4ba10826f8a714','3f04ffc96eef2dcb72289749a8a6875d99e74ce01f03649abb4d5cd1f0441e7d',8)}
stickpin='2755ea333588f7a1484198c1862df9d098cd46a16d8947a59d61587d803cdb7a'
H=('short','delayed'); states=('ALL','P_low','P_high','V_low','V_high','V_low_P_low','V_low_P_high','V_high_P_low','V_high_P_high')
def sha(b):return hashlib.sha256(b).hexdigest()
def source(s):
 if s=='stickleback':
  p=root/'v51_stickleback_raw_local.json';raw=p.read_bytes();assert sha(raw)==stickpin;j=json.loads(raw)
  assert j['status']=='V51_STICKLEBACK_SECONDARY_REPRESENTATION_SENSITIVITY';ids=j['source_unit_order'];assert ids==list(map(str,range(1,13)))
  rows=j['source_safe_losses'];n=12
  def losses(i,st,e):
   lk,both=('BL','BGL') if e=='residual' else ('BLraw','BGLraw')
   return [rows[i][st][k] for k in ('B','BG',lk,both)]
  provenance={'json_sha256':stickpin,'file':p.name}
 else:
  zp,jp,n=pins[s];p=root/f'v51-{s}.zip';assert sha(p.read_bytes())==zp
  with zipfile.ZipFile(p) as z:
   assert len(z.namelist())==1;raw=z.read(z.namelist()[0]);assert sha(raw)==jp
  j=json.loads(raw);assert j['status']=='V51_ORIGINAL_SOURCE_ORDER_TRANSFER_SCORED' and j['study']==s and j['n']==n
  ids=j['source_unit_order'];rows=j['source_safe_model_losses'];assert len(ids)==n and set(ids)==set(rows)
  def losses(i,st,e):
   lk,both=('BL','NEAR_TRUE') if e=='residual' else ('BLraw','BGLraw')
   return [[rows[i][st][k][h] for h in H] for k in ('G_geometry','GLOBAL',lk,both)]
  provenance={'zip_sha256':zp,'json_sha256':jp,'file':p.name}
 assert all(set(states)==set(rows[i]) for i in ids)
 return j,ids,losses,provenance

def stats(a,ind):
 a=np.asarray(a,float);assert np.isfinite(a).all();n=len(a);boot=a[ind].mean(1);loo=np.array([np.delete(a,i,0).mean(0) for i in range(n)])
 return {'mean':a.mean(0).tolist(),'positive':(a>0).sum(0).tolist(),'negative':(a<0).sum(0).tolist(),'descriptive_bootstrap95':np.quantile(boot,[.025,.975],axis=0).tolist(),'delete_one_range':[loo.min(0).tolist(),loo.max(0).tolist()],'per_unit':a.tolist()}

def share(x,t,ind):
 # signed share of total improvement: strict per-unit denominator gate, no deletion
 n=len(t);valid=(t>0).sum(0);o={'positive_total_gain_units':valid.tolist(),'per_horizon_percent':[float(100*x[:,h].mean()/t[:,h].mean()) if valid[h]==n else None for h in range(2)]}
 if not (t>0).all():o['status']='NONPOSITIVE_TOTAL_GAIN_STOP';return o
 r=100*x.mean(0)/t.mean(0);u=100*x/t;d=np.diff(u,axis=1).ravel();boot=100*np.diff(x[ind].mean(1)/t[ind].mean(1),axis=1).ravel();loo=[float(100*np.diff(np.delete(x,i,0).mean(0)/np.delete(t,i,0).mean(0))[0]) for i in range(n)]
 o.update(status='ADMITTED',change_pp=float(r[1]-r[0]),unit_change=stats(d,ind),ratio_of_means_change_descriptive_bootstrap95_pp=np.quantile(boot,[.025,.975]).tolist(),ratio_of_means_change_delete_one_range_pp=[min(loo),max(loo)],mean_of_unit_shares_percent=u.mean(0).tolist())
 return o

out={'status':'POST_V51_SIGNED_PREDICTIVE_COMMONALITY_NO_REFIT','method':'For B,BG,BL,BGL heldout losses, T=B-BGL, unique global U_G=BL-BGL, unique local U_L=BG-BGL, signed overlap C=B-BG-BL+BGL. T=U_G+U_L+C; PhiG=U_G+C/2, PhiL=U_L+C/2. Signed overlap is not Shannon mutual information or causal redundancy: negative values are possible. Both encodings, all 9 states, all signed scores. B-normalized equal-unit gains and ratio-of-mean total-gain shares separately. No pooling; 10000 paired resamples at seed 20261125 descriptive only; overlapping training folds. T>0 every unit required for shares; no denominator rescue.','studies':{}}
for s in (*pins,'stickleback'):
 j,ids,loss,prov=source(s);n=len(ids);ind=np.random.default_rng(20261125).integers(n,size=(10000,n));study={'source':prov,'unit_order':ids,'n':n,'encodings':{}}
 for e in ('residual','raw_local'):
  result={}
  for st in states:
   B,BG,BL,BGL=np.array([loss(i,st,e) for i in ids]).transpose(1,0,2);assert np.isfinite([B,BG,BL,BGL]).all() and (B>0).all()
   T=B-BGL;ug=BL-BGL;ul=BG-BGL;c=B-BG-BL+BGL;g0=B-BG;l0=B-BL;pg=ug+c/2;pl=ul+c/2
   np.testing.assert_allclose(ug+ul+c,T,atol=1e-10,rtol=1e-10);np.testing.assert_allclose(pg+pl,T,atol=1e-10,rtol=1e-10)
   # Replay previous Phi allocations exactly from stored v51 result, independent formula.
   prev=j['results'][e]['states'][st]['native_gains']
   for key,v in [('PhiG',pg),('PhiL',pl),('G0',g0),('L0',l0)]:np.testing.assert_allclose(v,prev[key]['per_unit'],rtol=1e-8,atol=1e-10)
   vals={'total':T,'unique_global':ug,'unique_local':ul,'signed_overlap':c,'unique_balance':ug-ul,'global_standalone':g0,'local_standalone':l0}
   z={'native':{},'baseline_normalized_percent':{},'total_gain_shares_percent':{}}
   for k,v in vals.items():
    z['native'][k]={'levels':stats(v,ind),'delayed_minus_short':stats(np.diff(v,axis=1).ravel(),ind)}
    w=100*v/B;z['baseline_normalized_percent'][k]={'levels':stats(w,ind),'delayed_minus_short':stats(np.diff(w,axis=1).ravel(),ind)}
    if k!='total':z['total_gain_shares_percent'][k]=share(v,T,ind)
   # Additional exact order-average balance relation: R = (1-balance)/(1+balance) *100, where balance=(UG-UL)/T.
   if (T.mean(0)>0).all() and (pg.mean(0)>0).all():
    bal=(ug-ul).mean(0)/T.mean(0);np.testing.assert_allclose(100*(1-bal)/(1+bal),100*pl.mean(0)/pg.mean(0),rtol=1e-10,atol=1e-10)
   result[st]=z
  study['encodings'][e]=result
 out['studies'][s]=study
 for e,v in study['encodings'].items():
  a=v['ALL'];print('\n',s,e)
  for k in ['unique_global','unique_local','signed_overlap','unique_balance']:
   z=a['total_gain_shares_percent'][k];b=a['baseline_normalized_percent'][k];print(k,'share',z.get('per_horizon_percent'),'change',z.get('change_pp'),'pos/neg',z.get('unit_change',{}).get('positive'),z.get('unit_change',{}).get('negative'),'CI',z.get('ratio_of_means_change_descriptive_bootstrap95_pp'),'base',b['levels']['mean'])
(root/'v52_overlap_audit.json').write_text(json.dumps(out,indent=2)+'\n')
