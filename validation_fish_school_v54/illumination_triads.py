"""v54 independent Liu & Burbano 2025 original illumination experiment.
No fish-level trajectories or fitted coefficients exported.
"""
import argparse,hashlib,itertools,json,io,subprocess,zipfile
from pathlib import Path,PurePosixPath
from collections import Counter
import numpy as np
import pandas as pd
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
from validation_fish_school_v46.zebrafish_holdout import parity

COMMIT='2eb7fdd4172fff870224b7cbc4d7bdb086b5fbf0'
ARCH={'Singles.zip':1,'Pairs.zip':2,'Triads.zip':3}
EXPECTED={'Singles-Bright':10,'Singles-Dark':10,'Pairs-Bright':9,'Pairs-Dark':10,'Triads-Bright':9,'Triads-Dark':10}
PREFIX={1:'Singles',2:'Pairs',3:'Triads'}
MODELS=('B','GLOBAL','NEAR','ROT','STALE')
H=('short','delayed')
OFF=np.array([-11,-10,-6,-5,-3,-2,-1,0,1,3,4])*6
def sha(b):return hashlib.sha256(b).hexdigest()
def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def grid(f,p):
    t=np.arange(66,len(f)-24,6);ix=t[:,None]+OFF
    good=np.isfinite(p[ix]).all((1,2,3))&((f[ix]-f[t,None])==OFF).all(1)
    t=t[good]
    if len(t)<1000:raise ValueError('MIN_GROUP_TIMES_STOP')
    return t
def read_csv(raw,n):
    s=raw.decode('utf-8-sig')
    required=['Frame','Time']+[z for i in range(n) for z in (f'X_Arena0_Ind{i}',f'Y_Arena0_Ind{i}')]
    header=s.splitlines()[0];seps=[sep for sep in (',',';','\t') if header.split(sep)==required]
    if len(seps)!=1:raise ValueError('EXPLICIT_HEADER_MISMATCH:'+header[:180])
    d=pd.read_csv(io.StringIO(s),sep=seps[0],keep_default_na=False,na_values=['','NA','NaN','nan','N/A'])
    if list(d.columns)!=required:raise ValueError('CSV_HEADER_DRIFT')
    a=d.apply(pd.to_numeric,errors='raise').to_numpy(float)
    if not 17000<=len(a)<=18001:raise ValueError('TRIAL_DURATION_STOP')
    f=a[:,0];clock=a[:,1]
    if not (np.isfinite(f).all() and np.isfinite(clock).all() and (f==np.round(f)).all() and (np.diff(f)>0).all() and (np.diff(clock)>0).all()):raise ValueError('NATIVE_CLOCK_STOP')
    err=float(np.max(np.abs(clock-clock[0]-(f-f[0])/30)))
    if err>.0051:raise ValueError('CLOCK_30HZ_DRIFT')
    p=a[:,2:].reshape(len(a),n,2)
    if np.isinf(p).any():raise ValueError('INF_COORDINATE')
    # Check documented cm/tank-centered coordinate support. No centering inferred from outcomes.
    radial=np.linalg.norm(p,axis=-1);rmax=float(np.nanmax(radial))
    if not rmax<=33:raise ValueError('DOCUMENTED_CM_CENTER_SUPPORT_STOP')
    t=grid(f,p)
    return f.astype(np.int64),p,{'rows':len(f),'frame_span':int(f[-1]-f[0]+1),'clock_max_error_s':err,'finite_position_fraction':float(np.isfinite(p).all(-1).mean()),'max_radius_cm':rmax,'eligible_group_times':len(t),'missing_source_frames':int(f[-1]-f[0]+1-len(f))}
