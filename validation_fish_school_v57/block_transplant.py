"""v57 same-study coefficient-block transplant and signed Shapley loss allocation.
No raw trajectories or fitted coefficients exported. Source gates precede scoring.
"""
import argparse,hashlib,itertools,json,math,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v54 import illumination_triads as v54
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment

PIN_ZIP='fdefee8d9927286f3c61953b11a5967bef8aa5603e2c16a17bfb67f43114a8ca'
PIN_JSON='dbe0f7d18184e3b2af977db6f19aff60f09ae8282e69551962a69803ee731411'
LIGHTS=('Bright','Dark'); MODES=('base','geometry'); MODELS=v54.MODELS; H=v54.H
BLOCKS=('B','G','N'); SUBSETS=tuple(range(8)); CONVENTIONS=('raw_origin','test_covariate_mean')
RTOL=1e-7;ATOL=1e-10

def reference(path):
    rawzip=path.read_bytes()
    assert hashlib.sha256(rawzip).hexdigest()==PIN_ZIP
    with zipfile.ZipFile(path) as z:
        assert len(z.namelist())==1
        raw=z.read(z.namelist()[0])
    assert hashlib.sha256(raw).hexdigest()==PIN_JSON
    j=json.loads(raw)
    assert j['status']=='V56_ORIGINAL_TRIAD_TRANSFER_AND_STATE_SCORED'
    assert j['scientific_status']=='COMMON_STATE_SUPPORT_STOP'
    return j

def hybrid(s,o,mask,r):
    bs,as_=s;bo,ao=o;d=len(bs)
    assert d>=4 and bs.shape==bo.shape and r.shape==(d,)
    b=bs.copy()
    parts=(slice(None,-4),slice(-4,-2),slice(-2,None))
    for q,part in enumerate(parts):
        if mask&(1<<q):b[part]=bo[part]
    # Affine intercept at the common anchor belongs to B.
    anchor=ao+r@bo if mask&1 else as_+r@bs
    return b,anchor-r@b

def allocation(v):
    """v[subset mask, horizon], three-block Shapley exact order average."""
    v=np.asarray(v,float);assert v.shape==(8,2)
    phi=np.zeros((3,2))
    for order in itertools.permutations(range(3)):
        mask=0
        for q in order:
            after=mask|(1<<q)
            phi[q]+=(v[after]-v[mask])/6
            mask=after
    np.testing.assert_allclose(phi.sum(0),v[7]-v[0],rtol=1e-10,atol=1e-10)
    return phi

def fixtures():
    v54.tests()
    rng=np.random.default_rng(57)
    bs=rng.normal(size=(18,4));bo=rng.normal(size=(18,4))
    a=rng.normal(size=4);b=rng.normal(size=4);r=rng.normal(size=18)
    for anchor in (r,np.zeros_like(r)):
        for mask in (0,7):
            got=hybrid((bs,a),(bo,b),mask,anchor)
            want=(bs,a) if mask==0 else (bo,b)
            for x,y in zip(got,want):np.testing.assert_allclose(x,y,rtol=1e-12,atol=1e-12)
        for mask in (2,4,6):
            c,d=hybrid((bs,a),(bo,b),mask,anchor)
            np.testing.assert_allclose(anchor@c+d,anchor@bs+a,rtol=1e-12,atol=1e-12)
    v=np.array([[sum((k+1) for k in range(3) if mask&(1<<k)),2*sum((k+1) for k in range(3) if mask&(1<<k))] for mask in SUBSETS],float)
    np.testing.assert_allclose(allocation(v),[[1,2],[2,4],[3,6]],atol=1e-12)
    print('v57 fixed-block endpoints, anchor invariance, Shapley efficiency fixtures PASS',flush=True)

def stat(a):
    a=np.asarray(a,float);assert a.ndim==1 and np.isfinite(a).all()
    n=len(a);ind=np.random.default_rng(20261126).integers(n,size=(10000,n))
    loo=np.array([np.delete(a,i).mean() for i in range(n)])
    return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),
            'bootstrap95':np.quantile(a[ind].mean(1),[.025,.975]).tolist(),
            'delete_one_range':[float(loo.min()),float(loo.max())],'per_trial':a.tolist()}

