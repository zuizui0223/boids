#!/usr/bin/env python3
"""2026-11-16 pre-outcome frozen 2017 original Wolverine matched-step source-state fidelity.

This is a source-defined *destination-choice* test, not causal state stabilization.
All original data stay ephemeral on the CI runner. Standard library XLSX XML streaming,
NumPy+SciPy conditional softmax, equal-original-animal holdout.
"""
from __future__ import annotations
import collections, hashlib, io, json, math, os, sys, tempfile, urllib.request, zipfile
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

RECORD_ID=5011732
NAME='GPS_traffic_data_wolverine_revised.xlsx'
PROVIDER_MD5='6d694faeadde68fbce1c0b45632aa21c'
SOURCE_SHA256='979a362af1acaff069a7c53dfabf5284eb68d0c448899858ae18be999513b1bd'
SOURCE_BYTES=74178559
H=['cluster','used','SL_m','id','sex','time_start','hour_start','month_start','day_start','year_start','twilight','road_end','road_start','stream_end','stream_start','traffic_end','traffic_start']
SHEETS=('xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml')
MIN_CAND=5
MIN_ANIMALS=10
MIN_STEPS=50
L2=0.02
BOOT=10000
SEED=20261116
MAX_ROWS=2_200_000
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
FEATURES={
 'destination':['log_sl','sl_km','logroad_end','logtraffic_end','logstream_end','roadtraffic',
                'road_hour_cos','road_hour_sin','traffic_hour_cos','traffic_hour_sin',
                'road_sheet2','traffic_sheet2'],
 'road_origin':['log_sl','sl_km','logroad_end','logtraffic_end','logstream_end','roadtraffic',
                'road_hour_cos','road_hour_sin','traffic_hour_cos','traffic_hour_sin',
                'road_sheet2','traffic_sheet2','road_start_end_divergence'],
 'risk_origin':['log_sl','sl_km','logroad_end','logtraffic_end','logstream_end','roadtraffic',
                'road_hour_cos','road_hour_sin','traffic_hour_cos','traffic_hour_sin',
                'road_sheet2','traffic_sheet2','road_start_end_divergence','traffic_start_end_divergence']}

def source():
    from source_v10b import download
    with urllib.request.urlopen(urllib.request.Request('https://zenodo.org/api/records/5011732',headers={'User-Agent':'ecostate-v10c-original/1'}),timeout=40) as res:
        m=json.loads(res.read())
    f=[x for x in m.get('files',[]) if x.get('key')==NAME]
    if len(f)!=1 or f[0].get('checksum')!='md5:'+PROVIDER_MD5 or f[0].get('size')!=SOURCE_BYTES:
        raise ValueError('SOURCE_STOP_PROVIDER_FILE_CHANGED')
    url=f[0]['links'].get('content') or f[0]['links'].get('self')
    if not url:raise ValueError('SOURCE_STOP_NO_PROVIDER_LINK')
    tmp=tempfile.TemporaryDirectory()
    path=Path(tmp.name)/'original.xlsx'
    n,md,sha=download(url,path)
    if n!=SOURCE_BYTES or md!=PROVIDER_MD5 or sha!=SOURCE_SHA256:
        tmp.cleanup();raise ValueError('SOURCE_STOP_ORIGINAL_CHECKSUM_MISMATCH')
    return tmp,path

def parse_shared(z):
    import xml.etree.ElementTree as ET
    values=[]
    if 'xl/sharedStrings.xml' not in z.namelist():return values
    with z.open('xl/sharedStrings.xml') as inp:
        # Keep only a single shared-string item in memory at a time.
        for _,e in ET.iterparse(inp,events=('end',)):
            if e.tag==NS+'si':
                values.append(''.join(e.itertext()))
                e.clear()
    return values

def decode_cell(c,shared):
    ty=c.attrib.get('t')
    v=c.find(NS+'v')
    inline=c.find(NS+'is')
    raw=v.text if v is not None else ''.join(inline.itertext()) if inline is not None else ''
    if ty=='s' and raw is not None:
        idx=int(raw)
        if idx<0 or idx>=len(shared):raise ValueError('SOURCE_SCHEMA_STOP_SHARED_STRING_INDEX')
        return shared[idx]
    return raw

