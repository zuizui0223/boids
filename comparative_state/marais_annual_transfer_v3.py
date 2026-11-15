"""Source-pinned site-blocked *annual assemblage* state-change transfer.

Source: Secondi et al 2026, doi:10.5281/zenodo.18161913, MD5
 a08325ee4e24acfc159b1cd7c1fe425d (licensed CC BY 4.0).

This is NOT individual movement, state retention, causal habitat filtering, or
visit-time state switching.  Outcome scoring is only allowed after source gate.
Predeclared analysis date 2026-11-15 before original species counts opened.
"""
from __future__ import annotations
import argparse,hashlib,json,math,re,zipfile
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

MD5='a08325ee4e24acfc159b1cd7c1fe425d'
S=48
ALPHA=25.0
SMOOTH=0.5
SEED=20261115
SOURCE_DOI='10.5281/zenodo.18161913'
WATER=['WA.mean','WA.sd','WDH.mean','WDH.sd']
VEG=['VH.mean','VH.sd']
YEARS=list(range(2016,2021))


def column_index(cell_ref):
    m=re.match(r'^([A-Z]+)[0-9]+$',cell_ref)
    if not m:raise ValueError('SOURCE_STOP invalid Excel cell ref')
    o=0
    for c in m.group(1):o=o*26+ord(c)-64
    return o-1


def read_rows_xlsx(xlsx):
    """Minimal XLSX XML reader, no workbook values modified, exact sheet name."""
    with zipfile.ZipFile(xlsx) as z:
        ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
            'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        sheets=wb.find('m:sheets',ns)
        names=[(s.attrib.get('name'),s.attrib.get('{'+ns['r']+'}id')) for s in sheets]
        found=[rid for name,rid in names if name=='Bird by survey']
        if len(found)!=1:raise ValueError('SOURCE_STOP no unique Bird by survey sheet')
        relations=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        lookup={r.attrib['Id']:r.attrib['Target'] for r in relations}
        t=lookup[found[0]]
        filename=t.lstrip('/') if t.startswith('/') else 'xl/'+t
        if filename.startswith('xl/xl/'):filename=filename[3:]
        if filename not in z.namelist():raise ValueError('SOURCE_STOP workbook sheet target missing')
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            ss=ET.fromstring(z.read('xl/sharedStrings.xml'))
            strings=[''.join(t.text or '' for t in el.iter('{'+ns['m']+'}t'))
                     for el in ss.findall('m:si',ns)]
        sheet=ET.fromstring(z.read(filename))
        data=sheet.find('m:sheetData',ns)
        out=[]
        for row in data.findall('m:row',ns):
            cells={}
            for c in row.findall('m:c',ns):
                idx=column_index(c.attrib['r'])
                v=c.find('m:v',ns);typ=c.attrib.get('t','n')
                if typ=='inlineStr':
                    val=''.join(n.text or '' for n in c.iter('{'+ns['m']+'}t'))
                elif v is None:
                    val=None
                elif typ=='s':
                    val=strings[int(v.text)]
                elif typ in {'str','e'}:
                    val=v.text
                else:
                    try:val=float(v.text)
                    except (TypeError,ValueError):val=v.text
                cells[idx]=val
            out.append((int(row.attrib['r']),cells))
        return out


def strict_numeric(v,name,integer=False):
    if not isinstance(v,(int,float)) or not math.isfinite(float(v)) or v<0:
        raise ValueError('SOURCE_SCHEMA_STOP missing/negative/nonfinite numeric '+name)
    if integer and not float(v).is_integer():
        raise ValueError('SOURCE_SCHEMA_STOP noninteger species abundance '+name)
    return float(v)


