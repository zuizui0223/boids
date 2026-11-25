"""v48 fixed-model polarization x horizon transfer and speed-conditioned sensitivity."""
from pathlib import Path
import hashlib,json,zipfile,tempfile,subprocess,sys
import numpy as np
from validation_fish_school_v42 import matched_horizons as v42
from validation_fish_school_v46 import zebrafish_holdout as v46
from validation_fish_school_v46.grid_preflight import grid,panels
from validation_fish_school_v45.zebrafish_schema import acquire,selected,read_header_and_data
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
MODELS=v46.MODELS; H=v46.H
PINS={'tetra':(14925460476,'1d98e9ec844d742e9f4ebf8427bdb6004d2dbaf9687719bcf098721275ac866f','356102aab4e2afddbd14ae9421e07f8d23eed1aaff577875e8d866ec8eaa49b4'),
      'ayu':(14923998689,'ab935d966b2bca6c54b56a68b8908004b24f625143ffc6f26bf410310466749b','84e30c425ec498b0474ea6be78de506514331f0f49038ce4cf0ebcc3a6676119')}
STATES=('P_low','P_high','V_low','V_high','V_low_P_low','V_low_P_high','V_high_P_low','V_high_P_high')
PARTS=[STATES[:2],STATES[2:4],STATES[4:]]
def prior(study):
    if study=='zebrafish':
        return json.loads(v46.Path('docs/collective_state_synthesis_20261124/V46_SOURCE_SAFE_SCORES_FROM_ORIGINAL_JOB_LOG.json').read_text())
    art,digest,jdigest=PINS[study]
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'prior.zip'
        with p.open('wb') as f:subprocess.run(['gh','api',f'/repos/zuizui0223/boids/actions/artifacts/{art}/zip'],stdout=f,check=True)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('V42_PRIOR_ZIP_DRIFT')
        with zipfile.ZipFile(p) as z:
            if len(z.namelist())!=1:raise ValueError('V42_PRIOR_MEMBERS')
            raw=z.read(z.namelist()[0])
        if hashlib.sha256(raw).hexdigest()!=jdigest:raise ValueError('V42_PRIOR_JSON_DRIFT')
    d=json.loads(raw)
    if d['study']!=study or d['status']!='V42_ORIGINAL_SOURCE_SCORED':raise ValueError('V42_PRIOR_STATUS')
    return d
def high(z):
    if len(z)<400 or not np.isfinite(z).all():raise ValueError('STATE_SUPPORT')
    o=np.argsort(z,kind='stable');m=np.zeros(len(z),bool);m[o[len(z)//2:]]=True
    return m
def states(pos,t,fps):
    s=round(fps*.2);v=(pos[t]-pos[t-s])/.2;speed=np.linalg.norm(v,axis=-1,keepdims=True)
    u=np.divide(v,speed,out=np.zeros_like(v),where=speed>0)
    P=high(np.linalg.norm(u.mean(1),axis=-1));V=high(speed[:,:,0].mean(1))
    return dict(zip(STATES,(~P,P,~V,V,~V&~P,~V&P,V&~P,V&P)))
def stats(a,ind):
    a=np.asarray(a,float);loo=[np.delete(a,i).mean() for i in range(len(a))]
    return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),'per_file':a.tolist(),'descriptive_bootstrap95':np.quantile(a[ind].mean(1),[.025,.975]).tolist(),'delete_one_range':[float(min(loo)),float(max(loo))]}
