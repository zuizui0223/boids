"""v144: true original-source 9-site diel fish choruses and season/hour conditional overlap.

Source unit = deployed recorder-hour. No-events mean no MANUALLY LOGGED CHORUS
in a nominal source effort hour, not confirmed absence of fish or audibility.
Paired chorusing overlap O/E is a conditional opportunity *descriptive*
null, not an acoustic social interaction test with independent p-values.
"""
from __future__ import annotations
import argparse, io, json, math, sys, zipfile
from collections import Counter, defaultdict
from datetime import datetime,timedelta,timezone
from functools import lru_cache
from itertools import combinations
from hashlib import sha256
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v142"))
from chorus_60_source_audit import acquire, excel_reader, extract_sheet, numeric_excel, PUBLISHED
from masking_corrections import source_label, overlapping_hours, fully_inside_hours
from site_gauge_distance import SITES
from astral import Observer
from astral.sun import elevation

TYPES=tuple(PUBLISHED)
TZ=ZoneInfo("America/Los_Angeles")
EPOCH=datetime(1899,12,30,tzinfo=timezone.utc)
CUTS=(-0.833,-6.0)

@lru_cache(maxsize=300000)
def local_time(h):
    return (EPOCH+timedelta(hours=h+.5)).astimezone(TZ)

@lru_cache(maxsize=300000)
def sun_alt(site,h):
    geo=SITES[site]
    return elevation(Observer(latitude=geo["lat"],longitude=geo["lon"]),
                     EPOCH+timedelta(hours=h+.5))

def original():
    saved=json.loads((ROOT/"validation_v142/results/all_60_chorus_original_source_audit.json").read_text())
    original_sha={r["file"]:r["sha256"] for r in saved["per_file_quality"]}
    if len(original_sha)!=60:raise AssertionError("60 source SHA manifests required")
    raw=acquire()
    sites={site:{"n_deployments":0, "nominal":set(),"off":set(),"noise":set(),
                 "fish":defaultdict(set),"raw_labels":Counter(),"bad_timestamp_rows":0}
           for site in SITES}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members={n for n in z.namelist() if n.endswith((".xls",".xlsx"))}
        if members!=set(original_sha):raise AssertionError("Original source members changed")
        for name in sorted(members):
            buf=z.read(name)
            if sha256(buf).hexdigest()!=original_sha[name]:
                raise AssertionError("Original individual workbook SHA differs: "+name)
            site=name.split("_")[0]
            item=sites[site]
            tabs=excel_reader(buf,name)
            D,dc=extract_sheet(tabs,"Detections")
            M,mc=extract_sheet(tabs,"MetaData")
            eligible=set()
            for row in M[1:]:
                a=numeric_excel(row[mc["start"]] if len(row)>mc["start"] else None)
                b=numeric_excel(row[mc["end"]] if len(row)>mc["end"] else None)
                if a is not None and b is not None and b>a:
                    eligible.update(fully_inside_hours(a,b))
            if not eligible:raise AssertionError("No source deployment effort: "+name)
            item["nominal"].update(eligible)
            item["n_deployments"]+=1
            for row in D[1:]:
                a=numeric_excel(row[dc["start"]] if len(row)>dc["start"] else None)
                b=numeric_excel(row[dc["end"]] if len(row)>dc["end"] else None)
                if a is None and b is None:continue
                if a is None or b is None or b<=a or b-a>100:
                    item["bad_timestamp_rows"]+=1;continue
                label=row[dc["label"]] if len(row)>dc["label"] else ""
                group,_=source_label(label)
                hh=overlapping_hours(a,b)&eligible
                if not hh:continue
                item["raw_labels"][group]+=1
                if group in TYPES:item["fish"][group].update(hh)
                elif group=="OFF_EFFORT":item["off"].update(hh)
                elif group=="SOURCE_NOISE":item["noise"].update(hh)
    if sum(r["n_deployments"] for r in sites.values())!=60:
        raise AssertionError("Incomplete 60 source deployments")
    return sites

def diel_counts(site,eff,positive,cut):
    dark={h for h in eff if sun_alt(site,h)<cut}
    day=eff-dark
    n=len(positive&dark);d=len(positive&day)
    N=len(dark);D=len(day)
    return {
        "night_eligible_hours":N, "day_eligible_hours":D,
        "night_positive_hours":n, "day_positive_hours":d,
        "night_fraction":round(n/N,7) if N else None,
        "day_fraction":round(d/D,7) if D else None,
        "night_minus_day":round(n/N-d/D,7) if N and D else None,
        "night_day_ratio":round((n/N)/(d/D),5) if N and D and d else None,
        "positive_day_and_night":n>0 and d>0,
    }