def extract_siteyears(rows):
    hd=[c.get(i) for i in range(62) for r,c in rows if r==2]
    if len(hd)!=62 or hd[0]!='Survey_ID' or hd[10]!='Recurvirostra avosetta' or hd[58]!='Abondance':
        raise ValueError('SOURCE_SCHEMA_STOP unexpected Bird by survey exact source header')
    if [hd[i] for i in (4,5,6,7,8,9)]!=['WA.mean','WA.sd','VH.mean','VH.sd','WDH.mean','WDH.sd']:
        raise ValueError('SOURCE_SCHEMA_STOP environmental header changed')
    byid={}
    for row,c in rows:
        if row<3:continue
        name=c.get(0)
        if name is None:continue
        if not isinstance(name,str):raise ValueError('SOURCE_SCHEMA_STOP Survey_ID not text')
        m=re.fullmatch(r'(20\d{2})_(\d{1,2})',name)
        if not m:raise ValueError('SOURCE_SCHEMA_STOP unexpected siteyear key')
        year,site=int(m.group(1)),int(m.group(2))
        env={hd[i]:strict_numeric(c.get(i),hd[i]) for i in range(4,10)}
        abund=np.asarray([strict_numeric(c.get(i),hd[i],True) for i in range(10,58)],float)
        total=strict_numeric(c.get(58),'Abondance')
        if abs(abund.sum()-total)>0.01:
            raise ValueError('SOURCE_SCHEMA_STOP species sum disagrees with Abondance')
        if (site,year) in byid:raise ValueError('SOURCE_SCHEMA_STOP duplicate siteyear')
        byid[(site,year)]={'site':site,'year':year,'environment':env,'abund':abund,
                             'total':int(total)}
    return byid,hd[10:58]


def build_transitions(siteyears):
    trans=[]
    for (site,year),a in sorted(siteyears.items()):
        k=(site,year+1)
        if k not in siteyears:continue
        b=siteyears[k]
        if a['total']==0 or b['total']==0:continue
        trans.append({'site':site,'year':year+1,'prev':a['abund'], 'nprev':a['total'],
                      'next':b['abund'],'nnext':b['total'],
                      'change':{key: (math.log1p(b['environment'][key])-math.log1p(a['environment'][key]))
                                  if key.startswith('WA.') else b['environment'][key]-a['environment'][key]
                                for key in WATER+VEG}})
    return trans


def prepare_x(trans,training,feature_keys):
    years=np.asarray([[int(x['year']==y) for y in YEARS] for x in trans],float)
    if not feature_keys:return years
    feat=np.asarray([[x['change'][p] for p in feature_keys] for x in trans],float)
    scaler=StandardScaler().fit(feat[training])
    return np.hstack([years,scaler.transform(feat)])


def smoother(c):return (c+SMOOTH)/(float(np.sum(c))+len(c)*SMOOTH)


def annual_y(trans):
    vals=[]
    for t in trans:
        x=np.log(smoother(t['next']))-np.log(smoother(t['prev']))
        vals.append(x-x.mean())
    return np.asarray(vals)


def score_models(trans,alpha=ALPHA):
    """Returns equal-site annual composition CE gains M1/M2/M3 vs M0."""
    sites=sorted(set(t['site'] for t in trans))
    if len(sites)<12 or len(trans)<50:
        return {'status':'PRIMARY_NOT_ADMITTED','eligible_sites':len(sites),
                'eligible_annual_transitions':len(trans)}
    Y=annual_y(trans)
    q_next=np.asarray([t['next']/t['nnext'] for t in trans])
    q_prev=np.asarray([smoother(t['prev']) for t in trans])
    labels=['M0','M1_water','M2_veg','M3_all']
    feature_sets=[[],WATER,VEG,WATER+VEG]
    by_site=[]
    for site in sites:
        te=np.asarray([i for i,t in enumerate(trans) if t['site']==site],int)
        tr=np.asarray([i for i,t in enumerate(trans) if t['site']!=site],int)
        cnt=Counter(t['site'] for i,t in enumerate(trans) if i in set(tr))
        weights=np.asarray([1./cnt[trans[i]['site']] for i in tr])
        ce={}
        for lbl,feat in zip(labels,feature_sets):
            X=prepare_x(trans,tr,feat)
            r=Ridge(alpha=alpha,fit_intercept=True)
            r.fit(X[tr],Y[tr],sample_weight=weights)
            pred=r.predict(X[te])
            logits=np.log(q_prev[te])+pred
            logits=logits-logits.max(axis=1,keepdims=True)
            q=np.exp(logits);q=q/q.sum(axis=1,keepdims=True)
            ce[lbl]=float(np.mean(-np.sum(q_next[te]*np.log(q),axis=1)))
        by_site.append({'site':site,'transitions':len(te),**{f'CE_{k}':v for k,v in ce.items()},
                        **{f'gain_{label}':ce['M0']-ce[label] for label in labels[1:]}})
    return {'status':'VALID_ORIGINAL_SITE_HELDOUT_ASSEMBLAGE_RESULTS',
            'site_results':by_site,'eligible_sites':len(sites),'eligible_annual_transitions':len(trans),
            'alpha':alpha,'smoothing_per_species':SMOOTH}


