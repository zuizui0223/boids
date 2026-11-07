"""v64: ORIGINAL source-only WATLAS red-knot and sanderling tide-heading opportunity.

No next-heading angle, tide-dependent regression, social effect or behavioural
prediction is calculated. Only source row counts and 3-fix *speed magnitude*
eligibility are measured. Never publish individual TAG / original TIME / XY.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ARTICLES={
    "red_knot":(26553446,"10.6084/m9.figshare.26553446.v1"),
    "sanderling":(26553443,"10.6084/m9.figshare.26553443.v1")}
NEEDED={"TAG","TIME","X","Y","NBS","VARX","VARY","COVXY",
        "tideID","tidaltime","waterlevel"}
CAP=150_000_000
MIN_UNIX=1483228800 # 2017-01-01 UTC
MAX_UNIX=1704067200 # 2024-01-01 UTC, exclusive
MIN_SPEED=.2
MAX_SPEED=30.
MIN_GAP=30
MAX_GAP=180
BIN_SECONDS=30
MIN_TRIPLES=120
MIN_BIRDS=3
MIN_TIDES=4
MIN_PER_PHASE=30
MIN_TIDES_PER_PHASE=2
MIN_HOLDOUT_CYCLES=2
MIN_HOLDOUT_CYCLE_TRIPLES=20
KNOWN_RED_KNOT_RAW=7595
KNOWN_RED_KNOT_SHA256="f8ef4f488a1f7f77182da59a0350b761c1b3aaa935fc5f99c3caa7ef4d15afff"

def _get_bytes(url,max_bytes):
    req=Request(url,headers={"User-Agent":"boids-v64-reproducible-source-audit/1.0"})
    with urlopen(req,timeout=45) as response:
        size=response.headers.get("content-length")
        if size is not None and int(size)>max_bytes:
            raise ValueError("SOURCE_STOP_V64_PUBLIC_ORIGINAL_TOO_LARGE")
        raw=response.read(max_bytes+1)
    if len(raw)>max_bytes:
        raise ValueError("SOURCE_STOP_V64_BYTES_OVER_MAXIMUM")
    return raw

def original_source(species):
    if species not in ARTICLES:
        raise ValueError("SOURCE_STOP_V64_UNREGISTERED_SPECIES")
    article_id,doi=ARTICLES[species]
    meta=json.loads(_get_bytes(f"https://api.figshare.com/v2/articles/{article_id}",2_000_000))
    if meta.get("id")!=article_id:
        raise ValueError("SOURCE_STOP_V64_WRONG_FIGSHARE_ARTICLE")
    csv_files=[f for f in meta.get("files",[]) if
               str(f.get("name","")).lower().endswith(".csv")
               and not f.get("is_link_only")]
    if len(csv_files)!=1:
        raise ValueError("SOURCE_STOP_V64_EXPECT_ONE_ORIGINAL_CSV")
    record=csv_files[0]
    md5_expected=record.get("computed_md5") or record.get("supplied_md5")
    if not md5_expected:
        raise ValueError("SOURCE_STOP_V64_PROVIDER_MD5_MISSING")
    raw=_get_bytes(record["download_url"],CAP)
    calculated_md5=hashlib.md5(raw).hexdigest()
    if calculated_md5.lower()!=str(md5_expected).lower():
        raise ValueError("SOURCE_STOP_V64_PROVIDER_ORIGINAL_MD5_MISMATCH")
    if len(raw)!=int(record["size"]):
        raise ValueError("SOURCE_STOP_V64_ORIGINAL_BYTE_LENGTH_CHANGED")
    sha=hashlib.sha256(raw).hexdigest()
    if species=="red_knot" and sha!=KNOWN_RED_KNOT_SHA256:
        raise ValueError("SOURCE_STOP_V64_V38_AUTHENTIC_RED_KNOT_SHA_CHANGED")
    return raw,{
        "species":species,"published_doi":"https://doi.org/"+doi,
        "figshare_article_id":article_id,"original_provider_filename":record["name"],
        "verified_source_bytes":len(raw),
        "provider_original_md5_verified":True,"original_sha256":sha}

def _float_or_none(value):
    try:
        v=float(value)
        return v if math.isfinite(v) else None
    except (ValueError,TypeError):
        return None

def _source_phase_proxy(relative_high_tide_minutes):
    """Signed time relative to HIGH, not original waterlevel physical derivative."""
    x=relative_high_tide_minutes
    if x is None:return None
    if -300<=x<=-30:return "before_high"
    if 30<=x<=300:return "after_high"
    return None

def source_only_audit(raw):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not NEEDED<=set(reader.fieldnames or []):
        raise ValueError("SOURCE_STOP_V64_ORIGINAL_SCHEMA_CHANGED")
    raw_rows=0;valid_rows=0;drops=Counter()
    duplicates=0
    seen=set()
    bins=defaultdict(list)
    all_tags=set()
    all_tides=set()
    for row in reader:
        raw_rows+=1
        bird=(row.get("TAG") or "").strip()
        tide=(row.get("tideID") or "").strip()
        vals={k:_float_or_none(row.get(k)) for k in
              ("TIME","X","Y","NBS","VARX","VARY","COVXY","tidaltime","waterlevel")}
        t,x,y,nbs,vx,vy,cov=(vals[k] for k in
                            ("TIME","X","Y","NBS","VARX","VARY","COVXY"))
        if (not bird or any(z is None for z in (t,x,y,nbs,vx,vy,cov))):
            drops["missing_bird_or_core_numeric"]+=1
            continue
        if not (MIN_UNIX<=t<MAX_UNIX):
            drops["timestamp_outside_source_years"]+=1
            continue
        if not (100000<=x<=900000 and 4000000<=y<=7000000):
            drops["invalid_original_utm31"]+=1
            continue
        if nbs<3 or not (0<=vx<=5000 and 0<=vy<=5000):
            drops["original_localisation_error_gate"]+=1
            continue
        if (bird,t) in seen:
            duplicates+=1
        seen.add((bird,t))
        all_tags.add(bird)
        if tide:all_tides.add(tide)
        valid_rows+=1
        bins[(bird,int(t//BIN_SECONDS))].append(
            (x,y,tide,vals["tidaltime"],vals["waterlevel"]))
    if raw_rows<=0:
        raise ValueError("SOURCE_STOP_V64_EMPTY_ORIGINAL_CSV")
    bybird=defaultdict(list)
    missing_bin_tide=0
    for (bird,k),obs in bins.items():
        raw_tides={z[2] for z in obs}
        signed=[z[3] for z in obs]
        water=[z[4] for z in obs]
        tide=(next(iter(raw_tides)) if len(raw_tides)==1 and "" not in raw_tides else None)
        if (tide is None or any(z is None for z in signed+water)
                or max(signed)-min(signed)>2
                or max(water)-min(water)>5):
            tide=None
            ttime=None
            w=None
            missing_bin_tide+=1
        else:
            ttime=sum(signed)/len(signed)
            w=sum(water)/len(water)
        bybird[bird].append({
            "t":k*BIN_SECONDS,"x":sum(z[0] for z in obs)/len(obs),
            "y":sum(z[1] for z in obs)/len(obs),"tid":tide,
            "clock_from_high":ttime,"waterlevel":w})
    raw_triplets=0;same_tide=0;speed_eligible=0
    with_tide_cov=0
    full=[]
    phase_counts=Counter()
    phase_tags=defaultdict(set)
    phase_tides=defaultdict(set)
    cycle_n=Counter()
    selected_tags=set()
    for bird,trace in bybird.items():
        trace.sort(key=lambda z:z["t"])
        for a,b,c in zip(trace,trace[1:],trace[2:]):
            da=b["t"]-a["t"]
            db=c["t"]-b["t"]
            if not (MIN_GAP<=da<=MAX_GAP and MIN_GAP<=db<=MAX_GAP):
                continue
            raw_triplets+=1
            if not (a["tid"] and a["tid"]==b["tid"]==c["tid"]):
                continue
            same_tide+=1
            va=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/da
            vb=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/db
            if not (MIN_SPEED<=va<=MAX_SPEED and MIN_SPEED<=vb<=MAX_SPEED):
                continue
            speed_eligible+=1
            if b["clock_from_high"] is None or b["waterlevel"] is None:
                continue
            with_tide_cov+=1
            phase=_source_phase_proxy(b["clock_from_high"])
            if phase is None:
                continue
            selected_tags.add(bird)
            cycle_n[b["tid"]]+=1
            phase_counts[phase]+=1
            phase_tags[phase].add(bird)
            phase_tides[phase].add(b["tid"])
    n=sum(phase_counts.values())
    heldout=sum(v>=MIN_HOLDOUT_CYCLE_TRIPLES for v in cycle_n.values())
    eligible=(n>=MIN_TRIPLES and len(selected_tags)>=MIN_BIRDS
              and len(cycle_n)>=MIN_TIDES
              and phase_counts["before_high"]>=MIN_PER_PHASE
              and phase_counts["after_high"]>=MIN_PER_PHASE
              and all(len(phase_tides[sign])>=MIN_TIDES_PER_PHASE
                      for sign in ("before_high","after_high"))
              and heldout>=MIN_HOLDOUT_CYCLES)
    return {
        "analysis":"V64_WATLAS_PER_INDIVIDUAL_MULTITIDE_MOVEMENT_SOURCE_ONLY",
        "original_raw_rows":raw_rows,
        "QC_accepted_original_rows":valid_rows,
        "original_TAG_count_after_QC":len(all_tags),
        "original_tideID_count_after_QC":len(all_tides),
        "duplicate_original_TAG_TIME_instances":duplicates,
        "original_source_dropped_rows":dict(drops),
        "original_TAG_30s_location_bins":len(bins),
        "bins_without_consistent_complete_tide_covariates":missing_bin_tide,
        "distinct_TAGs_with_binned_positions":len(bybird),
        "observed_three_fix_candidates_with_both_gaps_30_to_180_s":raw_triplets,
        "three_fix_candidates_same_original_tideID":same_tide,
        "three_fix_candidates_with_both_speed_magnitudes_0p2_to_30_mps":speed_eligible,
        "three_fix_candidates_with_original_tide_metadata":with_tide_cov,
        "source_triplets_with_signed_high_tide_side_proxy":n,
        "proxy_before_high_triplets":phase_counts["before_high"],
        "proxy_after_high_triplets":phase_counts["after_high"],
        "source_TAGs_with_signed_proxy_triples":len(selected_tags),
        "source_tideIDs_with_signed_proxy_triples":len(cycle_n),
        "before_high_distinct_TAGs":len(phase_tags["before_high"]),
        "after_high_distinct_TAGs":len(phase_tags["after_high"]),
        "before_high_distinct_tideIDs":len(phase_tides["before_high"]),
        "after_high_distinct_tideIDs":len(phase_tides["after_high"]),
        "tideIDs_with_at_least_20_eligible_source_triples":heldout,
        "support_thresholds":{
            "min_triplets":MIN_TRIPLES,"min_tags":MIN_BIRDS,
            "min_tideIDs":MIN_TIDES,"min_each_signed_phase":MIN_PER_PHASE,
            "min_distinct_tideIDs_per_phase":MIN_TIDES_PER_PHASE,
            "min_cycles_with_at_least_20_triplets":MIN_HOLDOUT_CYCLES},
        "admission":("SOURCE_FEASIBLE_FOR_SEPARATE_PREREGISTERED_TIDAL_FORECAST"
                     if eligible else
                     "NOT_ADMITTED_INSUFFICIENT_ORIGINAL_INDIVIDUAL_TIDAL_TRAJECTORIES"),
        "no_observed_next_heading_effect_or_tide_model_estimated":True,
        "signed_time_from_high_is_not_verified_physical_water_slope":True,
        "published_west_terschelling_waterlevel_not_local_front_exposure":True,
        "neighbour_social_Boids_force_not_estimated":True}
    
def run(output):
    out={"analysis":"V64_TWO_WATLAS_SHOREBIRD_SPECIES_SOURCE_ONLY",
         "primary":"red_knot","companion":"sanderling",
         "no_field_prediction_or_effect_scored":True,
         "species":{}}
    for species in ("red_knot","sanderling"):
        raw,provenance=original_source(species)
        qa=source_only_audit(raw)
        if species=="red_knot" and qa["original_raw_rows"]!=KNOWN_RED_KNOT_RAW:
            raise ValueError("SOURCE_STOP_V64_RED_KNOT_V38_RAW_RECEIPT_CHANGED")
        out["species"][species]={"publisher_source":provenance,
                                 "source_only_tide_heading_opportunity":qa}
        print("V64_ORIGINAL_SOURCE_ONLY "+json.dumps({
            "species":species,"source_sha256":provenance["original_sha256"],
            "original_source_rows":qa["original_raw_rows"],
            "original_TAGs":qa["original_TAG_count_after_QC"],
            "original_tides":qa["original_tideID_count_after_QC"],
            "three_fix_temporal_candidates":qa["observed_three_fix_candidates_with_both_gaps_30_to_180_s"],
            "same_tide_three_fix_candidates":qa["three_fix_candidates_same_original_tideID"],
            "moving_and_tide_metadata_candidates":qa["three_fix_candidates_with_original_tide_metadata"],
            "phase_proxy_opportunities":qa["source_triplets_with_signed_high_tide_side_proxy"],
            "before_high":qa["proxy_before_high_triplets"],
            "after_high":qa["proxy_after_high_triplets"],
            "tides_with_20_triples":qa["tideIDs_with_at_least_20_eligible_source_triples"],
            "admission":qa["admission"]},sort_keys=True),flush=True)
    target=Path(output)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("V64_ORIGINAL_SOURCE_AUDIT_COMPLETED",flush=True)
    return out

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    run(a.output)
