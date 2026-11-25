"""v51: replay all original v48 panels and fit the reduced / raw-local blocks.
Only source-safe aggregate losses are output, not trajectories or coefficients.
"""
import hashlib,json,subprocess,tempfile,zipfile,sys
from pathlib import Path
import numpy as np
from validation_fish_school_v42 import matched_horizons as v42
from validation_fish_school_v46 import zebrafish_holdout as v46
from validation_fish_school_v46.grid_preflight import grid,panels
from validation_fish_school_v45.zebrafish_schema import acquire,selected,read_header_and_data
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
from validation_fish_school_v48.polarization_transfer import states,STATES,PARTS,MODELS,H
PINS={
'tetra':(15002482854,'7ac770a4c2425e7569f265fd690c783cb3d500056d2b13859de215f792afff2e','74afe2917dc7924728330fb8022cb04d7b198bd454729b9416447a23a360e786'),
'ayu':(15003545097,'5c23516a6b807974bbc3694f48ce0902dedf25783d07e6cbbe3fb46f2de9994f','69952920a5ae2bccddac617dfd09a157a492ad2d99ce697bbf35f16d0ca8b465'),
'zebrafish':(15002602208,'96755c92ab081b969af770f727e5a92c05abeb1f2aa43c26f0ff8fdd81e28617','2e365b6975c4d0b37d34b7044aff996e417a935bc4fd1ab267945598375a1943')}
N={'tetra':6,'ayu':7,'zebrafish':8}
ALL=('ALL',)+STATES
RTOL=1e-7;ATOL=1e-10
I=np.eye(18)
RAW=I[:,14:16]+I[:,16:18]
TRANS={'B_check':I[:,:14],'BG_check':I[:,:16],'BGL_check':I,
       'BL':I[:,list(range(14))+[16,17]],'BLraw':np.column_stack((I[:,:14],RAW)),
       'BGLraw':np.column_stack((I[:,:16],RAW))}
def reference(study):
    artifact,zipsha,jsonsha=PINS[study]
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/'prior.zip'
        with p.open('wb') as f:
            subprocess.run(['gh','api',f'/repos/zuizui0223/boids/actions/artifacts/{artifact}/zip'],stdout=f,check=True)
        if hashlib.sha256(p.read_bytes()).hexdigest()!=zipsha:raise ValueError('V48_ZIP_DRIFT')
        with zipfile.ZipFile(p) as z:
            if len(z.namelist())!=1:raise ValueError('V48_ZIP_MEMBERS')
            raw=z.read(z.namelist()[0])
        if hashlib.sha256(raw).hexdigest()!=jsonsha:raise ValueError('V48_JSON_DRIFT')
    j=json.loads(raw)
    assert j['study']==study and j['status']=='V48_ORIGINAL_STATE_TRANSFER_SCORED'
    assert j['n']==N[study] and j['joint_speed_strata_admitted'] is True
    return j
def transform(m,T):
    assert m['sx'].shape==(18,) and T.shape[0]==18
    return {'n':m['n'],'sx':T.T@m['sx'],'sxx':T.T@m['sxx']@T,'sxy':T.T@m['sxy'],'sy':m['sy'].copy(),'syy':m['syy'].copy()}
def test():
    v46.parity()
    rng=np.random.default_rng(51)
    x=rng.normal(size=(3000,18));y=rng.normal(size=(3000,4))+x[:,:4]
    t=rng.normal(size=(1200,18));z=rng.normal(size=(1200,4))
    for k,T in TRANS.items():
        m=transform(file_moment(x,y),T);direct=file_moment(x@T,y)
        for q in ('sx','sxx','sxy','sy','syy'):np.testing.assert_allclose(m[q],direct[q],rtol=1e-10,atol=1e-9)
        B,b=train_only_standardized_ridge(m)
        pred=v46.predict_train_file_only(x@T,y,t@T)
        np.testing.assert_allclose(t@T@B+b,pred,rtol=1e-9,atol=1e-10)
        z0=score_file_moment(transform(file_moment(t,z),T),B,b)
        np.testing.assert_allclose([z0[h] for h in H],[np.mean((z[:,:2]-pred[:,:2])**2),np.mean((z[:,2:]-pred[:,2:])**2)],rtol=1e-9,atol=1e-12)
    print('Six transform moment/direct standardized ridge parity checks PASS',flush=True)
