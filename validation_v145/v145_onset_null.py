"""v145 source-real transition timing under month-specific daily circular shifts.

Transitions are first manually chorus-positive hourly bins after a nonpositive
hour, not exact acoustic event onsets or fish individual behavior. Whole daily
profiles shift within source site × yearmonth continuous full-day runs; date-
specific shared noise, temperature, tide, moon and instrument audibility
remain potential unmeasured shared causes. No source raw audio redistributed.
"""
from __future__ import annotations
import argparse,json,sys
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
from v145_blockshift import (
    original,eligible_complete_days,contiguous_runs,hour_mask,
    MIN_TEST_DAYS,PERMUTATIONS,
    randomization,benjamini_hochberg,TYPES
)

MIN_SOURCE_ONSETS=20
MIN_EXPECTED_ONSET_OVERLAP=3
WINDOWS=(0,1)
DAY_BITS=(1<<24)-1

def onset_day_masks(presence):
    """24h binary sequence, cross-day transition accounted for inside block."""
    if not presence:raise ValueError("Empty day sequence")
    stream=sum(v<<(24*i) for i,v in enumerate(presence))
    # Prevent false onset at first hour of the run (prior hour unknown).
    onset=(stream & ~(stream<<1)) & ~1
    return [(onset>>(24*i))&DAY_BITS for i in range(len(presence))]

def tolerant_rotated_scores(a,b,tolerance):
    if len(a)!=len(b) or not a or tolerance<0 or tolerance>3:
        raise ValueError("Equal day sequences and 0-3 hour tolerance required")
    n=len(a)
    A=sum(v<<(24*i) for i,v in enumerate(a))
    m=(1<<(24*n))-1
    ans=[]
    for offset in range(n):
        B=sum(b[(i+offset)%n]<<(24*i) for i in range(n))
        extended=B
        for dt in range(1,tolerance+1):
            extended |= (B<<dt)|(B>>dt)
        ans.append((A & (extended&m)).bit_count())
    return ans

def analyze():
    sources=original()
    qc=[];out=[]
    for site,item in sorted(sources.items()):
        eligible=item["nominal"]-item["off"]-item["noise"]
        calendar_days=eligible_complete_days(eligible)
        runs=contiguous_runs(calendar_days)
        selected_hours=24*sum(len(run) for run in runs)
        matrices=[]
        for run in runs:
            days=[calendar_days[d] for d in run]
            by_type={}
            for typ in TYPES:
                pres=[hour_mask(day,item["fish"][typ]) for day in days]
                by_type[typ]=onset_day_masks(pres)
            matrices.append(by_type)
        nstarts={t:sum(v.bit_count() for matrices_row in matrices
                       for v in matrices_row[t]) for t in TYPES}
        qc.append({"site":site,"fully_retained_source_hours":selected_hours,
                   "nominal_effort_after_explicit_masks":len(eligible),
                   "fraction_retained":round(selected_hours/len(eligible),6),
                   "contiguous_month_7day_blocks":len(runs),
                   "source_first_positive_hour_after_negative_by_type":nstarts})
        for a,b in combinations(TYPES,2):
            for w in WINDOWS:
                scores=[tolerant_rotated_scores(m[a],m[b],w) for m in matrices]
                obs=sum(sc[0] for sc in scores)
                exact=sum(sum(sc)/len(sc) for sc in scores)
                ok=(selected_hours>=24*MIN_TEST_DAYS
                    and nstarts[a]>=MIN_SOURCE_ONSETS and nstarts[b]>=MIN_SOURCE_ONSETS
                    and exact>=MIN_EXPECTED_ONSET_OVERLAP and len(scores)>=2)
                result={
                  "site":site,"chorus_A":a,"chorus_B":b,"tolerance_hours":w,
                  "A_transition_hours":nstarts[a],"B_transition_hours":nstarts[b],
                  "source_hours_in_complete_runs":selected_hours,
                  "observed_A_transition_near_B_transition":obs,
                  "exact_source_conditional_expected":round(exact,5),
                  "status":"SCREENED_RESTRICTED_SHIFT_NULL" if ok else "STOP_ONSET_UNDERPOWERED_OR_SOURCE_SUPPORT",
                  "shift_null":None}
                if ok:
                    result["shift_null"]=randomization(
                        obs,scores,site,a+" onset_tol"+str(w),b,n=PERMUTATIONS)
                out.append(result)
    screens={}
    for w in WINDOWS:
        screens[str(w)]=benjamini_hochberg([r for r in out if r["tolerance_hours"]==w])
    return {
        "version":"v145_original_chorus_transition_source_shift_1",
        "source_Dryad_DOI":"10.5061/dryad.q2bvq83sw",
        "primary_original_paper_DOI":"10.3354/meps14910",
        "source_SHA256_verified_workbooks":60,"n_source_sites":9,
        "source_n_deployments":60,
        "transition_definition":"First positive HOUR after a negative hour; first source run hour excluded from onset and every time series is source-annotated, not true fish calling behavior",
        "timing_criteria":{"day_block_length_min_days":7,"n_MC":PERMUTATIONS,
                           "minimum_type_onset_hours":MIN_SOURCE_ONSETS,
                           "minimum_expected_overlap":MIN_EXPECTED_ONSET_OVERLAP,
                           "source_retained_days_min":MIN_TEST_DAYS,
                           "tolerance_hours":list(WINDOWS)},
        "source_block_quality":qc,
        "per_site_type_pair_timing":out,
        "screened_comparisons_by_tolerance":screens,
        "true_fish_onset_and_mechanistic_interaction":"NOT_IDENTIFIED",
        "uncalibrated_lunar_tide_weather":"DOES_NOT_DISENTANGLE_SAME_DAY_FORCING",
        "global_tide_solar_meta_effect":"NOT_ESTIMATED"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=analyze()
    path=Path(__file__).parent/"results"/"onset_transition_original_blocknull.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    if args.check:
        if result!=json.loads(path.read_text()):
            raise AssertionError("Source onsets source-verified saved values differ")
    else:
        path.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    print("V145_ONSET_NULL_START")
    print(json.dumps(result,ensure_ascii=False))
    print("V145_ONSET_NULL_END")

if __name__=="__main__":main()
