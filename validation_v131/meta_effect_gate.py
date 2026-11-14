"""v131 conservative, source-aware meta-effect gate.

The real effect ledger is EMPTY until actual full-text source extraction and
independent coast/taxon effect SE are verified. Synthetic unit tests exercise
the estimator but are not empirical ecological meta-effects.
"""
from __future__ import annotations
from collections import Counter
from math import sqrt,isfinite
from pathlib import Path
import json,argparse
METRICS=('hedges_g','fisher_z_partial_r','cv_relative_skill')
ENDPOINTS=('classified_behavior','movement','field_density','acoustic_detection')
LEDGER_VERSION='v131-effect-ledger-1'

class EffectGateStop(ValueError):pass


def validate_effect_entry(e):
    required=('effect_id','study_id','source_url','independent_coast_cluster',
      'taxon','functional_group','ocean_region','endpoint_family','metric',
      'effect','sampling_se','original_effect_source_verified','effect_estimate_status')
    missing=[k for k in required if k not in e or e[k] in (None,'')]
    if missing:raise EffectGateStop('STOP_V131_EFFECT_SOURCE_MISSING_'+','.join(missing))
    if e['metric'] not in METRICS or e['endpoint_family'] not in ENDPOINTS:
        raise EffectGateStop('STOP_V131_EFFECT_METRIC_OR_ENDPOINT_NOT_COMPARABLE')
    if (e['effect_estimate_status']!='SOURCE_EXTRACTED' or
        e['original_effect_source_verified'] is not True):
        raise EffectGateStop('STOP_V131_EFFECT_NOT_VERIFIED_IN_ORIGINAL_SOURCE')
    for key in ('effect','sampling_se'):
        if isinstance(e[key],bool) or not isinstance(e[key],(int,float)) or not isfinite(e[key]):
            raise EffectGateStop('STOP_V131_NONFINITE_OR_NONNUMERIC_EFFECT_OR_SE')
    if e['sampling_se']<=0:
        raise EffectGateStop('STOP_V131_EFFECT_MUST_HAVE_POSITIVE_SAMPLING_SE')
    if e['metric']=='cv_relative_skill' and not(-1<=e['effect']<=1):
        # Negative large relative scores possible, but disallow out-of-range
        # until loss normalizer convention is explicitly agreed.
        raise EffectGateStop('STOP_V131_RELATIVE_SKILL_NOT_IN_FIXED_RANGE')
    return True


def eligibility_for_one_endpoint(entries,strict_three_oceans=False):
    if not entries:return {'admitted':False,'status':'NOT_ESTIMATED_EMPTY_EFFECT_LEDGER','k':0}
    try:
        for e in entries:validate_effect_entry(e)
    except EffectGateStop as ex:
        return {'admitted':False,'status':str(ex),'k':len(entries)}
    metric={e['metric'] for e in entries}
    family={e['endpoint_family'] for e in entries}
    if len(metric)!=1 or len(family)!=1:
        return {'admitted':False,'status':'NOT_ESTIMATED_MIXED_NONCOMPARABLE_ENDPOINTS','k':len(entries)}
    studies={e['study_id'] for e in entries}
    sites=[e['independent_coast_cluster'] for e in entries]
    site_unique=len(set(sites))
    if len(sites)!=site_unique:
        return {'admitted':False,'status':'NOT_ESTIMATED_DUPLICATED_COAST_OR_STUDY_EFFECT_WITHOUT_COVARIANCE','k':len(entries),
            'unique_sites':site_unique}
    groups={e['functional_group'] for e in entries}
    taxa={e['taxon'] for e in entries}
    basins={e['ocean_region'] for e in entries}
    checks={
      'geographically_independent_coasts_ge3':site_unique>=3,
      'different_taxa_ge3':len(taxa)>=3,
      'functional_groups_ge2':len(groups)>=2,
      'independent_study_sources_ge3':len(studies)>=3}
    if strict_three_oceans:checks['ocean_regions_ge3']=len(basins)>=3
    return {'admitted':all(checks.values()),
       'status':'CROSS_SOURCE_DESCRIPTIVE_SYNTHESIS_ELIGIBLE' if all(checks.values())
          else 'NOT_ESTIMATED_INDEPENDENT_STUDY_TAXON_OR_COAST_GATE',
       'k':len(entries),'unique_coasts':site_unique,'unique_taxa':len(taxa),
       'unique_groups':len(groups),'unique_ocean_regions':len(basins),'gates':checks,
       'endpoint_family':next(iter(family)),'metric':next(iter(metric))}


