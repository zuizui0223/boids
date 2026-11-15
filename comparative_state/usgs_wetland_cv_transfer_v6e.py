"""Immutable v6c predictor with only original Year1/Year2 source grammar corrected."""
from __future__ import annotations
import argparse,csv,hashlib,io,json
from pathlib import Path
from comparative_state import usgs_wetland_cv_transfer_v6c as v6c
from comparative_state import usgs_wetland_year_grammar_v6d as v6d

MAP={'Year1':'2022','Year2':'2023'}
EXPECTED={'Year1':{'2022':136},'Year2':{'2023':104}}


def normalize_years(rows, audit):
    """Exactly one permitted source-only transformation before any v6c outcomes."""
    if audit.get('status')!='SOURCE_YEAR_GRAMMAR_ADMITTED':
        raise ValueError('SOURCE_STOP_YEAR_GRAMMAR')
    if audit.get('year_token_to_calendar_year_counts')!=EXPECTED:
        raise ValueError('SOURCE_STOP_UNEXPECTED_NATIVE_YEAR_MAPPING')
    if audit.get('date_format_counts')!={'%m/%d/%Y':240}:
        raise ValueError('SOURCE_STOP_UNEXPECTED_DATE_FORMAT')
    if len(rows)!=240:raise ValueError('SOURCE_STOP_UNEXPECTED_ROW_COUNT')
    result=[]
    for r in rows:
        v=dict(r)
        if v['Study year'].strip() not in MAP:raise ValueError('SOURCE_STOP_UNEXPECTED_YEAR_TOKEN')
        v['Study year']=MAP[v['Study year'].strip()]
        result.append(v)
    return result


def run(out):
    receipt={'schema':'ecostate.usgs_wetland_original_year_amendment_v6e',
             'source_doi':'10.5066/P13UJQP5','source_file':'BirdUseCWHP.csv',
             'status':'SOURCE_STOP','primary_gate':'NOT_EVALUATED',
             'amendment':'Source-only Year1 (2022) / Year2 (2023) native grammar; v6c model unchanged',
             'original_v6c_primary_result':'SOURCE_DOMAIN_STOP_NO_ECOLOGICAL_SCORES'}
    try:
        b=v6c.read_exact_source()
        receipt['source_original_sha256']=hashlib.sha256(b).hexdigest()
        grammar=v6d.audit(b)
        receipt['source_native_year_codes']=grammar.get('year_token_to_calendar_year_counts')
        source_rows=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
        rows=normalize_years(source_rows,grammar)
        qc,valid=v6c.parse_input(rows)
        receipt['qc']=qc;receipt['status']=qc['status']
        if valid is not None:
            scored=v6c.bootstrap(v6c.property_holdout(valid))
            receipt.update(scored)
    except Exception as e:
        receipt.update({'status':'SOURCE_STOP_OR_ANALYSIS_EXCEPTION',
                        'exception_type':type(e).__name__,'exception':str(e)[:350]})
    receipt['claim_ceiling']=[
       'Independent source group use counts, not individual movement or state tracking',
       'Original published paper already modelled water-depth CV, so this only tests out-of-property incremental prediction',
       'Do not retune threshold, exclude species/property after outcome, or reinterpret original v6c STOP']
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('USGS_WETLAND_V6E',receipt['status'],receipt['primary_gate'],receipt.get('per_property',{}).get('log_shore_minus_dabbling',{}))
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='comparative_state/results/usgs_wetland_cv_transfer_v6e.json')
    run(p.parse_args().out)
