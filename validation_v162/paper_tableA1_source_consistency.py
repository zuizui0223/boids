"""v162 genuine publisher Table A1 date-range provenance sensitivity for Data S2.

Source: Stavenow Jerremalm et al. 2025 DOI 10.1002/ece3.72566 Table A1
published site (from/until MONTH) vs the published supplementary ORIGINAL
Data S2 (year,YDAY,hour). Source CSV member SHA256 fixed in v158/v159.

Post hoc source-quality gate due witnessed HONO/2022-23 vs original CSV
2015-18 and NVSK4/2021 vs CSV 2019-20 inconsistency. Published metadata
may be incomplete rather than CSV wrong; DO NOT decide which is correct.

Conservative sensitivity: exclude ENTIRE SITE from both train and test if
ANY original CSV time lies beyond its published Table A1 month-year window.
Keep original v160 and v161 estimates frozen and unchanged; this is not an
outcome-selected source rule. All v160 original model features, thresholds,
regularizers, labels and v161 year holdouts are reused exactly.

No new p values, animal identities or globally pooled tide×solar effects.
"""
from __future__ import annotations

import argparse,csv,hashlib,io,json,math,sys
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
for z in ("validation_v158","validation_v159","validation_v160","validation_v161"):
    sys.path.insert(0,str(ROOT/z))
from porpoise_source_gate import acquire
from site_hour_integrity import as_int
from porpoise_site_holdout import (
    source as original_source,
    evaluate as geographic_evaluate,
    summary as geographic_summary
)
from porpoise_temporal_holdout import (
    source_year,evaluate as temporal_evaluate,
    summarize as temporal_summary
)

FULL=ROOT/"validation_v162/results/original_tableA1_date_source_sensitivity_v162.json"
RECEIPT=ROOT/"validation_v162/results/frozen_published_metadata_receipt_v162.json"
V160=ROOT/"validation_v160/results/frozen_source_receipt_v160.json"
V161=ROOT/"validation_v161/results/frozen_temporal_source_receipt_v161.json"
ORIGINAL_SHA="972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf"

# Manual transcription of ORIGINAL paper Table A1 "Data from"/"Data until"
# month-year. Numeric ICE source codes are the 17 unique suffixes of named
# SKJAL*/EYJA* Table A1 deployments, not a validated animal identity.
# Source MRC4 is a possible label mismatch to paper MSC4, kept explicit.
def published_tableA1():
    data={}
    for site in ("1","13","14","17","18","19","28","33","36",
                 "37","48","49","69","70","74","91","92"):
        data[site]=("ICE",(2017,8),(2018,8),"Iceland numbered suffix")
    for site,yr in {
        "BALGO1":((2019,5),(2023,4)),
        "FLAD2":((2019,5),(2023,4)),
        "HONO":((2022,10),(2023,9)),
        "LMIDD1":((2019,5),(2023,4)),
        "NVSK4":((2021,8),(2022,10)),
        "NVSK6":((2019,5),(2023,4)),
        "STMIDD1":((2019,5),(2023,4))
    }.items():data[site]=("SWE",yr[0],yr[1],site)
    for site,yr in {
        "LS1":((2009,4),(2015,10)),
        "LS2":((2009,7),(2017,7)),
        "LS3":((2009,4),(2016,7)),
        "LS4":((2010,3),(2017,7)),
    }.items():data[site]=("BHB",yr[0],yr[1],site)
    for site,yr in {
        "CALF":((2020,11),(2023,5)),
        "LONG":((2021,4),(2023,5)),
        "SHERKIN":((2020,11),(2023,5)),
    }.items():data[site]=("RWB",yr[0],yr[1],site)
    for site,yr in {
        "LINIOU":((2012,7),(2013,9)),
        "MAREE":((2013,12),(2014,4)),
        "LAVANDREE":((2013,4),(2013,7)),
        "AWAC":((2012,10),(2013,12)),
    }.items():data[site]=("FRANORTH",yr[0],yr[1],site)
    for site,yr in {
        "LISEA1":((2015,11),(2016,11)),
        "LISEA2":((2015,11),(2016,11)),
        "LISEA3":((2016,3),(2016,12)),
        "LISEA4":((2015,11),(2016,11)),
        "MRC1":((2013,1),(2013,12)),
        "MRC2":((2013,3),(2013,9)),
        "MRC3":((2013,5),(2014,5)),
        "MRC4":((2013,6),(2014,3)),
    }.items():data[site]=("FRASOUTH",yr[0],yr[1],"MSC4 paper alias" if site=="MRC4" else site)
    if len(data)!=43:
        raise AssertionError("Original paper Table A1 expected exactly 43 deployments")
    return data

