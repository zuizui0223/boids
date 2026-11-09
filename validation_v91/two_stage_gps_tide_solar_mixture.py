"""v91 original 2010 tidal×daylight model-index rank vs WMR flat-membership.

Source and previously published outcome replay MUST pass before NEW mixture
components may be examined. Source v82/v86 original GPS, NIOZ monthly model
and independently published WMR class3/4 native ecology map; genuine RWS
Schier/Ameland physical tide and real Sun at true timestamp.

EXACT ALGEBRA at each true original bird×month×RWS height 4-cell group:
  D_model_R = D_entry_composition + D_conditional_residual
  D_entry_composition = (mean_R_inside_flat - mean_R_outside_flat) * D_flatP
    where pooled class means across ALL four source condition cells.
If one habitat class absent in the entire group, set both class baselines
to pooled mean; entry=0 and residual=D_model_R by convention, record source
group unsupported for two-class interpretation. No favorable group dropped.

An algebraic identity ≠ identified causal two-stage habitat-choice mechanism.
All original bird-level values remain private, only independent bird-block
bootstrap summary exported. WMR exact corrected-2021 v2 source unverified.
"""
from __future__ import annotations
from collections import Counter,defaultdict
import numpy as np

from wild_2010_modelled_tidal_exposure_rank import _rank
from two_island_common_month_bird_contrast import (
    _private_original_bird_means,_site_bird_boot,
    SOURCE_MONTHS,independent_bird_site_contrast)
from wild_tideflat_binary_fourway import (
    _score_original_site,hard_before_outcome_both_sites,
    ORIGINAL_NATIVE_SOURCE_CELLS)

SEED_NEW=20261109
SEED_OLD=20261108
BOOTS=10000
SITES=("Schier","Ameland")
CELLS=((1,"NIGHT"),(1,"DAY"),(-1,"NIGHT"),(-1,"DAY"))
SIGNS=(1,-1,-1,1)
PRIOR_TRUE_2010={
    "Schier":{
        "D_rank":0.0499790599,
        "D_rank_95":(0.0223792846,0.0831319486),
        "D_binary":-0.0561556674,
        "D_binary_95":(-0.0769971705,-0.0357502024),
        "birds":18,"groups":857},
    "Ameland":{
        "D_rank":0.0052737884296153855,
        "D_rank_95":(-0.0341009670,0.0546901114),
        "D_binary":-0.0203797513,
        "D_binary_95":(-0.0933135849,0.0841504810),
        "birds":10,"groups":381}}
RANK_REPLAY_TOL=1e-10
GROUP_IDENTITY_TOL=1e-12
CATEGORIES=(3,4)

def four_cell_original_identity(cells):
    """Input four { (phase,light): (native_rank_vec,binary_flat_vec) }.

    Synthetic-known-truth tests can pass arbitrary 4-cell data; real source
    caller gets actual R(B) and Y(B) only AFTER prior RWS/bird replay gate.
    """
    if set(cells)!=set(CELLS):
        raise ValueError("ESTIMAND_STOP_V91_NOT_EXACT_TRUE_TIDE_SOLAR_FOUR_CELLS")
    pooled_r=[]
    pooled_y=[]
    means={}
    proportions={}
    for c in CELLS:
        a,b=cells[c]
        r=np.asarray(a,dtype=float)
        y=np.asarray(b,dtype=int)
        if (r.ndim!=1 or y.ndim!=1 or len(r)==0 or
            len(r)!=len(y) or not np.isfinite(r).all() or
            not np.isin(y,[0,1]).all()):
            raise ValueError("ESTIMAND_STOP_V91_INVALID_ORIGINAL_RANK_OR_HABITAT_Y")
        pooled_r.append(r)
        pooled_y.append(y)
        means[c]=float(np.mean(r))
        proportions[c]=float(np.mean(y))
    all_r=np.concatenate(pooled_r)
    all_y=np.concatenate(pooled_y).astype(bool)
    has_both=bool(all_y.any() and (~all_y).any())
    if has_both:
        inside=float(np.mean(all_r[all_y]))
        outside=float(np.mean(all_r[~all_y]))
    else:
        inside=outside=float(np.mean(all_r))
    diff=inside-outside
    d_r=sum(float(sign)*means[key] for sign,key in zip(SIGNS,CELLS))
    d_p=sum(float(sign)*proportions[key] for sign,key in zip(SIGNS,CELLS))
    d_entry=diff*d_p
    d_resid=sum(
        float(sign)*(means[key]-outside-diff*proportions[key])
        for sign,key in zip(SIGNS,CELLS))
    if abs(d_r-(d_entry+d_resid))>GROUP_IDENTITY_TOL:
        raise ValueError("ESTIMAND_STOP_V91_SOURCE_MIXTURE_IDENTITY_NOT_EXACT")
    return {
        "D_rank":float(d_r),"D_flatP":float(d_p),
        "D_entry":float(d_entry),"D_resid":float(d_resid),
        "has_both_original_WMR_habitat_classes":has_both,
        "pooled_original_rank_mid_high_minus_outside":float(diff),
        "max_exact_mixture_identity_residual":float(abs(d_r-d_entry-d_resid))}

