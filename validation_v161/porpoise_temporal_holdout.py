"""v161: SAME-SITE strictly previous-source-YEAR to later-year holdout.

Independent confirmation after v160's geographically heldout source result.
Uses identical original 2025 Data S2 member and exact 78030 click-positive
t/t-1 hourly pairs. Previous-year models train on SAME SITE earlier years,
test ALL recorded source-click-positive pairs in one future year.

This distinguishes some long-lived SITE heterogeneity from actual
predictive information in the previous-hour acoustic buzz state. Still not
animal individual self-history, not continuous C-POD on-effort, and uses
observed current clicks; retrospective conditional classification only.

All thresholds/models inherited UNCHANGED from frozen v160. No positive
sites/year/time selected after examining new out-of-year model results.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v160"))
from porpoise_site_holdout import (
    source,gate,prediction,loss,brier,
    MODELS,GHOST_MODELS,
    MIN_TRAIN,MIN_TEST,MIN_TR_POS,MIN_TR_NEG,
    MIN_TE_POS,MIN_TE_NEG,MIN_GHOST_TRAIN,MIN_GHOST_TEST,
    MIN_GHOST_TE_POS,MIN_GHOST_TE_NEG
)

RECEIPT=ROOT/"validation_v161/results/frozen_temporal_source_receipt_v161.json"
FULL=ROOT/"validation_v161/results/porpoise_temporal_holdout_full_v161.json"
BASE_V160=ROOT/"validation_v160/results/frozen_source_receipt_v160.json"

def source_year(r):
    # Exactly invert v160's frozen input column (year-2016)/5.
    # This is a source feature, not a target-derived selection.
    x=r["C1"][8]
    y=int(round(x*5+2016))
    if not 2009<=y<=2023 or abs((y-2016)/5-x)>1e-10:
        raise AssertionError("Not original source YEAR from fixed v160 feature")
    return y

def evaluate(train,test,ghost=False):
    supported,q=gate(train,test,ghost)
    if not supported:
        return {"status":"STOP_ORIGINAL_YEAR_SOURCE_OR_LABEL_SUPPORT","source_support":q}
    types=GHOST_MODELS if ghost else MODELS
    y=[r["Y"] for r in test]
    scores={}
    for label in types:
        basis="C2_previous_click_density" if label=="C2_common" else label
        pred=prediction(train,test,basis)
        scores[label]={"logloss":round(loss(y,pred),8),
                       "brier":round(brier(y,pred),8)}
    gain=lambda a,b:round(scores[a]["logloss"]-scores[b]["logloss"],8)
    if ghost:
        gains={
            "real_previous_1h_over_click_density":gain("C2_common","C3_previous_1h_buzz"),
            "real_previous_24h_over_click_density":gain("C2_common","G24_previous_day_buzz"),
            "real_previous_1h_vs_24h_daycontrol":gain("G24_previous_day_buzz","C3_previous_1h_buzz"),
        }
    else:
        gains={
            "clock_and_current_clicks_over_constant":gain("C0_constant","C1_clock_current_clicks"),
            "prev_click_density_over_clock_and_current_clicks":gain("C1_clock_current_clicks","C2_previous_click_density"),
            "real_previous_1h_buzz_over_click_count_and_clock":gain("C2_previous_click_density","C3_previous_buzz"),
        }
    return {"status":"EVALUATED_FULL_LATER_SOURCE_YEAR",
            "source_support":q,
            "heldout_logloss_and_brier":scores,
            "gains_nats_per_detected_clickpositive_hour":gains}

def summarize(sub):
    valid=[r for r in sub if r["status"]=="EVALUATED_FULL_LATER_SOURCE_YEAR"]
    if not valid:
        return {"evaluated_siteyears":0,"unique_sites":0,"status":"STOP_NO_ELIGIBLE_TEMPORAL_HOLDOUT"}
    bysite=defaultdict(list)
    for r in valid:bysite[r["SITE"]].append(r)
    keys=list(valid[0]["gains_nats_per_detected_clickpositive_hour"])
    def s(z):
        return round(float(np.mean(z)),8) if z else None
    bysite_summary={}
    for site,recs in sorted(bysite.items()):
        bysite_summary[site]={
            "n_heldout_years":len(recs),
            "year_labels":[r["test_year"] for r in recs],
            "site_year_mean_nats_per_hour":{
                k:s([r["gains_nats_per_detected_clickpositive_hour"][k] for r in recs])
                for k in keys
            }
        }
    site_stats={}
    for k in keys:
        vals=[rec["site_year_mean_nats_per_hour"][k] for rec in bysite_summary.values()]
        site_stats[k]={
            "site_equal_mean":s(vals),
            "positive_sites":sum(v>0 for v in vals),
            "negative_sites":sum(v<0 for v in vals),
            "range_site_means":[round(min(vals),8),round(max(vals),8)]
        }
    siteyear_stats={}
    for k in keys:
        vals=[r["gains_nats_per_detected_clickpositive_hour"][k] for r in valid]
        siteyear_stats[k]={
            "siteyear_equal_mean":s(vals),
            "positive_siteyears":sum(v>0 for v in vals),
            "negative_siteyears":sum(v<0 for v in vals),
        }
    return {
        "evaluated_siteyears":len(valid),
        "unique_sites":len(bysite),
        "total_heldout_true_source_clickpositive_hours":sum(r["source_support"]["test_clickpositive_hours"] for r in valid),
        "true_site_holdouts_are_temporal_not_out_of_site":True,
        "site_equal_summary":site_stats,
        "siteyear_equal_summary":siteyear_stats,
        "per_site_descriptives":bysite_summary,
        "n_sites_at_least_two_to_describe_region":len(bysite)>=2,
    }

def run():
    frozen=json.loads(BASE_V160.read_text())
    if (frozen["original_source_opportunities"]["true_consecutive_clickpositive_hour_pairs"]!=78030
        or frozen["original_source_opportunities"]["original_clickpositive_rows"]!=126231
        or frozen["n_primary_sites_evaluated"]!=21):
        raise AssertionError("Frozen original v160 site-holdout source result changed")
    data,source_qc,source_counts=source()
    records=[];regional={};n_site_year=0
    for group in sorted(data):
        src=data[group]
        sites=sorted({r["SITE"] for r in src})
        group_rows=[]
        for site in sites:
            sr=[r for r in src if r["SITE"]==site]
            years=sorted(set(source_year(r) for r in sr))
            for yr in years:
                train=[r for r in sr if source_year(r)<yr]
                test=[r for r in sr if source_year(r)==yr]
                base=evaluate(train,test,False)
                base.update({"GROUP":group,"SITE":site,"test_year":yr,
                             "analysis":"PRIMARY_PRIOR_YEARS_TO_COMPLETE_LATER_YEAR",
                             "train_source_years":sorted(set(source_year(r) for r in train))})
                group_rows.append(base);records.append(base)
                tr24=[r for r in train if r["G24"] is not None]
                te24=[r for r in test if r["G24"] is not None]
                other=evaluate(tr24,te24,True)
                other.update({"GROUP":group,"SITE":site,"test_year":yr,
                              "analysis":"SECONDARY_DAY24_SAME_SOURCE_YEAR",
                              "train_source_years":sorted(set(source_year(r) for r in tr24))})
                group_rows.append(other);records.append(other)
                n_site_year+=1
        regional[group]={
            "source_sites":len(sites),
            "source_SITEyear_source_records":sum(len({source_year(x) for x in src if x["SITE"]==site}) for site in sites),
            "PRIMARY":summarize([r for r in group_rows if r["analysis"]=="PRIMARY_PRIOR_YEARS_TO_COMPLETE_LATER_YEAR"]),
            "DAY24_NEGATIVE_CONTROL":summarize([r for r in group_rows if r["analysis"]=="SECONDARY_DAY24_SAME_SOURCE_YEAR"]),
        }
    if n_site_year<43 or len(records)!=2*n_site_year:
        raise AssertionError("Every source SITE/year must have both primary/ghost gates")
    return {
        "version":"v161_authentic_porpoise_prior_year_temporal_holdout_self_buzz_1",
        "original_source_CSV_sha256":frozen["original_CSV_member_SHA256_reverified"],
        "source_reacquired_real_43_SITE_6_GROUP":True,
        "source_original_clickpositive_opportunities":source_counts,
        "source_SITEyear_pairs_with_previous_hour":n_site_year,
        "source_full_43_SITE_counts":source_qc,
        "original_model_no_changes_to_v160_fixed_features_or_source_gate":True,
        "train_test":"Same original SITE all strictly earlier click-positive source years train, complete later source-year clicks-positive hours heldout",
        "source_unit":"Buzz>0 CONDITIONAL on detected clicks at current AND previous source hour",
        "all_source_SITEyear_gates_and_scores":records,
        "per_GROUP_prior_year_time_holdout_results":regional,
        "n_primary_site_years_fitted":sum(r["status"]=="EVALUATED_FULL_LATER_SOURCE_YEAR" and r["analysis"]=="PRIMARY_PRIOR_YEARS_TO_COMPLETE_LATER_YEAR" for r in records),
        "n_day24_site_years_fitted":sum(r["status"]=="EVALUATED_FULL_LATER_SOURCE_YEAR" and r["analysis"]=="SECONDARY_DAY24_SAME_SOURCE_YEAR" for r in records),
        "no_independent_43_years_as_43_biological_studies":True,
        "global_tidal_solar_biological_effect":"NOT_ESTIMATED",
        "social_Boids_motion_force":"NOT_IDENTIFIED",
        "no_p_values":True
    }

def receipt(result):
    canon=json.dumps(result,sort_keys=True,ensure_ascii=True,separators=(",",":"))
    return {
        "version":result["version"],
        "first_run_full_result_canonical_sha256":hashlib.sha256(canon.encode()).hexdigest(),
        "original_CSV_member_SHA256":result["original_source_CSV_sha256"],
        "source_original_clickpositive_opportunities":result["source_original_clickpositive_opportunities"],
        "source_SITEyear_pairs_with_previous_hour":result["source_SITEyear_pairs_with_previous_hour"],
        "n_primary_site_years_fitted":result["n_primary_site_years_fitted"],
        "n_day24_site_years_fitted":result["n_day24_site_years_fitted"],
        "all_region_results":result["per_GROUP_prior_year_time_holdout_results"],
        "all_siteyear_status_gates_gains":[{
            "GROUP":z["GROUP"],"SITE":z["SITE"],"year":z["test_year"],
            "analysis":z["analysis"],"status":z["status"],
            "source":z["source_support"],
            "gains":z.get("gains_nats_per_detected_clickpositive_hour")
        } for z in result["all_source_SITEyear_gates_and_scores"]],
        "source_43_sites_no_missing_silent_hours_created":True,
    }

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit",action="store_true")
    g.add_argument("--check",action="store_true")
    opts=p.parse_args()
    v=run();rec=receipt(v)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    if opts.check:
        if not RECEIPT.exists():raise AssertionError("Missing initial true original v161 receipt")
        old=json.loads(RECEIPT.read_text())
        mismatches=[]
        def verify(prefix,a,b):
            if len(mismatches)>=25:return
            if prefix=="root.first_run_full_result_canonical_sha256":return
            if type(a)!=type(b):mismatches.append([prefix,str(type(a)),str(type(b))])
            elif isinstance(a,dict):
                if set(a)!=set(b):mismatches.append([prefix,"KEYS_CHANGED"])
                else:
                    for k in sorted(a):verify(prefix+"."+str(k),a[k],b[k])
            elif isinstance(a,list):
                if len(a)!=len(b):mismatches.append([prefix,"LEN",len(a),len(b)])
                else:
                    for i in range(len(a)):verify(prefix+"["+str(i)+"]",a[i],b[i])
            elif isinstance(a,float):
                if not math.isfinite(a) or not math.isfinite(b):
                    if a!=b:mismatches.append([prefix,a,b])
                elif abs(a-b)>1e-7:mismatches.append([prefix,a,b])
            elif a!=b:mismatches.append([prefix,a,b])
        verify("root",old,json.loads(json.dumps(rec,sort_keys=True)))
        if mismatches:
            print("V161_FROZEN_MODEL_DIFF="+json.dumps(mismatches,ensure_ascii=True))
            raise AssertionError("v161 original member SHA/gates/scores changed")
        print("V161_ORIGINAL_YEAR_HOLDOUT_MODEL_SOURCE_REPLAY_PASS")
    else:
        print("V161_SOURCE_RECEIPT_START")
        print(json.dumps(rec,ensure_ascii=True,sort_keys=True,separators=(",",":")))
        print("V161_SOURCE_RECEIPT_END")
    print("V161_REGION_RESULT="+json.dumps(v["per_GROUP_prior_year_time_holdout_results"],ensure_ascii=True,sort_keys=True))

if __name__=="__main__":main()
