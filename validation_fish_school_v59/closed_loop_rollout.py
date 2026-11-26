"""v59 heldout free-running 0.2 s group dynamics, frozen v58 rules.
Only aggregate statistics and scores leave the runner.
"""
import argparse,hashlib,itertools,json,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v54 import illumination_triads as v54
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v58 import selective_rules as v58
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
PIN='0114ab958c67ade8dd389335cbfcacc5b4020a9f2ab03d1eeb6ddaa783b0d750'
JPIN='090e2a6856e6808c601befe67b833013bf613421830d1726411e80e81116d0fe'
LIGHTS=('Bright','Dark'); MASKS=tuple(range(8)); STEPS=(10,25,50)
REGIMES=('deterministic','stochastic'); METRICS=('speed','nearest_distance','polarization')
RTOL=1e-7; ATOL=1e-10
def sha(b):return hashlib.sha256(b).hexdigest()
def reference(path):
    assert sha(path.read_bytes())==PIN
    with zipfile.ZipFile(path) as z:
        assert len(z.namelist())==1;raw=z.read(z.namelist()[0])
    assert sha(raw)==JPIN
    j=json.loads(raw)
    assert j['status']=='V58_BALANCED_POOLED_RULES_SCORED'
    assert j['scientific_status']=='CONDITIONAL_NEAR_SPECIFICITY_NOT_SUPPORTED'
    return j
def geom(p):
    off=p[:,None,:,:]-p[:,:,None,:]
    d2=np.sum(off**2,axis=-1);i=np.arange(3);d2[:,i,i]=np.inf
    near=np.argmin(d2,axis=2);idx=np.arange(len(p))[:,None]
    return off,d2,near,idx,i[None,:]
def features(p,prev,older):
    v=(p-prev)/.2;old=(prev-older)/.2
    off,d2,near,idx,i=geom(p)
    other=(v.sum(1,keepdims=True)-v)/2
    b=np.concatenate((p,v,old,v-old,np.linalg.norm(v,axis=-1,keepdims=True),p.mean(1,keepdims=True)-p,off[idx,i,near],np.sqrt(d2[idx,i,near])[:,:,None]),axis=-1)
    x=np.concatenate((b,other-v,v[idx,near]-other),axis=-1)
    assert x.shape==(len(p),3,18)
    return x
def descriptors(p,v):
    speed=np.linalg.norm(v,axis=-1)
    unit=np.divide(v,speed[:,:,None],out=np.zeros_like(v),where=speed[:,:,None]>0)
    _,d2,_,_,_=geom(p)
    return np.column_stack((speed.mean(1),np.sqrt(d2.min(2)).mean(1),np.linalg.norm(unit.mean(1),axis=-1)))
def fixture():
    v58.fixtures()
    rng=np.random.default_rng(59)
    p=rng.normal(size=(18000,3,2));f=np.arange(len(p))
    X,Y,t=v56.native_panels(f,p,'v59-fixture')
    x=features(p[t],p[t-6],p[t-12]).reshape(-1,18)
    np.testing.assert_array_equal(x,X['base']['NEAR'])
    np.testing.assert_allclose(descriptors(p[t],(p[t]-p[t-6])/.2),v56.state_values(f,p,t),rtol=1e-12,atol=1e-12)
    # Simultaneous update integrates a prescribed constant velocity exactly.
    r=p[:2].copy();v=np.ones_like(r)*3
    beta=np.zeros((19,2));beta[-1]=3
    y=np.c_[features(r,r-.2*v,r-.4*v).reshape(-1,18),np.ones(6)]@beta
    np.testing.assert_allclose(r+.2*y.reshape(r.shape),r+.2*v,rtol=0,atol=1e-12)
    print('v59 simulation feature/descriptor and simultaneous update fixtures PASS',flush=True)
def stat(a):
    return v58.stat(a)