def stats(x,ind):
    x=np.asarray(x,float);assert np.isfinite(x).all()
    loo=[np.delete(x,i,axis=0).mean(axis=0) for i in range(len(x))]
    return {'mean':x.mean(0).tolist(),'positive':(x>0).sum(0).tolist(),'negative':(x<0).sum(0).tolist(),'per_unit':x.tolist(),
            'descriptive_bootstrap95':np.quantile(x[ind].mean(1),[.025,.975],axis=0).tolist(),'delete_one_range':[np.min(loo,0).tolist(),np.max(loo,0).tolist()]}
def ratio_result(num,den,ind):
    n=len(num);assert num.shape==den.shape==(n,2)
    # Also retain per-horizon ratios when only the other horizon has bad denominators.
    positive=(den>0).sum(0).tolist()
    means=[float(100*num[:,h].mean()/den[:,h].mean()) if positive[h]==n else None for h in range(2)]
    if not (den>0).all():
        return {'status':'NONPOSITIVE_DENOMINATOR_STOP','positive_denominator_counts':positive,'ratio_percent':means}
    r=100*num.mean(0)/den.mean(0);delta=float(r[1]-r[0]);ud=100*np.diff(num/den,axis=1).ravel()
    boot=100*np.diff(num[ind].mean(1)/den[ind].mean(1),axis=1).ravel()
    loo=[float(100*np.diff(np.delete(num,i,0).mean(0)/np.delete(den,i,0).mean(0))[0]) for i in range(n)]
    return {'status':'ADMITTED','ratio_percent':r.tolist(),'change_pp':delta,'decrease_count':int((ud<0).sum()),'per_unit_change_pp':ud.tolist(),
            'bootstrap95_pp':np.quantile(boot,[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)],
            'negative_direction_gate_pass':bool(delta<0 and (ud<0).sum()>=np.ceil(.75*n) and max(loo)<0)}
def polarization_contrast(lo,hi,ind):
    # Each tuple: (PhiL, PhiG); compare ratio of equal-unit means at fixed horizon.
    nl,dl=lo;nh,dh=hi;n=len(nl);o={}
    for hidx,h in enumerate(H):
        d1=dl[:,hidx];d2=dh[:,hidx];l1=nl[:,hidx];l2=nh[:,hidx]
        counts=[int((d1>0).sum()),int((d2>0).sum())]
        if counts!=[n,n]:
            o[h]={'status':'NONPOSITIVE_DENOMINATOR_STOP','positive_denominator_counts_low_high':counts};continue
        def contrast(i):
            return 100*(l1[i].mean(axis=-1)/d1[i].mean(axis=-1)-l2[i].mean(axis=-1)/d2[i].mean(axis=-1))
        v=float(contrast(np.arange(n)));u=100*(l1/d1-l2/d2);bs=contrast(ind)
        loo=[float(contrast(np.delete(np.arange(n),i))) for i in range(n)]
        o[h]={'status':'ADMITTED','low_minus_high_pp':v,'positive_units':int((u>0).sum()),'per_unit_pp':u.tolist(),
              'bootstrap95_pp':np.quantile(bs,[.025,.975]).tolist(),'delete_one_range_pp':[min(loo),max(loo)],
              'positive_direction_gate_pass':bool(v>0 and (u>0).sum()>=np.ceil(.75*n) and min(loo)>0)}
    return o
