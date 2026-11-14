"""v131 first-party *metadata-only* source inventory and bounded literature discovery.

NO biological raw telemetry, effect values, GPS locations, timestamps, animal IDs,
tidal-water values or unpublished research data are downloaded. No candidate
metadata hit is labelled as a completed meta-analysis study.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError,URLError
import argparse,json,re,time,unicodedata

SOURCE_FILE=Path(__file__).with_name('source_registry.json')
EUROPE_PMC='https://www.ebi.ac.uk/europepmc/webservices/rest/search'
SEARCH_CUTOFF=2026
SEARCH_RESULTS_PER_QUERY=35
PUBLISHER_FILE_LIMIT=15_000_000
WELL_KNOWN_KINDS=('zenodo','dryad','paper')
QUERIES={
  'tidal_diel_shorebird':'(tide OR tidal) AND (diel OR diurnal OR nocturnal) AND (shorebird OR oystercatcher OR wader)',
  'tidal_solar_seabird':'(tide OR tidal) AND (diel OR solar OR nocturnal) AND (seabird OR gull)',
  'tidal_fish':'(tidal OR circatidal) AND (fish OR teleost) AND (behaviour OR behavior OR movement OR activity)',
  'tidal_crustacean':'(tidal OR circatidal) AND (crab OR amphipod OR crustacean) AND (activity OR movement)',
  'tidal_benthic_mollusc':'(tidal OR circatidal) AND (mollusc OR limpet OR bivalve OR oyster) AND (rhythm OR activity)',
  'tidal_intertidal_insects':'(tidal OR circatidal OR circalunar) AND (intertidal OR mangrove) AND (insect OR midge OR cricket)',
  'light_tide_behavior':'(tidal AND (light OR photoperiod OR circadian) AND (behavior OR behaviour OR foraging))'
}


def fetch_json(url,max_bytes=PUBLISHER_FILE_LIMIT,timeout=20,tries=2,opener=None):
    op=opener or urlopen
    last=None
    for attempt in range(tries):
        try:
            req=Request(url,headers={'User-Agent':'boids-v131-global-meta-metadata-audit/1.0 (scientific study registry, publicly released metadata only)',
                   'Accept':'application/json'})
            with op(req,timeout=timeout) as response:
                payload=response.read(max_bytes+1)
                if len(payload)>max_bytes:raise ValueError('STOP_V131_PROVIDER_METADATA_EXCEEDS_SIZE_LIMIT')
            return json.loads(payload),sha256(payload).hexdigest()
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as e:
            last=e
            if attempt+1<tries:time.sleep(2*(attempt+1))
    raise RuntimeError('SOURCE_METADATA_UNAVAILABLE_'+str(last)[:120])


def norm_doi(x):
    val=str(x or '').strip().lower()
    return re.sub(r'^https?://(?:dx\.)?doi\.org/','',val).replace('doi:','').strip()


def normalize_title(x):
    s=unicodedata.normalize('NFKC',str(x or '')).casefold()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()


def validate_registry(source):
    if source.get('record_version')!='v131-source-candidates-1':raise ValueError('STOP_V131_REGISTRY_VERSION')
    items=source.get('entries')
    if not isinstance(items,list) or len(items)<10:raise ValueError('STOP_V131_REGISTRY_MUST_HAVE_REAL_CROSS_TAXON_CANDIDATES')
    ids=[x['id'] for x in items]
    if len(ids)!=len(set(ids)):raise ValueError('STOP_V131_DUPLICATED_SOURCE_ID')
    for item in items:
        if item['kind'] not in WELL_KNOWN_KINDS or not item.get('url') or not item.get('independence_group'):
            raise ValueError('STOP_V131_INVALID_SOURCE_TYPE_OR_INDEPENDENCE_ID')
        if item['kind']=='zenodo' and not isinstance(item.get('record_id'),int):
            raise ValueError('STOP_V131_ZENODO_RECORD_NOT_LITERAL_ID')
        if item['candidate_status']=='previous_single_site_field_effect_observed' and item['id']!='O_VLIELAND':
            raise ValueError('STOP_V131_NO_UNSEEN_FIELD_EFFECT_MAY_BE_CALLED_OBSERVED')
    if source.get('meta_effects_admitted_from_this_registry')!=0:
        raise ValueError('STOP_V131_META_NOT_YET_FITTED')
    meta=[x for x in items if x['kind']=='zenodo']
    return {'source_register_seed_n':len(items),
       'zenodo_firstparty_catalog_audit_candidates_n':len(meta),
       'metadata_only_non_zenodo_or_literature_candidates_n':len(items)-len(meta),
       'candidate_functional_groups':dict(Counter(x['functional_group'] for x in items)),
       'candidate_regions_metadata_not_global_biological_replication':dict(Counter(x['region'] for x in items)),
       'raw_effects_currently_admitted_to_global_meta':0,
       'previous_known_source_backed_2018_Vlieland_single_site':1,
       'registry_is_NOT_prisma_complete_and_is_NOT_pooled_global_analysis':True}


def audit_zenodo_record(entry,api_response,metadata_sha):
    expected=int(entry['record_id'])
    if int(api_response.get('id') or -1)!=expected:
        raise ValueError('STOP_V131_WRONG_ZENODO_RECORD_ID_'+entry['id'])
    meta=api_response.get('metadata') or {}
    files=api_response.get('files') or []
    keys=[f.get('key') for f in files]
    if (not isinstance(files,list) or not keys or any(not isinstance(k,str) for k in keys)
         or len(keys)!=len(set(keys))):
        raise ValueError('STOP_V131_DUPLICATED_OR_MISSING_ORIGINAL_FILE_NAMES_'+entry['id'])
    # Check structural fields from real publisher - no unverified raw behavior counts.
    gps=[k for k in keys if k.startswith(entry['expected_gps_prefix']) and (k.endswith('.csv.gz') or k.endswith('.csv'))]
    if not gps:
        raise ValueError('STOP_V131_REAL_ORIGINAL_GPS_FILES_MISSING_'+entry['id'])
    b_prefix=entry.get('expected_behavior_prefix')
    behavior=([k for k in keys if k.startswith(b_prefix) and (k.endswith('.csv.gz') or k.endswith('.csv'))]
            if b_prefix else [])
    if b_prefix and not behavior:
        raise ValueError('STOP_V131_ORIGINAL_CLASSIFIED_BEHAVIOR_FILE_NOT_PRESENT_'+entry['id'])
    raw_acc=[k for k in keys if '-acceleration-' in k and (k.endswith('.csv.gz') or k.endswith('.csv'))]
    allsource=([f for f in files if f.get('key') in gps+behavior+raw_acc])
    bad=[f.get('key') for f in allsource if not str(f.get('checksum','')).startswith('md5:') or
         not isinstance(f.get('size'),int) or f['size']<=0]
    if bad:raise ValueError('STOP_V131_ORIGINAL_CATALOG_MD5_SIZE_INVALID_'+entry['id'])
    if entry['id']=='O_VLIELAND' and not any('2018' in k for k in gps):
        raise ValueError('STOP_V131_VLIELAND_2018_ORIGINAL_GPS_MISSING')
    return {'source_id':entry['id'],
       'publisher':'Zenodo',
       'literal_original_publisher_record_id':expected,
       'provider_original_metadata_SHA256':metadata_sha,
       'provider_original_title':str(meta.get('title') or '')[:220],
       'native_catalog_original_GPS_yearfiles':len(gps),
       'native_catalog_original_acc_raw_yearfiles':len(raw_acc),
       'native_catalog_original_behavior_class_yearfiles':len(behavior),
       'source_original_MD5_and_positive_size_verified_for_selected_file_headers':True,
       'original_GPS_file_name_examples':gps[:3],
       'original_classification_file_name_examples':behavior[:3],
       'original_classification_not_guarantee_comparable_behavior_across_taxa':True,
       'source_catalog_only_no_raw_rows_or_biological_effect':True,
       'status':'TRUE_ORIGINAL_ZENODO_SOURCE_METADATA_ADMITTED'}


def harvest_europepmc_query(group,query,response):
    raw=response.get('resultList',{}).get('result') or []
    out=[]
    for r in raw:
        year=int(r.get('pubYear') or 0)
        if not 1950<=year<=SEARCH_CUTOFF:continue
        title=str(r.get('title') or '').strip()
        if not title:continue
        doi=norm_doi(r.get('doi'))
        key='doi:'+doi if doi else 'title:'+normalize_title(title)
        if key.endswith(':'):continue
        out.append({'dedup_key':key,'doi':doi or None,'title':title[:320],
            'year':year,'journal':str(r.get('journalTitle') or '')[:160],
            'publication_pmid':str(r.get('pmid') or ''),
            'found_by_metadata_query':group,
            'metadata_only_no_fulltext_eligibility_or_effect':True})
    return out


def dedup_literature_queries(results):
    bykey={}
    seen=defaultdict(set)
    for group,rows in results.items():
        for r in rows:
            k=r['dedup_key']
            if k not in bykey:bykey[k]=dict(r)
            seen[k].add(group)
    return [dict(bykey[k],query_groups=sorted(seen[k])) for k in sorted(bykey)]


def run(output,no_literature=False):
    source=json.loads(SOURCE_FILE.read_text())
    report={'analysis':'V131_GLOBAL_TIDAL_SOLAR_TEMPORAL_NICHE_RAW_SOURCE_AND_METADATA_DISCOVERY',
      'review_status':'SEED_REGISTRY_METADATA_ONLY',
      'global_biological_meta_effect':'NOT_ESTIMATED_NO_CROSS_TAXON_INDEPENDENT_EFFECT_LEDGER_YET',
      'source_register_preoutcome_gate':validate_registry(source),
      'search_cutoff_2026_11_14':True,
      'source_catalogs':[],
      'source_failures':[],
      'literature_search_metadata_candidates_only':{},
      'DO_NOT_claim_meta_analysis_pooled_positive':True}
    for entry in source['entries']:
        if entry['kind']!='zenodo':continue
        url=f'https://zenodo.org/api/records/{entry["record_id"]}'
        try:
            data,sh=fetch_json(url)
            v=audit_zenodo_record(entry,data,sh)
            report['source_catalogs'].append(v)
            print('V131_TRUE_ZENODO_SOURCE_METADATA '+json.dumps({
                'id':v['source_id'],'status':v['status'],
                'gps_yearfiles':v['native_catalog_original_GPS_yearfiles'],
                'behavior_yearfiles':v['native_catalog_original_behavior_class_yearfiles']},sort_keys=True),flush=True)
        except (RuntimeError,ValueError,TypeError,KeyError) as e:
            report['source_failures'].append({'source_id':entry['id'],
                'source_metadata_status':'NOT_ADMITTED',
                'reason':str(e)[:240]})
            print('V131_SOURCE_CATALOG_GATE_FAILURE '+entry['id']+' '+str(e)[:160],flush=True)
    if not no_literature:
        rows={};errors={}
        for group,q in QUERIES.items():
            args=urlencode({'query':q,'format':'json','pageSize':SEARCH_RESULTS_PER_QUERY,'resultType':'core'})
            try:
                data,sh=fetch_json(EUROPE_PMC+'?'+args,max_bytes=3_000_000,timeout=20)
                candidates=harvest_europepmc_query(group,q,data)
                rows[group]=candidates
                print('V131_LITERATURE_METADATA_QUERY '+json.dumps({
                  'group':group,'original_metadata_matches_returned':len(candidates),
                  'publisher_response_sha256':sh,
                  'no_fulltext_screen_or_effect_scored':True},sort_keys=True),flush=True)
            except (RuntimeError,ValueError,TypeError,KeyError) as e:
                errors[group]=str(e)[:200]
        dedup=dedup_literature_queries(rows)
        report['literature_search_metadata_candidates_only']={
           'API':'Europe PMC public webservices rest/search',
           'query_groups':list(QUERIES),
           'query_strings':QUERIES,
           'fixed_max_per_query':SEARCH_RESULTS_PER_QUERY,
           'actual_metadata_hits_by_query':{x:len(rows.get(x,[])) for x in QUERIES},
           'source_queries_with_errors':errors,
           'deduplicated_bibliographic_discovery_candidates_n':len(dedup),
           'metadata_only_candidate_citations':dedup,
           'PRISMA_fulltext_screened_n':0,
           'PRISMA_included_effect_count':0,
           'NOT_an_exhaustive_systematic_literature_search':True}
    report['source_metadata_zenodo_admitted_n']=len(report['source_catalogs'])
    report['source_metadata_zenodo_failed_n']=len(report['source_failures'])
    report['scientific_status']='GLOBAL_META_NOT_ESTIMATED_PILOT_SOURCE_REGISTRY_ONLY'
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V131_GLOBAL_META_HONEST_SOURCE_CENSUS '+json.dumps({
      'scientific_status':report['scientific_status'],
      'seed_n':report['source_register_preoutcome_gate']['source_register_seed_n'],
      'zenodo_catalog_admitted':report['source_metadata_zenodo_admitted_n'],
      'zenodo_failed':report['source_metadata_zenodo_failed_n'],
      'literature_metadata_unique':(report['literature_search_metadata_candidates_only'].get(
        'deduplicated_bibliographic_discovery_candidates_n')),
      'fulltext_eligible_meta_effects':0},sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--no-literature',action='store_true')
    args=p.parse_args()
    run(args.output,args.no_literature)