def starts_for(p,t):
    s=np.arange(66,len(p)-300,300)
    s=s[np.isin(s,t)]
    ix=s[:,None]+6*np.arange(-2,51)[None,:]
    s=s[np.isfinite(p[ix]).all((1,2,3))]
    if len(s)<30:raise ValueError('ROLLOUT_WINDOW_SUPPORT_STOP')
    return s
def evaluate(p,starts,coef,scale,lo,hi,noise=None):
    reps=1 if noise is None else noise.shape[2]
    n=len(starts)
    older=np.repeat(p[starts-12],reps,axis=0)
    prev=np.repeat(p[starts-6],reps,axis=0)
    now=np.repeat(p[starts],reps,axis=0)
    total=np.zeros((reps,3));obs=np.zeros(3);poserr=np.zeros(reps);outside=np.zeros(reps)
    result={}
    for k in range(1,51):
        x=features(now,prev,older)
        v=x@coef[:-1]+coef[-1]
        if noise is not None:v=v+noise[k-1].reshape(n*reps,3,2)
        new=now+.2*v
        if not np.isfinite(new).all() or not np.isfinite(v).all() or max(np.abs(new).max(),np.abs(v).max())>1e9:
            return {'status':'DIVERGED_SAFETY_STOP','failed_step':k,'horizons':result}
        real=p[starts+6*k];realv=(real-p[starts+6*(k-1)])/.2
        total+=descriptors(new,v).reshape(n,reps,3).mean(0)
        obs+=descriptors(real,realv).mean(0)
        poserr+=np.linalg.norm(new.reshape(n,reps,3,2)-real[:,None,:,:],axis=-1).mean((0,2))
        outside+=(((new<lo)|(new>hi)).any(-1)).reshape(n,reps,3).mean((0,2))
        older,prev,now=prev,now,new
        if k in STEPS:
            pred=total.mean(0)/k;ob=obs/k;err=(pred-ob)/scale
            result[str(k)]={'simulated_mean':pred.tolist(),'observed_mean':ob.tolist(),
                'standardized_signed_error':err.tolist(),'loss':float(np.mean(err**2)),
                'replicate_descriptor_means':(total/k).tolist(),
                'mean_position_error_native':float(poserr.mean()/k),
                'outside_training_rectangle_fraction':float(outside.mean()/k)}
    return {'status':'COMPLETE','horizons':result}
