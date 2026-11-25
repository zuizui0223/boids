"""v55 source-semantic correction; preserve v54 base endpoint and all source STOPs.
All source trials pinned to outcome-blind v54 diagnostic. No raw XY exported.
"""
import argparse,copy,hashlib,io,json,subprocess,tempfile,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from validation_fish_school_v54 import illumination_triads as v54

ART=15007229391
ZIP_SHA='06f189c79c55f20f418306031e974df796294082f6460dda43f4cbea5e4aed79'
JSON_SHA='33f7c7230f74eeaa95ce2d1e5707db7b5c09bbac490496c3f1c32a1c7a6ed5f6'
def sha(b):return hashlib.sha256(b).hexdigest()
def reference(path):
    b=Path(path).read_bytes()
    if sha(b)!=ZIP_SHA:raise ValueError('DIAGNOSTIC_ZIP_DRIFT')
    with zipfile.ZipFile(path) as z:
        if z.namelist()!=['schema_diagnostic.json']:raise ValueError('DIAGNOSTIC_MEMBER_DRIFT')
        raw=z.read('schema_diagnostic.json')
    if sha(raw)!=JSON_SHA:raise ValueError('DIAGNOSTIC_JSON_DRIFT')
    ref=json.loads(raw)
    assert ref['status']=='SOURCE_SCHEMA_ONLY' and ref['author_commit']==v54.COMMIT and ref['prediction_scores_exported'] is False
    assert ref['counts']==v54.EXPECTED and len(ref['trials'])==58
    for v in ref['trials'].values():
        assert v['status']=='STRUCTURE_READ' and all(v[k] for k in ('all_clock_finite','integer_frame','strict_frame','strict_time'))
        assert v['rows']>=18000 and v['frame_span']==v['rows'] and v['clock_30hz_max_error_seconds']<=.0051
    return ref
def admit(repo,ref,qc):
    bysha={v['sha256']:v for v in ref['trials'].values()}
    assert len(bysha)==58
    def read_csv(raw,n):
        expected=bysha.get(sha(raw))
        if expected is None:raise ValueError('UNPINNED_SOURCE_MEMBER')
        header=raw.splitlines()[0].decode('utf-8-sig')
        required=['Frame','Time']+[s for i in range(n) for s in (f'X_Arena0_Ind{i}',f'Y_Arena0_Ind{i}')]
        if header!=expected['header'] or header.split(';')!=required:raise ValueError('EXPLICIT_HEADER_DRIFT')
        d=pd.read_csv(io.StringIO(raw.decode('utf-8-sig')),sep=';',keep_default_na=False,na_values=['','NA','NaN','nan','N/A'])
        if list(d.columns)!=required:raise ValueError('PARSED_HEADER_DRIFT')
        a=d.apply(pd.to_numeric,errors='raise').to_numpy(float);f=a[:,0];clock=a[:,1]
        if len(a)!=expected['rows'] or not (np.isfinite(f).all() and np.isfinite(clock).all() and (f==np.round(f)).all() and (np.diff(f)==1).all() and (np.diff(clock)>0).all()):raise ValueError('NATIVE_ROWS_OR_CLOCK_DRIFT')
        err=float(np.max(np.abs(clock-clock[0]-(f-f[0])/30)))
        if err>.0051 or not np.isclose(err,expected['clock_30hz_max_error_seconds'],atol=1e-12,rtol=0):raise ValueError('CLOCK_30HZ_DRIFT')
        p=a[:,2:].reshape(len(a),n,2)
        if np.isinf(p).any():raise ValueError('INF_COORDINATE')
        frac=float(np.isfinite(p).all(-1).mean())
        if frac!=expected['finite_xy_fraction']:raise ValueError('FINITE_COHORT_DRIFT')
        t=v54.grid(f,p)
        return f.astype(np.int64),p,{'rows':len(f),'frame_span':int(f[-1]-f[0]+1),'clock_max_error_s':err,'finite_position_fraction':frac,'eligible_group_times':len(t),'missing_source_frames':0,'coordinate_units':'unconverted source-native, physical calibration not admitted'}
    old=v54.read_csv;v54.read_csv=read_csv
    try:data=v54.admit(repo,qc)
    finally:v54.read_csv=old
    assert set(qc['trials'])==set(ref['trials'])
    for key,v in qc['trials'].items():
        old=ref['trials'][key]
        assert v['csv_sha256']==old['sha256'] and v['csv_bytes']==old['bytes'] and v['condition']==old['condition'] and v['header']==old['header'] and v['rows']==old['rows']
    for fn,v in qc['archive'].items():
        for k in ('bytes','sha256','git_blob'):assert v[k]==ref['archives'][fn][k]
    return data

