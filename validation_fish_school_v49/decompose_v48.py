import hashlib,zipfile,json,numpy as np,sys
from pathlib import Path
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
pins={'tetra':'7ac770a4c2425e7569f265fd690c783cb3d500056d2b13859de215f792afff2e','ayu':'5c23516a6b807974bbc3694f48ce0902dedf25783d07e6cbbe3fb46f2de9994f','zebrafish':'96755c92ab081b969af770f727e5a92c05abeb1f2aa43c26f0ff8fdd81e28617'}
out={'status':'POST_V48_COMPONENT_DECOMPOSITION_NO_REFIT','source_scope':'Same v48 source-safe scores; no new model fit. Each component is a predictive contrast, not a causal effect. Positive K_F means relative far advantage in longer forecasts at high polarization.','studies':{}}
for s,pin in pins.items():
 path=root/f'v48-{s}.zip';assert hashlib.sha256(path.read_bytes()).hexdigest()==pin
 with zipfile.ZipFile(path) as z:
  assert len(z.namelist())==1;raw=z.read(z.namelist()[0]);j=json.loads(raw)
 ids=j['source_unit_order'];ss=j['source_safe_state_MSE'];full=j['full_MSE'];n=len(ids);ind=np.random.default_rng(20261125).integers(n,size=(10000,n))
 def stats(x):
  return {'mean':float(x.mean()),'positive':int((x>0).sum()),'negative':int((x<0).sum()),'bootstrap95':np.quantile(x[ind].mean(1),[.025,.975]).tolist(),'delete_one_range':[float(min(np.delete(x,i).mean() for i in range(n))),float(max(np.delete(x,i).mean() for i in range(n)))],'per_unit':x.tolist()}
 data={}
 for scale in ['state_global','full_global','state_geometry','native']:
  def gain(st,h,model):
   m=[ss[i][st] for i in ids];d=np.array([v['GLOBAL'][h]-v[model][h] for v in m]);den={'state_global':np.array([v['GLOBAL'][h] for v in m]),'full_global':np.array([full[i]['GLOBAL'][h] for i in ids]),'state_geometry':np.array([v['G_geometry'][h] for v in m]),'native':1}[scale];return d if scale=='native' else 100*d/den
  def K(lo,hi,model):return gain(hi,'delayed',model)-gain(lo,'delayed',model)-gain(hi,'short',model)+gain(lo,'short',model)
  comps={}
  for label,lo,hi,refkey in [('all','P_low','P_high','P_horizon_interaction'),('low_speed','V_low_P_low','V_low_P_high','P_horizon_low_speed'),('high_speed','V_high_P_low','V_high_P_high','P_horizon_high_speed')]:
   l,a=K(lo,hi,'NEAR_TRUE'),K(lo,hi,'FAR_TRUE');diff=a-l
   np.testing.assert_allclose(diff,j['results'][scale][refkey]['per_file'],rtol=1e-10,atol=1e-10)
   comps[label]={'near_K':stats(l),'far_K':stats(a),'far_minus_near_K':stats(diff)}
  l=np.array(comps['high_speed']['near_K']['per_unit'])-np.array(comps['low_speed']['near_K']['per_unit']);a=np.array(comps['high_speed']['far_K']['per_unit'])-np.array(comps['low_speed']['far_K']['per_unit']);np.testing.assert_allclose(a-l,j['results'][scale]['speed_moderation_of_K']['per_file'],rtol=1e-10,atol=1e-10)
  comps['speed_moderation']={'near_K':stats(l),'far_K':stats(a),'far_minus_near_K':stats(a-l)};data[scale]=comps
 out['studies'][s]={'n':n,'zip_sha256':pin,'json_sha256':hashlib.sha256(raw).hexdigest(),'scales':data}
 for label,v in data['state_global'].items():print(s,label,[(k,round(x['mean'],6),x['positive'],[round(z,6) for z in x['bootstrap95']]) for k,x in v.items()])
(root/'v48_component_decomposition.json').write_text(json.dumps(out,indent=2)+'\n')
