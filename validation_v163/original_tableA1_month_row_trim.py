"""v163 original 43-SITE porpoise source quality alternative:
retain ONLY Data S2 source records within PUBLISHED Table A1 source site
start/end YEAR-MONTH, rather than exclude an entire SITE when any row
is outside the published date range (v162 extreme conservative).

This is an exploratory source sensitivity AFTER knowing v160-v162 model
results. It does not resolve whether Data S2 records outside Table A1 are
miscoded or simply use additional deployments. Do not replace original
published source data or declare mismatching observations biologically false.

CRITICAL: clip individual ORIGINAL click-positive hours BEFORE making t-1
or t-24 source pairs. Thus no phantom history crosses discarded times.
Reuse source/response positivity gate, C=.25 original v160 geographic
and v161 strictly earlier calendar-year heldouts without retuning.

Response = buzz positive GIVEN an actually detected click-positive hour.
The same-hour click count is used in all candidate models, so the
experiment is retrospective conditional classification, not an
independent prevalence or prospective ecological forecast.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,sys
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for directory in ("validation_v158","validation_v159","validation_v160","validation_v161","validation_v162"):
    sys.path.insert(0,str(ROOT/directory))
from porpoise_source_gate import acquire
from site_hour_integrity import as_int,iso_weekday_source_ordinal
from porpoise_site_holdout import (
    fixed_features,evaluate as geographic_evaluate,summary as geographic_summary
)
from porpoise_temporal_holdout import (
    source_year,evaluate as temporal_evaluate,summarize as temporal_summary
)
from paper_tableA1_source_consistency import published_tableA1
ORIGINAL_SHA="972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf"
V162=ROOT/"validation_v162/results/frozen_published_metadata_receipt_v162.json"
V160=ROOT/"validation_v160/results/frozen_source_receipt_v160.json"
V161=ROOT/"validation_v161/results/frozen_temporal_source_receipt_v161.json"
FULL=ROOT/"validation_v163/results/paper_date_record_trim_original_v163.json"
RECEIPT=ROOT/"validation_v163/results/frozen_record_trim_receipt_v163.json"
SOURCE_TOTAL_EXPECTED=126231
PAPER_OUT_OF_MONTH_ROWS_EXPECTED=20315
SOURCE_RETAINED_EXPECTED=105916
REGIONS=("BHB","FRANORTH","FRASOUTH","ICE","RWB","SWE")

def exact_datetime(y,d,h):
    hour=iso_weekday_source_ordinal(y,d,h)
    if hour is None:raise AssertionError("original source year/day/hour invalid")
    return datetime(y,1,1)+timedelta(days=d-1,hours=h)

def generate_pairs():
    prior=json.loads(V162.read_text())
    v160=json.loads(V160.read_text())
    v161=json.loads(V161.read_text())
    if (prior["source_metadata_consistency"]["source_site_ids_flagged_any_outside_published_monthyear"]!=6
        or prior["source_metadata_consistency"]["source_rows_outside_monthyear"]!=20315
        or v160["n_primary_sites_evaluated"]!=21
        or v161["n_primary_site_years_fitted"]!=15):
        raise AssertionError("Source upstream frozen Table A1/transfer results changed")
    pub=published_tableA1()
    if len(pub)!=43:raise AssertionError("Published Table A1 not 43 site identities")
    raw, meta=acquire()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA or len(raw)!=26454371:
        raise AssertionError("Original Data S2 member SHA256/bytes changed")
    source_count=0
    trimmed=0
    site_raw=defaultdict(int)
    site_trim=defaultdict(int)
    site_clip=defaultdict(dict)
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline="")):
        source_count+=1
        site=row["SITE"].strip()
        group=row["GROUP"].strip()
        if site not in pub or pub[site][0]!=group:
            raise AssertionError("Original source site/group differs from published Table A1")
        year=as_int(row["year"]);yday=as_int(row["YDAY"]);hh=as_int(row["hr"])
        dt=exact_datetime(year,yday,hh)
        month=(dt.year,dt.month)
        clicks=as_int(row["clicks"]);buzz=as_int(row["buzz"])
        if clicks is None or clicks<=0 or buzz is None or buzz<0 or buzz>clicks:
            raise AssertionError("Original click/buzz source count invalid")
        site_raw[site]+=1
        if not (pub[site][1]<=month<=pub[site][2]):
            trimmed+=1
            site_trim[site]+=1
            continue
        key=iso_weekday_source_ordinal(year,yday,hh)
        if key in site_clip[site]:raise AssertionError("Clipped original duplicate source hour")
        site_clip[site][key]=(year,yday,hh,clicks,buzz)
    if (source_count!=SOURCE_TOTAL_EXPECTED or trimmed!=PAPER_OUT_OF_MONTH_ROWS_EXPECTED
        or sum(map(len,site_clip.values()))!=SOURCE_RETAINED_EXPECTED
        or len(site_raw)!=43 or len(site_clip)!=43):
        raise AssertionError("Original Table A1 row-level provenance totals mismatch")
    meta_flags=prior["source_metadata_consistency"]["flagged_source_SITE_labels"]
    if set(meta_flags)!={z for z in site_raw if site_trim[z]>0}:
        raise AssertionError("Six original source metadata discrepancy sites changed")
    bygroup=defaultdict(list)
    site_qc=[]
    total_pairs=0;total_day24=0
    for site,info in sorted(pub.items()):
        group=info[0]
        sourcehours=site_clip[site]
        prevcount=0;daycount=0
        for k,now in sorted(sourcehours.items()):
            before=sourcehours.get(k-1)
            if before is None:continue
            if now[2]!=(before[2]+1)%24:
                raise AssertionError("Clipped 1h pair not adjacent original source hour")
            yr,yd,hh,clicks,buzz=now
            base,lag=fixed_features(yr,yd,hh,clicks,before[3])
            day24=sourcehours.get(k-24)
            bygroup[group].append({
                "SITE":site,
                "Y":int(buzz>0),
                "C1":base,
                "C2":lag,
                "C3":[*lag,int(before[4]>0)],
                "G24":int(day24[4]>0) if day24 is not None else None,
            })
            prevcount+=1
            if day24 is not None:daycount+=1
        total_pairs+=prevcount
        total_day24+=daycount
        site_qc.append({
            "SITE":site,"GROUP":group,
            "original_clickpositive_rows":site_raw[site],
            "outside_Table_A1_paper_month_rows_discarded":site_trim[site],
            "original_clickpositive_rows_within_publication_months":len(sourcehours),
            "true_clickpositive_one_hour_pairs_after_trim":prevcount,
            "true_clickpositive_previous24h_source_pairs_after_trim":daycount,
        })
    if set(bygroup)!=set(REGIONS):
        raise AssertionError("Source records lost an original GROUP")
    if total_pairs>78030 or total_day24>49562:
        raise AssertionError("Source clipping cannot introduce more eligible 1h or 24h pairs")
    return bygroup,site_qc,{
        "source_original_records":source_count,
        "source_outside_published_months":trimmed,
        "source_records_within_published_months":source_count-trimmed,
        "source_distinct_SITE_after_trim":len(site_clip),
        "source_clickpositive_1hour_pairs_after_trim":total_pairs,
        "source_clickpositive_previous24h_pairs_after_trim":total_day24,
        "all_43_SITEs_still_represented":len(site_clip)==43,
    }

def evaluate():
    groups,quality,counts=generate_pairs()
    region_results={}
    geographic=[]
    temporal=[]
    for group in REGIONS:
        observations=groups[group]
        sites=sorted({x["SITE"] for x in observations})
        gitems=[];titems=[]
        for site in sites:
            tr=[x for x in observations if x["SITE"]!=site]
            te=[x for x in observations if x["SITE"]==site]
            a=geographic_evaluate(tr,te,False)
            a.update({
                "GROUP":group,"SITE":site,"panel":"PRIMARY_SITE_HELDOUT",
                "effects":a.get("gains_nats_per_clickpositive_hour")
            })
            geographic.append(a);gitems.append(a)
            gx=geographic_evaluate([x for x in tr if x["G24"] is not None],
                                   [x for x in te if x["G24"] is not None],True)
            gx.update({
                "GROUP":group,"SITE":site,"panel":"DAY24_SITE_HELDOUT",
                "effects":gx.get("gains_nats_per_clickpositive_hour")
            })
            geographic.append(gx);gitems.append(gx)
            within_site=[x for x in observations if x["SITE"]==site]
            for yr in sorted({source_year(x) for x in within_site}):
                train=[x for x in within_site if source_year(x)<yr]
                test=[x for x in within_site if source_year(x)==yr]
                b=temporal_evaluate(train,test,False)
                b.update({"GROUP":group,"SITE":site,"year":yr,"panel":"PRIMARY_YEAR_HELDOUT"})
                temporal.append(b);titems.append(b)
                bx=temporal_evaluate([x for x in train if x["G24"] is not None],
                                     [x for x in test if x["G24"] is not None],True)
                bx.update({"GROUP":group,"SITE":site,"year":yr,"panel":"DAY24_YEAR_HELDOUT"})
                temporal.append(bx);titems.append(bx)
        region_results[group]={
            "n_source_SITE_after_month_trim":len(sites),
            "source_true_1h_clickpositive_pairs_after_trim":len(observations),
            "geographic_SITE_holdout":{
                "primary":geographic_summary([x for x in gitems if x["panel"]=="PRIMARY_SITE_HELDOUT"]),
                "day24":geographic_summary([x for x in gitems if x["panel"]=="DAY24_SITE_HELDOUT"]),
            },
            "temporal_full_year_holdout":{
                "primary":temporal_summary([x for x in titems if x["panel"]=="PRIMARY_YEAR_HELDOUT"]),
                "day24":temporal_summary([x for x in titems if x["panel"]=="DAY24_YEAR_HELDOUT"]),
            },
        }
    if len(geographic)!=86 or len(temporal)<86:
        raise AssertionError("All 43 original source SITEs and available years must be audited")
    return {
        "version":"v163_original_paper_date_row_only_source_trim_sensitivity_1",
        "DOI":"10.1002/ece3.72566",
        "original_wiley_CSV_member_byteSHA256_verified":ORIGINAL_SHA,
        "method_determined_post_v160_v162_results":True,
        "source_month_filter_from_published_original_Table_A1":True,
        "source_clip_before_any_actual_one_hour_or_24h_history":True,
        "source_tableA1_months_are_not_verified_full_deployment_logs":True,
        "no_unobserved_Cpod_hours_imputed_as_silent":True,
        "same_v160_v161_fixed_models_and_gates_no_retune":True,
        "source_quality":counts,
        "all_43_source_SITE_row_counts":quality,
        "all_six_group_original_model_replays":region_results,
        "all_geo_source_site_gates_and_scores":[{
            "GROUP":r["GROUP"],"SITE":r["SITE"],"panel":r["panel"],
            "status":r["status"],"source":r["source"],
            "effects":r.get("effects")
        } for r in geographic],
        "all_year_source_SITEyear_gates_and_scores":[{
            "GROUP":r["GROUP"],"SITE":r["SITE"],"year":r["year"],
            "panel":r["panel"],"status":r["status"],"source":r["source_support"],
            "effects":r.get("gains_nats_per_detected_clickpositive_hour")
        } for r in temporal],
        "n_geographic_site_holdout_primary_eligible":sum(x["status"]=="EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE" and x["panel"]=="PRIMARY_SITE_HELDOUT" for x in geographic),
        "n_temporal_year_holdout_primary_eligible":sum(x["status"]=="EVALUATED_FULL_LATER_SOURCE_YEAR" and x["panel"]=="PRIMARY_YEAR_HELDOUT" for x in temporal),
        "n_geographic_day24_control_eligible":sum(x["status"]=="EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE" and x["panel"]=="DAY24_SITE_HELDOUT" for x in geographic),
        "n_temporal_day24_control_eligible":sum(x["status"]=="EVALUATED_FULL_LATER_SOURCE_YEAR" and x["panel"]=="DAY24_YEAR_HELDOUT" for x in temporal),
        "actual_on_effort_zero_click_hours":"NOT_OBSERVED",
        "physical_local_tide_and_solar_causes":"NOT_IDENTIFIED",
        "direct_mammal_boids_social_forces":"NOT_IDENTIFIED",
        "global_tide_solar_biological_meta_effect":"NOT_ESTIMATED"
    }

def compact_receipt(full):
    canonical=json.dumps(full,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":full["version"],
        "source_full_aggregate_SHA256":hashlib.sha256(canonical.encode()).hexdigest(),
        "source_full_aggregate_nbytes":len(canonical.encode()),
        "original_wiley_member_SHA256":ORIGINAL_SHA,
        "source_quality":full["source_quality"],
        "geographic_primary_eligible":full["n_geographic_site_holdout_primary_eligible"],
        "temporal_primary_eligible":full["n_temporal_year_holdout_primary_eligible"],
        "geo_day24_eligible":full["n_geographic_day24_control_eligible"],
        "year_day24_eligible":full["n_temporal_day24_control_eligible"],
        "all_six_region_analytical_source_summaries":full["all_six_group_original_model_replays"],
        "all_43_SITE_row_source_quality":full["all_43_source_SITE_row_counts"],
        "no_unverified_effort_or_tide_social_claim":True,
    }

def compare_close(p,a,b,issues):
    if len(issues)>=30:return
    if p=="root.source_full_aggregate_SHA256" or p=="root.source_full_aggregate_nbytes":
        return
    if type(a)!=type(b):
        issues.append([p,"TYPE",str(type(a)),str(type(b))])
    elif isinstance(a,dict):
        if set(a)!=set(b):issues.append([p,"KEYS"])
        else:
            for k in sorted(a):compare_close(p+"."+str(k),a[k],b[k],issues)
    elif isinstance(a,list):
        if len(a)!=len(b):issues.append([p,"LEN",len(a),len(b)])
        else:
            for i in range(len(a)):compare_close(p+"["+str(i)+"]",a[i],b[i],issues)
    elif isinstance(a,float):
        if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-7:
            issues.append([p,a,b])
    elif a!=b:
        issues.append([p,a,b])

def main():
    ap=argparse.ArgumentParser()
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit",action="store_true")
    group.add_argument("--check",action="store_true")
    args=ap.parse_args()
    full=evaluate()
    rec=compact_receipt(full)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    if args.check:
        if not RECEIPT.is_file():raise AssertionError("No frozen publisher source trim receipt")
        saved=json.loads(RECEIPT.read_text())
        issues=[]
        compare_close("root",saved,json.loads(json.dumps(rec,sort_keys=True)),issues)
        if issues:
            print("V163_FROZEN_SOURCE_REPLAY_DIFFERENCES="+json.dumps(issues,ensure_ascii=True))
            raise AssertionError("Original clipped source site/year model results changed")
        print("V163_GENUINE_CSV_SOURCE_PAPER_WINDOW_NUMERIC_REPLAY_PASS")
    else:
        print("V163_SOURCE_RECEIPT_START")
        print(json.dumps(rec,sort_keys=True,ensure_ascii=True,separators=(",",":")))
        print("V163_SOURCE_RECEIPT_END")
    print("V163_SOURCE_RESULT_SUMMARY="+json.dumps({
        "source":rec["source_quality"],
        "group":rec["all_six_region_analytical_source_summaries"]
    },sort_keys=True,ensure_ascii=True))

if __name__=="__main__":
    main()
