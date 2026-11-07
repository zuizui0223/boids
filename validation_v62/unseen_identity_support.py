"""v62 frozen original identity-disjoint Schier observed paired-tide robustness.

Source pair choice and 2010 training-id removal are based only on identities and
time, never on observed 2011 heading. Other field predictor and scoring code
are literally imported, unchanged, from v60/v61.
"""
from __future__ import annotations
from collections import Counter

REQUIRED_FULL_TRAIN=7911
REQUIRED_FULL_TRAIN_BIRDS=21
REQUIRED_TEST=4948
REQUIRED_TEST_BIRDS=13
REQUIRED_DISJOINT_TRAIN=1508
REQUIRED_DISJOINT_BIRDS=8
REQUIRED_MATCHES=211
REQUIRED_MATCHED_BIRDS=10
REQUIRED_QUALIFIED_BIRDS=7
MIN_QUALIFY_PAIRS=10
PRIOR_V61_T=0.22867885497020074

def disjoint_2010_training(full_train,test,*,strict=True):
    train_ids={r["id"] for r in full_train}
    test_ids={r["id"] for r in test}
    remaining=[r for r in full_train if r["id"] not in test_ids]
    kept_ids={r["id"] for r in remaining}
    receipt={
        "original_2010_training_rows":len(full_train),
        "original_2010_training_birds":len(train_ids),
        "original_2011_test_rows":len(test),
        "original_2011_test_birds":len(test_ids),
        "training_rows_removed_for_2011_overlap":len(full_train)-len(remaining),
        "literal_2010_train_ids_seen_in_2011":len(train_ids & test_ids),
        "disjoint_training_rows":len(remaining),
        "disjoint_training_birds":len(kept_ids),
        "literal_train_test_identity_overlap":len(kept_ids & test_ids),
        "excluded_identities_removed_before_model_fit":True}
    if kept_ids & test_ids:
        raise ValueError("SOURCE_STOP_V62_TEST_ID_IN_TRAIN_AFTER_EXCLUSION")
    if strict and ((len(full_train),len(train_ids),len(test),len(test_ids),
                   len(remaining),len(kept_ids))!=
                   (REQUIRED_FULL_TRAIN,REQUIRED_FULL_TRAIN_BIRDS,
                    REQUIRED_TEST,REQUIRED_TEST_BIRDS,
                    REQUIRED_DISJOINT_TRAIN,REQUIRED_DISJOINT_BIRDS)):
        raise ValueError("SOURCE_STOP_V62_FROZEN_UNSEEN_TRAIN_COUNT_DRIFT")
    return remaining,receipt

def source_qualified_pair_subset(test,pairs,*,strict=True):
    if not pairs:raise ValueError("SOURCE_STOP_V62_MISSING_ORIGINAL_PAIRED_SOURCE")
    bybird=Counter(test[i]["id"] for i,j in pairs)
    qualified={b for b,n in bybird.items() if n>=MIN_QUALIFY_PAIRS}
    sub=[(i,j) for i,j in pairs if test[i]["id"] in qualified]
    if strict and (len(pairs)!=REQUIRED_MATCHES or len(bybird)!=REQUIRED_MATCHED_BIRDS
                   or len(qualified)!=REQUIRED_QUALIFIED_BIRDS):
        raise ValueError("SOURCE_STOP_V62_FROZEN_PAIR_SUPPORT_DRIFT")
    if any(test[i]["id"]!=test[j]["id"] for i,j in sub):
        raise ValueError("SOURCE_STOP_V62_MISIDENTIFIED_PAIRS")
    return sub,{
        "source_original_all_disjoint_rising_falling_pairs":len(pairs),
        "source_original_all_matched_birds":len(bybird),
        "source_qualified_min_pairs_per_bird":MIN_QUALIFY_PAIRS,
        "source_qualified_birds":len(qualified),
        "source_qualified_pairs":len(sub),
        "qualified_by_source_counts_only_never_heading":True,
        "no_original_bird_ids_persisted":True}

def exact_prior_v61_replay(metric):
    if abs(float(metric)-PRIOR_V61_T)>1e-9:
        raise ValueError("SOURCE_STOP_V62_OLD_V61_OBSERVED_T_REPLAY_DRIFT")
    return True
