"""Recompute v49 from authenticated source-safe moments and score v50 reduced panels.
Usage: python v50_order_audit.py /path/to/downloaded/ZIPs
No raw positions, targets or fitted coefficients exported.
"""
import hashlib, json, sys, zipfile
from pathlib import Path
import numpy as np
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
PINS=['c1c731cee067d7e70f0ca4d322654f042d6329dc86d1c0688e52394814ed17ce','ef1c00831d34e7e952c907d506975b99287c332c09bc4d8f3f38cd1c2f8e90ac','2b8ef237e220e8c1a8e497468797d4306c600238fcc9906c55d59ee491ce5145','5c39d5a72ed95e3a669eccb9111203f2f18248e9dc8310dbb0236ab8539a568c','4c2b355fc4ee5171bfa4eff06c2d96bc547cabde553ce644c58751ab78f4fb05','95497ebcd4eb471cdbaf266f96d4fce4f7cff51b2d4f79db8fe3d7db25012aaf','d07d5778ece12eaa706d524d0a11988b2fa46ec81125c1dc002a74211163ac68','e520f64b66a60e7df93a5392349a6ac81f6dbcb35a59078df939067d0a2f7066','5d32c7d0d6e81dd2c41951ccf2a54db62e9f610e10e776ce643f473c3c0a354b','62cddc5c0b997d14f5190551f5417854c6bc2322b989a97701322e843b2c0a51','d91a89c4cc54764eb0afb77778bc352899fc0365730ba6bc7d939f26586bc2fd','ecdd9ea97801e43cb2a8b1813e0a08377bf51dda9909f6dc899261243cf6df47']
REFPIN='422b42d5d69623b88c17adb0c8be0ea1c01f46562c692f7111e6650ac64fe6cc'
STATES=['ALL','P_low','P_high','V_low','V_high','V_low_P_low','V_low_P_high','V_high_P_low','V_high_P_high']
MODS=['G_geometry','GLOBAL','NEAR_TRUE','FAR_TRUE','NEAR_ROT1','NEAR_STALE_0.2S']
H=['short','delayed']; ids=list(map(str,range(1,13)))
def read(name,digest):
 p=root/name; assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 with zipfile.ZipFile(p) as z:
  assert len(z.namelist())==1; raw=z.read(z.namelist()[0]);return json.loads(raw),hashlib.sha256(raw).hexdigest()
ref,ref_json=read('v49-stickleback.zip',REFPIN)
assert ref['status']=='V49_ORIGINAL_84_TRACKS_12_SHOAL_SCORED' and ref['source_unit_order']==ids
files={}; groups={}; manifest=[]
for g,pin in zip(ids,PINS):
 d,js=read(f'v49-original-shoal-{g}.zip',pin);assert d['status']=='V49_SOURCE_MOMENTS_ONLY' and d['group']==g
 manifest.append({'group':g,'zip_sha256':pin,'json_sha256':js,'file_count':len(d['files'])})
 for n,v in d['files'].items():
  assert n not in files and v['group']==g
  q=ref['source_file_QC'][n]
  for k in ['group','sha256','source_bytes','cohort','counts']:assert q[k]==v[k]
  assert set(v['moments'])==set(STATES)
  files[n]={s:{k:{kk:(vv if kk=='n' else np.asarray(vv,float)) for kk,vv in mm.items()} for k,mm in m.items()} for s,m in v['moments'].items()};groups[n]=g
assert len(files)==84 and set(files)==set(ref['source_file_QC'])
assert np.array_equal(np.sum([v['cohort'] for v in ref['source_file_QC'].values()],0),[3147771,570360,4562880,57968])
# Independent centered normal equations: same fixed ridge penalty on standardized columns.
def fit(ms):
 m={k:sum(x[k] for x in ms) for k in ms[0]};n=m['n'];mx=m['sx']/n;my=m['sy']/n;C=m['sxx']-n*np.outer(mx,mx);D=m['sxy']-n*np.outer(mx,my)
 scale=np.sqrt(np.maximum(np.diag(C)/n,0));scale[scale<=1e-14]=1
 A=C/np.outer(scale,scale);beta=np.linalg.solve((A+A.T)/2+10*np.eye(len(scale)),D/scale[:,None])/scale[:,None]
 return beta,my-mx@beta

