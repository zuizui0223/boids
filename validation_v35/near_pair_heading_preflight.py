"""v35 source-only original paired-heading admission for tide × Boids.

No observed neighbor influence or crowd alignment is estimated. Original per-bird
past heading and future target-heading eligibility are kept separate.
"""
from __future__ import annotations
import argparse,csv,gzip,json,math,tempfile
from collections import Counter,defaultdict,deque
from datetime import datetime
from pathlib import Path
from source_preflight import download_and_pin,parse_stamp,haversine_m

def heading(a,b,dt_limit=(120,1800),speed_limit=(.4,80.)):
    dt=(b["time"]-a["time"]).total_seconds()
    if dt < dt_limit[0] or dt > dt_limit[1]:return None
    metres=haversine_m((None,a["lat"],a["lon"]),(None,b["lat"],b["lon"]))
    speed=metres*3.6/dt
    if not(speed_limit[0]<=speed<=speed_limit[1]):return None
    latrad=math.radians(.5*(a["lat"]+b["lat"]))
    x=(b["lon"]-a["lon"])*math.cos(latrad)
    y=b["lat"]-a["lat"]
    n=math.hypot(x,y)
    return (x/n,y/n) if n>0 else None

def audit(path,year):
    animals=defaultdict(list)
    events=set();drops=Counter();original=0
    with gzip.open(path,"rt",newline="",encoding="utf-8-sig") as input:
        rows=csv.DictReader(input)
        needed={"event-id","timestamp","location-lat","location-long",
                "individual-local-identifier","visible"}
        if not needed<=set(rows.fieldnames or []):
            raise ValueError("Original source Movebank field schema absent")
        for row in rows:
            original+=1
            if row["visible"].strip().upper() in ("FALSE","0"):
                drops["not_visible"]+=1;continue
            ident=row["individual-local-identifier"].strip()
            event=row["event-id"].strip()
            if not ident or not event or event in events:
                drops["missing_id_or_duplicate_event"]+=1;continue
            events.add(event)
            try:
                lat=float(row["location-lat"])
                lon=float(row["location-long"])
                t=parse_stamp(row["timestamp"])
            except (ValueError,TypeError):
                drops["unreadable_original_fix"]+=1;continue
            if not(math.isfinite(lat) and math.isfinite(lon) and 53.2<=lat<=53.7 and 5.7<=lon<=6.6):
                drops["not_in_source_study_region"]+=1;continue
            animals[ident].append({"time":t,"lat":lat,"lon":lon,"bird":ident,
                                   "past_heading":None,"next_heading":None})
    valid_prior=valid_next=0
    for arr in animals.values():
        arr.sort(key=lambda x:x["time"])
        for i,fix in enumerate(arr):
            if i>0:
                fix["past_heading"]=heading(arr[i-1],fix)
                valid_prior+=fix["past_heading"] is not None
            if i+1<len(arr):
                fix["next_heading"]=heading(fix,arr[i+1])
                valid_next+=fix["next_heading"] is not None
    fixes=sorted((r for arr in animals.values() for r in arr),key=lambda r:r["time"])
    nearby=deque();pair_count=0;qualified_directed=0;pairdays=set();days=set()
    participating=set();dyads=set()
    for fix in fixes:
        t=fix["time"]
        while nearby and (t-nearby[0]["time"]).total_seconds()>5:
            nearby.popleft()
        for other in nearby:
            if other["bird"]==fix["bird"]:continue
            if haversine_m((None,fix["lat"],fix["lon"]),
                           (None,other["lat"],other["lon"]))>100:continue
            pair_count+=1
            dyad=tuple(sorted((fix["bird"],other["bird"])))
            num=0
            if fix["past_heading"] is not None and fix["next_heading"] is not None and other["past_heading"] is not None:
                num+=1
            if other["past_heading"] is not None and other["next_heading"] is not None and fix["past_heading"] is not None:
                num+=1
            if num:
                qualified_directed+=num
                pairdays.add((t.date(),dyad))
                days.add(t.date())
                dyads.add(dyad)
                participating.update(dyad)
        nearby.append(fix)
    admission=(qualified_directed>=200 and len(participating)>=5 and
               len(dyads)>=5 and len(days)>=10)
    return {"year":year,"status":"M3_SOURCE_HEADING_FEASIBLE_ONLY" if admission else "NOT_ADMITTED_SOCIAL_MOVEMENT_FORECAST",
            "source":"ZENODO_ORIGINAL_GPS",
            "raw_original_fixes":original,
            "admitted_visible_region_fixes":len(fixes),
            "original_birds_in_region":len(animals),
            "original_source_fixes_with_past_movement_heading":valid_prior,
            "original_source_fixes_with_future_target_heading":valid_next,
            "nearby_raw_different_bird_pairs_5s_100m":pair_count,
            "qualifying_directed_neighbor_prior_to_focal_next_pairs":qualified_directed,
            "unique_qualifying_birds":len(participating),
            "unique_qualifying_undirected_dyads":len(dyads),
            "unique_day_dyad_replicates":len(pairdays),
            "unique_calendar_days":len(days),
            "quality_drops":dict(drops),
            "source_clock":"ORIGINAL_NATIVE_UNVERIFIED_UTC_OR_GPS",
            "tide_joined":False,
            "social_alignment_or_causal_boids":"NOT_ESTIMATED",
            "next_step_only_used_for_eligibility":True}

def run(path):
    summary={"analysis":"v35_2010_2011_original_joint_heading_source_only",
             "years":[]}
    with tempfile.TemporaryDirectory(prefix="v35_source_only_") as td:
        for year in (2010,2011):
            temp=Path(td)/f"{year}.csv.gz"
            manifest=download_and_pin(year,temp)
            a=audit(temp,year)
            summary["years"].append({"original_checksum":manifest,"admission":a})
            temp.unlink(missing_ok=True)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    return summary

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    arg=p.parse_args()
    print(json.dumps(run(arg.output),sort_keys=True))