def bootstrap(vals,nboot=10000):
    rng=np.random.default_rng(SEED)
    a=np.asarray(vals,float)
    b=np.mean(a[rng.integers(0,len(a),(nboot,len(a)))],axis=1)
    return [float(np.quantile(b,0.025)),float(np.quantile(b,0.975))]


def run(src,out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    status={'source_doi':SOURCE_DOI,'analysis_kind':'annual site-level species composition',
            'does_not_test':'individual movement, visit-time switching, true hydrological state portfolios',
            'status':'SOURCE_STOP'}
    try:
        raw=Path(src).read_bytes()
        if hashlib.md5(raw).hexdigest()!=MD5:raise ValueError('SOURCE_STOP original MD5 mismatch')
        siteyears,taxa=extract_siteyears(read_rows_xlsx(src))
        sites=sorted(set(s for s,y in siteyears))
        if len(siteyears)!=90 or len(sites)!=18 or len(taxa)!=S:
            raise ValueError('SOURCE_SCHEMA_STOP exact annual site/taxon structure mismatch')
        t=build_transitions(siteyears)
        status.update(original_md5=MD5,original_sha256=hashlib.sha256(raw).hexdigest(),
                      species_columns=len(taxa),original_siteyears=len(siteyears),
                      original_sites=len(sites), original_years=sorted(set(y for s,y in siteyears)),
                      eligible_yearly_transitions=len(t),eligible_sites_with_transitions=len(set(z['site'] for z in t)))
        score=score_models(t)
        status.update(score)
        if score['status'].startswith('VALID_'):
            s=score['site_results']
            status['primary']={}
            for name in ['M1_water','M2_veg','M3_all']:
                vals=[r[f'gain_{name}'] for r in s]
                status['primary'][name]={'heldout_site_equal_gain_nats_per_observed_bird':float(np.mean(vals)),
                    'cluster_site_bootstrap_95pct':bootstrap(vals),
                    'positive_sites':sum(v>0 for v in vals),
                    'negative_or_zero_sites':sum(v<=0 for v in vals)}
            p=status['primary']['M1_water'];status['primary_rule_pass']=p['cluster_site_bootstrap_95pct'][0]>0 and p['positive_sites']>len(s)/2
            status['mean_CE_M0']=float(np.mean([r['CE_M0'] for r in s]))
    except (ValueError,KeyError,RuntimeError,OSError,IndexError,zipfile.BadZipFile) as e:
        status.update(status='SOURCE_STOP',reason=str(e), original_effects_scored=False)
    out.write_text(json.dumps(status,indent=2,allow_nan=False)+'\n')
    print('MARAIS_ANNUAL_TRANSFER',status['status'])
    if status['status']=='SOURCE_STOP':print('STOP_REASON',status['reason'])
    return status

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',required=True);a.add_argument('--out',required=True)
    args=a.parse_args();run(args.source,args.out)
