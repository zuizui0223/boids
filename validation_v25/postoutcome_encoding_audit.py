#!/usr/bin/env python3
"""v25-D2 post-outcome encoding/tautology audit, not another model fit.

No trainable coefficient or new animal/niche inference. Original TRUE is a
used habitat profile, FALSE aggregated 100 random movement outcomes. If TRUE
is one-hot while FALSE is averaged, large/sparse category rule can classify
their source representation without identifying biological preference.
"""
from __future__ import annotations
import argparse
import collections
import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

import usgs_step_manifest_gate as usgs
import usgs_step_schema_gate as source

CSV_FILE="Data Release P9ELSUHN.csv"
ORIGINAL_SHA256="1a5c2342f9df4c70f170741c14b92b5146f0558f29fd593307768a228b82ca15"
HABITAT=("Corn","Field","Other","Protected","Rice","Urban","Wetland")
SOURCE_ROWS=380578
SOURCE_PAIRS=190289
SOURCE_BIRDYEARS=493
COLUMNS=("birdyear","timestamp","species","case","season","photoperiod",*HABITAT)
SCORES=("max_pct","fewer_nonzero","lower_entropy")

def summarize_case(a:np.ndarray)->dict:
    sums=a.sum(axis=1)
    nonzero=np.count_nonzero(a,axis=1)
    maxima=a.max(axis=1)
    onehot=(nonzero==1)&(maxima==100)&(sums==100)
    den=np.where(sums>0,sums,1)
    prob=a/den[:,None]
    with np.errstate(divide="ignore",invalid="ignore"):
        ent=np.where(prob>0,-prob*np.log(prob),0).sum(axis=1)
    ent=ent/np.log(len(HABITAT))
    return {
        "row_count":len(a),
        "n_exact_one_hot_100":int(onehot.sum()),
        "fraction_exact_one_hot_100":float(onehot.mean()),
        "n_source_percentage_sums_exactly_100":int((sums==100).sum()),
        "n_source_percentage_sums_equal_0":int((sums==0).sum()),
        "number_nonzero_categories_distribution":{
            str(k):int(v) for k,v in sorted(collections.Counter(nonzero).items())
        },
        "maximum_percentage_quantiles_0_25_50_75_100":[float(x) for x in np.quantile(maxima,[0,.25,.5,.75,1])],
        "shannon_entropy_normalized_quantiles_0_25_50_75_100":[float(x) for x in np.quantile(ent,[0,.25,.5,.75,1])],
        "n_max_habitat_pct_equal_100":int((maxima==100).sum()),
        "n_rows_with_at_least_two_positive_habitats":int((nonzero>=2).sum()),
        "_max":maxima,"_nonzero":nonzero,"_entropy":ent
    }