def genuine_source_periods():
    pub=published_tableA1()
    raw,_=acquire()
    if len(raw)!=26454371 or hashlib.sha256(raw).hexdigest()!=ORIGINAL_SHA:
        raise AssertionError("Original publisher DataS2 member SHA changed")
    sitequality=defaultdict(lambda:{"original_rows":0,"outside_monthyear_rows":0,
        "outside_whole_year_rows":0,"within_monthyear_rows":0,
        "source_monthyear_min":None,"source_monthyear_max":None,
        "bad_calendar_rows":0,"years_outside":Counter()})
    n=0
    for x in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline="")):
        n+=1
        site=x["SITE"].strip();group=x["GROUP"].strip()
        if site not in pub or group!=pub[site][0]:
            raise AssertionError("Original 43 SITE / GROUP codes no longer match published Table A1 mapping")
        y=as_int(x["year"]);d=as_int(x["YDAY"])
        if y is None or d is None or d<1 or d>366:
            raise AssertionError("Original site year/day missing")
        dt=datetime(y,1,1)+timedelta(days=d-1)
        if dt.year!=y:raise AssertionError("Impossible original source leap-day")
        month=(y,dt.month)
        pgroup,pbegin,pend,pname=pub[site]
        a=sitequality[site]
        a["original_rows"]+=1
        a["source_monthyear_min"]=month if a["source_monthyear_min"] is None else min(month,a["source_monthyear_min"])
        a["source_monthyear_max"]=month if a["source_monthyear_max"] is None else max(month,a["source_monthyear_max"])
        if pbegin<=month<=pend:
            a["within_monthyear_rows"]+=1
        else:
            a["outside_monthyear_rows"]+=1
            a["years_outside"][str(y)]+=1
        if y<pbegin[0] or y>pend[0]:
            a["outside_whole_year_rows"]+=1
    if n!=126231 or len(sitequality)!=43:
        raise AssertionError("Publisher source table vs actual 126231/43 source scope changed")
    source_rows=[]
    for site,meta in sorted(pub.items()):
        q=sitequality[site]
        source_rows.append({
            "SITE":site,"GROUP":meta[0],"original_paper_site_label":meta[3],
            "published_from_YYYY_MM":"%04d-%02d"%meta[1],
            "published_until_YYYY_MM":"%04d-%02d"%meta[2],
            "source_first_YYYY_MM":"%04d-%02d"%q["source_monthyear_min"],
            "source_last_YYYY_MM":"%04d-%02d"%q["source_monthyear_max"],
            "n_original_clickpositive_rows":q["original_rows"],
            "n_within_published_monthyear":q["within_monthyear_rows"],
            "n_outside_published_monthyear":q["outside_monthyear_rows"],
            "n_outside_published_full_year_range":q["outside_whole_year_rows"],
            "outside_paper_monthyear_source_year_counts":dict(sorted(q["years_outside"].items())),
            "conservative_whole_SITE_exclusion":q["outside_monthyear_rows"]>0,
            "paper_alias_or_source_SITE_identity_uncertainty":site=="MRC4" or meta[0]=="ICE",
        })
    return source_rows