def admit(repo,qc):
    if git(repo,'rev-parse','HEAD')!=COMMIT or git(repo,'rev-parse','v1.0.0^{commit}')!=COMMIT:raise ValueError('AUTHOR_RELEASE_DRIFT')
    if git(repo,'rev-parse',COMMIT+':README.md')!='48c0824b55bdd34d280a2e701f4c477b52639ef1':raise ValueError('README_DRIFT')
    if git(repo,'rev-parse',COMMIT+':LICENSE')!='0e259d42c996742e9e3cba14c677129b2c1b6311':raise ValueError('LICENSE_DRIFT')
    data={c:{} for c in EXPECTED};qc.update(author_commit=COMMIT,archive={},trials={})
    for fn,n in ARCH.items():
        path=repo/fn
        expected=git(repo,'rev-parse',COMMIT+':'+fn)
        if git(repo,'hash-object',str(path.resolve()))!=expected:raise ValueError('AUTHOR_ZIP_BLOB_DRIFT')
        if path.stat().st_size>100_000_000:raise ValueError('ARCHIVE_BYTE_CAP')
        qc['archive'][fn]={'git_blob':expected,'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}
        with zipfile.ZipFile(path) as z:
            inf=z.infolist()
            if sum(x.file_size for x in inf)>300_000_000 or len({x.filename for x in inf})!=len(inf):raise ValueError('ZIP_CAP_OR_DUPLICATE')
            qc['archive'][fn]['member_paths']=[x.filename for x in inf if not x.is_dir() and not x.filename.startswith('__MACOSX/')]
            for item in inf:
                name=item.filename;p=PurePosixPath(name)
                if p.is_absolute() or '..' in p.parts or '\\' in name:raise ValueError('UNSAFE_ARCHIVE_PATH')
                if item.is_dir() or '__MACOSX' in p.parts or p.name.startswith('.'):continue
                if p.suffix.lower()!='.csv':continue
                c=[k for k in EXPECTED if k.startswith(PREFIX[n]+'-') and k in p.parts[:-1]]
                if len(c)!=1:raise ValueError('TRIAL_CONDITION_PATH_STOP:'+name)
                if item.file_size>20_000_000:raise ValueError('CSV_CAP')
                raw=z.read(item);key=fn+'/'+name
                row={'condition':c[0],'csv_sha256':sha(raw),'csv_bytes':len(raw),'header':raw.splitlines()[0].decode('utf-8-sig')[:300]}
                qc['trials'][key]=row
                f,a,meta=read_csv(raw,n);row.update(meta);data[c[0]][key]=(f,a)
                print('authenticated trial',c[0],p.name,meta['rows'],meta['eligible_group_times'],flush=True)
    counts={k:len(v) for k,v in data.items()};qc['trial_counts']=counts
    if counts!=EXPECTED:raise ValueError('PUBLISHED_58_TRIAL_ROSTER_STOP')
    return data
def panels(f,p,key):
    assert p.shape[1:]==(3,2)
    t=grid(f,p);now=p[t];v=(now-p[t-6])/.2;old=(p[t-6]-p[t-12])/.2
    off=now[:,None,:,:]-now[:,:,None,:];d2=np.sum(off**2,-1);i=np.arange(3);d2[:,i,i]=np.inf
    nearest=np.argmin(d2,axis=2);assert not np.any(nearest==i[None,:])
    idx=np.arange(len(t))[:,None];focus=np.arange(3)[None,:]
    other=(v.sum(1,keepdims=True)-v)/2;pastother=(old.sum(1,keepdims=True)-old)/2
    near=v[idx,nearest]-other;past=old[idx,nearest]-pastother;g=other-v
    # Fixed, independent local label swap. Always retain the same global mean.
    seed=int.from_bytes(hashlib.sha256(('v54-fixed-swap:'+key).encode()).digest()[:8],'little')
    sign=np.random.default_rng(seed).choice([-1.,1.],size=near.shape[:2])
    rot=near*sign[:,:,None]
    G=np.concatenate((now,v,old,v-old,np.linalg.norm(v,axis=-1,keepdims=True),now.mean(1,keepdims=True)-now,off[idx,focus,nearest],np.sqrt(d2[idx,focus,nearest])[:,:,None]),axis=-1)
    # 14-D baseline: 2+2+2+2+1+2+2+1.
    assert G.shape[-1]==14
    x,y=now[:,:,0],now[:,:,1];vx,vy=v[:,:,0],v[:,:,1];r=np.sqrt(x*x+y*y)
    radial=np.divide(x*vx+y*vy,r,out=np.zeros_like(r),where=r>0)
    tang=np.divide(x*vy-y*vx,r,out=np.zeros_like(r),where=r>0)
    E=np.stack((x*x,x*y,y*y,x*vx,x*vy,y*vx,y*vy,r,radial,tang),-1)
    target=np.concatenate(((p[t+6]-now)/.2,(p[t+24]-p[t+18])/.2),axis=-1).reshape(-1,4)
    out={}
    for label,b in [('base',G),('geometry',np.concatenate((G,E),-1))]:
        bg=np.concatenate((b,g),-1)
        out[label]={'B':b.reshape(-1,b.shape[-1]),'GLOBAL':bg.reshape(-1,bg.shape[-1])}
        for k,u in [('NEAR',near),('ROT',rot),('STALE',past)]:
            z=np.concatenate((bg,u),-1);out[label][k]=z.reshape(-1,z.shape[-1])
        assert tuple(out[label])==MODELS and all(len(z)==len(target) and np.isfinite(z).all() for z in out[label].values())
    return out,target,t
def tests():
    parity()
    rng=np.random.default_rng(54);f=np.arange(18000);p=rng.normal(size=(len(f),3,2))
    X,Y,t=panels(f,p,'fixture')
    z=p.copy();z[t[-1]+24]+=5;XX,YY,tt=panels(f,z,'fixture')
    np.testing.assert_array_equal(t,tt)
    for a in X:
        for k in MODELS:np.testing.assert_array_equal(X[a][k],XX[a][k])
    assert not np.array_equal(Y,YY)
    for a in X:
        n=X[a]['NEAR'][:,-2:];r=X[a]['ROT'][:,-2:];np.testing.assert_array_equal(np.abs(n),np.abs(r))
        np.testing.assert_array_equal(X[a]['NEAR'][:,:-2],X[a]['ROT'][:,:-2])
    print('v54 frozen group support, future exclusion and global-preserving randomized local assignment PASS',flush=True)
def moments(f,p,key):
    X,Y,t=panels(f,p,key)
    return {a:{k:file_moment(X[a][k],Y) for k in MODELS} for a in X},len(t)
def eval_ensemble(trainsets,ms,target):
    scores={a:{k:{h:[] for h in H} for k in MODELS} for a in ('base','geometry')}
    for train in trainsets:
        assert len(train)==8 and len(set(train))==8
        for a in scores:
            for k in MODELS:
                B,b=train_only_standardized_ridge(sum_moments([ms[i][a][k] for i in train]))
                val=score_file_moment(target[a][k],B,b)
                for h in H:scores[a][k][h].append(val[h])
    return {a:{k:{h:float(np.mean(v[h])) for h in H} for k,v in m.items()} for a,m in scores.items()}
def score_data(data,qc):
    ms={};counts={}
    for c in ('Triads-Bright','Triads-Dark'):
        for key,(f,p) in data[c].items():
            ms[key],counts[key]=moments(f,p,key)
            if counts[key]!=qc['trials'][key]['eligible_group_times']:raise ValueError('SOURCE_COHORT_DRIFT')
    real={}
    for light in ('Bright','Dark'):
        ids=sorted(data['Triads-'+light]);real[light]={}
        for held in ids:
            train=[i for i in ids if i!=held];sets=list(itertools.combinations(train,8))
            assert held not in {i for s in sets for i in s}
            real[light][held]=eval_ensemble(sets,ms,ms[held])
    pseudo={};pseudo_qc={}
    for light in ('Bright','Dark'):
        singles=sorted(data['Singles-'+light]);triads=sorted(data['Triads-'+light]);sets=list(itertools.combinations(triads,8));pseudo[light]={}
        pseudo_qc[light]={'unused_single':singles[-1],'groups':{}}
        for k in range(3):
            chosen=singles[3*k:3*k+3];src=[data['Singles-'+light][i] for i in chosen];key='pseudo-'+light+'-'+str(k)
            fs=[f-f[0] for f,p in src];common=np.array(sorted(set(fs[0])&set(fs[1])&set(fs[2])),dtype=int)
            try:
                if len(common)<17000:raise ValueError('PSEUDO_CLOCK_SUPPORT')
                pos=np.concatenate([p[np.searchsorted(ff,common)] for ff,(f,p) in zip(fs,src)],axis=1)
                mm,n=moments(common,pos,key);pseudo[light][key]=eval_ensemble(sets,ms,mm)
                pseudo_qc[light]['groups'][key]={'source_singles':chosen,'eligible_group_times':n,'status':'ADMITTED'}
            except ValueError as e:pseudo_qc[light]['groups'][key]={'source_singles':chosen,'status':'PSEUDO_STOP','reason':str(e)}
    return real,pseudo,pseudo_qc

def summarize(real):
    rng=np.random.default_rng(20261125)
    def stats(a):
        a=np.asarray(a);return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),'per_trial':a.tolist()}
    def compare(a,b):
        ia=rng.integers(len(a),size=(10000,len(a)));ib=rng.integers(len(b),size=(10000,len(b)))
        boot=a[ia].mean(1)-b[ib].mean(1)
        loo=[np.delete(a,i).mean()-b.mean() for i in range(len(a))]+[a.mean()-np.delete(b,i).mean() for i in range(len(b))]
        return {'bright':stats(a),'dark':stats(b),'bright_minus_dark':float(a.mean()-b.mean()),'descriptive_bootstrap95':np.quantile(boot,[.025,.975]).tolist(),'delete_one_range':[float(min(loo)),float(max(loo))]}
    z={}
    for mode in ('base','geometry'):
        z[mode]={}
        for h in H:
            z[mode][h]={}
            for metric in ('assignment','local','global','assignment_native','assignment_base_norm','local_total_share'):
                vals={}
                for light in ('Bright','Dark'):
                    ls=[real[light][i][mode] for i in sorted(real[light])]
                    B,G,N,R,S=np.array([[v[k][h] for k in MODELS] for v in ls]).T
                    if (B<=0).any() or (G<=0).any():raise ValueError('NONPOSITIVE_BASE_LOSS')
                    if metric=='local_total_share' and (B-N<=0).any():vals[light]=None;continue
                    vals[light]={'assignment':lambda:100*(R-N)/G,'local':lambda:100*(G-N)/G,'global':lambda:100*(B-G)/B,'assignment_native':lambda:R-N,'assignment_base_norm':lambda:100*(R-N)/B,'local_total_share':lambda:100*(G-N)/(B-N)}[metric]()
                if any(v is None for v in vals.values()):z[mode][h][metric]={'status':'NONPOSITIVE_TOTAL_GAIN_STOP'};continue
                z[mode][h][metric]=compare(vals['Bright'],vals['Dark'])
    p=z['base']['short']['assignment'];support=p['bright_minus_dark']>0 and p['bright']['mean']>0 and p['bright']['positive']>=7 and p['delete_one_range'][0]>0 and p['descriptive_bootstrap95'][0]>0
    return z,'PRIMARY_DIRECTION_SUPPORTED_DESCRIPTIVE' if support else 'PRIMARY_DIRECTION_NOT_SUPPORTED'
def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args()
    o={'status':'SOURCE_OR_MODEL_STOP','source_QC':{},'raw_positions_or_coefficients_exported':False}
    try:
        tests()
        data=admit(a.source,o['source_QC'])
        o['source_status']='ALL_58_ORIGINAL_TRIALS_ADMITTED'
        r,p,pq=score_data(data,o['source_QC']);s,decision=summarize(r)
        o.update(status='V54_INDEPENDENT_ILLUMINATION_TRIADS_SCORED',scientific_status=decision,real_heldout_MSE=r,pseudo_control_MSE=p,pseudo_QC=pq,results=s,source_independence='Authors report no fish reuse; source trial identities verified; not independent population samples.')
    except Exception as e:
        o['reason']=str(e)[:600];o['error_type']=type(e).__name__
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in o.items() if k not in ('source_QC','real_heldout_MSE','pseudo_control_MSE')},sort_keys=True),flush=True)
    if o['status']!='V54_INDEPENDENT_ILLUMINATION_TRIADS_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
