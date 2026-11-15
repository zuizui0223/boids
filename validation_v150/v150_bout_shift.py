"""v150: same-local-day +/-1/2h acoustic shifted-partner negative controls.

This diagnostic preserves each recorded source day, original presence bouts,
all original fish-chorus positive hours, nominal source effort, local dates,
and local dark/light states in eligible central hours. Only evaluate 02:00-21:00
focal hours for which the solar night/day label does not change under ALL
+/-1h or +/-2h offsets. No wrapping across midnight and no extrapolation.

IMPORTANT: ±1h/±2h signed offsets are DESCRIPTIVE alternatives, not an
exchangeable p-value distribution and not individual fish social behavior.
"""
from __future__ import annotations

import argparse, hashlib, json, sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v145"))
sys.path.insert(0,str(ROOT/"validation_v144"))
from v145_blockshift import original, eligible_complete_days, contiguous_runs, hour_mask, TYPES
from full9_temporal import sun_alt

V145=ROOT/"validation_v145/results/source_blockshift_cochorus_null.json"
RECEIPT=ROOT/"validation_v150/results/frozen_source_receipt_v150.json"
FULL=ROOT/"validation_v150/results/source_boutshift_full_v150.json"
PAIRS=tuple(combinations(TYPES,2))
OFFSETS=(-2,-1,1,2)
NIGHT_SUN=-0.833
DAY_MASK=(1<<24)-1

def beginnings(mask):
    """Source hourly 0->1 transitions, first hour not scored in this diagnostic."""
    return (mask & ~(mask<<1)) & DAY_MASK

def safe_central_hours(light_binary):
    """Both current time and all four offsets have the same daylight class."""
    if len(light_binary)!=24:raise ValueError("24 local calendar-hour solar flags required")
    return tuple(h for h in range(2,22) if len({light_binary[h+k] for k in (-2,-1,0,1,2)})==1)

def shifts_for_day(a,b,center_hours):
    """Exact observed + four +/- offset acoustic coincidences, no wrap."""
    if not all(2<=h<=21 for h in center_hours):raise ValueError("Unsafe local-time edges")
    z=[]
    for lag in (0,)+OFFSETS:
        z.append(sum(bool(a&(1<<h)) and bool(b&(1<<(h+lag))) for h in center_hours))
    return z

def summarize_site(site,item):
    eff=item["nominal"]-item["off"]-item["noise"]
    complete=eligible_complete_days(eff)
    runs=contiguous_runs(complete)
    source_days=[d for r in runs for d in r]
    rows_by_year=defaultdict(lambda:{key:{"presence":[0]*5,"onset":[0]*5}
                                    for key in PAIRS})
    site_hours=0
    subset_hours=0
    by_year_eligible=defaultdict(lambda:{"days":0,"source24h":0,"center_same_solar":0,
                                        "center_night":0,"center_day":0})
    for day in source_days:
        hours=complete[day]
        if len(hours)!=24:raise AssertionError("Missing full original local solar day")
        flags=[sun_alt(site,h)<NIGHT_SUN for h in hours]
        center=safe_central_hours(flags)
        selected={t:hour_mask(hours,item["fish"].get(t,set())) for t in TYPES}
        onset={t:beginnings(selected[t]) for t in TYPES}
        info=by_year_eligible[day.year]
        info["days"]+=1
        info["source24h"]+=24
        info["center_same_solar"]+=len(center)
        info["center_night"]+=sum(flags[h] for h in center)
        info["center_day"]+=sum(not flags[h] for h in center)
        site_hours+=24
        subset_hours+=len(center)
        for a,b in PAIRS:
            dest=rows_by_year[day.year][(a,b)]
            pres=shifts_for_day(selected[a],selected[b],center)
            ons=shifts_for_day(onset[a],onset[b],center)
            for i in range(5):
                dest["presence"][i]+=pres[i]
                dest["onset"][i]+=ons[i]
    year_pairs=[]
    site_pairs=[]
    for year in sorted(rows_by_year):
        for (a,b),v in sorted(rows_by_year[year].items()):
            pp=v["presence"]; oo=v["onset"]
            year_pairs.append({
                "site":site,"year":year,"A":a,"B":b,
                "presence_O":pp[0],
                "presence_shifted_sum_four":sum(pp[1:]),
                "onset_O":oo[0],
                "onset_shifted_sum_four":sum(oo[1:]),
            })
    for a,b in PAIRS:
        yy=[r for r in year_pairs if r["A"]==a and r["B"]==b]
        if not yy:raise AssertionError("Site has no source years")
        presO=sum(x["presence_O"] for x in yy)
        presQ=sum(x["presence_shifted_sum_four"] for x in yy)
        onsetO=sum(x["onset_O"] for x in yy)
        onsetQ=sum(x["onset_shifted_sum_four"] for x in yy)
        site_pairs.append({
            "site":site,"A":a,"B":b,
            "presence_O":presO,
            "presence_shift_control_mean":presQ/4,
            "presence_OE":round(4*presO/presQ,6) if presQ else None,
            "onset_O":onsetO,
            "onset_shift_control_mean":onsetQ/4,
            "onset_OE":round(4*onsetO/onsetQ,6) if onsetQ else None,
            "source_years":len(rows_by_year),
        })
    return {"site":site,"n_source_days":len(source_days),"n_7d_run_blocks":len(runs),
            "n_original_24h_source_hours":site_hours,"n_safe_same_solar_center_hours":subset_hours,
            "source_years":sorted(rows_by_year),
            "annual_hours":[{"year":year,**x} for year,x in sorted(by_year_eligible.items())]
            },site_pairs,year_pairs

