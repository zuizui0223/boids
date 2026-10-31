#!/usr/bin/env python3
"""v32 independent original oystercatcher GPS day-ahead spatial spread forecast.

This is a single independent-source, fixed-predictor test. Previous wild duck
results v23/v29/v30 were known, and v31 time-only source STOP is preserved.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import tempfile
import urllib.request

import numpy as np

RECORD=10053970
LABEL="O_SCHIERMONNIKOOG"
SOURCE_ROWS=602396
SOURCE_BIRDS=39
EXPECTED_FIELDS=("event-id","visible","timestamp","location-long","location-lat","bar:barometric-pressure",
                 "external-temperature","gps:dop","gps:satellite-count","gps-time-to-fix","ground-speed",
                 "heading","height-above-msl","import-marked-outlier","location-error-numerical",
                 "manually-marked-outlier","vertical-error-numerical","sensor-type",
                 "individual-taxon-canonical-name","tag-local-identifier",
                 "individual-local-identifier","study-name")
# Original v31 SOURCE-ONLY MD5+SHA256 receipts, frozen before any GPS coordinates were read.
PINS={
2008:(661210,"2624a15e124450f54ddc5a4b5c5fce91","ce27f90122193f2efd6ecc2ffa83a9d2c442706df2c68bc4447efc0d1376525f"),
2009:(2171293,"1967bdcd6a4720c63bb986abdaf48ab0","794d1a6f817b0254c917534845649a17b8b2b61af52e45c15016645e8b1129af"),
2010:(14272442,"0f1c603a285f1980a5b4ee962e2e28ad","8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d"),
2011:(9392944,"610e3edb48bda7d922d63978feb22ac1","297938bade48ca5502a4325105a64f0d6e0124a268bbcf2caa49676449f7946f"),
2012:(1406855,"a2ccce5afe2a6cad09a27e2957beacaf","f9935a50a9b557795ecf38ebd77890f52566b8e9d6c5a6650b46b18b6cb6d3d0"),
2013:(200336,"6137d93ee58289fc8a5e2163aa4c05fc","9b355d9760984a82fa386ac191d5177b81491b9f34416ce0edb2c72b8e9da157"),
2014:(508350,"21e7fda801096449e6974f616d6dedd9","2819c3013f229ab65b2c58ebdc361b538767168238100825a7fc31136013a032")
}
META_URL=f"https://zenodo.org/api/records/{RECORD}"
MAX_META_BYTES=2_000_000
MAX_ORIGINAL_BYTES=20_000_000
MIN_DAY_FIXES=6
MIN_DAY_HOURS=8.
MIN_OWN=3
MAX_OWN=14
MIN_OTHER=5
MIN_OTHER_DAYS=20
MIN_ELIGIBLE_BIRDS=20
MIN_TARGET_DAYS=500
BOOT_REPS=10000
BOOT_SEED=20261031
MODELS=("M0","MP","MI","MH")
PROTOCOL="docs/V32_OYSTERCATCHER_FORECAST_PROTOCOL.md"
USER_AGENT="boids-v32-original-oystercatcher-source/1.0"

def parse_timestamp(text):
    """Original ISO UTC (may have milliseconds or Z); reject non-UTC offsets."""
    val=str(text or "").strip().replace("Z","+00:00").replace(" ","T")
    if not val: raise ValueError("Missing source timestamp")
    out=dt.datetime.fromisoformat(val)
    if out.tzinfo is not None:
        if out.utcoffset()!=dt.timedelta(0): raise ValueError("Non-UTC source time")
        out=out.replace(tzinfo=None)
    return out

def flag_true(value, *, blank_false=False):
    val=str(value or "").strip().casefold()
    if val in ("true","1","t"):return True
    if val in ("false","0","f"):return False
    if blank_false and not val:return False
    if not val:return None
    raise ValueError("Unrecognized source Boolean observation flag")

def original_manifest():
    req=urllib.request.Request(META_URL,headers={"User-Agent":USER_AGENT,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=45) as res: raw=res.read(MAX_META_BYTES+1)
    if len(raw)>MAX_META_BYTES: raise ValueError("Source metadata exceeded cap")
    data=json.loads(raw)
    if data.get("id")!=RECORD:raise ValueError("Original Zenodo record ID changed")
    files=data.get("files") or []
    if isinstance(files,dict): files=list((files.get("entries") or {}).values())
    selected={}
    for f in files:
        name=f.get("key") or f.get("filename") or ""
        mo=re.fullmatch(re.escape(LABEL)+r"-gps-(\d{4})\.csv\.gz",name)
        if not mo:continue
        year=int(mo.group(1))
        if year not in PINS or year in selected:raise ValueError("Unexpected source GPS year")
        size,md5,_=PINS[year]
        if f.get("size")!=size or f.get("checksum")!=f"md5:{md5}":
            raise ValueError("Original source provider manifest drift")
        url=(f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
        if not isinstance(url,str) or not url.startswith("https://zenodo.org/"):
            raise ValueError("Original GPS origin not approved Zenodo")
        selected[year]=(url,name)
    if sorted(selected)!=sorted(PINS): raise ValueError("Missing mandatory original GPS-year gzip")
    return selected

def original_files_to_temp(tmp):
    meta=original_manifest()
    paths=[]
    for year in sorted(PINS):
        url,name=meta[year]
        expected_size,expected_md5,expected_sha=PINS[year]
        path=tmp/name
        req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
        md5,sha=hashlib.md5(),hashlib.sha256()
        length=0
        with urllib.request.urlopen(req,timeout=120) as response,path.open("wb") as output:
            for chunk in iter(lambda:response.read(1048576),b""):
                length+=len(chunk)
                if length>MAX_ORIGINAL_BYTES:raise ValueError("Original file size over cap")
                output.write(chunk);md5.update(chunk);sha.update(chunk)
        if (length!=expected_size or md5.hexdigest()!=expected_md5 or
            sha.hexdigest()!=expected_sha):raise ValueError("Frozen original MD5/SHA/size mismatch")
        paths.append(path)
    return paths

def read_original_daily(paths):
    """Original tag ID/time/quality/position parsed only after frozen code tests."""
    seen=collections.Counter()
    candidates=collections.defaultdict(list)
    recorded_studies=collections.defaultdict(set)
    known_taxa={}
    qa=collections.Counter()
    for p in paths:
        with gzip.open(p,"rt",encoding="utf-8-sig",newline="") as inp:
            rd=csv.DictReader(inp)
            if tuple(rd.fieldnames or ())!=EXPECTED_FIELDS:
                raise ValueError("Source-only verified original header drift")
            for row in rd:
                qa["original_physical_rows"]+=1
                bird=str(row.get("individual-local-identifier") or "").strip()
                taxon=str(row.get("individual-taxon-canonical-name") or "").strip()
                study=str(row.get("study-name") or "").strip()
                if not bird or not taxon or not study:
                    qa["missing_original_ID_taxon_or_study_rows"]+=1;continue
                if bird in known_taxa and known_taxa[bird]!=taxon:
                    raise ValueError("Source original bird changes taxonomic ID")
                known_taxa[bird]=taxon
                recorded_studies[bird].add(study)
                try:stamp=parse_timestamp(row.get("timestamp"))
                except (ValueError,TypeError):
                    qa["invalid_source_UTC_rows"]+=1;continue
                key=(bird,stamp)
                seen[key]+=1
                try:
                    visible=flag_true(row.get("visible"))
                    outlier=flag_true(row.get("manually-marked-outlier"),blank_false=True)
                except ValueError:
                    raise ValueError("Source visibility/outlier flag grammar unknown")
                if visible is not True:
                    qa["not_source_visible_rows"]+=1;continue
                if outlier is True:
                    qa["manually_marked_outlier_rows"]+=1;continue
                try:
                    lat=float(row["location-lat"]);lon=float(row["location-long"])
                    if not (math.isfinite(lat) and math.isfinite(lon) and
                            -90<=lat<=90 and -180<=lon<=180):
                        raise ValueError("Invalid WGS84")
                except (KeyError,TypeError,ValueError):
                    qa["invalid_original_WGS84_rows"]+=1;continue
                candidates[key].append((lat,lon))
                qa["source_visible_valid_coordinate_rows"]+=1
    if qa["original_physical_rows"]!=SOURCE_ROWS:raise ValueError("Original source GPS row count drift")
    if len(known_taxa)!=SOURCE_BIRDS:raise ValueError("Frozen original source-only ID total drift")
    if any(len(studies)!=1 for studies in recorded_studies.values()):
        raise ValueError("One source bird changes original study label")
    if len({next(iter(x)) for x in recorded_studies.values()})!=1:
        raise ValueError("Multiple original study names in fixed single-study source")
    byday=collections.defaultdict(list)
    dup=0
    for (bird,stamp),locations in candidates.items():
        if seen[bird,stamp]!=1:
            dup+=len(locations)
            continue
        if len(locations)!=1:
            raise ValueError("Original timestamp mapped to multiple acceptable values")
        lat,lon=locations[0]
        byday[bird,stamp.date()].append((stamp,lat,lon))
    # Some duplicated rows could have failed GPS QC; count all original duplicated timestamps.
    qa["original_source_duplicate_ID_UTC_keys"]=sum(v>1 for v in seen.values())
    qa["visible_valid_coordinate_rows_dropped_for_duplicate_UTC"]=dup
    days={}
    for (bird,date),fixes in byday.items():
        if len(fixes)<MIN_DAY_FIXES:continue
        fixes.sort(key=lambda q:q[0])
        span=(fixes[-1][0]-fixes[0][0]).total_seconds()/3600
        if span<MIN_DAY_HOURS: continue
        meanlat=sum(p[1] for p in fixes)/len(fixes)
        meanlon=sum(p[2] for p in fixes)/len(fixes)
        c=111.2*math.cos(math.radians(meanlat))
        r2=sum(((p[1]-meanlat)*111.2)**2+((p[2]-meanlon)*c)**2
               for p in fixes)/len(fixes)
        r=math.sqrt(r2)
        if not math.isfinite(r):raise ValueError("Nonfinite source radius-of-gyration")
        days[bird,date]=math.log1p(r)
    qa["complete_original_GPS_days"]=len(days)
    qa["source_birds_with_complete_GPS_days"]=len({bird for bird,_ in days})
    qa["original_source_distinct_birds"]=len(known_taxa)
    qa["source_unique_study_count"]=1
    qa["GPS_original_gps_dop_is_not_hdop_and_not_thresholded"]=True
    qa["source_gps_altitude_or_wind_exposure_not_used"]=True
    qa["GPS_interpolation_used"]=False
    return days,dict(qa)

def candidate_events(days):
    return [(bird,date,days[bird,date])
            for bird,date in days if (bird,date-dt.timedelta(days=1)) in days]

def predict(days,events):
    """All future observations from t are embargoed until t is scored."""
    own=collections.defaultdict(lambda:collections.deque(maxlen=MAX_OWN))
    external=collections.defaultdict(list)
    out=[]
    qa=collections.Counter()
    by_date=collections.defaultdict(list)
    for bird,date,val in events:by_date[date].append((bird,val))
    for date in sorted(by_date):
        block=by_date[date]
        for bird,y in block:
            qa["candidate_days"]+=1
            past=list(own[bird])
            if len(past)<MIN_OWN:
                qa["insufficient_own_history"]+=1;continue
            other=[sum(xs)/len(xs) for b,xs in external.items() if b!=bird and xs]
            other_days=sum(len(xs) for b,xs in external.items() if b!=bird)
            if len(other)<MIN_OTHER or other_days<MIN_OTHER_DAYS:
                qa["insufficient_other_bird_history"]+=1;continue
            prev=days.get((bird,date-dt.timedelta(days=1)))
            if prev is None:raise ValueError("No exact prior complete GPS day")
            mi=sum(past)/len(past)
            m0=sum(other)/len(other)
            mp=prev
            mh=(mp+mi)/2.
            errors=[(y-est)**2 for est in (m0,mp,mi,mh)]
            if any(not math.isfinite(v) for v in errors):
                raise ValueError("Nonfinite original prediction error")
            out.append({"bird":bird,"date":date,"errors":errors,
                        "n_past_own":len(past)})
        for bird,y in block:
            external[bird].append(y)
            own[bird].append(y)
    qa["common_future_days_scored"]=len(out)
    qa["common_future_birds_scored"]=len({x["bird"] for x in out})
    qa["same_date_or_future_animal_uses_in_training"]=0
    return out,dict(qa)

def sign_tail(k,n):
    return sum(math.comb(n,i) for i in range(k,n+1))/(2**n) if n else 1.

def evaluate(rows):
    bybird=collections.defaultdict(list)
    for r in rows:bybird[r["bird"]].append(r)
    count=len(bybird);n=len(rows)
    if count<MIN_ELIGIBLE_BIRDS or n<MIN_TARGET_DAYS:
        return {"status":"NOT_ADMITTED_ORIGINAL_INDEPENDENT_GPS_QUALITY_SUPPORT",
                "candidate_birds":count,"candidate_bird_days":n,"any_model_scores_exported":False}
    names=sorted(bybird)
    perbird={}
    matrix=[]
    for i,b in enumerate(names,1):
        rs=bybird[b]
        errors=np.array([x["errors"] for x in rs],dtype=float)
        mean=errors.mean(axis=0)
        matrix.append(mean)
        perbird[f"bird_{i:03d}"]={"future_days_scored":len(rs),
                                "original_gps_day_MSE_M0_MP_MI_MH":list(map(float,mean))}
    matrix=np.array(matrix)
    if not np.isfinite(matrix).all():raise ValueError("Nonfinite score matrix")
    rng=np.random.default_rng(BOOT_SEED)
    boot=rng.integers(0,count,size=(BOOT_REPS,count))
    comparisons={}
    for title,i,j in [
        ("PRIMARY_MP_minus_MH",1,3),("secondary_M0_minus_MP",0,1),
        ("secondary_MP_minus_MI",1,2)]:
        diff=matrix[:,i]-matrix[:,j]
        positive=int((diff>0).sum());nonzero=int((diff!=0).sum())
        comparisons[title]={
            "equal_original_bird_mean_MSE_gain":float(diff.mean()),
            "individual_bootstrap_95_percentile":list(map(float,np.quantile(
                 diff[boot].mean(axis=1),[.025,.975]))),
            "positive_original_bird_IDs":positive,
            "nonzero_original_bird_IDs":nonzero,
            "independent_original_birds":count,
            "exact_one_sided_bird_sign_p":sign_tail(positive,nonzero)}
    return {"status":"EXPLORATORY_INDEPENDENT_ORIGINAL_OYSTERCATCHER_NEXT_DAY_FORECAST",
            "independent_original_birds":count,"future_original_bird_days":n,
            "mean_MSE_M0_MP_MI_MH":list(map(float,matrix.mean(axis=0))),
            "model_order":list(MODELS),"all_frozen_comparisons":comparisons,
            "anonymized_original_bird_scores":perbird,
            "whole_original_bird_bootstrap_reps":BOOT_REPS,
            "boot_seed":BOOT_SEED,"all_models_on_same_future_day_targets":True,
            "no_raw_original_bird_IDs_locations_or_UTC_events_exported":True}

def run():
    with tempfile.TemporaryDirectory() as d:
        paths=original_files_to_temp(Path(d))
        days,source_qa=read_original_daily(paths)
        events=candidate_events(days)
        scored,forecast_qa=predict(days,events)
        outcome=evaluate(scored)
    return {"status":outcome["status"],
            "study":"v32-independent-oystercatcher-single-original-source-day-ahead-GPS-spread",
            "registered_source":"Zenodo 10053970 version v4; all GPS years 2008-2014",
            "registered_protocol":PROTOCOL,
            "source_only_prior_original_ID_UTC_audit":"v31 source-only STOP at 0ba9d18fdf7d0124da871bcce281ce9e50a07430",
            "original_source_pins":{str(year):{"bytes":p[0],"md5":p[1],"sha256":p[2]}
                                    for year,p in sorted(PINS.items())},
            "original_source_quality":source_qa,
            "eligibility":forecast_qa,
            "observed_outcome":outcome,
            "original_v31_two_site_STOP_remains_frozen":True,
            "v23_v29_v30_results_unchanged":True,
            "no_original_individual_ID_UTC_location_or_daily_response_exported":True,
            "limitations":[
                "One new original species/source but a SINGLE nonrandom coastal field study",
                "A positive 50/50 hybrid cannot distinguish learning from repeated environment or GPS measurement noise",
                "No measured actual resource use, social contacts, weather/tide predictors, 3D niche or Boids force",
                "Future-day forecasts for already tracked individual birds only",
                "Whole-bird bootstrap does not provide independent geographic or weather replication"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v32/results/oystercatcher_independent_v32.json"))
    args=ap.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
         prefix=".v32-",delete=False) as temp:
        temp.write(data);temp_path=Path(temp.name)
    os.replace(temp_path,args.out)
    print("V32_SOURCE_QUALITY",json.dumps(out["original_source_quality"],sort_keys=True))
    print("V32_ELIGIBILITY",json.dumps(out["eligibility"],sort_keys=True))
    print("V32_STATUS",out["status"])
    if out["observed_outcome"].get("all_frozen_comparisons"):
        print("V32_ALL_FROZEN_COMPARISONS",json.dumps(out["observed_outcome"]["all_frozen_comparisons"],sort_keys=True))
    else:
        print("V32_NO_MODEL_SCORES",json.dumps(out["observed_outcome"],sort_keys=True))
    print("V32_AGGREGATE_JSON",json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