def diagnostic(source_frame:pd.DataFrame)->dict:
    if tuple(source_frame.columns)!=COLUMNS or len(source_frame)!=SOURCE_ROWS:
        raise ValueError("Original source columns or row count changed")
    if not source_frame["case"].isin(("TRUE","FALSE")).all():
        raise ValueError("Original source case labels changed")
    for name in HABITAT:
        if source_frame[name].isna().any():
            raise ValueError("Original habitat missing")
    raw=source_frame[list(HABITAT)].to_numpy(dtype=float)
    if not np.isfinite(raw).all() or np.any(raw<0) or np.any(raw>100):
        raise ValueError("Original raw source percentage changed")
    pairkey=["birdyear","timestamp"]
    true=(source_frame[source_frame["case"]=="TRUE"]
          .set_index(pairkey).sort_index())
    false=(source_frame[source_frame["case"]=="FALSE"]
           .set_index(pairkey).sort_index())
    if not true.index.equals(false.index) or len(true)!=SOURCE_PAIRS:
        raise ValueError("Original paired source structure changed")
    if len(true.index.get_level_values("birdyear").unique())!=SOURCE_BIRDYEARS:
        raise ValueError("Original number of birdyear tokens changed")
    for col in ("species","season","photoperiod"):
        if not (true[col].to_numpy()==false[col].to_numpy()).all():
            raise ValueError("Original matched source class fields conflict")
    a=true[list(HABITAT)].to_numpy(dtype=float)
    b=false[list(HABITAT)].to_numpy(dtype=float)
    u=summarize_case(a)
    v=summarize_case(b)
    vals={
        "max_pct":(u["_max"]-v["_max"]),
        "fewer_nonzero":(v["_nonzero"]-u["_nonzero"]),
        "lower_entropy":(v["_entropy"]-u["_entropy"]),
    }
    ids=true.index.get_level_values("birdyear").to_numpy()
    models={}
    for method,difference in vals.items():
        rank=(difference>1e-10).astype(float)+.5*(np.abs(difference)<=1e-10)
        individual=pd.DataFrame({"bird":ids,"rank":rank})
        per=individual.groupby("bird",sort=True)["rank"].mean()
        models[method]={
            "method_has_no_fitted_parameter":True,
            "original_source_pairs":len(rank),
            "source_pairs_true_wins":int((rank==1).sum()),
            "source_pairs_false_wins":int((rank==0).sum()),
            "source_pairs_tied":int((rank==.5).sum()),
            "overall_paired_classification_rank":float(rank.mean()),
            "equal_birdyear_mean_classification_rank":float(per.mean()),
            "number_birdyear_tokens":len(per),
            "source_birdyear_tokens_with_perfect_rank":int((per==1).sum()),
        }
    def clean(x):
        return {k:val for k,val in x.items() if not k.startswith("_")}
    same=np.isclose(a,b,atol=0,rtol=0).all(axis=1)
    true_onehot=(u["_nonzero"]==1)&(u["_max"]==100)
    false_aggregate=(v["_nonzero"]>=2)&(v["_max"]<100)
    dominant_exact=(u["_max"]==100)&(v["_max"]<100)
    return {
        "study":"v25-D2-source-encoding-postoutcome-trivial-diagnostic",
        "status":"POSTOUTCOME_ORIGINAL_USED_AVAIL_PROFILE_ENCODING_DIAGNOSTIC",
        "source_pairs":len(a),
        "source_birdyear_tokens":len(set(ids)),
        "source_case_TRUE_used_original_profile_summary":clean(u),
        "source_case_FALSE_simulated_available_aggregate_profile_summary":clean(v),
        "n_paired_used_TRUE_equals_available_FALSE_in_all_seven_fields":int(same.sum()),
        "n_TRUE_onehot_100_and_FALSE_multicategory_lt100":int((true_onehot&false_aggregate).sum()),
        "n_used_max100_and_available_max_lt100":int(dominant_exact.sum()),
        "three_no_training_structural_rank_controls":models,
        "original_use_source_rows_are_single_points_but_false_source_rows_are_100_step_aggregates":True,
        "original_100_alternatives_not_in_source_csv":True,
        "source_future_locations_or_behavioral_choice_effect_model_fitted":False,
        "previous_v25D1_original_numbers_changed":False,
        "this_is_post_outcome_not_confirmatory":True,
        "original_animal_ID_exact_timestamp_or_habitat_rows_exported":False,
        "interpretive_caution":"If nonlearned sparsity/max rules are perfect, original v25-D1 100% ranking is structurally explainable and must NOT be claimed ecological perfect prediction."
    }

def run()->dict:
    item=None
    for url in usgs.ENDPOINTS:
        try:
            item=usgs.original_item(usgs.original_json(url))
            break
        except Exception:continue
    if item is None:
        return {"study":"v25D2","status":"NOT_ADMITTED_OFFICIAL_USGS_SOURCE_UNAVAILABLE","any_ecological_effect_fitted":False}
    fs=source.select_files(item)[CSV_FILE]
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/CSV_FILE
        receipt=source.fetch_verified(CSV_FILE,fs,path)
        if receipt["original_independent_sha256"]!=ORIGINAL_SHA256:
            raise ValueError("Previously frozen source checksum drift")
        frame=pd.read_csv(path,dtype={
            "birdyear":"string","timestamp":"string",
            "species":"string","case":"string","season":"string","photoperiod":"string"})
        result=diagnostic(frame)
    result["original_file_receipt"]={
        "sha256":receipt["original_independent_sha256"],
        "provider_md5":receipt["provider_md5"],
        "exact_bytes":receipt["bytes"],
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v25/results/source_encoding_postoutcome_audit_v25D2.json"))
    args=p.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V25D2_ORIGINAL_ENCODING_AUDIT",json.dumps(out,sort_keys=True))
    print("V25D2_NO_NEW_ECOLOGICAL_CHOICE_CLAIM")
if __name__=="__main__":
    main()
