"""v65 original-source tide-slope eligibility for published WATLAS shorebirds.

No B->C bearing, fitted ecological effect, fabricated tide record, interpolated
location, raw bird identifier, precise timestamp or location is exported.
The source waterlevel column is a *published gauge-linked covariate*, not an
independently authenticated RWS original gauge or GPS-local waterline.
"""
from __future__ import annotations

import csv
import io
import json
import math
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

from watlas_cross_taxon_tide_source import (
    ARTICLES, NEEDED, MIN_UNIX, MAX_UNIX, BIN_SECONDS, MIN_GAP, MAX_GAP,
    MIN_SPEED, MAX_SPEED, _float_or_none, original_source, source_only_audit,
    MIN_TRIPLES, MIN_BIRDS, MIN_TIDES, MIN_PER_PHASE, MIN_TIDES_PER_PHASE,
    MIN_HOLDOUT_CYCLES, MIN_HOLDOUT_CYCLE_TRIPLES
)

SOURCE_SHA = {
    "red_knot": "f8ef4f488a1f7f77182da59a0350b761c1b3aaa935fc5f99c3caa7ef4d15afff",
    "sanderling": "d26674dc3a02f3e6f2e68d40658c7243b4a871fdd610593e6f3f7a13851c2c70",
}
EXACT_RAW = {"red_knot": 7595, "sanderling": 6509}
EXACT_V64_MOVING_WITH_TIDE = {"red_knot": 194, "sanderling": 572}
BRACKET_MIN_SECONDS = 10 * 60
BRACKET_MAX_SECONDS = 50 * 60
DESIRED_BRACKET_SECONDS = 30 * 60
SLOPE_THRESHOLD_CM_PER_HOUR = 3.0
MAX_SIMULTANEOUS_GAUGE_SPREAD_CM = 5.0

def quantiles(values):
    """Anonymized finite-source distribution, never individual datapoints."""
    a = sorted(values)
    if not a:
        return {"n": 0, "min": None, "p05": None, "median": None,
                "p95": None, "max": None}
    def q(p):
        f = (len(a) - 1) * p
        k = int(f)
        if k == len(a) - 1:
            return float(a[-1])
        return float(a[k] + (a[k+1] - a[k]) * (f-k))
    return {"n": len(a), "min": float(a[0]), "p05": q(.05),
            "median": q(.5), "p95": q(.95), "max": float(a[-1])}

