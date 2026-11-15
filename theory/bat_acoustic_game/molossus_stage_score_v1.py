"""Post-outcome stage audit of published Molossus data; no new measurements.

Preserve E=1, original M2 fits and whole-bat holdouts. Compare distinct
prediction tasks, not additive causal effects. Never export original bat IDs.
"""
from __future__ import annotations
import hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent
EXPECTED='pnas.2321724121.sd01.xlsx'
EXPECTED_SHA='92acbc36cce42028bfd5a07ad1ec8aa8062121575d6d665dc7392b47222f562d'
OUTPUT=ROOT/'MOLOSSUS_STAGE_SCORE_AUDIT_RESULT_V1.json'

def inspect_bundle(data, expected_sha=EXPECTED_SHA):
    """Strict analytical member identity; ZIP container is provenance only."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        matches=[i for i in z.infolist() if i.filename.split('/')[-1]==EXPECTED]
        if len(matches)!=1:raise ValueError('Original XLSX must occur exactly once')
        raw=z.read(matches[0]); sha=hashlib.sha256(raw).hexdigest()
        if sha!=expected_sha:raise ValueError('Original analytical workbook SHA changed')
        members={i.filename:hashlib.sha256(z.read(i)).hexdigest()
                 for i in z.infolist() if not i.is_dir()}
        receipt={'zip_sha256':hashlib.sha256(data).hexdigest(),
                 'xlsx_sha256':sha,'members':members,
                 'member_zip_timestamps':{i.filename:list(i.date_time) for i in z.infolist()}}
    return receipt,raw

def conditional_nll(y,a,p):
    y=np.asarray(y,dtype=float);a=np.asarray(a,dtype=float);p=np.asarray(p,dtype=float)
    if y.shape!=a.shape or p.shape!=a.shape or np.any(y<0) or np.any(a<y):
        raise ValueError('Invalid successes, attempts or probability dimensions')
    if not np.all(np.isfinite(y+a+p)) or np.any(p<0) or np.any(p>1):
        raise ValueError('Invalid probability/count')
    if a.sum()==0:return None
    p=np.clip(p,1e-12,1-1e-12)
    return float(-np.sum(y*np.log(p)+(a-y)*np.log1p(-p))/a.sum())

def summarize_pairs(pairs):
    valid=[x for x in pairs if x[0] is not None and x[1] is not None]
    if not valid:return {'eligible_bats':0,'difference_mean':None}
    a=np.asarray(valid,dtype=float);d=a[:,1]-a[:,0]
    rng=np.random.default_rng(20261106)
    boot=np.mean(rng.choice(d,size=(5000,len(d)),replace=True),axis=1)
    return {'eligible_bats':len(d),'baseline_mean':float(a[:,0].mean()),
            'density_mean':float(a[:,1].mean()),'difference_mean':float(d.mean()),
            'paired_bat_bootstrap95':np.quantile(boot,[.025,.975]).tolist(),
            'bats_improved':int(np.sum(d< -1e-12)),
            'bats_worsened':int(np.sum(d>1e-12)),
            'bats_tied':int(np.sum(np.abs(d)<=1e-12))}

def evaluate_stages(rows):
    from molossus_2024_source_capture_LOBO_v1 import model_rates, poisson_deviance_per_exposure, density_bin, DENSITY_BINS
    bats=sorted({r['bat'] for r in rows})
    pairs={k:[] for k in ('attacks','success_given_attack','total_captures')}
    calibration={b:{'rows':0,'attacks':0,'captures':0,'supporting_bats':set(),
          'predicted_attacks':0.,'predicted_captures':0.,
          'predicted_successes_given_observed_attacks':0.} for b in DENSITY_BINS}
    for bat in bats:
        train=[r for r in rows if r['bat']!=bat];test=[r for r in rows if r['bat']==bat]
        assert len({r['bat'] for r in train})>=7
        assert all(r['E']==1 for r in train+test)
        rates=model_rates(train,test)
        A=np.asarray([r['A'] for r in test],dtype=float)
        Y=np.asarray([r['Y'] for r in test],dtype=float)
        n=len(test)
        A0=(sum(r['A'] for r in train)+.5)/(len(train)+1)
        p0=(sum(r['Y'] for r in train)+.5)/(sum(r['A'] for r in train)+1)
        predA=rates['source_predicted_attack_rate']
        predp=rates['source_predicted_attack_success_fraction']
        pairs['attacks'].append((poisson_deviance_per_exposure(A,np.full(n,A0),n),
                                 poisson_deviance_per_exposure(A,predA,n)))
        pairs['success_given_attack'].append((conditional_nll(Y,A,np.full(n,p0)),
                                               conditional_nll(Y,A,predp)))
        pairs['total_captures'].append((poisson_deviance_per_exposure(Y,rates['M0'],n),
                                        poisson_deviance_per_exposure(Y,rates['M2'],n)))
        for i,row in enumerate(test):
            c=calibration[density_bin(row['density'])]
            c['rows']+=1;c['attacks']+=row['A'];c['captures']+=row['Y']
            c['supporting_bats'].add(bat)
            c['predicted_attacks']+=float(predA[i])
            c['predicted_captures']+=float(rates['M2'][i])
            c['predicted_successes_given_observed_attacks']+=float(A[i]*predp[i])
    for v in calibration.values():v['supporting_bats']=len(v['supporting_bats'])
    return {'bat_count':len(bats),'five_second_rows':len(rows),
            'stages':{k:summarize_pairs(v) for k,v in pairs.items()},
            'heldout_pooled_density_calibration':calibration,
            'score_units':{'attacks':'Poisson deviance / 5s',
              'success_given_attack':'binomial NLL / observed attack',
              'total_captures':'Poisson deviance / 5s'}}

def run():
    from molossus_2024_supplement_structure_v1 import download_bounded, URL
    from molossus_2024_source_capture_LOBO_v1 import decode_sheet
    from molossus_2024_source_capture_LOBO_corrected_v2 import admit_corrected_source
    assert (ROOT/'MOLOSSUS_STAGE_SCORE_AUDIT_PREOUTPUT_2026_11_06.md').exists()
    receipts=[];raw=None
    for _ in range(2):
        data,_,_=download_bounded(URL)
        receipt,raw=inspect_bundle(data)
        receipts.append(receipt)
    assert receipts[0]['members']==receipts[1]['members'], 'Member contents changed between requests'
    rows,clean,qc=admit_corrected_source(decode_sheet(raw))
    all_result=evaluate_stages(rows)
    clean_result=evaluate_stages([r for r in rows if r['bat'] in clean])
    ledger=json.loads((ROOT/'MOLOSSUS_2024_CORRECTED_CAPTURE_SOURCE_RESULTS_LEDGER_V2.json').read_text())
    for name,result in [('primary_all_ten_source_bats',all_result),
                        ('sensitivity_nine_source_time_consecutive_bats',clean_result)]:
        prior=ledger['cohorts'][name]['source_bat_equal_holdout']['source_model_scores']
        for key,m in [('baseline_mean','M0'),('density_mean','M2')]:
            assert math.isclose(result['stages']['total_captures'][key],
                  prior[m]['equal_bat_mean_capture_deviance_per_5s'],rel_tol=1e-9,abs_tol=1e-10)
    return {'schema':1,'date':'2026-11-06',
      'status':'POST_OUTCOME_STAGE_SCORE_AUDIT_OF_PUBLISHED_MOLOSSUS_SOURCE',
      'source_doi':'10.1073/pnas.2321724121','source_xlsx_sha256':EXPECTED_SHA,
      'new_measurements':False,'raw_bat_ids_or_rows_exported':False,
      'original_M2_models_unchanged':True,'previous_total_capture_scores_reproduced':True,
      'package_diagnostic':{'downloads':receipts,
        'all_member_hashes_identical':receipts[0]['members']==receipts[1]['members'],
        'package_hash_equal':receipts[0]['zip_sha256']==receipts[1]['zip_sha256'],
        'historical_package_sha256':ledger['original_supplement_zip_SHA256']},
      'source_quality':qc,'all_ten':all_result,'nine_clean':clean_result,
      'limitations':['Post-outcome secondary diagnostic in one already-published study.',
        'Ten bats, each one tracked flight; nine-clean is overlapping sensitivity.',
        'Conditional score uses observed attacks and is not total-capture forecasting.',
        'Different stage score units are not additive.',
        'Call density is observational; no causal sonar-jamming conclusion.',
        'Fixed source SHA and E=1; old numel-exposure V1 remains invalid.']}

if __name__=='__main__':
    result=run()
    OUTPUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PACKAGE_DIAGNOSTIC',json.dumps(result['package_diagnostic'],sort_keys=True))
    for group in ('all_ten','nine_clean'):
        print('STAGE_RESULT',group,json.dumps(result[group],sort_keys=True))
    print('SOURCE_XLSX_IDENTITY_AND_PREVIOUS_TOTAL_CAPTURE_SCORES_VERIFIED')
