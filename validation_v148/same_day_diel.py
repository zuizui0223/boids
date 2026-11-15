"""v148: distinguish daily common-state coactivity from within-day temporal overlap.

TRUE SOURCE: all sixty v142 SHA-verified original fish chorus workbooks. Fix
exactly v145 retained 7+ contiguous complete local 24h calendar days and source
Off/noise exclusion. All 90 observed O must reproduce v145 exactly.

Expected overlaps are CONDITIONAL INDEPENDENCE DESCRIPTIVES, not randomization
p-values and do not preserve both 24-hour call bout trajectories. Each model
compares identical actual source hours:
  M1: previous v145 day-block circular-shift exact expected E,
  M2: same local date with fixed daily positive-hour margins,
  M3: same local date x astronomical daylight/night with fixed stratum margins,
  M4: same local year-month x local clock hour,
and no inferred causal contribution from differences among these expectations.
"""
from __future__ import annotations

import argparse
from collections import defaultdict, Counter
from datetime import date
from itertools import combinations
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "validation_v145"))
sys.path.insert(0, str(ROOT / "validation_v144"))
from v145_blockshift import original, TYPES, eligible_complete_days, contiguous_runs
from full9_temporal import local_time, sun_alt

INPUT = ROOT / "validation_v145/results/source_blockshift_cochorus_null.json"
OUTPUT = ROOT / "validation_v148/results/daily_common_gate_original_v148.json"
SOLAR_ALT_CUTOFF = -0.833
ALL_PAIRS = tuple(combinations(TYPES, 2))

def fresh():
    return {"n": 0, "positive": Counter(), "joint": Counter()}

def add_group(groups, key, types):
    g = groups[key]
    g["n"] += 1
    g["positive"].update(types)
    g["joint"].update(combinations(types, 2))

def overlap(groups, a, b):
    # Freeze source-group ordering across Python hash seeds.  math.fsum
    # prevents 1e-8 decimal rounding drift from different group insertion
    # orders; this is a numerical reproducibility repair, not model tuning.
    keys = sorted(groups)
    o = sum(groups[k]["joint"][(a, b)] for k in keys)
    e = math.fsum(
        groups[k]["positive"][a] * groups[k]["positive"][b] / groups[k]["n"]
        for k in keys if groups[k]["n"]
    )
    return o, e

def inspect_site(site, info):
    original_hours = info["nominal"] - info["off"] - info["noise"]
    days = eligible_complete_days(original_hours)
    runs = contiguous_runs(days)
    retained = {h for run in runs for d in run for h in days[d]}
    by_date = defaultdict(fresh)
    by_date_light = defaultdict(fresh)
    by_month_hour = defaultdict(fresh)
    num_hours_by_year = Counter()
    num_days_by_year = Counter()
    fish = {typ: info["fish"].get(typ, set()) for typ in TYPES}
    for run in runs:
        for d in run:
            num_days_by_year[d.year] += 1
    for h in retained:
        dt = local_time(h)
        local_date = dt.date()
        light = "night" if sun_alt(site, h) < SOLAR_ALT_CUTOFF else "day_including_twilight"
        typs = tuple(x for x in TYPES if h in fish[x])
        add_group(by_date, (local_date,), typs)
        add_group(by_date_light, (local_date,light), typs)
        add_group(by_month_hour, (dt.year,dt.month,dt.hour), typs)
        num_hours_by_year[dt.year] += 1
    if len(retained) != sum(g["n"] for g in by_date.values()):
        raise AssertionError("Overlapping/vanishing source hours")
    if len(retained) != sum(g["n"] for g in by_date_light.values()):
        raise AssertionError("Lost source in day/daylight grouping")
    if len(retained) != sum(g["n"] for g in by_month_hour.values()):
        raise AssertionError("Lost source in yearmonth/clock grouping")
    if any(g["n"]!=24 for g in by_date.values()):
        raise AssertionError("Expected precisely 24 observed local hours per source date")
    if len(by_date) != len(retained)//24:
        raise AssertionError("Expected unique selected source days")
    return {
        "hours":len(retained),
        "run_count":len(runs),
        "days":len(by_date),
        "site_years":sorted(num_hours_by_year),
        "hours_by_year":num_hours_by_year,
        "days_by_year":num_days_by_year,
        "date_groups":by_date,
        "date_light_groups":by_date_light,
        "yearmonth_clock_groups":by_month_hour,
    }

def subset_year(groups, year):
    # Date, date+light or yearmonth+hour keys all have a local-date/year first key.
    return {k:g for k,g in groups.items() if
            (k[0].year if isinstance(k[0],date) else k[0])==year}

def round8(v):
    return round(v,8)

def safe_ratio(o, e):
    return round(o/e,6) if e>0 else None