def summarize(new,ids):
    n=len(ids);ind=np.random.default_rng(20261125).integers(n,size=(10000,n))
    outputs={}
    for encoding,(lk,both) in {'residual':('BL','NEAR_TRUE'),'raw_local':('BLraw','BGLraw')}.items():
        z={};ph={}
        for s in ALL:
            B,BG,BL,BGL=np.array([[[new[i][s][k][h] for h in H] for k in ('G_geometry','GLOBAL',lk,both)] for i in ids]).transpose(1,0,2)
            G0=B-BG;L1=BG-BGL;L0=B-BL;G1=BL-BGL;pg=(G0+G1)/2;pl=(L0+L1)/2
            np.testing.assert_allclose(pg+pl,B-BGL,rtol=1e-10,atol=1e-10)
            np.testing.assert_allclose(G0-G1,L0-L1,rtol=1e-10,atol=1e-10)
            g={'G0':G0,'L1':L1,'L0':L0,'G1':G1,'PhiG':pg,'PhiL':pl,'shared_order_component':G0-G1}
            assert (B>0).all();ph[s]=(pl,pg)
            z[s]={'native_gains':{k:stats(x,ind) for k,x in g.items()},'baseline_normalized_gains_percent':{k:stats(100*x/B,ind) for k,x in g.items()},
                  'ratios':{k:ratio_result(a,b,ind) for k,a,b in [('global_first',L1,G0),('local_first',L0,G1),('order_averaged',pl,pg)]}}
        c={k:polarization_contrast(ph[l],ph[h],ind) for k,l,h in [('all_speed','P_low','P_high'),('low_speed','V_low_P_low','V_low_P_high'),('high_speed','V_high_P_low','V_high_P_high')]}
        outputs[encoding]={'states':z,'polarization_low_minus_high':c}
    return outputs
