"""v41 REAL original GPS tidal turning: 2010–11 train, 2012 test.

This is a previously unscored DIRECTIONAL endpoint in the already used v40
original bird cohort. It tests whether ebb/flood helps forecast next movement
heading after a bird's own previous heading; it does NOT fit social Boids or
moving prey/exposure fronts.

Frozen contract: docs/V41_FROZEN_2012_TIDAL_DIRECTION_FORECAST.md
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import tempfile
from collections import Counter, defaultdict
from datetime import timedelta, timezone
from pathlib import Path

import numpy as np

from source_preflight import download_and_pin, haversine_m, parse_stamp
from source_gate_2012 import get_ameland_original, REGIONS
from ameland_external_site import original_gps
from source_fetch_resilience import observed_rws_year
from heldout_2012_tidal_lag import original_2012_gauge
from tide_phase_yearago_placebo import percentile_interval

SITES=("schiermonnikoog","ameland")
YEARS=(2010,2011,2012)
TEST_YEAR=2012
CLOCKS=(0,-15)
MIN_KMPH=0.4
MAX_KMPH=120.
MIN_DT_S=1800
MAX_DT_S=7200
RIDGE=10.
TIDE_TOLERANCE_M_PER_H=.012
ORIGINAL_FIELDS={"event-id","timestamp","location-lat","location-long",
                 "individual-local-identifier","visible"}

def unit_direction(a,b):
    """Horizontal unit EN directions, not 3D flight or calibrated velocity."""
    midlat=math.radians(.5*(a[1]+b[1]))
    east=(b[2]-a[2])*math.cos(midlat)
    north=b[1]-a[1]
    norm=math.hypot(east,north)
    if norm<=0:return None
    return east/norm,north/norm

def original_three_fix_heading_episodes(path,tide,site,clock_shift_s=0):
    if site not in SITES or clock_shift_s not in CLOCKS:
        raise ValueError("Outside frozen location/clock choices")
    bounds=REGIONS[site]
    first_in_hour=defaultdict(dict)
    seen=set()
    raw=0;filtered=Counter()
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as source:
        reader=csv.DictReader(source)
        if not ORIGINAL_FIELDS<=set(reader.fieldnames or ()):
            raise ValueError("Unexpected original Movebank source GPS field dictionary")
        for row in reader:
            raw+=1
            eid=(row.get("event-id") or "").strip()
            if not eid or eid in seen:
                filtered["duplicate_or_missing_original_event"]+=1
                continue
            seen.add(eid)
            if row["visible"].strip().upper() in ("FALSE","0"):
                filtered["not_originally_visible"]+=1
                continue
            bird=(row.get("individual-local-identifier") or "").strip()
            if not bird:
                filtered["missing_source_bird"]+=1
                continue
            try:
                t=parse_stamp(row["timestamp"]).replace(tzinfo=timezone.utc)+timedelta(seconds=clock_shift_s)
                lat=float(row["location-lat"]);lon=float(row["location-long"])
            except (ValueError,TypeError):
                filtered["bad_original_clock_or_coordinates"]+=1;continue
            if not all(map(math.isfinite,(lat,lon))) or not (
                bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]
            ):
                filtered["outside_original_island_gate"]+=1;continue
            hour=t.replace(minute=0,second=0,microsecond=0)
            old=first_in_hour[bird].get(hour)
            if old is None or t<old[0]:
                first_in_hour[bird][hour]=(t,lat,lon)
    rows=[];candidate=0
    for bird,hourly in first_in_hour.items():
        fixes=sorted(hourly.values())
        for a,b,c in zip(fixes,fixes[1:],fixes[2:]):
            candidate+=1
            dt_before=(b[0]-a[0]).total_seconds()
            dt_next=(c[0]-b[0]).total_seconds()
            if not (MIN_DT_S<=dt_before<=MAX_DT_S and MIN_DT_S<=dt_next<=MAX_DT_S):
                filtered["gapped_original_three_fix"]+=1;continue
            speed_before=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))*3.6/dt_before
            speed_next=haversine_m((None,b[1],b[2]),(None,c[1],c[2]))*3.6/dt_next
            if not (MIN_KMPH<=speed_before<=MAX_KMPH and MIN_KMPH<=speed_next<=MAX_KMPH):
                filtered["stationary_or_implausible_heading"]+=1;continue
            previous=unit_direction(a,b)
            future=unit_direction(b,c)
            if previous is None or future is None:
                filtered["zero_length_direction"]+=1;continue
            try:
                h,phase,rate=tide.at_with_phase(b[0],lookback_minutes=20,
                                              tolerance_m_per_hour=TIDE_TOLERANCE_M_PER_H)
            except ValueError:
                filtered["no_gauge_within_tolerance"]+=1;continue
            if phase==0:
                filtered["source_slack_water_phase"]+=1;continue
            hour=b[0].hour+b[0].minute/60+b[0].second/3600
            day=b[0].timetuple().tm_yday
            rows.append({"id":bird,"t":b[0],"lat":b[1],"lon":b[2],
                         "h":h,"phase":phase,
                         "previous_e":previous[0],"previous_n":previous[1],
                         "previous_speed_log":math.log1p(speed_before),
                         "target_e":future[0],"target_n":future[1],
                         "clocksin":math.sin(2*math.pi*hour/24),
                         "clockcos":math.cos(2*math.pi*hour/24),
                         "yearsin":math.sin(2*math.pi*day/365.25),
                         "yearcos":math.cos(2*math.pi*day/365.25)})
    summary={"original_raw_source_fixes":raw,
             "original_birds_with_visible_geographic_fixes":len(first_in_hour),
             "source_selected_hourly_first_fixes":sum(map(len,first_in_hour.values())),
             "three_fix_candidate_episodes":candidate,
             "admitted_real_three_fix_heading_episodes":len(rows),
             "admitted_real_episode_birds":len({r["id"] for r in rows}),
             "admitted_real_episode_ISO_weeks":len({r["t"].isocalendar()[:2] for r in rows}),
             "source_exclusions":dict(filtered),
             "direction_is_from_two_original_GPS_displacements":True,
             "source_future_C_only_used_as_target_not_predictor":True}
    return rows,summary

def vector(row,level):
    if level not in (0,1):raise ValueError("Only frozen M0/M1")
    h=row["h"]
    baseline=[1.,h,h*h,(row["lat"]-53.45)*10,(row["lon"]-6.)*5,
              row["clocksin"],row["clockcos"],row["yearsin"],row["yearcos"],
              row["previous_e"],row["previous_n"],row["previous_speed_log"]]
    if level==1:
        baseline.extend([row["phase"],row["phase"]*h])
    return baseline

def forecast(train,test,level):
    if not train or not test:raise ValueError("Missing original GPS trajectory episodes")
    x=np.asarray([vector(r,level) for r in train],dtype=float)
    z=np.asarray([vector(r,level) for r in test],dtype=float)
    y=np.asarray([[r["target_e"],r["target_n"]] for r in train],dtype=float)
    avg=x[:,1:].mean(axis=0);sd=x[:,1:].std(axis=0)
    sd[sd<1e-9]=1
    x[:,1:]=(x[:,1:]-avg)/sd
    z[:,1:]=(z[:,1:]-avg)/sd
    n=Counter(r["id"] for r in train)
    weight=np.asarray([1/n[r["id"]] for r in train],dtype=float)
    weight*=len(train)/weight.sum()
    reg=np.eye(x.shape[1])*RIDGE
    reg[0,0]=0.
    coef=np.linalg.solve(x.T@(x*weight[:,None])+reg,x.T@(weight[:,None]*y))
    return z@coef

def directional_half_mse(truth,pred):
    if np.shape(truth)!=np.shape(pred) or np.shape(truth)[-1]!=2:
        raise ValueError("Target/predicted directional dimensions must be Nx2")
    return .5*np.square(np.asarray(truth)-np.asarray(pred)).sum(axis=1)

def score(train,test,*,bird_draws=10000,week_draws=4000,seed=20261105):
    groups=defaultdict(list);weeks=defaultdict(list)
    for i,r in enumerate(test):
        if r["t"].year!=TEST_YEAR:raise ValueError("Test source must be entirely 2012")
        groups[r["id"]].append(i)
        weeks[r["t"].isocalendar()[:2]].append(i)
    if (len(train)<1000 or len(test)<1000 or len(groups)<3 or len(weeks)<4):
        return {"status":"NOT_ADMITTED_INSUFFICIENT_2012_DIRECTION_SOURCE",
                "train_episodes":len(train),"test_episodes":len(test),
                "test_birds":len(groups),"test_weeks":len(weeks)}
    target=np.asarray([[r["target_e"],r["target_n"]] for r in test],dtype=float)
    e0=directional_half_mse(target,forecast(train,test,0))
    e1=directional_half_mse(target,forecast(train,test,1))
    difference=e0-e1
    bird_gains=[float(np.mean(difference[idx])) for idx in groups.values()]
    week_gains=[]
    for idx in weeks.values():
        present=defaultdict(list)
        for i in idx:present[test[i]["id"]].append(i)
        week_gains.append(float(np.mean([np.mean(difference[v]) for v in present.values()])))
    mse0=float(np.mean([np.mean(e0[idx]) for idx in groups.values()]))
    mse1=float(np.mean([np.mean(e1[idx]) for idx in groups.values()]))
    return {"status":"OBSERVED_2012_TIDE_CONDITIONAL_HEADING_TRANSFER",
            "train_episodes":len(train),"test_episodes":len(test),
            "test_birds":len(groups),"test_weeks":len(weeks),
            "M0_equal_bird_direction_half_MSE":mse0,
            "M1_equal_bird_direction_half_MSE":mse1,
            "phase_gain_pooled_equal_bird_half_MSE":mse0-mse1,
            "phase_gain_pct_of_baseline":100*(mse0-mse1)/mse0 if mse0>0 else None,
            "pooled_equal_bird_bootstrap95":percentile_interval(bird_gains,bird_draws,seed),
            "bird_positive_count":int(sum(v>0 for v in bird_gains)),
            "separate_equal_week_bird_gain":float(np.mean(week_gains)),
            "separate_equal_week_bird_bootstrap95":percentile_interval(week_gains,week_draws,seed+100),
            "week_positive_count":int(sum(v>0 for v in week_gains)),
            "outcome_not_in_source_features":True,
            "native_GPS_clock_not_calibrated":True,
            "no_prey_front_or_social_force_estimated":True}

def run(site,outfile):
    if site not in SITES:raise ValueError("Outside frozen original site list")
    station="schiermonnikoog.waddenzee" if site=="schiermonnikoog" else "ameland.nes"
    data={clock:{} for clock in CLOCKS}
    provenance={}
    with tempfile.TemporaryDirectory(prefix="v41_original_direction_") as root:
        for year in YEARS:
            path=Path(root)/f"{site}_{year}.csv.gz"
            if site=="schiermonnikoog":
                original=download_and_pin(year,path)
            else:
                original=get_ameland_original(path) if year==2012 else original_gps(year,path)
            tide,gauge=(original_2012_gauge(station) if year==2012 else observed_rws_year(station,year))
            if gauge["gauge_rows"]<50000:
                raise ValueError("Source-gauge coverage did not pass frozen annual gate")
            provenance[str(year)]={"source_gps_original_SHA256":original["original_sha256"],
                                  "GPS_provider_MD5_verified":original.get("provider_md5_match",original.get("provider_original_md5_matched")),
                                  "RWS_measured_WATHTE_NAP_values":gauge["gauge_rows"],
                                  "RWS_source_station":station}
            for clock in CLOCKS:
                steps,audit=original_three_fix_heading_episodes(path,tide,site,clock)
                data[clock][year]=steps
                provenance[str(year)][f"clock_{clock}s_audit"]=audit
            path.unlink(missing_ok=True)
    outcomes={}
    for clock in CLOCKS:
        training=data[clock][2010]+data[clock][2011]
        test=data[clock][2012]
        outcomes[f"native_clock_shift_{clock}s"]=score(training,test)
    result={"analysis":"V41_ORIGINAL_2012_HEADING_AFTER_PRIVATE_HISTORY",
            "original_source":"ZENODO_PROVIDER_MD5_GPS_AND_MEASURED_RWS_NAP",
            "site":site,"training_years":[2010,2011],"test_year":2012,
            "statistical_endpoint":"half_squared_unit_heading_vector_error",
            "source_receipts":provenance,"scenarios":outcomes,
            "previous_speed_phase_results_already_known":True,
            "claim":"Tide directional prediction vs own past motion; no causal front or Reynolds steering"}
    Path(outfile).parent.mkdir(parents=True,exist_ok=True)
    Path(outfile).write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",choices=SITES,required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=run(args.site,args.output)
    print(json.dumps(result,sort_keys=True))
