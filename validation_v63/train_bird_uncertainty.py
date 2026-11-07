"""v63: genuine 2011 paired GPS heading concordance under 2010 source-bird uncertainty.

Original matched 2011 next-heading outcomes are NEVER used in source-pair
selection or source-bird bootstrap choices. Same v41 weighted ridge is called
unchanged. Only anonymous aggregates leave this ephemeral execution.
"""
from __future__ import annotations

from collections import defaultdict
import numpy as np

from paired_real_phase_heading import _unit

REPS=1024
TRAIN_SEED=20261107
TEST_SEED_ALL=20261108
TEST_SEED_QUALIFIED=20261109
PRIOR_V62_ALL=0.17641912034715593
PRIOR_V62_QUALIFIED=0.03815442590078731

def _blocks_by_original_2010_bird(source_train, *, strict=True):
    blocks=defaultdict(list)
    for r in source_train:
        if not isinstance(r.get("id"),str) or not r["id"]:
            raise ValueError("SOURCE_STOP_V63_BAD_2010_ID")
        blocks[r["id"]].append(r)
    keys=sorted(blocks)
    out=[blocks[k] for k in keys]
    if strict and (len(out)!=8 or sum(map(len,out))!=1508):
        raise ValueError("SOURCE_STOP_V63_FROZEN_DISJOINT_SOURCE_COUNT_DRIFT")
    if not out or any(not block for block in out):
        raise ValueError("SOURCE_STOP_V63_EMPTY_TRAIN_BIRD_BLOCK")
    return out

def _resample_source_blocks(blocks, picked):
    """Clone a complete sampled bird into a separate ephemeral draw-slot ID.

    v41 uses equal-bird ridge weighting. Sharing an original ID among duplicate
    draws would silently collapse their expected cluster-bootstrap mass.
    """
    if len(picked)!=len(blocks):
        raise ValueError("SOURCE_STOP_V63_EXPECT_ONE_DRAW_PER_SOURCE_BIRD")
    rows=[]
    for slot,j in enumerate(picked):
        if int(j)!=j or not 0<=int(j)<len(blocks):
            raise ValueError("SOURCE_STOP_V63_INVALID_BOOTSTRAP_BIRD_INDEX")
        for old in blocks[int(j)]:
            rows.append({**old,"id":"v63_draw_slot_"+str(slot)})
    if len({r["id"] for r in rows})!=len(blocks):
        raise ValueError("SOURCE_STOP_V63_DUPLICATE_RESAMPLED_SLOT_ID")
    return rows

def _prepare_original_pairs(test,pairs,qualified_pairs):
    if not pairs or not qualified_pairs:
        raise ValueError("SOURCE_STOP_V63_MISSING_PAIRED_OR_QUALIFIED_SOURCE")
    if len(set(pairs))!=len(pairs) or len(set(qualified_pairs))!=len(qualified_pairs):
        raise ValueError("SOURCE_STOP_V63_DUPLICATE_MATCH")
    selected=set(qualified_pairs)
    if not selected.issubset(set(pairs)):
        raise ValueError("SOURCE_STOP_V63_QUALIFIED_SET_NOT_SOURCE_SUBSET")
    # No original field ID/positions/timestamps leave memory. Original observed
    # next direction is opened here only after source pair matching and gates.
    endpoints=[]
    d=[]
    labels=[]
    qualified=[]
    for plus,minus in pairs:
        if (plus==minus or test[plus]["id"]!=test[minus]["id"]
                or test[plus]["phase"]!=1 or test[minus]["phase"]!=-1):
            raise ValueError("SOURCE_STOP_V63_NOT_A_REAL_OBSERVED_TIDE_PAIR")
        endpoints.extend([
            {k:v for k,v in test[plus].items() if k not in ("target_e","target_n")},
            {k:v for k,v in test[minus].items() if k not in ("target_e","target_n")}])
        y=_unit([[test[plus]["target_e"],test[plus]["target_n"]],
                 [test[minus]["target_e"],test[minus]["target_n"]]],"OBSERVED_PAIR")
        d.append(y[0]-y[1])
        labels.append(test[plus]["id"])
        qualified.append((plus,minus) in selected)
    obs=np.asarray(d,dtype=float)
    kval=np.asarray(qualified,dtype=bool)
    if not np.isfinite(obs).all():
        raise ValueError("ESTIMAND_STOP_NONFINITE_ACTUAL_OBSERVED_PAIR")
    bird_names=sorted(set(labels))
    birds=np.asarray([bird_names.index(v) for v in labels],dtype=int)
    qualified_birds=sorted(set(birds[kval]))
    if any(np.any((birds==b)&(~kval)) for b in qualified_birds):
        raise ValueError("SOURCE_STOP_V63_QUALIFIED_BIRD_HAS_EXCLUDED_MATCH")
    return endpoints,obs,birds,kval,bird_names,qualified_birds

