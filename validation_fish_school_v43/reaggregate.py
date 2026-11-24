"""Post-v42 descriptive reaggregation of three immutable source-safe artifacts.
Usage: python validation_fish_school_v43/reaggregate.py DIRECTORY
DIRECTORY contains the named downloaded original artifacts; no raw fish XY.
"""
import hashlib,json,zipfile,sys
from pathlib import Path
import numpy as np
ROOT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(".")
PINS={
 'tetra':('v42-tetra.zip','1d98e9ec844d742e9f4ebf8427bdb6004d2dbaf9687719bcf098721275ac866f',14925460476),
 'ayu':('v42-ayu.zip','ab935d966b2bca6c54b56a68b8908004b24f625143ffc6f26bf410310466749b',14923998689),
 'stickleback':('v33b-stickleback.zip','4aa514578f04b850c977070fb49bc0773aec831fed0b7260efb7dc73bdffed7a',14906668781)}
OUT={'status':'POST_V42_DESCRIPTIVE_SOURCE_SCORE_REAGGREGATION','scope':'Same observed recordings and overlapping training folds; no independent confirmation; native study MSE never pooled. Local-vs-global gain ratio is order-dependent and not causal. Bootstrap descriptive only.', 'method':'Equal held-out file or shoal means. B=G_geometry, G=GLOBAL, N=NEAR_TRUE. globalGain=B-G, localGain=G-N. Ratio localGain/globalGain only if globalGain>0. All groups retained, even negative localGain. Paired delayed-short bootstrap 10000 fixed-seed whole-unit draws.','studies':{}}
rng=np.random.default_rng(20261125)
for s,(fn,sha,art) in PINS.items():
 p=ROOT/fn; b=p.read_bytes(); assert hashlib.sha256(b).hexdigest()==sha
 with zipfile.ZipFile(p) as z:
  assert len(z.namelist())==1; raw=z.read(z.namelist()[0]); d=json.loads(raw)
 if s=='stickleback':
  records=d['original_true_shoal_holdout_records']; assert len(records)==12 and d['n_original_EIDC_trial_files']==84
  ids=[r['original_heldout_shoal_ID'] for r in records]; assert set(ids)==set(map(str,range(1,13))) and all(not r['train_and_test_biological_shoal_overlap'] for r in records)
  sc={r['original_heldout_shoal_ID']:r['original_equal_trial_within_shoal_MSE'] for r in records}
 else:
  assert d['status']=='V42_ORIGINAL_SOURCE_SCORED' and d['baseline_v30_replay'] is True and not d['paired_ratio_test_admitted']
  ids=d['source_files']; sc=d['source_file_scores']; assert len(ids)==(6 if s=='tetra' else 7) and set(sc)==set(ids)
 a=np.array([[[sc[i][k][h] for k in ['G_geometry','GLOBAL','NEAR_TRUE','FAR_TRUE','NEAR_ROT1','NEAR_STALE_0.2S']] for h in ['short','delayed']] for i in ids]); assert np.isfinite(a).all() and (a>0).all()
 base,g,near,far,rot,old=a.transpose(2,0,1); G=base-g; L=g-near
 assert (G.mean(axis=0)>0).all()
 ratio=L.mean(axis=0)/G.mean(axis=0); share=L.mean(axis=0)/(G+L).mean(axis=0)
 n=len(ids); ind=rng.integers(n,size=(10000,n)); bootG=G[ind].mean(1); bootL=L[ind].mean(1); mask=(bootG>0).all(1)
 delta=100*((bootL[mask,1]/bootG[mask,1])-(bootL[mask,0]/bootG[mask,0])); loo=[]
 for j in range(n):
  gg=np.delete(G,j,0).mean(0); ll=np.delete(L,j,0).mean(0)
  if (gg>0).all():loo.append(float(100*(ll[1]/gg[1]-ll[0]/gg[0])))
 unit_valid=(G>0).all(1); unit_delta=np.full(n,np.nan); unit_delta[unit_valid]=100*(L[unit_valid,1]/G[unit_valid,1]-L[unit_valid,0]/G[unit_valid,0]); valid=unit_delta[unit_valid]
 signs={'negative':int((valid<0).sum()),'positive':int((valid>0).sum()),'zero':int((valid==0).sum()),'undefined':int((~unit_valid).sum())}
 out={'n_units':n,'unit':'biological shoal' if s=='stickleback' else 'recording file; independent shoal IDs unknown','zip_sha256':sha,'json_sha256':hashlib.sha256(raw).hexdigest(),'artifact_id':art,'global_gain_positive_units':(G>0).sum(0).tolist(),'local_gain_positive_units':(L>0).sum(0).tolist(),'global_mse_gain_percent_of_G_geometry':(100*G.mean(0)/base.mean(0)).tolist(),'local_mse_gain_percent_of_GLOBAL':(100*L.mean(0)/g.mean(0)).tolist(),'local_to_global_gain_percent':(100*ratio).tolist(),'local_share_of_total_gain_percent':(100*share).tolist(),'local_to_global_ratio_change_pp':float(100*(ratio[1]-ratio[0])),'paired_bootstrap95_pp':np.quantile(delta,[.025,.975]).tolist(),'valid_bootstrap_draws':int(mask.sum()),'delete_one_existing_test_unit_range_pp':[min(loo),max(loo)],'delete_one_valid':len(loo),'within_unit_ratio_change_signs':signs,'source_safe_per_unit_scores':{i:{h:{k:float(a[j,t,l]) for l,k in enumerate(['G_geometry','GLOBAL','NEAR_TRUE','FAR_TRUE','NEAR_ROT1','NEAR_STALE_0.2S'])} for t,h in enumerate(['short','delayed'])} for j,i in enumerate(ids)}}
 OUT['studies'][s]=out
 print(s, json.dumps({k:v for k,v in out.items() if k!='source_safe_per_unit_scores'},ensure_ascii=False))
(ROOT/'v43_reaggregation.json').write_text(json.dumps(OUT,indent=2)+'\n')
