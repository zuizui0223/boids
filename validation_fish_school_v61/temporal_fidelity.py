"""v61 temporal fidelity and 30s rollout; exact v60 score replay first."""
import argparse,hashlib,itertools,json,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v58 import selective_rules as v58
from validation_fish_school_v59 import closed_loop_rollout as v59
from validation_fish_school_v60 import residual_dependence as v60
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge

PINS={
 'Bright':('f6fdc48a02705635ccb2b12303ae3e0c84a6b5685bba9ff4a42d9af41e335ac9','2017fdade0cd6d075d64acf0efbd423a4b4efb711e626abd519b3aa8a73c431c'),
 'Dark':('1e7a99bb8f74777e11af03d7a17149b202d96eea9084aad90af89c7f18f20e19','3bc74db14eddd51ab8bd9dfcb62b8a3a39e77e34d706875eeaff4587ac3c419f')}
LIGHTS=('Bright','Dark');MASKS=(0,3);LONG_REGS=('light_group_centered','light_block_centered')
REGS=v60.REGIMES;RTOL=1e-7;ATOL=1e-10
def sha(b):return hashlib.sha256(b).hexdigest()
def ref(path,light):
    zp,jp=PINS[light];assert sha(path.read_bytes())==zp
    with zipfile.ZipFile(path) as z:
        assert z.namelist()==[light+'.json'];raw=z.read(light+'.json')
    assert sha(raw)==jp
    j=json.loads(raw)
    assert j['status']=='V60_ORIGINAL_RESIDUAL_DEPENDENCE_SCORED' and j['light']==light and j['n_safety_stops']==0
    return j

def rms_lag(a,lag,vector=False):
    diff=a[lag:]-a[:-lag]
    if vector:return float(np.sqrt(np.mean(np.sum(diff*diff,axis=-1))))
    return np.sqrt(np.mean(diff*diff,axis=tuple(range(diff.ndim-1))))
def dynamic(d,o,c,oc,scale):
    pp=np.array([rms_lag(d,l) for l in (1,5)]);oo=np.array([rms_lag(o,l) for l in (1,5)])
    e=(pp-oo)/scale
    x={'simulated_lag_rms':pp.tolist(),'observed_lag_rms':oo.tolist(),'standardized_lag_errors':e.tolist(),
       'temporal_loss':float(np.mean(e*e)),'centroid_displacement_rms_native':{'simulated':[rms_lag(c,l,True) for l in (1,5)],'observed':[rms_lag(oc,l,True) for l in (1,5)]}}
    if len(d)>25:
        x['lag_25_secondary']={'simulated_rms':rms_lag(d,25).tolist(),'observed_rms':rms_lag(o,25).tolist(),
          'centroid_displacement_rms_native':[rms_lag(c,25,True),rms_lag(oc,25,True)]}
    return x
def fixtures():
    v59.fixture()
    x=np.arange(50.)[:,None,None,None]*np.ones((1,3,8,3))
    y=np.arange(50.)[:,None,None]*np.ones((1,3,3))
    c=x[...,:2];oc=y[...,:2]
    z=dynamic(x,y,c,oc,np.ones(3))
    np.testing.assert_allclose(z['simulated_lag_rms'],[[1]*3,[5]*3],atol=1e-12)
    assert z['temporal_loss']==0
    # Rearrangement leaves quantiles fixed but not trajectory dynamics.
    rev=np.r_[np.arange(0,50,2),np.arange(49,0,-2)]
    np.testing.assert_array_equal(np.sort(x[rev],axis=0),x)
    assert dynamic(x[rev],y,c[rev],oc,np.ones(3))['temporal_loss']>0
    print('temporal loss and identical-marginal ordering fixture PASS',flush=True)
def long_starts(p,t):
    s=np.arange(66,len(p)-900,900);s=s[np.isin(s,t)]
    ix=s[:,None]+6*np.arange(-2,151)[None,:]
    return s[np.isfinite(p[ix]).all((1,2,3))]
