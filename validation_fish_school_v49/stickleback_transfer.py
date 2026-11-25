"""v49 original stickleback: exact source pins, whole-shoal transfer, fixed-state scoring."""
import hashlib,json,sys,tempfile,zipfile,subprocess,argparse
from pathlib import Path
import numpy as np
from validation_fish_school_v26.recording_age_forecast import read_source
from validation_fish_school_v32.stickleback_12_shoal import verify_crosswalk_bytes,verified_directory_index,source_fetch_file
from validation_fish_school_v33.neighbor_panels import original_panels,frozen_original_source_clock_and_cohort
from validation_fish_school_v33.aggregate_shoal_shards import restore_file_moments
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
from validation_fish_school_v46.zebrafish_holdout import parity
from validation_fish_school_v48.polarization_transfer import states,stats,STATES,PARTS,MODELS,H

PRIOR_ART=14906668781
PRIOR_ZIP='4aa514578f04b850c977070fb49bc0773aec831fed0b7260efb7dc73bdffed7a'
PRIOR_JSON='a409e041e0f8b3392836ff256c6edf75a1d2c29ded425a52383f1ac2f1801386'
SHOALS=tuple(str(i) for i in range(1,13))
COUNTS=(3147771,570360,4562880,57968)
def reference(path):
    b=Path(path).read_bytes()
    if hashlib.sha256(b).hexdigest()!=PRIOR_ZIP:raise ValueError('PRIOR_ZIP_DRIFT')
    with zipfile.ZipFile(path) as z:
        if len(z.namelist())!=1:raise ValueError('PRIOR_MEMBERS')
        raw=z.read(z.namelist()[0])
    if hashlib.sha256(raw).hexdigest()!=PRIOR_JSON:raise ValueError('PRIOR_JSON_DRIFT')
    j=json.loads(raw)
    assert j['status']=='V33_ORIGINAL_84_RECORDINGS_12_SHOALS_LOCAL_VERSUS_GLOBAL_HOLDOUT'
    assert j['n_original_EIDC_trial_files']==84 and j['n_original_biological_shoal_holdouts']==12
    meta=j['original_file_source_provenance']['per_original_file_source_authentication_without_raw_tracks']
    pins={x['source_original_EIDC_filename']:x for x in meta}
    assert len(meta)==len(pins)==84
    ref={x['original_heldout_shoal_ID']:x for x in j['original_true_shoal_holdout_records']}
    assert set(ref)==set(SHOALS)
    return pins,ref
def test():
    parity()
    rng=np.random.default_rng(49)
    p=rng.normal(size=(4400,8,2));f=np.arange(len(p));t=frozen_original_source_clock_and_cohort(f,p)
    masks=states(p,t,25)
    assert set(masks)==set(STATES)
    for part in PARTS:assert np.all(sum(masks[k].astype(int) for k in part)==1)
    for k,m in masks.items():
        a=p.copy();a[t[-1]+20]+=12
        np.testing.assert_array_equal(m,states(a,t,25)[k])
    print('v49 state partition and future-only isolation PASS',flush=True)
def encode(m):
    return {k:(int(v) if k=='n' else np.asarray(v).tolist()) for k,v in m.items()}