def conditional_overlap(eff, a, b, group):
    data=defaultdict(lambda:[0,0,0,0])
    for h in eff:
        q=data[group(h)]
        q[0]+=1
        A=h in a;B=h in b
        q[1]+=int(A);q[2]+=int(B);q[3]+=int(A and B)
    observed=sum(q[3] for q in data.values())
    expected=sum(q[1]*q[2]/q[0] for q in data.values())
    return observed,expected,len(data)

def calculate():
    sources=original()
    output={
      "version":"v144_full9_2018_2023_time_niche_and_conditional_cochorus_v1",
      "original_primary_doi":"10.3354/meps14910",
      "original_repository_doi":"10.5061/dryad.q2bvq83sw",
      "original_60_member_sha256_verified":True,
      "n_sites":9,"n_original_deployments":60,
      "local_month_hour_timezone":"America/Los_Angeles (DST applied)",
      "solar_thresholds_degrees":list(CUTS),
      "night_definition":"sun center-of-UTC-hour altitude < threshold at original site",
      "source_effort_is_nominal_not_verified_audible":True,
      "full9_site_effort":[],
      "site_chorus_diel":[],
      "yearmonth_site_chorus":[],
      "cochorus_pairs":[],
      "pooled_physical_tide_solar_effect":"NOT_ESTIMATED",
      "source_published_overall_percent_reproduction":"STILL_UNRESOLVED",
      "fish_individual_behavior":"NOT_ESTIMATED"}
    all_hrs=Counter()
    for site,v in sorted(sources.items()):
        nominal=v["nominal"]
        filtered=nominal-v["off"]-v["noise"]
        off=v["off"]&nominal;noise=v["noise"]&nominal
        all_hrs["nominal"]+=len(nominal)
        all_hrs["exclude_off"]+=len(nominal-off)
        all_hrs["exclude_off_and_noise"]+=len(filtered)
        output["full9_site_effort"].append({
          "site":site,"sanctuary":SITES[site]["sanctuary"],
          "source_deployments":v["n_deployments"],
          "nominal_UTC_hours":len(nominal),
          "off_overlap_hours":len(off),"noise_overlap_hours":len(noise),
          "after_off_noise_hours":len(filtered),
          "bad_source_timestamp_rows":v["bad_timestamp_rows"],
          "no_complete_audibility_series":True,
        })
        pos={typ:v["fish"].get(typ,set()) & filtered for typ in TYPES}
        for typ in TYPES:
            p=pos[typ]
            output["site_chorus_diel"].append({
                "site":site,"sanctuary":SITES[site]["sanctuary"],
                "chorus_type":typ,"eligible_hours":len(filtered),
                "annotated_positive_hours":len(p),
                "fraction_positive":round(len(p)/len(filtered),7),
                "diel":{str(c):diel_counts(site,filtered,p,c) for c in CUTS},
            })
        yearmonth=defaultdict(set)
        m_clock={}
        for h in filtered:
            dt=local_time(h)
            yearmonth[(dt.year,dt.month)].add(h)
            m_clock[h]=(dt.month,dt.hour)
        for (year,month),hours in sorted(yearmonth.items()):
            night={h for h in hours if sun_alt(site,h)<CUTS[0]}
            day=hours-night
            output["yearmonth_site_chorus"].append({
                "site":site,"sanctuary":SITES[site]["sanctuary"],
                "local_year":year,"local_month":month,
                "eligible_hours":len(hours),
                "night_hours":len(night),"day_hours":len(day),
                "positive_by_type":{typ:{
                   "total":len(pos[typ]&hours),
                   "night":len(pos[typ]&night),"day":len(pos[typ]&day),
                   "fraction":round(len(pos[typ]&hours)/len(hours),7)
                } for typ in TYPES},
            })
        yearmonth_clock={h:(local_time(h).year,local_time(h).month,local_time(h).hour) for h in filtered}
        date_diel={h:(local_time(h).date().isoformat(),int(sun_alt(site,h)<CUTS[0])) for h in filtered}
        for A,B in combinations(TYPES,2):
            a=pos[A];b=pos[B]
            observed,base_ex,_=conditional_overlap(filtered,a,b,lambda h:0)
            another,expected,nstrata=conditional_overlap(filtered,a,b,lambda h:m_clock[h])
            oy,exy,ny=conditional_overlap(filtered,a,b,lambda h:yearmonth_clock[h])
            od,exd,nd=conditional_overlap(filtered,a,b,lambda h:date_diel[h])
            if len({observed,another,oy,od})!=1:
                raise AssertionError("Changing conditional null must not change observed overlap")
            output["cochorus_pairs"].append({
                "site":site,"sanctuary":SITES[site]["sanctuary"],
                "type_A":A,"type_B":B,"eligible_hours":len(filtered),
                "A_positive_hours":len(a),"B_positive_hours":len(b),
                "same_hour_positive_for_both":observed,
                "global_unstratified_overlap_expectation":round(base_ex,4),
                "month_x_local_clock_hour_expected_overlap":round(expected,4),
                "observed_to_conditional_expected":round(observed/expected,5) if expected>0 else None,
                "conditioning_strata":nstrata,
                "yearmonth_x_local_clock_hour_expected_overlap":round(exy,4),
                "observed_over_yearmonth_clock_expected":round(observed/exy,5) if exy>0 else None,
                "yearmonth_clock_strata":ny,
                "source_local_date_x_astronomical_diel_expected_overlap":round(exd,4),
                "observed_over_date_diel_expected":round(observed/exd,5) if exd>0 else None,
                "date_diel_strata":nd,
                "screen_eligible":len(a)>=50 and len(b)>=50 and expected>=10,
                "statistical_p_value":"NOT_COMPUTED",
                "coordinated_behavior_claim":"NOT_INFERABLE_FROM_COINCIDENCE",
            })
    output["all_9site_effort_totals"]=dict(all_hrs)
    if output["all_9site_effort_totals"]!={"nominal":160166,"exclude_off":158012,"exclude_off_and_noise":155871}:
        raise AssertionError("Original 9-site source hours diverge from v142")
    if len(output["site_chorus_diel"])!=45 or len(output["cochorus_pairs"])!=90:
        raise AssertionError("Missing 9x5 or 9x10 original report cells")
    summary={}
    for typ in TYPES:
        rows=[r for r in output["site_chorus_diel"] if r["chorus_type"]==typ]
        supported=[r for r in rows if r["diel"][str(CUTS[0])]["positive_day_and_night"]]
        summary[typ]={
            "sites_with_any_original_chorus":sum(r["annotated_positive_hours"]>0 for r in rows),
            "sites_positive_in_both_daynight":len(supported),
            "sites_night_fraction_higher":sum(r["diel"][str(CUTS[0])]["night_minus_day"]>0 for r in supported),
            "sites_day_fraction_higher":sum(r["diel"][str(CUTS[0])]["night_minus_day"]<0 for r in supported),
            "night_day_ratios_nonzero_day_sites":{r["site"]:r["diel"][str(CUTS[0])]["night_day_ratio"]
                                                   for r in supported},
        }
    output["by_chorus_diel_summary"]=summary
    output["conditional_cochorus_summary"]={}
    for A,B in combinations(TYPES,2):
        rows=[x for x in output["cochorus_pairs"] if x["type_A"]==A and x["type_B"]==B and x["screen_eligible"]]
        output["conditional_cochorus_summary"][A+" | "+B]={
          "eligible_sites":len(rows),
          "sites_excess_positive":sum(x["same_hour_positive_for_both"]>x["month_x_local_clock_hour_expected_overlap"] for x in rows),
          "sites_excess_negative":sum(x["same_hour_positive_for_both"]<x["month_x_local_clock_hour_expected_overlap"] for x in rows),
          "per_site_O_over_E":{r["site"]:r["observed_to_conditional_expected"] for r in rows},
          "effect_and_statistical_independence":"NOT_ESTIMATED",
        }
    return output