def evaluate(p,starts,coef,scale,lo,hi,noise,horizons):
    # Same arithmetic/order as v60 for all existing outputs.
    n=len(starts);reps=8
    assert noise.shape==(max(horizons),n,reps,3,2)
    older=np.repeat(p[starts-12],reps,axis=0);prev=np.repeat(p[starts-6],reps,axis=0);now=np.repeat(p[starts],reps,axis=0)
    total=np.zeros((reps,3));obs=np.zeros(3);poserr=np.zeros(reps);outside=np.zeros(reps);obsout=0.
    pred_rows=[];obs_rows=[];cent=[];ocent=[];result={}
    for k in range(1,max(horizons)+1):
        x=v59.features(now,prev,older)
        v=x@coef[:-1]+coef[-1]+noise[k-1].reshape(n*reps,3,2)
        new=now+.2*v
        if not np.isfinite(new).all() or not np.isfinite(v).all() or max(np.abs(new).max(),np.abs(v).max())>1e9:
            return {'status':'DIVERGED_SAFETY_STOP','failed_step':k,'horizons':result}
        real=p[starts+6*k];realv=(real-p[starts+6*(k-1)])/.2
        d=v59.descriptors(new,v).reshape(n,reps,3);o=v59.descriptors(real,realv)
        total+=d.mean(0);obs+=o.mean(0);pred_rows.append(d);obs_rows.append(o)
        cent.append(new.reshape(n,reps,3,2).mean(2));ocent.append(real.mean(1))
        poserr+=np.linalg.norm(new.reshape(n,reps,3,2)-real[:,None,:,:],axis=-1).mean((0,2))
        outside+=(((new<lo)|(new>hi)).any(-1)).reshape(n,reps,3).mean((0,2))
        obsout+=float(((real<lo)|(real>hi)).any(-1).mean())
        older,prev,now=prev,now,new
        if k in horizons:
            mean=total.mean(0)/k;ob=obs/k;err=(mean-ob)/scale
            qp=np.quantile(np.concatenate([r.reshape(-1,3) for r in pred_rows]),v60.QUANTILES,axis=0)
            qo=np.quantile(np.concatenate(obs_rows),v60.QUANTILES,axis=0);qe=(qp-qo)/scale
            result[str(k)]={'simulated_mean':mean.tolist(),'observed_mean':ob.tolist(),'standardized_signed_error':err.tolist(),
              'loss':float(np.mean(err**2)),'replicate_descriptor_means':(total/k).tolist(),'mean_position_error_native':float(poserr.mean()/k),
              'outside_training_rectangle_fraction':float(outside.mean()/k),'observed_outside_training_rectangle_fraction':obsout/k,
              'simulated_quantiles':qp.tolist(),'observed_quantiles':qo.tolist(),'standardized_quantile_errors':qe.tolist(),'quantile_loss':float(np.mean(qe**2)),
              **dynamic(np.array(pred_rows),np.array(obs_rows),np.array(cent),np.array(ocent),scale)}
    return {'status':'COMPLETE','horizons':result}
def summarize(records,ids,regimes,horizons):
    out={}
    fields=('loss','quantile_loss','temporal_loss','outside_training_rectangle_fraction','observed_outside_training_rectangle_fraction',
            'mean_position_error_native','simulated_mean','observed_mean','simulated_lag_rms','observed_lag_rms','standardized_lag_errors','simulated_quantiles','observed_quantiles')
    for h in map(str,horizons):
        z={}
        for reg in regimes:
            g={}
            for mask in map(str,MASKS):
                bad=[i for i in ids if any(r[mask][reg]['status']!='COMPLETE' for r in records[i])]
                if bad:g[mask]={'status':'STOP','failed_trials':bad};continue
                rows=[[r[mask][reg]['horizons'][h] for r in records[i]] for i in ids]
                d={'status':'ADMITTED'}
                for k in fields:
                    a=np.array([np.mean([q[k] for q in rr],axis=0) for rr in rows]);d[k]={'equal_trial_mean':a.mean(0).tolist(),'per_trial':a.tolist()}
                d['excess_rectangle_fraction']=v58.stat(np.array(d['outside_training_rectangle_fraction']['per_trial'])-d['observed_outside_training_rectangle_fraction']['per_trial'])
                g[mask]=d
            if g['0']['status']==g['3']['status']=='ADMITTED':
                for k in ('loss','quantile_loss','temporal_loss'):
                    d=v58.stat(np.array(g['0'][k]['per_trial'])-g['3'][k]['per_trial']);d['direction_gate_pass']=v58.gate(d,len(ids));g['3'][k+'_improvement_vs_M0']=d
            z[reg]=g
        c={}
        for m in map(str,MASKS):
            a=z['light_group_centered'][m];b=z['light_block_centered'][m]
            if a['status']==b['status']=='ADMITTED':
                c[m]={}
                for k in ('loss','quantile_loss','temporal_loss','outside_training_rectangle_fraction'):
                    d=v58.stat(np.array(a[k]['per_trial'])-b[k]['per_trial']);d['direction_gate_pass']=v58.gate(d,len(ids));c[m][k]=d
            else:c[m]={'status':'STOP'}
        z['group_minus_block']=c;out[h]=z
    return out
