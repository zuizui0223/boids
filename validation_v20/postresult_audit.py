#!/usr/bin/env python3
"""v20-C explicitly POST-OUTCOME all-season credibility of frozen v20-B result.

This is a sensitivity/diagnostic after primary values were opened. No model,
tuning parameter, target support, historic source, or source inclusion is
modified. We re-run the SAME v20-B predictions solely to report every source
season's effect, exact sign probability, group leave-one-out and temporal
dependence cautions. No original ecological response rows/GPS exported.
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import tempfile
from pathlib import Path
import numpy as np

import group_season_forecast as frozen
import source_gate as src

ORIGINAL_FROZEN_MAIN_GAIN=0.0026482957582551667
EXPECTED_GROUPS=15
EXPECTED_TARGET_ROWS=24
SIGNED_ONE_SIDED_NULL=0.5


def group_equal_gain(records:list[dict])->tuple[float,int,int]:
    by=collections.defaultdict(list)
    for row in records:by[row["group"]].append(
        row["error_M0"]-row["error_M2"])
    if not by:
        return float("nan"),0,0
    g=[float(np.mean(v)) for v in by.values()]
    return float(np.mean(g)),len(g),len(records)


def audit(records:list[dict],primary_gain:float)->dict:
    if not (math.isfinite(primary_gain) and len(records)==EXPECTED_TARGET_ROWS):
        raise ValueError("Frozen original target support changed")
    by=collections.defaultdict(list)
    for row in records:by[row["group"]].append(row)
    if len(by)!=EXPECTED_GROUPS:
        raise ValueError("Frozen independent group denominator changed")
    group_gains={g:float(np.mean([r["error_M0"]-r["error_M2"] for r in rr]))
                 for g,rr in by.items()}
    equal=float(np.mean(list(group_gains.values())))
    if not math.isclose(equal,primary_gain,rel_tol=0,abs_tol=1e-13):
        raise ValueError("Original v20-B primary calculation not reproduced")
    if not math.isclose(equal,ORIGINAL_FROZEN_MAIN_GAIN,rel_tol=0,abs_tol=1e-13):
        raise ValueError("Frozen endpoint differs from original CI result")
    k=sum(v>0 for v in group_gains.values())
    n=len(group_gains)
    sign_p=sum(math.comb(n,j) for j in range(k,n+1))/2**n
    byseason={}
    season_leaveout={}
    for season in frozen.SEASON_ORDER:
        rows=[r for r in records if r["season"]==season]
        if not rows:
            continue
        mean,gs,targets=group_equal_gain(rows)
        byseason[season]={
            "target_group_season_cells":targets,
            "groups_with_target":gs,
            "equal_group_primary_gain":mean,
            "groups_positive_in_this_season":sum(
              r["error_M0"]>r["error_M2"] for r in rows)}
        other=[r for r in records if r["season"]!=season]
        gain,groups,support=group_equal_gain(other)
        season_leaveout[season]={
            "remaining_groups":groups,
            "remaining_group_season_targets":support,
            "equal_group_primary_gain":gain}
    leave_group={}
    for idx,g in enumerate(sorted(group_gains),1):
        remain=[v for t,v in group_gains.items() if t!=g]
        leave_group[f"cluster_{idx:02d}"]=float(np.mean(remain))
    return {
        "status":"POST_OUTCOME_DESCRIPTIVE_AUDIT_ONLY",
        "source_groups":n,
        "source_future_group_season_targets":len(records),
        "original_source_main_gain_recomputed_exact":equal,
        "positive_group_sign_count":k,
        "exact_one_sided_sign_probability_if_independent_group_signs":sign_p,
        "original_future_season_effects":byseason,
        "leave_one_target_season_out":season_leaveout,
        "leave_one_group_out_primary_mean":leave_group,
        "all_leave_one_group_out_primary_means_positive":
            all(v>0 for v in leave_group.values()),
        "multiple_source_seasons_are_shared_environment_not_independent_climates":True,
        "no_target_or_hyperparameter_refitted":True,
        "source_raw_GPS_or_original_ecological_rows_exported":False,
        "notes":[
          "Group bootstrap v20-B is a descriptive resampling of 15 group identities; groups experience shared environmental seasons.",
          "Season table and leave-one-season-out diagnostics were planned after opening v20-B primary.",
          "Exact group sign probability is not a new preregistered hypothesis significance claim.",
          "No direct climate, resources or individual memory were measured in this authors' derived seasonal table."
        ]
    }


def run()->dict:
    import pyreadr
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/"original.Rdata"
        pin=src.download_pinned(path)
        if pin["sha256"]!=frozen.ORIGINAL_SHA256:
            raise ValueError("Original group seasonal source changed")
        data=frozen.registered_source(pyreadr.read_r(str(path))[frozen.REGISTERED_OBJECT])
        supports=frozen.eligible_targets(data)
        observations=frozen.predictions(frozen.transformed_source(data,"fidelity"),supports)
        result=audit(observations,ORIGINAL_FROZEN_MAIN_GAIN)
    return {
        "study":"v20-C-after-outcome-group-and-season-credibility",
        "original_source_verified":pin,
        "preregistered_v20B_endpoint_value_unchanged":ORIGINAL_FROZEN_MAIN_GAIN,
        "original_v20B_primary_run":"https://github.com/zuizui0223/boids/actions/runs/40628278255",
        "audit_is_post_outcome_not_confirmatory":True,
        "diagnostics":result,
        "no_new_behavioral_mechanism_claim":True,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,
        default=Path("validation_v20/results/postresult_group_season_audit_v20.json"))
    args=parser.parse_args()
    d=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V20_POSTRESULT",json.dumps(d["diagnostics"],sort_keys=True))
    print("V20_NO_SECOND_HYPOTHESIS_FITTED")
if __name__=="__main__":
    main()