def run(source,diag,v55zip,v56zip,out):
    fixtures()
    prior55=v56.ref(v55zip);prior56=reference(v56zip)
    qc={};data=v55.admit(source,v55.reference(diag),qc)
    if qc!=prior55['source_QC']:raise ValueError('V55_QC_REPLAY_STOP')
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS}
    assert ids==prior56['trial_order'] and [len(ids[l]) for l in LIGHTS]==[9,10]
    full={}
    for l in LIGHTS:
        for i,(f,p) in data['Triads-'+l].items():
            X,Y,t=v56.native_panels(f,p,i)
            assert len(t)==prior55['windows']['full_archive']['window_group_times'][i]
            for a in MODES:
                d=X[a]['B'].shape[1]
                assert d==(14 if a=='base' else 21)
                assert X[a]['NEAR'].shape[1]==d+4
                np.testing.assert_array_equal(X[a]['B'],X[a]['NEAR'][:,:d])
                np.testing.assert_array_equal(X[a]['GLOBAL'],X[a]['NEAR'][:,:d+2])
            full[i]={a:{k:file_moment(X[a][k],Y) for k in MODELS} for a in MODES}
    ensembles={l:list(itertools.combinations(ids[l],8)) for l in LIGHTS}
    assert [len(ensembles[l]) for l in LIGHTS]==[9,45]
    fits={l:{tr:{a:{k:train_only_standardized_ridge(sum_moments([full[i][a][k] for i in tr])) for k in MODELS} for a in MODES} for tr in ensembles[l]} for l in LIGHTS}
    result={c:{} for c in CONVENTIONS};max_replay=0.;max_hybrid=0.;pair_count=0
    for l in LIGHTS:
        o='Dark' if l=='Bright' else 'Bright'
        for i in ids[l]:
            ss=[tr for tr in ensembles[l] if i not in tr];oo=ensembles[o]
            assert len(ss)==(1 if l=='Bright' else 9) and len(oo)==(45 if l=='Bright' else 9)
            pair_count+=len(ss)*len(oo)
            for a in MODES:
                for k in MODELS:
                    for src,chosen,prior_key in [(l,ss,'full_same'),(o,oo,'full_cross')]:
                        scores=[score_file_moment(full[i][a][k],*fits[src][tr][a][k]) for tr in chosen]
                        for h in H:
                            v=float(np.mean([q[h] for q in scores]));p=prior56['source_safe_MSE'][prior_key][i][a][k][h]
                            max_replay=max(max_replay,abs(v-p))
                            if not np.isclose(v,p,rtol=RTOL,atol=ATOL):raise ValueError('V56_MSE_REPLAY_STOP')
                m=full[i][a]['NEAR'];d=len(m['sx'])
                for c in CONVENTIONS:
                    anchor=np.zeros(d) if c=='raw_origin' else m['sx']/m['n']
                    accum=np.zeros((8,2))
                    for s in ss:
                        for t in oo:
                            fs=fits[l][s][a]['NEAR'];fo=fits[o][t][a]['NEAR']
                            for mask in SUBSETS:
                                q=score_file_moment(m,*hybrid(fs,fo,mask,anchor))
                                accum[mask]+=np.array([q[h] for h in H])
                    accum/=len(ss)*len(oo)
                    for mask,key in [(0,'full_same'),(7,'full_cross')]:
                        expected=np.array([prior56['source_safe_MSE'][key][i][a]['NEAR'][h] for h in H])
                        max_hybrid=max(max_hybrid,float(np.max(np.abs(accum[mask]-expected))))
                        np.testing.assert_allclose(accum[mask],expected,rtol=RTOL,atol=ATOL)
                    phi=allocation(accum)
                    result[c].setdefault(a,{})[i]={'subset_MSE':accum.tolist(),'shapley_native':phi.tolist()}
            print('whole-trial heldout block transplant scored',l,i,flush=True)
    assert pair_count==1215
    summary={}
    for c in CONVENTIONS:
        summary[c]={}
        for a in MODES:
            summary[c][a]={}
            for hi,h in enumerate(H):
                summary[c][a][h]={}
                for l in LIGHTS:
                    V=np.array([result[c][a][i]['subset_MSE'] for i in ids[l]])[:,:,hi]
                    P=np.array([result[c][a][i]['shapley_native'] for i in ids[l]])[:,:,hi]
                    base=V[:,0]
                    assert (base>0).all()
                    costs={'B':P[:,0],'G':P[:,1],'N':P[:,2],'total':V[:,7]-V[:,0],
                           'N_replaced_first':V[:,4]-V[:,0],'N_replaced_last':V[:,7]-V[:,3],
                           'G_replaced_first':V[:,2]-V[:,0],'G_replaced_last':V[:,7]-V[:,5]}
                    summary[c][a][h][l]={'relative_percent':{k:stat(100*v/base) for k,v in costs.items()},'native':{k:stat(v) for k,v in costs.items()}}
    p=summary['raw_origin']['base']['short']['Dark']['relative_percent']['N']
    gate=p['mean']>0 and p['positive']>=8 and p['delete_one_range'][0]>0 and p['bootstrap95'][0]>0
    out.update(status='V57_ORIGINAL_TRIAD_BLOCK_TRANSPLANT_SCORED',scientific_status='LOCAL_NONPORTABILITY_DIRECTION_SUPPORTED_DESCRIPTIVE' if gate else 'LOCAL_NONPORTABILITY_DIRECTION_NOT_SUPPORTED',
               prior_v56_scientific_status=prior56['scientific_status'],prior_v56_zip_sha256=PIN_ZIP,prior_v56_json_sha256=PIN_JSON,
               trial_order=ids,source_QC={'all_58_members_reauthenticated':True,'same_source_QC_as_v55':True},
               training_combinations={l:len(ensembles[l]) for l in LIGHTS},fit_pairs=pair_count,max_original_model_replay_abs=max_replay,max_hybrid_endpoint_replay_abs=max_hybrid,
               subset_bit_order=list(BLOCKS),horizon_order=list(H),source_safe_hybrid_losses=result,summary=summary,raw_positions_or_coefficients_exported=False)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True);p.add_argument('--diagnostic',type=Path,required=True)
    p.add_argument('--v55',type=Path,required=True);p.add_argument('--v56',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a.source,a.diagnostic,a.v55,a.v56,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    if 'summary' in o:
        sm={c:{a:{h:{l:{k:{z:v[z] for z in ('mean','positive','bootstrap95','delete_one_range')} for k,v in x['relative_percent'].items()} for l,x in y.items()} for h,y in w.items()} for a,w in v.items()} for c,v in o['summary'].items()}
    else:sm=None
    print(json.dumps({**{k:v for k,v in o.items() if k not in ('summary','source_safe_hybrid_losses','trial_order')},'summary_compact':sm},sort_keys=True),flush=True)
    if o['status']!='V57_ORIGINAL_TRIAD_BLOCK_TRANSPLANT_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
