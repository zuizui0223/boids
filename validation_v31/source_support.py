#!/usr/bin/env python3
"""v31-S: strict structural eligibility from source ID+UTC ONLY.
Does not read any location, altitude, movement, or observation-quality values.
The result is an upper bound on later GPS-quality-gated study support.
"""
from __future__ import annotations
import argparse
import collections
import csv
import datetime as dt
import gzip
import json
from pathlib import Path
import tempfile
import source_only as source

ROOT=Path(__file__).resolve().parents[1]
RECEIPT=ROOT/"validation_v31/results/oystercatcher_source_only_v31.json"
MIN_DAY_FIXES=6
MIN_SPAN_HOURS=8.
MIN_OWN_EVENTS=3
MIN_OTHER_BIRDS=5
MIN_OTHER_DAYS=20
MIN_STUDY_BIRDS=8
MIN_STUDY_DAYS=80
MIN_TOTAL_BIRDS=20
MIN_TOTAL_DAYS=300

def upper_bound_from_id_stamps(birds):
    """Source-only chronological eligibility; quality filters only reduce it."""
    complete={}
    for bird,stamps in birds.items():
        byday=collections.defaultdict(set)
        for stamp in stamps:
            byday[stamp.date()].add(stamp)
        for date,v in byday.items():
            if len(v)>=MIN_DAY_FIXES and (max(v)-min(v)).total_seconds()/3600>=MIN_SPAN_HOURS:
                complete[bird,date]=True
    events=[(bird,date) for bird,date in complete if (bird,date-dt.timedelta(days=1)) in complete]
    per_bird=collections.defaultdict(list)
    hist=collections.Counter()
    scored=[]
    bydate=collections.defaultdict(list)
    for bird,date in events: bydate[date].append(bird)
    for date in sorted(bydate):
        for bird in bydate[date]:
            n_own=hist[bird]
            ext_ids=sum(n>0 for other,n in hist.items() if other!=bird)
            ext_days=sum(n for other,n in hist.items() if other!=bird)
            if n_own>=MIN_OWN_EVENTS and ext_ids>=MIN_OTHER_BIRDS and ext_days>=MIN_OTHER_DAYS:
                scored.append((bird,date))
        for bird in bydate[date]:
            hist[bird]+=1
    return {"original_source_distinct_birds":len(birds),
            "original_complete_UTC_days_upper_bound":len(complete),
            "original_consecutive_complete_day_events_upper_bound":len(events),
            "birds_potentially_eligible_before_GPS_quality":len({bird for bird,date in scored}),
            "individual_future_days_potentially_eligible_before_GPS_quality":len(scored),
            "original_time_only_not_location_or_response":True}

def run():
    pinned=json.loads(RECEIPT.read_text(encoding="utf-8"))
    if pinned.get("status")!="SOURCE_ONLY_TWO_ORIGINAL_ZENODO_RECORDS_VERIFIED":
        raise ValueError("Original pinned source-only admission absent")
    result={"status":"ORIGINAL_ID_UTC_STRUCTURAL_AUDIT",
            "source_only_receipt":"validation_v31/results/oystercatcher_source_only_v31.json",
            "no_GPS_location_altitude_speed_or_response_read":True,
            "studies":{}}
    for label,cfg in source.RECORDS.items():
        obj=source.read_api(cfg["record"])
        specs=source.select_gps_files(obj,label,cfg["years"])
        pins={v["file"]["original_gzip_name"]:v for v in pinned["records"][label]["source_only_files"]}
        allstamps=collections.defaultdict(set)
        raw_count=0
        with tempfile.TemporaryDirectory() as folder:
            for f in specs:
                ref=pins[f["name"]]
                path=Path(folder)/f["name"]
                verified=source.fetch_original_file(f,path)
                if verified["original_sha256"]!=ref["file"]["original_sha256"] or verified["bytes"]!=ref["file"]["bytes"]:
                    raise ValueError("Frozen original GPS gzip SHA/size changed")
                with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as csvfile:
                    rd=csv.DictReader(csvfile)
                    if rd.fieldnames!=ref["ID_and_UTC_only"]["header_columns"]:
                        raise ValueError("Frozen original CSV header changed")
                    for r in rd:
                        raw_count+=1
                        bird=(r.get("individual-local-identifier") or "").strip()
                        if not bird: continue
                        try: t=source.timestamp(r.get("timestamp") or "")
                        except ValueError: continue
                        allstamps[bird].add(t)
        expected_rows=sum(x["ID_and_UTC_only"]["original_physical_rows"] for x in pins.values())
        if raw_count!=expected_rows:
            raise ValueError("Previously frozen original physical row count mismatch")
        out=upper_bound_from_id_stamps(allstamps)
        result["studies"][label]={"source_rows":raw_count, **out}
    total_birds=sum(s["birds_potentially_eligible_before_GPS_quality"] for s in result["studies"].values())
    total_days=sum(s["individual_future_days_potentially_eligible_before_GPS_quality"] for s in result["studies"].values())
    result["total_bird_support_UPPER_BOUND"]=total_birds
    result["total_future_days_UPPER_BOUND"]=total_days
    if (any(s["birds_potentially_eligible_before_GPS_quality"]<MIN_STUDY_BIRDS
            or s["individual_future_days_potentially_eligible_before_GPS_quality"]<MIN_STUDY_DAYS
            for s in result["studies"].values()) or
            total_birds<MIN_TOTAL_BIRDS or total_days<MIN_TOTAL_DAYS):
        result["status"]="NOT_ADMITTED_ORIGINAL_ID_UTC_SUPPORT_BEFORE_GPS_OUTCOMES"
        result["no_model_scores_permitted"]=True
    else:
        result["status"]="ORIGINAL_ID_UTC_SUPPORT_POSSIBLE_GPS_QUALITY_GATE_STILL_REQUIRED"
        result["no_model_scores_permitted"]=False
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v31/results/oystercatcher_source_support_v31.json"))
    args=p.parse_args()
    data=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("V31_SOURCE_SUPPORT",json.dumps(data,sort_keys=True,separators=(",",":")))
    print("V31_NO_GPS_POSITION_OR_PREDICTION_OPENED")

if __name__=="__main__": main()
