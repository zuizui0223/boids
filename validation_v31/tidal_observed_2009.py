"""v31 real 2009 oystercatcher GPS × measured Waddenzee tide phase.

OBSERVED movement and tide but exploratory clock/representative-gauge uncertainty.
Retrospective association, not causal exposure-front tracking or Boids forces.
Protocol: docs/V31_FROZEN_OBSERVED_2009_TIDAL_PHASE.md
"""
from __future__ import annotations
import argparse, csv, gzip, json, math, random, sys, tempfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from bisect import bisect_left
import numpy as np

from source_preflight import download_and_pin, parse_stamp, haversine_m
from rws_source_probe import ROOT, WATHTE, post_json
from tidal_front import TideSeries

UTC=timezone.utc
ONE_HOUR=timezone(timedelta(hours=1))
STATION="schiermonnikoog.waddenzee"
FIRST=datetime(2009,5,18,tzinfo=ONE_HOUR)
LAST=datetime(2010,1,2,tzinfo=ONE_HOUR)

def get_gauge(start=FIRST, end=LAST, request=post_json):
    """Receive original 10-min gauge readings, never silently mix NAP/LAT."""
    samples={}
    t=start
    chunks=0
    total_received=0
    while t<end:
        hi=min(t+timedelta(days=14), end)
        payload={"Locatie":{"Code":STATION},
                 "AquoPlusWaarnemingMetadata":{"AquoMetadata":dict(WATHTE,ProcesType="meting")},
                 "Periode":{"Begindatumtijd":t.strftime("%Y-%m-%dT%H:%M:%S.000+01:00"),
                            "Einddatumtijd":hi.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")}}
        result=request("/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen",payload)
        if result.get("Succesvol") is not True:
            raise ValueError("RWS returned explicit unsuccessful status")
        group=result.get("WaarnemingenLijst") or []
        if len(group)!=1:
            raise ValueError("Unexpected number of RWS source station series for 14-day chunk")
        row=group[0]
        meta=row.get("AquoMetadata") or {}
        if (meta.get("Eenheid") or {}).get("Code")!="cm":
            raise ValueError("STOP: measured water unit is not cm")
        if "NAP" not in str((meta.get("Hoedanigheid") or {}).get("Code","")).upper():
            raise ValueError("STOP: measured water reference is not NAP")
        if (meta.get("Grootheid") or {}).get("Code")!="WATHTE":
            raise ValueError("STOP: source measurement is not WATHTE")
        measurements=row.get("MetingenLijst") or []
        if not measurements:raise ValueError("RWS historical water level chunk has zero observations")
        for item in measurements:
            original=datetime.fromisoformat(item["Tijdstip"].replace("Z","+00:00"))
            if original.tzinfo is None or original.utcoffset()!=timedelta(hours=1):
                raise ValueError("RWS timestamp must be fixed UTC+01, never Dutch DST")
            stamp=original.astimezone(UTC)
            value=float((item.get("Meetwaarde") or {})["Waarde_Numeriek"])
            if not math.isfinite(value) or abs(value)>500:
                continue # documented sentinels/implausible measurements not treated as tide
            if stamp in samples and abs(samples[stamp]-value/100)>1e-8:
                raise ValueError("Inconsistent overlapping original RWS gauge samples")
            samples[stamp]=value/100
            total_received+=1
        chunks+=1;t=hi
    if len(samples)<10000:
        raise ValueError("Fewer than 10,000 real NAP gauge values")
    ordered=sorted(samples.items())
    data=TideSeries(ordered,datum="NAP_m",provenance="observed")
    gaps=[(b[0]-a[0]).total_seconds()/60 for a,b in zip(ordered,ordered[1:])]
    audit={"source":"RWS_DDAPI2_original_WATHTE_observed",
           "station_code":STATION,"station_not_identically_confirmed_to_Dryad":True,
           "unit":"m_after_cm_divided_by_100","datum":"NAP",
           "fixed_original_timestamp_offset":"+01:00",
           "n_request_chunks":chunks,"original_values_received_including_boundary_duplicates":total_received,
           "unique_valid_water_observations":len(samples),
           "n_interval_gaps_over_30_minutes":sum(z>30 for z in gaps),
           "largest_gap_minutes":max(gaps) if gaps else None,
           "first_time_utc":ordered[0][0].isoformat(),
           "last_time_utc":ordered[-1][0].isoformat(),
           "water_level_min_max_nap_m":[min(samples.values()),max(samples.values())]}
    return data,audit

def read_gps(path):
    fixes=defaultdict(list)
    nraw=0;reason=Counter();events=set()
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh)
        required={"event-id","timestamp","location-lat","location-long","individual-local-identifier"}
        if not required <= set(reader.fieldnames or []):
            raise ValueError("Original GPS missing required original field schema")
        for row in reader:
            nraw+=1
            eid=row["event-id"]; ident=row["individual-local-identifier"]
            if not eid or eid in events:
                reason["event_missing_or_duplicate"]+=1;continue
            events.add(eid)
            if not ident:
                reason["missing_individual"]+=1;continue
            if row.get("visible","").upper() in ("FALSE","0"):
                reason["not_visible"]+=1;continue
            try:
                lat=float(row["location-lat"]);lon=float(row["location-long"])
                tm=parse_stamp(row["timestamp"])
            except (ValueError,TypeError):
                reason["unreadable_fix"]+=1;continue
            if not(math.isfinite(lat) and math.isfinite(lon) and 53.2<=lat<=53.7 and 5.7<=lon<=6.6):
                reason["outside_geo_gate"]+=1;continue
            # Native-naive clock not relabelled at source admission.
            fixes[ident].append((tm,lat,lon))
    for positions in fixes.values():
        positions.sort()
    return fixes,{"raw_source_fixes":nraw,
                  "n_original_birds":len(fixes),
                  "n_admitted_source_fixes":sum(map(len,fixes.values())),
                  "dropped_source_fixes":dict(reason)}

def make_steps(fixes,tide,clock_offset_seconds=0):
    records=[];dropped=Counter()
    for ident,positions in fixes.items():
        for a,b in zip(positions,positions[1:]):
            diff=(b[0]-a[0]).total_seconds()
            if not(120<=diff<=3600):
                dropped["dt_not_2min_to_1h"]+=1;continue
            start=(a[0]+timedelta(seconds=clock_offset_seconds)).replace(tzinfo=UTC)
            hdist=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))
            kmph=hdist*3.6/diff
            if not(0<=kmph<=120):
                dropped["implausible_displacement"]+=1;continue
            try:
                height,phase,rate=tide.at_with_phase(start)
            except ValueError:
                dropped["gauge_outside_range_or_gap"]+=1;continue
            hour=start.hour+start.minute/60+start.second/3600
            day=start.timetuple().tm_yday-1+hour/24
            records.append({"bird":ident,"stamp":start,"week":start.isocalendar()[:2],
                            "y":math.log1p(kmph),"height":height,"phase":phase,
                            "rate":rate,"lat":a[1],"lon":a[2],"dt_s":diff,
                            "hour":hour,"day":day,"kmph":kmph})
    records.sort(key=lambda r:r["stamp"])
    return records,{"n_eligible_steps":len(records),"n_birds":len({r["bird"] for r in records}),
                    "n_week_blocks":len({r["week"] for r in records}),
                    "drop_reason":dict(dropped),
                    "phase_counts":{str(k):v for k,v in sorted(Counter(r["phase"] for r in records).items())}}