def analyze():
    frozen=json.loads(V145.read_text())
    if frozen["sites"]!=9 or frozen["screened_site_pairs"]!=32 or not frozen["source_original_workbook_SHA_verified_all_60"]:
        raise AssertionError("frozen original v145 source drift")
    source=original()
    assert set(source)=={r["site"] for r in frozen["source_site_block_qc"]}
    site_quality=[];pairs=[];years=[]
    for site,item in sorted(source.items()):
        quality,one,y=summarize_site(site,item)
        ref=next(r for r in frozen["source_site_block_qc"] if r["site"]==site)
        if quality["n_original_24h_source_hours"]!=ref["selected_source_eligible_hours"]:
            raise AssertionError("v145 original observed opportunity mismatch")
        if quality["n_7d_run_blocks"]!=ref["continuous_local_yearmonth_run_blocks_7days_plus"]:
            raise AssertionError("v145 source original run count changed")
        site_quality.append(quality);pairs.extend(one);years.extend(y)
    if len(pairs)!=90 or len(years)!=320:
        raise AssertionError("All site/type pairs and original year pairs required")
    if sum(x["n_original_24h_source_hours"] for x in site_quality)!=136032:
        raise AssertionError("v145 original 136032 source hours changed")
    if sum(x["n_7d_run_blocks"] for x in site_quality)!=275:
        raise AssertionError("v145 original source blocks changed")
    old_pair={(r["site"],r["chorus_A"],r["chorus_B"]):r
              for r in frozen["per_site_type_pair"]}
    if len(old_pair)!=90:raise AssertionError("original 90 pairs required")
    for row in pairs:
        r=old_pair[(row["site"],row["A"],row["B"])]
        row["v145_screened"]=r["status"]=="SCREENED_RESTRICTED_SHIFT_NULL"
        row["v145_all_hours_O"]=r["observed_same_hour_chorusing_in_retained_blocks"]
        row["v145_all_hours_OE"]=r["shift_null"]["observed_over_shift_expectation"] if r["shift_null"] else None
        if row["presence_O"]>row["v145_all_hours_O"]:
            raise AssertionError("Filtered subset observed O exceeds full original O")
    focus={}
    for b in ("UF440","White Seabass"):
        q=[r for r in pairs if r["A"]=="Bocaccio" and r["B"]==b and r["v145_screened"]]
        focus[b]={
            "sites":len(q),
            "presence_OE_above_one":sum(r["presence_OE"] is not None and r["presence_OE"]>1 for r in q),
            "onset_OE_above_one":sum(r["onset_OE"] is not None and r["onset_OE"]>1 for r in q),
            "site_rows":[{"site":x["site"],"narrow_presence_O":x["presence_O"],
                          "shifted_presence_expected":x["presence_shift_control_mean"],
                          "narrow_presence_OE":x["presence_OE"],
                          "narrow_onset_O":x["onset_O"],
                          "shifted_onset_expected":x["onset_shift_control_mean"],
                          "narrow_onset_OE":x["onset_OE"],
                          "all24h_v145_OE":x["v145_all_hours_OE"]}
                         for x in q]
        }
    full={
        "version":"v150_original_24h_day_profile_plusminus_2h_without_diel_flip_1",
        "source_verified_all_60_original_files":True,
        "central_source_restrict_hours":list(range(2,22)),
        "signed_hour_shift_controls":list(OFFSETS),
        "date_and_same_astronomical_daylight_class_held_fixed":True,
        "all_shift_comparisons_preserve_daily_call_bouts_except_no_wrap_boundaries":True,
        "observation_unit":"annotated 1h positive source-acoustic types, not identified animal individuals",
        "time_shift_control_not_exchangeable_statistical_null":True,
        "night_flag_degrees":NIGHT_SUN,
        "source_sites":site_quality,
        "all_90_original_site_pair_results":pairs,
        "all_320_original_site_year_pair_results":years,
        "already_seen_bocaccio_pairs_posthoc_focus":focus,
        "n_original_sites":len(site_quality),
        "n_original_siteyears":sum(len(x["source_years"]) for x in site_quality),
        "source_complete_local_day_hours":sum(x["n_original_24h_source_hours"] for x in site_quality),
        "source_solar_safe_shift_hours":sum(x["n_safe_same_solar_center_hours"] for x in site_quality),
        "meta_admissible_independent_new_coasts":0,
        "physical_tide_solar_effect":"NOT_ESTIMATED",
        "fish_social_boids":"NOT_IDENTIFIED",
    }
    canon=json.dumps(full,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    receipt={
        "version":full["version"],
        "full_source_canonical_sha256":hashlib.sha256(canon.encode()).hexdigest(),
        "full_source_canonical_json_bytes":len(canon.encode()),
        "n_original_sites":full["n_original_sites"],
        "n_original_siteyears":full["n_original_siteyears"],
        "source_complete_local_day_hours":full["source_complete_local_day_hours"],
        "source_solar_safe_shift_hours":full["source_solar_safe_shift_hours"],
        "site_quality":site_quality,
        "target_pair_focus_posthoc":focus,
        "source_verified_all_60_original_files":True,
        "no_new_p_values":True,
        "independent_biological_coasts_added":0,
        "physical_tide_solar_effect":"NOT_ESTIMATED",
        "social_boids":"NOT_IDENTIFIED"}
    return full,receipt

def main():
    p=argparse.ArgumentParser()
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--emit",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=p.parse_args()
    full,receipt=analyze()
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("Frozen authenticated source receipt missing")
        saved=json.loads(RECEIPT.read_text())
        if receipt!=saved:
            diff=[k for k in sorted(set(saved)|set(receipt)) if saved.get(k)!=receipt.get(k)]
            raise AssertionError("Original source and numeric fingerprint changed: "+repr(diff))
        print("V150_FULL_SOURCE_CRYPTOGRAPHIC_REPLAY_SUCCESS")
    else:
        print("V150_SOURCE_RECEIPT_START")
        print(json.dumps(receipt,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V150_SOURCE_RECEIPT_END")
    print("V150_SCOPE_AND_FOCUS_START")
    print(json.dumps({"source_complete_local_day_hours":receipt["source_complete_local_day_hours"],
                      "source_solar_safe_shift_hours":receipt["source_solar_safe_shift_hours"],
                      "target_pair_focus_posthoc":receipt["target_pair_focus_posthoc"]},
                     ensure_ascii=True,sort_keys=True))
    print("V150_SCOPE_AND_FOCUS_END")

if __name__=="__main__":main()
