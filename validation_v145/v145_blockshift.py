"""v145: calendar-day-block circular-shift null for actual California chorusing.

No model of fish individuals or social interaction. Same-acoustic-recorder
pairwise overlap is contrasted with a restricted timing null:

- retain only complete nominally audible 24h *local* calendar days, with
  source-annotated Off effort/Noise hours excluded;
- partition continuous complete days by site, local year and month;
- retain contiguous day runs of >=7 days (fixed, before inspecting results);
- keep A time-series fixed, rotate B's 24-hour daily profile across the
  same 7+-day run by a random whole-number day lag (0 included), separately
  by run. Preserves B bouts for every day & adjacent dates except wrap seam;
  preserves clock hour and month, but not date-specific temperature/tide;
- use *all possible circular day offsets* for analytical null expectation,
  then 1999 deterministic Monte Carlo restricted shifts for null dispersion.

Shift null p values are only model-conditional sampling diagnostics.
Original workbooks have per-file SHA fingerprints from v142. Remaining
time has not been independently calibrated for acoustic detection ability.
Unrecognized fish chorus types and original-published denominator mismatch
remain unresolved; no ecological mechanism or independent coast inference.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from datetime import timedelta
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
from math import sqrt
from pathlib import Path
from random import Random
import json,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v144"))
from full9_temporal import original, local_time, TYPES

MIN_RUN_DAYS=7
MIN_TEST_DAYS=60
MIN_TYPE_POS_HOURS=100
MIN_EXPECTED_BOTH_HOURS=10.0
PERMUTATIONS=1999
SEED_PREFIX="v145_day_shift_fixed_20261115"
PRIMARY_POLICY="exclude_full_source_off_effort_and_noise"

def eligible_complete_days(hours):
    """One unique eligible UTC-hour midpoint for every 0..23 local hour."""
    days=defaultdict(dict)
    ambiguous=set()
    for h in hours:
        dt=local_time(h)
        date=dt.date()
        if dt.hour in days[date]:
            ambiguous.add(date) # local 25h fall DST day not 24 independent hours
        days[date][dt.hour]=h
    return {date:tuple(hrs[h] for h in range(24))
            for date,hrs in days.items()
            if len(hrs)==24 and date not in ambiguous}

def contiguous_runs(day_by_date, min_days=MIN_RUN_DAYS):
    """No run crosses a calendar-year, month, local-day gap, or DST short day."""
    run=[];out=[]
    for date in sorted(day_by_date):
        if run and (date-run[-1]).days!=1:
            if len(run)>=min_days:out.append(tuple(run))
            run=[]
        run.append(date)
    if len(run)>=min_days:out.append(tuple(run))
    # Split at local year-month boundaries if a continuous run spans them.
    split=[]
    for run in out:
        current=[]
        for date in run:
            if current and (date.year,date.month)!=(current[-1].year,current[-1].month):
                if len(current)>=min_days:split.append(tuple(current))
                current=[]
            current.append(date)
        if len(current)>=min_days:split.append(tuple(current))
    return split

def hour_mask(hours, positive):
    return sum(1<<i for i,h in enumerate(hours) if h in positive)

def score_by_all_rotations(a,b):
    """Clock-hour preserving circular offsets of complete local-day bitsets."""
    if len(a)!=len(b) or not a:
        raise ValueError("Nonempty equal-length source-day arrays required")
    return [sum((av & b[(i+lag)%len(a)]).bit_count()
                for i,av in enumerate(a)) for lag in range(len(a))]

def seed_for(site,A,B):
    value=f"{SEED_PREFIX}|{site}|{A}|{B}".encode()
    return int.from_bytes(sha256(value).digest()[:8],"big")

def randomization(observed,all_score_arrays,site,A,B,n=PERMUTATIONS):
    if n<10:raise ValueError("Monte Carlo null requires at least 10 draws")
    expected=sum(sum(v)/len(v) for v in all_score_arrays)
    rng=Random(seed_for(site,A,B))
    sims=[sum(v[rng.randrange(len(v))] for v in all_score_arrays) for _ in range(n)]
    sims.sort()
    tails=sum(abs(z-expected)>=abs(observed-expected)-1e-12 for z in sims)
    upper=sum(z>=observed for z in sims)
    lower=sum(z<=observed for z in sims)
    lo=sims[int(.025*n)]
    hi=sims[int(.975*n)]
    return {
        "observed_simultaneous_chorus_hours":observed,
        "exact_uniform_shift_expectation_hours":round(expected,5),
        "observed_over_shift_expectation":round(observed/expected,6) if expected else None,
        "null_shift_2p5_percentile":lo,
        "null_shift_97p5_percentile":hi,
        "two_sided_monte_carlo_compatibility_p":round((tails+1)/(n+1),6),
        "upper_tail_monte_carlo_compatibility_p":round((upper+1)/(n+1),6),
        "lower_tail_monte_carlo_compatibility_p":round((lower+1)/(n+1),6),
        "n_fixed_permutations":n,
        "p_values_are_exploratory_under_shift_exchangeability_not_biological_interaction_tests":True,
    }

def benjamini_hochberg(result_rows):
    """Multiple comparisons explicit: all screened site×chorus pairs, no cherry-pick."""
    valid=[r for r in result_rows if r["status"]=="SCREENED_RESTRICTED_SHIFT_NULL"]
    valid.sort(key=lambda r:r["shift_null"]["two_sided_monte_carlo_compatibility_p"])
    m=len(valid);prev=1.
    for rank,r in reversed(list(enumerate(valid,1))):
        p=r["shift_null"]["two_sided_monte_carlo_compatibility_p"]
        prev=min(prev,p*m/rank)
        r["shift_null"]["BH_FDR_q_within_all_screened_site_pairs"]=round(prev,6)
    return m

def analyze():
    source=original()
    rows=[]
    qc=[]
    for site,rec in sorted(source.items()):
        nominal=rec["nominal"]
        hours=nominal-rec["off"]-rec["noise"]
        full=eligible_complete_days(hours)
        runs=contiguous_runs(full)
        day_map={d:hour for d,hour in full.items()}
        retained={h for run in runs for d in run for h in day_map[d]}
        retain_by_type={t:rec["fish"][t]&retained for t in TYPES}
        qc.append({
            "site":site,
            "source_nominal_hours_after_off_and_noise":len(hours),
            "complete_local_day_hours":24*len(full),
            "complete_local_days":len(full),
            "continuous_local_yearmonth_run_blocks_7days_plus":len(runs),
            "source_whole_local_days_retained_in_7day_plus_runs":sum(len(run) for run in runs),
            "selected_source_eligible_hours":len(retained),
            "selected_fraction_of_nominal_effort":round(len(retained)/len(hours),6),
            "local_DSL_23h_or_25h_and_noncontinuous_effort_excluded":True,
            "source_event_clock_still_nominal_audibility":True,
        })
        masks={}
        for r_idx,run in enumerate(runs):
            masks[r_idx]={
                t:[hour_mask(day_map[d],retain_by_type[t]) for d in run] for t in TYPES}
        for A,B in combinations(TYPES,2):
            site_a=retain_by_type[A]
            site_b=retain_by_type[B]
            block_scores=[score_by_all_rotations(m[A],m[B]) for m in masks.values()]
            obs=sum(score[0] for score in block_scores)
            expected=sum(sum(v)/len(v) for v in block_scores)
            valid=(len(retained)>=24*MIN_TEST_DAYS and
                   len(site_a)>=MIN_TYPE_POS_HOURS and len(site_b)>=MIN_TYPE_POS_HOURS and
                   expected>=MIN_EXPECTED_BOTH_HOURS and len(block_scores)>=2)
            row={
                "site":site,"chorus_A":A,"chorus_B":B,
                "complete_yearmonth_consecutive_day_runs":len(runs),
                "retained_nominal_source_hours":len(retained),
                "source_chorus_A_positive_hours":len(site_a),
                "source_chorus_B_positive_hours":len(site_b),
                "observed_same_hour_chorusing_in_retained_blocks":obs,
                "exact_shift_null_expected_same_hour_hours":round(expected,5),
                "source_nominal_heldout_of_blocks":len(hours)-len(retained),
                "status":"SCREENED_RESTRICTED_SHIFT_NULL" if valid else "STOP_RARE_OR_INSUFFICIENT_CONTINUOUS_OPPORTUNITY",
                "shift_null":None,
            }
            if valid:row["shift_null"]=randomization(obs,block_scores,site,A,B)
            rows.append(row)
    screened=benjamini_hochberg(rows)
    summary={}
    for A,B in combinations(TYPES,2):
        these=[r for r in rows if r["chorus_A"]==A and r["chorus_B"]==B and r["shift_null"]]
        summary[A+" | "+B]={
            "screened_sites":len(these),
            "observed_greater_than_shift_expected_sites":sum(
                r["observed_same_hour_chorusing_in_retained_blocks"] >
                r["exact_shift_null_expected_same_hour_hours"] for r in these),
            "observed_less_than_shift_expected_sites":sum(
                r["observed_same_hour_chorusing_in_retained_blocks"] <
                r["exact_shift_null_expected_same_hour_hours"] for r in these),
            "site_results":{r["site"]:{
                "O":r["observed_same_hour_chorusing_in_retained_blocks"],
                "E":r["exact_shift_null_expected_same_hour_hours"],
                "O_over_E":r["shift_null"]["observed_over_shift_expectation"],
                "p_shift_null":r["shift_null"]["two_sided_monte_carlo_compatibility_p"],
                "BH_q_shift_null":r["shift_null"]["BH_FDR_q_within_all_screened_site_pairs"],
            } for r in these}
        }
    out={
        "version":"v145_restricted_contiguous_day_shift_null_original_california_1",
        "source_Dryad_DOI":"10.5061/dryad.q2bvq83sw",
        "original_article_DOI":"10.3354/meps14910",
        "source_original_workbook_SHA_verified_all_60":True,
        "sites":9,"original_deployments":60,
        "source_original_years":"2018-2023",
        "null_definition":"Within same site/local year-month/contiguous 7+ fully recorded local days, shift whole 24h binary fish chorus daily masks by an integer number of days for fish B, independently by block; exact shift expectation plus Monte Carlo rotations.",
        "preserved":"within-day and most across-day bout autocorrelation of shifted fish B; local clock & local year-month distribution; actual source opportunity in complete days",
        "not_preserved":"wraparound seams, original daily shared weather, unlogged detection audibility, selection of incomplete days",
        "source_min_run_days":MIN_RUN_DAYS,
        "min_site_test_days":MIN_TEST_DAYS,
        "min_positive_source_hours_for_each_chorus":MIN_TYPE_POS_HOURS,
        "min_analytical_expected_overlap_hours":MIN_EXPECTED_BOTH_HOURS,
        "permutations":PERMUTATIONS,
        "fixed_seed_prefix":SEED_PREFIX,
        "source_site_block_qc":qc,
        "per_site_type_pair":rows,
        "screened_site_pairs":screened,
        "pair_summary":summary,
        "global_tide_solar_effect":"NOT_ESTIMATED",
        "fish_behavioral_interaction":"NOT_IDENTIFIED_FROM_ACOUSTIC_COINCIDENCE",
        "independent_coastal_studies_n":1,
        "boids_individual_motion_parameters":"NOT_ESTIMATED",
    }
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    res=analyze()
    path=Path(__file__).parent/"results"/"source_blockshift_cochorus_null.json"
    path.parent.mkdir(exist_ok=True,parents=True)
    if args.check:
        if res!=json.loads(path.read_text()):
            raise AssertionError("Frozen v145 source/day-shift null output changed")
    else:
        path.write_text(json.dumps(res,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print("V145_CONDITIONAL_SHIFT_START")
    print(json.dumps(res,ensure_ascii=False))
    print("V145_CONDITIONAL_SHIFT_END")

if __name__=="__main__":main()