def source_heldout_sensitivity():
    a=json.loads(V160.read_text());b=json.loads(V161.read_text())
    if (a["n_primary_sites_evaluated"]!=21 or a["n_dayghost_sites_evaluated"]!=19
        or b["n_primary_site_years_fitted"]!=15 or b["n_day24_site_years_fitted"]!=8):
        raise AssertionError("Original frozen v160/v161 source results changed")
    meta=genuine_source_periods()
    excluded={r["SITE"] for r in meta if r["conservative_whole_SITE_exclusion"]}
    groups,old_sites,quality=original_source()
    if quality["original_clickpositive_rows"]!=126231 or quality["true_consecutive_clickpositive_hour_pairs"]!=78030:
        raise AssertionError("Original acoustic source duration changed")
    geographic=[];temporal=[];regional={}
    for group in sorted(groups):
        original=groups[group]
        clean=[r for r in original if r["SITE"] not in excluded]
        sites=sorted({r["SITE"] for r in clean})
        geos=[];years=[]
        for site in sites:
            tr=[r for r in clean if r["SITE"]!=site]
            te=[r for r in clean if r["SITE"]==site]
            p=geographic_evaluate(tr,te,False)
            p.update({"GROUP":group,"SITE":site,"panel":"GEOGRAPHIC_ORIGINAL_V160"})
            geos.append(p);geographic.append(p)
            q=geographic_evaluate([r for r in tr if r["G24"] is not None],
                                  [r for r in te if r["G24"] is not None],True)
            q.update({"GROUP":group,"SITE":site,"panel":"GEOGRAPHIC_DAY24"})
            geos.append(q);geographic.append(q)
            all_site=[r for r in clean if r["SITE"]==site]
            for year in sorted({source_year(r) for r in all_site}):
                train=[r for r in all_site if source_year(r)<year]
                test=[r for r in all_site if source_year(r)==year]
                v=temporal_evaluate(train,test,False)
                v.update({"GROUP":group,"SITE":site,"test_year":year,"panel":"TEMPORAL_ORIGINAL_V161"})
                temporal.append(v);years.append(v)
                w=temporal_evaluate([r for r in train if r["G24"] is not None],
                                    [r for r in test if r["G24"] is not None],True)
                w.update({"GROUP":group,"SITE":site,"test_year":year,"panel":"TEMPORAL_DAY24"})
                temporal.append(w);years.append(w)
        regional[group]={
            "original_SOURCE_SITE_n":len({r["SITE"] for r in original}),
            "strict_paper_metadata_compatible_SOURCE_SITE_n":len(sites),
            "excluded_paper_metadata_mismatch_SOURCE_SITES":sorted(set(r["SITE"] for r in original)&excluded),
            "original_v160_source_clickpositive_pair_count":len(original),
            "after_site_exclusion_same_SOURCE_clickpositive_pair_count":len(clean),
            "geographic_v160_replay_primary":geographic_summary([x for x in geos if x["panel"]=="GEOGRAPHIC_ORIGINAL_V160"]),
            "geographic_v160_replay_day24":geographic_summary([x for x in geos if x["panel"]=="GEOGRAPHIC_DAY24"]),
            "temporal_v161_replay_primary":temporal_summary([x for x in years if x["panel"]=="TEMPORAL_ORIGINAL_V161"]),
            "temporal_v161_replay_day24":temporal_summary([x for x in years if x["panel"]=="TEMPORAL_DAY24"]),
        }
    return {
        "version":"v162_original_published_TableA1_monthyear_metadata_source_sensitivity_1",
        "original_publisher_source_CSV_member_SHA256":ORIGINAL_SHA,
        "original_paper_TableA1_DOI":"10.1002/ece3.72566",
        "paper_site_date_source":"Table A1 43 SITE publication-month dates manually transcribed and validated as 43",
        "source_audit_posthoc_after_v160_v161_results":True,
        "month_start_end_are_published_metadata_not_verified_source_deployment_logs":True,
        "outside_paper_range_is_QA_flag_not_proof_of_false_CSV_row":True,
        "source_metadata_by_all_43_SITE":meta,
        "source_monthyear_consistency_summary":{
            "all_original_rows":sum(z["n_original_clickpositive_rows"] for z in meta),
            "source_rows_outside_monthyear":sum(z["n_outside_published_monthyear"] for z in meta),
            "source_rows_outside_whole_year":sum(z["n_outside_published_full_year_range"] for z in meta),
            "source_site_ids_flagged_any_outside_published_monthyear":sum(z["conservative_whole_SITE_exclusion"] for z in meta),
            "flagged_source_SITE_labels":[z["SITE"] for z in meta if z["conservative_whole_SITE_exclusion"]],
        },
        "source_sensitivity_rule":"Conservative entire SITE excluded from training AND testing if any Data S2 month lies outside its published Table A1 date range; original source remains unchanged",
        "source_model_regularizers_and_gates_same_as_frozen_v160_and_v161":True,
        "strict_subset_sensitivity_by_six_GROUP":regional,
        "all_conservative_geographic_and_temporal_frozen_model_statuses":({
            "geographic":[{
                "GROUP":x["GROUP"],"SITE":x["SITE"],"panel":x["panel"],"status":x["status"],
                "source":x["source"],"gains":x.get("gains_nats_per_clickpositive_hour")
            } for x in geographic],
            "temporal":[{
                "GROUP":x["GROUP"],"SITE":x["SITE"],"year":x["test_year"],
                "panel":x["panel"],"status":x["status"],
                "source":x["source_support"],"gains":x.get("gains_nats_per_detected_clickpositive_hour")
            } for x in temporal],
        }),
        "genuine_table_A1_vs_CSV_original_uncertainty_not_resolved":True,
        "no_direct_individual_mammal_tracking_or_social_Boids_forces":True,
        "global_tidal_x_solar_effect":"NOT_ESTIMATED",
    }

