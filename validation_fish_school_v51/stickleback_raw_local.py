"""V51 secondary stickleback representation sensitivity; no new raw data.
Usage: python script.py /path/to/13/ZIPs /path/to/v50/order_audit.py
"""
import contextlib, hashlib, io, json, runpy, sys
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]); script=Path(sys.argv[2]); assert hashlib.sha256(script.read_bytes()).hexdigest()=='da97d9252ac7841e7305db7ccb66bf568ea1d5b991f737186a2d7aca18fe41f8'
sys.argv=[str(script),str(root)]
with contextlib.redirect_stdout(io.StringIO()): d=runpy.run_path(str(script))
files,groups,ids,states,fit,score,new=(d[k] for k in ('files','groups','ids','STATES','fit','score','new'))
I=np.eye(18); raw=I[:,14:16]+I[:,16:18]
trans={'BLraw':np.column_stack((I[:,:14],raw)),'BGLraw':np.column_stack((I[:,:16],raw))}
def transform(m,T):
 return {'n':m['n'],'sx':T.T@m['sx'],'sxx':T.T@m['sxx']@T,'sxy':T.T@m['sxy'],'sy':m['sy'],'syy':m['syy']}
for held in ids:
 train=sorted([n for n in files if groups[n]!=held],key=lambda x:int(x[:-4]));test=sorted([n for n in files if groups[n]==held],key=lambda x:int(x[:-4]));assert len({groups[n] for n in train})==11
 for k,T in trans.items():
  B,b=fit([transform(files[n]['ALL']['NEAR_TRUE'],T) for n in train])
  for s in states:new[held][s][k]=np.mean([score(transform(files[n][s]['NEAR_TRUE'],T),B,b) for n in test],0).tolist()
ind=np.random.default_rng(20261125).integers(12,size=(10000,12))
def stats(a):
 a=np.asarray(a);loo=[np.delete(a,i,0).mean(0) for i in range(12)];return {'mean':a.mean(0).tolist(),'positive':(a>0).sum(0).tolist(),'negative':(a<0).sum(0).tolist(),'bootstrap95':np.quantile(a[ind].mean(1),[.025,.975],axis=0).tolist(),'delete_one_range':[np.min(loo,0).tolist(),np.max(loo,0).tolist()],'per_unit':a.tolist()}
def ratios(num,den):
 n=len(num); pos=(den>0).sum(0).tolist();means=[float(100*num[:,h].mean()/den[:,h].mean()) if pos[h]==n else None for h in range(2)]
 if not (den>0).all():return {'status':'NONPOSITIVE_DENOMINATOR_STOP','positive_denominator_counts':pos,'ratio_percent':means}
 r=100*num.mean(0)/den.mean(0);delta=float(np.diff(r)[0]);ud=100*np.diff(num/den,axis=1).ravel();boot=100*np.diff(num[ind].mean(1)/den[ind].mean(1),axis=1).ravel();loo=[float(100*np.diff(np.delete(num,i,0).mean(0)/np.delete(den,i,0).mean(0))[0]) for i in range(n)]
 return {'status':'ADMITTED','ratio_percent':r.tolist(),'change_pp':delta,'decrease_count':int((ud<0).sum()),'per_unit_change_pp':ud.tolist(),'bootstrap95_pp':np.quantile(boot,[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)],'negative_direction_gate_pass':bool(delta<0 and (ud<0).sum()>=9 and max(loo)<0)}
def pol(lo,hi):
 nl,dl=lo;nh,dh=hi;o={}
 for h,name in enumerate(('short','delayed')):
  a,b,c,e=nl[:,h],dl[:,h],nh[:,h],dh[:,h];pos=[int((b>0).sum()),int((e>0).sum())]
  if pos!=[12,12]:o[name]={'status':'NONPOSITIVE_DENOMINATOR_STOP','positive_denominator_counts_low_high':pos};continue
  def dif(i):return 100*(a[i].mean(-1)/b[i].mean(-1)-c[i].mean(-1)/e[i].mean(-1))
  v=float(dif(np.arange(12)));u=100*(a/b-c/e);loo=[float(dif(np.delete(np.arange(12),i))) for i in range(12)]
  o[name]={'status':'ADMITTED','low_minus_high_pp':v,'positive_units':int((u>0).sum()),'bootstrap95_pp':np.quantile(dif(ind),[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)],'positive_direction_gate_pass':bool(v>0 and (u>0).sum()>=9 and min(loo)>0),'per_unit_pp':u.tolist()}
 return o
out={'status':'V51_STICKLEBACK_SECONDARY_REPRESENTATION_SENSITIVITY','scope':'Existing v49 moments, same 12 shoals, all v50 source and score gates rerun. Raw near velocity block excludes whole-group mean from that block alone; baseline still contains group geometry. No causal allocation.','v50_script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'source_safe_losses':new,'source_unit_order':ids,'results':{}}
for encoding,(local,both) in {'residual':('BL','BGL'),'raw_local':('BLraw','BGLraw')}.items():
 z={};ph={}
 for s in states:
  B,BG,BL,BGL=np.array([[new[g][s][k] for k in ('B','BG',local,both)] for g in ids]).transpose(1,0,2);G0=B-BG;L1=BG-BGL;L0=B-BL;G1=BL-BGL;pg=(G0+G1)/2;pl=(L0+L1)/2
  np.testing.assert_allclose(pg+pl,B-BGL,rtol=1e-10,atol=1e-10);np.testing.assert_allclose(G0-G1,L0-L1,rtol=1e-10,atol=1e-10)
  g={'G0':G0,'L1':L1,'L0':L0,'G1':G1,'PhiG':pg,'PhiL':pl,'shared_order_component':G0-G1};ph[s]=(pl,pg)
  z[s]={'native_gains':{k:stats(v) for k,v in g.items()},'baseline_normalized_gains_percent':{k:stats(100*v/B) for k,v in g.items()},'ratios':{k:ratios(a,b) for k,a,b in [('global_first',L1,G0),('local_first',L0,G1),('order_averaged',pl,pg)]}}
 c={k:pol(ph[l],ph[h]) for k,l,h in [('all_speed','P_low','P_high'),('low_speed','V_low_P_low','V_low_P_high'),('high_speed','V_high_P_low','V_high_P_high')]};out['results'][encoding]={'states':z,'polarization_low_minus_high':c}
 print(encoding,json.dumps({'all':z['ALL']['ratios']['order_averaged'],'P_low':z['P_low']['ratios']['order_averaged'],'P_high':z['P_high']['ratios']['order_averaged'],'Pcontrast':c['all_speed']},ensure_ascii=False))
(root/'v51_stickleback_raw_local.json').write_text(json.dumps(out,indent=2)+'\n')
