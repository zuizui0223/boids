"""v62 training-only empirical occupancy projections, not a calibrated physical wall.
Same v61 original 30s support and paired noise. Only aggregate score receipts."""
import argparse,hashlib,itertools,json,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v58 import selective_rules as v58
from validation_fish_school_v59 import closed_loop_rollout as v59
from validation_fish_school_v60 import residual_dependence as v60
from validation_fish_school_v61 import temporal_fidelity as v61
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge
PINS={
 'Bright':('71a8a33e23806d7eb6a622a3b5be67814ea850042f3e298048ac8e6ff23c7233','966d6dda83053b7081199fe592653443b8a0081ca0db83f9f4392def6aee8613'),
 'Dark':('5e0d3a7ea014d662b959cc59d823bf95f16aa44425965531d1aa4c387f2d4016','c0683870f5069f3dc4a139c1cb4b76832d2d221d10443236d3ea539f26387b58')}
LIGHTS=('Bright','Dark');MASKS=(0,3);REGS=v61.LONG_REGS;MODES=('free','rectangle','circle');H=(50,150)
RTOL=1e-7;ATOL=1e-10
def sha(b):return hashlib.sha256(b).hexdigest()
def reference(path,light):
    zp,jp=PINS[light];assert sha(path.read_bytes())==zp
    with zipfile.ZipFile(path) as z:
        assert z.namelist()==[light+'.json'];raw=z.read(light+'.json')
    assert sha(raw)==jp
    j=json.loads(raw)
    assert j['status']=='V61_ORIGINAL_TEMPORAL_FIDELITY_SCORED' and j['light']==light and j['long_safety_stops']==0
    return j

def envelope(xy):
    lo=xy.min(0);hi=xy.max(0);center=(lo+hi)/2
    radius=float(np.linalg.norm(xy-center,axis=-1).max())
    assert np.isfinite(radius) and radius>0 and (hi>lo).all()
    return lo,hi,center,radius

def project(p,env,mode):
    lo,hi,c,r=env
    if mode=='free':return p
    if mode=='rectangle':return np.clip(p,lo,hi)
    if mode!='circle':raise ValueError('UNKNOWN_ENVELOPE')
    d=p-c;rho=np.linalg.norm(d,axis=-1,keepdims=True)
    # Avoid a roundoff change of an unprojected position.
    factor=np.divide(r,rho,out=np.ones_like(rho),where=rho>r)
    return np.where(rho>r,c+d*factor,p)

def occupancy(p,env):
    lo,hi,c,r=env;tol=1e-8*max(1.,r)
    rho=np.linalg.norm(p-c,axis=-1)
    rect=((p<lo)|(p>hi)).any(-1)
    circ=rho>r+tol
    rect_surface=(~rect)&((np.abs(p-lo)<=tol)|(np.abs(p-hi)<=tol)).any(-1)
    circ_surface=np.abs(rho-r)<=tol
    return np.array([rect.mean(),circ.mean(),rect_surface.mean(),circ_surface.mean()])
def fixture():
    v61.fixtures()
    xy=np.array([[-2.,-1.],[2.,1.],[0.,0.]])
    env=envelope(xy);p=np.array([[[0.,0.],[4.,0.],[-3.,-4.]]])
    c=project(p,env,'circle');b=project(p,env,'rectangle')
    np.testing.assert_array_equal(c[0,0],p[0,0]);assert occupancy(c,env)[1]==0
    np.testing.assert_array_equal(b,[[[0.,0.],[2.,0.],[-2.,-1.]]]);assert occupancy(b,env)[0]==0
    np.testing.assert_allclose(np.linalg.norm(c[0,1:]-env[2],axis=1),env[3],atol=1e-12)
    print('v62 envelope projection, surface and free-feature fixtures PASS',flush=True)