def run(a,out):
    fixtures();prior=v60.ref(a.v59);old=ref(a.v60,a.light);j55=v56.ref(a.v55);qc={}
    data=v55.admit(a.source,v55.reference(a.diagnostic),qc);assert qc==j55['source_QC']
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS};assert ids==prior['trial_order'] and ids[a.light]==old['trial_order']
    allids=ids['Bright']+ids['Dark'];lights={i:l for l in LIGHTS for i in ids[l]}
    rec={};orig={};times={}
    for l in LIGHTS:
        for i,(f,p) in data['Triads-'+l].items():
            X,Y,t=v56.native_panels(f,p,i);x=X['base']['NEAR']
            assert len(t)==j55['windows']['full_archive']['window_group_times'][i]
            np.testing.assert_array_equal(v59.features(p[t],p[t-6],p[t-12]).reshape(-1,18),x)
            s=v59.starts_for(p,t);assert len(s)==prior['n_starts_by_trial'][i]
            z=v59.descriptors(p[t],(p[t]-p[t-6])/.2)
            rec[i]={'p':p,'x':x,'y':Y,'z':z,'starts':s,'long_starts':long_starts(p,t)}
            orig[i]=file_moment(x,Y);times[i]=t
    combos=[b+d for b in itertools.combinations(ids['Bright'],8) for d in itertools.combinations(ids['Dark'],8)]
    selected={i:sorted([tr for tr in combos if i not in tr],key=lambda tr:sha(('v59|'+i+'|'+'|'.join(tr)).encode()))[:3] for i in allids}
    for i in allids:assert [list(tr) for tr in selected[i]]==[r['training_ids'] for r in prior['source_safe_rollout_scores'][i]]
    result={};longresult={};replay=0.;checks=0;stops=0
    for i in ids[a.light]:
        r=rec[i];l=lights[i];result[i]=[];longresult[i]=[]
        for j,tr in enumerate(selected[i]):
            assert i not in tr and len(tr)==16
            oldr=old['source_safe_scores'][i][j];assert list(tr)==oldr['training_ids'] and len(r['starts'])==oldr['n_starts']
            fit={}
            for mask in MASKS:
                T={l:v58.transform_matrix(18,1 if l=='Bright' else -1,mask) for l in LIGHTS}
                m=[v58.transform(orig[q],T[lights[q]]) for q in tr];beta,bias=train_only_standardized_ridge(sum_moments(m))
                fit[mask]={l:(T[l]@beta+np.vstack((np.zeros((18,4)),bias[None,:])))[:,:2] for l in LIGHTS}
            res={q:(rec[q]['y'][:,:2]-(rec[q]['x']@fit[0][lights[q]][:-1]+fit[0][lights[q]][-1])).reshape(-1,3,2) for q in tr}
            noises,noiseqc=v60.make_noises(res,times,tr,lights,l,i,len(r['starts']))
            xy=np.concatenate([rec[q]['x'][:,:2] for q in tr]);lo=xy.min(0);hi=xy.max(0)
            scale=np.concatenate([rec[q]['z'] for q in tr]).std(0)
            np.testing.assert_allclose(scale,oldr['training_descriptor_sd'],rtol=RTOL,atol=ATOL)
            assert noiseqc['pooled_vector_count']==oldr['noise_qc']['pooled_vector_count']
            row={}
            for mask in MASKS:
                row[str(mask)]={}
                for reg in REGS:
                    z=evaluate(r['p'],r['starts'],fit[mask][l],scale,lo,hi,noises[reg],(10,25,50))
                    assert z['status']=='COMPLETE'
                    before=oldr['masks'][str(mask)][reg]['horizons']
                    for h,v in z['horizons'].items():
                        for k,y in before[h].items():
                            x=np.asarray(v[k],float);y=np.asarray(y,float)
                            np.testing.assert_allclose(x,y,rtol=RTOL,atol=ATOL)
                            replay=max(replay,float(np.max(np.abs(x-y))));checks+=1
                    row[str(mask)][reg]=z
            result[i].append(row)
            row={}
            s=r['long_starts']
            if len(s)<15:
                row={str(m):{reg:{'status':'LONG_SUPPORT_STOP','n_starts':len(s)} for reg in LONG_REGS} for m in MASKS}
            else:
                chunks=[v60.make_noises(res,times,tr,lights,l,'v61-long|'+i+'|'+str(k),len(s))[0] for k in range(3)]
                longnoise={reg:np.concatenate([c[reg] for c in chunks],axis=0) for reg in LONG_REGS}
                for mask in MASKS:
                    row[str(mask)]={}
                    for reg in LONG_REGS:
                        z=evaluate(r['p'],s,fit[mask][l],scale,lo,hi,longnoise[reg],(50,150))
                        stops+=z['status']!='COMPLETE';row[str(mask)][reg]=z
            longresult[i].append(row)
        print('v61 temporal replay and long support evaluated',a.light,i,len(r['starts']),len(r['long_starts']),flush=True)
    shortsum=summarize(result,ids[a.light],REGS,(10,25,50))
    longsum=summarize(longresult,ids[a.light],LONG_REGS,(50,150))
    p=shortsum['50']['group_minus_block']['3']['temporal_loss']
    verdict='SECONDARY_BRIGHT' if a.light=='Bright' else ('BLOCK_TEMPORAL_FIDELITY_SUPPORTED_DESCRIPTIVE' if p['direction_gate_pass'] else 'BLOCK_TEMPORAL_FIDELITY_NOT_SUPPORTED')
    out.update(status='V61_ORIGINAL_TEMPORAL_FIDELITY_SCORED',light=a.light,scientific_status=verdict,
       prior_v60_scientific_status=old['scientific_status'],prior_v60_zip_sha256=PINS[a.light][0],prior_v60_json_sha256=PINS[a.light][1],
       source_58_reauthenticated=True,trial_order=ids[a.light],replay_checks=checks,max_v60_replay_abs=replay,long_safety_stops=stops,
       short_starts={i:len(rec[i]['starts']) for i in ids[a.light]},long_starts={i:len(rec[i]['long_starts']) for i in ids[a.light]},
       short_summary=shortsum,long_summary=longsum,source_safe_short_scores=result,source_safe_long_scores=longresult,raw_positions_or_coefficients_exported=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--light',choices=LIGHTS,required=True)
    for k in ('source','diagnostic','v55','v59','v60','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    sm={k:v for k,v in o.items() if k not in ('short_summary','long_summary','source_safe_short_scores','source_safe_long_scores','trial_order')}
    if 'short_summary' in o:
        for key,h in [('short_summary','50'),('long_summary','150')]:
            sm[key]={reg:{m:{k:v[k]['equal_trial_mean'] for k in ('loss','quantile_loss','temporal_loss','outside_training_rectangle_fraction','observed_outside_training_rectangle_fraction') if k in v} for m,v in g.items()} for reg,g in o[key][h].items() if reg!='group_minus_block'}
        sm['primary']=o['short_summary']['50']['group_minus_block']['3']['temporal_loss']
    print(json.dumps(sm,sort_keys=True),flush=True)
    if o['status']!='V61_ORIGINAL_TEMPORAL_FIDELITY_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