def source(group,prior):
    if group not in SHOALS:raise ValueError('GROUP')
    pins,_=reference(prior)
    author=verify_crosswalk_bytes();index=verified_directory_index()
    assert set(author)==set(index)==set(pins) and len(author)==84
    names=sorted((n for n in author if author[n]==group),key=lambda x:int(x[:-4]))
    rows={}
    for n in names:
        pin=pins[n];assert pin['original_author_Group']==group and pin['source_published_original_EIDC_bytes']==index[n]
        raw,sha,_=source_fetch_file(n,index[n])
        if sha!=pin['original_authenticated_SHA256'] or hashlib.sha256(raw).hexdigest()!=sha:raise ValueError('SOURCE_84_SHA_DRIFT_'+n)
        f,p=read_source(raw);case=original_panels(f,p,n);X,Y=case['X'],case['Y']
        t=frozen_original_source_clock_and_cohort(f,p)
        assert tuple(X)==MODELS and len(Y)==len(t)*8
        current=(case['n_source_rows'],len(t),len(Y),case['n_discarded_original_source_group_times'])
        expected=tuple(pin[k] for k in ['original_source_native_position_rows','n_original_source_valid_group_times','n_original_source_fish_frame_rows','n_original_source_discarded_group_times'])
        if current!=expected:raise ValueError('SOURCE_FILE_COHORT_DRIFT_'+n)
        masks=states(p,t,25);counts={k:int(v.sum()) for k,v in masks.items()}
        if any(counts[k]<200 for k in STATES[:4]):raise ValueError('MARGINAL_SUPPORT_STOP_'+n)
        mom={'ALL':{k:encode(file_moment(X[k],Y)) for k in MODELS}}
        for s,v in masks.items():
            if counts[s]<200:continue
            ix=np.repeat(v,8);mom[s]={k:encode(file_moment(X[k][ix],Y[ix])) for k in MODELS}
        rows[n]={'group':group,'sha256':sha,'source_bytes':len(raw),'cohort':list(current),'counts':counts,'moments':mom}
        print('original source authenticated',group,n,len(t),flush=True)
    return {'status':'V49_SOURCE_MOMENTS_ONLY','group':group,'prior_zip_sha256':PRIOR_ZIP,'files':rows,'raw_XY_or_targets_exported':False}
