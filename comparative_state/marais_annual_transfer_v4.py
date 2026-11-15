"""Exploratory post-source-domain correction of frozen Marais annual field endpoint.

v3 remains immutable and SOURCE_SCHEMA_STOP (noninteger bird counts).
v4 excludes one untrustworthy entire source site: site 18 had two original
species-abundance/Abondance disagreements (2019_18, 2020_18), as documented
before any environmental prediction scores were opened. No source number repaired.
Everything else (species, predictors, regression alpha, model, null, LOO sites)
is exactly the v3 pre-outcome method; this is exploratory, not fully prospective.
"""
import argparse,hashlib,json,zipfile
from pathlib import Path
from .marais_annual_transfer_v3 import (MD5,S,SEED,SOURCE_DOI,read_rows_xlsx,
  extract_siteyears,build_transitions,score_models,bootstrap)
import numpy as np

EXCLUDED_SITE=18
SOURCE_DOMAIN_ANOMALY_IDS={'2019_18','2020_18'}

def source_grammar_amendment(rows):
    """Check two exact original anomaly IDs, then delete entire site 18 *before* model effects."""
    valid=[];seen=set();failed=[]
    for row,c in rows:
        key=c.get(0)
        if not isinstance(key,str) or row<3:
            valid.append((row,c));continue
        if key in SOURCE_DOMAIN_ANOMALY_IDS:
            seen.add(key)
            vals=[c.get(i) for i in range(10,58)]
            nonint=sum(not isinstance(v,(float,int)) or float(v)<0 or float(v)!=int(float(v)) for v in vals)
            total=c.get(58)
            discrepancy=not isinstance(total,(int,float)) or abs(sum(vals)-total)>0.01
            if nonint < 1 or not discrepancy:
                raise ValueError('SOURCE_SCHEMA_STOP: registered original anomaly no longer reproduced')
            failed.append({'siteyear':key,'noninteger_species_cells':nonint,
               'abundance_total_disagrees':True})
        if key.rsplit('_',1)[-1]=='18':
            continue
        valid.append((row,c))
    if seen!=SOURCE_DOMAIN_ANOMALY_IDS:
        raise ValueError('SOURCE_SCHEMA_STOP: original two record anomalies absent')
    return valid,failed

def run(src,out):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    status={'source_doi':SOURCE_DOI,'analysis_kind':'annual site-level species composition',
           'claim_class':'EXPLORATORY_POST_SOURCE_DOMAIN_AMENDMENT',
           'parent_frozen_v3_status':'SOURCE_SCHEMA_STOP_NONINTEGER_SPECIES_COUNTS',
           'fixed_original_source_site_excluded':18,
           'does_not_test':'individual mobility, year-specific habitat accessibility, or causation',
           'status':'SOURCE_STOP'}
    try:
        raw=Path(src).read_bytes()
        if hashlib.md5(raw).hexdigest()!=MD5:raise ValueError('SOURCE_STOP source MD5 mismatch')
        rows,anom=source_grammar_amendment(read_rows_xlsx(src))
        byid,taxa=extract_siteyears(rows)
        sites=sorted(set(x for x,y in byid))
        if len(byid)!=87 or len(sites)!=17 or len(taxa)!=S:
            raise ValueError('SOURCE_SCHEMA_STOP unexpected original nonanomalous panel counts')
        trans=build_transitions(byid)
        status.update(status='SOURCE_ONLY_PASS', original_source_sha256=hashlib.sha256(raw).hexdigest(),
          source_anomalies=anom,excluded_site_id=18,
          retained_original_siteyears=len(byid),retained_independent_sites=len(sites),
          eligible_annual_transitions=len(trans),species_columns=len(taxa))
        sc=score_models(trans)
        status.update(sc)
        if sc['status'].startswith('VALID_'):
            site_res=sc['site_results'];status['contrasts']={}
            for m in ['M1_water','M2_veg','M3_all']:
                g=[x[f'gain_{m}'] for x in site_res]
                status['contrasts'][m]={'mean_site_equal_gain_nats':float(np.mean(g)),
                   'site_cluster_bootstrap_95pct':bootstrap(g),
                   'positive_sites':sum(v>0 for v in g),
                   'negative_or_zero_sites':sum(v<=0 for v in g)}
            p=status['contrasts']['M1_water'];status['primary_pass']=p['site_cluster_bootstrap_95pct'][0]>0 and p['positive_sites']>len(site_res)/2
            status['baseline_CE_nats']=float(np.mean([x['CE_M0'] for x in site_res]))
    except (ValueError,KeyError,RuntimeError,OSError,IndexError,zipfile.BadZipFile) as e:
        status.update(status='SOURCE_STOP',source_domain_reason=str(e),effects_scored=False)
    out.write_text(json.dumps(status,indent=2,allow_nan=False)+'\n')
    print('MARAIS_ANNUAL_TRANSFER_V4',status['status'])
    if status['status']=='SOURCE_STOP':print(status['source_domain_reason'])
    return status

if __name__=='__main__':
    pa=argparse.ArgumentParser();pa.add_argument('--source',required=True);pa.add_argument('--out',required=True)
    a=pa.parse_args();run(a.source,a.out)
