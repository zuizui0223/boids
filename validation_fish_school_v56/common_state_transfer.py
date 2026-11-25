"""v56: v55 exact source replay, common-state standardized score and cross-light transfer.
All reported quantities are heldout predictive losses or structural counts.
No raw fish coordinates, timestamps or fitted coefficients exported.
"""
import argparse,itertools,json,re,zipfile,hashlib
from pathlib import Path
import numpy as np
from validation_fish_school_v54 import illumination_triads as v54
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
PIN_ZIP='252458a040349cc881b77dfcccea0996cdaaffbbb998df4d3e03a4cbde63ea11'
PIN_JSON='9026c9109c6bf1ebf3a1a00c2d8f56e6b2cc2d6ce878b2a64f457a57762272ef'
LIGHTS=('Bright','Dark'); MODES=('base','geometry'); MODELS=v54.MODELS; H=v54.H
RTOL=1e-7;ATOL=1e-10
def sha(b):return hashlib.sha256(b).hexdigest()
def ref(path):
    assert sha(path.read_bytes())==PIN_ZIP
    with zipfile.ZipFile(path) as z:
        assert len(z.namelist())==1
        raw=z.read(z.namelist()[0]);assert sha(raw)==PIN_JSON
    j=json.loads(raw)
    assert j['status']=='V55_ARCHIVE_NATIVE_ILLUMINATION_SCORED' and j['primary_window']=='full_archive'
    assert j['source_status']=='ALL_58_ORIGINAL_TRIALS_ADMITTED_NATIVE_COORDINATES'
    return j
def state_values(f,p,t):
    # Same current 0.2-s velocity used in v54. No target values in states.
    now=p[t];v=(now-p[t-6])/.2
    speed=np.linalg.norm(v,axis=-1)
    u=np.divide(v,speed[:,:,None],out=np.zeros_like(v),where=speed[:,:,None]>0)
    pol=np.linalg.norm(u.mean(1),axis=-1)
    d=np.linalg.norm(now[:,None,:,:]-now[:,:,None,:],axis=-1)
    i=np.arange(3);d[:,i,i]=np.inf
    nearest=d.min(2).mean(1)
    out=np.column_stack((speed.mean(1),nearest,pol))
    assert np.isfinite(out).all()
    return out
def cell_index(z,cut):
    return (z>cut).astype(int)@np.array([4,2,1])
def native_panels(f,p,key):
    X,Y,t=v54.panels(f,p,key)
    for k,x in X['geometry'].items():
        X['geometry'][k]=np.concatenate((x[:,:21],x[:,24:]),axis=1)
    return X,Y,t
def small_moment(x,y):
    # Same sufficient statistic as v32, without its source-training minimum.
    # These are heldout cells only, NEVER individual training fits.
    x=np.asarray(x,dtype=np.float64);y=np.asarray(y,dtype=np.float64)
    assert x.ndim==2 and y.shape==(len(x),4) and len(x)>=90 and np.isfinite(x).all() and np.isfinite(y).all()
    return {'n':int(len(x)),'sx':x.sum(0),'sxx':x.T@x,'sxy':x.T@y,'sy':y.sum(0),'syy':(y*y).sum(0)}
def verify():
    v54.tests()
    rng=np.random.default_rng(56);f=np.arange(18000);p=rng.normal(size=(len(f),3,2))
    X,Y,t=native_panels(f,p,'fixture-v56');z=state_values(f,p,t);cut=np.median(z,0);c=cell_index(z,cut)
    assert np.all((c>=0)&(c<8))
    a=p.copy();a[t[-1]+24]+=100
    np.testing.assert_array_equal(z,state_values(f,a,t))
    # Invariance of state values under common rotation/reflection/translation of source axes.
    q=p@np.array([[0.,-1.],[-1.,0.]])+10.
    np.testing.assert_allclose(z,state_values(f,q,t),atol=1e-10,rtol=1e-10)
    m=small_moment(X['base']['GLOBAL'],Y);d=file_moment(X['base']['GLOBAL'],Y)
    for k in m:np.testing.assert_allclose(m[k],d[k],rtol=1e-10,atol=1e-10)
    print('v56 synthetic state invariance, future exclusion, and heldout moment parity PASS',flush=True)
def mean_score(scores):
    return {h:float(np.mean([s[h] for s in scores])) for h in H}