def compact(r):
    copy={k:v for k,v in r.items() if k!="yearmonth_site_chorus"}
    copy["site_yearmonth_records"]=len(r["yearmonth_site_chorus"])
    return copy

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--check",action="store_true")
    args=a.parse_args()
    res=calculate()
    dest=Path(__file__).parent/"results"
    dest.mkdir(parents=True,exist_ok=True)
    core=compact(res)
    if args.check:
        if core!=json.loads((dest/"source_full9_core.json").read_text()):
            raise AssertionError("Frozen original member results differ from regenerated full9 source")
    else:
        (dest/"source_full9_core.json").write_text(json.dumps(core,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    monthly_path=dest/"source_full9_monthly.json"
    if args.check:
        if res["yearmonth_site_chorus"]!=json.loads(monthly_path.read_text()):
            raise AssertionError("Frozen monthly source results changed")
    else:
        monthly_path.write_text(json.dumps(res["yearmonth_site_chorus"],indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    print("V144_MONTHLY_START")
    print(json.dumps(res["yearmonth_site_chorus"],ensure_ascii=False))
    print("V144_MONTHLY_END")
    print("V144_ORIGINAL_FULL9_START")
    print(json.dumps(core,ensure_ascii=False))
    print("V144_ORIGINAL_FULL9_END")

if __name__=="__main__":main()
