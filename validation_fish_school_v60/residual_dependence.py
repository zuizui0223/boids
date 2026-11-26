"""v60 distributional rollout and training-only residual dependence sensitivity."""
import argparse,itertools,json,hashlib,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v58 import selective_rules as v58
from validation_fish_school_v59 import closed_loop_rollout as v59
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge
PIN='e1c6ab2dcdba2da341aee914c69c51e4229d7ad0e19fb303d18cec7a3a075ecf'
JPIN='e20a7115cd82442a5160c13be240491ccd45a5f3024c40306e361740992dda75'
REGIMES=('pooled_iid','light_iid_centered','light_group_centered','light_block_centered')
MASKS=(0,3,7);LIGHTS=('Bright','Dark');QUANTILES=(.1,.5,.9);STEPS=(10,25,50)
RTOL=1e-7;ATOL=1e-10
def sha(b):return hashlib.sha256(b).hexdigest()
def ref(path):
    assert sha(path.read_bytes())==PIN
    with zipfile.ZipFile(path) as z:
        assert z.namelist()==['rollout.json'];raw=z.read('rollout.json')
    assert sha(raw)==JPIN
    j=json.loads(raw)
    assert j['status']=='V59_HELDOUT_CLOSED_LOOP_ROLLOUT_SCORED' and j['n_safety_stops']==0
    return j
def seed(s):return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8],'little')
def make_noises(residuals,times,train,lights,light,held,n):
    # residuals[j] has original eligible group-time × 3 original fish × XY.
    pool=np.concatenate([residuals[j].reshape(-1,2) for j in train])
    group=np.concatenate([residuals[j] for j in train if lights[j]==light])
    mu=group.mean((0,1));group=group-mu
    chunks=[]
    for j in train:
        if lights[j]!=light:continue
        t=times[j];r=residuals[j]-mu
        ix=np.arange(len(t)-4)[:,None]+np.arange(5)[None,:]
        good=np.all(np.diff(t[ix],axis=1)==6,axis=1)
        chunks.append(r[ix[good]])
    blocks=np.concatenate(chunks)
    assert len(blocks)>1000 and np.isfinite(blocks).all()
    tag=held+'|'+'|'.join(train)
    out={}
    rng=np.random.default_rng(seed('v59-noise|'+tag))
    out['pooled_iid']=pool[rng.integers(len(pool),size=(50,n,8,3))]
    rng=np.random.default_rng(seed('v60-light-iid|'+tag));flat=group.reshape(-1,2)
    out['light_iid_centered']=flat[rng.integers(len(flat),size=(50,n,8,3))]
    rng=np.random.default_rng(seed('v60-light-group|'+tag))
    g=group[rng.integers(len(group),size=(50,n,8))]
    perm=rng.permuted(np.broadcast_to(np.arange(3),(50,n,8,3)),axis=-1)
    out['light_group_centered']=np.take_along_axis(g,perm[...,None],axis=3)
    rng=np.random.default_rng(seed('v60-light-block|'+tag))
    b=blocks[rng.integers(len(blocks),size=(10,n,8))]
    perm=rng.permuted(np.broadcast_to(np.arange(3),(10,n,8,3)),axis=-1)
    b=np.take_along_axis(b,perm[:,:,:,None,:,None],axis=4)
    out['light_block_centered']=b.transpose(0,3,1,2,4,5).reshape(50,n,8,3,2)
    for x in out.values():assert x.shape==(50,n,8,3,2) and np.isfinite(x).all()
    # No individual residual or fitted coefficient export.
    return out,{'pooled_vector_count':len(pool),'same_light_group_time_count':len(group),'same_light_block_start_count':len(blocks),
                'draw_diagnostics':{k:{'mean_xy':x.mean((0,1,2,3)).tolist(),'rms':float(np.sqrt(np.mean(x*x)))} for k,x in out.items()}}