def run(study):
    v46.parity(); ref=prior(study); full={};sub={};qc={}
    def capture(frame,pos,fps,source_name):
        # Use original v42 source parser and exact six panels; no state-dependent refitting.
        if fps==15:
            X,Y,t=panels(frame,pos,15)
        else:
            case=original(frame,pos,fps,source_name);X,Y=case['X'],case['Y'];t=grid(frame,pos,fps)
            if len(t)!=case['n_original_eligible_group_times']:raise ValueError('GRID_REPLAY')
        if tuple(X)!=MODELS or len(Y)!=len(t)*pos.shape[1]:raise ValueError('SOURCE_COHORT')
        m=states(pos,t,fps);n=pos.shape[1];full[source_name]={k:file_moment(X[k],Y) for k in MODELS};sub[source_name]={}
        qc[source_name]={'eligible_group_times':len(t),'fish_per_group':n,'state_counts':{k:int(v.sum()) for k,v in m.items()}}
        for k in STATES:
            if m[k].sum()<200:
                if k in STATES[:4]:raise ValueError('MARGINAL_STATE_SUPPORT')
                continue
            take=np.repeat(m[k],n);sub[source_name][k]={j:file_moment(X[j][take],Y[take]) for j in MODELS}
        return {'eligible_group_times':len(t)}
    original=v42.original_panels
    if study=='zebrafish':
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'data.zip';acquire(p)
            with zipfile.ZipFile(p) as z:
                for name in selected(z):
                    _,fields,a=read_header_and_data(z,name);f=np.arange(len(a))
                    if fields!=v46.HEADER or a.shape!=(54001,31) or not np.isfinite(a).all() or not (np.diff(a[:,0])>0).all() or np.max(np.abs(a[:,0]-a[0,0]-f/15))>.0051:raise ValueError('ZEBRA_SOURCE_DRIFT')
                    pos=np.stack([a[:,[1+3*i,2+3*i]] for i in range(10)],axis=1)
                    if not ((pos>=0)&(pos<=1)).all():raise ValueError('XY_DRIFT')
                    capture(f,pos,15,name)
                    if qc[name]['eligible_group_times']!=17986:raise ValueError('ZEBRA_GRID_DRIFT')
        auth={'original_archive_sha256':v46.SHA,'original_all_eight_file_hashes_verified':True}
    else:
        v42.original_panels=capture
        try:
            _,auth=v42.tetra_cases() if study=='tetra' else v42.ayu_cases('external_ayu')
        finally:v42.original_panels=original
        for name,v in qc.items():
            if v['eligible_group_times']!=ref['source_cohorts'][name]['n_eligible_group_times']:raise ValueError('V42_GRID_DRIFT')
    ids=sorted(full);n=len(ids);expected={'tetra':6,'ayu':7,'zebrafish':8}[study]
    if n!=expected or set(ids)!=set(ref['source_file_scores']):raise ValueError('SOURCE_ROSTER_DRIFT')
    ss={};fs={};max_replay=0.;max_partition=0.
    for held in ids:
        train=[i for i in ids if i!=held];ss[held]={s:{} for s in sub[held]};fs[held]={}
        for k in MODELS:
            B,b=train_only_standardized_ridge(sum_moments([full[i][k] for i in train]))
            f=score_file_moment(full[held][k],B,b);fs[held][k]=f
            for h in H:
                old=ref['source_file_scores'][held][k][h];max_replay=max(max_replay,abs(f[h]-old))
                if not np.isclose(f[h],old,rtol=1e-7,atol=1e-10):raise ValueError('FULL_MSE_REPLAY_STOP')
            for s in sub[held]:ss[held][s][k]=score_file_moment(sub[held][s][k],B,b)
            for part in PARTS:
                if not all(s in ss[held] for s in part):continue
                counts=qc[held]['state_counts'];total=sum(counts[s] for s in part)
                if total!=qc[held]['eligible_group_times']:raise ValueError('PARTITION_COUNT')
                for h in H:
                    v=sum(counts[s]*ss[held][s][k][h] for s in part)/total;max_partition=max(max_partition,abs(v-f[h]))
                    if not np.isclose(v,f[h],rtol=1e-7,atol=1e-10):raise ValueError('PARTITION_MSE')
    rng=np.random.default_rng(20261125);ind=rng.integers(n,size=(10000,n))
    allowed=[s for s in STATES if all(s in ss[i] for i in ids)];joint=all(s in allowed for s in STATES[4:])
    def far(s,h,scale):
        a=[]
        for i in ids:
            m=ss[i][s];d=m['NEAR_TRUE'][h]-m['FAR_TRUE'][h]
            den={'state_global':m['GLOBAL'][h],'full_global':fs[i]['GLOBAL'][h],'state_geometry':m['G_geometry'][h],'native':1.}[scale]
            if den<=0:raise ValueError('LOSS_DENOMINATOR')
            a.append(d if scale=='native' else 100*d/den)
        return np.array(a)
    out={}
    for scale in ('state_global','full_global','state_geometry','native'):
        o={h:{s:stats(far(s,h,scale),ind) for s in allowed} for h in H}
        def effect(lo,hi,h):return far(hi,h,scale)-far(lo,h,scale)
        def K(lo,hi):return effect(lo,hi,'delayed')-effect(lo,hi,'short')
        o['P_effect']={h:stats(effect('P_low','P_high',h),ind) for h in H}
        o['P_horizon_interaction']=stats(K('P_low','P_high'),ind)
        if joint:
            lo=K('V_low_P_low','V_low_P_high');hi=K('V_high_P_low','V_high_P_high')
            o['P_effect_within_speed']={h:{'low':stats(effect('V_low_P_low','V_low_P_high',h),ind),'high':stats(effect('V_high_P_low','V_high_P_high',h),ind)} for h in H}
            o['P_horizon_low_speed']=stats(lo,ind);o['P_horizon_high_speed']=stats(hi,ind)
            o['P_horizon_speed_equal_weight']=stats((lo+hi)/2,ind);o['speed_moderation_of_K']=stats(hi-lo,ind)
        out[scale]=o
    k=out['state_global']['P_horizon_interaction']
    threshold=int(np.ceil(.75*n));supported=k['mean']>0 and k['positive']>=threshold and k['delete_one_range'][0]>0
    if study=='zebrafish':
        if not np.isclose(k['mean'],.07920515937713973,rtol=0,atol=1e-9):raise ValueError('V47_P_HORIZON_REPLAY_STOP')
    return {'status':'V48_ORIGINAL_STATE_TRANSFER_SCORED','study':study,'scientific_status':('SAME_SOURCE_REPLAY' if study=='zebrafish' else ('TRANSFER_DIRECTION_SUPPORTED_DESCRIPTIVE' if supported else 'TRANSFER_DIRECTION_NOT_SUPPORTED')),'n':n,'source_unit_order':ids,'source_authentication':auth,'source_QC':qc,'source_safe_state_MSE':ss,'full_MSE':fs,'max_prior_replay_error':max_replay,'max_partition_error':max_partition,'joint_speed_strata_admitted':joint,'results':out,'independent_shoals_not_verified':study!='zebrafish','raw_positions_exported':False}
if __name__=='__main__':
    study=sys.argv[1];p=Path(f'validation_fish_school_v48/results/{study}.json');p.parent.mkdir(parents=True,exist_ok=True)
    try:d=run(study)
    except Exception as e:
        p.write_text(json.dumps({'status':'SOURCE_OR_MODEL_STOP','study':study,'reason':str(e)},indent=2)+'\n');raise
    p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k not in ('source_safe_state_MSE','full_MSE','source_QC')},sort_keys=True))
