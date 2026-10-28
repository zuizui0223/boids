#!/usr/bin/env python3
"""v15 frozen exploratory source-real 2D turning forecast, no raw track exports.

The source protocol lives in docs/OBSERVED_HORIZONTAL_TURN_FORECAST_CONTRACT_V15.md.
Results from 3 independently recorded flock-trial episodes cannot alone be
confirmatory of biological social forces, animal memory, competition or 3D niche.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import datetime as datetime
import hashlib
import json
import math
import re
import tempfile
import urllib.request
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

SOURCE_URL = ("https://zenodo.org/api/records/21092705/files/"
              "pigeon_homing_public_trials_v1.0.0.zip/content")
SOURCE_BYTES = 126_588_691
SOURCE_MD5 = "5c1e9b386bff5794e177b122b1fcb244"
SOURCE_SHA256 = "756eed718ad13c14233e60b19009ce0916f183eb540b1262ba030ebc25a0ab03"
RMC_PREFIXES = ("$GNRMC,", "$GPRMC,")
SOURCE_MEMBERS = "data/checksums_sha256.txt"
SOURCE_TRIALS = ("analysis_trial_01", "analysis_trial_02", "analysis_trial_03")
SPEED_KNOT_M_S = .514444
MIN_FLIGHT_M_S, MAX_FLIGHT_M_S = 6., 35.
MAX_CONTIGUOUS_GAP_MS = 500
MIN_RUN_LENGTH_MS = 12_000
MIN_RUN_FIXES = 60
ANCHOR_STRIDE_MS = 5_000
COFIX_TOLERANCE_MS = 200
MAX_NEIGHBOR_DISTANCE_M = 100.
MIN_TRIAL_PRIMARY_ANCHORS = 60
MIN_TRIAL_BIRDS = 3
MIN_TRIAL_GHOST_ANCHORS = 30
RIDGE_ALPHA = 30.
ZIP_CAP_BYTES = 160_000_000
RADIUS = 6_371_008.8
MODEL_NAMES = ("own", "current", "stale")


@dataclass(frozen=True, slots=True)
class Fix:
    time_ms: int
    lat: float
    lon: float
    speed: float
    heading: float
    x: float = 0.
    y: float = 0.
    run: int = -1
    run_first_ms: int = 0
    first_x: float = 0.
    first_y: float = 0.


@dataclass
class Track:
    bird: str
    fixes: list[Fix]
    times: list[int]
    runs: dict[int, tuple[int, int]]
    qc: dict


@dataclass(frozen=True, slots=True)
class Event:
    trial: str
    bird: str
    x0: tuple[float, ...]
    current: tuple[float, ...]
    stale: tuple[float, ...]
    ghost: tuple[float, ...] | None
    target: float


def wrapped(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def checksum_ok(raw: str) -> bool:
    if not raw.startswith("$"):
        return False
    if "*" not in raw:
        return True  # Sentences lacking a checksum are admitted but never called CRC-verified.
    body, checksum = raw[1:].split("*", 1)
    if not re.fullmatch(r"[0-9a-fA-F]{2}", checksum[:2]):
        return False
    v = 0
    for c in body:
        v ^= ord(c)
    return v == int(checksum[:2], 16)


def nmea_angle(raw: str, hemi: str, latitude: bool) -> float:
    n = float(raw)
    if not math.isfinite(n) or n < 0:
        raise ValueError("nonfinite or negative NMEA angle")
    deg = int(n // 100)
    minute = n - 100 * deg
    if not 0 <= minute < 60:
        raise ValueError("NMEA minutes invalid")
    if (latitude and deg > 90) or (not latitude and deg > 180):
        raise ValueError("NMEA angle out of bounds")
    if hemi not in (("N", "S") if latitude else ("E", "W")):
        raise ValueError("NMEA hemisphere invalid")
    result = deg + minute / 60
    if (latitude and hemi == "S") or (not latitude and hemi == "W"):
        result = -result
    return result


def parse_original_rmc(text: str) -> tuple[str, Fix | None]:
    positions = [text.find(p) for p in RMC_PREFIXES if p in text]
    if not positions:
        return "non_rmc", None
    sentence = text[min(positions):].strip()
    if not checksum_ok(sentence):
        return "bad_checksum", None
    col = sentence.split("*", 1)[0].split(",")
    if len(col) < 10:
        return "malformed", None
    if col[2].strip() != "A":
        return "invalid_status", None
    try:
        utc = col[1].strip()
        if not re.fullmatch(r"\d{6}(?:\.\d+)?", utc):
            raise ValueError("bad UTC")
        hr, mn, sec = int(utc[:2]), int(utc[2:4]), float(utc[4:])
        if not (0 <= hr < 24 and 0 <= mn < 60 and 0 <= sec < 60):
            raise ValueError("bad UTC bounds")
        day = datetime.datetime.strptime(col[9].strip(), "%d%m%y").date().toordinal()
        lat = nmea_angle(col[3].strip(), col[4].strip(), True)
        lon = nmea_angle(col[5].strip(), col[6].strip(), False)
        speed = float(col[7].strip()) * SPEED_KNOT_M_S
        course = float(col[8].strip())
        if not (math.isfinite(speed) and math.isfinite(course)
                and speed >= 0 and 0 <= course <= 360):
            raise ValueError("invalid speed or heading")
        # Explicitly observed course over ground; NOT yaw/vertical attitude.
        return "valid", Fix(
            day * 86_400_000 + round((hr*3600 + mn*60 + sec)*1000),
            lat, lon, speed, math.radians(course % 360))
    except (ValueError, TypeError, OverflowError):
        return "invalid_fields", None


def projected(lat: float, lon: float, lat_ref: float, lon_ref: float) -> tuple[float, float]:
    return (RADIUS * math.cos(math.radians(lat_ref)) * math.radians(lon-lon_ref),
            RADIUS * math.radians(lat-lat_ref))


def raw_runs(lines: list[bytes], lat_ref: float, lon_ref: float) -> tuple[list[Fix], dict]:
    """Retain true unbroken speed-qualified runs, drop ALL repeated UTC fixes."""
    parsed: list[tuple[str, Fix | None]] = [
        parse_original_rmc(line.decode("utf-8", errors="replace")) for line in lines]
    missing_crc = sum(1 for line in lines if any(p.encode() in line for p in RMC_PREFIXES) and b"*" not in line)
    counts = collections.Counter(r.time_ms for status, r in parsed
                                 if status == "valid" and r is not None)
    counts_by_type = collections.Counter(status for status, _ in parsed)
    kept: list[Fix] = []
    active: list[Fix] = []
    run_id = 0
    segment_count = 0
    n_duplicate_rows = 0
    n_speed_ok = 0
    def flush() -> None:
        nonlocal active, run_id, segment_count
        if active and (active[-1].time_ms - active[0].time_ms >= MIN_RUN_LENGTH_MS
                       and len(active) >= MIN_RUN_FIXES):
            start = active[0]
            current_run = run_id
            run_id += 1
            segment_count += 1
            kept.extend(replace(f, run=current_run,
                                run_first_ms=start.time_ms,
                                first_x=start.x, first_y=start.y) for f in active)
        active = []
    for status, fix in parsed:
        if status == "non_rmc":
            continue
        if status != "valid" or fix is None:
            flush()
            continue
        if counts[fix.time_ms] != 1:
            n_duplicate_rows += 1
            flush()
            continue
        if not MIN_FLIGHT_M_S <= fix.speed <= MAX_FLIGHT_M_S:
            flush()
            continue
        n_speed_ok += 1
        x, y = projected(fix.lat, fix.lon, lat_ref, lon_ref)
        fix = replace(fix, x=x, y=y)
        if active and (fix.time_ms <= active[-1].time_ms or
                       fix.time_ms - active[-1].time_ms > MAX_CONTIGUOUS_GAP_MS):
            flush()
        active.append(fix)
    flush()
    kept.sort(key=lambda f:f.time_ms)
    return kept, {
        "raw_lines":len(lines),
        "raw_valid_rmc":counts_by_type["valid"],
        "raw_invalid_rmc":sum(v for k,v in counts_by_type.items() if k not in ("valid","non_rmc")),
        "rmc_without_crc_field":missing_crc,
        "duplicate_utc_rows_discarded":n_duplicate_rows,
        "individual_speed_valid_raw_fixes":n_speed_ok,
        "accepted_flight_segments":segment_count,
        "airborne_fixes_in_accepted_segments":len(kept),
    }


def track_from_lines(bird: str, raw: list[bytes], lat_ref: float, lon_ref: float) -> Track:
    fixes, qc = raw_runs(raw,lat_ref,lon_ref)
    runs = {}
    for i, f in enumerate(fixes):
        if f.run not in runs:
            runs[f.run] = (i, i)
        a, _ = runs[f.run]
        runs[f.run] = (a, i)
    return Track(bird,fixes,[f.time_ms for f in fixes],runs,qc)


def nearest(track: Track, target_ms: int, same_run: int | None = None) -> Fix | None:
    k = bisect.bisect_left(track.times,target_ms)
    candidates = [track.fixes[i] for i in (k-1,k)
                  if 0 <= i < len(track.fixes) and
                  abs(track.times[i]-target_ms) <= COFIX_TOLERANCE_MS]
    if same_run is not None:
        candidates = [f for f in candidates if f.run == same_run]
    return min(candidates, key=lambda f:(abs(f.time_ms-target_ms),f.time_ms)) if candidates else None


def nearest_past(track: Track, focal_ms: int, same_run: int | None = None) -> Fix | None:
    """Partner data MUST be observed no later than the focal measurement."""
    ix = bisect.bisect_right(track.times, focal_ms) - 1
    if ix < 0:
        return None
    item = track.fixes[ix]
    if focal_ms - item.time_ms > COFIX_TOLERANCE_MS:
        return None
    if same_run is not None and item.run != same_run:
        return None
    return item


def relative_partner(a: Fix, b: Fix) -> tuple[float,...]:
    dx, dy = b.x - a.x, b.y - a.y
    # Compass heading: 0 north, 90 east; along/lateral relative to A's heading.
    ahead = dx*math.sin(a.heading) + dy*math.cos(a.heading)
    side = dx*math.cos(a.heading) - dy*math.sin(a.heading)
    d = math.hypot(dx, dy)
    delta = wrapped(b.heading-a.heading)
    return (ahead/50., side/50., math.log1p(d)/5.,
            math.sin(delta), math.cos(delta), (b.speed-a.speed)/10.)


def own_features(a: Fix, prev: Fix) -> tuple[float,...]:
    return (math.sin(a.heading),math.cos(a.heading),a.speed/15.,
            wrapped(a.heading-prev.heading), (a.speed-prev.speed)/5.,
            (a.time_ms-a.run_first_ms)/300000.,
            (a.x-a.first_x)/1000.,(a.y-a.first_y)/1000.)


def trial_events(trial: str, tracks: dict[str,Track]) -> tuple[list[Event], dict]:
    events = []
    qc = {"trial":trial,
          "birds_with_airborne_runs":sum(bool(x.runs) for x in tracks.values()),
          "accepted_flight_segments":sum(len(x.runs) for x in tracks.values()),
          "airborne_fixes":sum(len(x.fixes) for x in tracks.values()),
          "raw_valid_rmc":sum(x.qc["raw_valid_rmc"] for x in tracks.values()),
          "duplicate_utc_rows_discarded":sum(x.qc["duplicate_utc_rows_discarded"] for x in tracks.values()),
          "rmc_without_crc_field":sum(x.qc["rmc_without_crc_field"] for x in tracks.values()),
          "n_focal_anchor_attempts":0,"n_primary_eligible":0,
          "n_30s_surrogate_eligible":0,
          "distinct_focal_birds":0}
    for bird, tr in sorted(tracks.items()):
        used = 0
        for run_id,(start_ix,end_ix) in tr.runs.items():
            start = tr.fixes[start_ix]
            end = tr.fixes[end_ix]
            t0 = ((start.time_ms + 10000 + ANCHOR_STRIDE_MS - 1)//ANCHOR_STRIDE_MS)*ANCHOR_STRIDE_MS
            for time_ms in range(t0, end.time_ms-1000+1, ANCHOR_STRIDE_MS):
                qc["n_focal_anchor_attempts"] += 1
                a = nearest(tr,time_ms,run_id)
                a_1 = nearest(tr,time_ms-1000,run_id)
                a_fut = nearest(tr,time_ms+1000,run_id)
                a_10 = nearest(tr,time_ms-10000,run_id)
                if None in (a,a_1,a_fut,a_10):
                    continue
                candidates = []
                for other_bird, other in sorted(tracks.items()):
                    if other_bird == bird:
                        continue
                    b = nearest_past(other,a.time_ms)
                    if b is None:
                        continue
                    dist = math.hypot(b.x-a.x,b.y-a.y)
                    if dist > MAX_NEIGHBOR_DISTANCE_M:
                        continue
                    b_10 = nearest_past(other,a_10.time_ms,b.run)
                    if b_10 is None:
                        continue
                    candidates.append((dist,other_bird,b,b_10,other))
                if not candidates:
                    continue
                _,partner,b,b_10,partner_track = min(candidates,key=lambda x:(x[0],x[1]))
                a_30 = nearest(tr,time_ms-30000,run_id)
                b_30 = nearest_past(partner_track,a_30.time_ms,b.run) if a_30 is not None else None
                ghost = relative_partner(a_30,b_30) if a_30 is not None and b_30 is not None else None
                events.append(Event(trial,bird,own_features(a,a_1),
                                    relative_partner(a,b), relative_partner(a_10,b_10),
                                    ghost, wrapped(a_fut.heading-a.heading)))
                used += 1
                qc["n_primary_eligible"] += 1
                if ghost is not None:
                    qc["n_30s_surrogate_eligible"] += 1
        if used:
            qc["distinct_focal_birds"] += 1
    return events,qc


def zip_download(to: Path) -> dict:
    request = urllib.request.Request(SOURCE_URL,headers={
        "User-Agent":"boids-v15-frozen-original-GPS-forecast/1.0"})
    sha, md5, n = hashlib.sha256(),hashlib.md5(),0
    with urllib.request.urlopen(request,timeout=120) as r, to.open("wb") as out:
        claimed = r.headers.get("Content-Length")
        if claimed and int(claimed) != SOURCE_BYTES:
            raise ValueError("Source length changed before download")
        for block in iter(lambda:r.read(1024*1024),b""):
            n+=len(block)
            if n>ZIP_CAP_BYTES:
                raise ValueError("Source exceeded bounded download size")
            out.write(block);sha.update(block);md5.update(block)
    if n!=SOURCE_BYTES or sha.hexdigest()!=SOURCE_SHA256 or md5.hexdigest()!=SOURCE_MD5:
        raise ValueError("STOP source checksum or size mismatch")
    return {"bytes":n,"sha256":sha.hexdigest(),"md5":md5.hexdigest(),"exact_pinned_match":True}


def verify_original_members(arc:zipfile.ZipFile) -> dict:
    if SOURCE_MEMBERS not in arc.namelist():
        raise ValueError("Missing source SHA256 file list")
    expected={}
    for line in arc.read(SOURCE_MEMBERS).decode("utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m=re.fullmatch(r"([0-9a-fA-F]{64})\s+\*?(.+?)\s*",line)
        if m is None:
            raise ValueError("Unknown source hash manifest structure")
        key=m.group(2).replace("\\","/").lstrip("./")
        expected[key]=m.group(1).lower()
    names=[n for n in arc.namelist() if "/raw_gps/" in n or "/raw_attitude/" in n]
    if len(names)!=56:
        raise ValueError("Changed raw sensor file count")
    for name in names:
        key=name.removeprefix("data/")
        if key not in expected:
            raise ValueError("Unlisted raw member file")
        digest=hashlib.sha256()
        with arc.open(name) as f:
            for block in iter(lambda:f.read(1024*1024),b""):
                digest.update(block)
        if digest.hexdigest()!=expected[key]:
            raise ValueError("STOP source member mismatch")
    return {"verified_sensor_members":56,"manifest_entries":len(expected)}


def get_source_events(archive: Path) -> tuple[dict,list[Event],dict]:
    with zipfile.ZipFile(archive) as arc:
        receipt = verify_original_members(arc)
        gps_names=sorted(n for n in arc.namelist() if "/raw_gps/" in n and n.endswith("_GPS.txt"))
        bytrial=collections.defaultdict(list)
        for name in gps_names:
            spl=Path(name).parts
            if len(spl)<4 or spl[1] not in SOURCE_TRIALS:
                raise ValueError("Changed original source path")
            bytrial[spl[1]].append(name)
        if tuple(sorted(bytrial))!=SOURCE_TRIALS or tuple(len(bytrial[t]) for t in SOURCE_TRIALS)!=(7,11,10):
            raise ValueError("Changed source trial grouping")
        events=[];gate={}
        for trial in SOURCE_TRIALS:
            parsed_files={}
            ref=None
            # Origin is the first original, valid GPS fix of the first lexical bird,
            # available independently of target outcomes and common within trial.
            for name in bytrial[trial]:
                raw=arc.read(name).splitlines()
                if ref is None:
                    for line in raw:
                        status,fix=parse_original_rmc(line.decode("utf-8",errors="replace"))
                        if status=="valid":
                            ref=(fix.lat,fix.lon)
                            break
                parsed_files[name]=raw
            if ref is None:
                raise ValueError("No source trial geographical reference")
            tracks={}
            for name,raw in parsed_files.items():
                bird=Path(name).stem.removesuffix("_GPS")
                tracks[bird]=track_from_lines(bird,raw,*ref)
            rows,qc=trial_events(trial,tracks)
            events.extend(rows)
            gate[trial]=qc
        return receipt,events,gate


def design(events:list[Event], mode:str) -> np.ndarray:
    own=np.asarray([e.x0 for e in events],dtype=float)
    if own.ndim!=2 or own.shape[1]!=8:
        raise ValueError("Invalid own feature shape")
    if mode=="own":
        return own
    if mode not in ("current","stale","ghost"):
        raise ValueError("Unregistered feature mode")
    vectors=[]
    for e in events:
        feat=getattr(e,mode)
        if feat is None:
            raise ValueError("Missing feature in target-matched subset")
        vectors.append(feat)
    partners=np.asarray(vectors,dtype=float)
    if partners.shape!=(len(events),6):
        raise ValueError("Social feature shape changed")
    return np.concatenate((own,partners),axis=1)


def fit_ridge(training:list[Event],mode:str) -> tuple[np.ndarray,np.ndarray,np.ndarray,float]:
    if not training:
        raise ValueError("Empty training")
    X=design(training,mode)
    y=np.asarray([e.target for e in training])
    n=len(training)
    trial_counts=collections.Counter(e.trial for e in training)
    if len(trial_counts)!=2:
        raise ValueError("Require two independent source trial groups for training")
    w=np.asarray([n/(2*trial_counts[e.trial]) for e in training],dtype=float)
    if not np.isclose(w.sum(),n):
        raise AssertionError("Trial balancing broken")
    mean=np.average(X,axis=0,weights=w)
    dev=X-mean
    sd=np.sqrt(np.average(dev**2,axis=0,weights=w))
    sd=np.where(sd<=1e-12,1.,sd)
    scaled=dev/sd
    target_mean=float(np.average(y,weights=w))
    gram=scaled.T@(scaled*w[:,None])+RIDGE_ALPHA*np.eye(X.shape[1])
    coef=np.linalg.solve(gram,scaled.T@(w*(y-target_mean)))
    if not np.isfinite(coef).all():
        raise ValueError("Nonfinite model coefficients")
    return mean,sd,coef,target_mean


def evaluate(training:list[Event], test:list[Event], mode:str) -> float:
    mean,scale,coef,intercept=fit_ridge(training,mode)
    x=design(test,mode)
    y=np.asarray([e.target for e in test])
    pred=(x-mean)/scale@coef+intercept
    delta=np.arctan2(np.sin(y-pred),np.cos(y-pred))
    return float(np.mean(delta**2))


def forecast(events:list[Event],qc:dict) -> dict:
    out={"study":"v15-original-GPS-exploratory-1s-horizontal-turning",
         "status":"NOT_ADMITTED",
         "scientific_scope":"observed short-horizon GPS ground-track heading, NOT social force or 3D niche",
         "frozen_contract":"docs/OBSERVED_HORIZONTAL_TURN_FORECAST_CONTRACT_V15.md",
         "source_episodes":3,"source_bird_trial_files":28,
         "policy":{"min_speed_m_s":MIN_FLIGHT_M_S,"max_speed_m_s":MAX_FLIGHT_M_S,
             "max_contiguous_gap_ms":MAX_CONTIGUOUS_GAP_MS,
             "min_run_seconds":MIN_RUN_LENGTH_MS/1000,"min_run_fixes":MIN_RUN_FIXES,
             "utc_anchor_spacing_seconds":ANCHOR_STRIDE_MS/1000,
             "nearest_raw_utc_max_delta_ms":COFIX_TOLERANCE_MS,
             "max_present_neighbor_m":MAX_NEIGHBOR_DISTANCE_M,
             "target_horizon_seconds":1,"stale_partner_seconds":10,
             "surrogate_same_partner_past_seconds":30,
             "ridge_alpha":RIDGE_ALPHA,
             "standardization":"training-only; equal-total-weight per training source trial",
             "independence":"three source-trial folds, not fixes, birds or dyads"},
         "trial_structural_qc":qc}
    by={t:[e for e in events if e.trial==t] for t in SOURCE_TRIALS}
    faults=[]
    for trial in SOURCE_TRIALS:
        if len(by[trial])<MIN_TRIAL_PRIMARY_ANCHORS:
            faults.append(f"{trial}:only_{len(by[trial])}_matched_anchors")
        distinct=len({e.bird for e in by[trial]})
        if distinct<MIN_TRIAL_BIRDS:
            faults.append(f"{trial}:only_{distinct}_focal_birds")
    if faults:
        out["reasons"]=faults
        return out
    by_trial={}
    for trial in SOURCE_TRIALS:
        tr=[e for e in events if e.trial!=trial]
        te=by[trial]
        errs={mode:evaluate(tr,te,mode) for mode in MODEL_NAMES}
        errs["zero_turn"]=float(np.mean(np.asarray([e.target for e in te])**2))
        by_trial[trial]={"matched_events":len(te),
                         "focal_birds":len({e.bird for e in te}),
                         "mse_rad2":errs,
                         "primary_stale_minus_current_rad2":errs["stale"]-errs["current"],
                         "secondary_own_minus_current_rad2":errs["own"]-errs["current"]}
    focal=np.asarray([v["primary_stale_minus_current_rad2"] for v in by_trial.values()])
    secondary=np.asarray([v["secondary_own_minus_current_rad2"] for v in by_trial.values()])
    out["status"]="EXPLORATORY_OBSERVED_3_TRIALS_NO_CONFIRMATORY_CLAIM"
    out["per_trial"]=by_trial
    out["summary"]={"equal_trial_mean_primary_stale_minus_current_rad2":float(focal.mean()),
                    "primary_positive_trials":int((focal>0).sum()),
                    "equal_trial_mean_secondary_own_minus_current_rad2":float(secondary.mean()),
                    "secondary_positive_trials":int((secondary>0).sum()),
                    "theoretical_min_one_sided_sign_p_with_3_trials":.125,
                    "inference":"descriptive only; no identifiable Reynolds coefficient"}
    matched={t:[e for e in by[t] if e.ghost is not None] for t in SOURCE_TRIALS}
    if all(len(matched[t])>=MIN_TRIAL_GHOST_ANCHORS for t in SOURCE_TRIALS):
        ghost_results={}
        for trial in SOURCE_TRIALS:
            tr=[e for t in SOURCE_TRIALS if t!=trial for e in matched[t]]
            te=matched[trial]
            values={mode:evaluate(tr,te,mode) for mode in (*MODEL_NAMES,"ghost")}
            ghost_results[trial]={"matched_events":len(te),"mse_rad2":values,
                                  "ghost_minus_current_rad2":values["ghost"]-values["current"],
                                  "stale_minus_current_rad2":values["stale"]-values["current"]}
        g=np.array([v["ghost_minus_current_rad2"] for v in ghost_results.values()])
        out["30s_surrogate_secondary"]={"status":"MATCHED_RESTRICTED_SUBSET_EXPLORATORY",
                                        "per_trial":ghost_results,
                                        "equal_trial_mean_ghost_minus_current_rad2":float(g.mean()),
                                        "positive_trials":int((g>0).sum())}
    else:
        out["30s_surrogate_secondary"]={"status":"NOT_ADMITTED_IN_ALL_THREE_TRIALS",
             "matched_events_per_trial":{t:len(v) for t,v in matched.items()}}
    return out


def experiment(out: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/"original_zenodo.zip"
        provenance=zip_download(path)
        integrity,events,qc=get_source_events(path)
        model=forecast(events,qc)
    result={"source_integrity":{"archive":provenance,"members":integrity},**model,
            "limits":["Only three source flock-flight episodes: no confirmatory p<0.05 trial-level sign test",
                      "Time nearest-neighbor co-fixes are not known camera/receiver error calibration",
                      "No GPS altitude, ecological resources, observed learning or experimental social rewiring",
                      "30s negative control uses time-lagged same partner, not independent ghost",
                      "Training folds contain bird IDs overlapping heldout trials; not individual-identity transfer",
                      "No raw coordinates, event-level predictions or animal identities are exported"]}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return result


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,
        default=Path("validation_v15/results/frozen_turn_forecast_v15.json"))
    args=parser.parse_args()
    result=experiment(args.out)
    print("V15_FROZEN_OBSERVED_EXPLORATORY")
    print("SOURCE",json.dumps(result["source_integrity"],sort_keys=True))
    print("QC",json.dumps(result["trial_structural_qc"],sort_keys=True))
    print("STATUS",result["status"])
    if "summary" in result:
        print("RESULT",json.dumps(result["summary"],sort_keys=True))
        print("TRIALS",json.dumps(result["per_trial"],sort_keys=True))
        print("SURROGATE",json.dumps(result["30s_surrogate_secondary"],sort_keys=True))
    else:
        print("GATE_FAIL",json.dumps(result["reasons"]))
    print("RECEIPT",args.out)


if __name__=="__main__":
    main()
