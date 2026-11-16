"""v160: Source-real porpoise within-region leave-one-SITE-out foraging-state
transfer, conditional ON a real click-positive C-POD hour and the preceding
hour ALSO being click-positive in the original Data S2. Missing CSV hours
are never manufactured zero clicks, negative buzzes or equipment effort.

Primary: baseline -> clock/season + same-hour detected-click density ->
last hour detected-click density -> last hour buzz-presence. Secondary on
IDENTICAL true source opportunity with t-24 also click-positive:
last 1h buzz state versus same-site same-clock previous-day buzz state.

Both are click-conditional retrospective classifications (the current
click total is already observed), NOT absolute encounter rates, population
ecology, prospective forecasts, tide causality or Boids social steering.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
for d in ("validation_v158","validation_v159"):
    sys.path.insert(0,str(ROOT/d))
from porpoise_source_gate import acquire
from site_hour_integrity import iso_weekday_source_ordinal,as_int

SOURCE_SHA="972b43b0313cb29aa485733b2892fba1f42aea5543da08ab87f8389bb3b7addf"
PRIOR=ROOT/"validation_v159/results/original_multiregion_hour_integrity_v159.json"
FULL=ROOT/"validation_v160/results/source_porpoise_heldout_full_v160.json"
RECEIPT=ROOT/"validation_v160/results/frozen_source_receipt_v160.json"
REGIONS=("BHB","FRANORTH","FRASOUTH","ICE","RWB","SWE")
MODELS=("C0_constant","C1_clock_current_clicks","C2_previous_click_density","C3_previous_buzz")
GHOST_MODELS=("C2_common","C3_previous_1h_buzz","G24_previous_day_buzz")
C=.25
MIN_TRAIN=1000;MIN_TEST=250;MIN_TR_POS=100;MIN_TR_NEG=100;MIN_TE_POS=40;MIN_TE_NEG=30
MIN_GHOST_TRAIN=700;MIN_GHOST_TEST=150;MIN_GHOST_TE_POS=25;MIN_GHOST_TE_NEG=20

def fixed_features(year,day,hour,clicks,previous_clicks):
    clock=2*math.pi*(hour+.5)/24
    yearphase=2*math.pi*(day-.5)/365.2425
    a=[math.sin(clock),math.cos(clock),
       math.sin(2*clock),math.cos(2*clock),
       math.sin(yearphase),math.cos(yearphase),
       math.sin(2*yearphase),math.cos(2*yearphase),
       (year-2016)/5,math.log1p(clicks)]
    return a,[*a,math.log1p(previous_clicks)]

def source():
    frozen=json.loads(PRIOR.read_text())
    if (frozen["original_CSV_rows"]!=126231 or frozen["unique_source_SITE_ids"]!=43
        or frozen["unique_source_GROUP_labels"]!=6
        or frozen["real_rows_with_invalid_composite_time"]!=0
        or frozen["real_rows_with_duplicate_sitehour"]!=0
        or frozen["genuine_previous_clickpositive_hour_pairs_not_verified_Cpod_effort"]!=78030):
        raise AssertionError("Frozen v159 source integrity gate changed")
    raw,_=acquire()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA or len(raw)!=26454371:
        raise AssertionError("Original 2025 DataS2 CSV member SHA/size changed")
    sitehours=defaultdict(dict);sitegroup={}
    n=0
    for x in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline="")):
        n+=1
        site=x["SITE"].strip();group=x["GROUP"].strip()
        year=as_int(x["year"]);day=as_int(x["YDAY"]);hour=as_int(x["hr"])
        k=iso_weekday_source_ordinal(year,day,hour)
        clicks=as_int(x["clicks"]);buzz=as_int(x["buzz"])
        if (not site or group not in REGIONS or k is None or
            clicks is None or clicks<=0 or buzz is None or buzz<0 or buzz>clicks):
            raise AssertionError("Original C-POD source labels or click counts invalid")
        if site in sitegroup and sitegroup[site]!=group:
            raise AssertionError("Original site mapped to two GROUPs")
        sitegroup[site]=group
        if k in sitehours[site]:raise AssertionError("Duplicate original source SITE-hour")
        sitehours[site][k]=(year,day,hour,clicks,buzz)
    if n!=126231 or len(sitehours)!=43 or set(sitegroup.values())!=set(REGIONS):
        raise AssertionError("Genuine original sites/groups/source rows changed")
    groups=defaultdict(list);quality=[];n_source_adjacent=0;n_ghost=0
    for site,hours in sorted(sitehours.items()):
        nprev=n24=0
        for k,current in sorted(hours.items()):
            previous=hours.get(k-1)
            if previous is None:continue
            year,day,hour,clicks,buzz=current
            if hour!=(previous[2]+1)%24:
                raise AssertionError("Original previous click-positive hour not adjacent")
            c1,c2=fixed_features(year,day,hour,clicks,previous[3])
            old_day=hours.get(k-24)
            record={
                "SITE":site,
                "Y":int(buzz>0),
                "C1":c1,
                "C2":c2,
                "C3":[*c2,int(previous[4]>0)],
                "G24":int(old_day[4]>0) if old_day is not None else None,
            }
            groups[sitegroup[site]].append(record)
            nprev+=1
            if old_day is not None:n24+=1
        quality.append({
            "SITE":site,"GROUP":sitegroup[site],
            "n_clickpositive_hours":len(hours),
            "n_genuine_consecutive_clickpositive_pairs":nprev,
            "n_day24_real_clickpositive_control_opportunities":n24
        })
        n_source_adjacent+=nprev;n_ghost+=n24
    if n_source_adjacent!=78030:
        raise AssertionError("V159 78030 true consecutive clickpositive pairs drifted")
    return groups,quality,{"original_clickpositive_rows":n,
                          "true_consecutive_clickpositive_hour_pairs":n_source_adjacent,
                          "true_previous_24h_clickpositive_source_pairs":n_ghost}

def gate(train,test,isghost=False):
    q={"train_clickpositive_hours":len(train),"test_clickpositive_hours":len(test),
       "train_buzz_positive":sum(r["Y"] for r in train),
       "test_buzz_positive":sum(r["Y"] for r in test)}
    q["train_buzz_negative"]=q["train_clickpositive_hours"]-q["train_buzz_positive"]
    q["test_buzz_negative"]=q["test_clickpositive_hours"]-q["test_buzz_positive"]
    minima={
        "train_clickpositive_hours":MIN_GHOST_TRAIN if isghost else MIN_TRAIN,
        "test_clickpositive_hours":MIN_GHOST_TEST if isghost else MIN_TEST,
        "train_buzz_positive":MIN_TR_POS,"train_buzz_negative":MIN_TR_NEG,
        "test_buzz_positive":MIN_GHOST_TE_POS if isghost else MIN_TE_POS,
        "test_buzz_negative":MIN_GHOST_TE_NEG if isghost else MIN_TE_NEG
    }
    return all(q[k]>=v for k,v in minima.items()),q

def prediction(train,test,label):
    Y=np.asarray([r["Y"] for r in train],dtype=int)
    if label=="C0_constant":
        return np.full(len(test),float(Y.mean()),dtype=float)
    def design(rows):
        if label in MODELS:
            field={"C1_clock_current_clicks":"C1",
                   "C2_previous_click_density":"C2",
                   "C3_previous_buzz":"C3"}[label]
            return np.asarray([r[field] for r in rows],dtype=float)
        a=np.asarray([r["C2"] for r in rows],dtype=float)
        col="C3" if label=="C3_previous_1h_buzz" else "G24"
        b=[r["C3"][-1] if col=="C3" else r[col] for r in rows]
        return np.column_stack((a,b))
    scale=StandardScaler()
    x=scale.fit_transform(design(train))
    xtest=scale.transform(design(test))
    model=LogisticRegression(C=C,solver="lbfgs",max_iter=350,
                             tol=1e-6,random_state=20261116)
    model.fit(x,Y)
    return model.predict_proba(xtest)[:,1]

def loss(y,p):
    y=np.asarray(y,dtype=float)
    z=np.clip(np.asarray(p,dtype=float),1e-6,1-1e-6)
    return float(np.mean(-(y*np.log(z)+(1-y)*np.log1p(-z))))

def brier(y,p):
    return float(np.mean((np.asarray(y,dtype=float)-np.asarray(p,dtype=float))**2))

def evaluate(train,test,ghost=False):
    supported,src=gate(train,test,ghost)
    if not supported:return {"status":"STOP_SOURCE_OR_RESPONSE_SUPPORT","source":src}
    models=GHOST_MODELS if ghost else MODELS
    y=[r["Y"] for r in test]
    scores={}
    for label in models:
        fitted_label="C2_previous_click_density" if label=="C2_common" else label
        p=prediction(train,test,fitted_label)
        scores[label]={"logloss":round(loss(y,p),8),
                       "brier":round(brier(y,p),8)}
    gain=lambda a,b:round(scores[a]["logloss"]-scores[b]["logloss"],8)
    if ghost:
        effects={
            "prev1_buzz_over_click_history":gain("C2_common","C3_previous_1h_buzz"),
            "prev24_buzz_over_click_history":gain("C2_common","G24_previous_day_buzz"),
            "prev1_buzz_over_prev24_clock_control":gain("G24_previous_day_buzz","C3_previous_1h_buzz"),
        }
    else:
        effects={
            "clock_and_current_clicks_over_constant":gain("C0_constant","C1_clock_current_clicks"),
            "prev_clicks_over_clock_and_current_clicks":gain("C1_clock_current_clicks","C2_previous_click_density"),
            "own_prev1_buzz_over_clock_and_click_counts":gain("C2_previous_click_density","C3_previous_buzz"),
        }
    return {"status":"EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE",
            "source":src,"scores":scores,"gains_nats_per_clickpositive_hour":effects}

def summary(rows):
    valid=[r for r in rows if r["status"]=="EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE"]
    if not valid:
        return {"eligible_sites":0,"n_clickpositive_test_hours":0,
                "status":"NO_SOURCE_ELIGIBLE_GEOGRAPHIC_HOLDOUTS"}
    keys=list(valid[0]["gains_nats_per_clickpositive_hour"])
    stats={key:{
        "equal_site_mean":round(float(np.mean([r["gains_nats_per_clickpositive_hour"][key] for r in valid])),8),
        "positive_heldout_sites":sum(r["gains_nats_per_clickpositive_hour"][key]>0 for r in valid),
        "negative_heldout_sites":sum(r["gains_nats_per_clickpositive_hour"][key]<0 for r in valid)
    } for key in keys}
    return {"eligible_sites":len(valid),
            "n_clickpositive_test_hours":sum(r["source"]["test_clickpositive_hours"] for r in valid),
            "site_equal_exploratory_scores":stats,
            "region_has_2_or_more_source_eligible_sites":len(valid)>=2,
            "not_a_full_monitoring_effort_or_population_rate":True}

def run():
    raw,source_quality,total=source()
    all_status=[]
    grouped={}
    for group in REGIONS:
        rows=raw[group]
        sites=sorted({r["SITE"] for r in rows})
        for site in sites:
            tr=[r for r in rows if r["SITE"]!=site]
            te=[r for r in rows if r["SITE"]==site]
            a=evaluate(tr,te,False)
            all_status.append({"GROUP":group,"SITE":site,"panel":"PRIMARY","status":a["status"],
                               "source":a["source"],"effects":a.get("gains_nats_per_clickpositive_hour"),
                               "scores":a.get("scores")})
            tr24=[r for r in tr if r["G24"] is not None]
            te24=[r for r in te if r["G24"] is not None]
            b=evaluate(tr24,te24,True)
            all_status.append({"GROUP":group,"SITE":site,"panel":"PREVIOUS_DAY_24H","status":b["status"],
                               "source":b["source"],"effects":b.get("gains_nats_per_clickpositive_hour"),
                               "scores":b.get("scores")})
        grouped[group]={
            "n_source_SITE_labels":len(sites),
            "n_true_consecutive_clickpositive_hours":len(rows),
            "PRIMARY":summary([r for r in all_status if r["GROUP"]==group and r["panel"]=="PRIMARY" ]),
            "PREVIOUS_DAY_24H":summary([r for r in all_status if r["GROUP"]==group and r["panel"]=="PREVIOUS_DAY_24H"]),
        }
    if len(all_status)!=86:raise AssertionError("43 original SITE IDs must produce 86 source gates")
    return {
        "version":"v160_authentic_porpoise_siteholdout_clickpositive_foraging_1",
        "original_CSV_sha256":SOURCE_SHA,
        "original_source_reacquired_and_site_hour_SHA_verified":True,
        "original_source_opportunities":total,
        "all_43_site_source_observation_counts":source_quality,
        "fixed_design":{
            "unit":"SITE-hour with actual detected clicks and click-positive previous 1h, not all recorder on-effort hours",
            "holdout":"entire original SITE, train only other SITE in same published GROUP",
            "response":"presence of at least one buzz click in click-positive hour",
            "clock":"2 harmonic local hour; 2 harmonic year-day; linear source year",
            "current_observation":"log1p detected current clicks; retrospective, not prospective",
            "additional_prev_click_count":"log1p actual clicks t-1",
            "additional_previous_foraging":"buzz positive t-1 at same SITE",
            "same_clock_negative_control":"buzz positive t-24h at same SITE only if actually observed",
            "model_regularizer_C":C,
            "feature_scaling":"training other sites only",
            "MIN_TRAIN":MIN_TRAIN,"MIN_TEST":MIN_TEST,
            "MIN_TR_POS":MIN_TR_POS,"MIN_TR_NEG":MIN_TR_NEG,
            "MIN_TE_POS":MIN_TE_POS,"MIN_TE_NEG":MIN_TE_NEG,
            "MIN_GHOST_TRAIN":MIN_GHOST_TRAIN,
            "MIN_GHOST_TEST":MIN_GHOST_TEST,
            "MIN_GHOST_TE_POS":MIN_GHOST_TE_POS,"MIN_GHOST_TE_NEG":MIN_GHOST_TE_NEG,
            "missing_original_hours_never_imputed_negative":True,
        },
        "all_86_site_source_gates_and_scores":all_status,
        "all_six_region_results":grouped,
        "n_primary_sites_evaluated":sum(r["panel"]=="PRIMARY" and r["status"]=="EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE" for r in all_status),
        "n_dayghost_sites_evaluated":sum(r["panel"]=="PREVIOUS_DAY_24H" and r["status"]=="EVALUATED_REAL_SITE_HELDOUT_CLICKPOSITIVE" for r in all_status),
        "independent_biological_regions_fitted":"ONLY_ELIGIBLE_REGIONS_DESCRIPTIVE",
        "no_global_pooled_biological_tide_by_solar_effect":True,
        "social_Boids_parameter":"NOT_IDENTIFIED",
        "statistical_pvalues":"NOT_COMPUTED",
    }

def receipt(full):
    sha=hashlib.sha256(json.dumps(full,ensure_ascii=True,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {
        "version":full["version"],
        "original_full_result_SHA256":sha,
        "original_CSV_member_SHA256_reverified":SOURCE_SHA,
        "original_source_opportunities":full["original_source_opportunities"],
        "n_primary_sites_evaluated":full["n_primary_sites_evaluated"],
        "n_dayghost_sites_evaluated":full["n_dayghost_sites_evaluated"],
        "fixed_design":full["fixed_design"],
        "all_six_region_results":full["all_six_region_results"],
        "all_site_source_gates_and_deltas":[{
            "GROUP":r["GROUP"],"SITE":r["SITE"],"panel":r["panel"],
            "status":r["status"],"source":r["source"],"effects":r["effects"]
        } for r in full["all_86_site_source_gates_and_scores"]],
        "not_prospective_not_inferred_silence_or_social_interaction":True,
    }

def main():
    p=argparse.ArgumentParser()
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--emit",action="store_true")
    group.add_argument("--check",action="store_true")
    opt=p.parse_args()
    full=run();s=receipt(full)
    FULL.parent.mkdir(parents=True,exist_ok=True)
    FULL.write_text(json.dumps(full,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    if opt.check:
        if not RECEIPT.exists():raise AssertionError("Missing previously frozen source receipt")
        frozen=json.loads(RECEIPT.read_text())
        if frozen!=json.loads(json.dumps(s,sort_keys=True)):
            raise AssertionError("Original C-POD clickpositive model and source summary changed")
        print("V160_ORIGINAL_SOURCE_REGION_SITE_HELDOUT_REPLAY_SUCCESS")
    else:
        print("V160_SOURCE_RECEIPT_START")
        print(json.dumps(s,ensure_ascii=True,sort_keys=True,separators=(",",":")))
        print("V160_SOURCE_RECEIPT_END")
    print("V160_SOURCE_SUMMARY="+json.dumps({
        "source":s["original_source_opportunities"],
        "n_primary_sites_evaluated":s["n_primary_sites_evaluated"],
        "n_dayghost_sites_evaluated":s["n_dayghost_sites_evaluated"],
        "regions":s["all_six_region_results"]},ensure_ascii=True,sort_keys=True))

if __name__=="__main__":
    main()