def evaluate(p,starts,coef,scale,env,noise,mode):
    n=len(starts);reps=8
    assert noise.shape==(150,n,reps,3,2)
    older=np.repeat(p[starts-12],reps,axis=0);prev=np.repeat(p[starts-6],reps,axis=0);now=np.repeat(p[starts],reps,axis=0)
    init=occupancy(np.stack((older,prev,now)),env)
    total=np.zeros((reps,3));obs=np.zeros(3);poserr=np.zeros(reps);outside=np.zeros(reps);obsout=0.
    pred_rows=[];obs_rows=[];cent=[];ocent=[];result={}
    occ=np.zeros(4);oocc=np.zeros(4);corr_frac=0.;corr_m2=0.;corr_speed=0.
    lo,hi,_,radius=env
    for k in range(1,151):
        x=v59.features(now,prev,older)
        v=x@coef[:-1]+coef[-1]+noise[k-1].reshape(n*reps,3,2)
        proposal=now+.2*v
        if not np.isfinite(proposal).all() or not np.isfinite(v).all() or max(np.abs(proposal).max(),np.abs(v).max())>1e9:
            return {'status':'DIVERGED_SAFETY_STOP','failed_step':k,'horizons':result}
        new=project(proposal,env,mode)
        delta=new-proposal;cor=np.linalg.norm(delta,axis=-1)
        if mode!='free':
            v=(new-now)/.2
        if not np.isfinite(new).all() or not np.isfinite(v).all() or max(np.abs(new).max(),np.abs(v).max())>1e9:
            return {'status':'DIVERGED_SAFETY_STOP','failed_step':k,'horizons':result}
        if mode=='rectangle':assert not (((new<lo)|(new>hi)).any())
        if mode=='circle':assert occupancy(new,env)[1]==0
        real=p[starts+6*k];realv=(real-p[starts+6*(k-1)])/.2
        d=v59.descriptors(new,v).reshape(n,reps,3);o=v59.descriptors(real,realv)
        total+=d.mean(0);obs+=o.mean(0);pred_rows.append(d);obs_rows.append(o)
        cent.append(new.reshape(n,reps,3,2).mean(2));ocent.append(real.mean(1))
        poserr+=np.linalg.norm(new.reshape(n,reps,3,2)-real[:,None,:,:],axis=-1).mean((0,2))
        outside+=(((new<lo)|(new>hi)).any(-1)).reshape(n,reps,3).mean((0,2))
        obsout+=float(((real<lo)|(real>hi)).any(-1).mean())
        occ+=occupancy(new,env);oocc+=occupancy(real,env)
        corr_frac+=float((cor>0).mean());corr_m2+=float(np.mean(cor**2))
        corr_speed+=float(np.mean(np.linalg.norm(v,axis=-1)-np.linalg.norm((proposal-now)/.2,axis=-1)))
        older,prev,now=prev,now,new
        if k in H:
            mean=total.mean(0)/k;ob=obs/k;err=(mean-ob)/scale
            qp=np.quantile(np.concatenate([r.reshape(-1,3) for r in pred_rows]),v60.QUANTILES,axis=0)
            qo=np.quantile(np.concatenate(obs_rows),v60.QUANTILES,axis=0);qe=(qp-qo)/scale
            result[str(k)]={'simulated_mean':mean.tolist(),'observed_mean':ob.tolist(),'standardized_signed_error':err.tolist(),
                'loss':float(np.mean(err**2)),'replicate_descriptor_means':(total/k).tolist(),
                'mean_position_error_native':float(poserr.mean()/k),'outside_training_rectangle_fraction':float(outside.mean()/k),
                'observed_outside_training_rectangle_fraction':obsout/k,
                'simulated_quantiles':qp.tolist(),'observed_quantiles':qo.tolist(),'standardized_quantile_errors':qe.tolist(),'quantile_loss':float(np.mean(qe**2)),
                **v61.dynamic(np.array(pred_rows),np.array(obs_rows),np.array(cent),np.array(ocent),scale),
                'simulated_occupancy_diagnostics':(occ/k).tolist(),'observed_occupancy_diagnostics':(oocc/k).tolist(),
                'corrected_proposal_fraction':corr_frac/k,'correction_rms_native':float(np.sqrt(corr_m2/k)),
                'mean_realized_minus_proposed_speed_native':corr_speed/k,'initial_history_occupancy_diagnostics':init.tolist()}
    return {'status':'COMPLETE','horizons':result}

def replay(a,b):
    if isinstance(b,dict):
        n=0;err=0.
        for k,v in b.items():
            x,e=replay(a[k],v);n+=x;err=max(err,e)
        return n,err
    x=np.asarray(a,float);y=np.asarray(b,float)
    np.testing.assert_allclose(x,y,rtol=RTOL,atol=ATOL)
    return 1,float(np.max(np.abs(x-y)))