def evaluate(p,starts,coef,scale,lo,hi,noise):
    n=len(starts);reps=8
    older=np.repeat(p[starts-12],reps,axis=0);prev=np.repeat(p[starts-6],reps,axis=0);now=np.repeat(p[starts],reps,axis=0)
    total=np.zeros((reps,3));obs=np.zeros(3);poserr=np.zeros(reps);outside=np.zeros(reps)
    pred_rows=[];obs_rows=[];result={}
    for k in range(1,51):
        x=v59.features(now,prev,older);v=x@coef[:-1]+coef[-1]+noise[k-1].reshape(n*reps,3,2)
        new=now+.2*v
        if not np.isfinite(new).all() or not np.isfinite(v).all() or max(np.abs(new).max(),np.abs(v).max())>1e9:
            return {'status':'DIVERGED_SAFETY_STOP','failed_step':k,'horizons':result}
        real=p[starts+6*k];realv=(real-p[starts+6*(k-1)])/.2
        d=v59.descriptors(new,v).reshape(n,reps,3);o=v59.descriptors(real,realv)
        total+=d.mean(0);obs+=o.mean(0);pred_rows.append(d.reshape(-1,3));obs_rows.append(o)
        poserr+=np.linalg.norm(new.reshape(n,reps,3,2)-real[:,None,:,:],axis=-1).mean((0,2))
        outside+=(((new<lo)|(new>hi)).any(-1)).reshape(n,reps,3).mean((0,2))
        older,prev,now=prev,now,new
        if k in STEPS:
            mean=total.mean(0)/k;ob=obs/k;err=(mean-ob)/scale
            qp=np.quantile(np.concatenate(pred_rows),QUANTILES,axis=0);qo=np.quantile(np.concatenate(obs_rows),QUANTILES,axis=0)
            qe=(qp-qo)/scale
            result[str(k)]={'simulated_mean':mean.tolist(),'observed_mean':ob.tolist(),'standardized_signed_error':err.tolist(),
                'loss':float(np.mean(err**2)),'replicate_descriptor_means':(total/k).tolist(),
                'mean_position_error_native':float(poserr.mean()/k),'outside_training_rectangle_fraction':float(outside.mean()/k),
                'simulated_quantiles':qp.tolist(),'observed_quantiles':qo.tolist(),'standardized_quantile_errors':qe.tolist(),'quantile_loss':float(np.mean(qe**2))}
    return {'status':'COMPLETE','horizons':result}
