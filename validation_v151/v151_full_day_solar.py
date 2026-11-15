"""v151: full-source-day bout-preserving +/-1,2h controls and solar-mask audit.

Required source: all 60 published California fish-chorus XLS workbooks, each
independently SHA256 checked by v144.original()/v142. Retains exactly the
v145 original 136032 hours; never imputes unrecorded events as negatives.

The full-date comparison circularly shifts B's own 24h binary source profile
by +/-1 or 2 hours. This creates seam artifacts at midnight; a separate
20h nonwrap comparison and solar-stable/solar-transition split expose them.

Signed hour offsets are NOT exchangeable randomization replicates, so do not
report biological p-values or fish social/reproductive causal interactions.
"""
from __future__ import annotations

import argparse,hashlib,json,sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
sys.path.insert(0,str(ROOT/"validation_v144"))
sys.path.insert(0,str(ROOT/"validation_v150"))
from v145_blockshift import original,TYPES,eligible_complete_days,contiguous_runs,hour_mask
from full9_temporal import sun_alt
from v150_bout_shift import safe_central_hours

V145=ROOT/"validation_v145/results/source_blockshift_cochorus_null.json"
V150=ROOT/"validation_v150/results/frozen_source_receipt_v150.json"
OUT=ROOT/"validation_v151/results/full_day_solar_mask_source_v151.json"
RECEIPT=ROOT/"validation_v151/results/frozen_source_receipt_v151.json"
PAIRS=tuple(combinations(TYPES,2))
LAGS=(0,-2,-1,1,2)
MIDNIGHT=(0,1,22,23)
CENTRAL=tuple(range(2,22))
STRATA=("full24_cyclic","central20_no_wrap","solar_stable_no_wrap",
        "solar_transition_adjacent_no_wrap","midnight_wrap_four_hours")
NIGHT=-0.833

def score_bits(a,b,hours,wrapped):
    """The four negative control offsets keep B's original same-day bout."""
    if not wrapped and any(h not in CENTRAL for h in hours):
        raise ValueError("Nonwrap offset evaluation requires focal 02..21h")
    return [sum((a>>h&1)*(b>>((h+lag)%24 if wrapped else h+lag)&1)
                for h in hours) for lag in LAGS]

def source_date_scores(site,day_hours,by_type,night):
    if len(day_hours)!=24 or len(night)!=24:raise ValueError("Complete source day required")
    safe=safe_central_hours(night)
    crossed=tuple(h for h in CENTRAL if h not in set(safe))
    if len(safe)+len(crossed)!=20:raise AssertionError("Solar mask partition changed")
    windows={
        "full24_cyclic":(tuple(range(24)),True),
        "central20_no_wrap":(CENTRAL,False),
        "solar_stable_no_wrap":(safe,False),
        "solar_transition_adjacent_no_wrap":(crossed,False),
        "midnight_wrap_four_hours":(MIDNIGHT,True),
    }
    if sum(len(hs) for k,(hs,_) in windows.items() if k=="solar_stable_no_wrap" or k=="solar_transition_adjacent_no_wrap")!=20:
        raise AssertionError("Solar masks do not partition central 20h")
    overlap={}
    for aa,bb in PAIRS:
        overlap[(aa,bb)]={key:score_bits(by_type[aa],by_type[bb],h,wrap)
                          for key,(h,wrap) in windows.items()}
        for i in range(5):
            obs=overlap[(aa,bb)]
            if obs["full24_cyclic"][i] != (obs["central20_no_wrap"][i]+obs["midnight_wrap_four_hours"][i]):
                raise AssertionError("Full source-day split into central and wrap seam failed")
            if obs["central20_no_wrap"][i] != (obs["solar_stable_no_wrap"][i]+obs["solar_transition_adjacent_no_wrap"][i]):
                raise AssertionError("Full central-day split into light-safe and transition failed")
    return overlap,{k:len(windows[k][0]) for k in STRATA}

def blank():
    return {name:[0]*5 for name in STRATA}

def ratio(vals):
    o=vals[0];sh=sum(vals[1:])
    return round(4*o/sh,6) if sh else None