def rows_from_sheet(z,sheet,shared):
    import xml.etree.ElementTree as ET
    with z.open(sheet) as fh:
        context=ET.iterparse(fh,events=('start','end'))
        _,root=next(context)
        for ev,e in context:
            if ev=='end' and e.tag==NS+'row':
                cells={}
                for c in e.findall(NS+'c'):
                    ref=c.attrib.get('r','')
                    col=''.join(x for x in ref if x.isalpha())
                    idx=0
                    for a in col:idx=26*idx+ord(a.upper())-64
                    if idx>0:cells[idx-1]=decode_cell(c,shared)
                out=[cells.get(j,'') for j in range(len(H))]
                e.clear()
                root.clear()
                yield out

def safe_float(x):
    try:
        a=float(x)
        return a if math.isfinite(a) else math.nan
    except (ValueError,TypeError):return math.nan

def id_string(v):
    v=str(v).strip()
    if not v or v.lower() in ('none','nan'):return ''
    # Original Excel may store arbitrary integer IDs as numeric or text.
    try:
        a=float(v)
        if a.is_integer() and 0<=a<=1e14:return str(int(a))
    except ValueError:pass
    return v

def case_flag(v):
    a=str(v).lower().strip()
    if a in ('true','1','1.0','t','yes'):return 1
    if a in ('false','0','0.0','f','no'):return 0
    return -1

def build(path):
    """Streams original 2-sheet XLSX, no guessing source step origins or row-order joins."""
    d={k:[] for k in ('animal','cluster','sheet','used','hour','sl','road_end','road_start','traffic_end','traffic_start','stream_end','stream_start')}
    with zipfile.ZipFile(path) as z:
        if not set(SHEETS).issubset(z.namelist()):raise ValueError('SOURCE_SCHEMA_STOP_SHEET_CHANGE')
        shared=parse_shared(z)
        for sheetindex,sheet in enumerate(SHEETS):
            readcount=0
            for row in rows_from_sheet(z,sheet,shared):
                if readcount==0:
                    if row!=H:raise ValueError('SOURCE_SCHEMA_STOP_UNEXPECTED_HEADERS '+str(row))
                else:
                    r=dict(zip(H,row))
                    d['animal'].append(id_string(r['id']))
                    d['cluster'].append(id_string(r['cluster']))
                    d['sheet'].append(sheetindex)
                    d['used'].append(case_flag(r['used']))
                    for key,nm in [('hour','hour_start'),('sl','SL_m'),('road_end','road_end'),('road_start','road_start'),('traffic_end','traffic_end'),('traffic_start','traffic_start'),('stream_end','stream_end'),('stream_start','stream_start')]:
                        d[key].append(safe_float(r[nm]))
                    if len(d['animal'])>MAX_ROWS:raise ValueError('SOURCE_SCHEMA_STOP_TOO_MANY_ROWS')
                readcount+=1
            d.setdefault('sheet_lengths',[]).append(readcount-1)
    arr={k:np.array(v,dtype=object if k in ('animal','cluster') else int if k in ('sheet','used') else float) for k,v in d.items() if k!='sheet_lengths'}
    qc={'source_rows':len(d['animal']),'sheet_rows':d['sheet_lengths']}
    return arr,qc

def group_admit(d,qc):
    n=len(d['animal'])
    groups=collections.defaultdict(list)
    for i in range(n):
        if d['animal'][i] and d['cluster'][i]:
            groups[(int(d['sheet'][i]),str(d['animal'][i]),str(d['cluster'][i]))].append(i)
    total=len(groups)
    numeric=['hour','sl','road_end','road_start','traffic_end','traffic_start','stream_end','stream_start']
    validrow=np.isfinite(np.column_stack([d[x] for x in numeric])).all(axis=1)
    for x in ['sl','road_end','road_start','traffic_end','traffic_start','stream_end','stream_start']:
        validrow &= d[x]>=0
    validrow &= d['hour']>=0
    validrow &= d['hour']<24
    allowed=[];rejected=collections.Counter()
    for k,idx in groups.items():
        if len(idx)<MIN_CAND:rejected['candidate_count']+=1;continue
        if d['used'][idx].sum()!=1 or not np.isin(d['used'][idx],[0,1]).all():rejected['observed_flag']+=1;continue
        if not validrow[idx].all():rejected['numeric_missing_or_range']+=1;continue
        if any(np.ptp(d[col][idx])>1e-6 for col in ('hour','road_start','stream_start','traffic_start')):
            rejected['inconsistent_start']+=1;continue
        allowed.append((k,idx))
    ctr=collections.Counter(k[1] for k,idx in allowed)
    admitted_ids={i for i,c in ctr.items() if c>=MIN_STEPS}
    selected=[(k,idx) for k,idx in allowed if k[1] in admitted_ids]
    selected.sort(key=lambda x:x[0])
    qc.update({'original_distinct_animal_tokens':len(set(d['animal'])-set([''])),
                'original_matched_groups':total,'group_exclusion_reasons':dict(rejected),
                'source_valid_groups':len(allowed),'eligible_independent_animals':len(admitted_ids),
                'eligible_strata':len(selected),'eligible_rows':sum(len(idx) for _,idx in selected),
                'original_rows_excluded':n-sum(len(idx) for _,idx in selected)})
    if len(admitted_ids)<MIN_ANIMALS or len(selected)<600:
        raise ValueError('SOURCE_SCHEMA_STOP_INDEPENDENT_ANIMALS_OR_GROUPS '+json.dumps(qc))
    return selected,qc