def score_pair(a,b,groups1,groups2,groups3,source_shift=None):
    o1,e1=overlap(groups1,a,b)
    o2,e2=overlap(groups2,a,b)
    o3,e3=overlap(groups3,a,b)
    if not (o1==o2==o3):
        raise AssertionError("Observed same-hour overlap changes under conditioning")
    row={
        "chorus_A":a,"chorus_B":b,"same_hour_observed":o1,
        "E_same_local_date":round8(e1),
        "E_same_local_date_and_astronomical_light":round8(e2),
        "E_same_local_yearmonth_and_clockhour":round8(e3),
        "O_over_E_date":safe_ratio(o1,e1),
        "O_over_E_date_light":safe_ratio(o1,e2),
        "O_over_E_month_clock":safe_ratio(o1,e3),
        "night_tag_is_solar_altitude_below_degrees":SOLAR_ALT_CUTOFF,
        "note":"E are fixed-margin conditional independence expectations; not track-preserving valid p-value nulls",
    }
    if source_shift is not None:
        observed=int(source_shift["observed_same_hour_chorusing_in_retained_blocks"])
        if observed!=o1:raise AssertionError("Source frozen v145 O changed")
        expected=float(source_shift["exact_shift_null_expected_same_hour_hours"])
        row["E_original_v145_whole_local_day_shift"]=round8(expected)
        row["O_over_E_original_v145_shift"]=safe_ratio(o1,expected)
        row["original_v145_site_pair_screen"]=source_shift["status"]
        row["direction_shift_plus"]=o1>expected
        row["direction_date_light_plus"]=o1>e2
        row["qualitative_sign_changed_at_date_light"]=((o1>expected)!=(o1>e2)) if o1!=expected and o1!=e2 else None
    return row

