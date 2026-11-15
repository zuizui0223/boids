"""v149 California fish acoustic overlap under same-date 6h, 4h, 2h clock-bin controls.

Actual input is the 60 original v142-member-SHA-pinned Dryad fish chorus
workbooks via v144.original(). Strictly reuses the original v145 fully recorded
7+ local-day opportunity. No new causal fish-fish or tide×solar inference.

Post-hoc after v145-v148 pair directions were observed. The width=1h limit
must yield E=O exactly; it is a tautological identity, NOT evidence.
"""
from __future__ import annotations

import argparse,hashlib,json,math,sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
sys.path.insert(0,str(ROOT/"validation_v148"))
from v145_blockshift import original, TYPES, eligible_complete_days, contiguous_runs
from same_day_diel import fresh, add_group, overlap, local_time

V148_PATH=ROOT/"validation_v148/results/daily_common_gate_original_v148.json"
RECEIPT=ROOT/"validation_v149/results/frozen_source_receipt_v149.json"
FULL=ROOT/"validation_v149/results/source_annual_full_v149.json"
BIN_WIDTHS=(24,6,4,2,1)
PAIRS=tuple(combinations(TYPES,2))

def bin_groups(site, item):
    eligible=item["nominal"]-item["off"]-item["noise"]
    calendar=eligible_complete_days(eligible)
    runs=contiguous_runs(calendar)
    hours={h for r in runs for d in r for h in calendar[d]}
    by_width={w:defaultdict(fresh) for w in BIN_WIDTHS}
    pos={t:item["fish"].get(t,set()) for t in TYPES}
    for h in hours:
        local=local_time(h)
        types=tuple(t for t in TYPES if h in pos[t])
        for w in BIN_WIDTHS:
            add_group(by_width[w],(local.date(),local.hour//w),types)
    if sum(v["n"] for v in by_width[1].values())!=len(hours):
        raise AssertionError("Source 1-hour partition lost/duplicated hours")
    if any(v["n"]!=1 for v in by_width[1].values()):
        raise AssertionError("Source 1h partition must have exactly one real hour")
    if any(v["n"]!=24 for v in by_width[24].values()):
        raise AssertionError("Original date must have 24 complete local observed hours")
    return hours,runs,by_width

def compare_pair(group_map,a,b, ref_o):
    row={}
    for w in BIN_WIDTHS:
        obs,expectation=overlap(group_map[w],a,b)
        if obs!=ref_o:raise AssertionError("Original same-hour O changed under "+str(w)+"h group")
        row[str(w)]=round(expectation,8)
    if abs(row["1"]-ref_o)>1e-8:raise AssertionError("1h exact saturation must equal O")
    return row

def subgroups(groups,year):
    return {w:{k:v for k,v in g.items() if k[0].year==year} for w,g in groups.items()}

def estimate():
    old=json.loads(V148_PATH.read_text())
    if (old["n_sites"]!=9 or old["n_site_pair_records"]!=90
        or old["total_source_hours"]!=136032 or old["n_site_years"]!=32):
        raise AssertionError("Prior source sample drift")
    bypair={(r["site"],r["chorus_A"],r["chorus_B"]):r
            for r in old["all_90_site_pair_comparisons"]}
    byyear={(r["site"],r["local_year"],r["chorus_A"],r["chorus_B"]):r
            for r in old["all_site_year_pair_comparisons"]}
    if len(bypair)!=90 or len(byyear)!=320:raise AssertionError("Previous 90 or 320 rows changed")
    src=original()
    rows=[]; annual=[]; quality=[]
    for site, item in sorted(src.items()):
        eligible,runs,groups=bin_groups(site,item)
        site_ref=next(r for r in old["original_site_quality"] if r["site"]==site)
        if len(eligible)!=site_ref["n_hours"] or len(runs)!=site_ref["n_runs"]:
            raise AssertionError("Source opportunity not identical to v148")
        years=sorted(set(k[0].year for k in groups[24]))
        quality.append({"site":site,"source_hours":len(eligible),
                        "source_years":years,"continuous_7d_month_runs":len(runs)})
        for a,b in PAIRS:
            ref=bypair[(site,a,b)]
            o=ref["same_hour_observed"]
            e=compare_pair(groups,a,b,o)
            if abs(e["24"]-ref["E_same_local_date"])>1e-6:
                raise AssertionError("v148 same-calendar-date expectation not reproduced")
            rows.append({
                "site":site,"A":a,"B":b,"O":o,
                "E_by_hours":e,
                "OE6":round(o/e["6"],6) if e["6"]>0 else None,
                "OE4":round(o/e["4"],6) if e["4"]>0 else None,
                "OE2":round(o/e["2"],6) if e["2"]>0 else None,
                "v145_screened":ref["original_v145_site_pair_screen"]=="SCREENED_RESTRICTED_SHIFT_NULL",
                "v145_OE":ref["O_over_E_original_v145_shift"],
                "v148_date_light_OE":ref["O_over_E_date_light"]
            })
        for year in years:
            one=subgroups(groups,year)
            for a,b in PAIRS:
                ref=byyear[(site,year,a,b)]
                o=ref["same_hour_observed"]
                e=compare_pair(one,a,b,o)
                if abs(e["24"]-ref["E_same_local_date"])>1e-6:
                    raise AssertionError("v148 annual date-expectation drift")
                annual.append({"site":site,"year":year,"A":a,"B":b,"O":o,"E_by_hours":e})
        for row in rows:
            if row["site"]!=site:continue
            aa=[z for z in annual if z["site"]==site and z["A"]==row["A"] and z["B"]==row["B"]]
            if sum(z["O"] for z in aa)!=row["O"]:raise AssertionError("Annual O additivity failed")
            for w in BIN_WIDTHS:
                if abs(math.fsum(x["E_by_hours"][str(w)] for x in aa)
                        -row["E_by_hours"][str(w)])>0.00002:
                    raise AssertionError("Annual E additivity failed for "+str(w)+"h")
    if len(rows)!=90 or len(annual)!=320 or sum(x["source_hours"] for x in quality)!=136032:
        raise AssertionError("Frozen total source coverage failed")
    focus={}
    for b in ("UF440","White Seabass"):
        q=[z for z in rows if z["A"]=="Bocaccio" and z["B"]==b and z["v145_screened"]]
        focus[b]={
            "eligible_sites":len(q),
            "v145_positive":sum(x["v145_OE"] is not None and x["v145_OE"]>1 for x in q),
            "same_date_6h_positive":sum(x["OE6"] is not None and x["OE6"]>1 for x in q),
            "same_date_4h_positive":sum(x["OE4"] is not None and x["OE4"]>1 for x in q),
            "same_date_2h_positive":sum(x["OE2"] is not None and x["OE2"]>1 for x in q),
            "all_sites":[{"site":x["site"],"O":x["O"],
                          "OE_v145_shift":x["v145_OE"],
                          "OE_date_solar":x["v148_date_light_OE"],
                          "OE6":x["OE6"],"OE4":x["OE4"],"OE2":x["OE2"]}
                         for x in q]
        }
    full={"version":"v149_original_source_within_date_clock_bin_conditional_1",
          "original_60_sha_members_rechecked":True,
          "source_summary":{"sites":len(quality),"site_years":32,
                            "acoustic_sites_x_type_pairs":len(rows),"source_site_year_pair_rows":len(annual),
                            "source_hours":sum(x["source_hours"] for x in quality)},
          "bin_widths_hours":list(BIN_WIDTHS),
          "bin_expected_definition":"sum over same local-date x clock-bin fixed A/B acoustic-hour margins of positives_A*positives_B / hours",
          "one_hour_expected_equals_observed_by_construction":True,
          "source_sites":quality,
          "site_pair":rows,
          "site_year_pair":annual,
          "selected_pair_focus_posthoc":focus,
          "p_values_not_computed":True,
          "tidal_solar_effect":"NOT_ESTIMATED",
          "social_boids_forces":"NOT_IDENTIFIED"}
    source_repr=json.dumps(full,ensure_ascii=True,sort_keys=True,separators=(",",":"))
    receipt={
        "version":full["version"],
        "canonical_full_source_aggregate_SHA256":hashlib.sha256(source_repr.encode()).hexdigest(),
        "canonical_full_source_aggregate_nbytes":len(source_repr.encode()),
        "source_summary":full["source_summary"],
        "original_60_sha_members_rechecked":True,
        "bin_widths_hours":list(BIN_WIDTHS),
        "selected_pair_focus_posthoc":focus,
        "source_sites":quality,
        "full_90_pair_source_records":len(rows),
        "full_320_siteyear_pair_source_records":len(annual),
        "no_new_p_values":True,
        "one_hour_null_is_tautological":True,
        "independent_coastal_studies_added":0,
        "tidal_solar_pooled_effect":"NOT_ESTIMATED",
        "fish_individual_boids_social_forces":"NOT_IDENTIFIED"}
    return full,receipt

def main():
    p=argparse.ArgumentParser()
    q=p.add_mutually_exclusive_group(required=True)
    q.add_argument("--emit",action="store_true")
    q.add_argument("--check",action="store_true")
    args=p.parse_args()
    full,receipt=estimate()
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("Frozen source receipt required")
        saved=json.loads(RECEIPT.read_text())
        if saved!=receipt:
            changes=[k for k in sorted(set(receipt)|set(saved)) if receipt.get(k)!=saved.get(k)]
            raise AssertionError("Frozen original-source compact receipt drift: "+repr(changes))
        print("V149_FROZEN_SHA256_RECEIPT_SUCCESS")
    else:
        print("V149_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V149_SOURCE_RECEIPT_END")
    print("V149_SOURCE_SCOPE="+json.dumps(receipt["source_summary"],sort_keys=True))
    print("V149_CLOCKBIN_FOCUS="+json.dumps(receipt["selected_pair_focus_posthoc"],sort_keys=True))

if __name__=="__main__":main()
