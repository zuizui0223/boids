"""Observed within-bat high conspecific call density versus attack success.

Original Krivoruchko et al 2024 Molossus source is ALREADY published.
Contrasts are descriptive, condition on attacks and source bat identity.
No new animal records, no individual bat IDs/rows emitted, no causal claim.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
import hashlib, io, json, math, random, zipfile

from molossus_2024_supplement_structure_v1 import download_bounded, URL, EXPECTED
from molossus_2024_source_capture_LOBO_v1 import decode_sheet, SOURCE_SHA, parse_integer
from molossus_2024_source_capture_LOBO_corrected_v2 import admit_corrected_source

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_RESULT_V1.json"
CONTRACT=ROOT/"MOLOSSUS_WITHIN_BAT_HIGH_DENSITY_PREOUTPUT_2026_11_07.md"
BOOT_SEED=20261107
BOOT_N=5000

def source_group(d):
    if d==0:return "zero"
    if d<=25:return "low"
    if d<=75:return "moderate"
    return "high"

def quantiles(v):
    if not v:return None
    v=sorted(v)
    return {"min":v[0],"median":median(v),"max":v[-1]}

def bootstrap(vals):
    n=len(vals)
    if not n:return None
    rng=random.Random(BOOT_SEED)
    s=sorted(mean(vals[rng.randrange(n)] for _ in range(n)) for _ in range(BOOT_N))
    def p(q):
        h=(len(s)-1)*q
        k=int(h)
        return s[k]*(1-(h-k))+s[min(k+1,len(s)-1)]*(h-k)
    return [p(.025),p(.975)]

def pair_tables(rows,ref="moderate",by_time=False):
    grouped=defaultdict(lambda:{"high":{"A":0,"Y":0,"rows":0},
                                "ref":{"A":0,"Y":0,"rows":0}})
    source_bats={}
    for row in rows:
        bat=row["bat"]
        band=source_group(row["density"])
        if band not in ("high",ref):continue
        key=(bat,row["third"]) if by_time else (bat,)
        side="high" if band=="high" else "ref"
        group=grouped[key][side]
        group["A"]+=row["A"];group["Y"]+=row["Y"];group["rows"]+=1
        source_bats[key]=bat
    tables=[]
    for key,parts in grouped.items():
        hi=parts["high"];refdat=parts["ref"]
        if hi["A"]<=0 or refdat["A"]<=0:continue
        tables.append({
            "high_attacks":hi["A"],"high_success":hi["Y"],
            "ref_attacks":refdat["A"],"ref_success":refdat["Y"],
            "_bat":source_bats[key],
            "_high_rows":hi["rows"],"_reference_rows":refdat["rows"]})
    return tables

def exact_lower_tail(tables):
    """Exact conditional hypergeometric per stratum; source allocation null only."""
    if not tables:return None
    dist={0:1.}
    observed=0
    for t in tables:
        H=t["high_attacks"];L=t["ref_attacks"]
        h=t["high_success"];l=t["ref_success"]
        if not all(isinstance(q,int) and q>=0 for q in (H,L,h,l)):
            raise ValueError("Counts must be nonnegative integers")
        if h>H or l>L or H<=0 or L<=0:
            raise ValueError("Invalid original attempt/success stratum")
        N=H+L;S=h+l
        normalizer=math.comb(N,H)
        lo=max(0,H-(N-S));hi=min(H,S)
        probs={x:math.comb(S,x)*math.comb(N-S,H-x)/normalizer
               for x in range(lo,hi+1)}
        new=defaultdict(float)
        for old,p in dist.items():
            for x,q in probs.items():
                new[old+x]+=p*q
        dist=new
        observed+=h
    return min(1.,max(0.,sum(p for success,p in dist.items() if success<=observed)))

def mantel_haenszel_or(tables):
    if not tables:return None
    up=down=0.
    for t in tables:
        h=t["high_success"];A=t["high_attacks"]
        l=t["ref_success"];L=t["ref_attacks"]
        N=A+L
        up+=h*(L-l)/N
        down+=(A-h)*l/N
    if down==0:return None
    return up/down

def observed_bat_contrast(rows,ref):
    tables=pair_tables(rows,ref,by_time=False)
    cats={"high":source_group(100),"reference":ref}
    eligible=len(tables)
    if eligible<3:
        return {"status":"SOURCE_SUPPORT_STOP_LT_3_BATS",
                "reference_band":ref,"eligible_bats":eligible,
                "conditional_exact_lower_tail":None}
    ds=[t["high_success"]/t["high_attacks"]-
        t["ref_success"]/t["ref_attacks"] for t in tables]
    high=[t["high_attacks"] for t in tables]
    ref_counts=[t["ref_attacks"] for t in tables]
    summary={
        "status":"DESCRIPTIVE_WITHIN_BAT_CONTRAST",
        "reference_band":ref,"eligible_bats":eligible,
        "high_attacks_eligible":sum(high),
        "reference_attacks_eligible":sum(ref_counts),
        "high_successes_eligible":sum(t["high_success"] for t in tables),
        "reference_successes_eligible":sum(t["ref_success"] for t in tables),
        "per_bat_high_attack_support":quantiles(high),
        "per_bat_reference_attack_support":quantiles(ref_counts),
        "bat_mean_high_minus_reference_success_fraction":mean(ds),
        "bat_median_high_minus_reference_success_fraction":median(ds),
        "bat_bootstrap95_mean_risk_difference":bootstrap(ds),
        "bats_high_fraction_lower":sum(x<0 for x in ds),
        "bats_high_fraction_higher":sum(x>0 for x in ds),
        "bats_high_fraction_equal":sum(x==0 for x in ds),
        "mantel_haenszel_success_odds_ratio":mantel_haenszel_or(tables),
        "conditional_exact_lower_tail":exact_lower_tail(tables),
        "original_bat_IDs_exported":False,
        "source_probability_not_randomized_causal_pvalue":True
    }
    return summary

def flight_third(sec,low,high):
    if high<=low:raise ValueError("Source flight group indices not ordered")
    t=(sec-low)/(high-low)
    if not 0<=t<=1:
        raise ValueError("Source sec_group index out of range")
    return 0 if t<1/3 else 1 if t<2/3 else 2

def add_flight_thirds(rows):
    mins={}
    maxs={}
    for r in rows:
        b=r["bat"];s=r["sec"]
        mins[b]=min(s,mins.get(b,s))
        maxs[b]=max(s,maxs.get(b,s))
    for r in rows:
        r["third"]=flight_third(r["sec"],mins[r["bat"]],maxs[r["bat"]])

def run_time_stratification(rows):
    if any("third" not in x for x in rows):
        add_flight_thirds(rows)
    tables=pair_tables(rows,"moderate",by_time=True)
    bats=len({t["_bat"] for t in tables})
    high_attack_covered=sum(t["high_attacks"] for t in tables)
    all_high_attacks=sum(r["A"] for r in rows if source_group(r["density"])=="high")
    enough=bats>=3 and high_attack_covered>=8
    return {
        "status":"DESCRIPTIVE_TIME_MATCHED" if enough
                   else "SOURCE_SUPPORT_STOP_LOW_TIME_MATCHED_COVERAGE",
        "support_status":"SUPPORTED" if enough else "STOP",
        "source_bats_with_time_matched_high_and_moderate_attacks":bats,
        "eligible_bat_flight_third_strata":len(tables),
        "original_high_attacks_covered":high_attack_covered,
        "original_high_attacks_not_covered":all_high_attacks-high_attack_covered,
        "original_moderate_attacks_covered":sum(t["ref_attacks"] for t in tables),
        "observed_high_successes_covered":sum(t["high_success"] for t in tables),
        "exact_conditional_null":"exchangeable success allocation within source bat x flight third, not causal",
        "conditional_exact_lower_tail":exact_lower_tail(tables) if enough else None,
        "bat_IDs_or_source_rows_exported":False
    }

def from_original():
    if not CONTRACT.exists():raise ValueError("STOP_SOURCE_TEST_NOT_PRECOMMITTED")
    binary,status,ctype=download_bounded(URL)
    z=zipfile.ZipFile(io.BytesIO(binary))
    matches=[f for f in z.infolist() if f.filename.split("/")[-1]==EXPECTED]
    if len(matches)!=1:raise ValueError("STOP_SOURCE_WORKBOOK_NOT_UNIQUE")
    raw=z.read(matches[0])
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=SOURCE_SHA:raise ValueError("STOP_SOURCE_WORKBOOK_SHA_CHANGED")
    source_rows=decode_sheet(raw)
    rows,clean,metadata=admit_corrected_source(source_rows)
    for r,rawrow in zip(rows,source_rows):
        assert r["bat"]==str(rawrow[0]).strip()
        r["sec"]=parse_integer(rawrow[1],"sec_group")
    return rows,clean,metadata,digest

def analyze_cohort(rows):
    contrasts={ref:observed_bat_contrast(rows,ref)
               for ref in ("moderate","low","zero")}
    return {
        "source_bats":len({r["bat"] for r in rows}),
        "source_5s_windows":len(rows),
        "high_density_original_bats":len({r["bat"] for r in rows if source_group(r["density"])=="high"}),
        "high_density_original_windows":sum(source_group(r["density"])=="high" for r in rows),
        "high_density_original_attacks":sum(r["A"] for r in rows if source_group(r["density"])=="high"),
        "by_reference":contrasts,
        "high_vs_moderate_time_thirds":run_time_stratification(rows)
    }

def run():
    rows,clean,meta,digest=from_original()
    primary=analyze_cohort(rows)
    secondary=analyze_cohort([r.copy() for r in rows if r["bat"] in clean])
    return {
        "schema":1,"date":"2026-11-07",
        "status":"SECONDARY_PUBLISHED_WITHIN_BAT_HIGH_CALL_DENSITY",
        "source_paper_doi":"10.1073/pnas.2321724121",
        "source_workbook_sha256":digest,
        "original_source_rows":4299,"original_bats":10,
        "original_bat_ids_or_five_second_rows_exported":False,
        "new_bat_measurements":False,
        "postpublication_and_prior_aggregate_outcomes_seen":True,
        "original_2024_glmm_with_bat_effect_already_prior_art":True,
        "high_threshold_calls_per_5s":76,
        "primary_original_all_ten":primary,
        "sensitivity_overlapping_nine_complete_secgroup":secondary,
        "inference_limit":"Descriptive conditional original source attack-success association; no randomization, behavioral mechanism or other species validation."
    }

def main():
    try:o=run()
    except Exception as e:
        o={"schema":1,"status":"STOP_ORIGINAL_SOURCE_OR_LOCK",
           "error":type(e).__name__+":"+str(e)[:230],
           "new_bat_measurements":False,
           "original_bat_ids_or_five_second_rows_exported":False}
    OUT.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
    print("WITHIN_BAT_SOURCE_STATUS",o["status"])
    if o["status"].startswith("STOP"):
        print("STOP_REASON",o["error"])
        return 3
    for cohort in ("primary_original_all_ten","sensitivity_overlapping_nine_complete_secgroup"):
        r=o[cohort]
        print("COHORT",cohort,"source_bats",r["source_bats"],
              "original_5s_rows",r["source_5s_windows"],
              "high_calls_bats",r["high_density_original_bats"],
              "high_attacks",r["high_density_original_attacks"])
        for name,v in r["by_reference"].items():
            print("WITHIN_BAT",cohort,name,json.dumps(v,sort_keys=True))
        print("FLIGHT_TIME_THIRDS",cohort,json.dumps(r["high_vs_moderate_time_thirds"],sort_keys=True))
    return 0

if __name__=="__main__":raise SystemExit(main())
