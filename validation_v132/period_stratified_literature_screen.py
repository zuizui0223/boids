"""v132 original Europe PMC metadata: period × functional group, high-sensitivity rule triage.
NOT a completed systematic review, raw biological study, or quantitative meta-analysis.
Retains full original source DOI/title/PMID and short abstract prefix only.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from hashlib import sha256
import argparse,html,json,re,time,unicodedata

API='https://www.ebi.ac.uk/europepmc/webservices/rest/search'
ERAS={'1970_1999':(1970,1999),'2000_2009':(2000,2009),
      '2010_2014':(2010,2014),'2015_2019':(2015,2019),
      '2020_2024':(2020,2024),'2025_2026':(2025,2026)}
TAXON={
'shorebirds':'shorebird OR wader OR oystercatcher OR plover OR red knot OR spoonbill',
'seabirds':'seabird OR gull OR tern OR gannet OR penguin',
'fish':'fish OR teleost OR salmon OR eel OR shark',
'crustaceans':'crab OR amphipod OR crustacean OR horseshoe crab',
'benthic':'mollusc OR bivalve OR mussel OR oyster OR barnacle OR polychaete',
'coastal_other':'insect OR midge OR coastal mammal OR otter OR intertidal reptile'}
MAX_PER_QUERY=40
SLEEP_BETWEEN_QUERIES_S=.3
GROUPS=('possible_field_tide_solar','possible_field_tide_only',
        'possible_clock_lab','possible_review_theory','uncertain_relevance','unrelated')
TIDE=re.compile(r'\b(tid(?:e|es|al)|circatidal|semidiurnal|spring.neap|high.water|low.water)\b',re.I)
SUN=re.compile(r'\b(diel|diurnal|nocturnal|night|daylight|solar|photoperiod|circadian|sunrise|sunset|dawn|dusk)\b',re.I)
BIO=re.compile(r'\b(animals?|shorebirds?|oystercatchers?|waders?|plovers?|knots?|spoonbills?|birds?|gulls?|seabirds?|fishes?|fish|teleosts?|sharks?|eels?|crabs?|amphipods?|crustaceans?|horseshoe.crabs?|molluscs?|mussels?|oysters?|bivalves?|barnacles?|polychaetes?|insects?|midges?|mammals?|otters?|penguins?|gannets?|salmon|snails?)\b',re.I)
BEHAVIOR=re.compile(r'\b(behavio[u]?r|forag(?:e|ing)|feed(?:ing)?|movement|migrat(?:ion|ing)|activity|locomot(?:ion|or)|emergence|spawning|reproduction|rhythms?|periodicity|distribut(?:ion|ed)|habitat use|niche|occupancy|detection|acoustic|telemetry|tracking|swim(?:ming)?)\b',re.I)
FIELD=re.compile(r'\b(field|coast|coastal|intertidal|estuar(?:y|ies)|in situ|tagged|tracking|wild|telemetry|habitat|shoreline|lagoon|mudflat|acoustic monitor|survey|camera trap|observation)\b',re.I)
LAB=re.compile(r'\b(laboratory|experiment|cultured|molecular|gene knock|knockout|transcriptom|endogenous|circadian clock gene|rhythm gene|CRISPR|free.running)\b',re.I)
REVIEW=re.compile(r'\b(review|perspective|theory|conceptual|systematic review|meta.analysis)\b',re.I)
EXCLUDE=re.compile(r'\b(antimicrobial resistance|antibiotic resistance|carbapenem resistant|acute respiratory distress|pacemaker|cancer therapy|prebiotic membrane|insecticid|microplastic uptake|pesticide)\b',re.I)

def get_json(url,opener=urlopen,retry=2):
    last=None
    for k in range(retry):
        try:
            req=Request(url,headers={'User-Agent':'boids-v132-period-stratified-public-metadata-synthesis/1.0','Accept':'application/json'})
            with opener(req,timeout=24) as resp:
                raw=resp.read(4_000_001)
                if len(raw)>4_000_000:raise ValueError('SOURCE_REJECT_EUROPEPMC_OVER_4MB')
            return json.loads(raw),sha256(raw).hexdigest()
        except (HTTPError,URLError,TimeoutError,OSError,ValueError,json.JSONDecodeError) as e:
            last=e
            if k+1<retry:time.sleep(2*(k+1))
    raise RuntimeError('SOURCE_API_UNAVAILABLE_'+str(last)[:160])

def norm_doi(v):
    return re.sub(r'^https?://(?:dx\.)?doi\.org/','',str(v or '').strip().casefold()).removeprefix('doi:').strip()

def norm_title(v):
    return re.sub(r'\W+',' ',unicodedata.normalize('NFKC',html.unescape(re.sub('<[^>]+>',' ',str(v or '')))).casefold()).strip()

def query_string(taxon,era):
    lo,hi=ERAS[era]
    q=f'((tidal OR tide OR circatidal) AND (diel OR diurnal OR nocturnal OR night OR circadian OR solar OR lunar) AND ({TAXON[taxon]})) AND FIRST_PDATE:[{lo}-01-01 TO {hi}-12-31]'
    return q

def sanitize_source_record(r,era,taxon):
    title=html.unescape(re.sub(r'<[^>]+>',' ',str(r.get('title') or ''))).strip()
    doi=norm_doi(r.get('doi'))
    pmid=str(r.get('pmid') or '').strip()
    if not title or not (doi or pmid):return None
    year=int(r.get('pubYear') or 0)
    if year<1970 or year>2026:return None
    key='doi:'+doi if doi else 'pmid:'+pmid
    abstract=html.unescape(re.sub(r'<[^>]+>',' ',str(r.get('abstractText') or ''))).strip()
    return {'id':key,'doi':doi or None,'pmid':pmid or None,
       'title':' '.join(title.split())[:450],'year':year,'journal':str(r.get('journalTitle') or '')[:140],
       'abstract_excerpt':' '.join(abstract.split())[:180],
       '_screen_text':title+' '+abstract,
       'discovery_queries':[era+':'+taxon]}

def triage_title_abstract(title,abstract):
    text=html.unescape(re.sub(r'<[^>]+>',' ',str(title or '')+' '+str(abstract or '')))
    has={'tide':bool(TIDE.search(text)),'solar':bool(SUN.search(text)),
      'animal':bool(BIO.search(text)),'behavior':bool(BEHAVIOR.search(text)),
      'field':bool(FIELD.search(text)),'lab':bool(LAB.search(text)),
      'review':bool(REVIEW.search(text)), 'obvious_non_ecology':bool(EXCLUDE.search(text))}
    # Bad acronym CRAB (carbapenem resistant Acinetobacter) must be excluded.
    if has['obvious_non_ecology'] or not has['animal']:
        stage='unrelated'
    elif has['review'] and not has['field']:
        stage='possible_review_theory'
    elif has['lab'] and not has['field'] and has['tide']:
        stage='possible_clock_lab'
    elif has['tide'] and has['solar'] and has['behavior'] and has['field']:
        stage='possible_field_tide_solar'
    elif has['tide'] and has['behavior'] and has['field']:
        stage='possible_field_tide_only'
    elif has['tide'] and has['lab']:
        stage='possible_clock_lab'
    else:
        stage='uncertain_relevance'
    assert stage in GROUPS
    return stage,has

def merge_with_old(prior,records):
    if prior.get('analysis')!='V131_GLOBAL_TIDAL_SOLAR_TEMPORAL_NICHE_RAW_SOURCE_AND_METADATA_DISCOVERY':
        raise ValueError('STOP_V132_PREVIOUS_V131_ORIGINAL_METADATA_WRONG')
    original=prior['literature_search_metadata_candidates_only']['metadata_only_candidate_citations']
    if len(original)!=197:raise ValueError('STOP_V132_OLD_197_DOI_TITLE_CENSUS_DRIFT')
    seen={}
    for x in original:
        key=('doi:'+x['doi']) if x.get('doi') else ('pmid:'+str(x.get('publication_pmid') or ''))
        if key=='pmid:':key='title:'+norm_title(x['title'])
        seen[key]={'id':key,'doi':x.get('doi'),'pmid':x.get('publication_pmid') or None,
         'title':html.unescape(re.sub(r'<[^>]+>',' ',x['title']))[:450],
         'year':int(x['year']),'journal':x.get('journal',''),
         'abstract_excerpt':'',
         '_screen_text':x['title'],'discovery_queries':['v131_seed_197']}
    source_duplicated=0
    for r in records:
        key=r['id']
        if key not in seen:
            title_key=norm_title(r['title'])
            matches=[k for k,v in seen.items() if norm_title(v['title'])==title_key and v['year']==r['year']]
            if matches:key=matches[0]
        if key in seen:
            source_duplicated+=1
            x=seen[key]
            x['discovery_queries']=sorted(set(x['discovery_queries']+r['discovery_queries']))
            if not x.get('abstract_excerpt') and r.get('abstract_excerpt'):
                x['abstract_excerpt']=r['abstract_excerpt']
                x['_screen_text']=r['_screen_text']
            if not x.get('doi') and r.get('doi'):x['doi']=r['doi']
            if not x.get('pmid') and r.get('pmid'):x['pmid']=r['pmid']
        else: seen[key]=r
    return list(seen.values()),{'v131_seed_count':len(original),
        'v132_new_query_raw_record_rows':len(records),
        'v132_records_matching_existing_or_new_query_entries':source_duplicated,
        'unique_records_after_v131_v132_merge':len(seen),
        'duplicate_same_doi_or_exact_title_year_not_independent_studies':True}

def run(prior_file,output):
    prior=json.loads(Path(prior_file).read_text())
    report={'analysis':'V132_PERIOD_STRATIFIED_GLOBAL_TIDAL_SOLAR_BIOLOGY_LITERATURE_SOURCE_TRIAGE',
     'study_status':'BIBLIOGRAPHIC_METADATA_AND_ABSTRACT_MACHINE_TRIAGE_ONLY',
     'source_quality_note':'No human fulltext eligibility, no global effect, no quantitative meta',
     'fixed_methods':'docs/V132_FROZEN_TIME_STRATIFIED_TIDE_SOLAR_LITERATURE_SCREEN.md',
     'searches':[],'failed_original_metadata_queries':[],
     'PRISMA_fulltext_eligible_k':0,'global_meta_pooled_effect':'NOT_ESTIMATED'}
    found=[]
    for era in ERAS:
      for taxon in TAXON:
        q=query_string(taxon,era)
        query=urlencode({'query':q,'format':'json','resultType':'core','pageSize':str(MAX_PER_QUERY)})
        try:
            data,hash_=get_json(API+'?'+query)
            raw=(data.get('resultList') or {}).get('result') or []
            rec=[x for v in raw if (x:=sanitize_source_record(v,era,taxon)) is not None]
            found.extend(rec)
            count=int(data.get('hitCount') or 0)
            report['searches'].append({'era':era,'taxon_group':taxon,'original_publisher_query':q,
               'publisher_response_SHA256':hash_,'publisher_total_hitcount_not_unique_studies':count,
               'original_rows_returned_max40':len(raw),'valid_source_rows':len(rec),
               'known_source_page_cap_or_truncation':count>len(raw)})
            print('V132_PUBLISHER_TIME_STRATIFIED_QUERY '+json.dumps({'era':era,'taxon':taxon,'total_hits':count,'retrieved':len(rec)},sort_keys=True),flush=True)
        except (RuntimeError,ValueError,TypeError,KeyError) as e:
            report['failed_original_metadata_queries'].append({'era':era,'taxon':taxon,'source_error':str(e)[:220]})
            print('V132_ORIGINAL_QUERY_SOURCE_FAILURE '+era+' '+taxon+': '+str(e)[:140],flush=True)
        time.sleep(SLEEP_BETWEEN_QUERIES_S)
    merged,source=merge_with_old(prior,found)
    counts=Counter();per_era=Counter();selected=[]
    for r in merged:
        stage,has=triage_title_abstract(r['title'],r['_screen_text'])
        r['automated_relevance_priority']=stage
        r['source_screen_evidence_flags']=has
        r['source_abstract_or_title_only']=bool(r['abstract_excerpt'])
        del r['_screen_text']
        counts[stage]+=1
        per_era[next((k for k,(lo,hi) in ERAS.items() if lo<=r['year']<=hi),'unknown')]+=1
        selected.append(r)
    report['source_census']={**source,
      'fixed_periods':ERAS,'fixed_taxonomic_groups':list(TAXON),
      'planned_query_groups':len(ERAS)*len(TAXON),
      'actual_completed_query_groups':len(report['searches']),
      'failed_query_groups':len(report['failed_original_metadata_queries']),
      'all_planned_query_groups_completed':len(report['searches'])==len(ERAS)*len(TAXON),
      'metadata_publications_by_era':dict(per_era),
      'automatic_triage_counts_not_eligible_studies':dict(counts),
      'PRISMA_human_screened_titles':0,'PRISMA_fulltext_screened':0,
      'PRISMA_quantitative_tide_solar_effect_estimates':0,
      'original_behavioral_data_are_NOT_fetched_in_this_metadata_audit':True}
    report['original_published_bibliography_machine_triage']=sorted(selected,key=lambda x:(x['year'],x['title']),reverse=True)
    report['scientific_status']='NOT_ESTIMATED_NO_HUMAN_ELIGIBILITY_OR_META_EFFECTS'
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V132_SOURCE_CENSUS_YEAR_BALANCED_GLOBAL_BIBLIOGRAPHY '+json.dumps(report['source_census'],sort_keys=True),flush=True)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v131-original-source',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.v131_original_source,a.output)