def split_rows(rows):
    weeks=sorted({r["week"] for r in rows})
    if len(weeks)<8:raise ValueError("At least 8 available weekly blocks needed")
    cut=int(len(weeks)*0.70)
    train_week=set(weeks[:cut]);test_week=set(weeks[cut+1:])
    train_all=[r for r in rows if r["week"] in train_week]
    test_all=[r for r in rows if r["week"] in test_week]
    known={r["bird"] for r in train_all}
    test=[r for r in test_all if r["bird"] in known]
    shared={r["bird"] for r in test}
    train=[r for r in train_all if r["bird"] in shared]
    info={"total_weeks":len(weeks),"n_training_weeks":len(train_week),
          "n_embargo_weeks":1,"n_test_weeks":len(test_week),
          "training_step_count":len(train),"test_step_count":len(test),
          "n_shared_test_birds":len(shared),
          "n_excluded_unseen_test_birds":len({r["bird"] for r in test_all}-known),
          "phase_counts_train":{str(k):v for k,v in sorted(Counter(r["phase"] for r in train).items())},
          "phase_counts_test":{str(k):v for k,v in sorted(Counter(r["phase"] for r in test).items())}}
    return train,test,info

def features(r,level,bird_index):
    day_theta=2*math.pi*r["day"]/365
    hour_theta=2*math.pi*r["hour"]/24
    h=r["height"]
    x=[1,h,h*h,r["lat"],r["lon"],math.sin(hour_theta),math.cos(hour_theta),
       math.sin(day_theta),math.cos(day_theta),math.log(r["dt_s"]/600)]
    if level>=1:x.extend([r["phase"],r["phase"]*h])
    x.extend(float(r["bird"]==bird) for bird in bird_index[1:])
    return x

def model_fit(train,test,level):
    birds=sorted({r["bird"] for r in train})
    X=np.array([features(r,level,birds) for r in train],dtype=float)
    Z=np.array([features(r,level,birds) for r in test],dtype=float)
    y=np.array([r["y"] for r in train],dtype=float)
    center=X[:,1:].mean(0)
    sd=X[:,1:].std(0)
    sd[sd<1e-9]=1
    X[:,1:]=(X[:,1:]-center)/sd
    Z[:,1:]=(Z[:,1:]-center)/sd
    per=Counter(r["bird"] for r in train)
    w=np.array([1/per[r["bird"]] for r in train])
    w*=len(train)/w.sum()
    penalty=np.eye(X.shape[1])*1.0
    penalty[0,0]=0.
    coef=np.linalg.solve(X.T@(X*w[:,None])+penalty,X.T@(w*y))
    return Z@coef