def summarize(rows,ids):
    fields=('loss','quantile_loss','temporal_loss','outside_training_rectangle_fraction','observed_outside_training_rectangle_fraction',
            'simulated_occupancy_diagnostics','observed_occupancy_diagnostics','initial_history_occupancy_diagnostics',
            'corrected_proposal_fraction','correction_rms_native','mean_realized_minus_proposed_speed_native','mean_position_error_native',
            'simulated_mean','observed_mean','simulated_lag_rms','observed_lag_rms','simulated_quantiles','observed_quantiles')
    out={}
    for h in map(str,H):
        out[h]={}
        for r in REGS:
            g={}
            for mode in MODES:
                g[mode]={}
                for m in map(str,MASKS):
                    rr=[[q[m][r][mode] for q in rows[i]] for i in ids]
                    bad=[i for i,q in zip(ids,rr) if any(x['status']!='COMPLETE' for x in q)]
                    if bad:g[mode][m]={'status':'STOP','failed_trials':bad};continue
                    a=[[x['horizons'][h] for x in q] for q in rr];z={'status':'ADMITTED'}
                    for k in fields:
                        v=np.array([np.mean([x[k] for x in q],axis=0) for q in a])
                        z[k]={'equal_trial_mean':v.mean(0).tolist(),'per_trial':v.tolist()}
                    g[mode][m]=z
                if all(g[mode][m]['status']=='ADMITTED' for m in ('0','3')):
                    for k in ('loss','quantile_loss','temporal_loss'):
                        q=v58.stat(np.array(g[mode]['0'][k]['per_trial'])-g[mode]['3'][k]['per_trial']);q['direction_gate_pass']=v58.gate(q,len(ids))
                        g[mode]['3'][k+'_improvement_vs_M0']=q
            for mode in ('rectangle','circle'):
                for m in map(str,MASKS):
                    z=g[mode][m];b=g['free'][m]
                    if z['status']==b['status']=='ADMITTED':
                        for k in ('loss','quantile_loss','temporal_loss','outside_training_rectangle_fraction','mean_position_error_native'):
                            q=v58.stat(np.array(b[k]['per_trial'])-z[k]['per_trial']);q['direction_gate_pass']=v58.gate(q,len(ids));z[k+'_improvement_vs_free']=q
            out[h][r]=g
    return out

