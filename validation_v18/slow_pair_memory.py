#!/usr/bin/env python3
"""v18: frozen observed future-memory route forecast from 14 external pair components.

Only TR GPS tracks create historical templates; only later CM tracks are scored.
Three models share identical supported CM crossing targets, and 14 original
pairs (not 426 files or GPS fixes) are the independent evaluation clusters.
No GPS/wind source rows, animal coordinates, or exact flight times are exported.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import io
import json
import math
import re
import tempfile
import zipfile
from pathlib import Path
import numpy as np

import fourteen_pair_source_gate as source

ORIGINAL_ZIP_SHA256 = "8e3f588ae927ab196f8c9dc9eebc9146bf656b344e68db8ba5f3c20d49edc3dc"
ORIGINAL_META_SHA256 = "8796f115d80f13b455704a2ad4c8710e23b18103ab0ba6d913c553fbd7342279"
LAT_LON_ORIGIN={"LH": (51.8303056,-1.3915),
                "SH": (51.7527778,-1.42375)}
EARTH_RADIUS_METRES=6_371_008.8
SHELLS=(250,500,750,1000,1250,1500,1750,2000)
MAX_CROSSING_OVERSHOOT_M=75.
MAX_STEP_M=100.
MAX_GPS_GAP_S=5.
MIN_PAIR_MEMORY_TEST_FILES=2
MIN_PAIR_MATCHED_SHELL_UNITS=8
BOOTSTRAP_RESAMPLES=10000
BOOTSTRAP_SEED=20261028
ORIGINAL_GPS_FILES=426
ORIGINAL_PAIRS=14
FILE_PATTERN=re.compile(
 r"(?P<bird>\d{2}-[A-Za-z]\d{2})_Site_(?P<site>LH|SH)_"
 r"(?P<mode>pair\*?|solo)_(?:Nocheck|Checked)_(?P<stage>TR|CM)_"
 r"(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\.csv$",re.I
)
FIELD_REQUIRED=("DT","Latitude","Longitude")

def wrapped(theta:float)->float:
    return math.atan2(math.sin(theta),math.cos(theta))

def mean_angle(angles:list[float])->float|None:
    if not angles:return None
    s=sum(math.sin(x) for x in angles)
    c=sum(math.cos(x) for x in angles)
    if math.hypot(s,c)<1e-12:return None
    return math.atan2(s,c)

def projected(site:str,latitude:float,longitude:float)->tuple[float,float]:
    if site not in LAT_LON_ORIGIN:
        raise ValueError("Unknown original release-site metadata")
    lat0,lon0=LAT_LON_ORIGIN[site]
    return (EARTH_RADIUS_METRES*math.cos(math.radians(lat0))*math.radians(longitude-lon0),
            EARTH_RADIUS_METRES*math.radians(latitude-lat0))

def original_time_utc(value:str)->dt.datetime:
    s=str(value or "").strip()
    if not s:
        raise ValueError("Missing original ISO datetime")
    out=dt.datetime.fromisoformat(s)
    if out.tzinfo is not None:
        out=out.astimezone(dt.timezone.utc).replace(tzinfo=None)
    if not (2024<=out.year<=2025):
        raise ValueError("Unexpected original GPS year")
    return out

def file_identity(path:str)->tuple[str,str,str,str,str]|None:
    name=Path(path).name
    match=FILE_PATTERN.fullmatch(name)
    if not match:return None
    return (match.group("bird").upper(),match.group("site").upper(),
            match.group("mode").lower().rstrip("*"),match.group("stage").upper(),
            match.group("date"))

def read_first_crossing(arc:zipfile.ZipFile,member:str,site:str)->tuple[dict[int,float],dict]:
    observed={}
    prev=None
    valid=invalid=gaps=0
    with arc.open(member) as stream:
        text=io.TextIOWrapper(stream,encoding="utf-8-sig",errors="replace",newline="")
        reader=csv.DictReader(text)
        if not set(FIELD_REQUIRED).issubset(set(reader.fieldnames or [])):
            raise ValueError("Original 18-column header misses GPS clock or location")
        for row in reader:
            try:
                t=original_time_utc(row["DT"])
                lat=float(row["Latitude"])
                lon=float(row["Longitude"])
                if (not math.isfinite(lat) or not math.isfinite(lon) or
                    not(-90<=lat<=90 and -180<=lon<=180)):
                    raise ValueError("GPS coordinate invalid")
                x,y=projected(site,lat,lon)
            except (ValueError,OverflowError,TypeError,KeyError):
                invalid+=1
                prev=None
                continue
            valid+=1
            radius=math.hypot(x,y)
            if prev is not None:
                pt,px,py=prev
                gap=(t-pt).total_seconds()
                distance=math.hypot(x-px,y-py)
                if 0<gap<=MAX_GPS_GAP_S and distance<=MAX_STEP_M:
                    prior_radius=math.hypot(px,py)
                    for shell in SHELLS:
                        if (shell not in observed and prior_radius<shell<=radius
                            and radius-shell<=MAX_CROSSING_OVERSHOOT_M):
                            observed[shell]=math.atan2(x,y)
                else:
                    gaps+=1
            prev=(t,x,y)
            if len(observed)==len(SHELLS):
                break
    return observed,{"valid_original_rows_scanned_until_final_first_crossing":valid,
                     "invalid_original_rows_scanned":invalid,
                     "clock_or_distance_discontinuities":gaps,
                     "shells_observed":len(observed)}

def get_source_tracks(path:Path,meta_path:Path)->tuple[dict,dict,dict]:
    with meta_path.open("r",encoding="utf-8-sig",newline="") as f:
        pairs=list(csv.DictReader(f))
    roster={};sites={}
    pair_birds=collections.defaultdict(set)
    for row in pairs:
        for bird in (row["Bird"],row["Partner"]):
            if bird in roster:raise ValueError("Bird belongs to two pairs")
            roster[bird]=row["Pair_ID"]
            pair_birds[row["Pair_ID"]].add(bird)
        sites[row["Pair_ID"]]=row["Additional_training_site"]
    if len(pair_birds)!=ORIGINAL_PAIRS or any(len(b)!=2 for b in pair_birds.values()):
        raise ValueError("Changed independently published pair count")
    with zipfile.ZipFile(path) as arc:
        names=sorted(x for x in arc.namelist()
                    if x.lower().endswith(".csv") and not Path(x).name.startswith("._"))
        if len(names)!=ORIGINAL_GPS_FILES:
            raise ValueError("Original GPS file count changed")
        manifest=[]
        for name in names:
            ident=file_identity(name)
            if ident is None:raise ValueError("Unrecognized original bird/site/stage/mode filename")
            bird,site,mode,stage,date=ident
            if bird not in roster:
                raise ValueError("Original GPS bird not in external pair roster")
            manifest.append({"file":name,"pair":roster[bird],"bird":bird,
                             "site":site,"mode":mode,"stage":stage,"date":date})
        counts=collections.defaultdict(collections.Counter)
        for entry in manifest:
            counts[entry["pair"]][(entry["site"],entry["stage"])]+=1
        # This gate uses filenames ONLY, before opening any GPS response.
        failures=[]
        for pair in sorted(pair_birds):
            for site in LAT_LON_ORIGIN:
                if counts[pair][(site,"TR")]==0:
                    failures.append(f"{pair}_{site}_no_training")
                if counts[pair][(site,"CM")]==0:
                    failures.append(f"{pair}_{site}_no_memory_test")
            if sum(counts[pair][(site,"CM")] for site in LAT_LON_ORIGIN)<MIN_PAIR_MEMORY_TEST_FILES:
                failures.append(f"{pair}_insufficient_memory_files")
        qc={"source_gps_files":len(manifest),
            "original_independent_pair_ids":len(pair_birds),
            "pair_train_CM_file_counts":{p:{site:{
                "TR":counts[p][(site,"TR")],
                "CM":counts[p][(site,"CM")]}
                for site in LAT_LON_ORIGIN} for p in sorted(pair_birds)},
            "stage_filename_only_failures":failures,
            "prior_stage_site_manifest_gate_passed":len(failures)==0,
            "GPS_positions_exported":False}
        if failures:return {},qc,{"roster":roster,"pair_birds":dict(pair_birds),"sites":sites}
        tracks={}
        per_pair_qc=collections.defaultdict(collections.Counter)
        for e in manifest:
            crossing,info=read_first_crossing(arc,e["file"],e["site"])
            key=(e["pair"],e["bird"],e["site"],e["mode"],e["stage"],e["file"])
            tracks[key]=crossing
            q=per_pair_qc[e["pair"]]
            q["original_track_files"]+=1
            q["crossings_seen"]+=info["shells_observed"]
            q["original_GPS_rows_read"]+=info["valid_original_rows_scanned_until_final_first_crossing"]
            q["invalid_GPS_rows"]+=info["invalid_original_rows_scanned"]
            q["temporal_or_distance_discontinuities"]+=info["clock_or_distance_discontinuities"]
        qc["source_quality_by_pair"]={p:dict(v) for p,v in per_pair_qc.items()}
        return tracks,qc,{"roster":roster,"pair_birds":dict(pair_birds),"sites":sites}

def build_historic_templates(tracks:dict)->tuple[dict,dict]:
    observed=collections.defaultdict(list)
    for (pair,bird,site,mode,stage,name),angles in tracks.items():
        if stage!="TR":continue
        for shell,angle in angles.items():
            observed[(pair,bird,site,shell)].append(angle)
    personal={k:mean_angle(v) for k,v in observed.items()}
    group_obs=collections.defaultdict(list)
    for (pair,bird,site,shell),angle in personal.items():
        if angle is not None:
            group_obs[(pair,site,shell)].append(angle)
    group={k:mean_angle(v) for k,v in group_obs.items()}
    return personal,group

def population_without_pair(group:dict,pair:str,site:str,shell:int)->float|None:
    others=[val for (p,s,r),val in group.items()
            if p!=pair and s==site and r==shell and val is not None]
    return mean_angle(others)

def score(tracks:dict,original_pair_ids:list[str])->dict:
    personal,group=build_historic_templates(tracks)
    # pair -> site -> mode -> bird -> flight-average errors, then mean at
    # each level. Avoid domination by repetitions or number of GPS fixes.
    levels=collections.defaultdict(lambda:collections.defaultdict(
        lambda:collections.defaultdict(lambda:collections.defaultdict(list))))
    matched_support=collections.Counter()
    matched_files=collections.defaultdict(set)
    fallback=collections.Counter()
    for (pair,bird,site,mode,stage,name),targets in tracks.items():
        if stage!="CM":continue
        terms=[]
        for shell,y in targets.items():
            baseline=population_without_pair(group,pair,site,shell)
            g=group.get((pair,site,shell))
            if baseline is None or g is None:
                continue
            own=personal.get((pair,bird,site,shell))
            if own is None:
                own=g
                fallback[pair]+=1
            terms.append([wrapped(y-baseline)**2,
                          wrapped(y-g)**2,
                          wrapped(y-own)**2])
        if terms:
            arr=np.asarray(terms,float)
            levels[pair][site][mode][bird].append(arr.mean(axis=0))
            matched_files[pair].add(name)
            matched_support[pair]+=len(terms)
    stop=[]
    for pair in original_pair_ids:
        if len(matched_files[pair])<MIN_PAIR_MEMORY_TEST_FILES or (
                matched_support[pair]<MIN_PAIR_MATCHED_SHELL_UNITS):
            stop.append({"pair":pair,"matched_CM_files":len(matched_files[pair]),
                         "matched_shell_targets":matched_support[pair]})
    if stop:
        return {"status":"NOT_ADMITTED_FROZEN_CM_ROUTE_SUPPORT",
                "pair_support":stop,
                "eligible_CM_track_count_by_pair":{p:len(matched_files[p])
                                                   for p in original_pair_ids},
                "eligible_CM_shell_count_by_pair":{p:matched_support[p]
                                                   for p in original_pair_ids},
                "any_prediction_score_exported":False}
    all_pair={}
    for pair in sorted(original_pair_ids):
        cells={}
        for site in sorted(levels[pair]):
            for mode in sorted(levels[pair][site]):
                bybird=levels[pair][site][mode]
                birds=np.array([np.mean(v,axis=0) for v in bybird.values()])
                mean=birds.mean(axis=0)
                cells[f"{site}_{mode}"]={"n_birds":len(bybird),
                    "n_CM_tracks":sum(len(x) for x in bybird.values()),
                    "mse_M0_M1_M2_rad2":list(map(float,mean)),
                    "pair_gain_M0_minus_M1_rad2":float(mean[0]-mean[1]),
                    "individual_gain_M1_minus_M2_rad2":float(mean[1]-mean[2])}
        err=np.array([c["mse_M0_M1_M2_rad2"] for c in cells.values()]).mean(axis=0)
        all_pair[pair]={
            "matched_CM_files":len(matched_files[pair]),
            "matched_CM_shell_targets":int(matched_support[pair]),
            "historical_no_self_template_fallback_shells":int(fallback[pair]),
            "observed_site_mode_cells":len(cells),
            "cell_scores":cells,
            "mse_M0_M1_M2_rad2":list(map(float,err)),
            "primary_population_minus_pair_rad2":float(err[0]-err[1]),
            "secondary_pair_minus_individual_rad2":float(err[1]-err[2])}
    gain=np.array([r["primary_population_minus_pair_rad2"] for r in all_pair.values()])
    personal_gain=np.array([r["secondary_pair_minus_individual_rad2"] for r in all_pair.values()])
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    inds=rng.integers(0,len(gain),size=(BOOTSTRAP_RESAMPLES,len(gain)))
    def summ(v):
        lo,hi=np.quantile(v[inds].mean(axis=1),(.025,.975))
        return {"equal_pair_mean_gain_rad2":float(v.mean()),
                "bootstrap_95_pair_percentile":[float(lo),float(hi)],
                "positive_independent_pairs":int((v>0).sum()),
                "n_independent_pairs":len(v)}
    return {"status":"EXPLORATORY_14_PAIR_FUTURE_CM_ROUTE_MEMORY_FORECAST",
            "primary_pair_history":summ(gain),
            "secondary_individual_history":summ(personal_gain),
            "per_pair":all_pair,
            "total_matched_CM_tracks":sum(len(v) for v in matched_files.values()),
            "total_matched_CM_shell_targets":sum(matched_support.values()),
            "notes":[
                "14 independently assigned paired bird clusters are statistical units",
                "CM memory-test route geometry is a future endpoint; TR-only template history",
                "No weather, true altitude niche, neural memory causality, or motor Boids forces",
                "Original source has processed/trimmed GPS rather than native sensor NMEA"
            ]}

def experiment(out:Path)->dict:
    with tempfile.TemporaryDirectory() as tmp:
        pair_file=Path(tmp)/"CM info.csv"
        zip_file=Path(tmp)/"CM_trimmed.zip"
        md=source.download_pinned(source.PAIR_PATH,source.PAIR_BYTES,
             source.PAIR_BLOB_SHA1,100000,pair_file)
        zd=source.download_pinned(source.ZIP_PATH,source.ZIP_BYTES,
             source.ZIP_BLOB_SHA1,source.ZIP_CAP,zip_file)
        if md["sha256"]!=ORIGINAL_META_SHA256 or zd["sha256"]!=ORIGINAL_ZIP_SHA256:
            raise ValueError("Source changed after v17-D independent hash freeze")
        p=source.independent_pair_assignments(pair_file)
        tracks,qc,meta=get_source_tracks(zip_file,pair_file)
        if qc["stage_filename_only_failures"]:
            result={"status":"NOT_ADMITTED_ORIGINAL_FILENAME_STAGE_SITE_GATE",
                    "stage_filename_only_failures":qc["stage_filename_only_failures"],
                    "any_prediction_score_exported":False}
        else:
            result=score(tracks,sorted(meta["pair_birds"]))
    receipt={
        "study":"v18-independent-14-original-pair-history-predicts-later-CM-trajectory",
        "result_status":result["status"],
        "source":{"original_author_commit":source.REV,
                  "gps_sha256":zd["sha256"],
                  "pair_ledger_sha256":md["sha256"],
                  "source_pair_count":p["original_published_pair_ID_count"],
                  "source_raw_track_license":"unverified_not_redistributed"},
        "registered_protocol":"docs/V18_FROZEN_14PAIR_MEMORY_FORECAST_CONTRACT.md",
        "original_data_status":"authors_processed_trimmed_GPS_not_raw_unmodified_receiver_NMEA",
        "original_site_locations_degrees":{"LH":"as registered",
                                          "SH":"as registered"},
        "radial_shell_m":list(SHELLS),
        "historic_source_stage":"TR",
        "fully_heldout_target_stage":"CM",
        "source_quality":qc,
        "observed_result":result,
        "frozen_previous_v13_v15_v16_v17_endpoints_unchanged":True,
        "raw_individual_GPS_or_response_rows_exported":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2,
                              allow_nan=False)+"\n",encoding="utf-8")
    return receipt

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v18/results/slow_pair_memory_v18.json"))
    a=ap.parse_args()
    d=experiment(a.out)
    print("V18_SOURCE",json.dumps(d["source"],sort_keys=True))
    print("V18_QC",json.dumps(d["source_quality"],sort_keys=True))
    print("V18_STATUS",d["result_status"])
    if "primary_pair_history" in d["observed_result"]:
        print("V18_PRIMARY",json.dumps(d["observed_result"]["primary_pair_history"],sort_keys=True))
        print("V18_SECONDARY",json.dumps(d["observed_result"]["secondary_individual_history"],sort_keys=True))
        print("V18_PER_PAIR",json.dumps(d["observed_result"]["per_pair"],sort_keys=True))
    else:
        print("V18_STOP",json.dumps(d["observed_result"],sort_keys=True))
    print("V18_FROZEN_AGGREGATE",a.out)

if __name__=="__main__":
    main()
