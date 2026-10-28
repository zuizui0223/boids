#!/usr/bin/env python3
"""v16: predeclared fast 1-s GPS turn vs 10-s-stale partner on a new 8-flock source.

Different source from v15, without any post-hoc revision of v15 outcomes.
This benchmark describes GPS prediction, not recovered Reynolds forces,
ecological feeding niches, learning, or actual contact-network rewiring.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import csv
import hashlib
import io
import json
import math
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import route_memory_forecast as slow
import source_gate as source

ORIGINAL_SHA256 = slow.ORIGINAL_SHA256
SOURCE_FLOCKS = slow.REQUIRED_FLOCKS
HISTORIC_TRAIN = (5,6,7,8)
FUTURE_RELEASE_MIN, FUTURE_RELEASE_MAX = 9,15
SHELL_MIN_M, SHELL_MAX_M = 500.,4500.
MAX_STEP_M = 50.
MAX_TIME_GAP_MS = 1000
MIN_FLIGHT_RUN_S = 12.
MIN_FLIGHT_FIXES = 60
ANCHOR_SPACING_MS = 5000
RAW_FIX_MAX_OFFSET_MS = 200
NEIGHBOR_MAX_M = 100.
STALE_PARTNER_MS = 10000
FUTURE_TARGET_MS = 1000
MIN_FLOCK_EVENTS = 60
MIN_FOCAL_IDS = 3
RIDGE_ALPHA = 30.
MIN_FLOCK_TRAIN_GROUPS = 7
PREDICTION_MODELS = ("own","current","stale")


@dataclass(frozen=True)
class Fix:
    t:int
    x:float
    y:float
    h:float
    r:float


@dataclass
class BirdTrack:
    bird:str
    raw:list[Fix]
    times:list[int]


@dataclass(frozen=True)
class Event:
    flock:str
    release:int
    bird:str
    own:tuple[float,...]
    current:tuple[float,...]
    stale:tuple[float,...]
    target:float


def wrapped(a:float)->float:
    return math.atan2(math.sin(a),math.cos(a))


def direction_features(a:Fix, prev:Fix)->tuple[float,...]:
    axis=math.radians(149.5)  # published homeward direction from Bladon
    cross=a.x*math.cos(axis)-a.y*math.sin(axis)
    return (math.sin(a.h),math.cos(a.h),wrapped(a.h-prev.h),
            a.r/5000.,cross/1000.)


def social_features(a:Fix,b:Fix)->tuple[float,...]:
    dx=b.x-a.x;dy=b.y-a.y
    along=dx*math.sin(a.h)+dy*math.cos(a.h)
    cross=dx*math.cos(a.h)-dy*math.sin(a.h)
    hdiff=wrapped(b.h-a.h)
    return (along/50.,cross/50.,math.sin(hdiff),math.cos(hdiff))


def read_bird_track(arc:zipfile.ZipFile,name:str,bird:str)->tuple[BirdTrack,dict]:
    """First observed 500..4500m outbound course only, no fabricated positions.

    We retain the *first* contiguous original sensor segment crossing both
    spatial boundaries. No speed-unit assumption and no interpolated GPS time.
    """
    ordered=[]
    previous=None
    started=False
    breaks=0
    invalid=0
    rows=0
    with arc.open(name) as inp:
        reader=csv.DictReader(io.TextIOWrapper(inp,encoding="utf-8-sig",errors="replace",newline=""))
        if not set((*slow.REQUIRED_COLS,"HEADING")).issubset(reader.fieldnames or []):
            raise ValueError("Source heading/clock columns differ from fixed schema")
        for row in reader:
            rows+=1
            valid=slow.original_row_xy_t(row)
            if valid is None:
                previous=None
                invalid+=1
                if started:
                    break
                continue
            t,x,y=valid
            try:
                h=float(row["HEADING"])
                if not math.isfinite(h) or not 0<=h<=360:
                    raise ValueError("Bad GPS heading")
                h=math.radians(h%360)
            except (TypeError,ValueError):
                previous=None
                invalid+=1
                if started:
                    break
                continue
            now=Fix(t,x,y,h,math.hypot(x,y))
            if previous is not None:
                step=math.hypot(x-previous.x,y-previous.y)
                if (t<=previous.t or t-previous.t>MAX_TIME_GAP_MS or step>MAX_STEP_M):
                    breaks+=1
                    if started:
                        break
                    previous=now
                    continue
                if not started and previous.r<SHELL_MIN_M<=now.r and now.r-SHELL_MIN_M<=50.:
                    started=True
                    ordered=[now]
                elif started:
                    if now.r>=SHELL_MAX_M:
                        break
                    ordered.append(now)
            previous=now
    # Discard *all* duplicate raw timestamps (including the earliest),
    # not choosing the first/last duplicate using future outcomes.
    counts=collections.Counter(f.t for f in ordered)
    unique=[f for f in ordered if counts[f.t]==1]
    if (len(unique)<MIN_FLIGHT_FIXES or
        unique[-1].t-unique[0].t<MIN_FLIGHT_RUN_S*1000 if unique else True):
        unique=[]
    return BirdTrack(bird,unique,[f.t for f in unique]),{
        "rows_scanned":rows,"invalid_source_rows":invalid,
        "clock_or_position_breaks":breaks,
        "original_outbound_fixes":len(unique)
    }


def near(track:BirdTrack,target_ms:int)->Fix|None:
    j=bisect.bisect_left(track.times,target_ms)
    candidates=[track.raw[k] for k in (j-1,j)
                if 0<=k<len(track.raw) and abs(track.times[k]-target_ms)<=RAW_FIX_MAX_OFFSET_MS]
    return min(candidates,key=lambda x:(abs(x.t-target_ms),x.t)) if candidates else None


def past(track:BirdTrack,target_ms:int)->Fix|None:
    i=bisect.bisect_right(track.times,target_ms)-1
    if i<0:return None
    f=track.raw[i]
    return f if 0<=target_ms-f.t<=RAW_FIX_MAX_OFFSET_MS else None


def flight_events(flock:str,release:int,group:dict[str,BirdTrack])->tuple[list[Event],dict]:
    events=[]
    attempt=0
    bybird=collections.Counter()
    for bird,trace in sorted(group.items()):
        if not trace.raw:continue
        t0=((trace.raw[0].t+STALE_PARTNER_MS+ANCHOR_SPACING_MS-1)//ANCHOR_SPACING_MS)*ANCHOR_SPACING_MS
        latest=trace.raw[-1].t-FUTURE_TARGET_MS
        for t in range(t0,latest+1,ANCHOR_SPACING_MS):
            attempt+=1
            now=near(trace,t)
            prev=near(trace,t-1000)
            earlier=near(trace,t-STALE_PARTNER_MS)
            future=near(trace,t+FUTURE_TARGET_MS)
            if now is None or prev is None or earlier is None or future is None:
                continue
            neighbors=[]
            for mate,mate_track in group.items():
                if mate==bird or not mate_track.raw:
                    continue
                mate_now=past(mate_track,now.t)
                if mate_now is None:
                    continue
                dist=math.hypot(now.x-mate_now.x,now.y-mate_now.y)
                if dist>NEIGHBOR_MAX_M:
                    continue
                mate_old=past(mate_track,earlier.t)
                if mate_old is None:
                    continue
                neighbors.append((dist,mate,mate_now,mate_old))
            if not neighbors:
                continue
            dist,mate,mate_now,mate_old=min(neighbors,key=lambda x:(x[0],x[1]))
            events.append(Event(flock,release,bird,direction_features(now,prev),
                social_features(now,mate_now),social_features(earlier,mate_old),
                wrapped(future.h-now.h)))
            bybird[bird]+=1
    return events,{"candidate_utc_anchors":attempt,
        "matched_common_target_anchors":len(events),
        "focal_IDs_with_eligible_predictions":len(bybird)}


def load_events(path:Path)->tuple[list[Event],dict]:
    result=[]
    qc=collections.defaultdict(lambda:collections.Counter())
    by_episode=collections.defaultdict(dict)
    with zipfile.ZipFile(path) as arc:
        source.archive_name_gate(arc.infolist())
        names=[n for n in arc.namelist()
               if n.lower().endswith(".csv") and not Path(n).name.startswith("._")]
        if len(names)!=559:
            raise ValueError("The originally admitted 559 source GPS files changed")
        for name in sorted(names):
            identity=source.member_identity(name)
            if identity is None:
                raise ValueError("Unrecognized original member identity")
            flock,bird,release=identity
            track,stats=read_bird_track(arc,name,bird)
            if bird in by_episode[(flock,release)]:
                raise ValueError("Duplicate flock-bird-release source track")
            by_episode[(flock,release)][bird]=track
            qc[flock]["csv_tracks"]+=1
            qc[flock]["outbound_raw_GPS_fixes"]+=stats["original_outbound_fixes"]
            qc[flock]["invalid_source_rows_before_end"]+=stats["invalid_source_rows"]
        for (flock,release),members in sorted(by_episode.items()):
            batch,n=flight_events(flock,release,members)
            result.extend(batch)
            for k,v in n.items():
                qc[flock][k]+=v
            qc[flock]["episodes_with_any_matched_anchor"]+=int(bool(batch))
    return result,{k:dict(v) for k,v in qc.items()}


def design(events:list[Event],mode:str)->np.ndarray:
    own=np.array([e.own for e in events],dtype=float)
    if own.ndim!=2 or own.shape[1]!=5:
        raise ValueError("No stable own features")
    if mode=="own":return own
    if mode not in ("current","stale"):
        raise ValueError("Unknown registered fast predictor")
    partner=np.array([getattr(e,mode) for e in events],dtype=float)
    if partner.shape!=(len(events),4):
        raise ValueError("Partner features inconsistent")
    return np.concatenate((own,partner),axis=1)


def fit_predict(train:list[Event],test:list[Event],mode:str)->float:
    if not train or not test:
        raise ValueError("Missing training/test event pairs")
    X=design(train,mode)
    Xt=design(test,mode)
    y=np.array([e.target for e in train],float)
    yt=np.array([e.target for e in test],float)
    groups=collections.Counter(e.flock for e in train)
    if len(groups)!=MIN_FLOCK_TRAIN_GROUPS:
        raise ValueError("Not all seven other independent training flocks represented")
    n=len(train)
    w=np.array([n/(len(groups)*groups[e.flock]) for e in train],float)
    mu=np.average(X,weights=w,axis=0)
    sigma=np.sqrt(np.average((X-mu)**2,weights=w,axis=0))
    sigma=np.where(sigma>1e-12,sigma,1.)
    Z=(X-mu)/sigma
    y0=float(np.average(y,weights=w))
    coef=np.linalg.solve(Z.T@(Z*w[:,None])+RIDGE_ALPHA*np.eye(Z.shape[1]),
                        Z.T@(w*(y-y0)))
    yh=(Xt-mu)/sigma@coef+y0
    return float(np.mean(np.arctan2(np.sin(yt-yh),np.cos(yt-yh))**2))


def evaluate(events:list[Event],qc:dict)->dict:
    primary={f:[e for e in events if e.flock==f and
                FUTURE_RELEASE_MIN<=e.release<=FUTURE_RELEASE_MAX]
             for f in SOURCE_FLOCKS}
    past={f:[e for e in events if e.flock==f and e.release in HISTORIC_TRAIN]
          for f in SOURCE_FLOCKS}
    failures=[]
    for f in SOURCE_FLOCKS:
        if len(primary[f])<MIN_FLOCK_EVENTS:
            failures.append(f"{f}_future_{len(primary[f])}_events")
        if len({e.bird for e in primary[f]})<MIN_FOCAL_IDS:
            failures.append(f"{f}_future_missing_independent_focal_birds")
        if len(past[f])<MIN_FLOCK_EVENTS:
            failures.append(f"{f}_train_{len(past[f])}_events")
    if failures:
        return {"status":"FAST_NOT_ADMITTED_FROZEN_GATE",
                "failures":failures,
                "primary_events_per_flock":{f:len(v) for f,v in primary.items()},
                "historic_events_per_flock":{f:len(v) for f,v in past.items()}}
    fold={}
    for heldout in SOURCE_FLOCKS:
        tr=[e for flock in SOURCE_FLOCKS if flock!=heldout for e in past[flock]]
        te=primary[heldout]
        mse={mode:fit_predict(tr,te,mode) for mode in PREDICTION_MODELS}
        fold[heldout]={
            "test_future_anchors":len(te),
            "test_distinct_focal_ids":len({e.bird for e in te}),
            "mse_rad2":mse,
            "stale_minus_current_rad2":mse["stale"]-mse["current"],
            "own_minus_current_rad2":mse["own"]-mse["current"]}
    d1=np.array([fold[f]["stale_minus_current_rad2"] for f in SOURCE_FLOCKS])
    d2=np.array([fold[f]["own_minus_current_rad2"] for f in SOURCE_FLOCKS])
    rng=np.random.default_rng(20261028)
    indices=rng.integers(0,8,size=(10000,8))
    def stat(v):
        return {"equal_flock_mean":float(v.mean()),
                "positive_flocks":int((v>0).sum()),
                "bootstrap_95_flock_percentile":list(map(float,np.quantile(v[indices].mean(axis=1),[.025,.975]))),
                "n_independent_flocks":8}
    return {"status":"EXPLORATORY_INDEPENDENT_EIGHT_FLOCK_FAST_TURN_FORECAST",
            "per_flock":fold,"current_vs_stale":stat(d1),
            "current_vs_own":stat(d2),
            "min_one_sided_unanimous_sign_p":1/256,
            "inference":"Short-step GPS heading prediction only, not social force or animal learning"}


def experiment(out:Path)->dict:
    record=source.get_api(source.RECORD_API)
    spec=source.select_file(record)
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"Data.zip"
        transfer=source.bounded_download(spec,path)
        if transfer["sha256"]!=ORIGINAL_SHA256:
            raise ValueError("Pinned original GPS ZIP changed")
        events,qc=load_events(path)
        results=evaluate(events,qc)
    receipt={
        "study":"v16-independent-eight-flock-raw-GPS-fast-1s-turning",
        "source_integrity":transfer,
        "original_2016_source":"Zenodo 4943714 / Dryad 508j2",
        "source_flc":8,"source_csv_tracks":559,
        "speed_unit_not_assumed":True,
        "target":"1s GPS heading difference in original un-interpolated UTC",
        "historic_train_releases":list(HISTORIC_TRAIN),
        "future_heldout_release_ids":[FUTURE_RELEASE_MIN,FUTURE_RELEASE_MAX],
        "feature_models":list(PREDICTION_MODELS),
        "sample_gates":{
            "outbound_radial_m":[SHELL_MIN_M,SHELL_MAX_M],
            "max_raw_GPS_step_m":MAX_STEP_M,
            "max_raw_time_gap_ms":MAX_TIME_GAP_MS,
            "min_segment_seconds":MIN_FLIGHT_RUN_S,
            "min_segment_fixes":MIN_FLIGHT_FIXES,
            "anchor_seconds":ANCHOR_SPACING_MS/1000,
            "max_cotime_lag_ms":RAW_FIX_MAX_OFFSET_MS,
            "max_partner_distance_m":NEIGHBOR_MAX_M,
            "stale_seconds":STALE_PARTNER_MS/1000,
            "ridge_alpha":RIDGE_ALPHA},
        "qc_by_flock":qc,
        "observed_result":results,
        "all_older_observational_endpoints_unchanged":True,
        "limits":[
            "The fast outcome has not been combined algebraically with the slow distinct route target.",
            "Eight flocks in a single published experiment, not eight taxa.",
            "No social force coefficients, food-resource niches, real habituation or causal rewiring inferred.",
            "No test bird data used in training or fold normalization; full-future-release holdouts.",
            "No individual GPS rows, GPS coordinates or event predictions redistributed."
        ]}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v16/results/fast_turn_forecast_v16.json"))
    a=ap.parse_args()
    r=experiment(a.out)
    print("V16_FAST_SOURCE",json.dumps(r["source_integrity"],sort_keys=True))
    print("V16_FAST_QC",json.dumps(r["qc_by_flock"],sort_keys=True))
    print("V16_FAST_RESULT",json.dumps(r["observed_result"],sort_keys=True))
    print("V16_FAST_SOURCE_LIMIT_NO_3D_NO_CAUSAL_FORCES")


if __name__=="__main__":
    main()