def source_receipt(v):
    canonical=json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":v["version"],
        "original_full_audit_and_model_output_SHA256":hashlib.sha256(canonical.encode()).hexdigest(),
        "source_SHA256":v["original_publisher_source_CSV_member_SHA256"],
        "source_metadata_consistency":v["source_monthyear_consistency_summary"],
        "all_43_source_paper_date_comparisons":v["source_metadata_by_all_43_SITE"],
        "all_six_group_geographic_and_temporal_strict_sensitivity":v["strict_subset_sensitivity_by_six_GROUP"],
        "source_rules_unchanged":True,
        "posthoc_conservative_date_filter":True,
        "no_global_meta_tide_sun":True,
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=source_heldout_sensitivity()
    r=source_receipt(result)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    if args.check:
        if not RECEIPT.exists():raise AssertionError("Missing v162 original source receipt")
        saved=json.loads(RECEIPT.read_text())
        problems=[]
        def compare(p,a,b):
            if len(problems)>=30:return
            if p=="root.original_full_audit_and_model_output_SHA256":return
            if type(a)!=type(b):problems.append([p,"TYPE"])
            elif isinstance(a,dict):
                if set(a)!=set(b):problems.append([p,"KEYS"])
                else:
                    for k in sorted(a):compare(p+"."+str(k),a[k],b[k])
            elif isinstance(a,list):
                if len(a)!=len(b):problems.append([p,"LENGTH",len(a),len(b)])
                else:
                    for i in range(len(a)):compare(p+"["+str(i)+"]",a[i],b[i])
            elif isinstance(a,float):
                if not math.isfinite(a) or not math.isfinite(b) or abs(a-b)>1e-7:
                    problems.append([p,a,b])
            elif a!=b:problems.append([p,a,b])
        compare("root",saved,json.loads(json.dumps(r,sort_keys=True)))
        if problems:
            print("V162_REPLAY_SOURCE_DIFFERENCES="+json.dumps(problems,ensure_ascii=True))
            raise AssertionError("Original published date vs source original / heldout source changed")
        print("V162_SOURCE_METADATA_AND_SENSITIVITY_REPLAY_SUCCESS")
    else:
        print("V162_SOURCE_RECEIPT_START")
        print(json.dumps(r,ensure_ascii=True,sort_keys=True,separators=(",",":")))
        print("V162_SOURCE_RECEIPT_END")
    print("V162_SOURCE_REPORT_SUMMARY="+json.dumps({
        "source":r["source_metadata_consistency"],
        "group":r["all_six_group_geographic_and_temporal_strict_sensitivity"]
    },ensure_ascii=True,sort_keys=True))

if __name__=="__main__":main()