def _bird_hierarchy(per_original_bird_month):
    values={}
    for bird,month in sorted(per_original_bird_month.items()):
        averages={}
        for metric in ("D_rank","D_flatP","D_entry","D_resid"):
            month_means=[float(np.mean([group[metric] for group in v]))
                        for _,v in sorted(month.items())]
            if not month_means:
                raise ValueError("ESTIMAND_STOP_V91_BIRD_HAS_NO_MEASURED_MONTHS")
            averages[metric]=float(np.mean(month_means))
        values[bird]=averages
    if not values:
        raise ValueError("ESTIMAND_STOP_V91_NO_SOURCE_BIRD_BLOCKS")
    return {k:np.asarray([v[k] for _,v in sorted(values.items())])
            for k in ("D_rank","D_flatP","D_entry","D_resid")}

def _new_bird_boot(v,seed=SEED_NEW):
    x=np.asarray(v,dtype=float)
    if x.ndim!=1 or len(x)==0 or not np.isfinite(x).all():
        raise ValueError("ESTIMAND_STOP_V91_INVALID_TRUE_BIRD_COMPONENTS")
    rng=np.random.default_rng(seed)
    boot=rng.integers(0,len(x),size=(BOOTS,len(x)))
    q=np.quantile(x[boot].mean(axis=1),[.025,.975])
    return [float(q[0]),float(q[1])]

def original_site_old_outcome_replays(site,four,preflights,class_arr):
    """Crucial stop: original v82 and v86 endpoints exact before NEW mixture."""
    if site not in SITES:
        raise ValueError("SOURCE_STOP_V91_UNKNOWN_SITE")
    expected=PRIOR_TRUE_2010[site]
    if len(four)!=expected["groups"]:
        raise ValueError("SOURCE_STOP_V91_PRIOR_ORIGINAL_FOUR_GROUPS_CHANGED")
    old_rank=_private_original_bird_means(four,preflights)
    old_binary,old_summary=_score_original_site(
        site,four,preflights,class_arr,positive_codes=CATEGORIES)
    observed={
        "D_rank":float(np.mean(old_rank)),
        "D_flatP":float(np.mean(old_binary)),
        "D_rank_95":_site_bird_boot(old_rank,SEED_OLD),
        "D_flatP_95":old_summary[
            "primary_binary_GPS_position_in_intertidal_probability_D"][
              "true_bird_10000_bootstrap95"],
        "original_birds":len(old_rank),
        "source_groups":len(four)}
    if (len(old_rank)!=expected["birds"] or
        len(old_binary)!=expected["birds"] or
        abs(observed["D_rank"]-expected["D_rank"])>RANK_REPLAY_TOL or
        abs(observed["D_flatP"]-expected["D_binary"])>RANK_REPLAY_TOL or
        not np.allclose(
            observed["D_rank_95"],expected["D_rank_95"],
            atol=RANK_REPLAY_TOL,rtol=0) or
        not np.allclose(
            observed["D_flatP_95"],expected["D_binary_95"],
            atol=RANK_REPLAY_TOL,rtol=0)):
        raise ValueError("SOURCE_STOP_V91_PRIOR_ORIGINAL_V82_V86_EFFECT_AND_BIRD_BOOT_NOT_REPRODUCED")
    return observed,old_rank,old_binary

