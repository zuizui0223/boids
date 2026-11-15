"""v152 genuine California acoustic solar-state decomposition under v145 whole-day shifts.

Purpose: distinguish whether the v151 dawn/dusk-concentrated co-recording also
exceeds the ORIGINAL v145 clock-preserving, call-bout-preserving whole-day-shift
null, rather than ±1/2-hour controls which change diel phase.

Every one of 60 original Dryad XLS(X) members SHA-256 matches v142 via
v144.full9_temporal.original(). Same v145 complete seven-plus-day local runs.
Each type B entire daily 24-hour bitmask is rotated by INTEGER CALENDAR DAYS
within the same local year-month contiguous run (v145 exact conditional null).
A and A-day solar regime masks stay fixed. Exact mean all offsets, NO NEW p
values. This is post-v145/v151 exploratory; not fish social forces or causality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
sys.path.insert(0,str(ROOT/"validation_v144"))
sys.path.insert(0,str(ROOT/"validation_v150"))
from v145_blockshift import original, eligible_complete_days, contiguous_runs, hour_mask, TYPES
from full9_temporal import sun_alt
from v150_bout_shift import safe_central_hours

V145=ROOT/"validation_v145/results/source_blockshift_cochorus_null.json"
V151=ROOT/"validation_v151/results/frozen_source_receipt_v151.json"
OUT=ROOT/"validation_v152/results/original_solar_stratified_shift_v152.json"
RECEIPT=ROOT/"validation_v152/results/frozen_source_receipt_v152.json"
PAIRS=tuple(combinations(TYPES,2))
STRATA=("dawn_transition","dusk_transition","stable_night","stable_day","midnight_legacy")
ALL24=(1<<24)-1
SOLAR_NIGHT_ALTITUDE=-0.833

def regime_masks(site,hours):
    """Return disjoint exact 24-bit regime masks on the actual A source day."""
    if len(hours)!=24:
        raise AssertionError("All source local days must have 24 distinct observed UTC hours")
    alt=[sun_alt(site,h) for h in hours]
    dark=[z<SOLAR_NIGHT_ALTITUDE for z in alt]
    safe=set(safe_central_hours(dark))
    out={name:0 for name in STRATA}
    for local_hour in range(24):
        if local_hour in (0,1,22,23):
            key="midnight_legacy"
        elif local_hour in safe:
            key="stable_night" if dark[local_hour] else "stable_day"
        else:
            # Test whether sun is rising in real astronomical UTC, not the
            # digital local-clock arithmetic used for window selection.
            before=sun_alt(site,hours[local_hour]-1)
            after=sun_alt(site,hours[local_hour]+1)
            if abs(after-before)<1e-8:
                raise AssertionError("Astronomical dawn/dusk direction ambiguous")
            key="dawn_transition" if after>before else "dusk_transition"
        out[key]|=1<<local_hour
    combined=0
    for name in STRATA:
        if combined & out[name]:raise AssertionError("Overlapping solar regime masks")
        combined |= out[name]
    if combined!=ALL24:raise AssertionError("Solar regimes must partition the actual 24h")
    if (out["dawn_transition"]|out["dusk_transition"]|
        out["stable_night"]|out["stable_day"]) & 0b11:
        raise AssertionError("Solar central category leaked local midnight")
    return out

def exact_rotations(a,b,selectors):
    """V145 exact day-shift null scores for five disjoint A-day hourly masks.

    For every run-lag j, B[i+j modulo n] is paired with real A[i] at exactly
    the same LOCAL CLOCK HOUR, so no B-diel clock shift is introduced.
    B's complete day profiles and within-day bouts remain intact.
    """
    n=len(a)
    if not n or len(b)!=n or len(selectors)!=n:raise ValueError("Unequal empty day-shift run")
    sums={name:[0]*n for name in STRATA}
    for i in range(n):
        day_a=a[i]
        daymask=selectors[i]
        if set(daymask)!=set(STRATA):raise AssertionError("Regime labels incomplete")
        for lag in range(n):
            target_b=b[(i+lag)%n]
            total=0
            for name in STRATA:
                m=(day_a & daymask[name] & target_b).bit_count()
                sums[name][lag]+=m
                total+=m
            if total!=(day_a&target_b).bit_count():
                raise AssertionError("Per-day exact O/E regime additivity failed")
    return sums

def empty_agg():
    return {name:{"O":0,"E":0.0} for name in STRATA}

def add_to(agg,rot):
    for name in STRATA:
        xs=rot[name]
        agg[name]["O"]+=xs[0]
        agg[name]["E"]+=math.fsum(xs)/len(xs)

def summary_panel(a):
    return {name:{
        "O":a[name]["O"],
        "E":round(a[name]["E"],8),
        "O_over_E":round(a[name]["O"]/a[name]["E"],6) if a[name]["E"]>0 else None,
        "O_minus_E":round(a[name]["O"]-a[name]["E"],8)
    } for name in STRATA}

def one_source():
    ref=json.loads(V145.read_text())
    prior=json.loads(V151.read_text())
    if (ref["sites"]!=9 or ref["original_deployments"]!=60 or
        ref["screened_site_pairs"]!=32 or not ref["source_original_workbook_SHA_verified_all_60"]):
        raise AssertionError("v145 original evidence gate changed")
    if (prior["source_scope"]["original_day_hours"]!=136032 or
        prior["source_scope"]["site_pairs"]!=90 or
        prior["source_opportunity_by_window"]["solar_transition_adjacent_no_wrap"]!=45269):
        raise AssertionError("v151 original solar-mask evidence gate changed")
    original_sites=original()
    legacy={(x["site"],x["chorus_A"],x["chorus_B"]):x for x in ref["per_site_type_pair"]}
    if len(legacy)!=90 or set(original_sites)!={r["site"] for r in ref["source_site_block_qc"]}:
        raise AssertionError("Frozen source site/pair manifest changed")
    source_quality=[];all_site_pairs=[];all_year_pairs=[]
    for site,record in sorted(original_sites.items()):
        eff=record["nominal"]-record["off"]-record["noise"]
        complete=eligible_complete_days(eff)
        runs=contiguous_runs(complete)
        site_source=sum(24*len(run) for run in runs)
        rsite=next(r for r in ref["source_site_block_qc"] if r["site"]==site)
        if site_source!=rsite["selected_source_eligible_hours"] or len(runs)!=rsite["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("Strict original 7+ day source hours/blocks drift")
        by_type={t:record["fish"].get(t,set()) for t in TYPES}
        site_agg={p:empty_agg() for p in PAIRS}
        year_agg=defaultdict(lambda:{p:empty_agg() for p in PAIRS})
        hours_regime={name:0 for name in STRATA}
        for run in runs:
            day_masks=[regime_masks(site,complete[d]) for d in run]
            yr=run[0].year
            if any(d.year!=yr or d.month!=run[0].month for d in run):
                raise AssertionError("Year/month break within v145 contiguous run")
            for day_mask in day_masks:
                for name in STRATA:
                    hours_regime[name]+=day_mask[name].bit_count()
            daily={typ:[hour_mask(complete[d],by_type[typ]) for d in run] for typ in TYPES}
            for a,b in PAIRS:
                scores=exact_rotations(daily[a],daily[b],day_masks)
                add_to(site_agg[(a,b)],scores)
                add_to(year_agg[yr][(a,b)],scores)
        oldsite=next(r for r in prior["source_sites"] if r["site"]==site)
        if hours_regime["dawn_transition"]+hours_regime["dusk_transition"]!=oldsite["opportunity_hours"]["solar_transition_adjacent_no_wrap"]:
            raise AssertionError("v151 solar transition source hours changed")
        if hours_regime["stable_day"]+hours_regime["stable_night"]!=oldsite["opportunity_hours"]["solar_stable_no_wrap"]:
            raise AssertionError("v151 solar stable source hours changed")
        if hours_regime["midnight_legacy"]!=oldsite["opportunity_hours"]["midnight_wrap_four_hours"]:
            raise AssertionError("v151 midnight source hours changed")
        if sum(hours_regime.values())!=site_source:
            raise AssertionError("Some actual original source hours lost in solar masks")
        source_quality.append({
            "site":site,"source_hours":site_source,
            "n_consecutive_local_yearmonth_runs":len(runs),
            "source_years":sorted(year_agg),
            "source_hour_opportunities_by_solar_category":hours_regime,
        })
        for a,b in PAIRS:
            old=legacy[(site,a,b)]
            agg=site_agg[(a,b)]
            O=sum(agg[name]["O"] for name in STRATA)
            E=math.fsum(agg[name]["E"] for name in STRATA)
            if O!=old["observed_same_hour_chorusing_in_retained_blocks"]:
                raise AssertionError("Original v145 O not preserved in solar regime panels")
            if abs(E-old["exact_shift_null_expected_same_hour_hours"])>0.000035:
                raise AssertionError("Original v145 E not preserved in solar regime panels")
            entry={"site":site,"A":a,"B":b,"v145_screened":old["status"]=="SCREENED_RESTRICTED_SHIFT_NULL",
                   "O_original_all24h":O,"E_original_v145_shift":round(E,8),
                   "panel":summary_panel(agg)}
            all_site_pairs.append(entry)
            relevant_years=[]
            for year in sorted(year_agg):
                v=year_agg[year][(a,b)]
                relevant_years.append((year,v))
                all_year_pairs.append({"site":site,"local_year":year,"A":a,"B":b,
                                       "panel":summary_panel(v)})
            for name in STRATA:
                if sum(y[name]["O"] for _,y in relevant_years)!=agg[name]["O"]:
                    raise AssertionError("Calendar year O decomposition failed")
                if abs(math.fsum(y[name]["E"] for _,y in relevant_years)-agg[name]["E"])>1e-6:
                    raise AssertionError("Calendar year E decomposition failed")
    if len(source_quality)!=9 or len(all_site_pairs)!=90 or len(all_year_pairs)!=320:
        raise AssertionError("Original source site and time unit scope failed")
    site_total=sum(z["source_hours"] for z in source_quality)
    if site_total!=136032:raise AssertionError("Old source 136032 hours drift")
    totals={name:sum(z["source_hour_opportunities_by_solar_category"][name] for z in source_quality) for name in STRATA}
    if (totals["dawn_transition"]+totals["dusk_transition"]!=45269 or
        totals["stable_night"]+totals["stable_day"]!=68091 or
        totals["midnight_legacy"]!=22672):
        raise AssertionError("v151 exact source opportunity partition failed")
    # Same original A×B observations in v151 for every previously shown panel.
    for b in ("UF440","White Seabass"):
        for previous in prior["posthoc_known_pair_focus"][b]["sites_data"]:
            actual=next(z for z in all_site_pairs if z["site"]==previous["site"] and z["A"]=="Bocaccio" and z["B"]==b)
            p=actual["panel"]
            if (p["dawn_transition"]["O"]+p["dusk_transition"]["O"]!=previous["solar_transition"]["O"] or
                p["stable_day"]["O"]+p["stable_night"]["O"]!=previous["stable_solar"]["O"] or
                p["midnight_legacy"]["O"]!=previous["midnight_wrap"]["O"]):
                raise AssertionError("v151 exact observed solar partition changed")
    focus={}
    for b in ("UF440","White Seabass"):
        candidates=[z for z in all_site_pairs if z["A"]=="Bocaccio" and z["B"]==b and z["v145_screened"]]
        focus[b]={
            "n_sites_v145_source_screened":len(candidates),
            "n_site_positive_excess_by_regime":{name:sum(
                z["panel"][name]["O_minus_E"]>0 for z in candidates) for name in STRATA},
            "site_results":[{
                "site":z["site"],
                "original_all_day":{key:z[key] for key in ("O_original_all24h","E_original_v145_shift")},
                "regimes":z["panel"]
            } for z in candidates],
        }
    full={
        "version":"v152_genuine_24h_day_shift_solar_transition_strata_1",
        "original_all_60_individual_SHA256_verified":True,
        "source_scope":{"sites":9,"site_years":32,"site_chorus_pairs":90,
                        "annual_site_chorus_pairs":320,"recording_hours":site_total,
                        "consecutive_full_day_yearmonth_runs":275},
        "solar_regimes":list(STRATA),
        "same_local_clock_and_bout_preserving_day_shift":True,
        "whole_day_solar_category_from_station_specific_astronomical_altitude":True,
        "shift_null_is_clock_month_conditioned_not_environment_conditioned":True,
        "new_shift_p_values_not_computed":True,
        "data_dependent_pair_focus_from_v145_v151":True,
        "acoustic_source_hour_not_independent_fish":True,
        "source_qc_by_site":source_quality,
        "source_recording_hours_by_regime":totals,
        "all90_site_pair_results":all_site_pairs,
        "all320_year_pair_results":all_year_pairs,
        "posthoc_pair_focus":focus,
        "physical_tide_solar_effect":"NOT_ESTIMATED",
        "independent_coast_study_meta_effect":"NOT_ESTIMATED",
        "direct_social_boids_effect":"NOT_IDENTIFIED",
    }
    canonical=json.dumps(full,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    receipt={
        "version":full["version"],
        "source_verified_all_60_individual_sha256":True,
        "full_original_source_aggregate_sha256":hashlib.sha256(canonical.encode()).hexdigest(),
        "full_original_source_aggregate_bytes":len(canonical.encode()),
        "scope":full["source_scope"],
        "source_recording_hours_by_regime":totals,
        "posthoc_pair_focus":focus,
        "no_new_statistical_p_values":True,
        "no_direct_fish_social_or_causal_tide_sun":True,
        "independent_biological_coasts_added":0,
        "tide_by_solar_meta":"NOT_ESTIMATED",
    }
    return full,receipt

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    full,receipt=one_source()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("No original-verified frozen v152 receipt")
        old=json.loads(RECEIPT.read_text())
        if old!=receipt:
            changed=[k for k in sorted(set(old)|set(receipt)) if old.get(k)!=receipt.get(k)]
            raise AssertionError("Original-source v152 SHA/result changed "+repr(changed))
        print("V152_ALL_60_MEMBER_SHA_REPLAY_PASS")
    else:
        print("V152_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,ensure_ascii=True,sort_keys=True,separators=(",",":")))
        print("V152_SOURCE_RECEIPT_END")
    print("V152_SOURCE_SCOPE="+json.dumps(receipt["scope"],sort_keys=True))

if __name__=="__main__":main()
