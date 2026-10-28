#!/usr/bin/env python3
"""v16: predeclared independent eight-flock future-release route memory forecast.

Original Watts et al. 2016 GPS, Zenodo 4943714, Dryad 508j2.
All models predict later release shells from prior releases 5..8.
This is NOT a feeding niche, social causation or recovered Boids force.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import io
import json
import math
import statistics
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import source_gate as source

ORIGINAL_SHA256 = "7380feccd8c2e4e1675679411d1ee8075cd29ccbd2dada98e317ca88053ffbfa"
LAT0 = 51 + 49/60 + 23.48/3600
LON0 = -(1 + 21/60 + 26.29/3600)
RADIUS_M = 6_371_008.8
SHELLS = tuple(range(500,4501,500))
MAX_CROSSING_OVERSHOOT_M = 50.
MAX_ADJACENT_DISPLACEMENT_M = 50.
MAX_TIME_GAP_MS = 1000
HISTORIC_RELEASES = (5,6,7,8)
TEST_RELEASE_MIN = 9
TEST_RELEASE_MAX = 15
MIN_TEST_RELEASES_PER_FLOCK = 3
MIN_TARGET_SHELL_OBS_PER_FLOCK = 30
BOOTS = 10000
BOOT_SEED = 20261028
REQUIRED_FLOCKS = tuple(f"{x:02d}" for x in range(1,9))
REQUIRED_COLS = ("VALID","UTC DATE","UTC TIME","MS","LATITUDE","N/S","LONGITUDE","E/W")

def wrap(theta:float)->float:
    return math.atan2(math.sin(theta),math.cos(theta))

def mean_direction(v:list[float])->float|None:
    if not v:
        return None
    s=sum(math.sin(x) for x in v)
    c=sum(math.cos(x) for x in v)
    if math.hypot(s,c)<1e-9:
        return None
    return math.atan2(s,c)

def projected(lat:float,lon:float)->tuple[float,float]:
    return (RADIUS_M*math.cos(math.radians(LAT0))*math.radians(lon-LON0),
            RADIUS_M*math.radians(lat-LAT0))

def parse_date_clock_ms(row:dict)->int:
    ds=[int(x) for x in str(row["UTC DATE"]).strip().split("/")]
    ts=[int(x) for x in str(row["UTC TIME"]).strip().split(":")]
    if len(ds)!=3 or len(ts)!=3:
        raise ValueError("Expected original Qstarz YYYY/M/D H:M:S and separate MS")
    import datetime
    date=datetime.date(*ds)
    h,m,s=ts
    ms=int(str(row["MS"]).strip())
    if not (0<=h<24 and 0<=m<60 and 0<=s<60 and 0<=ms<=999):
        raise ValueError("Out-of-range original UTC clock token")
    return date.toordinal()*86_400_000 + ((h*60+m)*60+s)*1000+ms

def original_row_xy_t(row:dict)->tuple[int,float,float]|None:
    if str(row.get("VALID","")).strip().upper()!="FIXED":
        return None
    try:
        lat=float(row["LATITUDE"])
        lon=float(row["LONGITUDE"])
        hemi_lat=str(row["N/S"]).strip().upper()
        hemi_lon=str(row["E/W"]).strip().upper()
        if hemi_lat not in ("N","S") or hemi_lon not in ("E","W"):
            return None
        lat=abs(lat)*(1 if hemi_lat=="N" else -1)
        lon=abs(lon)*(1 if hemi_lon=="E" else -1)
        if not all(math.isfinite(v) for v in (lat,lon)):
            return None
        if not (-90<=lat<=90 and -180<=lon<=180):
            return None
        t=parse_date_clock_ms(row)
        x,y=projected(lat,lon)
        return t,x,y
    except (ValueError,KeyError,TypeError,OverflowError):
        return None

def first_shell_crossings(observations:list[tuple[int,float,float]])->dict[int,float]:
    """Preserve recorded row order; use only first OUTWARD measured crossings.

    Does NOT interpolate or reassign data to new times or shells. Invalid
    observations should be handled by splitting upstream segments.
    """
    observed={}
    last=None
    for record in observations:
        if record is None:
            last=None
            continue
        t,x,y=record
        r=math.hypot(x,y)
        if last is not None:
            pt,px,py=last
            prev_r=math.hypot(px,py)
            displacement=math.hypot(x-px,y-py)
            if not (0<t-pt<=MAX_TIME_GAP_MS
                    and displacement<=MAX_ADJACENT_DISPLACEMENT_M):
                last=record
                continue
            for shell in SHELLS:
                if (shell not in observed and prev_r<shell<=r
                    and r-shell<=MAX_CROSSING_OVERSHOOT_M):
                    observed[shell]=math.atan2(x,y)
        last=record
        if len(observed)==len(SHELLS):
            break
    return observed

def parse_track(arc:zipfile.ZipFile,name:str)->tuple[dict[int,float],dict]:
    selected={}
    last=None
    n_valid=0
    n_invalid=0
    n_gaps=0
    # Stream to avoid holding millions of Qstarz rows in memory.
    with arc.open(name) as raw:
        text=io.TextIOWrapper(raw,encoding="utf-8-sig",errors="replace",newline="")
        reader=csv.DictReader(text)
        if not set(REQUIRED_COLS).issubset(set(reader.fieldnames or ())):
            raise ValueError("GPS schema differs from preregistered Qstarz schema")
        for row in reader:
            item=original_row_xy_t(row)
            if item is None:
                last=None;n_invalid+=1
                continue
            n_valid+=1
            t,x,y=item
            r=math.hypot(x,y)
            if last is not None:
                pt,px,py=last
                prior_r=math.hypot(px,py)
                step=math.hypot(x-px,y-py)
                if 0<t-pt<=MAX_TIME_GAP_MS and step<=MAX_ADJACENT_DISPLACEMENT_M:
                    for shell in SHELLS:
                        if shell not in selected and prior_r<shell<=r and r-shell<=MAX_CROSSING_OVERSHOOT_M:
                            selected[shell]=math.atan2(x,y)
                else:
                    n_gaps+=1
            last=item
            if len(selected)==len(SHELLS):
                break
    return selected,{"valid_rows_scanned_to_last_first_crossing":n_valid,
                     "invalid_rows_scanned":n_invalid,
                     "temporal_or_position_breaks":n_gaps,
                     "shells_observed":len(selected)}

def get_source_profiles(archive:Path)->tuple[dict,dict]:
    tracks={}
    qc=collections.defaultdict(collections.Counter)
    with zipfile.ZipFile(archive) as arc:
        source.archive_name_gate(arc.infolist())
        names=[n for n in arc.namelist() if
               n.lower().endswith(".csv") and
               not Path(n).name.startswith("._")]
        if len(names)!=559:
            raise ValueError("Original 559 track count changed")
        for name in sorted(names):
            identity=source.member_identity(name)
            if identity is None or identity in tracks:
                raise ValueError("Source bird-release identity changed")
            track,info=parse_track(arc,name)
            tracks[identity]=track
            flock=identity[0]
            qc[flock]["tracks"]+=1
            qc[flock]["valid_raw_fix_rows_until_crossing"]+=info["valid_rows_scanned_to_last_first_crossing"]
            qc[flock]["invalid_raw_fix_rows_until_crossing"]+=info["invalid_rows_scanned"]
            qc[flock]["raw_gaps_until_crossing"]+=info["temporal_or_position_breaks"]
            qc[flock]["crossings_observed"]+=info["shells_observed"]
    return tracks,{k:dict(v) for k,v in qc.items()}


def training_templates(tracks:dict)->tuple[dict,dict]:
    individual=collections.defaultdict(lambda:collections.defaultdict(list))
    for (flock,bird,release),route in tracks.items():
        if release in HISTORIC_RELEASES:
            for shell,angle in route.items():
                individual[(flock,bird)][shell].append(angle)
    individual_angles={(flock,bird):{
         shell:mean_direction(v) for shell,v in by_shell.items()}
         for (flock,bird),by_shell in individual.items()}
    # Each bird gets equal weight, not one weight per source GPS fix.
    flock_aggregates=collections.defaultdict(lambda:collections.defaultdict(list))
    for (flock,_),shells in individual_angles.items():
        for shell,angle in shells.items():
            if angle is not None:
                flock_aggregates[flock][shell].append(angle)
    flock_angles={flock:{shell:mean_direction(v) for shell,v in shells.items()}
                  for flock,shells in flock_aggregates.items()}
    return individual_angles,flock_angles


def leave_flock_out_population(flock_models:dict,excluded:str)->dict[int,float|None]:
    out={}
    for shell in SHELLS:
        values=[v[shell] for f,v in flock_models.items()
                if f!=excluded and shell in v and v[shell] is not None]
        out[shell]=mean_direction(values)
    return out


def evaluate_routes(tracks:dict)->dict:
    individual,flock_templates=training_templates(tracks)
    trial_rows={}
    for heldout in REQUIRED_FLOCKS:
        baseline=leave_flock_out_population(flock_templates,heldout)
        own_flock=flock_templates.get(heldout,{})
        records=collections.defaultdict(list)
        total_target_shells=0
        personal_backoffs=0
        for (flock,bird,release),angles in tracks.items():
            if flock!=heldout or not TEST_RELEASE_MIN<=release<=TEST_RELEASE_MAX:
                continue
            own=individual.get((flock,bird),{})
            for shell,target in angles.items():
                global_ang=baseline.get(shell)
                group_ang=own_flock.get(shell)
                if global_ang is None or group_ang is None:
                    continue  # historical-support-only fixed eligibility
                indiv_ang=own.get(shell)
                if indiv_ang is None:
                    indiv_ang=group_ang
                    personal_backoffs+=1
                total_target_shells+=1
                records[release].append((
                    wrap(target-global_ang)**2,
                    wrap(target-group_ang)**2,
                    wrap(target-indiv_ang)**2
                ))
        release_scores={}
        for release,rows in sorted(records.items()):
            if not rows:
                continue
            a=np.asarray(rows,float)
            release_scores[release]={"targets":len(rows),
                "S0_global":float(a[:,0].mean()),
                "S1_group":float(a[:,1].mean()),
                "S2_individual":float(a[:,2].mean())}
        n_release=len(release_scores)
        means={key:float(np.mean([v[key] for v in release_scores.values()]))
               if release_scores else None
               for key in ("S0_global","S1_group","S2_individual")}
        trial_rows[heldout]={
            "later_releases_with_matched_shells":n_release,
            "matched_future_bird_release_shells":total_target_shells,
            "individual_template_backoff_target_count":personal_backoffs,
            "admitted":n_release>=MIN_TEST_RELEASES_PER_FLOCK and
                       total_target_shells>=MIN_TARGET_SHELL_OBS_PER_FLOCK,
            "mean_mse_rad2":means,
            "primary_global_minus_group_rad2":
                 means["S0_global"]-means["S1_group"] if n_release else None,
            "secondary_group_minus_individual_rad2":
                 means["S1_group"]-means["S2_individual"] if n_release else None,
            "by_release":release_scores
        }
    admitted=all(trial_rows[f]["admitted"] for f in REQUIRED_FLOCKS)
    if not admitted:
        return {"status":"NOT_ADMITTED_8_FLOCKS_INCOMPLETE",
                "all_8_flocks_admitted":False,
                "per_flock_structural_result":{f:{
                    "later_releases_with_matched_shells":v["later_releases_with_matched_shells"],
                    "matched_future_bird_release_shells":v["matched_future_bird_release_shells"]}
                  for f,v in trial_rows.items()}}
    primary=np.array([trial_rows[f]["primary_global_minus_group_rad2"] for f in REQUIRED_FLOCKS])
    secondary=np.array([trial_rows[f]["secondary_group_minus_individual_rad2"] for f in REQUIRED_FLOCKS])
    rng=np.random.default_rng(BOOT_SEED)
    boot=rng.integers(0,len(primary),size=(BOOTS,len(primary)))
    def summ(a):
        return {"equal_flock_mean":float(a.mean()),
                "bootstrap_95_flock_percentile":list(map(float,np.quantile(a[boot].mean(axis=1),[.025,.975]))),
                "positive_flocks":int((a>0).sum()),"n_flc":len(a)}
    return {"status":"EXPLORATORY_INDEPENDENT_8_FLOCKS_REPEATED_ROUTE_FORECAST",
            "all_8_flocks_admitted":True,
            "flock_primary":summ(primary),
            "flock_secondary":summ(secondary),
            "per_flock":trial_rows,
            "inference":"Reproducible route-history prediction, not proof of learning, habitat niche, social causality or clock-shift mechanism",
            "exact_unanimous_one_sided_sign_p_min":1/256}


def experiment(out:Path)->dict:
    record=source.get_api(source.RECORD_API)
    file=source.select_file(record)
    with tempfile.TemporaryDirectory() as root:
        archive=Path(root)/"Data.zip"
        downloaded=source.bounded_download(file,archive)
        if downloaded["sha256"]!=ORIGINAL_SHA256:
            raise ValueError("Previously pinned independent ZIP SHA256 changed")
        tracks,qc=get_source_profiles(archive)
        results=evaluate_routes(tracks)
    receipt={
        "study":"v16-2016-independent-eight-flock-repeated-navigation-route-memory",
        "data_source":"Watts et al. 2016, Zenodo 4943714, 10.5061/dryad.508j2",
        "source_integrity":downloaded,
        "source_actual_csv_tracks":len(tracks),
        "status":results["status"],
        "registered_protocol":"docs/DUAL_TIMESCALE_ROUTE_PREDICTION_CONTRACT_V16.md",
        "target":"observed first outward GPS route bearing at 500..4500 m radial shells",
        "historic_releases":list(HISTORIC_RELEASES),
        "test_release_window":[TEST_RELEASE_MIN,TEST_RELEASE_MAX],
        "projection_origin":"published Bladon release location",
        "crossing_gate":{"max_overshoot_m":MAX_CROSSING_OVERSHOOT_M,
                         "max_step_m":MAX_ADJACENT_DISPLACEMENT_M,
                         "max_utc_gap_ms":MAX_TIME_GAP_MS},
        "source_only_quality_by_flock":qc,
        "observed_result":results,
        "previous_negative_v15_untouched":True,
        "limits":[
            "Course history is navigation, not foraging resources or a species' fundamental niche.",
            "This is an observational future-release benchmark of published experimental data, not a new manipulation.",
            "Clock-shift treatment schedule was not used or inferred from track outcomes.",
            "No social-force coefficients, extra GPS height accuracy or resource rewards were fitted.",
            "Individual IDs and all raw GPS coordinates remain ephemeral on the runner.",
            "Per-flock cluster uncertainty does not imply 8 independent species."]
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")
    return receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v16/results/slow_route_forecast_v16.json"))
    a=p.parse_args()
    d=experiment(a.out)
    print("V16_SOURCE_VERIFIED",json.dumps(d["source_integrity"],sort_keys=True))
    print("V16_ROUTE_QC",json.dumps(d["source_only_quality_by_flock"],sort_keys=True))
    print("V16_SLOW_STATUS",d["status"])
    print("V16_SLOW_RESULT",json.dumps(d["observed_result"],sort_keys=True))
    print("V16_SLOW_AGGREGATE_RECEIPT",a.out)


if __name__=="__main__":
    main()