def design(d):
    eps=2*np.pi*d['hour']/24
    rl=np.log1p(d['road_end']);tl=np.log1p(d['traffic_end']);sl=np.log1p(d['stream_end'])
    vals={'log_sl':np.log1p(d['sl']), 'sl_km':d['sl']/1000,
       'logroad_end':rl,'logtraffic_end':tl,'logstream_end':sl,'roadtraffic':rl*tl,
       'road_hour_cos':rl*np.cos(eps),'road_hour_sin':rl*np.sin(eps),
       'traffic_hour_cos':tl*np.cos(eps),'traffic_hour_sin':tl*np.sin(eps),
       'road_sheet2':rl*d['sheet'],'traffic_sheet2':tl*d['sheet'],
       'road_start_end_divergence':np.abs(rl-np.log1p(d['road_start'])),
       'traffic_start_end_divergence':np.abs(tl-np.log1p(d['traffic_start']))}
    return np.column_stack([vals[k] for k in FEATURES['risk_origin']]).astype(float),FEATURES['risk_origin']

def condloss(beta,x,sizes,starts,used,w,deriv=False):
    eta=x@beta
    m=np.maximum.reduceat(eta,starts)
    p=np.exp(eta-np.repeat(m,sizes))
    t=np.add.reduceat(p,starts)
    nll=m+np.log(t)-eta[used]
    result=float(w@nll+L2*np.dot(beta,beta)/2)
    if not deriv:return result
    roww=(np.repeat(w/t,sizes)*p)
    grad=x.T@roww-x[used].T@w+L2*beta
    return result,grad