def score(m,b,a):
 n=m['n']; mx=m['sx']/n;my=m['sy']/n;C=m['sxx']-n*np.outer(mx,mx);D=m['sxy']-n*np.outer(mx,my);V=m['syy']-n*my**2
 v=V+np.sum(b*(C@b),axis=0)-2*np.sum(b*D,axis=0)+n*(my-(mx@b+a))**2
 assert np.isfinite(v).all() and (v>=0).all();return np.array([v[:2].sum(),v[2:].sum()])/(2*n)
def select(m,c):
 return {'n':m['n'],'sx':m['sx'][c],'sxx':m['sxx'][np.ix_(c,c)],'sxy':m['sxy'][c,:],'sy':m['sy'],'syy':m['syy']}
cols={'B':list(range(14)),'BG':list(range(16)),'BL':list(range(14))+[16,17],'BGL':list(range(18))}
replay=0.;part_error=0.;scores={};new={}
for held in ids:
 tr=sorted((n for n in files if groups[n]!=held),key=lambda x:int(x[:-4]));te=sorted((n for n in files if groups[n]==held),key=lambda x:int(x[:-4]))
 assert len({groups[n] for n in tr})==11
 scores[held]={s:{} for s in STATES};new[held]={s:{} for s in STATES}
 for k in MODS:
  b,a=fit([files[n]['ALL'][k] for n in tr])
  for s in STATES:
   v=np.mean([score(files[n][s][k],b,a) for n in te],0);scores[held][s][k]=v.tolist()
   old=ref['full_MSE'][held][k] if s=='ALL' else ref['source_safe_state_MSE'][held][s][k];old=np.array([old[h] for h in H]);replay=max(replay,float(np.max(np.abs(v-old))));np.testing.assert_allclose(v,old,rtol=1e-7,atol=1e-10)
 for k,c in cols.items():
  b,a=fit([select(files[n]['ALL']['NEAR_TRUE'],c) for n in tr])
  for s in STATES:
   v=np.mean([score(select(files[n][s]['NEAR_TRUE'],c),b,a) for n in te],0);new[held][s][k]=v.tolist()
   if k!='BL':
    old=scores[held][s][{'B':'G_geometry','BG':'GLOBAL','BGL':'NEAR_TRUE'}[k]];np.testing.assert_allclose(v,old,rtol=1e-7,atol=1e-10);part_error=max(part_error,float(np.max(np.abs(v-old))))
ind=np.random.default_rng(20261125).integers(12,size=(10000,12))
def stats(a):
 a=np.asarray(a);loo=[np.delete(a,i,0).mean(0) for i in range(12)];return {'mean':a.mean(0).tolist(),'positive':(a>0).sum(0).tolist(),'negative':(a<0).sum(0).tolist(),'bootstrap95':np.quantile(a[ind].mean(1),[.025,.975],axis=0).tolist(),'delete_one_range':[np.min(loo,0).tolist(),np.max(loo,0).tolist()],'per_shoal':a.tolist()}
def far(s,scale):
 v=np.array([scores[g][s]['NEAR_TRUE'] for g in ids])-np.array([scores[g][s]['FAR_TRUE'] for g in ids]); den={'state_global':np.array([scores[g][s]['GLOBAL'] for g in ids]),'full_global':np.array([scores[g]['ALL']['GLOBAL'] for g in ids]),'state_geometry':np.array([scores[g][s]['G_geometry'] for g in ids]),'native':1}[scale];return v if scale=='native' else 100*v/den
