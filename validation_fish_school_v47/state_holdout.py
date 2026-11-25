"""v47 post-v46 state-stratified scoring. Same 8 original test shoals and six frozen models."""
from pathlib import Path
import json,tempfile,zipfile
import numpy as np
from validation_fish_school_v45.zebrafish_schema import acquire,selected,read_header_and_data,SHA,PINS
from validation_fish_school_v46.grid_preflight import panels
from validation_fish_school_v46.zebrafish_holdout import MODELS,H,HEADER,parity
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'docs/collective_state_synthesis_20261124/V46_SOURCE_SAFE_SCORES_FROM_ORIGINAL_JOB_LOG.json'
MARGINAL={'dispersion':('S_low','S_high'),'polarization':('P_low','P_high')}
CELLS=('S_low_P_low','S_low_P_high','S_high_P_low','S_high_P_high')
def upper_half(z):
    z=np.asarray(z,float)
    if len(z)%2 or not np.isfinite(z).all():raise ValueError('rank support')
    order=np.argsort(z,kind='stable')
    out=np.zeros(len(z),bool);out[order[len(z)//2:]]=True
    return out
def state_values(pos,t):
    now=pos[t]; v=(now-pos[t-3])/.2
    d=np.sqrt(np.mean(np.sum((now-now.mean(1,keepdims=True))**2,axis=-1),axis=1))
    speed=np.linalg.norm(v,axis=-1,keepdims=True)
    u=np.divide(v,speed,out=np.zeros_like(v),where=speed>0)
    p=np.linalg.norm(u.mean(1),axis=-1)
    return d,p
def masks(pos,t):
    d,p=state_values(pos,t); S=upper_half(d);P=upper_half(p)
    return {'S_low':~S,'S_high':S,'P_low':~P,'P_high':P,
      'S_low_P_low':~S&~P,'S_low_P_high':~S&P,'S_high_P_low':S&~P,'S_high_P_high':S&P}
def test():
    rng=np.random.default_rng(47);x=rng.normal(size=(1200,10,2));t=np.arange(33,1188,3)[:384]
    d,p=state_values(x,t);z=x@np.array([[0.,-1.],[-1.,0.]])+10
    a,b=state_values(z,t);np.testing.assert_allclose(d,a,rtol=0,atol=1e-12);np.testing.assert_allclose(p,b,rtol=0,atol=1e-12)
    m=masks(x,t);assert m['S_low'].sum()==len(t)//2 and m['P_high'].sum()==len(t)//2
    assert np.all(sum(m[k].astype(int) for k in CELLS)==1)
    f=np.arange(8);assert np.array_equal(upper_half(np.zeros(8)),f>=4)
    # A modification to a future-only point cannot change the fixed states.
    changed=x.copy();changed[t[-1]+3]+=30
    for k,v in m.items():np.testing.assert_array_equal(v,masks(changed,t)[k])
    print('state invariance, rank tie rule, disjoint masks and future exclusion PASS',flush=True)
def summary(a,seed=20261125):
    a=np.asarray(a,float);assert a.shape==(8,) and np.isfinite(a).all()
    rng=np.random.default_rng(seed);boot=a[rng.integers(8,size=(10000,8))].mean(1)
    loo=np.array([np.delete(a,i).mean() for i in range(8)])
    return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),
     'per_shoal':a.tolist(),'descriptive_bootstrap95':np.quantile(boot,[.025,.975]).tolist(),
     'delete_one_range':[float(loo.min()),float(loo.max())]}