def aggregate(shards,prior):
    pins,ref=reference(prior);author=verify_crosswalk_bytes()
    files={};qc={}
    paths=sorted(Path(shards).glob('group_*.json'))
    if len(paths)!=12:raise ValueError('TWELVE_SHARDS_REQUIRED')
    groups=set()
    for path in paths:
        j=json.loads(path.read_text());g=j['group']
        assert j['status']=='V49_SOURCE_MOMENTS_ONLY' and j['prior_zip_sha256']==PRIOR_ZIP and g in SHOALS and g not in groups and j['raw_XY_or_targets_exported'] is False
        groups.add(g);assert set(j['files'])=={n for n in author if author[n]==g}
        for n,v in j['files'].items():
            pin=pins[n];assert n not in files and v['group']==g and v['sha256']==pin['original_authenticated_SHA256'] and v['source_bytes']==pin['source_published_original_EIDC_bytes']
            assert v['cohort']==[pin[k] for k in ['original_source_native_position_rows','n_original_source_valid_group_times','n_original_source_fish_frame_rows','n_original_source_discarded_group_times']]
            m={k:restore_file_moments(a) for k,a in v['moments'].items()}
            assert set(m)=={'ALL'}|{k for k,c in v['counts'].items() if c>=200} and all(s in m for s in STATES[:4])
            assert m['ALL']['GLOBAL']['n']==v['cohort'][2]
            for s in m:
                if s!='ALL':assert m[s]['GLOBAL']['n']==8*v['counts'][s]
            for part in PARTS:assert sum(v['counts'][k] for k in part)==v['cohort'][1]
            files[n]=m;qc[n]={k:val for k,val in v.items() if k!='moments'}
    assert set(groups)==set(SHOALS) and set(files)==set(author)==set(pins)
    assert tuple(np.sum([v['cohort'] for v in qc.values()],axis=0))==COUNTS
    allowed=[s for s in STATES if all(s in m for m in files.values())]
    joint=all(s in allowed for s in STATES[4:])
    fs={};ss={};file_scores={};replay=0.;partition=0.
    def avg(v):return {h:float(np.mean([a[h] for a in v])) for h in H}
    for held in SHOALS:
        train=sorted((n for n in author if author[n]!=held),key=lambda x:int(x[:-4]));test=sorted((n for n in author if author[n]==held),key=lambda x:int(x[:-4]))
        assert len({author[n] for n in train})==11 and held not in {author[n] for n in train}
        assert set(test)==set(ref[held]['source_original_test_trial_IDs'])
        fs[held]={};ss[held]={s:{} for s in allowed}
        for model in MODELS:
            B,b=train_only_standardized_ridge(sum_moments([files[n]['ALL'][model] for n in train]))
            for n in test:
                q={s:score_file_moment(m[model],B,b) for s,m in files[n].items()}
                file_scores.setdefault(n,{})[model]=q
                for part in PARTS:
                    if not all(s in q for s in part):continue
                    c=qc[n]['counts'];total=sum(c[s] for s in part)
                    for h in H:
                        z=sum(c[s]*q[s][h] for s in part)/total
                        partition=max(partition,abs(z-q['ALL'][h]))
                        if not np.isclose(z,q['ALL'][h],rtol=1e-7,atol=1e-10):raise ValueError('PARTITION_REPLAY_STOP')
            fs[held][model]=avg([file_scores[n][model]['ALL'] for n in test])
            for h in H:
                old=ref[held]['original_equal_trial_within_shoal_MSE'][model][h];now=fs[held][model][h]
                replay=max(replay,abs(old-now))
                if not np.isclose(now,old,rtol=1e-7,atol=1e-10):raise ValueError('V33B_GROUP_MSE_REPLAY_STOP')
            for s in allowed:ss[held][s][model]=avg([file_scores[n][model][s] for n in test])
    ind=np.random.default_rng(20261125).integers(12,size=(10000,12))
    def far(s,h,scale):
        vals=[]
        for g in SHOALS:
            m=ss[g][s];d=m['NEAR_TRUE'][h]-m['FAR_TRUE'][h]
            den={'state_global':m['GLOBAL'][h],'full_global':fs[g]['GLOBAL'][h],'state_geometry':m['G_geometry'][h],'native':1.}[scale]
            if den<=0:raise ValueError('LOSS_DENOMINATOR')
            vals.append(d if scale=='native' else 100*d/den)
        return np.array(vals)
    out={}
    for scale in ('state_global','full_global','state_geometry','native'):
        o={h:{s:stats(far(s,h,scale),ind) for s in allowed} for h in H}
        def eff(lo,hi,h):return far(hi,h,scale)-far(lo,h,scale)
        def K(lo,hi):return eff(lo,hi,'delayed')-eff(lo,hi,'short')
        o['P_effect']={h:stats(eff('P_low','P_high',h),ind) for h in H}
        o['P_horizon_interaction']=stats(K('P_low','P_high'),ind)
        if joint:
            lo=K('V_low_P_low','V_low_P_high');hi=K('V_high_P_low','V_high_P_high')
            o['P_effect_within_speed']={h:{'low':stats(eff('V_low_P_low','V_low_P_high',h),ind),'high':stats(eff('V_high_P_low','V_high_P_high',h),ind)} for h in H}
            for k,a in [('P_horizon_low_speed',lo),('P_horizon_high_speed',hi),('P_horizon_speed_equal_weight',(lo+hi)/2),('speed_moderation_of_K',hi-lo)]:o[k]=stats(a,ind)
        out[scale]=o
    k=out['state_global']['P_horizon_interaction'];support=k['mean']>0 and k['positive']>=9 and k['delete_one_range'][0]>0
    return {'status':'V49_ORIGINAL_84_TRACKS_12_SHOAL_SCORED','scientific_status':'TRANSFER_DIRECTION_SUPPORTED_DESCRIPTIVE' if support else 'TRANSFER_DIRECTION_NOT_SUPPORTED','source_unit_order':list(SHOALS),'source_file_QC':qc,'n_original_recordings':84,'n_actual_shoals':12,'max_prior_replay_error':replay,'max_partition_error':partition,'joint_speed_strata_admitted':joint,'source_safe_state_MSE':ss,'full_MSE':fs,'results':out,'prior_zip_sha256':PRIOR_ZIP,'raw_positions_or_coefficients_exported':False}
def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['test','source','aggregate']);p.add_argument('--group');p.add_argument('--prior',type=Path);p.add_argument('--shards',type=Path);p.add_argument('--out',type=Path);a=p.parse_args()
    if a.mode=='test':test();return
    try:j=source(a.group,a.prior) if a.mode=='source' else aggregate(a.shards,a.prior)
    except Exception as e:
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'status':'SOURCE_OR_MODEL_STOP','reason':str(e),'group':a.group},indent=2));raise
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(j,sort_keys=True,separators=(',',':'))+'\n')
    if a.mode=='source':print(json.dumps({k:v for k,v in j.items() if k!='files'}),flush=True)
    else:print(json.dumps({k:v for k,v in j.items() if k not in ('source_file_QC','source_safe_state_MSE','full_MSE')},sort_keys=True),flush=True)
if __name__=='__main__':main()