def quantile(numbers,p):
    x=sorted(numbers)
    return x[int(p*(len(x)-1))] if x else None

def score(train,test,split,bootstrap_seed=20261102,B=4000):
    if len(train)<1000 or len(test)<1000 or split["n_shared_test_birds"]<3 or split["n_test_weeks"]<4:
        return {"admission":"NOT_ADMITTED_INSUFFICIENT_SAME_BIRD_HOLDOUT","split":split}
    y=np.array([r["y"] for r in test],dtype=float)
    err0=(y-model_fit(train,test,0))**2
    err1=(y-model_fit(train,test,1))**2
    by_bird=defaultdict(list);by_week=defaultdict(list)
    for i,r in enumerate(test):
        by_bird[r["bird"]].append(i)
        by_week[r["week"]].append(i)
    bird_mse={b:(float(np.mean(err0[ids])),float(np.mean(err1[ids]))) for b,ids in by_bird.items()}
    d_bird=[a-b for a,b in bird_mse.values()]
    m0=float(np.mean([v[0] for v in bird_mse.values()]))
    m1=float(np.mean([v[1] for v in bird_mse.values()]))
    week_diff=[]
    for ids in by_week.values():
        each=defaultdict(list)
        for j in ids:each[test[j]["bird"]].append(j)
        week_diff.append(float(np.mean([np.mean(err0[ix]-err1[ix]) for ix in each.values()])))
    rand=random.Random(bootstrap_seed)
    n1=len(d_bird);n2=len(week_diff)
    boot_bird=[sum(rand.choice(d_bird) for _ in range(n1))/n1 for _ in range(B)]
    boot_week=[sum(rand.choice(week_diff) for _ in range(n2))/n2 for _ in range(B)]
    test_phase=Counter(r["phase"] for r in test)
    return {"admission":"OBSERVED_EXPLORATORY_CLOCK_UNVERIFIED",
            "M0_equal_bird_test_MSE":m0,"M1_equal_bird_test_MSE":m1,
            "gain_M0_minus_M1_MSE":m0-m1,
            "gain_percent_of_M0":100*(m0-m1)/m0 if m0>0 else None,
            "n_birds_with_improvement":sum(d>0 for d in d_bird),
            "n_heldout_birds":n1,
            "paired_bird_bootstrap_CI95":[quantile(boot_bird,.025),quantile(boot_bird,.975)],
            "paired_test_week_bootstrap_CI95":[quantile(boot_week,.025),quantile(boot_week,.975)],
            "n_heldout_tide_exposure_weeks":n2,
            "week_blocks_with_positive_gain":sum(d>0 for d in week_diff),
            "test_ebb_flood_slack_counts":{str(k):test_phase[k] for k in (-1,0,1)},
            "min_test_bird_rows":min(len(ix) for ix in by_bird.values()),
            "split":split,
            "notes":["No original animal identities, GPS coordinates or gauge time-series output",
                     "Test week bootstrap conditional on training model; birds share environmental exposure",
                     "No prey-use, social-force or causal front interpretation"]}

def run(out):
    with tempfile.TemporaryDirectory(prefix="v31_orig_") as td:
        gps_path=Path(td)/"2009_original.csv.gz"
        manifest=download_and_pin(2009,gps_path)
        fixes,gps_source_audit=read_gps(gps_path)
        gps_path.unlink(missing_ok=True)
    water,tide_audit=get_gauge()
    report={"study":"O_SCHIERMONNIKOOG_2009","source":"ORIGINAL_ZENODO_GPS_AND_RWS_MEASURED_NAP",
            "evidence":"OBSERVED_RETROSPECTIVE_EXPLORATORY_CLOCK_UNVERIFIED",
            "bird_original_manifest":manifest,"bird_source_summary":gps_source_audit,
            "gauge_source_summary":tide_audit,
            "gps_clock_assumed":"naive_original_2009_tag_clock_as_UTC_not_verified",
            "gauge_station_identity_to_Dryad":"NOT_VERIFIED",
            "front_M2":"NOT_ADMITTED_no_measured_DEM_or_exposure_time",
            "social_M3":"NOT_ADMITTED_not_fitted",
            "models":{}}
    for label,shift in [("source_clock_as_UTC",0),("GPS_clock_minus_18seconds",-18),
                        ("GPS_clock_minus_1hour",-3600),("GPS_clock_plus_1hour",3600)]:
        steps,step_audit=make_steps(fixes,water,clock_offset_seconds=shift)
        train,test,split=split_rows(steps)
        model=score(train,test,split)
        report["models"][label]={"clock_offset_seconds":shift,"step_audit":step_audit,"result":model}
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    Path(out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    # Avoid printing or storing individual geolocations or animal source ids.
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    r=run(a.output)
    print(json.dumps({"source":r["source"],"bird_source_summary":r["bird_source_summary"],
                      "gauge_source_summary":r["gauge_source_summary"],
                      "models":r["models"],"evidence":r["evidence"]},sort_keys=True))
