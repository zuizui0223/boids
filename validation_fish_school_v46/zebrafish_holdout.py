"""Independent v46 archive-defined eight 10-fish zebrafish holdouts.
Frozen v44 primary, schema confirmed by v45. No source XY or model coefficients exported.
"""
import hashlib,json,tempfile,zipfile
from pathlib import Path
import numpy as np
from validation_fish_school_v45.zebrafish_schema import acquire,selected,read_header_and_data,SHA,PINS
from validation_fish_school_v46.grid_preflight import panels,tests
from validation_fish_school_v32.moment_loo import file_moment,sum_moments,train_only_standardized_ridge,score_file_moment
from validation_fish_school_v30.harmonized_forecast import predict_train_file_only
MODELS=('G_geometry','GLOBAL','NEAR_TRUE','FAR_TRUE','NEAR_ROT1','NEAR_STALE_0.2S')
H=('short','delayed')
HEADER=['TimeStep']+[v for i in range(10) for v in (f'fish{i}X',f'fish{i}Y',f'direction{i}')]
def parity():
    tests()
    rng=np.random.default_rng(46)
    x=rng.normal(size=(2500,18)); y=rng.normal(size=(2500,4))+x[:,:4]
    t=rng.normal(size=(1100,18)); z=rng.normal(size=(1100,4))+t[:,:4]
    a,b=train_only_standardized_ridge(file_moment(x,y))
    expected=predict_train_file_only(x,y,t)
    np.testing.assert_allclose(t@a+b,expected,atol=1e-10,rtol=1e-9)
    m=score_file_moment(file_moment(t,z),a,b)
    np.testing.assert_allclose([m['short'],m['delayed']], [np.mean((z[:,:2]-expected[:,:2])**2),np.mean((z[:,2:]-expected[:,2:])**2)],rtol=1e-9,atol=1e-12)
    print('Moment backend exact sklearn parity PASS',flush=True)
def summarize(scores):
    ids=sorted(scores)
    if len(ids)!=8:raise ValueError('EIGHT_HOLDOUTS_REQUIRED')
    a=np.array([[[scores[i][k][h] for k in MODELS] for h in H] for i in ids])
    if not np.isfinite(a).all() or not (a>0).all():raise ValueError('INVALID_LOSS')
    base,g,near,far,rot,stale=a.transpose(2,0,1); dg=base-g; dl=g-near
    rng=np.random.default_rng(20261125); ind=rng.integers(8,size=(10000,8))
    def summary(x,den):
        v=100*x.mean(0)/den.mean(0)
        return {'short_delayed_percent':v.tolist(),'change_pp':float(v[1]-v[0]),'positive_units':(x>0).sum(0).tolist()}
    out={'primary_admitted':bool((dg>0).all()),'source_unit_order':ids,'global_gain':summary(dg,base),'local_gain':summary(dl,g),
         'all_model_equal_shoal_mean_MSE':{k:{h:float(a[:,t,j].mean()) for t,h in enumerate(H)} for j,k in enumerate(MODELS)},
         'matched_controls_relative_to_GLOBAL':{k:summary(x,g) for k,x in {'mapping':rot-near,'proximity':far-near,'freshness':stale-near,'far_additional':g-far,'stale_additional':g-stale}.items()},
         'per_shoal_global_gain':dg.tolist(),'per_shoal_local_gain':dl.tolist()}
    if not out['primary_admitted']:
        out['scientific_status']='GLOBAL_DENOMINATOR_GATE_STOP';return out
    ratio=100*dl.mean(0)/dg.mean(0); delta=float(ratio[1]-ratio[0])
    unit=100*np.diff(dl/dg,axis=1).ravel()
    boot=100*np.diff(dl[ind].mean(1)/dg[ind].mean(1),axis=1).ravel()
    loo=[float(100*np.diff(np.delete(dl,i,0).mean(0)/np.delete(dg,i,0).mean(0))[0]) for i in range(8)]
    nneg=int((unit<0).sum())
    out.update({'R_local_to_global_percent':ratio.tolist(),'R_change_pp':delta,'per_shoal_R_change_pp':unit.tolist(),'R_decreases_n':nneg,
       'R_change_descriptive_paired_bootstrap95_pp':np.quantile(boot,[.025,.975]).tolist(),'R_change_delete_one_range_pp':[min(loo),max(loo)],
       'scientific_status':'FROZEN_PRIMARY_DIRECTION_REPLICATED' if delta<0 and nneg>=6 and max(loo)<0 else 'FROZEN_PRIMARY_DIRECTION_NOT_REPLICATED',
       'relative_to_global_increment_secondary':{k:summary(x,dg) for k,x in {'mapping':rot-near,'proximity':far-near,'freshness':stale-near,'far_additional':g-far}.items()}})
    return out
def run():
    parity()
    moments={}; qc={}
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'data.zip'; acquire(path)
        with zipfile.ZipFile(path) as z:
            for name in selected(z):
                head,fields,a=read_header_and_data(z,name)
                if fields!=HEADER or a.shape!=(54001,31) or not np.isfinite(a).all():raise ValueError('SCHEMA_DRIFT')
                clock=a[:,0]; f=np.arange(len(clock)); err=float(np.max(np.abs((clock-clock[0])-f/15)))
                if not (np.diff(clock)>0).all() or err>.0051:raise ValueError('CLOCK_DRIFT')
                pos=np.stack([a[:,[1+3*i,2+3*i]] for i in range(10)],axis=1)
                if not ((pos>=0)&(pos<=1)).all():raise ValueError('XY_RANGE_DRIFT')
                X,Y,t=panels(f,pos,15)
                if tuple(X)!=MODELS or len(t)!=17985 or len(Y)!=179850:raise ValueError('COMMON_COHORT_DRIFT')
                moments[name]={k:file_moment(X[k],Y) for k in MODELS}
                qc[name]={'member_sha256':PINS[Path(name).name],'native_rows':len(f),'eligible_group_times':len(t),'eligible_fish_times':len(Y),'elapsed_clock_max_error_s':err}
                print('source cohort verified:',name,len(t),flush=True)
                del X,Y,t,a,pos
    if len(moments)!=8:raise ValueError('SOURCE_ROSTER_DRIFT')
    scores={}
    for held in sorted(moments):
        train=[k for k in sorted(moments) if k!=held]
        assert len(train)==7 and held not in train
        scores[held]={}
        for k in MODELS:
            B,b=train_only_standardized_ridge(sum_moments([moments[i][k] for i in train]))
            scores[held][k]=score_file_moment(moments[held][k],B,b)
    o=summarize(scores)
    o.update(status='ORIGINAL_EIGHT_ZEBRAFISH_TRIALS_SCORED',original_archive_sha256=SHA,source_cohorts=qc,source_file_scores=scores,
       n_holdout_trials=8,author_reports_no_fish_reuse_within_size=True,author_figure_roster_unresolved=True,
       confidence_probability_sensitivity='NOT_ADMITTED_NO_CONFIDENCE_COLUMN',raw_XY_or_coefficients_exported=False,causal_interpretation=False,
       native_units='source coordinate units per second squared, no physical calibration inferred',folds_share_training=True)
    return o
if __name__=='__main__':
    p=Path('validation_fish_school_v46/results/zebrafish.json');p.parent.mkdir(parents=True,exist_ok=True)
    try:o=run()
    except Exception as e:
        p.write_text(json.dumps({'status':'SOURCE_OR_MODEL_STOP','reason':str(e)},indent=2)+'\n');raise
    p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    print(json.dumps(o,sort_keys=True))