def run(a,out):
    fixture();old=reference(a.v61,a.light);j55=v56.ref(a.v55);prior=v60.ref(a.v59);qc={}
    data=v55.admit(a.source,v55.reference(a.diagnostic),qc);assert qc==j55['source_QC']
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS};assert ids==prior['trial_order'] and ids[a.light]==old['trial_order']
    allids=ids['Bright']+ids['Dark'];lights={i:l for l in LIGHTS for i in ids[l]};rec={};orig={};times={}
    for i in allids:
        f,p=data['Triads-'+lights[i]][i];X,Y,t=v56.native_panels(f,p,i);x=X['base']['NEAR']
        assert len(t)==j55['windows']['full_archive']['window_group_times'][i]
        np.testing.assert_array_equal(v59.features(p[t],p[t-6],p[t-12]).reshape(-1,18),x)
        z=v59.descriptors(p[t],(p[t]-p[t-6])/.2);s=v61.long_starts(p,t)
        if i in ids[a.light]:assert len(s)==old['long_starts'][i] and len(s)>=15
        rec[i]={'p':p,'x':x,'y':Y,'z':z,'starts':s};orig[i]=file_moment(x,Y);times[i]=t
    combos=[b+d for b in itertools.combinations(ids['Bright'],8) for d in itertools.combinations(ids['Dark'],8)]
    selected={i:sorted([tr for tr in combos if i not in tr],key=lambda tr:sha(('v59|'+i+'|'+'|'.join(tr)).encode()))[:3] for i in allids}
    for i in allids:assert [list(tr) for tr in selected[i]]==[r['training_ids'] for r in prior['source_safe_rollout_scores'][i]]
    results={};nchecks=0;max_replay=0.;stops=0
    # Whole-light replay gate: complete the original free rollouts BEFORE any constrained simulation.
    prepared=[]
    for i in ids[a.light]:
        r=rec[i];l=lights[i];results[i]=[]
        for j,tr in enumerate(selected[i]):
            assert i not in tr and len(tr)==16
            fit={}
            for mask in MASKS:
                T={l:v58.transform_matrix(18,1 if l=='Bright' else -1,mask) for l in LIGHTS}
                m=[v58.transform(orig[q],T[lights[q]]) for q in tr]
                beta,bias=train_only_standardized_ridge(sum_moments(m))
                fit[mask]={l:(T[l]@beta+np.vstack((np.zeros((18,4)),bias[None,:])))[:,:2] for l in LIGHTS}
            res={q:(rec[q]['y'][:,:2]-(rec[q]['x']@fit[0][lights[q]][:-1]+fit[0][lights[q]][-1])).reshape(-1,3,2) for q in tr}
            chunks=[v60.make_noises(res,times,tr,lights,l,'v61-long|'+i+'|'+str(k),len(r['starts']))[0] for k in range(3)]
            noise={reg:np.concatenate([c[reg] for c in chunks],axis=0) for reg in REGS}
            xy=np.concatenate([rec[q]['x'][:,:2] for q in tr]);env=envelope(xy);scale=np.concatenate([rec[q]['z'] for q in tr]).std(0)
            assert np.isfinite(scale).all() and (scale>0).all()
            np.testing.assert_allclose(scale,prior['source_safe_rollout_scores'][i][j]['training_descriptor_sd'],rtol=RTOL,atol=ATOL)
            assert occupancy(xy,env)[:2].max()==0
            row={}
            for mask in MASKS:
                row[str(mask)]={}
                for reg in REGS:
                    z=evaluate(r['p'],r['starts'],fit[mask][l],scale,env,noise[reg],'free')
                    before=old['source_safe_long_scores'][i][j][str(mask)][reg]
                    assert z['status']==before['status']=='COMPLETE'
                    n,e=replay(z['horizons'],before['horizons']);nchecks+=n;max_replay=max(max_replay,e)
                    row[str(mask)][reg]={'free':z}
            results[i].append(row)
            prepared.append((i,j,fit,noise,env,scale))
        print('v62 source free replay',a.light,i,flush=True)
    print('ALL v61 long-window metrics replayed',nchecks,max_replay,flush=True)
    for i,j,fit,noise,env,scale in prepared:
        r=rec[i];l=lights[i];row=results[i][j]
        for mask in MASKS:
            for reg in REGS:
                for mode in ('rectangle','circle'):
                    z=evaluate(r['p'],r['starts'],fit[mask][l],scale,env,noise[reg],mode)
                    stops+=z['status']!='COMPLETE';row[str(mask)][reg][mode]=z
        print('v62 constrained score',a.light,i,j,flush=True)
    summary=summarize(results,ids[a.light])
    p=summary['150']['light_block_centered']['circle']['3'].get('quantile_loss_improvement_vs_free')
    verdict='SECONDARY_BRIGHT' if a.light=='Bright' else ('PRIMARY_STOP' if p is None else ('CIRCLE_PROJECTION_QUANTILE_DIRECTION_SUPPORTED_DESCRIPTIVE' if p['direction_gate_pass'] else 'CIRCLE_PROJECTION_QUANTILE_DIRECTION_NOT_SUPPORTED'))
    out.update(status='V62_ORIGINAL_CONFINEMENT_SCORED',light=a.light,scientific_status=verdict,
        source_58_reauthenticated=True,prior_v61_zip_sha256=PINS[a.light][0],prior_v61_json_sha256=PINS[a.light][1],
        trial_order=ids[a.light],long_starts={i:len(rec[i]['starts']) for i in ids[a.light]},replay_checks=nchecks,max_v61_replay_abs=max_replay,
        safety_stops=stops,occupancy_order=['rectangle_outside','circle_outside','rectangle_surface','circle_surface'],
        source_safe_scores=results,summary=summary,physical_tank_calibrated=False,raw_positions_or_coefficients_exported=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--light',choices=LIGHTS,required=True)
    for k in ('source','diagnostic','v55','v59','v61','out'):p.add_argument('--'+k,type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    sm={k:v for k,v in o.items() if k not in ('summary','source_safe_scores','trial_order')}
    if 'summary'in o:
        sm['30_second']={r:{mode:{m:{k:v[k]['equal_trial_mean'] for k in ('loss','quantile_loss','temporal_loss','simulated_occupancy_diagnostics','observed_occupancy_diagnostics','corrected_proposal_fraction') if k in v} for m,v in ms.items()} for mode,ms in g.items()} for r,g in o['summary']['150'].items()}
        sm['primary']=o['summary']['150']['light_block_centered']['circle']['3'].get('quantile_loss_improvement_vs_free')
    print(json.dumps(sm,sort_keys=True),flush=True)
    if o['status']!='V62_ORIGINAL_CONFINEMENT_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