def _fitted_original_pair_T(source_train,endpoints,obs,forecast_fn):
    """One unchanged ridge fit, predicting phase + and - at both actual B states."""
    up=[{**r,"phase":1} for r in endpoints]
    down=[{**r,"phase":-1} for r in endpoints]
    predicted=np.asarray(forecast_fn(source_train,up+down,1),dtype=float)
    n=len(endpoints)
    if predicted.shape!=(2*n,2):
        raise ValueError("ESTIMAND_STOP_V63_WRONG_PREDICTED_SHAPE")
    # Hard-stop rather than deleting a source bird/bootstrap whose predictions
    # are inconvenient; it would bias the uncertainty distribution.
    p_up=_unit(predicted[:n],"RISING_BOOTSTRAP")
    p_down=_unit(predicted[n:],"FALLING_BOOTSTRAP")
    diff=p_up-p_down
    phasecontrast=(diff[0::2]+diff[1::2])*.5
    if phasecontrast.shape!=obs.shape:
        raise ValueError("ESTIMAND_STOP_V63_PAIR_CONTRAST_DIMENSIONS")
    if not np.isfinite(phasecontrast).all():
        raise ValueError("ESTIMAND_STOP_V63_NONFINITE_SWITCH")
    # g=0 is a real uninformative model switch and has T=0, never filtered.
    values=np.einsum("ij,ij->i",obs,phasecontrast)*.25
    if (np.abs(values)>1+1e-10).any() or not np.isfinite(values).all():
        raise ValueError("ESTIMAND_STOP_V63_SCORE_OUTSIDE_FROZEN_RANGE")
    return values

def _bird_means(values,birds,selected,group_ids):
    return np.asarray([float(values[(birds==bird)&selected].mean()) for bird in group_ids])

def _distribution(values):
    a=np.asarray(values,dtype=float)
    if a.ndim!=1 or not len(a) or not np.isfinite(a).all():
        raise ValueError("ESTIMAND_STOP_V63_INVALID_REPLICATE_DISTRIBUTION")
    return {"n_refits":int(len(a)),"mean":float(a.mean()),
            "median":float(np.median(a)),
            "percentile_95":np.quantile(a,[.025,.975]).tolist(),
            "fraction_positive":float(np.mean(a>0)),
            "minimum":float(a.min()),"maximum":float(a.max())}

def _summarize_condition(train_only,nested,loto,baseline):
    v={"original_fixed_source_T_replay":float(baseline),
       "train_bird_only_bootstrap":_distribution(train_only),
       "joint_train_and_test_bird_bootstrap":_distribution(nested),
       "leave_one_original_train_bird_out":{
           "count":int(len(loto)),"mean":float(np.mean(loto)),
           "minimum":float(np.min(loto)),"maximum":float(np.max(loto)),
           "positive_leave_one_out_models":int(sum(x>0 for x in loto))}}
    return v