def run(source,diag,p55,p58,out):
    fixture();j55=v56.ref(p55);j58=reference(p58)
    qc={};data=v55.admit(source,v55.reference(diag),qc);assert qc==j55['source_QC']
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS}
    assert ids==j58['trial_order'] and [len(ids[l]) for l in LIGHTS]==[9,10]
    allids=ids['Bright']+ids['Dark'];lights={i:l for l in LIGHTS for i in ids[l]}
    rec={};orig={}
    for l in LIGHTS:
        for i,(f,p) in data['Triads-'+l].items():
            X,Y,t=v56.native_panels(f,p,i);x=X['base']['NEAR']
            assert len(t)==j55['windows']['full_archive']['window_group_times'][i]
            np.testing.assert_array_equal(features(p[t],p[t-6],p[t-12]).reshape(-1,18),x)
            z=descriptors(p[t],(p[t]-p[t-6])/.2)
            np.testing.assert_allclose(z,v56.state_values(f,p,t),rtol=1e-12,atol=1e-12)
            s=starts_for(p,t)
            rec[i]={'p':p,'x':x,'y':Y,'z':z,'starts':s}
            orig[i]=file_moment(x,Y)
    combos=[b+d for b in itertools.combinations(ids['Bright'],8) for d in itertools.combinations(ids['Dark'],8)]
    assert len(combos)==405
    selected={i:sorted([tr for tr in combos if i not in tr],key=lambda tr:sha(('v59|'+i+'|'+'|'.join(tr)).encode()))[:3] for i in allids}
    keep={tr for rows in selected.values() for tr in rows};fits={tr:{} for tr in keep}
    replay=0.
    for mask in MASKS:
        T={l:v58.transform_matrix(18,1 if l=='Bright' else -1,mask) for l in LIGHTS}
        m={i:v58.transform(orig[i],T[lights[i]]) for i in allids}
        pred={i:[] for i in allids}
        for tr in combos:
            beta,bias=train_only_standardized_ridge(sum_moments([m[i] for i in tr]))
            if tr in keep:fits[tr][mask]={l:T[l]@beta+np.vstack((np.zeros((18,4)),bias[None,:])) for l in LIGHTS}
            for i in allids:
                if i in tr:continue
                q=score_file_moment(m[i],beta,bias);pred[i].append([q[h] for h in ('short','delayed')])
        for i in allids:
            assert len(pred[i])==(45 if lights[i]=='Bright' else 81)
            a=np.mean(pred[i],0);b=np.array(j58['source_safe_pooled_subset_MSE']['base'][i][mask])
            replay=max(replay,float(np.max(np.abs(a-b))))
            np.testing.assert_allclose(a,b,rtol=RTOL,atol=ATOL)
    print('all original v58 base MSEs reproduced',replay,flush=True)
    results={};n_runs=0;n_stop=0
    for i in allids:
        r=rec[i];l=lights[i];results[i]=[]
        for tr in selected[i]:
            assert i not in tr and len(tr)==16
            z=np.concatenate([rec[j]['z'] for j in tr]);scale=z.std(0)
            assert np.isfinite(scale).all() and (scale>0).all()
            bank=[]
            for j in tr:
                x=rec[j]['x'];c=fits[tr][0][lights[j]][:,:2]
                bank.append(rec[j]['y'][:,:2]-(x@c[:-1]+c[-1]))
            bank=np.concatenate(bank)
            xy=np.concatenate([rec[j]['x'][:,:2] for j in tr])
            lo=xy.min(0);hi=xy.max(0)
            seed=int.from_bytes(hashlib.sha256(('v59-noise|'+i+'|'+'|'.join(tr)).encode()).digest()[:8],'little')
            # Same independently drawn per-fish residual vectors for all masks.
            noise=bank[np.random.default_rng(seed).integers(len(bank),size=(50,len(r['starts']),8,3))]
            item={'training_ids':list(tr),'n_starts':len(r['starts']),'residual_bank_n':len(bank),'training_descriptor_sd':scale.tolist(),'masks':{}}
            for mask in MASKS:
                c=fits[tr][mask][l][:,:2]
                # Direct fitted-feature expression check on observed rows.
                q=c[:-1];bias=c[-1]
                assert q.shape==(18,2) and bias.shape==(2,)
                row={}
                for regime in REGIMES:
                    v=evaluate(r['p'],r['starts'],c,scale,lo,hi,noise if regime=='stochastic' else None)
                    n_runs+=1;n_stop+=v['status']!='COMPLETE';row[regime]=v
                item['masks'][str(mask)]=row
            results[i].append(item)
        print('all 3 frozen train-set rollouts complete',l,i,'starts',len(r['starts']),flush=True)
    summary={}
    for regime in REGIMES:
        summary[regime]={}
        for step in STEPS:
            h=str(step);summary[regime][h]={}
            for l in LIGHTS:
                group={}
                for mask in MASKS:
                    z=[];obs=[];sim=[];err=[];position=[];outside=[]
                    failed=[]
                    for i in ids[l]:
                        rr=[v['masks'][str(mask)][regime] for v in results[i]]
                        if any(v['status']!='COMPLETE' for v in rr):
                            failed.append(i);continue
                        vals=[v['horizons'][h] for v in rr]
                        z.append(np.mean([v['loss'] for v in vals]))
                        obs.append(np.mean([v['observed_mean'] for v in vals],0))
                        sim.append(np.mean([v['simulated_mean'] for v in vals],0))
                        err.append(np.mean([v['standardized_signed_error'] for v in vals],0))
                        position.append(np.mean([v['mean_position_error_native'] for v in vals]))
                        outside.append(np.mean([v['outside_training_rectangle_fraction'] for v in vals]))
                    if failed:group[str(mask)]={'status':'ROLLOUT_SAFETY_STOP','failed_trials':failed};continue
                    group[str(mask)]={'status':'ADMITTED','loss_per_trial':z,'mean_loss':float(np.mean(z)),
                        'mean_observed':np.mean(obs,0).tolist(),'mean_simulated':np.mean(sim,0).tolist(),
                        'mean_standardized_signed_error':np.mean(err,0).tolist(),'mean_position_error_native':float(np.mean(position)),
                        'outside_training_rectangle_fraction':float(np.mean(outside))}
                for mask in MASKS:
                    row=group[str(mask)];b=group['0']
                    if row['status']==b['status']=='ADMITTED':
                        a=stat(np.array(b['loss_per_trial'])-np.array(row['loss_per_trial']))
                        a['direction_gate_pass']=v58.gate(a,len(ids[l]))
                        row['improvement_vs_M0']=a
                if group['3']['status']==group['7']['status']=='ADMITTED':
                    group['M3_minus_M7']=stat(np.array(group['3']['loss_per_trial'])-np.array(group['7']['loss_per_trial']))
                summary[regime][h][l]=group
            diff={}
            for mask in MASKS:
                b=summary[regime][h]['Bright'][str(mask)];d=summary[regime][h]['Dark'][str(mask)]
                if b['status']==d['status']=='ADMITTED':
                    diff[str(mask)]={'observed_bright_minus_dark':(np.array(b['mean_observed'])-d['mean_observed']).tolist(),'simulated_bright_minus_dark':(np.array(b['mean_simulated'])-d['mean_simulated']).tolist()}
            summary[regime][h]['descriptor_contrast']=diff
    p=summary['stochastic']['50']['Dark']['3']
    decision=('ROLLOUT_PRIMARY_STOP' if 'improvement_vs_M0' not in p else ('ROLLOUT_M3_DIRECTION_SUPPORTED_DESCRIPTIVE' if p['improvement_vs_M0']['direction_gate_pass'] else 'ROLLOUT_M3_DIRECTION_NOT_SUPPORTED'))
    out.update(status='V59_HELDOUT_CLOSED_LOOP_ROLLOUT_SCORED',scientific_status=decision,
        prior_v58_scientific_status=j58['scientific_status'],prior_v58_zip_sha256=PIN,prior_v58_json_sha256=JPIN,
        all_58_original_members_authenticated=True,trial_order=ids,n_train_sets_per_heldout=3,
        original_v58_base_score_replay_max_abs=replay,n_rollout_trial_train_model_regime_runs=n_runs,n_safety_stops=n_stop,
        n_starts_by_trial={i:len(rec[i]['starts']) for i in allids},descriptor_order=list(METRICS),step_seconds=.2,
        physical_wall_or_speed_clipping=False,raw_coordinates_or_coefficients_exported=False,
        source_safe_rollout_scores=results,summary=summary)
def main():
    p=argparse.ArgumentParser()
    for name in ('source','diagnostic','v55','v58','out'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a.source,a.diagnostic,a.v55,a.v58,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    small={k:v for k,v in o.items() if k not in ('summary','source_safe_rollout_scores','trial_order')}
    if 'summary' in o:
        small['summary']={r:{h:{l:{m:{k:x.get(k) for k in ('status','mean_loss','mean_simulated','mean_observed','outside_training_rectangle_fraction','improvement_vs_M0')} for m,x in groups[l].items() if m in tuple(map(str,MASKS))} for l in LIGHTS} for h,groups in horizons.items()} for r,horizons in o['summary'].items()}
    print(json.dumps(small,sort_keys=True),flush=True)
    if o['status']!='V59_HELDOUT_CLOSED_LOOP_ROLLOUT_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