def run():
    frozen=json.loads(INPUT.read_text())
    if frozen["sites"]!=9 or frozen["original_deployments"]!=60 or frozen["screened_site_pairs"]!=32:
        raise AssertionError("v145 frozen source scope changed")
    if not frozen["source_original_workbook_SHA_verified_all_60"]:
        raise AssertionError("v145 source SHA provenance changed")
    source=original()
    if set(source)!={q["site"] for q in frozen["source_site_block_qc"]}:
        raise AssertionError("v145 nine-site source mismatch")
    lookup={(r["site"],r["chorus_A"],r["chorus_B"]):r for r in frozen["per_site_type_pair"]}
    if len(lookup)!=90:raise AssertionError("All original 90 site-by-pair rows required")
    sites=[];all_pairs=[];all_years=[]
    for site,info in sorted(source.items()):
        s=inspect_site(site,info)
        ref=next(x for x in frozen["source_site_block_qc"] if x["site"]==site)
        if s["hours"]!=ref["selected_source_eligible_hours"] or s["run_count"]!=ref["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("Source 7+ day retained opportunity changed")
        sites.append({"site":site,"n_hours":s["hours"],"n_days":s["days"],"n_years":len(s["site_years"]),"n_runs":s["run_count"],
                      "n_date_x_light_strata":len(s["date_light_groups"]),
                      "n_yearmonth_x_hour_strata":len(s["yearmonth_clock_groups"]),
                      "hours_by_year":{str(y):s["hours_by_year"][y] for y in s["site_years"]}})
        for a,b in ALL_PAIRS:
            fr=lookup[(site,a,b)]
            v=score_pair(a,b,s["date_groups"],s["date_light_groups"],s["yearmonth_clock_groups"],fr)
            v["site"]=site
            all_pairs.append(v)
        for year in s["site_years"]:
            g1=subset_year(s["date_groups"],year)
            g2=subset_year(s["date_light_groups"],year)
            g3=subset_year(s["yearmonth_clock_groups"],year)
            if sum(g["n"] for g in g1.values())!=s["hours_by_year"][year]:
                raise AssertionError("Year group did not preserve effort")
            for a,b in ALL_PAIRS:
                v=score_pair(a,b,g1,g2,g3)
                v["site"]=site
                v["local_year"]=year
                v["source_hours"]=s["hours_by_year"][year]
                all_years.append(v)
        # Yearwise observed and all three E are additive across local years.
        for a,b in ALL_PAIRS:
            total=next(x for x in all_pairs if x["site"]==site and x["chorus_A"]==a and x["chorus_B"]==b)
            subtotals=[x for x in all_years if x["site"]==site and x["chorus_A"]==a and x["chorus_B"]==b]
            if sum(x["same_hour_observed"] for x in subtotals)!=total["same_hour_observed"]:
                raise AssertionError("Yearwise observed O did not add to total")
            for k in ["E_same_local_date","E_same_local_date_and_astronomical_light","E_same_local_yearmonth_and_clockhour"]:
                if abs(sum(x[k] for x in subtotals)-total[k])>0.0002:
                    raise AssertionError("Yearwise exact conditional E did not add")
    if len(all_pairs)!=90 or sum(q["n_hours"] for q in sites)!=136032 or sum(q["n_runs"] for q in sites)!=275:
        raise AssertionError("Frozen scope missing")
    targets={}
    for b in ("UF440","White Seabass"):
        rows=[r for r in all_pairs if r["chorus_A"]=="Bocaccio" and r["chorus_B"]==b
              and r["original_v145_site_pair_screen"]=="SCREENED_RESTRICTED_SHIFT_NULL"]
        targets[b]={
            "eligible_site_count":len(rows),
            "sites_shift_residual_positive":sum(x["direction_shift_plus"] for x in rows),
            "sites_same_date_light_residual_positive":sum(x["direction_date_light_plus"] for x in rows),
            "n_same_date_light_ratio_missing":sum(x["O_over_E_date_light"] is None for x in rows),
            "sign_reversals_on_same_date_light":sum(x["qualitative_sign_changed_at_date_light"] is True for x in rows),
            "site_results":[{"site":x["site"],"O":x["same_hour_observed"],
                             "E_v145_shift":x["E_original_v145_whole_local_day_shift"],
                             "E_date":x["E_same_local_date"],
                             "E_date_light":x["E_same_local_date_and_astronomical_light"],
                             "ratio_v145_shift":x["O_over_E_original_v145_shift"],
                             "ratio_date":x["O_over_E_date"],
                             "ratio_date_light":x["O_over_E_date_light"],
                             "sign_changes":x["qualitative_sign_changed_at_date_light"]}
                            for x in rows]
        }
    return {
        "version":"v148_same_source_same_hour_date_and_diel_conditional_overlap_1",
        "source_DOI":"10.5061/dryad.q2bvq83sw",
        "source_workbooks_individual_sha256_verified":60,
        "same_136032_v145_hours":True,
        "source_scope":"all 9 sites x all 10 sound-type pairs, 32 site-years, strict 7+ whole local days",
        "expected_values_are_descriptive_no_new_randomization_p":True,
        "nulls_not_nested_and_no_attributable_causal_percentage":True,
        "shared_same_day_environment_and_audibility_remain_unmeasured":True,
        "solar_altitude_dark_threshold_degrees":SOLAR_ALT_CUTOFF,
        "original_site_quality":sites,
        "all_90_site_pair_comparisons":all_pairs,
        "all_site_year_pair_comparisons":all_years,
        "prior_selected_pair_illustrations_post_hoc":targets,
        "n_sites":len(sites),
        "n_site_years":sum(x["n_years"] for x in sites),
        "n_site_pair_records":len(all_pairs),
        "n_year_pair_records":len(all_years),
        "total_source_hours":sum(x["n_hours"] for x in sites),
        "independent_coast_studies_added":0,
        "fish_direct_social_force":"NOT_IDENTIFIED",
        "physical_tide_by_solar_effect":"NOT_ESTIMATED",
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", action="store_true")
    g.add_argument("--check", action="store_true")
    args=p.parse_args()
    result=run()
    raw=json.dumps(result,ensure_ascii=True,sort_keys=True,separators=(",",":"))
    if args.check:
        if not OUTPUT.is_file():raise AssertionError("Missing frozen source-signed v148 result")
        frozen_saved=json.loads(OUTPUT.read_text())
        if frozen_saved!=result:
            # Diagnostics only. Never accept discrepancies by loosening tolerance.
            differences=[]
            def compare(p, a, b):
                if len(differences)>=30:return
                if isinstance(a,dict) and isinstance(b,dict):
                    for k in sorted(set(a)|set(b)):
                        compare(p+"."+str(k), a.get(k,"<missing>"), b.get(k,"<missing>"))
                elif isinstance(a,list) and isinstance(b,list):
                    if len(a)!=len(b):
                        differences.append([p+".length",len(a),len(b)])
                    for i in range(min(len(a),len(b))):compare(p+"["+str(i)+"]",a[i],b[i])
                elif a!=b:
                    differences.append([p,a,b])
            compare("root",frozen_saved,result)
            print("V148_FROZEN_REPLAY_DIFF=",json.dumps(differences,ensure_ascii=True))
            raise AssertionError("Original v148 source-derived output differs")
        print("V148_SOURCE_AND_RESULT_REPLAY_SUCCESS")
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
        for i in range(0,len(raw),1800):
            print("V148_JSON_CHUNK_%05d="%(i//1800)+raw[i:i+1800])
    print("V148_RESULT_SUMMARY_START")
    print(json.dumps({"scope":{k:result[k] for k in ("n_sites","n_site_years","n_site_pair_records","n_year_pair_records","total_source_hours")},
      "target":result["prior_selected_pair_illustrations_post_hoc"]},ensure_ascii=True,sort_keys=True))
    print("V148_RESULT_SUMMARY_END")

if __name__=="__main__":main()