def fit_eval(d,groups,boot=BOOT):
    X,names=design(d)
    sizes=np.array([len(idx) for _,idx in groups],dtype=int)
    start=np.r_[0,np.cumsum(sizes)[:-1]]
    cols=np.concatenate([np.array(idx,dtype=int) for _,idx in groups])
    X=X[cols]
    # one chosen per admitted group, row/stratum alignment constructed from provider IDs.
    used=np.array([start[i]+np.flatnonzero(d['used'][idx]==1)[0] for i,(_,idx) in enumerate(groups)],dtype=int)
    animals=np.array([k[1] for k,idx in groups],dtype=object)
    ids=sorted(set(animals),key=lambda t:hashlib.sha256(t.encode()).hexdigest())
    fold={a:j%5 for j,a in enumerate(ids)}
    if min(sum(fold[a]==i for a in ids) for i in range(5))<1:
        raise ValueError('SOURCE_SCHEMA_STOP_FOLDS_EMPTY')
    scores={a:{name:[] for name in FEATURES} for a in ids}
    coeffs={name:[] for name in FEATURES if name!='destination'}
    all_idx={k:np.array([names.index(v) for v in cols],dtype=int) for k,cols in FEATURES.items()}
    for k in range(5):
        gtrain=np.flatnonzero(np.array([fold[a]!=k for a in animals]))
        gtest=np.flatnonzero(np.array([fold[a]==k for a in animals]))
        def slice_group(gg):
            ii=np.concatenate([np.arange(start[i],start[i]+sizes[i]) for i in gg])
            cnt=sizes[gg]
            st=np.r_[0,np.cumsum(cnt)[:-1]]
            u=used[gg]-start[gg]+st
            return ii,cnt,st,u
        trow,tn,ts,tu=slice_group(gtrain)
        erow,en,es,eu=slice_group(gtest)
        at=animals[gtrain];ae=animals[gtest]
        n_per=collections.Counter(at)
        w=np.array([1/(len(n_per)*n_per[a]) for a in at],dtype=float)
        mu=X[trow].mean(axis=0);sig=X[trow].std(axis=0);sig[sig<1e-8]=1
        xx=np.clip((X-mu)/sig,-10,10)
        for name,inds in all_idx.items():
            tx=xx[trow][:,inds];ex=xx[erow][:,inds]
            func=lambda theta: condloss(theta,tx,tn,ts,tu,w,deriv=True)
            opt=minimize(func,np.zeros(len(inds)),method='L-BFGS-B',jac=True,
                options={'maxiter':180,'ftol':1e-9,'gtol':1e-7})
            if not opt.success and np.linalg.norm(opt.jac)>0.0005:
                raise ValueError('MODEL_FIT_STOP_NONCONVERGENCE '+name+' '+str(k))
            scores_arr=ex@opt.x
            mm=np.maximum.reduceat(scores_arr,es)
            ll=mm+np.log(np.add.reduceat(np.exp(scores_arr-np.repeat(mm,en)),es))-scores_arr[eu]
            for a in set(ae):scores[a][name].extend(ll[ae==a].tolist())
            if name!='destination':
                last=opt.x[-2:] if name=='risk_origin' else opt.x[-1:]
                coeffs[name].append([float(x) for x in last])
    perid={a:{name:float(np.mean(scores[a][name])) for name in FEATURES} for a in ids}
    for a in ids:perid[a]['n_groups']=len(scores[a]['destination'])
    if any(perid[a]['n_groups']<MIN_STEPS for a in ids):raise ValueError('MODEL_STOP_SCORE_MISSING')
    rng=np.random.default_rng(SEED)
    def contrast(name,a,b,gate_direction=False):
        val=np.array([perid[x][a]-perid[x][b] for x in ids])
        bt=rng.choice(val,size=(boot,len(ids)),replace=True).mean(axis=1)
        ci=np.quantile(bt,[.025,.975]);pos=int((val>0).sum())
        # complete 10,000 resamples and >=65% of original animal IDs positive.
        sign=not gate_direction or sum(x[0]<0 for x in coeffs[b])>=4
        ok=ci[0]>0 and pos>=math.ceil(len(ids)*.65) and sign
        return {'mean_nats_per_movement':float(val.mean()),'ci95_animal_bootstrap':ci.tolist(),
           'n_individuals':len(ids),'positive_individuals':pos,'negative_individuals':int((val<0).sum()),
           'median_individual_gain':float(np.median(val)),
           'source_state_coeff_negative_folds':sum(x[0]<0 for x in coeffs[b]) if b in coeffs else None,
           'fixed_biological_direction_gate':'PASS' if ok else 'FAIL'}
    result={'n_animals':len(ids),'n_steps':len(groups),'candidate_rows':len(cols),
       'fold_animals':{str(k):sum(fold[a]==k for a in ids) for k in range(5)},
       'models':{name:{'features':FEATURES[name],
          'equal_animal_heldout_logloss_nats':float(np.mean([perid[a][name] for a in ids]))} for name in FEATURES},
       'primary_road_origin_vs_destination':contrast('road','destination','road_origin',True),
       'secondary_traffic_origin_vs_road':contrast('traffic','road_origin','risk_origin',False),
       'source_deviation_coefficients_by_fold':coeffs,
       'anonymous_individual_scores':[{'label':'A'+str(i+1).zfill(2),'n_steps':perid[a]['n_groups'],
           'road_gain':perid[a]['destination']-perid[a]['road_origin'],
           'traffic_increment':perid[a]['road_origin']-perid[a]['risk_origin']}
           for i,a in enumerate(ids)]}
    return result

def main(output):
    result={'schema':'ecostate.v10c.original_wolverine_start_end_choice','source':'10.5281/zenodo.5011732',
       'original_sha256':SOURCE_SHA256,'status':'SOURCE_STOP','primary_gate':'NOT_TESTED',
       'claim_ceiling':['Original 2018 Scrafford et al road avoidance and traffic movement effects already established.',
          'A source-state similarity predictive gain would not demonstrate active preference or state-buffering causality.',
          'No geographic coordinates, fully reachable alternative habitat network or observed prey/fitness.']}
    try:
        t,p=source()
        try:d,qc=build(p)
        finally:t.cleanup()
        admitted,qc=group_admit(d,qc)
        result['qc']=qc
        a=fit_eval(d,admitted)
        result.update({'status':'ORIGINAL_FIELD_COMPUTED','primary_gate':a['primary_road_origin_vs_destination']['fixed_biological_direction_gate'],'scores':a})
    except Exception as e:
        result.update({'status':'SOURCE_OR_MODEL_STOP','reason':str(e)[:1200]})
    out=Path(output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('WOLVERINE_V10C_RESULT',result['status'],result['primary_gate'],result.get('reason',''),
          result.get('scores',{}).get('primary_road_origin_vs_destination',''))
    return result

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'ecostate_v10/results/wolverine_field_v10c.json')
