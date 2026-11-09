"""v90 genuine 2018 WATLAS two shorebird taxa true measured tide x sunlight SOURCE.

No bird behavior or movement endpoint scored. Publisher's selected low-tide
Fig9 original radio-tracking sample (5 red knot,5 sanderling) is NOT the
whole 93/35 tagged populations. Independent original official RWS August
2018 true 10-min WATHTE cm NAP station terschelling.west, physically
30-min shifted a priori from earlier v66 source-only tidal propagation
diagnosis, with zero-shift companion. Astronomical sun from UNIX UTC and
genuine original UTM31N converted to WGS84, not human ts CET column.
No original exact locations, tag values/timestamps or RWS rows serialized.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone

import numpy as np
from astral import Observer
from astral.sun import elevation
from pyproj import Transformer

from watlas_original_two_shorebird_source import (
    ORIGINAL_REQUIRED,FIGSHARE_ORIGINAL,original_csv,
    audit_watlas_CSV,_normalized_fields)
from watlas_original_slope_source import SOURCE_SHA,EXACT_RAW
from watlas_official_rws_phase_check import (
    RWS_EXPECTED,RWS_STATION, get_original_official_rws,
    _official_phase_at,_closest_official_time)

TAXA=("Red_knot","Sanderling")
SOURCE_YEAR=2018
MONTH=8
UTC_DAYS=(12,19)
MIN_ORIGINAL_RADIO_RECEIVERS=3
SOLAR_DAY_DEGREES=3.0
RADIO_BIN_SEC=900
WATER_HEIGHT_BIN_CM=25
SOURCE_PRIOR_PHYSICAL_LAG_MIN=-30
SOURCE_COMPANION_LAG_MIN=0
OFFICIAL_NEAREST_GAUGE_SECONDS=300
SOURCE_MIN15MIN_PER_CELL=2
SOURCE_MIN_ORIGINAL_TIDE_CYCLES_PER_TAG_BIN=2
SOURCE_MIN_COMPLETE_TAGS_EACH_SPECIES=3
SOURCE_MIN_COMPLETE_TAG_HEIGHT_BINS_TOTAL=12
SOURCE_MIN_FIXES_FULL_FOURWAY=120
SOURCE_MIN_TIDE_CYCLES_EACH_SPECIES=3
PUBLISHED_FIG9_LOW_TIDE_MAX_CM=50
TRACK_ORIGINAL_FIG9_TOTAL={"Red_knot":7595,"Sanderling":6509}
RECEIVER_UNCERTAINTY_NOT_INDEPENDENT_GAUGE=True

def _original_source_windows(raw,species,*,transformer=None):
    """15-min source, no movement steps or GPS-used habitat model index."""
    if species not in TAXA:
        raise ValueError("SOURCE_STOP_V90_INVALID_ORIGINAL_SPECIES")
    transform=transformer or Transformer.from_crs(
        "EPSG:32631","EPSG:4326",always_xy=True)
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    names=_normalized_fields(reader.fieldnames or [])
    if not set(ORIGINAL_REQUIRED).issubset(names):
        raise ValueError("SOURCE_STOP_V90_WATLAS_ORIGINAL_SCHEMA")
    original=0
    ignored=Counter()
    buckets={}
    tags=set()
    for row in reader:
        original+=1
        try:
            tag=(row[names["tag"]] or "").strip()
            if not tag:raise ValueError("empty original TAG")
            unix=float(row[names["time"]])
            if not math.isfinite(unix):
                raise ValueError("TIME not finite")
            clock=datetime.fromtimestamp(unix,tz=timezone.utc)
            if clock.year!=SOURCE_YEAR or clock.month!=MONTH:
                ignored["outside_2018_Aug"]+=1;continue
            if not UTC_DAYS[0]<=clock.day<=UTC_DAYS[1]:
                ignored["outside_12_to_19_Aug_UTC"]+=1
                continue
            x=float(row[names["x"]]);y=float(row[names["y"]])
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("invalid UTM")
            lon,lat=transform.transform(x,y)
            if not (4<lon<7 and 52<lat<55):
                raise ValueError("invalid transformed original position")
            nbs=int(float(row[names["nbs"]]))
            if nbs<MIN_ORIGINAL_RADIO_RECEIVERS:
                ignored["source_fewer_than_three_receivers"]+=1
                continue
            tid=(row[names["tideid"]] or "").strip()
            if not tid:raise ValueError("missing tideID")
            tidetime=float(row[names["tidaltime"]])
            w=float(row[names["waterlevel"]])
            if (not math.isfinite(w) or not math.isfinite(tidetime)
                or abs(w)>500 or abs(tidetime)>600):
                raise ValueError("invalid original published tidal covariate")
            tags.add(tag)
            key=(tag,int(unix//RADIO_BIN_SEC))
            current=buckets.get(key)
            candidate=(unix,tag,tid,lon,lat,w,tidetime)
            if current is None or unix<current[0]:
                buckets[key]=candidate
        except (ValueError,TypeError,OverflowError) as e:
            ignored["invalid_genuine_radio_source"]+=1
    if original!=TRACK_ORIGINAL_FIG9_TOTAL[species]:
        raise ValueError("SOURCE_STOP_V90_ORIGINAL_V89_2018_CSV_COUNT_DRIFT")
    if len(tags)!=5:
        raise ValueError("SOURCE_STOP_V90_ORIGINAL_V89_FIVE_PUBLISHED_TAGS_DRIFT")
    ordered=sorted(buckets.values(),key=lambda r:(r[0],r[1]))
    clock_solar={}
    for unix,tag,tide,lon,lat,w,tidetime in ordered:
        sec=datetime.fromtimestamp(unix,tz=timezone.utc)
        angle=float(elevation(Observer(latitude=lat,longitude=lon,elevation=0),
                              sec,with_refraction=True))
        clock_solar[(tag,unix)]=(
            "DAY" if angle>SOLAR_DAY_DEGREES else
            "NIGHT" if angle< -SOLAR_DAY_DEGREES else
            "TWILIGHT")
    return ordered,clock_solar,{
        "original_species":species,
        "source_original_genuine_radio_rows":original,
        "source_distinct_original_TAGs":len(tags),
        "source_valid_actual_TAG_15min_windows":len(ordered),
        "source_radio_excluded_reason_counts":dict(ignored),
        "source_original_UTM31N_and_UNIX_UTC_verified":True,
        "source_low_tide_selection_in_published_Fig9_not_full_migratory_year":True,
        "no_animal_movement_or_velocity_scored":True}

def _source_one_gauge_alignment(windows,solar,values,*,shift):
    if shift not in (SOURCE_PRIOR_PHYSICAL_LAG_MIN,SOURCE_COMPANION_LAG_MIN):
        raise ValueError("SOURCE_STOP_V90_UNREGISTERED_GAUGE_PROPAGATION_SHIFT")
    sorted_t=sorted(values)
    raw=Counter()
    groups=defaultdict(lambda:defaultdict(list))
    tad=defaultdict(set)
    alltags=defaultdict(set)
    discrepancy=[]
    for species,source in windows.items():
        for unix,tag,tideid,lon,lat,w,tidetime in source:
            a=solar[species][(tag,unix)]
            if a=="TWILIGHT":
                raw[f"{species}_twilight"]+=1;continue
            sec=round(unix)
            gaugetime=sec+shift*60
            current=_closest_official_time(sorted_t,gaugetime)
            if current is None:
                raw[f"{species}_official_RWS_unbracketed_height"]+=1;continue
            water=values[current]
            phase=_official_phase_at(sec,values,sorted_t,shift)
            if phase not in ("rising","falling"):
                raw[f"{species}_{phase}"]+=1;continue
            name="FLOOD" if phase=="rising" else "EBB"
            raw[f"{species}_{name}_{a}"]+=1
            discrepancy.append(abs(water-w))
            bin_height=math.floor(water/WATER_HEIGHT_BIN_CM)
            key=(species,tag,bin_height)
            cell=(name,a)
            groups[key][cell].append((tideid,unix))
            tad[(species,tag)].add(tideid)
            alltags[species].add(tag)
    complete={}
    groups_all=Counter()
    complete_cycle=defaultdict(set)
    selected_source_15min=Counter()
    for key,dat in groups.items():
        species,tag,bin_height=key
        groups_all[species]+=1
        if not all(len(dat.get(cell,()))>=SOURCE_MIN15MIN_PER_CELL
                   for cell in (("FLOOD","DAY"),("FLOOD","NIGHT"),
                                ("EBB","DAY"),("EBB","NIGHT"))):
            continue
        source_cycles={r[0] for locs in dat.values() for r in locs}
        if len(source_cycles)<SOURCE_MIN_ORIGINAL_TIDE_CYCLES_PER_TAG_BIN:
            continue
        # The source is original bin/window only; do not read movements.
        complete[key]=dat
        complete_cycle[species].update(source_cycles)
        selected_source_15min[species]+=sum(len(v) for v in dat.values())
    species_eligible={
        k:len({tag for taxon,tag,height in complete if taxon==k})
        for k in TAXA}
    original_matched_bins=len(complete)
    admission=(
        all(species_eligible[s]>=SOURCE_MIN_COMPLETE_TAGS_EACH_SPECIES for s in TAXA)
        and original_matched_bins>=SOURCE_MIN_COMPLETE_TAG_HEIGHT_BINS_TOTAL
        and sum(selected_source_15min.values())>=SOURCE_MIN_FIXES_FULL_FOURWAY
        and all(len(complete_cycle[s])>=SOURCE_MIN_TIDE_CYCLES_EACH_SPECIES
                for s in TAXA))
    distribution={
        "official_gauge_shift_minutes":shift,
        "source_original_tag15min_windows_with_real_phase_and_astronomical_light_by_taxon":
            {t:{v:raw[f"{t}_{v}"] for v in
                ("FLOOD_DAY","FLOOD_NIGHT","EBB_DAY","EBB_NIGHT")}
             for t in TAXA},
        "all_actual_tag_height_bin_candidates_by_species":dict(groups_all),
        "original_complete_same_TAG_measured_25cm_all4_tide_solar_bins":
            original_matched_bins,
        "source_complete_mapped_TAGs_by_species":species_eligible,
        "source_TRUE_measured_RWS_height25cm_complete_4cell_tag_windows_by_species":
            dict(selected_source_15min),
        "source_distinct_original_tide_cycles_eligible_bins_by_species":
            {s:len(complete_cycle[s]) for s in TAXA},
        "source_valid_day_night_gauge_and_quality_drops":dict(raw),
        "published_2018_WATLAS_waterlevel_minus_true_official_gauge_abs_cm":
            ([float(v) for v in np.quantile(discrepancy,[.5,.95])]
             if discrepancy else None),
        "orig_sample_low_tide_only_selection_and_5TAG_taxon_bias":True,
        "SOURCE_ADMISSION":(
            "SOURCE_ADMITTED_V90_PILOT_TWO_TAXA_TRUE_RWS_TIDE_SOLAR_MATCHED_HEIGHT"
            if admission else
            "NOT_ADMITTED_V90_PILOT_WATLAS_TWO_TAXA_TRUE_RWS_TIDE_SOLAR_MATCHED_HEIGHT")}
    return distribution

def run(output):
    actual={}
    source={}
    solar={}
    provenance={}
    for k in TAXA:
        spec=FIGSHARE_ORIGINAL[k]
        content,receipt=original_csv(spec)
        import hashlib
        check=hashlib.sha256(content).hexdigest()
        idkey="red_knot" if k=="Red_knot" else "sanderling"
        if check!=SOURCE_SHA[idkey]:
            raise ValueError("SOURCE_STOP_V90_OLD_V65_ORIGINAL_CSV_SHA_DRIFT")
        old=audit_watlas_CSV(content,k)
        if (old["original_source_valid_genuine_WATLAS_localizations"]!=
            EXACT_RAW[idkey] or
            old["original_SOURCE_TAG_count_not_necessarily_independent_recaptures"]!=5):
            raise ValueError("SOURCE_STOP_V90_OLD_V89_ORIGINAL_TAG_SOURCE_DRIFT")
        windows,solar[k],receipt2=_original_source_windows(content,k)
        actual[k]=windows
        source[k]=receipt2
        provenance[k]={
            "original_source_DOI":spec["doi"],
            "original_CSV_original_bytes":len(content),
            "original_source_SHA256":check,
            "original_source_public_publisher_authentication":receipt,
            "original_v89_wild_TAG_and_UTC_source_replayed":True}
        print("V90_ORIGINAL_WATLAS_TWO_TAXA_UTC_RADIO_15MIN_SOURCE_FIRST "+
              json.dumps({"species":k,
                "original_source_radio_rows":receipt2["source_original_genuine_radio_rows"],
                "original_SOURCE_TAGs":receipt2["source_distinct_original_TAGs"],
                "original_TAG_15min_windows":len(windows),
                "no_animal_behavior_read":True},sort_keys=True),flush=True)
    official=get_original_official_rws()
    if official["source_manifest"]["official_10minute_distinct_samples"]!=RWS_EXPECTED:
        raise ValueError("SOURCE_STOP_V90_RWS_OFFICIAL_2018_MEASURED_GAUGE_INCOMPLETE")
    values=official["original_UTC_second_to_cm_NAP"]
    primary=_source_one_gauge_alignment(actual,solar,values,
                                        shift=SOURCE_PRIOR_PHYSICAL_LAG_MIN)
    zero=_source_one_gauge_alignment(actual,solar,values,
                                     shift=SOURCE_COMPANION_LAG_MIN)
    result={
        "analysis":"V90_AUTHENTIC_TWO_TAXA_2018_WATLAS_LOW_TIDE_OFFICIAL_WEST_TERSCHELLING_TIDE_BY_SUN_15MIN_SOURCE_ONLY",
        "frozen_protocol":"docs/V90_FROZEN_WATLAS_TWO_SPECIES_OFFICIAL_RWS_DAYLIGHT_MATCHED_SOURCE.md",
        "original_source_authentication_and_tag_coverage":provenance,
        "original_SOURCE_15min_UTC_windows_QA_by_species":source,
        "original_official_RWS_genuine_WATHTE_observations_manifest":official["source_manifest"],
        "source_primary_minus30min_real_gauge_height25cm_fourway":primary,
        "source_companion_0min_real_gauge_height25cm_fourway":zero,
        "source_result_is_matched_physical_and_UTC_OPPORTUNITY_only":True,
        "source_original_Fig9_LOW_TIDE_CHOSEN_5TAG_per_species_NOT_FULL_93_35":True,
        "no_new_WATLAS_bird_displacement_heading_foraging_or_habitat_effect_calculated":True,
        "no_original_TAG_ID_UTC_time_gps_utm_geography_or_real_RWS_full_series_exported":True,
        "not_new_sea_basin_or_independent_bird_population_genetic_replication":True}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V90_REAL_OFFICIAL_RWS_2018_WATLAS_TWO_SPECIES_TIDE_SOLAR_SOURCE_RESULT "+
          json.dumps({
            "RWS_measured_original_10min_count":RWS_EXPECTED,
            "source_minus30min_true_gauge_match_status":primary["SOURCE_ADMISSION"],
            "original_genuine_TAGs_complete_by_species":
                primary["source_complete_mapped_TAGs_by_species"],
            "source_matched_height25cm_TAG_4way_groups":
                primary["original_complete_same_TAG_measured_25cm_all4_tide_solar_bins"],
            "source_companion_zero_shift_status":zero["SOURCE_ADMISSION"],
            "no_animal_behavior_scored":True},sort_keys=True),flush=True)
    print("V90_WATLAS_TRUE_GAUGE_PHASE_BY_SOLAR_SOURCE_ONLY_FINISHED",flush=True)
    return result

if __name__=="__main__":
    args=argparse.ArgumentParser();args.add_argument("--output",required=True)
    opts=args.parse_args();run(opts.output)
