"""v59: SOURCE-ONLY actual opposite-tide pair admission at fixed original GPS B.

Only source B positions, measured tide sign/height, own prior A->B motion,
calendar and bird identities are accessed. No next B->C headings are read.
"""
from __future__ import annotations
from bisect import bisect_left,bisect_right
from collections import Counter,defaultdict
from datetime import datetime
from math import acos,cos,degrees,floor,hypot,isfinite,radians
from statistics import median

CELL_M=1000.
HEIGHT_TOL_M=.15
CLOCK_TOL_H=3.
DOY_TOL_DAYS=30
PRIOR_ANGLE_TOL_DEG=45.
PRIOR_LOG_SPEED_TOL=.4
SEPARATION_H_MIN=24.
MIN_PAIRS=60
MIN_PER_BIRD=10
MIN_BIRDS=3
MIN_WEEKS=8
MIN_MONTHS=3
SOURCE_YEAR=2011
R_M=6371000.
REF_LAT,REF_LON=53.,4.
LON_COS=cos(radians(53.5))
STAGES=("same_bird_and_1km_B_cell","plus_measured_water_height",
        "plus_separate_actual_days","plus_same_season","plus_same_clock",
        "plus_similar_prior_heading","plus_similar_prior_speed")

def _state(row):
    # Do NOT access target_e/target_n or any model predictions.
    t=row["t"]
    if not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None or t.year!=SOURCE_YEAR:
        raise ValueError("SOURCE_STOP_INVALID_2011_ORIGINAL_B_TIME")
    if not isinstance(row.get("id"),str) or not row["id"].strip():
        raise ValueError("SOURCE_STOP_INVALID_ORIGINAL_BIRD")
    lat,lon,h,pe,pn,ps=[float(row[k]) for k in
                        ("lat","lon","h","previous_e","previous_n","previous_speed_log")]
    if not all(map(isfinite,(lat,lon,h,pe,pn,ps))) or not (52.<=lat<=54.5 and 3.<=lon<=8.5):
        raise ValueError("SOURCE_STOP_INVALID_ORIGINAL_B_LOCATION_OR_FEATURE")
    mag=hypot(pe,pn)
    if row["phase"] not in (-1,1) or mag<1e-10:
        raise ValueError("SOURCE_STOP_INVALID_ORIGINAL_PHASE_OR_PREVIOUS_VECTOR")
    x=R_M*LON_COS*radians(lon-REF_LON)
    y=R_M*radians(lat-REF_LAT)
    return {"bird":row["id"],"t":t,"phase":int(row["phase"]),
            "cell":(floor(x/CELL_M),floor(y/CELL_M)),"h":h,
            "hour":t.hour+t.minute/60+t.second/3600,
            "doy":t.timetuple().tm_yday,"prev":(pe/mag,pn/mag),"speed":ps}

def _cyclic_clock(a,b):
    d=abs(a-b)%24
    return min(d,24-d)

def _cyclic_doy(a,b):
    d=abs(a-b)
    return min(d,365-d)

def _angle(a,b):
    dot=max(-1.,min(1.,a[0]*b[0]+a[1]*b[1]))
    return degrees(acos(dot))

def _different(a,b):
    return (abs(a["h"]-b["h"]),
            abs((a["t"]-b["t"]).total_seconds())/3600.,
            _cyclic_doy(a["doy"],b["doy"]),
            _cyclic_clock(a["hour"],b["hour"]),
            _angle(a["prev"],b["prev"]),
            abs(a["speed"]-b["speed"]))

def _conditions(d):
    return (d[0]<=HEIGHT_TOL_M,d[1]>=SEPARATION_H_MIN,
            d[2]<=DOY_TOL_DAYS,d[3]<=CLOCK_TOL_H,
            d[4]<=PRIOR_ANGLE_TOL_DEG,d[5]<=PRIOR_LOG_SPEED_TOL)