max_interaction=0.
for scale in ['state_global','full_global','state_geometry','native']:
 def K(l,h):return np.diff(far(h,scale)-far(l,scale),axis=1).ravel()
 a=K('P_low','P_high');lo=K('V_low_P_low','V_low_P_high');hi=K('V_high_P_low','V_high_P_high')
 for k,x in [('P_horizon_interaction',a),('P_horizon_low_speed',lo),('P_horizon_high_speed',hi),('P_horizon_speed_equal_weight',(lo+hi)/2),('speed_moderation_of_K',hi-lo)]:
  target=ref['results'][scale][k];np.testing.assert_allclose(x,target['per_file'],rtol=1e-7,atol=1e-8);np.testing.assert_allclose(stats(x)['bootstrap95'],target['descriptive_bootstrap95'],rtol=1e-7,atol=1e-8);max_interaction=max(max_interaction,float(np.max(np.abs(x-target['per_file']))))
out={'status':'V50_SOURCE_SAFE_REDUCED_PANEL_SCORED','scope':'Same original 12 shoals; no new independent replication or causal interpretation; local feature subtracts whole-school mean.','original_v49_zip_sha256':REFPIN,'original_v49_json_sha256':ref_json,'shards':manifest,'v49_replay_max_abs':replay,'reduced_original_panel_replay_max_abs':part_error,'v49_interaction_max_abs':max_interaction,'source_counts':[3147771,570360,4562880,57968],'states':{},'source_safe_four_panel_MSE':new}
for s in STATES:
 B,BG,BL,BGL=np.array([[new[g][s][k] for k in cols] for g in ids]).transpose(1,0,2)
 G0=B-BG;L1=BG-BGL;L0=B-BL;G1=BL-BGL;pg=(G0+G1)/2;pl=(L0+L1)/2
 np.testing.assert_allclose(pg+pl,B-BGL,atol=1e-10,rtol=1e-10);np.testing.assert_allclose(G0-G1,L0-L1,atol=1e-10,rtol=1e-10)
 z={'native_gains':{k:stats(x) for k,x in [('G0',G0),('L1',L1),('L0',L0),('G1',G1),('PhiG',pg),('PhiL',pl),('shared_order_component',G0-G1)]},'baseline_normalized_gains_percent':{k:stats(100*x/B) for k,x in [('G0',G0),('L1',L1),('L0',L0),('G1',G1),('PhiG',pg),('PhiL',pl)]},'ratios':{}}
 for k,num,den in [('global_first',L1,G0),('local_first',L0,G1),('order_averaged',pl,pg)]:
  if not (den>0).all():z['ratios'][k]={'status':'NONPOSITIVE_DENOMINATOR_STOP','positive_denominator_counts':(den>0).sum(0).tolist()};continue
  ratio=100*num.mean(0)/den.mean(0);delta=float(np.diff(ratio)[0]);ud=100*np.diff(num/den,axis=1).ravel();boot=100*np.diff(num[ind].mean(1)/den[ind].mean(1),axis=1).ravel();loo=[float(100*np.diff(np.delete(num,i,0).mean(0)/np.delete(den,i,0).mean(0))[0]) for i in range(12)]
  z['ratios'][k]={'status':'ADMITTED','ratio_percent':ratio.tolist(),'change_pp':delta,'decrease_count':int((ud<0).sum()),'per_shoal_change_pp':ud.tolist(),'bootstrap95_pp':np.quantile(boot,[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)],'negative_direction_gate_pass':bool(delta<0 and (ud<0).sum()>=9 and max(loo)<0)}
 out['states'][s]=z
print('V49 independent replay max abs',replay,'interaction',max_interaction,'v50 replay',part_error)
print('ALL ratios',json.dumps(out['states']['ALL']['ratios'],indent=2))
print('ALL native mean gains',[(k,v['mean']) for k,v in out['states']['ALL']['native_gains'].items()]);print('ALL baseline normalized means',[(k,v['mean']) for k,v in out['states']['ALL']['baseline_normalized_gains_percent'].items()])
(root/'v50_order_audit.json').write_text(json.dumps(out,indent=2)+'\n')