def run(a,out):
    v59.fixture()
    prior=ref(a.v59);j55=v56.ref(a.v55);qc={}
    data=v55.admit(a.source,v55.reference(a.diagnostic),qc);assert qc==j55['source_QC']
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS};assert ids==prior['trial_order']
    allids=ids['Bright']+ids['Dark'];lights={i:l for l in LIGHTS for i in ids[l]}
    rec={};orig={};times={}
    for l in LIGHTS:
        for i,(f,p) in data['Triads-'+l].items():
            X,Y,t=v56.native_panels(f,p,i);x=X['base']['NEAR']
            assert len(t)==j55['windows']['full_archive']['window_group_times'][i]
            np.testing.assert_array_equal(v59.features(p[t],p[t-6],p[t-12]).reshape(-1,18),x)
            z=v59.descriptors(p[t],(p[t]-p[t-6])/.2);s=v59.starts_for(p,t)
            assert len(s)==prior['n_starts_by_trial'][i]
            rec[i]={'p':p,'x':x,'y':Y,'z':z,'starts':s};orig[i]=file_moment(x,Y);times[i]=t
    combos=[b+d for b in itertools.combinations(ids['Bright'],8) for d in itertools.combinations(ids['Dark'],8)]
    assert len(combos)==405
    selected={i:sorted([tr for tr in combos if i not in tr],key=lambda tr:sha(('v59|'+i+'|'+'|'.join(tr)).encode()))[:3] for i in allids}
    for i in allids:assert [list(tr) for tr in selected[i]]==[r['training_ids'] for r in prior['source_safe_rollout_scores'][i]]
    results={};max_replay=0.;nchecks=0;stops=0
    for i in ids[a.light]:
        results[i]=[];r=rec[i];l=lights[i]
        for j,tr in enumerate(selected[i]):
            assert i not in tr and len(tr)==16
            fit={}
            for mask in MASKS:
                T={l:v58.transform_matrix(18,1 if l=='Bright' else -1,mask) for l in LIGHTS}
                m=[v58.transform(orig[q],T[lights[q]]) for q in tr]
                beta,bias=train_only_standardized_ridge(sum_moments(m))
                fit[mask]={l:(T[l]@beta+np.vstack((np.zeros((18,4)),bias[None,:])))[:,:2] for l in LIGHTS}
            res={q:(rec[q]['y'][:,:2]-(rec[q]['x']@fit[0][lights[q]][:-1]+fit[0][lights[q]][-1])).reshape(-1,3,2) for q in tr}
            noises,noise_qc=make_noises(res,times,tr,lights,l,i,len(r['starts']))
            xy=np.concatenate([rec[q]['x'][:,:2] for q in tr]);lo=xy.min(0);hi=xy.max(0)
            scale=np.concatenate([rec[q]['z'] for q in tr]).std(0)
            prev=prior['source_safe_rollout_scores'][i][j]
            np.testing.assert_allclose(scale,prev['training_descriptor_sd'],rtol=RTOL,atol=ATOL)
            assert noise_qc['pooled_vector_count']==prev['residual_bank_n']
            item={'training_ids':list(tr),'n_starts':len(r['starts']),'training_descriptor_sd':scale.tolist(),'noise_qc':noise_qc,'masks':{}}
            for mask in MASKS:
                item['masks'][str(mask)]={}
                for regime in REGIMES:
                    z=evaluate(r['p'],r['starts'],fit[mask][l],scale,lo,hi,noises[regime]);stops+=z['status']!='COMPLETE'
                    if regime=='pooled_iid':
                        assert z['status']=='COMPLETE'
                        old=prev['masks'][str(mask)]['stochastic']['horizons']
                        for h,v in z['horizons'].items():
                            for k in old[h]:
                                x=np.asarray(v[k],float);y=np.asarray(old[h][k],float)
                                np.testing.assert_allclose(x,y,rtol=RTOL,atol=ATOL);max_replay=max(max_replay,float(np.max(np.abs(x-y))));nchecks+=1
                    item['masks'][str(mask)][regime]=z
            results[i].append(item)
        print('v60 heldout trial complete',a.light,i,flush=True)
    summary={}
    for regime in REGIMES:
        summary[regime]={}
        for step in STEPS:
            h=str(step);g={}
            for mask in MASKS:
                rows=[[v['masks'][str(mask)][regime] for v in results[i]] for i in ids[a.light]]
                if any(q['status']!='COMPLETE' for r in rows for q in r):
                    g[str(mask)]={'status':'ROLLOUT_SAFETY_STOP'};continue
                rows=[[q['horizons'][h] for q in r] for r in rows]
                z={}
                for k in ('loss','quantile_loss','outside_training_rectangle_fraction','mean_position_error_native','simulated_mean','observed_mean','simulated_quantiles','observed_quantiles'):
                    v=np.array([np.mean([q[k] for q in r],axis=0) for r in rows])
                    z[k]={'equal_trial_mean':v.mean(0).tolist(),'per_trial':v.tolist()}
                g[str(mask)]={'status':'ADMITTED',**z}
            for mask in (3,7):
                if g['0']['status']==g[str(mask)]['status']=='ADMITTED':
                    for k in ('loss','quantile_loss'):
                        q=v58.stat(np.array(g['0'][k]['per_trial'])-g[str(mask)][k]['per_trial'])
                        q['direction_gate_pass']=v58.gate(q,len(ids[a.light]))
                        g[str(mask)][k+'_improvement_vs_M0']=q
            summary[regime][h]=g
    q=summary['light_block_centered']['50']['3'].get('quantile_loss_improvement_vs_M0')
    verdict='SECONDARY_BRIGHT' if a.light=='Bright' else ('PRIMARY_STOP' if q is None else ('BLOCK_DISTRIBUTION_M3_SUPPORTED_DESCRIPTIVE' if q['direction_gate_pass'] else 'BLOCK_DISTRIBUTION_M3_NOT_SUPPORTED'))
    out.update(status='V60_ORIGINAL_RESIDUAL_DEPENDENCE_SCORED',light=a.light,scientific_status=verdict,source_58_reauthenticated=True,
               prior_v59_zip_sha256=PIN,prior_v59_json_sha256=JPIN,trial_order=ids[a.light],n_safety_stops=stops,
               replay_checks=nchecks,max_v59_replay_abs=max_replay,summary=summary,source_safe_scores=results,raw_positions_or_coefficients_exported=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--light',choices=LIGHTS,required=True)
    for k in ('source','diagnostic','v55','v59','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    small={k:v for k,v in o.items() if k not in ('summary','source_safe_scores','trial_order')}
    if 'summary' in o:
        small['ten_second']={r:{m:{k:v[k]['equal_trial_mean'] for k in ('loss','quantile_loss','outside_training_rectangle_fraction') if k in v} for m,v in g['50'].items()} for r,g in o['summary'].items()}
        small['primary']=o['summary']['light_block_centered']['50']['3'].get('quantile_loss_improvement_vs_M0')
    print(json.dumps(small,sort_keys=True),flush=True)
    if o['status']!='V60_ORIGINAL_RESIDUAL_DEPENDENCE_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