def decompose_real_original_site(site,four,preflights,class_arr,
                                 old_rank,old_binary):
    if site not in SITES or class_arr.shape!=(ORIGINAL_NATIVE_SOURCE_CELLS,):
        raise ValueError("SOURCE_STOP_V91_NOT_PINNED_ORIGINAL_WMR_ECOTOPE_SOURCE")
    # Actual original used-cell NIOZ index accesses ONLY after
    # true source and previously known v82/v86 original outcomes replay.
    cached_rank={}
    all_bird=defaultdict(lambda:defaultdict(list))
    counts=Counter()
    original_class_diffs=[]
    max_error=0.
    for (bird,month,height),phases in four.items():
        cells={}
        for phase,light in CELLS:
            r=[];y=[]
            for m,i in phases[phase][light]:
                if m!=month:
                    raise ValueError("SOURCE_STOP_V91_TRUE_ORIGINAL_GPS_MONTH_MISMATCH")
                k=(m,i)
                p=preflights[m]
                index=int(p["closest"][i])
                if index<0 or index>=ORIGINAL_NATIVE_SOURCE_CELLS:
                    raise ValueError("SOURCE_STOP_V91_NOT_GENUINE_NATIVE_GRID_INDEX")
                if k not in cached_rank:
                    cached_rank[k]=_rank(
                        p["model_expo"],index,p["circles"][i])-.5
                r.append(cached_rank[k])
                y.append(int(class_arr[index] in CATEGORIES))
            cells[(phase,light)]=(r,y)
        group=four_cell_original_identity(cells)
        all_bird[bird][month].append(group)
        counts["both_habitat_classes"]+=int(group[
            "has_both_original_WMR_habitat_classes"])
        counts["only_one_habitat_class"]+=int(not group[
            "has_both_original_WMR_habitat_classes"])
        counts["total_original_fourcell_height_groups"]+=1
        max_error=max(max_error,group["max_exact_mixture_identity_residual"])
        if group["has_both_original_WMR_habitat_classes"]:
            original_class_diffs.append(
                group["pooled_original_rank_mid_high_minus_outside"])
    values=_bird_hierarchy(all_bird)
    if (len(values["D_rank"])!=len(old_rank) or
        len(values["D_flatP"])!=len(old_binary) or
        not np.allclose(values["D_rank"],old_rank,atol=RANK_REPLAY_TOL,rtol=0) or
        not np.allclose(values["D_flatP"],old_binary,atol=RANK_REPLAY_TOL,rtol=0)):
        raise ValueError("ESTIMAND_STOP_V91_EVERY_ORIGINAL_BIRD_REPLAY_RANK_AND_BINARY_NOT_EXACT")
    if not np.allclose(values["D_rank"],
                       values["D_entry"]+values["D_resid"],
                       atol=GROUP_IDENTITY_TOL,rtol=0):
        raise ValueError("ESTIMAND_STOP_V91_TRUE_BIRD_TWO_CHANNELS_NOT_ADDITIVE")
    result={}
    for part in ("D_rank","D_flatP","D_entry","D_resid"):
        x=values[part]
        q=_new_bird_boot(x)
        v=float(np.mean(x))
        status=("POSITIVE_EXPLORATORY_BIRD_CLUSTER_DIRECTION"
                if v>0 and q[0]>0 else
                "NEGATIVE_EXPLORATORY_BIRD_CLUSTER_DIRECTION"
                if v<0 and q[1]<0 else
                "DIRECTION_NOT_ESTABLISHED_OR_DESCRIPTIVE_ONLY")
        result[part]={
            "source_true_original_individual_birds":len(x),
            "original_bird_equal_component_value":v,
            "10k_original_whole_bird_bootstrap95":q,
            "source_original_birds_positive":int((x>0).sum()),
            "original_frozen_direction_status":status}
    diffs=np.asarray(original_class_diffs,float)
    return values,{
        "source_site":site,
        "original_prior_old_Drank_and_DflatP_exact_bird_replay":True,
        "original_true_source_fourway_habitat_class_support_counts":dict(counts),
        "original_source_rank_mid_high_minus_outside_when_both_classes":{
            "native_fourway_original_groups":len(diffs),
            "median_and_p05_p95":(
                [float(z) for z in np.quantile(diffs,[.05,.5,.95])]
                if len(diffs) else None)},
        "new_two_channel_tide_solar_mixture_components":result,
        "source_max_per_fourcell_algebra_identity_error":float(max_error),
        "original_NIOZ_model_index_monthly_ordinal_only_unit_UNKNOWN":True,
        "composition_is_observational_not_causal_entry_behavior":True,
        "residual_is_mixture_rank_covariation_not_direct_measured_within_forage":True,
        "original_bird_ID_GPS_location_and_per_bird_D_NOT_exported":True}