def exploratory_dl_pool(entries,strict_three_oceans=False):
    """Only an EXPLORATORY DerSimonian–Laird within a single comparable endpoint.
    A publishable synthesis requires multilevel study phylogeny/covariance and
    appropriate small-study adjusted intervals. This function NEVER imputes SE.
    """
    gate=eligibility_for_one_endpoint(entries,strict_three_oceans)
    if not gate['admitted']:
        return {'scientific_status':gate['status'],'gate':gate,'pooled_effect':None}
    effects=[float(e['effect']) for e in entries]
    variances=[float(e['sampling_se'])**2 for e in entries]
    w=[1/v for v in variances]
    mu=sum(a*b for a,b in zip(w,effects))/sum(w)
    Q=sum(a*(b-mu)**2 for a,b in zip(w,effects))
    denom=sum(w)-sum(a*a for a in w)/sum(w)
    if denom<=0:raise EffectGateStop('STOP_V131_HETEROGENEITY_DENOM_INVALID')
    tau2=max(0.,(Q-(len(w)-1))/denom)
    wr=[1/(v+tau2) for v in variances]
    pooled=sum(a*b for a,b in zip(wr,effects))/sum(wr)
    se=sqrt(1/sum(wr))
    return {'scientific_status':'EXPLORATORY_SAME_ENDPOINT_META_HETEROGENEITY_NOT_FINAL',
      'gate':gate,
      'pooled_effect':pooled,'approx_se':se,'approx_CI95_normal_not_final':[pooled-1.96*se,pooled+1.96*se],
      'tau2_DL':tau2,'Q':Q,
      'NOT_full_multilevel_phylogenetic_or_site_dependence_model':True,
      'NOT_a_final_globally_generalizable_claim':True}


def run(ledger_path,output):
    x=json.loads(Path(ledger_path).read_text())
    if x.get('version')!=LEDGER_VERSION or not isinstance(x.get('effects'),list):
        raise EffectGateStop('STOP_V131_NOT_VERSIONED_PRIMARY_EFFECT_LEDGER')
    groups={}
    for e in x['effects']:
        k=(e.get('endpoint_family'),e.get('metric'))
        groups.setdefault(k,[]).append(e)
    outputs={}
    for k,vals in groups.items():
        outputs[str(k)]=exploratory_dl_pool(vals)
    result={'analysis':'V131_INDEPENDENT_SITE_CROSS_TAXON_META_EFFECT_GATE',
       'effect_ledger_current_total_original_field_effects':len(x['effects']),
       'scientific_status':'NOT_ESTIMATED_NO_SOURCE_VERIFIED_INDEPENDENT_META_EFFECTS' if not x['effects'] else 'SOURCE_EFFECTS_SUBGROUP_EVALUATED',
       'source_eligible_endpoint_analyses':outputs,
       'one_Vlieland_2018_pilot_already_observed_but_NOT_global_meta_effect':True,
       'NO_FAKE_META_POSITIVE_OR_SAMPLE_REPLICATION':True}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('V131_HONEST_INDEPENDENT_META_EFFECT_GATE '+json.dumps({
        'status':result['scientific_status'],
        'real_fulltext_or_raw_compatible_meta_effects':len(x['effects']),
        'coast_taxon_pooled_effect':None if not outputs else 'see individual endpoint gate'},sort_keys=True),flush=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--ledger',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args();run(a.ledger,a.output)