def audit_source_only(rows):
    if not rows:
        raise ValueError("SOURCE_STOP_EMPTY_ORIGINAL_2011_COHORT")
    states=[_state(r) for r in rows]
    if len({(s["bird"],s["t"]) for s in states})!=len(states):
        raise ValueError("SOURCE_STOP_DUPLICATE_BIRD_B_TIME")
    groups=defaultdict(lambda:{1:[],-1:[]})
    for s in states:
        groups[(s["bird"],s["cell"])][s["phase"]].append(s)
    progress=Counter()
    pairs=[]
    for key in sorted(groups):
        plus=sorted(groups[key][1],key=lambda s:s["t"])
        minus=sorted(groups[key][-1],key=lambda s:(s["h"],s["t"]))
        if not minus:
            continue
        heights=[m["h"] for m in minus]
        used=set()
        for p in plus:
            progress[STAGES[0]]+=1
            left=bisect_left(heights,p["h"]-HEIGHT_TOL_M-1e-12)
            right=bisect_right(heights,p["h"]+HEIGHT_TOL_M+1e-12)
            any_pass=[False]*6
            candidates=[]
            for j in range(left,right):
                m=minus[j]
                d=_different(p,m)
                success=True
                for step,ok in enumerate(_conditions(d)):
                    success=success and ok
                    if success:
                        any_pass[step]=True
                    else:
                        break
                if success and j not in used:
                    score=(d[0]/HEIGHT_TOL_M)**2+(d[2]/DOY_TOL_DAYS)**2
                    score+=(d[3]/CLOCK_TOL_H)**2+(d[4]/PRIOR_ANGLE_TOL_DEG)**2
                    score+=(d[5]/PRIOR_LOG_SPEED_TOL)**2
                    candidates.append((score,m["t"],j))
            for step,ok in enumerate(any_pass):
                if ok:
                    progress[STAGES[step+1]]+=1
            if candidates:
                _,_,j=min(candidates)
                used.add(j)
                pairs.append((p,minus[j]))
    bybird=Counter(p["bird"] for p,_ in pairs)
    weeks={s["t"].isocalendar()[:2] for a,b in pairs for s in (a,b)}
    months={s["t"].month for a,b in pairs for s in (a,b)}
    qualified=sum(n>=MIN_PER_BIRD for n in bybird.values())
    admitted=(len(pairs)>=MIN_PAIRS and qualified>=MIN_BIRDS
              and len(weeks)>=MIN_WEEKS and len(months)>=MIN_MONTHS)
    return {
        "analysis":"V59_ACTUAL_OPPOSITE_TIDE_ORIGINAL_SOURCE_SUPPORT",
        "original_year":SOURCE_YEAR,"source_rows":len(states),
        "source_birds":len({s["bird"] for s in states}),
        "source_phase_counts":{"rising":sum(s["phase"]==1 for s in states),
                               "falling":sum(s["phase"]==-1 for s in states)},
        "fixed_matching":{"same_bird":True,"same_native_1km_B_cell":True,
                          "measured_height_diff_max_m":HEIGHT_TOL_M,
                          "observation_sep_min_hours":SEPARATION_H_MIN,
                          "cyclic_doy_diff_max":DOY_TOL_DAYS,
                          "cyclic_utc_hour_diff_max":CLOCK_TOL_H,
                          "prior_heading_angle_diff_max_degrees":PRIOR_ANGLE_TOL_DEG,
                          "prior_log_speed_diff_max":PRIOR_LOG_SPEED_TOL,
                          "one_to_one_without_replacement":True},
        "rising_rows_with_candidate_after_sequential_gates":{
            k:progress[k] for k in STAGES},
        "unique_disjoint_actual_opposite_tide_pairs":len(pairs),
        "matched_birds":len(bybird),
        "birds_with_at_least_ten_pairs":qualified,
        "matched_distinct_ISO_weeks":len(weeks),
        "matched_distinct_calendar_months":len(months),
        "anonymous_pairs_per_bird_min_median_max":{
            "min":min(bybird.values(),default=0),
            "median":float(median(bybird.values())) if bybird else 0.,
            "max":max(bybird.values(),default=0)},
        "admission":("SOURCE_SUPPORT_ADMITTED_FOR_LATER_PREREGISTERED_OUTCOME"
                     if admitted else "NOT_ADMITTED_INSUFFICIENT_REAL_MATCHED_SOURCE_SUPPORT"),
        "actual_next_heading_effect":"NOT_ESTIMATED",
        "never_read_BC_target_headings_for_matching":True,
        "never_publish_bird_ids_cells_coordinates_or_exact_dates":True,
        "not_independent_field_replication_or_causal_tide_test":True}
