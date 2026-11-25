"""v58 balanced training and selective condition-specific slopes, no outcome tuning."""
import argparse,itertools,json,hashlib,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v54 import illumination_triads as v54
from validation_fish_school_v55 import native_illumination as v55
from validation_fish_school_v56 import common_state_transfer as v56
from validation_fish_school_v57 import block_transplant as v57
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
LIGHTS=('Bright','Dark');MODES=('base','geometry');H=('short','delayed')
MASKS=tuple(range(8));RTOL=1e-7;ATOL=1e-10
PIN57='c7169d65d8c22e7014fb8c7549d3dcb380ce56ca16579975c4fa6e51c78bcbc1'
PIN57JSON='10631ccabb195d38259dd32a4d04f406f28cc9cec3c613175f4c189102087dd1'
def prior57(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==PIN57
    with zipfile.ZipFile(path) as z:
        assert len(z.namelist())==1; raw=z.read(z.namelist()[0])
    assert hashlib.sha256(raw).hexdigest()==PIN57JSON
    j=json.loads(raw); assert j['status']=='V57_ORIGINAL_TRIAD_BLOCK_TRANSPLANT_SCORED'
    return j
def transform_matrix(d,c,mask):
    I=np.eye(d+1);parts=(list(range(d-4)),list(range(d-4,d-2)),list(range(d-2,d)))
    cols=[I[:,:d]]
    for q,ix in enumerate(parts):
        if mask&(1<<q):
            cols.append(c*I[:,ix])
            if q==0:cols.append(c*I[:,d:d+1])
    return np.concatenate(cols,axis=1)
def transform(m,T):
    n=m['n'];sx=np.r_[m['sx'],n];xx=np.block([[m['sxx'],m['sx'][:,None]],[m['sx'][None,:],np.array([[n]])]])
    xy=np.vstack((m['sxy'],m['sy']))
    return {'n':n,'sx':T.T@sx,'sxx':T.T@xx@T,'sxy':T.T@xy,'sy':m['sy'].copy(),'syy':m['syy'].copy()}
def fixtures():
    v54.tests()
    rng=np.random.default_rng(58)
    for d in (18,25):
        x=rng.normal(size=(2400,d));z=rng.normal(size=(1200,d))
        y=rng.normal(size=(2400,4))+x[:,:4];u=rng.normal(size=(1200,4))
        for mask in MASKS:
            T=transform_matrix(d,1,mask);U=transform_matrix(d,-1,mask)
            xx=np.c_[x,np.ones(len(x))]@T;zz=np.c_[z,np.ones(len(z))]@U
            a=transform(file_moment(x,y),T);b=transform(file_moment(z,u),U)
            for m,q in ((a,file_moment(xx,y)),(b,file_moment(zz,u))):
                for k in m:np.testing.assert_allclose(m[k],q[k],rtol=1e-10,atol=1e-9)
            beta,bias=train_only_standardized_ridge(sum_moments([a,b]))
            from sklearn.preprocessing import StandardScaler
            from sklearn.linear_model import Ridge
            train=np.r_[xx,zz];target=np.r_[y,u];s=StandardScaler().fit(train);r=Ridge(alpha=10).fit(s.transform(train),target)
            np.testing.assert_allclose(train@beta+bias,r.predict(s.transform(train)),rtol=1e-8,atol=1e-9)
            assert transform_matrix(d,1,mask).shape[1]==d+sum((d-3,2,2)[q] for q in range(3) if mask&(1<<q))
    print('v58 all 16 design/moment and sklearn prediction fixtures PASS',flush=True)
def stat(a):
    a=np.asarray(a,float);n=len(a);ind=np.random.default_rng(20261126).integers(n,size=(10000,n))
    loo=np.array([np.delete(a,i).mean() for i in range(n)])
    return {'mean':float(a.mean()),'positive':int((a>0).sum()),'negative':int((a<0).sum()),'bootstrap95':np.quantile(a[ind].mean(1),[.025,.975]).tolist(),'delete_one_range':[float(loo.min()),float(loo.max())],'per_trial':a.tolist()}
def gate(q,n):
    return bool(q['mean']>0 and q['positive']>=int(np.ceil(.8*n)) and q['delete_one_range'][0]>0 and q['bootstrap95'][0]>0)
def run(source,diag,p55,p56,p57,out):
    fixtures();j55=v56.ref(p55);j56=v57.reference(p56);j57=prior57(p57)
    qc={};data=v55.admit(source,v55.reference(diag),qc);assert qc==j55['source_QC']
    ids={l:sorted(data['Triads-'+l]) for l in LIGHTS}
    assert ids==j56['trial_order']==j57['trial_order'] and [len(ids[l]) for l in LIGHTS]==[9,10]
    orig={}
    for l in LIGHTS:
        for i,(f,p) in data['Triads-'+l].items():
            X,Y,t=v56.native_panels(f,p,i)
            assert len(t)==j55['windows']['full_archive']['window_group_times'][i]
            orig[i]={a:file_moment(X[a]['NEAR'],Y) for a in MODES}
    combos={l:list(itertools.combinations(ids[l],8)) for l in LIGHTS}
    assert [len(combos[l]) for l in LIGHTS]==[9,45]
    # Replay old fits first, prior gates cannot be bypassed.
    oldfit={l:{tr:{a:train_only_standardized_ridge(sum_moments([orig[i][a] for i in tr])) for a in MODES} for tr in combos[l]} for l in LIGHTS}
    replay=0.;prior_endpoint=0.
    for l in LIGHTS:
        other='Dark' if l=='Bright' else 'Bright'
        for i in ids[l]:
            for a in MODES:
                for src,train,pk,mask in [(l,[tr for tr in combos[l] if i not in tr],'full_same',0),(other,combos[other],'full_cross',7)]:
                    scores=[score_file_moment(orig[i][a],*oldfit[src][tr][a]) for tr in train]
                    for hi,h in enumerate(H):
                        got=float(np.mean([s[h] for s in scores]));want=j56['source_safe_MSE'][pk][i][a]['NEAR'][h]
                        replay=max(replay,abs(got-want));np.testing.assert_allclose(got,want,rtol=RTOL,atol=ATOL)
                        for c in ('raw_origin','test_covariate_mean'):
                            val=j57['source_safe_hybrid_losses'][c][a][i]['subset_MSE'][mask][hi]
                            prior_endpoint=max(prior_endpoint,abs(val-want));np.testing.assert_allclose(val,want,rtol=RTOL,atol=ATOL)
    print('v58 original source and separate-fit score replay PASS',replay,flush=True)
    losses={a:{} for a in MODES};fits_count=0;test_count=0
    for a in MODES:
        d=len(orig[ids['Bright'][0]][a]['sx']);assert d==(18 if a=='base' else 25)
        for i in ids['Bright']+ids['Dark']:losses[a][i]=np.zeros((8,2))
        cnt={i:0 for i in losses[a]}
        for mask in MASKS:
            m={i:transform(orig[i][a],transform_matrix(d,1 if l=='Bright' else -1,mask)) for l in LIGHTS for i in ids[l]}
            # Reuse the same all-eligible 8+8 train sets, with no model-specific subset selection.
            for tb in combos['Bright']:
                for td in combos['Dark']:
                    train=tb+td;assert len(train)==16 and len(set(train))==16
                    held=[i for i in ids['Bright']+ids['Dark'] if i not in train];assert len(held)==3
                    beta,bias=train_only_standardized_ridge(sum_moments([m[i] for i in train]))
                    fits_count+=1
                    for i in held:
                        assert i not in train
                        q=score_file_moment(m[i],beta,bias);losses[a][i][mask]+=np.array([q[h] for h in H])
                        test_count+=1
                        if mask==0:cnt[i]+=1
            print('balanced pooled model complete',a,mask,flush=True)
        for l in LIGHTS:
            for i in ids[l]:
                assert cnt[i]==(45 if l=='Bright' else 81)
                losses[a][i]=(losses[a][i]/cnt[i]).tolist()
    assert fits_count==405*8*2 and test_count==1215*8*2
    summary={}
    for a in MODES:
        summary[a]={}
        for hi,h in enumerate(H):
            summary[a][h]={}
            for l in LIGHTS:
                V=np.array([losses[a][i] for i in ids[l]])[:,:,hi]
                base=V[:,0];assert (V>0).all() and np.isfinite(V).all()
                comparisons={'all_specific_vs_shared':(0,7),'collective_specific_vs_shared':(0,6),
                  'self_specific_vs_shared':(0,1),'self_additional_after_collective':(6,7),
                  'collective_additional_after_self':(1,7),'near_additional_after_self_global':(3,7),
                  'global_additional_after_self_near':(5,7),'global_only_vs_shared':(0,2),'near_only_vs_shared':(0,4)}
                s={k:stat(100*(V[:,lo]-V[:,up])/base) for k,(lo,up) in comparisons.items()}
                for k,v in s.items():v['direction_gate_pass']=gate(v,len(V))
                # Positive signed allocation means lower held-out MSE from enabling treatment dependence.
                phi=np.stack([v57.allocation(-np.column_stack((v,v)))[:,0] for v in V])
                np.testing.assert_allclose(phi.sum(1),V[:,0]-V[:,7],atol=1e-10,rtol=1e-10)
                inter={'BG':V[:,1]+V[:,2]-V[:,3]-V[:,0],
                       'BN':V[:,1]+V[:,4]-V[:,5]-V[:,0],
                       'GN':V[:,2]+V[:,4]-V[:,6]-V[:,0],
                       'BGN':V[:,0]-V[:,1]-V[:,2]-V[:,4]+V[:,3]+V[:,5]+V[:,6]-V[:,7]}
                sep=np.array([j56['source_safe_MSE']['full_same'][i][a]['NEAR'][h] for i in ids[l]])
                summary[a][h][l]={'comparisons_pp_of_shared':s,
                  'all_subset_gain_pp_of_shared':{str(m):stat(100*(base-V[:,m])/base) for m in MASKS},
                  'shapley_gain_pp_of_shared':{k:stat(100*phi[:,q]/base) for q,k in enumerate(('B','G','N'))},
                  'factorial_interaction_pp_of_shared':{k:stat(100*v/base) for k,v in inter.items()},
                  'fully_specific_pooled_minus_separate_pct_of_separate':stat(100*(V[:,7]-sep)/sep)}
    primary=summary['base']['short']['Dark']['comparisons_pp_of_shared']['near_additional_after_self_global']
    out.update(status='V58_BALANCED_POOLED_RULES_SCORED',scientific_status='CONDITIONAL_NEAR_SPECIFICITY_SUPPORTED_DESCRIPTIVE' if primary['direction_gate_pass'] else 'CONDITIONAL_NEAR_SPECIFICITY_NOT_SUPPORTED',
      prior_v56_scientific_status=j56['scientific_status'],prior_v57_scientific_status=j57['scientific_status'],
      source_58_reauthenticated=True,trial_order=ids,subset_bit_order=['B','G','N'],horizon_order=list(H),
      train_sets_per_encoding=405,heldout_fit_pairs_per_encoding=1215,new_fits_count=fits_count,heldout_fit_evaluations=test_count,
      max_v56_NEAR_replay_abs=replay,max_v57_prior_endpoint_abs=prior_endpoint,
      source_safe_pooled_subset_MSE=losses,summary=summary,raw_positions_or_coefficients_exported=False)
def main():
    p=argparse.ArgumentParser()
    for a in ('source','diagnostic','v55','v56','v57','out'):p.add_argument('--'+a,type=Path,required=True)
    a=p.parse_args();o={'status':'SOURCE_OR_MODEL_STOP'}
    try:run(a.source,a.diagnostic,a.v55,a.v56,a.v57,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:800],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    small={k:v for k,v in o.items() if k not in ('source_safe_pooled_subset_MSE','summary','trial_order')}
    if 'summary'in o:
        small['summary']={a:{h:{l:{k:{q:v[q] for q in ('mean','positive','bootstrap95','direction_gate_pass')} for k,v in r['comparisons_pp_of_shared'].items()} for l,r in z.items()} for h,z in y.items()} for a,y in o['summary'].items()}
    print(json.dumps(small,sort_keys=True),flush=True)
    if o['status']!='V58_BALANCED_POOLED_RULES_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