def analyze_training_bird_uncertainty(train,test,pairs,qualified_pairs,forecast_fn,
                                     *,reps=REPS,seed=TRAIN_SEED,strict=True):
    if reps<1:
        raise ValueError("SOURCE_STOP_V63_INVALID_REPETITIONS")
    blocks=_blocks_by_original_2010_bird(train,strict=strict)
    endpoints,obs,birds,mask,original_birds,qualified_birds=_prepare_original_pairs(
        test,pairs,qualified_pairs)
    if strict and (len(pairs)!=211 or len(qualified_pairs)!=204
                   or len(original_birds)!=10 or len(qualified_birds)!=7):
        raise ValueError("SOURCE_STOP_V63_FROZEN_ORIGINAL_MATCH_COUNTS_DRIFT")
    allmask=np.ones(len(pairs),dtype=bool)
    def paired_means(source):
        scores=_fitted_original_pair_T(source,endpoints,obs,forecast_fn)
        allmeans=_bird_means(scores,birds,allmask,list(range(len(original_birds))))
        qmeans=_bird_means(scores,birds,mask,qualified_birds)
        return allmeans,qmeans
    orig_all,orig_q=paired_means(train)
    base_all=float(orig_all.mean())
    base_q=float(orig_q.mean())
    if strict and (abs(base_all-PRIOR_V62_ALL)>1e-9 or
                   abs(base_q-PRIOR_V62_QUALIFIED)>1e-9):
        raise ValueError("SOURCE_STOP_V63_V62_ORIGINAL_FIXED_T_REPLAY_DRIFT")
    rng_train=np.random.default_rng(seed)
    rng_all=np.random.default_rng(TEST_SEED_ALL)
    rng_q=np.random.default_rng(TEST_SEED_QUALIFIED)
    drawn=rng_train.integers(0,len(blocks),size=(reps,len(blocks)))
    test_all=rng_all.integers(0,len(original_birds),
                              size=(reps,len(original_birds)))
    test_q=rng_q.integers(0,len(qualified_birds),
                          size=(reps,len(qualified_birds)))
    all_train=np.zeros(reps)
    all_joint=np.zeros(reps)
    q_train=np.zeros(reps)
    q_joint=np.zeros(reps)
    unique_counts=np.zeros(reps,dtype=int)
    for b in range(reps):
        unique_counts[b]=len(set(map(int,drawn[b])))
        resampled=_resample_source_blocks(blocks,drawn[b])
        s,q=paired_means(resampled)
        all_train[b]=float(s.mean())
        all_joint[b]=float(s[test_all[b]].mean())
        q_train[b]=float(q.mean())
        q_joint[b]=float(q[test_q[b]].mean())
    leave_all=[]
    leave_q=[]
    for omitted in range(len(blocks)):
        source=[r for i,block in enumerate(blocks) if i!=omitted for r in block]
        if len({r["id"] for r in source})!=len(blocks)-1:
            raise ValueError("SOURCE_STOP_V63_LEAVE_ONE_BIRD_WRONG_COUNT")
        s,q=paired_means(source)
        leave_all.append(float(s.mean()))
        leave_q.append(float(q.mean()))
    result={
        "analysis":"V63_SCHIER_REAL_PAIRED_TIDE_TRAIN_BIRD_PARAMETER_UNCERTAINTY",
        "frozen_training_birds":len(blocks),
        "original_training_rows":len(train),
        "original_test_2011_rows":len(test),
        "original_real_opposite_phase_pairs":len(pairs),
        "source_matched_birds":len(original_birds),
        "source_qualified_real_pairs":len(qualified_pairs),
        "source_qualified_birds":len(qualified_birds),
        "source_training_bootstrap_reps":reps,
        "source_training_bootstrap_seed":seed,
        "test_bird_resampling_seeds":[TEST_SEED_ALL,TEST_SEED_QUALIFIED],
        "full_8_bird_source_bootstrap_with_replacement":True,
        "duplicated_original_source_bird_gets_unique_temporary_weight_ID":True,
        "same_v41_per_fit_train_only_standardization_and_ridge_lambda10":True,
        "original_2011_pairs_and_targets_fixed_across_all_fits":True,
        "source_bootstrap_distinct_birds":{"min":int(unique_counts.min()),
             "median":float(np.median(unique_counts)),"max":int(unique_counts.max())},
        "main_all_211_original_real_matched_pairs":_summarize_condition(
             all_train,all_joint,leave_all,base_all),
        "secondary_source_qualified_204_real_pairs":_summarize_condition(
             q_train,q_joint,leave_q,base_q),
        "not_independent_biological_replications_or_tide_causation":True,
        "no_original_source_identifiers_geolocations_times_pairs_headings_or_fits_published":True}
    main=result["main_all_211_original_real_matched_pairs"]["joint_train_and_test_bird_bootstrap"]
    second=result["secondary_source_qualified_204_real_pairs"]["joint_train_and_test_bird_bootstrap"]
    result["v63_primary_status"]=(
        "TRAINING_AND_TEST_BIRD_POSITIVE_EXPLORATORY" if
        base_all>0 and main["percentile_95"][0]>0 else
        "TRAINING_UNCERTAINTY_POSITIVE_NOT_ESTABLISHED")
    result["qualified_secondary_status"]=(
        "SOURCE_QUALIFIED_POSITIVE_UNDER_TRAIN_AND_TEST_BOOTSTRAP" if
        base_q>0 and second["percentile_95"][0]>0 else
        "SOURCE_QUALIFIED_POSITIVE_NOT_ESTABLISHED_WITH_TRAIN_UNCERTAINTY")
    return result