def run():
    parity();test()
    prior=json.loads(REF.read_text());assert prior['status']=='ORIGINAL_EIGHT_ZEBRAFISH_TRIALS_SCORED' and prior['original_archive_sha256']==SHA
    full={};strata={};qc={}
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'data.zip';acquire(path)
        with zipfile.ZipFile(path) as z:
            for name in selected(z):
                _,fields,a=read_header_and_data(z,name)
                f=np.arange(len(a));clock=a[:,0]
                if fields!=HEADER or a.shape!=(54001,31) or not np.isfinite(a).all():raise ValueError('SCHEMA_DRIFT')
                if not (np.diff(clock)>0).all() or np.max(np.abs((clock-clock[0])-f/15))>.0051:raise ValueError('CLOCK_DRIFT')
                pos=np.stack([a[:,[1+3*i,2+3*i]] for i in range(10)],axis=1)
                if not ((pos>=0)&(pos<=1)).all():raise ValueError('XY_DRIFT')
                X,Y,t=panels(f,pos,15)
                if tuple(X)!=MODELS or len(t)!=17986 or len(Y)!=179860:raise ValueError('COHORT_DRIFT')
                m=masks(pos,t)
                qc[name]={'sha256':PINS[Path(name).name],'eligible_group_times':len(t),'state_counts':{k:int(v.sum()) for k,v in m.items()}}
                if any(m[k].sum()<300 for ks in MARGINAL.values() for k in ks):raise ValueError('MARGINAL_SUPPORT_STOP')
                full[name]={k:file_moment(X[k],Y) for k in MODELS}
                strata[name]={}
                for s,v in m.items():
                    if v.sum()<300:continue
                    take=np.repeat(v,10)
                    strata[name][s]={k:file_moment(X[k][take],Y[take]) for k in MODELS}
                print('verified source:',name,'group times',len(t),flush=True)
                del a,pos,X,Y,t
    ids=sorted(full)
    if len(ids)!=8 or set(ids)!=set(prior['source_file_scores']):raise ValueError('ROSTER_DRIFT')
    allscores={};ss={};max_replay=0.;max_partition=0.
    for held in ids:
        train=[i for i in ids if i!=held];assert len(train)==7
        allscores[held]={};ss[held]={s:{} for s in strata[held]}
        for k in MODELS:
            B,b=train_only_standardized_ridge(sum_moments([full[i][k] for i in train]))
            loss=score_file_moment(full[held][k],B,b);allscores[held][k]=loss
            for h in H:
                err=abs(loss[h]-prior['source_file_scores'][held][k][h]);max_replay=max(max_replay,err)
                if err>1e-10:raise ValueError('V46_MSE_REPLAY_STOP')
            for s in strata[held]:
                ss[held][s][k]=score_file_moment(strata[held][s][k],B,b)
            partitions=[*MARGINAL.values(),CELLS]
            for part in partitions:
                if not all(s in ss[held] for s in part):continue
                n=sum(qc[held]['state_counts'][s] for s in part)
                assert n==17986
                for h in H:
                    v=sum(qc[held]['state_counts'][s]*ss[held][s][k][h] for s in part)/n
                    err=abs(v-loss[h]);max_partition=max(max_partition,err)
                    if err>1e-10:raise ValueError('STATE_PARTITION_RECOMBINATION_STOP')
    allowed=[s for s in (*MARGINAL['dispersion'],*MARGINAL['polarization'],*CELLS) if all(s in ss[i] for i in ids)]
    def metric(s,h,key='far_advantage'):
        arr=[]
        for i in ids:
            x={k:ss[i][s][k][h] for k in MODELS}
            g,n,f,r=x['GLOBAL'],x['NEAR_TRUE'],x['FAR_TRUE'],x['NEAR_ROT1']
            if g<=0:raise ValueError('GLOBAL_LOSS_NONPOSITIVE')
            arr.append({'far_advantage':100*(n-f)/g,'absolute_far_advantage':n-f,
             'near_gain':100*(g-n)/g,'far_gain':100*(g-f)/g,'mapping':100*(r-n)/g}[key])
        return np.array(arr)
    metrics=('far_advantage','absolute_far_advantage','near_gain','far_gain','mapping')
    state={h:{s:{k:summary(metric(s,h,k)) for k in metrics} for s in allowed} for h in H}
    mods={}
    for h in H:
        mods[h]={}
        for axis,(lo,hi) in MARGINAL.items():
            mods[h][axis]={k:summary(metric(hi,h,k)-metric(lo,h,k)) for k in metrics}
        if all(c in allowed for c in CELLS):
            low={k:metric('S_high_P_low',h,k)-metric('S_low_P_low',h,k) for k in metrics}
            high={k:metric('S_high_P_high',h,k)-metric('S_low_P_high',h,k) for k in metrics}
            mods[h]['dispersion_within_P_low']={k:summary(v) for k,v in low.items()}
            mods[h]['dispersion_within_P_high']={k:summary(v) for k,v in high.items()}
            mods[h]['interaction']={k:summary(high[k]-low[k]) for k in metrics}
    primary=mods['delayed']['dispersion']['far_advantage']
    ok=primary['mean']>0 and primary['positive']>=6 and primary['delete_one_range'][0]>0
    return {'status':'V47_SOURCE_STATE_STRATIFIED_SCORED','scientific_status':'DISPERSION_DIRECTION_SUPPORTED_EXPLORATORY' if ok else 'DISPERSION_DIRECTION_NOT_SUPPORTED','prior_hierarchy_status':prior['scientific_status'],'source_archive_sha256':SHA,
       'source_unit_order':ids,'source_QC':qc,'max_v46_loss_replay_error':max_replay,'max_state_partition_recombination_error':max_partition,
       'all_2x2_cells_admitted':all(c in allowed for c in CELLS),'primary_delayed_dispersion_far_advantage':primary,
       'state_summaries':state,'state_moderation':mods,'source_safe_state_MSE':ss,
       'raw_coordinates_or_coefficients_exported':False,'physical_room_or_corridor_identified':False,'causal_interpretation':False}
if __name__=='__main__':
    p=Path('validation_fish_school_v47/results/state.json');p.parent.mkdir(parents=True,exist_ok=True)
    try:o=run()
    except Exception as e:
        p.write_text(json.dumps({'status':'SOURCE_OR_MODEL_STOP','reason':str(e)},indent=2)+'\n');raise
    p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in o.items() if k!='source_safe_state_MSE'},sort_keys=True))
