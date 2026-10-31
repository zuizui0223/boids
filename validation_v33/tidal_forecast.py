#!/usr/bin/env python3
"""v33-C: source-verified astronomical tidal RANGE, day-ahead movement prediction.

Original RWS Schiermonnikoog tide is known from orbit and can be supplied for
a future target day. NEVER use actual future MEASURED water level to forecast.
After-known v32 outcomes: exploratory predeclared extension, one coastal study.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import gc
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import urllib.request

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v32"))
import forecast as v32

RWS_URL="https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
STATION="schiermonnikoog.waddenzee"
SOURCE_PROCESS="astronomisch"
YEARS=tuple(range(2008,2015))
MAX_YEAR_RESPONSE_BYTES=30_000_000
DAY_SLOTS=144
MIN_SLOTS=116
MIN_QUADRANT_SLOTS=18
RWS_YEAR_GATE=.95
RIDGE=20.0
WARMUP=100
BOOT_REPS=10000
BOOT_SEED=20261031
MAX_NONMATCHED_RATIO=.15
MIN_MATCHED_BIRDS=30
MIN_MATCHED_DAYS=6000
PROTOCOL="docs/V33C_FIXED_TIDAL_INCREMENT_FORECAST.md"
V32_RECEIPT=ROOT/"validation_v32/results/oystercatcher_independent_v32.json"
MODEL_ORDER=("MH","MH_TIDE","MH_SEASON","MH_SEASON_TIDE","MH_SHIFT7")
KEYS=("PRIMARY_MH_minus_MH_TIDE",
      "secondary_MH_SEASON_minus_MH_SEASON_TIDE",
      "placebo_MH_minus_MH_SHIFT7")

def rws_body(year):
    if year not in YEARS:raise ValueError("Tidal year outside registered archive")
    start=f"{year}-01-01T00:00:00.000+01:00"
    end=f"{year+1}-01-02T00:00:00.000+01:00"
    return {"Locatie":{"Code":STATION},
      "AquoPlusWaarnemingMetadata":{"AquoMetadata":{
       "Compartiment":{"Code":"OW"},"Grootheid":{"Code":"WATHTE"},"ProcesType":SOURCE_PROCESS}},
      "Periode":{"Begindatumtijd":start,"Einddatumtijd":end}}

def rws_get_year(year):
    req=urllib.request.Request(RWS_URL,method="POST",
         data=json.dumps(rws_body(year),separators=(",",":")).encode(),
         headers={"Accept":"application/json","Content-Type":"application/json",
                  "User-Agent":"boids-v33-frozen-tidal-range-forecast/1.0"})
    with urllib.request.urlopen(req,timeout=90) as response:
        raw=response.read(MAX_YEAR_RESPONSE_BYTES+1)
    if len(raw)>MAX_YEAR_RESPONSE_BYTES:raise ValueError("RWS original year exceeds source cap")
    return json.loads(raw),len(raw)

def utc_stamp(value):
    out=dt.datetime.fromisoformat(str(value))
    if out.tzinfo is None:raise ValueError("RWS tide needs explicit +01:00 source offset")
    if out.utcoffset()!=dt.timedelta(hours=1):
        raise ValueError("Unexpected RWS time offset; Dutch winter time is fixed +01")
    return out.astimezone(dt.timezone.utc).replace(tzinfo=None)

def tide_series_from_response(obj, year):
    if obj.get("Succesvol") is not True:raise ValueError("RWS tide retrieval failed")
    groups=obj.get("WaarnemingenLijst")
    if not isinstance(groups,list) or len(groups)!=1:
        raise ValueError("Expected exactly one official astronomy/source series")
    x=groups[0];meta=x.get("AquoMetadata") or {}
    loc=x.get("Locatie") or {}
    if (loc.get("Code")!=STATION or
        (meta.get("Grootheid") or {}).get("Code")!="WATHTE" or
        (meta.get("Eenheid") or {}).get("Code")!="cm" or
        (meta.get("Hoedanigheid") or {}).get("Code")!="NAP" or
        meta.get("ProcesType")!=SOURCE_PROCESS):
        raise ValueError("RWS metadata station, units or astronomy mismatch")
    values={}
    counts=collections.Counter()
    for measurement in x.get("MetingenLijst") or []:
        t=utc_stamp(measurement["Tijdstip"])
        reading=(measurement.get("Meetwaarde") or {}).get("Waarde_Numeriek")
        try:h=float(reading)/100.
        except (ValueError,TypeError):h=float("nan")
        quality=measurement.get("WaarnemingMetadata") or {}
        qualitycodes=quality.get("KwaliteitswaardeCodeLijst") or []
        if isinstance(qualitycodes,dict): qualitycodes=[qualitycodes]
        if any(str(q.get("Code"))=="99" for q in qualitycodes if isinstance(q,dict)):
            counts["invalid_quality_99"]+=1;continue
        if not math.isfinite(h) or abs(h)>10.:
            counts["invalid_or_missing_numeric"]+=1;continue
        if t.minute%10!=0 or t.second!=0:
            raise ValueError("RWS astronomical observations not aligned at 10-minute UTC")
        old=values.get(t)
        if old is not None and abs(old-h)>1e-8:
            raise ValueError("Contradictory identical RWS tide timestamp")
        values[t]=h
        counts["valid_original_10minute_heights"]+=1
    required=round((dt.datetime(year+1,1,1)-dt.datetime(year,1,1)).total_seconds()/600)
    actual=sum(1 for t in values if t.year==year)
    if actual/RWS_YEAR_GATE < required:
        # The source is insufficient; never loosen the 95% per-year requirement.
        raise ValueError(f"RWS astronomical year {year} missing: {actual}/{required} UTC slots")
    return values,{"year":year,"expected_UTC_slots":required,
                   "valid_UTC_slots_in_year":actual,
                   "fraction_valid_in_year":actual/required,
                   "source_UTC_offset":"fixed +01:00 translated to UTC",
                   "observed_RWS_process":"astronomisch",
                   "count_source_measurements":sum(counts.values()),
                   "invalid_quality_99":counts["invalid_quality_99"],
                   "invalid_or_missing_numeric":counts["invalid_or_missing_numeric"]}

def load_original_astronomy():
    series={}
    years=[]
    for year in YEARS:
        obj,response_bytes=rws_get_year(year)
        sub,info=tide_series_from_response(obj,year)
        info["original_API_response_bytes"]=response_bytes
        years.append(info)
        for t,h in sub.items():
            if t in series and abs(h-series[t])>1e-8:
                raise ValueError("Overlapping annual RWS astronomy values disagree")
            series[t]=h
        del obj,sub
        gc.collect()
    return series,years

def daily_tide_range(series):
    days=collections.defaultdict(list)
    for t,h in series.items():
        if t.year not in YEARS:continue
        days[t.date()].append((t,h))
    result={}
    for date,observations in days.items():
        uniq={t:h for t,h in observations}
        if len(uniq)<MIN_SLOTS:continue
        quadrants=collections.Counter(t.hour//6 for t in uniq)
        if any(quadrants[q]<MIN_QUADRANT_SLOTS for q in range(4)):continue
        levels=list(uniq.values())
        result[date]={"range_m":max(levels)-min(levels),"mean_m":float(np.mean(levels)),
                      "slots":len(uniq)}
    return result

def reconstruct_original_v32_predictions(events, daily, v32_records):
    """Original scored target + reconstructed MH is checked at 1e-12 EVERY day."""
    bykey={(x["bird"],x["date"]):x for x in v32_records}
    if len(bykey)!=len(v32_records):raise ValueError("Original target duplicates")
    own=collections.defaultdict(lambda:collections.deque(maxlen=v32.MAX_OWN))
    full=[]
    for date, group in __import__("itertools").groupby(sorted(events,key=lambda e:(e[1],e[0])),key=lambda e:e[1]):
        block=list(group)
        for bird,_,y in block:
            v=bykey.get((bird,date))
            if v is None:continue
            past=list(own[bird])
            if len(past)!=v["n_past_own"]:
                raise ValueError("Original v32 history-count mismatch")
            prev=daily[bird,date-dt.timedelta(days=1)]
            mi=sum(past)/len(past)
            mh=.5*(prev+mi)
            errors=[(y-m)**2 for m in (prev,mi,mh)]
            if any(abs(a-b)>1e-12 for a,b in zip(errors,v["errors"][1:])):
                raise ValueError("Original v32 individual daily predictor receipt drift")
            full.append({"bird":bird,"date":date,"y":y,"mh":mh,
                         "original_v32_errors":v["errors"]})
        for bird,_,y in block:own[bird].append(y)
    if len(full)!=len(v32_records):raise ValueError("Original v32 matched target changed")
    return full

def check_v32_receipt(recomputed):
    original=json.loads(V32_RECEIPT.read_text())
    e=original["observed_outcome"]
    if (recomputed["status"]!=e["status"] or
        recomputed["independent_original_birds"]!=e["independent_original_birds"] or
        recomputed["future_original_bird_days"]!=e["future_original_bird_days"]):
        raise ValueError("Original v32 cohort/score status drift")
    def compare(a,b):
        if isinstance(a,dict):
            return isinstance(b,dict) and a.keys()==b.keys() and all(compare(a[k],b[k]) for k in a)
        if isinstance(a,list):
            return isinstance(b,list) and len(a)==len(b) and all(compare(x,y) for x,y in zip(a,b))
        if isinstance(a,float) and isinstance(b,(float,int)):
            return abs(a-b)<=1e-12
        return a==b
    if not compare(recomputed,e):raise ValueError("Frozen v32 full receipt mismatch")
    return {"status":"UNCHANGED_V32_36_BIRD_7086_DAYS_ALL_SCORE_FIELDS_MATCH",
            "original_birds":e["independent_original_birds"],
            "original_targets":e["future_original_bird_days"],
            "all_fields_verified_with_absolute_tolerance":1e-12}

def freeze_tide_features(original_rows,tide_days):
    out=[]
    missing=collections.Counter()
    for r in original_rows:
        date=r["date"]
        now=tide_days.get(date);prior=tide_days.get(date-dt.timedelta(days=1))
        future=tide_days.get(date+dt.timedelta(days=7))
        p_future=tide_days.get(date+dt.timedelta(days=6))
        if not now or not prior:
            missing["main_missing_daily_astronomical_range"]+=1;continue
        if not future or not p_future:
            missing["placebo_shift7_missing"]+=1;continue
        z=now["range_m"]-prior["range_m"]
        zfake=future["range_m"]-p_future["range_m"]
        if not (math.isfinite(z) and math.isfinite(zfake)):raise ValueError("Nonfinite tide range")
        doy=date.timetuple().tm_yday
        phi=2*math.pi*doy/365.25
        out.append({**r,"z":float(z),"z_shift":float(zfake),
                    "year_sin":math.sin(phi),"year_cos":math.cos(phi)})
    return out,dict(missing)

def predicted_errors(rows):
    """Use only PAST matched response residuals. Score full daily block at once."""
    counts=0
    a_z=RIDGE;b_z=0.
    a_fake=RIDGE;b_fake=0.
    a_season=RIDGE*np.eye(3);b_season=np.zeros(3)
    a_both=RIDGE*np.eye(4);b_both=np.zeros(4)
    result=[]
    for date, group in __import__("itertools").groupby(sorted(rows,key=lambda r:(r["date"],r["bird"])),key=lambda r:r["date"]):
        block=list(group)
        beta_z=b_z/a_z if counts>=WARMUP else 0.
        beta_fake=b_fake/a_fake if counts>=WARMUP else 0.
        beta_season=np.linalg.solve(a_season,b_season) if counts>=WARMUP else np.zeros(3)
        beta_both=np.linalg.solve(a_both,b_both) if counts>=WARMUP else np.zeros(4)
        for row in block:
            mh=row["mh"];z=row["z"];zf=row["z_shift"]
            xs=np.array([1.,row["year_sin"],row["year_cos"]])
            xb=np.array([1.,row["year_sin"],row["year_cos"],z])
            pred=[mh,mh+beta_z*z,mh+float(xs@beta_season),
                  mh+float(xb@beta_both),mh+beta_fake*zf]
            errors=[(row["y"]-v)**2 for v in pred]
            if abs(errors[0]-row["original_v32_errors"][3])>1e-12:
                raise ValueError("Changed frozen v32 MH squared error")
            result.append({"bird":row["bird"],"date":date,"errors":errors})
        for row in block:
            resid=row["y"]-row["mh"];z=row["z"];zf=row["z_shift"]
            xs=np.array([1.,row["year_sin"],row["year_cos"]])
            xb=np.array([1.,row["year_sin"],row["year_cos"],z])
            a_z+=z*z;b_z+=z*resid
            a_fake+=zf*zf;b_fake+=zf*resid
            a_season+=np.outer(xs,xs);b_season+=xs*resid
            a_both+=np.outer(xb,xb);b_both+=xb*resid
        counts+=len(block)
    return result,{"warmup_earlier_bird_days":WARMUP,
                   "initial_tide_ridge_diagonal":RIDGE,
                   "same_day_all_target_outcomes_embargoed":True,
                   "last_past_date_only_model_training":True}

def evaluate(forecasts):
    perbird=collections.defaultdict(list)
    for r in forecasts:perbird[r["bird"]].append(r["errors"])
    birds=sorted(perbird)
    if len(birds)<MIN_MATCHED_BIRDS or len(forecasts)<MIN_MATCHED_DAYS:
        return {"status":"NOT_ADMITTED_TIDE_MATCHED_SUPPORT",
                "matched_birds":len(birds),"matched_future_bird_days":len(forecasts),
                "any_tidal_forecast_scores_exported":False}
    matrix=np.array([np.mean(perbird[b],axis=0) for b in birds])
    means=matrix.mean(axis=0)
    samples=np.random.default_rng(BOOT_SEED).integers(0,len(birds),size=(BOOT_REPS,len(birds)))
    comparisons={}
    for name,i,j in zip(KEYS,(0,2,0),(1,3,4)):
        diff=matrix[:,i]-matrix[:,j]
        nplus=int(np.sum(diff>0));nnonzero=int(np.sum(diff!=0))
        comparisons[name]={
          "equal_bird_mean_MSE_gain":float(diff.mean()),
          "bird_bootstrap_95_percentile":list(map(float,
                 np.quantile(diff[samples].mean(axis=1),[.025,.975]))),
          "birds_positive":nplus,"birds_nonzero":nnonzero,"independent_original_bird_IDs":len(birds),
          "one_sided_bird_sign_tail":sum(math.comb(nnonzero,k) for k in range(nplus,nnonzero+1))/(2**nnonzero) if nnonzero else 1.,
          "original_bird_effects_anonymized":{f"bird_{ix+1:03d}":float(val) for ix,val in enumerate(diff)}
        }
    return {"status":"EXPLORATORY_RWS_ASTRONOMICAL_TIDE_FORECAST",
            "original_birds":len(birds),"common_future_bird_days":len(forecasts),
            "model_order":list(MODEL_ORDER),"mean_MSE":list(map(float,means)),
            "per_anonymous_bird_MSE":{f"bird_{i+1:03d}":{
               "n_future_days":len(perbird[b]),"MSE":list(map(float,matrix[i]))}
               for i,b in enumerate(birds)},
            "comparisons":comparisons,"whole_bird_bootstrap_replicates":BOOT_REPS,
            "seed":BOOT_SEED,
            "scores_are_post_v32_exploratory_source_specific":True}

def run():
    astronomy,year_qa=load_original_astronomy()
    daily_tide=daily_tide_range(astronomy)
    # Tide source and time support source-only before opening any new tide association.
    with tempfile.TemporaryDirectory() as d:
        files=v32.original_files_to_temp(Path(d))
        animal_daily,gps_qa=v32.read_original_daily(files)
    original_events=v32.candidate_events(animal_daily)
    v32_records,v32_qa=v32.predict(animal_daily,original_events)
    gate=check_v32_receipt(v32.evaluate(v32_records))
    orig=reconstruct_original_v32_predictions(original_events,animal_daily,v32_records)
    candidate,missing=freeze_tide_features(orig,daily_tide)
    if len(candidate)<MIN_MATCHED_DAYS or len({r["bird"] for r in candidate})<MIN_MATCHED_BIRDS:
        outcome={"status":"NOT_ADMITTED_TIDE_MATCHED_SUPPORT",
                 "matched_birds":len({r["bird"] for r in candidate}),
                 "matched_future_bird_days":len(candidate),
                 "any_tidal_forecast_scores_exported":False}
        prequential_qa=None
    else:
        scored,prequential_qa=predicted_errors(candidate)
        outcome=evaluate(scored)
    return {"status":outcome["status"],
            "source":"Rijkswaterstaat original waterwebservices WATHTE Schiermonnikoog Waddenzee, astronomical cm NAP",
            "source_url":"https://rijkswaterstaatdata.nl/waterdata/",
            "source_station":STATION,"source_years":list(YEARS),
            "source_annual_quality":year_qa,
            "source_daily_complete_astronomical_days":len(daily_tide),
            "source_UTC_time_transform":"RWS returned explicit Dutch fixed +01:00 → UTC",
            "v32_frozen_original_replay":gate,
            "same_original_v32_GPS_source_quality":gps_qa,
            "v32_target_quality":v32_qa,
            "tide_animal_match": {
                "original_v32_bird_days":len(orig),
                "matched_identical_future_days":len(candidate),
                "original_birds_in_matched":len({r["bird"] for r in candidate}),
                "missing":missing},
            "prequential_model_support":prequential_qa,
            "observed_outcome":outcome,
            "no_original_GPS_positions_dates_IDs_or_daily_source_heights_redistributed":True,
            "science_caution":[
              "Exploratory tide analysis within already opened v32 oystercatcher GPS source",
              "Astronomical model at one gauge is tidal forcing proxy, not measured bird food accessibility",
              "Future tide amplitude computed astronomically, not actual future storm-surge water levels",
              "Only one coastal bird site; same-site bird bootstrap cannot prove generality",
              "Daily tidal range does not capture semidiurnal exposure/foraging phase timing",
              "No Boids social-force or cognitive learning causal identification"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v33/results/oystercatcher_tide_forecast_v33.json"))
    args=ap.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
             prefix=".v33-",delete=False) as temp:
        temp.write(content);p=Path(temp.name)
    os.replace(p,args.out)
    print("V33_TIDE_SOURCE_COUNTS",json.dumps(result["source_annual_quality"],sort_keys=True))
    print("V33_FROZEN_V32_REPLAY",json.dumps(result["v32_frozen_original_replay"],sort_keys=True))
    print("V33_TIDE_MATCH",json.dumps(result["tide_animal_match"],sort_keys=True))
    print("V33_TIDAL_FORECAST_STATUS",result["status"])
    if result["observed_outcome"].get("comparisons"):
        print("V33_ALL_TIDE_COMPARISONS",json.dumps(
             {k:{a:b for a,b in v.items() if a!="original_bird_effects_anonymized"}
                 for k,v in result["observed_outcome"]["comparisons"].items()},sort_keys=True))
    else:
        print("V33_NO_TIDAL_SCORES",json.dumps(result["observed_outcome"],sort_keys=True))
    print("V33_AGGREGATE_JSON",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