def compare(a,b,seed=20261125):
    a=np.asarray(a,float);b=np.asarray(b,float)
    rng=np.random.default_rng(seed);ia=rng.integers(len(a),size=(10000,len(a)));ib=rng.integers(len(b),size=(10000,len(b)))
    d=a[ia].mean(1)-b[ib].mean(1)
    loo=[np.delete(a,i).mean()-b.mean() for i in range(len(a))]+[a.mean()-np.delete(b,i).mean() for i in range(len(b))]
    return {'bright_mean':float(a.mean()),'dark_mean':float(b.mean()),'bright_positive':int((a>0).sum()),'dark_positive':int((b>0).sum()),'contrast_pp':float(a.mean()-b.mean()),'bootstrap95':np.quantile(d,[.025,.975]).tolist(),'delete_one_range':[float(min(loo)),float(max(loo))],'bright_per_trial':a.tolist(),'dark_per_trial':b.tolist()}
def within(a,seed=20261125):
    a=np.asarray(a,float);n=len(a);rng=np.random.default_rng(seed);ind=rng.integers(n,size=(10000,n))
    return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),'bootstrap95':np.quantile(a[ind].mean(1),[.025,.975]).tolist(),'per_trial':a.tolist()}
def contrasts(rows,ids):
    out={}
    for mode in MODES:
        out[mode]={}
        for h in H:
            m={}
            for light in LIGHTS:
                a=np.array([[rows[i][mode][k][h] for k in MODELS] for i in ids[light]])
                B,G,N,R,S=a.T
                assert np.isfinite(a).all() and (B>0).all() and (G>0).all()
                m[light]={'assignment':100*(R-N)/G,'assignment_native':R-N,'assignment_base_norm':100*(R-N)/B,
                'local':100*(G-N)/G,'global':100*(B-G)/B,'stale':100*(S-N)/G}
            out[mode][h]={k:compare(m['Bright'][k],m['Dark'][k]) for k in m['Bright']}
    p=out['base']['short']['assignment'];ok=p['contrast_pp']>0 and p['bright_mean']>0 and p['bright_positive']>=7 and p['delete_one_range'][0]>0 and p['bootstrap95'][0]>0
    return {'decision':'DIRECTION_SUPPORTED_DESCRIPTIVE' if ok else 'DIRECTION_NOT_SUPPORTED','results':out}
def transfer(same,cross,ids):
    out={}
    for mode in MODES:
        out[mode]={}
        for h in H:
            result={}
            for light in LIGHTS:
                s=np.array([[same[i][mode][k][h] for k in MODELS] for i in ids[light]])
                c=np.array([[cross[i][mode][k][h] for k in MODELS] for i in ids[light]])
                assert (s>0).all() and (c>0).all()
                rel=100*(c-s)/s
                j={k:within(rel[:,q]) for q,k in enumerate(MODELS)}
                ix={k:q for q,k in enumerate(MODELS)}
                g,n,r,b=(ix[k] for k in ('GLOBAL','NEAR','ROT','B'))
                A1=100*(s[:,r]-s[:,n])/s[:,g];A2=100*(c[:,r]-c[:,n])/c[:,g]
                j['cross_minus_same_assignment_pp']=within(A2-A1)
                j['cross_excess_NEAR_minus_B_pp']=within(rel[:,n]-rel[:,b])
                result[light]=j
            out[mode][h]=result
    return out