def source():
    frozen=json.loads(V145.read_text())
    v150=json.loads(V150.read_text())
    if frozen["screened_site_pairs"]!=32 or frozen["sites"]!=9 or frozen["original_deployments"]!=60:
        raise AssertionError("v145 source scope changed")
    if v150["source_complete_local_day_hours"]!=136032 or v150["source_solar_safe_shift_hours"]!=68091:
        raise AssertionError("v150 source/solar truth changed")
    orig=original()
    old={(r["site"],r["chorus_A"],r["chorus_B"]):r for r in frozen["per_site_type_pair"]}
    if len(old)!=90:raise AssertionError("Source full nine-site ten-pair truth required")
    qual=[];site_results=[];year_results=[]
    for site,item in sorted(orig.items()):
        effort=item["nominal"]-item["off"]-item["noise"]
        days=eligible_complete_days(eff)
        runs=contiguous_runs(days)
        years=defaultdict(lambda:{p:blank() for p in PAIRS})
        opportunity=defaultdict(lambda:{s:0 for s in STRATA})
        site_day_count=0
        source_pos={typ:item["fish"].get(typ,set()) for typ in TYPES}
        for run in runs:
            for local_date in run:
                h=days[local_date]
                flags=[sun_alt(site,hh)<NIGHT for hh in h]
                bit={typ:hour_mask(h,source_pos[typ]) for typ in TYPES}
                day_scores,day_hrs=source_date_scores(site,h,bit,flags)
                yr=local_date.year
                site_day_count+=1
                for strata,nh in day_hrs.items():opportunity[yr][strata]+=nh
                for p,panels in day_scores.items():
                    v=years[yr][p]
                    for strata,nums in panels.items():
                        for i in range(5):v[strata][i]+=nums[i]
        ref=next(x for x in frozen["source_site_block_qc"] if x["site"]==site)
        if 24*site_day_count!=ref["selected_source_eligible_hours"]:
            raise AssertionError("V145 original site hour mismatch")
        if len(runs)!=ref["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("V145 original source run mismatch")
        site_opp={name:sum(opportunity[yr][name] for yr in opportunity) for name in STRATA}
        if site_opp["full24_cyclic"]!=site_day_count*24 or site_opp["central20_no_wrap"]!=site_day_count*20:
            raise AssertionError("Source per-day opportunity mismatch")
        qual.append({"site":site,"years":sorted(years),"complete_source_days":site_day_count,
                     "source_7day_runs":len(runs),"opportunity_hours":site_opp})
        for year in sorted(years):
            for a,b in PAIRS:
                v=years[year][(a,b)]
                year_results.append({
                    "site":site,"year":year,"A":a,"B":b,
                    "panels":{s:{"O":v[s][0],"four_shift_total":sum(v[s][1:])}
                              for s in STRATA},
                })
        for a,b in PAIRS:
            site_years=[r for r in year_results if r["site"]==site and r["A"]==a and r["B"]==b]
            v={name:[sum(years[year][(a,b)][name][i] for year in years)
                     for i in range(5)] for name in STRATA}
            source_o=old[(site,a,b)]["observed_same_hour_chorusing_in_retained_blocks"]
            if v["full24_cyclic"][0]!=source_o:
                raise AssertionError("Full source O differs from exact original v145 observed hours")
            for stratum in STRATA:
                if sum(r["panels"][stratum]["O"] for r in site_years)!=v[stratum][0]:
                    raise AssertionError("Source year-additive O failed")
                if sum(r["panels"][stratum]["four_shift_total"] for r in site_years)!=sum(v[stratum][1:]):
                    raise AssertionError("Source year-additive shifted control failed")
            site_results.append({
                "site":site,"A":a,"B":b,
                "source_v145_screened":old[(site,a,b)]["status"]=="SCREENED_RESTRICTED_SHIFT_NULL",
                "source_all24h_O":source_o,
                "strata":{name:{
                    "O":v[name][0],
                    "E_mean_four_offset_controls":sum(v[name][1:])/4,
                    "observed_over_offset_control":ratio(v[name])
                    } for name in STRATA}
            })
    if len(qual)!=9 or len(site_results)!=90 or len(year_results)!=320:raise AssertionError("Source site pairing scope failed")
    total={name:sum(q["opportunity_hours"][name] for q in qual) for name in STRATA}
    if total["full24_cyclic"]!=136032 or total["solar_stable_no_wrap"]!=68091:
        raise AssertionError("Old source and previous solar-stable opportunities not exactly reproduced")
    if total["central20_no_wrap"]!=113360 or total["solar_transition_adjacent_no_wrap"]!=45269 or total["midnight_wrap_four_hours"]!=22672:
        raise AssertionError("Original 20h daylight partition changed")
    # Old v150 known-focus exact overlap is an independent source-coherence gate.
    for b in ("UF440","White Seabass"):
        for ref in v150["target_pair_focus_posthoc"][b]["site_rows"]:
            row=next(x for x in site_results if x["site"]==ref["site"] and x["A"]=="Bocaccio" and x["B"]==b)
            if row["strata"]["solar_stable_no_wrap"]["O"]!=ref["narrow_presence_O"]:
                raise AssertionError("Original v150 observed coincidence changed")
            if row["strata"]["solar_stable_no_wrap"]["E_mean_four_offset_controls"]!=ref["shifted_presence_expected"]:
                raise AssertionError("Original v150 shifted control changed")
    focus={}
    for b in ("UF440","White Seabass"):
        q=[row for row in site_results if row["A"]=="Bocaccio" and row["B"]==b and row["source_v145_screened"]]
        focus[b]={
            "sites":len(q),
            "strata_above_one":{stratum:sum(x["strata"][stratum]["observed_over_offset_control"] is not None and
                                             x["strata"][stratum]["observed_over_offset_control"]>1
                                             for x in q) for stratum in STRATA},
            "sites_data":[{"site":x["site"],
                           "full24h":x["strata"]["full24_cyclic"],
                           "central20h":x["strata"]["central20_no_wrap"],
                           "stable_solar":x["strata"]["solar_stable_no_wrap"],
                           "solar_transition":x["strata"]["solar_transition_adjacent_no_wrap"],
                           "midnight_wrap":x["strata"]["midnight_wrap_four_hours"]}
                          for x in q]
        }
    full={
        "version":"v151_original_daywide_same_date_shift_vs_solar_mask_loss_1",
        "all60_original_workbook_SHA256_verified":True,
        "source_scope":{"sites":9,"site_years":32,"site_pairs":90,"annual_pairs":320,
                        "original_day_hours":total["full24_cyclic"],"source_daily_7dplus_runs":275},
        "source_opportunity_by_window":total,
        "controls_are_descriptive_not_valid_randomization_p":True,
        "full24h_cyclic_wrap_may_modify_original_midnight_bout_seam":True,
        "true_local_physical_tide_unmeasured":True,
        "source_sites":qual,
        "all90_site_pairs":site_results,
        "all320_site_year_pairs":year_results,
        "posthoc_known_pair_focus":focus,
        "actual_interspecific_social_effect":"NOT_IDENTIFIED",
        "global_tide_solar_effect":"NOT_ESTIMATED",
    }
    canon=json.dumps(full,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    receipt={
        "version":full["version"],
        "original_60_SHA256_rechecked":True,
        "full_source_canonical_SHA256":hashlib.sha256(canon.encode()).hexdigest(),
        "full_source_canonical_bytes":len(canon.encode()),
        "source_scope":full["source_scope"],
        "source_opportunity_by_window":total,
        "source_sites":qual,
        "posthoc_known_pair_focus":focus,
        "p_values_not_computed":True,
        "source_internal_60_workbooks_and_v145_v150_exact_crosschecks":True,
        "independent_coast_studies_added":0,
        "tide_solar_pooled_biological_effect":"NOT_ESTIMATED",
        "fish_social_boids_forces":"NOT_IDENTIFIED",
    }
    return full,receipt

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=ap.parse_args()
    full,receipt=source()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("Frozen v151 authenticated receipt absent")
        saved=json.loads(RECEIPT.read_text())
        if saved!=receipt:
            changed=[k for k in sorted(set(saved)|set(receipt)) if saved.get(k)!=receipt.get(k)]
            raise AssertionError("Full original source canonical fingerprint/result changes: "+repr(changed))
        print("V151_FROZEN_ORIGINAL_SOURCE_FULL_REPLAY_SUCCESS")
    else:
        print("V151_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V151_SOURCE_RECEIPT_END")
    print("V151_SUMMARY_START")
    print(json.dumps({"opportunities":receipt["source_opportunity_by_window"],
                      "focus":receipt["posthoc_known_pair_focus"]},sort_keys=True,ensure_ascii=True))
    print("V151_SUMMARY_END")

if __name__=="__main__":main()