def run(study):
    test();prior=reference(study); moments={};qc={}
    original=v42.original_panels
    def capture(frame,pos,fps,source_name):
        if fps==15:X,Y,t=panels(frame,pos,15)
        else:
            case=original(frame,pos,fps,source_name);X,Y=case['X'],case['Y'];t=grid(frame,pos,fps)
            if len(t)!=case['n_original_eligible_group_times']:raise ValueError('GRID_REPLAY_STOP')
        n=pos.shape[1]
        if tuple(X)!=MODELS or len(Y)!=len(t)*n:raise ValueError('MODEL_SUPPORT_STOP')
        m=states(pos,t,fps)
        qc[source_name]={'eligible_group_times':len(t),'fish_per_group':n,'state_counts':{k:int(v.sum()) for k,v in m.items()}}
        if qc[source_name]!=prior['source_QC'][source_name]:raise ValueError('V48_STATE_QC_DRIFT')
        if any(v.sum()<200 for v in m.values()):raise ValueError('STATE_SUPPORT_STOP')
        moments[source_name]={'ALL':{k:file_moment(X[k],Y) for k in MODELS}}
        for s,v in m.items():
            take=np.repeat(v,n);moments[source_name][s]={k:file_moment(X[k][take],Y[take]) for k in MODELS}
        print('authenticated state moments',study,source_name,len(t),flush=True)
        return {'eligible_group_times':len(t)}
    if study=='zebrafish':
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'data.zip';acquire(p)
            with zipfile.ZipFile(p) as z:
                for name in selected(z):
                    _,fields,a=read_header_and_data(z,name);f=np.arange(len(a))
                    if fields!=v46.HEADER or a.shape!=(54001,31) or not np.isfinite(a).all() or not (np.diff(a[:,0])>0).all() or np.max(np.abs(a[:,0]-a[0,0]-f/15))>.0051:raise ValueError('ZEBRA_SOURCE_DRIFT')
                    pos=np.stack([a[:,[1+3*i,2+3*i]] for i in range(10)],axis=1)
                    if not ((pos>=0)&(pos<=1)).all():raise ValueError('XY_DRIFT')
                    capture(f,pos,15,name)
        auth={'original_archive_sha256':v46.SHA,'original_all_eight_file_hashes_verified':True}
    else:
        v42.original_panels=capture
        try:_,auth=v42.tetra_cases() if study=='tetra' else v42.ayu_cases('external_ayu')
        finally:v42.original_panels=original
    if auth!=prior['source_authentication']:raise ValueError('AUTHENTICATION_DRIFT')
    ids=sorted(moments)
    if len(ids)!=N[study] or ids!=prior['source_unit_order']:raise ValueError('SOURCE_ROSTER_DRIFT')
    scores={};replay=0.;part=0.;reduced=0.
    for held in ids:
        train=[i for i in ids if i!=held];assert len(train)==len(ids)-1
        scores[held]={s:{} for s in ALL}
        for k in MODELS:
            B,b=train_only_standardized_ridge(sum_moments([moments[i]['ALL'][k] for i in train]))
            for s in ALL:
                v=score_file_moment(moments[held][s][k],B,b)
                old=prior['full_MSE'][held][k] if s=='ALL' else prior['source_safe_state_MSE'][held][s][k]
                for h in H:
                    replay=max(replay,abs(v[h]-old[h]))
                    if not np.isclose(v[h],old[h],rtol=RTOL,atol=ATOL):raise ValueError('V48_MSE_REPLAY_STOP')
                scores[held][s][k]=v
        for k,T in TRANS.items():
            B,b=train_only_standardized_ridge(sum_moments([transform(moments[i]['ALL']['NEAR_TRUE'],T) for i in train]))
            for s in ALL:
                v=score_file_moment(transform(moments[held][s]['NEAR_TRUE'],T),B,b)
                if k in ('B_check','BG_check','BGL_check'):
                    old=scores[held][s][{'B_check':'G_geometry','BG_check':'GLOBAL','BGL_check':'NEAR_TRUE'}[k]]
                    for h in H:
                        reduced=max(reduced,abs(v[h]-old[h]))
                        if not np.isclose(v[h],old[h],rtol=RTOL,atol=ATOL):raise ValueError('REDUCED_MSE_REPLAY_STOP')
                else:scores[held][s][k]=v
        for k in (*MODELS,'BL','BLraw','BGLraw'):
            for pp in PARTS:
                c=qc[held]['state_counts'];total=sum(c[s] for s in pp)
                assert total==qc[held]['eligible_group_times']
                for h in H:
                    v=sum(c[s]*scores[held][s][k][h] for s in pp)/total;old=scores[held]['ALL'][k][h]
                    part=max(part,abs(v-old))
                    if not np.isclose(v,old,rtol=RTOL,atol=ATOL):raise ValueError('PARTITION_REPLAY_STOP')
    result=summarize(scores,ids)
    return {'status':'V51_ORIGINAL_SOURCE_ORDER_TRANSFER_SCORED','study':study,'n':len(ids),'source_unit_order':ids,
       'source_authentication':auth,'source_QC':qc,'prior_v48_artifact_id':PINS[study][0],'prior_v48_zip_sha256':PINS[study][1],
       'max_v48_replay_abs':replay,'max_reduced_replay_abs':reduced,'max_partition_error_abs':part,
       'results':result,'source_safe_model_losses':scores,'raw_positions_or_coefficients_exported':False}
if __name__=='__main__':
    study=sys.argv[1];p=Path(f'validation_fish_school_v51/results/{study}.json');p.parent.mkdir(parents=True,exist_ok=True)
    try:j=run(study)
    except Exception as e:
        p.write_text(json.dumps({'status':'SOURCE_OR_MODEL_STOP','study':study,'reason':str(e)},indent=2)+'\n');raise
    p.write_text(json.dumps(j,indent=2,sort_keys=True)+'\n')
    small={k:{'all':v['states']['ALL']['ratios'],'P_low':v['states']['P_low']['ratios']['order_averaged'],'P_high':v['states']['P_high']['ratios']['order_averaged'],'polarization':v['polarization_low_minus_high']} for k,v in j['results'].items()}
    print(json.dumps({'status':j['status'],'study':study,'n':j['n'],'max_v48_replay_abs':j['max_v48_replay_abs'],'max_reduced_replay_abs':j['max_reduced_replay_abs'],'max_partition_error_abs':j['max_partition_error_abs'],'summary':small},sort_keys=True),flush=True)
