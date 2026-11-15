"""Predeclared original USGS 2025 property-holdout water-depth heterogeneity transfer.

See docs/USGS_WETLAND_SOURCE_AND_MODEL_FREEZE_V6C.md.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, re, urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from comparative_state.usgs_2025_schema_gate_v6b import SOURCE, BYTES, MD5

CONTROLS=['Wetland area','Flooded area','Mean water depth','Percent of flooded area with emergent veg',
          'Percent of flooded area with mud','Mean veg height','Veg height CV',
          'Wetlands within 5 km of wetland boundary','Agriculture land within 5 km of wetland boundary',
          'Developed land within 5 km of wetland boundary']
DEPTH_CV='Water depth CV'
CATS=['Region','Study year','Wetland type year of survey']
COUNT_COLS=['Number of shorebirds','Number of dabbling ducks','Number of wading birds',
           'Number of secretive marsh birds','Number of waterbirds','Number of species']
ALL_COLS=CONTROLS+[DEPTH_CV]+CATS+COUNT_COLS+['County','Property','Wetland unit','Date']
RESULT_NAMES=['log_shore_minus_dabbling','log_shore','log_dabbling','log_wading',
              'log_secretive_marsh','log_total_waterbirds','log_species_richness']
YEARS=['2022','2023']
SEED=20261115
MISSING={'','na','n/a','null','nan','none','-','missing'}


def parse_date(text):
    a=text.strip()
    for fmt in ('%Y-%m-%d','%m/%d/%Y','%m/%d/%y','%Y/%m/%d','%d-%b-%Y','%m/%d/%Y %H:%M:%S'):
        try:return datetime.strptime(a,fmt)
        except ValueError:pass
    raise ValueError('bad date')


def parse_input(rows):
    """Parse predeclared original header. Do not repair numeric domain errors."""
    if not rows: return {'status':'SOURCE_SCHEMA_STOP_EMPTY'},None
    if any(c not in rows[0] for c in ALL_COLS):
        return {'status':'SOURCE_SCHEMA_STOP_COLUMNS', 'missing_columns':sorted(set(ALL_COLS)-set(rows[0]))},None
    valid=[];missing=Counter(); invalid=[]
    for rownum,row in enumerate(rows,start=2):
        if any(not str(row.get(x,'')).strip() for x in ['Region','County','Property','Wetland unit']+CATS):
            missing['site_or_categorical_key']+=1;continue
        nums={};fail=None
        for c in CONTROLS+[DEPTH_CV]+COUNT_COLS:
            raw=str(row.get(c,'')).strip()
            if raw.lower() in MISSING:
                missing[c]+=1;fail='missing';break
            try:v=float(raw)
            except ValueError:
                invalid.append({'rownum':rownum,'field':c,'reason':'not numeric'});fail='bad';break
            if not math.isfinite(v):
                invalid.append({'rownum':rownum,'field':c,'reason':'nonfinite'});fail='bad';break
            if c in COUNT_COLS and (v<0 or abs(v-round(v))>1e-7):
                invalid.append({'rownum':rownum,'field':c,'reason':'invalid count domain'});fail='bad';break
            if c==DEPTH_CV and v<0:
                invalid.append({'rownum':rownum,'field':c,'reason':'negative heterogeneity'});fail='bad';break
            if c in ('Wetland area','Flooded area') and v<0:
                invalid.append({'rownum':rownum,'field':c,'reason':'negative area'});fail='bad';break
            nums[c]=v
        if fail:continue
        try:d=parse_date(str(row.get('Date','')))
        except ValueError:
            missing['Date']+=1;continue
        year=str(row['Study year']).strip()
        if year not in YEARS:
            invalid.append({'rownum':rownum,'field':'Study year','reason':'unregistered year'});continue
        # A date/year mismatch would be an audit failure, not a repair.
        if d.year!=int(year):
            invalid.append({'rownum':rownum,'field':'Date','reason':'date/year discrepancy'});continue
        prop='|'.join(str(row[x]).strip() for x in ['Region','County','Property'])
        wet='|'.join([prop,str(row['Wetland unit']).strip()])
        p={**nums,'Region':str(row['Region']).strip(),'Study year':year,
           'Wetland type year of survey':str(row['Wetland type year of survey']).strip(),
           'property_key':prop,'wetland_key':wet,'month':d.month,
           'sin_doy':math.sin(2*math.pi*d.timetuple().tm_yday/365.25),
           'cos_doy':math.cos(2*math.pi*d.timetuple().tm_yday/365.25)}
        valid.append(p)
    qc={'source_rows':len(rows),'valid_rows':len(valid),'excluded_missing':sum(missing.values()),
        'missing_fields':dict(missing),'source_domain_invalid_count':len(invalid),
        'source_domain_invalid_first':invalid[:6]}
    if invalid:return {'status':'SOURCE_DOMAIN_STOP',**qc},None
    pcount=len(set(x['property_key'] for x in valid));wcount=len(set(x['wetland_key'] for x in valid));
    ycount=Counter(x['Study year'] for x in valid)
    qc.update({'original_properties':pcount,'original_wetlands':wcount,'eligible_year_counts':dict(ycount)})
    if (len(valid)<120 or wcount<50 or pcount<15 or any(ycount[y]<20 for y in YEARS)):
        return {'status':'SOURCE_SCHEMA_STOP_INSUFFICIENT_ORIGINAL_SUPPORT',**qc},None
    return {'status':'SOURCE_DOMAIN_ADMITTED',**qc},valid


def design(rows, include_cv):
    nums=CONTROLS+(['Water depth CV'] if include_cv else [])+['sin_doy','cos_doy']
    numer=np.array([[r[x] for x in nums] for r in rows],dtype=float)
    cats=np.array([[r[x] for x in CATS] for r in rows],dtype=str)
    return nums,numer,cats


def responses(rows):
    a=np.array([[r[x] for x in COUNT_COLS] for r in rows],dtype=float)
    lg=np.log1p(a)
    # source count order: shore, dabbling, wading, secretive, total, richness
    return np.column_stack((lg[:,0]-lg[:,1],lg))


def property_holdout(rows):
    props=sorted({r['property_key'] for r in rows})
    group_stats=[]
    ys=responses(rows)
    for prop in props:
        idx_train=[i for i,r in enumerate(rows) if r['property_key']!=prop]
        idx_test=[i for i,r in enumerate(rows) if r['property_key']==prop]
        train=[rows[i] for i in idx_train];test=[rows[i] for i in idx_test]
        train_props=Counter(x['property_key'] for x in train)
        weights=np.array([len(train)/(len(train_props)*train_props[x['property_key']]) for x in train])
        losses=[]
        for include in (False,True):
            ncols,xtn,ctn=design(train,include)
            _,xts,cts=design(test,include)
            # fixed preprocessing fitted only to training groups.
            mu=xtn.mean(axis=0);sd=xtn.std(axis=0);sd[sd==0]=1
            xtn=(xtn-mu)/sd;xts=(xts-mu)/sd
            enc=OneHotEncoder(handle_unknown='ignore',sparse_output=False)
            ctrain=enc.fit_transform(ctn);ctest=enc.transform(cts)
            Xtr=np.column_stack((xtn,ctrain));Xte=np.column_stack((xts,ctest))
            model=Ridge(alpha=10.0,fit_intercept=True)
            model.fit(Xtr,ys[idx_train],sample_weight=weights)
            pred=model.predict(Xte)
            losses.append(np.mean((ys[idx_test]-pred)**2,axis=0))
        gain=losses[0]-losses[1]
        group_stats.append({'property_nvisits':len(idx_test),'gain':gain.tolist(),
                            'mse_reference':losses[0].tolist(),'mse_plus_depth_CV':losses[1].tolist()})
    return group_stats


def bootstrap(group_stats, repetitions=20000, seed=SEED):
    if not group_stats:return None
    a=np.array([g['gain'] for g in group_stats]);rng=np.random.default_rng(seed)
    n=len(a);nmetric=a.shape[1]
    boot=np.empty((repetitions,nmetric),dtype=float)
    for z in range(repetitions):
        idx=rng.integers(0,n,size=n)
        boot[z]=a[idx].mean(axis=0)
    output={}
    for j,name in enumerate(RESULT_NAMES):
        values=a[:,j];lo,hi=np.quantile(boot[:,j],[0.025,0.975]);
        output[name]={'equal_property_mean_gain_log2':float(values.mean()),
                    'property_bootstrap_95':[float(lo),float(hi)],
                    'median_property_gain':float(np.median(values)),
                    'positive_properties':int((values>0).sum()),'properties':n}
    r=output[RESULT_NAMES[0]]
    verdict='PASS' if r['equal_property_mean_gain_log2']>0 and r['property_bootstrap_95'][0]>0 and r['positive_properties']/n>=0.6 else 'FAIL'
    return {'status':'FIELD_COMPUTED_EXPLORATORY','primary_gate':verdict,
            'metric':'difference in heldout squared log(1+count) guild-contrast prediction',
            'per_property':output,
            'property_visit_counts_summary':{'min':min(x['property_nvisits'] for x in group_stats),
                 'max':max(x['property_nvisits'] for x in group_stats),
                 'sum':sum(x['property_nvisits'] for x in group_stats)},
            'n_bootstrap':repetitions,'seed':seed}


def read_exact_source():
    req=urllib.request.Request(SOURCE,headers={'User-Agent':'ecostate-2026-USGS-transfer/6.2','Accept':'text/csv'})
    with urllib.request.urlopen(req,timeout=50) as r:
        b=r.read(BYTES+1)
    if len(b)!=BYTES or hashlib.md5(b).hexdigest()!=MD5: raise ValueError('SOURCE_STOP file MD5 or size mismatch')
    return b


def run(output):
    receipt={'schema':'ecostate.usgs_wetland_same_survey_cv_transfer_v6c',
             'source_doi':'10.5066/P13UJQP5','source_file':'BirdUseCWHP.csv',
             'status':'SOURCE_STOP','primary_gate':'NOT_EVALUATED',
             'evidence_class':'independent_original_source_external_property_transfer, hypothesis frozen before numeric outcomes'}
    try:
        data=read_exact_source();receipt['source_original_sha256']=hashlib.sha256(data).hexdigest()
        rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
        qc,valid=parse_input(rows)
        receipt['qc']=qc;receipt['status']=qc['status']
        if valid is not None:
            groups=property_holdout(valid)
            scored=bootstrap(groups)
            receipt.update(scored)
    except Exception as e:
        receipt.update({'status':'SOURCE_STOP_OR_ANALYSIS_EXCEPTION',
                       'exception_type':type(e).__name__,'exception':str(e)[:350]})
    receipt['claim_ceiling']=[
      'Same survey-day depth CV and guild abundance association evaluated for previously unseen properties in source California region only.',
      'No individual state retention, movement, choice sets, community assembly causation, or portfolio-exhaustion threshold measured.',
      'Original paper already reported guild/water relationships; do not call this biological mechanism discovery.',
      'Always retain negative and unsupported fixed primary results.']
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    print('USGS_WETLAND_V6C',receipt['status'],receipt['primary_gate'],
          receipt.get('per_property',{}).get('log_shore_minus_dabbling',{}))
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='comparative_state/results/usgs_wetland_cv_transfer_v6c.json');run(p.parse_args().out)