def _site_independent_bird_component_diff(a,b,seed=SEED_NEW):
    sa=np.asarray(a,float);sb=np.asarray(b,float)
    if not len(sa) or not len(sb):
        raise ValueError("ESTIMAND_STOP_V91_SITE_BIRD_GROUP_MISSING")
    rng=np.random.default_rng(seed)
    ka=rng.integers(0,len(sa),size=(BOOTS,len(sa)))
    kb=rng.integers(0,len(sb),size=(BOOTS,len(sb)))
    draws=sa[ka].mean(axis=1)-sb[kb].mean(axis=1)
    diff=float(sa.mean()-sb.mean())
    ci=[float(t) for t in np.quantile(draws,[.025,.975])]
    return {
        "Schier_minus_Ameland_bird_conditional_difference":diff,
        "whole_original_bird_separate_site_bootstrap95":ci,
        "direction_status":(
            "POSITIVE_DIFFERENCE_IN_FIXED_TWO_SITES" if diff>0 and ci[0]>0 else
            "NEGATIVE_DIFFERENCE_IN_FIXED_TWO_SITES" if diff<0 and ci[1]<0 else
            "CONDITIONAL_SITE_DIFFERENCE_NOT_ESTABLISHED"),
        "two_sites_fixed_not_global_random_coast_sample":True}

def summarize_original_two_site_mixture(site_values,site_reports):
    if set(site_values)!=set(SITES):
        raise ValueError("SOURCE_STOP_V91_BOTH_ACTUAL_SITE_BIRDS_REQUIRED")
    for site in SITES:
        if site_reports[site]["source_max_per_fourcell_algebra_identity_error"]>GROUP_IDENTITY_TOL:
            raise ValueError("ESTIMAND_STOP_V91_ALGEBRA_IDENTITY_FAIL")
    comparisons={}
    for k in ("D_entry","D_resid"):
        comparisons[k]=_site_independent_bird_component_diff(
            site_values["Schier"][k],site_values["Ameland"][k])
    sch=site_reports["Schier"]["new_two_channel_tide_solar_mixture_components"]
    hypothesis=(sch["D_entry"]["original_frozen_direction_status"].startswith("NEGATIVE")
                and sch["D_resid"]["original_frozen_direction_status"].startswith("POSITIVE"))
    return {
        "two_sites_wild_2010_observational_two_stage_rank_mixture":site_reports,
        "between_two_fixed_sites_genuine_independent_original_bird_comparison":comparisons,
        "post_v86_exploratory_falsifiable_Schier_entry_negative_residual_positive_supported":bool(hypothesis),
        "exact_identity_is_general_math_not_proof_of_biological_adaptive_mechanism":True,
        "WMR_actual_corrected_2021_v2_version_NOT_VERIFIED":True,
        "no_true_foraging_or_original_individual_identifier_exported":True}
