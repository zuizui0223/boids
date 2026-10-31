#!/usr/bin/env python3
"""v33-D: matched UTC-hour×year-month within-bird HIGH-vs-LOW tide GPS step speed.

An explicitly exploratory contemporaneous observation analysis (not a
prospective GPS destination forecast), independently frozen before joining.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import gzip
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"validation_v32"))
import forecast as v32
import tidal_forecast as tide

STATION_LAT=53.468937
STATION_LON=6.202908
LOCAL_RADIUS_KM=25.0
MIN_PAIR_MINUTES=5.
MAX_PAIR_MINUTES=180.
MIN_CATEGORY_PER_STRATUM=2
MIN_STRATA_PER_BIRD=8
MIN_BIRDS=20
MIN_TOTAL_PAIRED_STRATA=200
BOOT_REPS=10000
SEED=20261031
PROTOCOL="docs/V33D_SUBDAILY_TIDE_MOVEMENT_ASSOCIATION_PROTOCOL.md"
EPOCH=dt.datetime(1970,1,1)

def haversine_km(lat1,lon1,lat2,lon2):
    r=6371.0088
    a1,a2=math.radians(lat1),math.radians(lat2)
    da=a2-a1
    dl=math.radians(lon2-lon1)
    a=math.sin(da/2)**2 + math.cos(a1)*math.cos(a2)*math.sin(dl/2)**2
    return r*2*math.asin(min(1.,math.sqrt(max(a,0.))))

def nearest_tide_key(t):
    seconds=(t-EPOCH).total_seconds()
    bucket=math.floor(seconds/600.+.5-1e-10)
    result=EPOCH+dt.timedelta(minutes=10*bucket)
    if abs((t-result).total_seconds())>300.001:
        raise ValueError("No valid 10 minute tide time within 5min")
    return result

def read_original_valid_gps(paths):
    """Mirrors v32 quality; drops ALL source bird+UTC duplicates."""
    points=[]
    original_counts=collections.Counter()
    source_taxa={}
    for path in paths:
        with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f)
            if tuple(reader.fieldnames or ())!=v32.EXPECTED_FIELDS:
                raise ValueError("Frozen v32 source header changed")
            for row in reader:
                original_counts["original_rows"]+=1
                bird=str(row.get("individual-local-identifier") or "").strip()
                taxon=str(row.get("individual-taxon-canonical-name") or "").strip()
                if not bird or not taxon:
                    original_counts["missing_ID_taxon"]+=1;continue
                if bird in source_taxa and source_taxa[bird]!=taxon:
                    raise ValueError("Source original bird taxon changed")
                source_taxa[bird]=taxon
                try:
                    stamp=v32.parse_timestamp(row.get("timestamp"))
                    visible=v32.flag_true(row.get("visible"))
                    outlier=v32.flag_true(row.get("manually-marked-outlier"),blank_false=True)
                except (TypeError,ValueError):
                    raise ValueError("Original source flag or UTC grammar changed")
                if visible is not True or outlier is True:
                    original_counts["source_flags_excluded"]+=1;continue
                try:
                    lat=float(row.get("location-lat"))
                    lon=float(row.get("location-long"))
                except (ValueError,TypeError):
                    original_counts["invalid_GPS"]+=1;continue
                if not all(map(math.isfinite,(lat,lon))) or abs(lat)>90 or abs(lon)>180:
                    original_counts["invalid_GPS"]+=1;continue
                points.append((bird,stamp,lat,lon))
    if original_counts["original_rows"]!=v32.SOURCE_ROWS or len(source_taxa)!=v32.SOURCE_BIRDS:
        raise ValueError("Original v32 source row/identity receipt drift")
    return points,dict(original_counts)

def source_level_quartiles(astronomy):
    allheights=[v for t,v in astronomy.items() if t.year in tide.YEARS]
    if len(allheights)<300000:
        raise ValueError("No complete original astronomical tide height coverage")
    q1,q3=np.quantile(allheights,[.25,.75])
    if not (-10<float(q1)<float(q3)<10):
        raise ValueError("Implausible source-only astronomical tide quartiles")
    return float(q1),float(q3)

def original_step_strata(points, astronomy, q1,q3):
    """No animal IDs/time/positions leave memory; aggregate matched stratum scores."""
    seen=collections.Counter((r[0],r[1]) for r in points)
    points=sorted((p for p in points if seen[p[0],p[1]]==1),key=lambda p:(p[0],p[1]))
    qa=collections.Counter()
    qa["accepted_original_fix_before_duplicate_gate"]=sum(seen.values())
    qa["all_dropped_original_duplicate_fix_rows"]=sum(n for n in seen.values() if n>1)
    strata=collections.defaultdict(lambda:[[],[]])
    for bird, group in itertools.groupby(points,key=lambda p:p[0]):
        prior=None
        for item in group:
            if prior is None:
                prior=item;continue
            _,stamp,lat,lon=item
            _,ps,plat,plon=prior
            prior=item
            elapsed=(stamp-ps).total_seconds()/60.
            if not MIN_PAIR_MINUTES<=elapsed<=MAX_PAIR_MINUTES:
                qa["original_pairs_excluded_by_duration"]+=1;continue
            if (haversine_km(lat,lon,STATION_LAT,STATION_LON)>LOCAL_RADIUS_KM or
                haversine_km(plat,plon,STATION_LAT,STATION_LON)>LOCAL_RADIUS_KM):
                qa["source_pairs_excluded_outside_25km_station"]+=1;continue
            middle=ps+(stamp-ps)/2
            h=astronomy.get(nearest_tide_key(middle))
            if h is None:
                qa["source_pairs_excluded_missing_RWS_10min_tide"]+=1;continue
            qa["pairs_with_valid_RWS_tide_and_local_GPS"]+=1
            if h<=q1:cat=0
            elif h>=q3:cat=1
            else:
                qa["pairs_middle_tide_excluded_fixed_quartiles"]+=1;continue
            speed=haversine_km(plat,plon,lat,lon)/(elapsed/60.)
            if speed>100:qa["original_step_speed_over_100_kmh_descriptive"]+=1
            response=math.log1p(speed)
            if not math.isfinite(response):raise ValueError("Nonfinite GPS movement speed")
            key=(bird,middle.year,middle.month,middle.hour)
            strata[key][cat].append(response)
            qa["source_pairs_tide_top_bottom_quartiles"]+=1
    per_bird=collections.defaultdict(list)
    for (bird,year,month,hr),(low,high) in strata.items():
        if len(low)>=MIN_CATEGORY_PER_STRATUM and len(high)>=MIN_CATEGORY_PER_STRATUM:
            per_bird[bird].append({"difference":float(np.mean(high)-np.mean(low)),
                                  "n_high":len(high),"n_low":len(low)})
            qa["accepted_paired_bird_month_hour_strata"]+=1
        else:qa["unpaired_or_insufficient_clock_month_strata"]+=1
    return per_bird,dict(qa)

def evaluate(perbird):
    admitted={b:v for b,v in perbird.items() if len(v)>=MIN_STRATA_PER_BIRD}
    n_birds=len(admitted)
    n_strata=sum(len(v) for v in admitted.values())
    support={"birds_with_minimum_clock_matched_strata":n_birds,
             "paired_original_bird_month_hour_strata":n_strata,
             "minimum_strata_per_bird":MIN_STRATA_PER_BIRD,
             "minimum_birds":MIN_BIRDS,"minimum_total_strata":MIN_TOTAL_PAIRED_STRATA}
    if n_birds<MIN_BIRDS or n_strata<MIN_TOTAL_PAIRED_STRATA:
        return {"status":"NOT_ADMITTED_WITHIN_BIRD_TIDE_HOUR_MATCHING",
                "support":support,"any_ecological_tide_effect_exported":False}
    birds=sorted(admitted)
    effects=np.array([np.mean([e["difference"] for e in admitted[b]]) for b in birds])
    resamples=np.random.default_rng(SEED).integers(0,len(birds),
                                    size=(BOOT_REPS,len(birds)))
    npos=int(np.sum(effects>0));nn=int(np.sum(effects!=0))
    ci=np.quantile(effects[resamples].mean(axis=1),[.025,.975])
    return {"status":"EXPLORATORY_ORIGINAL_HIGH_VS_LOW_TIDE_LOCAL_SPEED_ASSOCIATION",
            "support":support,"all_birds_equally_weighted":True,
            "fixed_comparison":"high astronomical RWS tide water-level quartile minus low",
            "response":"log1p(haversine_displacement_km_per_hour)",
            "mean_high_minus_low_log_speed":float(effects.mean()),
            "bird_bootstrap_95_interval":list(map(float,ci)),
            "birds_with_higher_speed_at_high_tide":npos,
            "birds_with_lower_speed_at_high_tide":int(np.sum(effects<0)),
            "n_nonzero_birds":nn,
            "one_sided_positive_sign_p":sum(math.comb(nn,i) for i in range(npos,nn+1))/(2**nn) if nn else 1.,
            "equal_bird_median_effect":float(np.median(effects)),
            "original_bird_effects_anonymized":{f"bird_{i+1:03d}":{
                "paired_hour_month_strata":len(admitted[b]),
                "high_minus_low_mean_log_speed":float(effects[i]),
                "high_tide_original_steps_in_matched_strata":sum(x["n_high"] for x in admitted[b]),
                "low_tide_original_steps_in_matched_strata":sum(x["n_low"] for x in admitted[b])
              } for i,b in enumerate(birds)},
            "boot_reps":BOOT_REPS,"seed":SEED,
            "study_count":1,"causal_mechanism_inferred":False}

def run():
    astro,year_qa=tide.load_original_astronomy()
    q1,q3=source_level_quartiles(astro)
    with tempfile.TemporaryDirectory() as root:
        files=v32.original_files_to_temp(Path(root))
        points,source_qa=read_original_valid_gps(files)
    strata,steps_qa=original_step_strata(points,astro,q1,q3)
    result=evaluate(strata)
    return {"status":result["status"],"source":tide.STATION,
            "tide_series_type":"astronomical WATHTE cm relative NAP from Rijkswaterstaat",
            "source_years":list(tide.YEARS),
            "astronomical_tide_year_coverage":year_qa,
            "tidal_source_only_high_low_quartiles_m_NAP":{"low_q25":q1,"high_q75":q3},
            "source_data_quality":source_qa,
            "geographic_and_clock_month_tide_pair_audit":steps_qa,
            "observed_association":result,
            "protocol":PROTOCOL,
            "only_GPS_within_25km_of_original_tide_station_analyzed":True,
            "time_zone":"GPS original UTC, RWS explicit +01:00 converted to UTC",
            "no_animal_GPS_IDs_positions_or_timestamps_exported":True,
            "previous_v32_results_unchanged":True,
            "interpretation_limits":[
                "Post-v32 exploratory same animal dataset, new independently observed astronomical tide source",
                "Movement speed is not proof of foraging, roosting, food intake or actual mudflat accessibility",
                "GPS sampling regimes, tidal geography and wind/time confound remaining",
                "Fixed local station water height may differ from waterlines at each GPS position",
                "This is contemporaneous environmental association, NOT a future-location forecast",
                "No evidence about learned memory, Reynolds force or 3D ecological niche partition"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v33/results/oystercatcher_tide_speed_v33.json"))
    args=ap.parse_args()
    out=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+"\n"
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",dir=args.out.parent,
        prefix=".v33phase-",delete=False) as temp:
        temp.write(data);p=Path(temp.name)
    os.replace(p,args.out)
    print("V33_SUBDAILY_SOURCE",json.dumps(out["tidal_source_only_high_low_quartiles_m_NAP"],sort_keys=True))
    print("V33_SUBDAILY_SUPPORT",json.dumps(out["geographic_and_clock_month_tide_pair_audit"],sort_keys=True))
    print("V33_SUBDAILY_STATUS",out["status"])
    if out["observed_association"].get("mean_high_minus_low_log_speed") is not None:
        print("V33_SUBDAILY_EFFECT",json.dumps({k:v for k,v in out["observed_association"].items()
            if k!="original_bird_effects_anonymized"},sort_keys=True))
    else:print("V33_SUBDAILY_NO_EFFECT_SCORED",json.dumps(out["observed_association"],sort_keys=True))
    print("V33_SUBDAILY_AGGREGATE_JSON",json.dumps(out,sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