def _native_valid_bins(raw):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not NEEDED <= set(reader.fieldnames or []):
        raise ValueError("SOURCE_STOP_V65_ORIGINAL_SCHEMA_CHANGED")
    positions = defaultdict(list)
    original_rows = accepted = 0
    drops = Counter()
    original_tags = set()
    for row in reader:
        original_rows += 1
        bird = (row.get("TAG") or "").strip()
        tide = (row.get("tideID") or "").strip()
        vals = {k: _float_or_none(row.get(k)) for k in
                ("TIME", "X", "Y", "NBS", "VARX", "VARY", "COVXY",
                 "tidaltime", "waterlevel")}
        t,x,y,nbs,vx,vy,cov = [vals[k] for k in
                             ("TIME", "X", "Y", "NBS", "VARX", "VARY", "COVXY")]
        if not bird or any(z is None for z in (t,x,y,nbs,vx,vy,cov)):
            drops["missing_id_or_core_source_numeric"] += 1
            continue
        if not MIN_UNIX <= t < MAX_UNIX:
            drops["source_unix_out_of_range"] += 1
            continue
        if not (100000 <= x <= 900000 and 4000000 <= y <= 7000000):
            drops["source_UTM31_out_of_bounds"] += 1
            continue
        if nbs < 3 or not (0 <= vx <= 5000 and 0 <= vy <= 5000):
            drops["localization_error_gate"] += 1
            continue
        original_tags.add(bird)
        accepted += 1
        positions[(bird,int(t//BIN_SECONDS))].append(
            (x,y,tide,vals["tidaltime"],vals["waterlevel"]))
    if not original_rows:
        raise ValueError("SOURCE_STOP_V65_EMPTY_ORIGINAL_CSV")
    track = defaultdict(list)
    tide_data = defaultdict(lambda: defaultdict(list))
    original_bin_clock = []
    complete = 0
    inconsistent = 0
    for (bird,bucket),points in positions.items():
        tides = {p[2] for p in points}
        clocks = [p[3] for p in points]
        water = [p[4] for p in points]
        valid = (len(tides)==1 and "" not in tides
                 and all(x is not None for x in clocks + water)
                 and max(clocks)-min(clocks) <= 2
                 and max(water)-min(water) <= 5)
        if valid:
            tid = next(iter(tides))
            clock = sum(clocks)/len(clocks)
            height = sum(water)/len(water)
            tide_data[tid][bucket*BIN_SECONDS].append(height)
            original_bin_clock.append(clock)
            complete += 1
        else:
            tid = clock = height = None
            inconsistent += 1
        track[bird].append({
            "t": bucket*BIN_SECONDS,
            "x": sum(p[0] for p in points)/len(points),
            "y": sum(p[1] for p in points)/len(points),
            "tid": tid, "clock": clock, "height": height})
    for values in track.values():
        values.sort(key=lambda p:p["t"])
    source = {
        "original_rows":original_rows,
        "original_QC_accepted_rows":accepted,
        "original_QC_drop_reasons":dict(drops),
        "original_tag_count":len(original_tags),
        "tag_30second_location_bins":len(positions),
        "bins_with_consistent_complete_original_tide_metadata":complete,
        "bins_missing_or_inconsistent_tide_metadata":inconsistent,
        "source_tidaltime_signed_minute_distribution":quantiles(original_bin_clock),
        "source_tidaltime_negative_bins":sum(t<0 for t in original_bin_clock),
        "source_tidaltime_zero_bins":sum(t==0 for t in original_bin_clock),
        "source_tidaltime_positive_bins":sum(t>0 for t in original_bin_clock),
    }
    return track,tide_data,source

def _gauge_reference(tide_data):
    """Median original published same-tide gauge value at genuine source times."""
    ret = {}
    time_removed = 0
    for tid,times in tide_data.items():
        good = []
        for t,heights in times.items():
            if max(heights)-min(heights) > MAX_SIMULTANEOUS_GAUGE_SPREAD_CM:
                time_removed += 1
                continue
            good.append((t,median(heights)))
        good.sort()
        ret[tid] = ([t for t,h in good], [h for t,h in good])
    return ret, time_removed

def _nearest_existing_reference(times,lo,hi,ideal):
    """No interpolation: genuine source record closest to 30min, earlier tie."""
    left=bisect_left(times,lo)
    right=bisect_right(times,hi)
    if left >= right:
        return None
    j=bisect_left(times,ideal,left,right)
    cand=[]
    if j < right:
        cand.append(j)
    if j > left:
        cand.append(j-1)
    return min(cand,key=lambda k:(abs(times[k]-ideal),times[k]))

def source_waterlevel_rate(btime,tid,ref):
    """Return signed gauge-linked cm/hour ONLY with two real bracket records."""
    if tid is None or tid not in ref:
        return None
    times,heights=ref[tid]
    pre=_nearest_existing_reference(
        times,btime-BRACKET_MAX_SECONDS,btime-BRACKET_MIN_SECONDS,
        btime-DESIRED_BRACKET_SECONDS)
    post=_nearest_existing_reference(
        times,btime+BRACKET_MIN_SECONDS,btime+BRACKET_MAX_SECONDS,
        btime+DESIRED_BRACKET_SECONDS)
    if pre is None or post is None:
        return None
    dt=(times[post]-times[pre])/3600.
    if dt <= 0:
        raise ValueError("SOURCE_STOP_V65_BROKEN_ORIGINAL_GAUGE_TIMES")
    return (heights[post]-heights[pre])/dt

def _phase(slope):
    if slope is None:
        return "unbracketed"
    if slope >= SLOPE_THRESHOLD_CM_PER_HOUR:
        return "rising"
    if slope <= -SLOPE_THRESHOLD_CM_PER_HOUR:
        return "falling"
    return "slack"

def audit_slope_source_only(raw):
    """Only source presence/magnitude checks. Never read next heading angle."""
    tracks,tide_data,metadata = _native_valid_bins(raw)
    reference,contradictory = _gauge_reference(tide_data)
    phase_counts=Counter()
    phase_birds=defaultdict(set)
    phase_cycles=defaultdict(set)
    eligible_cycles=Counter()
    birds=set()
    all_counts=Counter()
    source_slopes=[]
    for bird,track in tracks.items():
        for a,b,c in zip(track,track[1:],track[2:]):
            da=b["t"]-a["t"]
            db=c["t"]-b["t"]
            if not (MIN_GAP<=da<=MAX_GAP and MIN_GAP<=db<=MAX_GAP):
                continue
            all_counts["original_consecutive_three_fix_time_candidates"] += 1
            if not (a["tid"] and a["tid"]==b["tid"]==c["tid"]):
                continue
            all_counts["same_original_tideID_triples"] += 1
            va=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/da
            vb=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/db
            if not (MIN_SPEED<=va<=MAX_SPEED and MIN_SPEED<=vb<=MAX_SPEED):
                continue
            all_counts["source_speed_magnitudes_valid"] += 1
            if b["height"] is None or b["clock"] is None:
                continue
            all_counts["original_waterlevel_and_tidaltime_present"] += 1
            rate=source_waterlevel_rate(b["t"],b["tid"],reference)
            label=_phase(rate)
            phase_counts[label] += 1
            if rate is not None:
                source_slopes.append(rate)
            if label not in ("rising","falling"):
                continue
            birds.add(bird)
            phase_birds[label].add(bird)
            phase_cycles[label].add(b["tid"])
            eligible_cycles[b["tid"]] += 1
    total_physical=phase_counts["rising"]+phase_counts["falling"]
    cycles_ge20=sum(n>=MIN_HOLDOUT_CYCLE_TRIPLES
                    for n in eligible_cycles.values())
    feasible=(total_physical>=MIN_TRIPLES
              and len(birds)>=MIN_BIRDS
              and len(eligible_cycles)>=MIN_TIDES
              and phase_counts["rising"]>=MIN_PER_PHASE
              and phase_counts["falling"]>=MIN_PER_PHASE
              and len(phase_cycles["rising"])>=MIN_TIDES_PER_PHASE
              and len(phase_cycles["falling"])>=MIN_TIDES_PER_PHASE
              and cycles_ge20>=MIN_HOLDOUT_CYCLES)
    return {
        "analysis":"V65_PUBLISHED_GAUGE_LINKED_WATERLEVEL_SLOPE_SOURCE_ONLY",
        "source":metadata,
        "reference_unique_published_gauge_timestamps":sum(len(t[0]) for t in reference.values()),
        "reference_source_tideID_count":len(reference),
        "reference_simultaneous_report_contradictions_dropped":contradictory,
        "reference_bracket_actual_observed_times_no_interpolation":True,
        "reference_bracket_lag_minutes_each_side":[10,50],
        "reference_ideal_lag_each_side_minutes":30,
        "rate_threshold_cm_per_hour":SLOPE_THRESHOLD_CM_PER_HOUR,
        "gauge_linked_waterlevel_rate_cm_per_hour":quantiles(source_slopes),
        "eligible_moving_stage_counts":{key:all_counts[key] for key in
            ("original_consecutive_three_fix_time_candidates",
             "same_original_tideID_triples","source_speed_magnitudes_valid",
             "original_waterlevel_and_tidaltime_present")},
        "source_phase_classification_counts":{p:phase_counts[p]
            for p in ("rising","falling","slack","unbracketed")},
        "non_slack_bracketed_original_moving_triples":total_physical,
        "original_birds_with_rising_or_falling_triples":len(birds),
        "source_distinct_tideIDs_with_rising_or_falling_triples":len(eligible_cycles),
        "original_birds_in_rising":len(phase_birds["rising"]),
        "original_birds_in_falling":len(phase_birds["falling"]),
        "source_distinct_tideIDs_in_rising":len(phase_cycles["rising"]),
        "source_distinct_tideIDs_in_falling":len(phase_cycles["falling"]),
        "source_tideIDs_with_at_least_20_non_slack_triples":cycles_ge20,
        "frozen_gate_thresholds":{
            "min_non_slack_triples":MIN_TRIPLES,"min_birds":MIN_BIRDS,
            "min_source_tideIDs":MIN_TIDES,"min_per_phase":MIN_PER_PHASE,
            "min_cycles_per_phase":MIN_TIDES_PER_PHASE,
            "min_heldout_cycles_with_at_least_20":MIN_HOLDOUT_CYCLES},
        "admission":("SOURCE_FEASIBLE_FOR_FUTURE_INDEPENDENT_TIDAL_SLOPE_FORECAST"
            if feasible else "NOT_ADMITTED_INSUFFICIENT_ORIGINAL_SLOPE_BRACKETED_MOVEMENT"),
        "no_next_heading_angle_model_or_ecological_effect_scored":True,
        "source_linked_gauge_not_independent_official_RWS_validation":True,
        "no_raw_TAG_ID_original_time_UTM_or_waterlevel_series_exported":True
    }

def run(output,species):
    if species not in ARTICLES:
        raise ValueError("SOURCE_STOP_V65_UNREGISTERED_SPECIES")
    original,manifest=original_source(species)
    if manifest["original_sha256"]!=SOURCE_SHA[species]:
        raise ValueError("SOURCE_STOP_V65_PINNED_ORIGINAL_SHA_DRIFT")
    old=source_only_audit(original)
    if (old["original_raw_rows"]!=EXACT_RAW[species] or
        old["three_fix_candidates_with_original_tide_metadata"]!=
        EXACT_V64_MOVING_WITH_TIDE[species]):
        raise ValueError("SOURCE_STOP_V65_V64_FROZEN_AGGREGATE_DRIFT")
    audit=audit_slope_source_only(original)
    if (audit["source"]["original_rows"]!=old["original_raw_rows"] or
        audit["source"]["original_tag_count"]!=old["original_TAG_count_after_QC"]
        or audit["source"]["tag_30second_location_bins"]!=
           old["original_TAG_30s_location_bins"] or
        audit["eligible_moving_stage_counts"]["original_waterlevel_and_tidaltime_present"]
           !=old["three_fix_candidates_with_original_tide_metadata"]):
        raise ValueError("SOURCE_STOP_V65_V64_STAGE_COUNTS_CHANGED")
    report={
        "analysis":"V65_TWO_SPECIES_ORIGINAL_WATLAS_WATERLEVEL_SLOPE_SOURCE_ONLY",
        "taxon":species,
        "publisher_original_manifest":manifest,
        "v64_frozen_source_receipt":{
            "original_raw_rows":old["original_raw_rows"],
            "original_2011_STYLE_moving_tide_triples":
                old["three_fix_candidates_with_original_tide_metadata"],
            "v64_original_admission":old["admission"]},
        "v65_source_only_slope":audit,
        "no_new_original_heading_prediction_or_social_Boids_effect":True
    }
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    summary={
        "species":species,"source_sha":manifest["original_sha256"],
        "moving_with_waterlevel":audit["eligible_moving_stage_counts"][
            "original_waterlevel_and_tidaltime_present"],
        "rising":audit["source_phase_classification_counts"]["rising"],
        "falling":audit["source_phase_classification_counts"]["falling"],
        "slack":audit["source_phase_classification_counts"]["slack"],
        "no_bracket":audit["source_phase_classification_counts"]["unbracketed"],
        "birds":audit["original_birds_with_rising_or_falling_triples"],
        "cycles":audit["source_distinct_tideIDs_with_rising_or_falling_triples"],
        "cycles_ge20":audit["source_tideIDs_with_at_least_20_non_slack_triples"],
        "admission":audit["admission"]}
    print("V65_ORIGINAL_SLOPE_SOURCE_ONLY "+json.dumps(summary,sort_keys=True),flush=True)
    print("V65_ORIGINAL_SOURCE_AUDIT_COMPLETED",flush=True)
    return report

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--species",choices=tuple(ARTICLES),required=True)
    a=p.parse_args()
    run(a.output,a.species)