def windows(data,qc,window):
    if window=='full_archive':return data,copy.deepcopy(qc)
    out={c:{} for c in data};q=copy.deepcopy(qc)
    for c,trials in data.items():
        for key,(f,p) in trials.items():
            sl=slice(0,18000) if window=='first_18000' else slice(-18000,None)
            a,b=f[sl],p[sl];assert len(a)==18000 and (np.diff(a)==1).all()
            t=v54.grid(a,b);out[c][key]=(a,b)
            q['trials'][key].update(rows=len(a),frame_span=len(a),eligible_group_times=len(t),finite_position_fraction=float(np.isfinite(b).all(-1).mean()))
    return out,q

def run(source,diag,out):
    v54.tests();ref=reference(diag)
    qc={};data=admit(source,ref,qc)
    out['source_status']='ALL_58_ORIGINAL_TRIALS_ADMITTED_NATIVE_COORDINATES'
    out['source_QC']=qc
    old=v54.panels
    def native_panels(f,p,key):
        X,Y,t=old(f,p,key)
        # Original base and its fixed label-swap seed unchanged. Remove three
        # uncalibrated radius/radial/tangential features from secondary panel.
        for k,x in X['geometry'].items():
            assert x.shape[1] in (24,26,28)
            X['geometry'][k]=np.concatenate((x[:,:21],x[:,24:]),axis=1)
        return X,Y,t
    # Independent check of base replay and secondary column selection.
    rng=np.random.default_rng(55);f=np.arange(18000);p=rng.normal(size=(len(f),3,2))
    a,y,t=old(f,p,'fixture-v55');b,z,u=native_panels(f,p,'fixture-v55')
    np.testing.assert_array_equal(y,z);np.testing.assert_array_equal(t,u)
    for k in v54.MODELS:
        np.testing.assert_array_equal(a['base'][k],b['base'][k])
        assert b['geometry'][k].shape[1]==a['geometry'][k].shape[1]-3
    print('v55 native-coordinate base unchanged and fixed polynomial-only sensitivity PASS',flush=True)
    v54.panels=native_panels
    try:
        out['windows']={}
        for label in ('full_archive','first_18000','last_18000'):
            d,q=windows(data,qc,label)
            real,pseudo,pq=v54.score_data(d,q)
            summaries,decision=v54.summarize(real)
            # Keep internal key for compatibility but distinguish physical radial STOP.
            out['windows'][label]={'scientific_status':decision,'real_heldout_MSE':real,'pseudo_control_MSE':pseudo,'pseudo_QC':pq,'results':summaries,'window_group_times':{k:v['eligible_group_times'] for k,v in q['trials'].items()}}
            small={a:{h:{k:v for k,v in m.items() if k in ('assignment','local','global')} for h,m in hmap.items()} for a,hmap in summaries.items()}
            print(json.dumps({'window':label,'decision':decision,'results':small},sort_keys=True),flush=True)
    finally:v54.panels=old
    out.update(status='V55_ARCHIVE_NATIVE_ILLUMINATION_SCORED',primary_window='full_archive',scientific_status=out['windows']['full_archive']['scientific_status'],original_v54_stop_preserved=True,physical_radial_geometry='NOT_ADMITTED_UNVERIFIED_CALIBRATION',geometry_key_semantics='fixed native-coordinate polynomial only (no radial/tangential/physical-center terms)',diagnostic_artifact_id=ART,diagnostic_zip_sha256=ZIP_SHA,diagnostic_json_sha256=JSON_SHA,source_independence='Author reports no fish reuse; same study and shared training folds, not independent populations.')

def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--diagnostic',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args()
    o={'status':'SOURCE_OR_MODEL_STOP','raw_positions_or_coefficients_exported':False}
    try:run(a.source,a.diagnostic,o)
    except Exception as e:o.update(status='SOURCE_OR_MODEL_STOP',reason=str(e)[:600],error_type=type(e).__name__)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in o.items() if k not in ('source_QC','windows')},sort_keys=True),flush=True)
    if o['status']!='V55_ARCHIVE_NATIVE_ILLUMINATION_SCORED':raise SystemExit(1)
if __name__=='__main__':main()
