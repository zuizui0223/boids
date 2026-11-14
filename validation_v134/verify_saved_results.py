"""Read-only integrity checks for v134 evidence and prepared model results.

This checks source linkage and numerical consistency, not substantive scientific
eligibility or authenticity of source bytes. Optional caches are never downloaded;
--replay-directory reads an already completed penguin_analysis prepared replay.
Run from the repository root: python -m validation_v134.verify_saved_results.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd


class Checks:
    def __init__(self):
        self.count = 0

    def require(self, condition, label):
        if not condition:
            raise ValueError(label)
        self.count += 1

    def equal(self, actual, expected, label):
        self.require(actual == expected, label)

    def near(self, actual, expected, label, tolerance=1e-10):
        self.require(bool(np.isfinite(actual) and np.isfinite(expected)
                          and abs(actual - expected) <= tolerance), label)


def read_json(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pointer(document, value):
    if not value:
        return document
    if not value.startswith('/'):
        raise ValueError('INVALID_JSON_POINTER')
    for part in value[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        document = document[int(part)] if isinstance(document, list) else document[part]
    return document


def csv_value(value):
    return '' if value is None else str(value)


def verify_evidence(root, checks, fulltext_cache=None, rescue_cache=None):
    directory = root / 'validation_v134'
    records = read_json(directory / 'results/normalized_study_decisions.json')
    checks.equal(len(records), 118, 'DECISION_COUNT')
    checks.equal(len({r['doi'] for r in records}), len(records), 'DUPLICATE_DECISION_DOI')
    old = read_json(root / 'validation_v133/results/fulltext_access_audit.json')
    rescue = read_json(directory / 'results/rescue_access_audit.json')
    checks.equal(old['input_corpus_sha256'], rescue['input_corpus_sha256'], 'SOURCE_CORPUS_HASH')
    checks.equal(Counter(r['status'] for r in old['records']), old['access_status_counts'], 'OLD_ACCESS_COUNTS')
    checks.equal(Counter(r['status'] for r in rescue['records']), rescue['access_status_counts'], 'RESCUE_ACCESS_COUNTS')
    checks.equal(len(rescue['records']), rescue['selected_candidates'], 'RESCUE_SELECTION_COUNT')
    checks.equal(len({r['id'] for r in rescue['records']}), len(rescue['records']), 'RESCUE_DUPLICATE_ID')
    checks.equal(len(old['records']), old['selected_field_metadata_candidates'], 'OLD_SELECTION_COUNT')
    sources = {
        'v133_acquired': {r['doi'].lower(): r for r in old['records'] if r['status']=='ORIGINAL_XML_RETRIEVED_DOI_VERIFIED'},
        'uncertain_rescue': {r['doi'].lower(): r for r in rescue['records'] if r['status'] in ('ORIGINAL_XML_IDENTITY_AND_BODY_VERIFIED','ORIGINAL_XML_VERIFIED_BODY_UNAVAILABLE')},
    }
    checks.equal(len(sources['v133_acquired']), 86, 'OLD_XML_SOURCE_COUNT')
    checks.equal(len(sources['uncertain_rescue']), 32, 'RESCUE_XML_SOURCE_COUNT')
    checks.require(not (sources['v133_acquired'].keys() & sources['uncertain_rescue'].keys()), 'OVERLAPPING_SOURCE_ARMS')
    old_dois = {r['doi'].lower() for r in read_json(root/'validation_v133/source_evidence_index.json')['studies']}
    ledgers = {f'validation_v134/{name}': read_json(directory/name) for name in
               ('fulltext_screen_a.json', 'fulltext_screen_b.json', 'rescue_fulltext_screen.json')}
    expected_pointers = set()
    for name, document in ledgers.items():
        rows = document if isinstance(document, list) else document['records']
        expected_pointers.update((name, f'/{i}' if isinstance(document, list) else f'/records/{i}') for i in range(len(rows)))
    checks.equal({(r['ledger'], r['json_pointer']) for r in records}, expected_pointers, 'LEDGER_POINTER_COVERAGE')
    for origin, source in sources.items():
        checks.equal({r['doi'] for r in records if r['origin'] == origin}, set(source), 'SOURCE_DECISION_SET_'+origin)
    expected_numeric = []
    xml_count = 0
    for record in records:
        doi = record['doi']
        checks.equal(doi, doi.lower(), 'NONNORMALIZED_DECISION_DOI')
        row = pointer(ledgers[record['ledger']], record['json_pointer'])
        source = row.get('source', row.get('original_source', {}))
        access = sources[record['origin']][doi]
        checks.equal(str(row['doi']).lower(), doi, 'LEDGER_DOI_POINTER')
        checks.equal(row.get('decision', row.get('screening_decision')), record['decision'], 'LEDGER_DECISION')
        basis = row.get('screen_method', row.get('screening_basis', ''))
        checks.equal(record['screening_basis'], basis, 'LEDGER_SCREENING_BASIS')
        checks.equal(record['fulltext_substantively_read'], bool(row.get('focal_fulltext_read', 'Scope excluded from focal title/abstract' not in basis)), 'LEDGER_READ_CLAIM')
        checks.equal(record['endpoint_family'], row.get('endpoint_family', row.get('response_family')), 'LEDGER_ENDPOINT')
        for key in ('title', 'year', 'pmcid'):
            checks.equal(record[key], row.get(key), 'LEDGER_'+key.upper())
        checks.equal(source['sha256'], access['original_xml_sha256'], 'SOURCE_LEDGER_SHA_LINK')
        checks.equal(record['original_xml_sha256'], source['sha256'], 'SOURCE_NORMALIZED_SHA_LINK')
        checks.equal(source['bytes'], access['original_xml_bytes'], 'SOURCE_BYTE_LINK')
        checks.equal(record['pmcid'], access['resolved_pmcid'], 'SOURCE_PMCID_LINK')
        checks.equal(record['original_url'], access['fulltext_url'], 'SOURCE_URL_LINK')
        checks.equal(record['previously_audited_v133'], doi in old_dois, 'SOURCE_OLD_AUDIT_OVERLAP')
        checks.equal(record['body_available'], source.get('has_body', source.get('substantive_body_available', True)), 'SOURCE_BODY_LEDGER')
        checks.require(record['body_available'] or record['decision']=='UNRESOLVED', 'BODY_UNAVAILABLE_MUST_BE_UNRESOLVED')
        checks.require(not record['harmonized_meta_effect_admitted'], 'UNEXPECTED_META_ADMISSION')
        effects_key = 'effects' if 'decision' in row else 'numeric_effects'
        effects = row.get(effects_key, [])
        checks.equal(record['numeric_records'], len(effects), 'NUMERIC_LEDGER_COUNT')
        for i, effect in enumerate(effects):
            expected_numeric.append({
                'doi': doi, 'origin': record['origin'], 'screen_decision': record['decision'],
                'endpoint_family': record['endpoint_family'], 'label': effect.get('label'),
                'estimate': effect.get('estimate'), 'reported_se': effect.get('se'), 'reported_sd': effect.get('sd'),
                'reported_interval_json': json.dumps(effect.get('ci', effect.get('interval')), ensure_ascii=False),
                'scale_or_units': effect.get('scale', effect.get('units')),
                'role_as_extracted': effect.get('role', 'REPORTED_STATISTIC_SEE_SOURCE_LEDGER'),
                'source_locator': effect.get('locator', effect.get('source_locator')),
                'ledger': record['ledger'], 'json_pointer': record['json_pointer']+f'/{effects_key}/{i}', 'meta_included': False,
            })
        cache = fulltext_cache if record['origin']=='v133_acquired' else rescue_cache
        if cache is not None:
            path = Path(cache)/(record['pmcid']+'.xml')
            checks.require(path.is_file(), 'XML_CACHE_FILE_MISSING: '+str(path))
            raw = path.read_bytes()
            checks.equal(hashlib.sha256(raw).hexdigest(), access['original_xml_sha256'], 'XML_HASH: '+doi)
            checks.equal(len(raw), access['original_xml_bytes'], 'XML_BYTES: '+doi)
            article = ET.fromstring(raw)
            focal = {str(n.text or '').lower().removeprefix('https://doi.org/').removeprefix('doi:').strip()
                     for n in article.findall('./front/article-meta/article-id') if n.get('pub-id-type')=='doi'}
            checks.require(doi in focal, 'XML_FOCAL_DOI: '+doi)
            body = article.find('body')
            has_body = body is not None and bool(''.join(body.itertext()).strip())
            checks.equal(has_body, record['body_available'], 'XML_BODY_STATUS: '+doi)
            xml_count += 1
    with (directory/'results/reported_numeric_records.csv').open(newline='') as stream:
        actual_numeric = list(csv.DictReader(stream))
    checks.equal(actual_numeric, [{k:csv_value(v) for k,v in row.items()} for row in expected_numeric], 'NUMERIC_CSV_POINTER_VALUES')
    summary = read_json(directory/'results/evidence_summary.json')
    expected = {
        'decision_records':len(records), 'distinct_article_dois':len({r['doi'] for r in records}),
        'substantive_bodies_available':sum(r['body_available'] for r in records),
        'substantive_fulltext_read_records':sum(r['fulltext_substantively_read'] for r in records),
        'decision_counts':dict(Counter(r['decision'] for r in records)), 'by_origin':dict(Counter(r['origin'] for r in records)),
        'numeric_extraction_records':len(expected_numeric), 'articles_with_numeric_records':sum(r['numeric_records']>0 for r in records),
        'overlap_with_v133_17_article_source_audit':sum(r['doi'] in old_dois for r in records),
        'new_to_v133_17_article_source_audit':sum(r['doi'] not in old_dois for r in records),
        'frozen_metadata_corpus':old['input_metadata_candidates'],
        'prior_field_triage_candidates':len(old['records']), 'fixed_rule_uncertain_rescue_candidates':len(rescue['records']),
        'total_targeted_article_access_checks':len(old['records'])+len(rescue['records']),
        'remaining_metadata_records_outside_these_targeted_checks':old['input_metadata_candidates']-len(old['records'])-len(rescue['records']),
        'rescue_access_status_counts':dict(Counter(r['status'] for r in rescue['records'])),
        'global_meta_pooled_effect':'NOT_ESTIMATED', 'human_two_rater_prisma_adjudication_completed':False,
        'article_and_record_counts_are_not_independent_coast_study_counts':True,
    }
    for key, value in expected.items():
        checks.equal(summary[key], value, 'EVIDENCE_SUMMARY_'+key)
    receipt = read_json(directory/'rescue_validation_receipt.json')
    checks.equal(receipt['screen_sha256'], sha256(directory/'rescue_fulltext_screen.json'), 'RESCUE_SCREEN_RECEIPT_HASH')
    checks.equal(receipt['numeric_entries'], sum(r['numeric_records'] for r in records if r['origin']=='uncertain_rescue'), 'RESCUE_NUMERIC_RECEIPT')
    published = read_json(directory/'published_effect_verification.json')
    for item in published['sources'].values():
        matches = [r for r in records if r['doi']==item['doi']]
        checks.equal(len(matches), 1, 'INDEPENDENT_EFFECT_SOURCE_MISSING')
        checks.equal(item['sha256'], matches[0]['original_xml_sha256'], 'INDEPENDENT_EFFECT_SOURCE_HASH')
    return {'decision_records':len(records), 'numeric_records':len(expected_numeric), 'original_xml_files_checked':xml_count}


def grouped_loss(frame, values):
    data = frame[['ID','week']].copy()
    data['value'] = values
    return float(data.groupby(['week','ID']).value.mean().groupby('week').mean().mean())


def verify_models(root, checks):
    directory = root/'validation_v134'
    output = directory/'results'
    result = read_json(output/'penguin_analysis_results.json')
    audit = read_json(output/'penguin_analysis_source_audit.json')
    checks.equal(sha256(root/'docs/V134_PENGUIN_PREFIT_ANALYSIS.md'), result['spec_sha256'], 'SPEC_HASH')
    digest = sha256(output/'penguin_15min_matched_inputs.csv.gz')
    checks.equal(digest, result['source_input_sha256'], 'MODEL_INPUT_HASH')
    checks.equal(digest, audit['prepared_input_sha256'], 'SOURCE_INPUT_HASH')
    inputs = pd.read_csv(output/'penguin_15min_matched_inputs.csv.gz')
    checks.require(not inputs.duplicated(['ID','window_start_seconds']).any(), 'DUPLICATE_INPUT_WINDOW')
    checks.require(inputs.common_support.dtype == bool, 'INPUT_SUPPORT_BOOLEAN')
    checks.require(inputs.n_seconds.between(720,900).all(), 'INPUT_DENOMINATOR_RANGE')
    for name in ['n_seconds','depth_gt_1','depth_gt_2','depth_gt_5']:
        checks.require(np.isfinite(inputs[name]).all() and (inputs[name]%1==0).all(), 'INPUT_INTEGER_'+name)
    checks.require(((0<=inputs.depth_gt_5)&(inputs.depth_gt_5<=inputs.depth_gt_2)&(inputs.depth_gt_2<=inputs.depth_gt_1)&(inputs.depth_gt_1<=inputs.n_seconds)).all(), 'INPUT_THRESHOLD_NESTING')
    checks.require(((inputs.time_seconds>=inputs.window_start_seconds)&(inputs.time_seconds<inputs.window_start_seconds+900)).all(), 'INPUT_TIME_IN_BIN')
    checks.equal(len(inputs), audit['aggregation']['eligible_windows'], 'INPUT_AGGREGATION_WINDOWS')
    checks.equal(int(inputs.n_seconds.sum()), audit['aggregation']['eligible_observed_seconds'], 'INPUT_AGGREGATION_SECONDS')
    common = inputs.common_support
    primary = common & (inputs.static_zero_vertices==0)
    for key, value in [('candidate_windows',len(inputs)), ('outside_common_support',int((~common).sum())),
                       ('common_support_windows',int(common.sum())), ('common_support_touching_static_zero_node',int((common&(inputs.static_zero_vertices>0)).sum())),
                       ('conservative_primary_windows',int(primary.sum()))]:
        checks.equal(audit['current_join'][key], value, 'CURRENT_JOIN_'+key)
    checks.equal(int(primary.sum()),3334,'PRIMARY_FROZEN_SAMPLE_SIZE')
    checks.equal(int(common.sum()),3373,'RETAIN_ZERO_FROZEN_SAMPLE_SIZE')
    speed_names = [f'speed_clock{c}_shift{s}_{m}' for c in [-3,0,3] for s in [-24,-18,-12,-6,0,6,12,18,24] for m in ['linear','floor','nearest']]
    checks.require(np.isfinite(inputs.loc[common,speed_names]).all().all(), 'MATCHED_SPEED_MISSING')
    checks.require((inputs.loc[common,speed_names]>=0).all().all(), 'MATCHED_SPEED_NEGATIVE')
    # Independent receipt correspondence: compare recalculable claims, not just its passed flags.
    independent = read_json(directory/'penguin_independent_verification.json')
    checks.equal(independent['minute_reaggregation_exact']['eligible_windows'],len(inputs),'INDEPENDENT_AGGREGATION_WINDOWS')
    checks.equal(independent['minute_reaggregation_exact']['denominator_total'],int(inputs.n_seconds.sum()),'INDEPENDENT_AGGREGATION_SECONDS')
    for threshold in [1,2,5]:
        checks.equal(independent['minute_reaggregation_exact']['threshold_totals'][str(threshold)],int(inputs[f'depth_gt_{threshold}'].sum()),'INDEPENDENT_THRESHOLD_TOTAL')
    checks.equal(independent['independent_current_alignment']['primary_windows'],int(primary.sum()),'INDEPENDENT_CURRENT_WINDOWS')
    configs = {'primary':(2,0,'linear',False,.01),'threshold_1m':(1,0,'linear',False,.01),'threshold_5m':(5,0,'linear',False,.01),
               'clock_minus3h':(2,-3,'linear',False,.01),'clock_plus3h':(2,3,'linear',False,.01),
               'nearest_hour':(2,0,'nearest',False,.01),'floor_hour':(2,0,'floor',False,.01),
               'retain_original_zero_nodes':(2,0,'linear',True,.01),'ridge_0.001':(2,0,'linear',False,.001),'ridge_0.1':(2,0,'linear',False,.1)}
    scenarios = {r['scenario']:r for r in result['scenarios']}
    checks.equal(len(result['scenarios']),len(configs),'SCENARIO_DUPLICATE_OR_MISSING')
    checks.equal(set(scenarios),set(configs),'SCENARIO_SET')
    primary_frame = None
    for name, scenario in scenarios.items():
        threshold,clock,mode,include_zero,penalty = configs[name]
        checks.equal(tuple(scenario[k] for k in ('threshold_m','clock_shift_hours','time_interpolation','include_static_zero_nodes','ridge_penalty')), configs[name], 'SCENARIO_CONFIGURATION_'+name)
        frame = inputs.loc[common if include_zero else primary].copy()
        frame['week']=pd.to_datetime(frame.time_seconds+(clock-3)*3600,unit='s',utc=True).dt.strftime('%G-W%V')
        y=frame[f'depth_gt_{threshold}'].to_numpy()/frame.n_seconds.to_numpy()
        if name=='primary': primary_frame=frame
        for key,value in [('windows',len(frame)),('animals',frame.ID.nunique()),('weeks',frame.week.nunique()),('observed_seconds',int(frame.n_seconds.sum()))]:
            checks.equal(scenario[key],value,'SCENARIO_COUNT_'+name+'_'+key)
        checks.equal(scenario['confirmatory_eight_week_gate'],frame.week.nunique()>=8,'CONFIRMATORY_GATE_'+name)
        checks.equal(scenario['day_windows']+scenario['night_windows'],len(frame),'DAY_NIGHT_COUNT_'+name)
        for fold in scenario['folds']:
            test=frame.week==fold['held_out_week'];train=~test
            a,b=set(frame.loc[train,'ID']),set(frame.loc[test,'ID'])
            for key,value in [('train_windows',int(train.sum())),('test_windows',int(test.sum())),('train_animals',len(a)),('test_animals',len(b)),('animals_in_both',len(a&b))]:
                checks.equal(fold[key],value,'FOLD_'+name+'_'+key)
        checks.equal({f['held_out_week'] for f in scenario['folds']},set(frame.week),'FOLD_WEEK_SET_'+name)
        prevalence=np.empty(len(frame))
        for week in frame.week.unique():
            test=(frame.week==week).to_numpy()
            train_data=pd.DataFrame({'ID':frame.ID.to_numpy()[~test],'y':y[~test]})
            prevalence[test]=train_data.groupby('ID').y.mean().mean()
        for label,p in [('diagnostic_constant_half',np.full(len(y),.5)),('diagnostic_training_prevalence',prevalence)]:
            loss=-(y*np.log(p)+(1-y)*np.log1p(-p))
            checks.near(scenario['scores'][label]['cross_entropy'],grouped_loss(frame,loss),'BASELINE_CE_'+name+'_'+label)
            checks.near(scenario['scores'][label]['squared_share_error'],grouped_loss(frame,(y-p)**2),'BASELINE_SQUARED_'+name+'_'+label)
        scores={k:v['cross_entropy'] for k,v in scenario['scores'].items()}
        wrong={k:v for k,v in scores.items() if k.startswith('current_') and k!='current_+0h'}
        checks.equal(len(wrong),8,'WRONG_CLOCK_COUNT')
        real=scores['current_+0h'];best=min(wrong,key=wrong.get)
        checks.near(scenario['delta_solar'],scores['M0']-scores['M1'],'DELTA_SOLAR_'+name)
        checks.near(scenario['delta_current'],scores['M1']-real,'DELTA_CURRENT_'+name)
        checks.near(scenario['delta_phase'],wrong[best]-real,'DELTA_PHASE_'+name)
        checks.equal(scenario['best_wrong_clock'],best,'BEST_WRONG_CLOCK_'+name)
        checks.equal(scenario['real_clock_rank_of_9'],1+sum(v<real for v in wrong.values()),'CLOCK_RANK_'+name)
    saved=pd.read_csv(output/'penguin_primary_animal_week_scores.csv')
    checks.require(not saved.duplicated(['ID','week']).any(),'DUPLICATE_ANIMAL_WEEK_SCORE')
    checks.equal(set(map(tuple,saved[['ID','week']].to_numpy())),set(map(tuple,primary_frame[['ID','week']].drop_duplicates().to_numpy())),'ANIMAL_WEEK_SCORE_SET')
    checks.equal(set(saved)-{'ID','week'},set(scenarios['primary']['scores']),'ANIMAL_WEEK_MODEL_SET')
    refit=read_json(directory/'penguin_independent_refit.json')
    for label,score in scenarios['primary']['scores'].items():
        checks.near(float(saved.groupby('week')[label].mean().mean()),score['cross_entropy'],'HIERARCHICAL_SCORE_'+label)
        checks.near(independent['primary_scores'][label],score['cross_entropy'],'INDEPENDENT_SCORE_'+label)
        if label in refit['scores']:
            checks.near(refit['scores'][label],score['cross_entropy'],'INDEPENDENT_REFIT_'+label,tolerance=5e-6)
            checks.near(refit['difference_from_saved_LBFGS'][label],refit['scores'][label]-score['cross_entropy'],'INDEPENDENT_REFIT_DIFFERENCE_'+label)
    checks.equal(result['independent_studies'],1,'STUDY_COUNT')
    checks.equal(result['independent_coasts'],1,'COAST_COUNT')
    checks.require('NOT_CONFIRMATORY' in result['status'] and 'NOT_GLOBAL_META_ANALYSIS' in result['status'],'INFERENCE_STATUS')
    return result


def verify_replay(saved, directory, checks, tolerance):
    replay=read_json(Path(directory)/'penguin_analysis_results.json')
    checks.equal(replay['spec_sha256'],saved['spec_sha256'],'REPLAY_SPEC_HASH')
    checks.equal(replay['source_input_sha256'],saved['source_input_sha256'],'REPLAY_INPUT_HASH')
    a={s['scenario']:s for s in saved['scenarios']};b={s['scenario']:s for s in replay['scenarios']}
    checks.equal(len(replay['scenarios']),len(a),'REPLAY_SCENARIO_COUNT')
    checks.equal(set(a),set(b),'REPLAY_SCENARIO_SET')
    maximum=0.
    for name in a:
        for key in ('threshold_m','clock_shift_hours','time_interpolation','include_static_zero_nodes','ridge_penalty','windows','animals','weeks','observed_seconds','night_windows','day_windows','folds','best_wrong_clock','real_clock_rank_of_9','confirmatory_eight_week_gate'):
            checks.equal(a[name][key],b[name][key],'REPLAY_'+name+'_'+key)
        checks.equal(set(a[name]['scores']),set(b[name]['scores']),'REPLAY_MODEL_SET_'+name)
        for model,metrics in a[name]['scores'].items():
            for metric,value in metrics.items():
                other=b[name]['scores'][model][metric]
                checks.near(value,other,'REPLAY_SCORE_'+name+'_'+model+'_'+metric,tolerance)
                maximum=max(maximum,abs(value-other))
        for delta in ('delta_solar','delta_current','delta_phase'):
            checks.near(a[name][delta],b[name][delta],'REPLAY_'+name+'_'+delta,tolerance)
    for label,interval in saved['primary_conditional_intervals']['intervals'].items():
        for a,b in zip(interval,replay['primary_conditional_intervals']['intervals'][label]):
            checks.near(a,b,'REPLAY_CONDITIONAL_INTERVAL_'+label,tolerance)
    return maximum


def verify(root=None, fulltext_cache=None, rescue_cache=None, replay_directory=None, tolerance=5e-6):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    checks=Checks()
    receipt=verify_evidence(root,checks,fulltext_cache,rescue_cache)
    result=verify_models(root,checks)
    receipt.update(scenarios=len(result['scenarios']),replay_compared=False)
    if replay_directory is not None:
        receipt['maximum_replay_score_difference']=verify_replay(result,replay_directory,checks,tolerance)
        receipt['replay_compared']=True
    receipt.update(checks_passed=checks.count,status='PASS',read_only=True,
                   scope='Cross-file numerical/provenance integrity; not human eligibility adjudication or a new biological test.')
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--fulltext-cache',type=Path)
    parser.add_argument('--rescue-cache',type=Path)
    parser.add_argument('--replay-directory',type=Path,help='Existing prepared replay output; this verifier never runs or writes a model.')
    parser.add_argument('--tolerance',type=float,default=5e-6,help='Absolute tolerance for optional replay numerical comparisons.')
    args=parser.parse_args()
    try:
        if not np.isfinite(args.tolerance) or args.tolerance<0:
            raise ValueError('INVALID_REPLAY_TOLERANCE')
        print(json.dumps(verify(args.repository,args.fulltext_cache,args.rescue_cache,args.replay_directory,args.tolerance),indent=2))
    except (ValueError,KeyError,IndexError,OSError,ET.ParseError) as error:
        parser.exit(1,f'VERIFICATION_FAILED: {error}\n')


if __name__=='__main__':
    main()