def run(source,diag,prior,out):
    verify();original=ref(prior);qc={};data=v55.admit(source,v55.reference(diag),qc)
    assert qc==original['source_QC']
    ids={light:sorted(data['Triads-'+light]) for light in LIGHTS}
    assert [len(ids[l]) for l in LIGHTS]==[9,10]
    records={};zs={}
    for light in LIGHTS:
        for key,(f,p) in data['Triads-'+light].items():
            X,Y,t=native_panels(f,p,key);records[key]=(X,Y,t)
            assert len(t)==original['windows']['full_archive']['window_group_times'][key]
            zs[key]=state_values(f,p,t)
    cut=np.median(np.concatenate([zs[i] for light in LIGHTS for i in ids[light]],0),axis=0)
    codes={i:cell_index(z,cut) for i,z in zs.items()}
    counts={i:np.bincount(c,minlength=8) for i,c in codes.items()}
    n=np.array([counts[i].sum() for light in LIGHTS for i in ids[light]])
    C=np.array([counts[i] for light in LIGHTS for i in ids[light]])
    support=(C>=30).all(0);mins=np.min(C/n[:,None],axis=0);w0=np.where(support,mins,0.);mass=float(w0.sum())
    ok=bool(support.sum()>=2 and mass>=.20)
    w=w0/mass if mass>0 else w0
    out.update(source_QC={'original_58_files_reauthenticated':True,'original_source_QC_exact_replay':True,'trial_counts':{k:len(v) for k,v in ids.items()}},
      state_support={'covariates':['group_mean_speed','mean_nearest_distance','polarization'],'pooled_medians_native_units':cut.tolist(),
      'counts_by_trial':{k:v.tolist() for k,v in counts.items()},'min_fractions':mins.tolist(),'supported_cells':np.where(support)[0].tolist(),
      'unnormalized_overlap_mass':mass,'target_weights':w.tolist(),'mass_per_trial_in_supported_cells':{i:float(counts[i][support].sum()/counts[i].sum()) for i in counts},
      'admitted':ok,'decision':'ADMITTED' if ok else 'COMMON_STATE_SUPPORT_STOP'})
    full={};cells={};max_replay=0.;max_partition=0.
    for i,(X,Y,t) in records.items():
        full[i]={a:{k:file_moment(X[a][k],Y) for k in MODELS} for a in MODES}
        # For exact partition replay include every nonempty cell, even if unsupported.
        # score_file_moment accepts positive n; small_moment >=90 for admitted cells.
        cells[i]={}
        for c in range(8):
            take=np.repeat(codes[i]==c,3)
            if not take.any():continue
            def m(x,y):
                if len(x)>=90:return small_moment(x,y)
                return {'n':int(len(x)),'sx':x.sum(0),'sxx':x.T@x,'sxy':x.T@y,'sy':y.sum(0),'syy':(y*y).sum(0)}
            cells[i][c]={a:{k:m(X[a][k][take],Y[take]) for k in MODELS} for a in MODES}
    # Fit each unique 8-trial training combination only once. Reuse coefficients internally.
    ensembles={light:list(itertools.combinations(ids[light],8)) for light in LIGHTS}
    assert [len(ensembles[l]) for l in LIGHTS]==[9,45]
    fits={}
    for light in LIGHTS:
        fits[light]={}
        for tr in ensembles[light]:
            fits[light][tr]={a:{k:train_only_standardized_ridge(sum_moments([full[i][a][k] for i in tr])) for k in MODELS} for a in MODES}
    same={};cross={};stdsame={};stdcross={}
    for light in LIGHTS:
        other='Dark' if light=='Bright' else 'Bright'
        for i in ids[light]:
            for src,chosen,fout,sout in [(light,[tr for tr in ensembles[light] if i not in tr],same,stdsame),(other,ensembles[other],cross,stdcross)]:
                assert len(chosen)==((1 if light=='Bright' else 9) if src==light else (45 if light=='Bright' else 9))
                fout[i]={};sout[i]={}
                for a in MODES:
                    fout[i][a]={};sout[i][a]={}
                    for k in MODELS:
                        scores=[];std=[]
                        for tr in chosen:
                            beta,bias=fits[src][tr][a][k]
                            s=score_file_moment(full[i][a][k],beta,bias);scores.append(s)
                            cm={c:score_file_moment(mm[a][k],beta,bias) for c,mm in cells[i].items()}
                            for h in H:
                                back=sum(counts[i][c]*val[h] for c,val in cm.items())/counts[i].sum()
                                max_partition=max(max_partition,abs(back-s[h]))
                                if not np.isclose(back,s[h],rtol=RTOL,atol=ATOL):raise ValueError('CELL_PARTITION_LOSS_REPLAY_STOP')
                            if ok:std.append({h:sum(w[c]*cm[c][h] for c in np.where(support)[0]) for h in H})
                        fout[i][a][k]=mean_score(scores)
                        if ok:sout[i][a][k]=mean_score(std)
                        if src==light:
                            prior_score=original['windows']['full_archive']['real_heldout_MSE'][light][i][a][k]
                            for h in H:
                                err=abs(fout[i][a][k][h]-prior_score[h]);max_replay=max(max_replay,err)
                                if not np.isclose(fout[i][a][k][h],prior_score[h],rtol=RTOL,atol=ATOL):raise ValueError('V55_FULL_LOSS_REPLAY_STOP')
            print('all original model scores replayed and transfer scored',light,i,flush=True)
    out['max_v55_same_light_abs_replay_error']=max_replay;out['max_cell_partition_abs_error']=max_partition
    out['training_combinations']={l:len(v) for l,v in ensembles.items()}
    out['trial_order']=ids;out['full_same_light']=contrasts(same,ids);out['full_cross_light']=contrasts(cross,ids);out['full_transfer']=transfer(same,cross,ids)
    out['source_safe_MSE']={'full_same':same,'full_cross':cross}
    if ok:
        out['standardized_same_light']=contrasts(stdsame,ids);out['standardized_cross_light']=contrasts(stdcross,ids)
        out['standardized_transfer']=transfer(stdsame,stdcross,ids);out['source_safe_MSE'].update(std_same=stdsame,std_cross=stdcross)
        changes={}
        for a in MODES:
            changes[a]={}
            for h in H:
                d={}
                for light in LIGHTS:
                    d[light]=np.array([100*((stdsame[i][a]['ROT'][h]-stdsame[i][a]['NEAR'][h])/stdsame[i][a]['GLOBAL'][h]-(same[i][a]['ROT'][h]-same[i][a]['NEAR'][h])/same[i][a]['GLOBAL'][h]) for i in ids[light]])
                changes[a][h]=compare(d['Bright'],d['Dark'])
        out['standardized_minus_full_assignment_change']=changes
        out['scientific_status']=out['standardized_same_light']['decision']
    else:
        out['scientific_status']='COMMON_STATE_SUPPORT_STOP'
    # Token-based day sensitivity, no claim of independently verified calendar dates.
    by={}
    for light in LIGHTS:
        for i in ids[light]:
            m=re.search(r'temp-(\d{8})\d{6}_Corrected\.csv$',i)
            if not m:raise ValueError('DATE_TOKEN_SCHEMA_STOP')
            by.setdefault(m.group(1),{l:[] for l in LIGHTS})[light].append(i)
    days={}
    for date,z in sorted(by.items()):
        row={'counts':{l:len(z[l]) for l in LIGHTS},'available_same_light_training_if_whole_date_heldout':{l:len(ids[l])-len(z[l]) for l in LIGHTS},'full_assignment':{}}
        for a in MODES:
            row['full_assignment'][a]={}
            for h in H:
                A={l:[100*(same[i][a]['ROT'][h]-same[i][a]['NEAR'][h])/same[i][a]['GLOBAL'][h] for i in z[l]] for l in LIGHTS}
                row['full_assignment'][a][h]={'condition_means':{l:float(np.mean(v)) if v else None for l,v in A.items()},'bright_minus_dark':float(np.mean(A['Bright'])-np.mean(A['Dark'])) if all(A.values()) else None}
        days[date]=row
    out['filename_date_token_sensitivity']=days
    out.update(status='V56_ORIGINAL_TRIAD_TRANSFER_AND_STATE_SCORED',prior_v55_zip_sha256=PIN_ZIP,prior_v55_json_sha256=PIN_JSON,raw_positions_or_coefficients_exported=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--diagnostic',type=Path,required=True);ap.add_argument('--prior',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a.source,a.diagnostic,a.prior,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:600],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    small={k:v for k,v in o.items() if k not in ('source_safe_MSE','trial_order')}
    # Compact useful log; original artifact contains full results and per-trial scores.
    for k in ('full_same_light','full_cross_light','standardized_same_light','standardized_cross_light'):
        if k in small:small[k]={'decision':small[k]['decision'],'assignment':{a:{h:small[k]['results'][a][h]['assignment'] for h in H} for a in MODES}}
    for k in ('full_transfer','standardized_transfer'):
        if k in small:small[k]={a:{h:{l:{j:v['mean'] for j,v in m.items()} for l,m in z.items()} for h,z in v.items()} for a,v in small[k].items()}
    print(json.dumps(small,sort_keys=True),flush=True)
    if o['status']!='V56_ORIGINAL_TRIAD_TRANSFER_AND_STATE_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
