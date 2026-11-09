"""v87 genuine 2011 NEW original birds vs authenticated 2010 old IDs source ONLY.

Do NOT open WMR habitat Y, RWS tide, astronomy, animal movement or NIOZ
index. Original four provider MD5-verified Zenodo gzip annual sources:
Schier 2010/11 and Ameland 2010/11, earliest native true bird×hour
within fixed published site geographic bounds, source months Jan–Dec.
Outputs anonymous source totals, never actual source bird IDs, GPS exact
timestamps/latlon or social/feeding/location outcomes.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import os
import tempfile
from collections import Counter,defaultdict
from pathlib import Path

from source_preflight import (
    download_and_pin, parse_stamp,
    GPS_MD5 as SCHIER_PROVIDER_MD5)
from ameland_external_site import (
    original_gps, GPS_MD5 as AMELAND_PROVIDER_MD5,
    BBOX as AMELAND_BBOX)
from two_island_common_month_bird_contrast import (
    SCHIER_SOURCE,AMELAND_SOURCE)

YEARS=(2010,2011)
SITES=("Schier","Ameland")
SCHIER_BBOX=(53.2,53.7,5.7,6.6)
SITE_BBOX={"Schier":SCHIER_BBOX,"Ameland":AMELAND_BBOX}
ORIGINAL_2010_SOURCE_SHA={
    "Schier":"8d7d0ac9cef0935e7351bcf9a525c0f9eeb7605dc603d227f9b09744dadd532d",
    "Ameland":"c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c"}
KNOWN_ORIGINAL_RAW_2010={"Schier":282920,"Ameland":119507}
TARGET_MONTHS=(6,7,8,9,10,11,12)
MIN_NOVEL_BIRDS_IN_FIXED_YEAR_PERIOD=8
MIN_MONTHS_WITH_NOVEL_SOURCE=3
MIN_NOVEL_BIRDS_PER_MONTH=5
MIN_SOURCE_FIXES_EACH_MONTH=200
MIN_SOURCE_FIXES_PER_BIRD_PER_MONTH=20
MIN_SOURCE_FIXES_PER_NEW_BIRD_PERIOD=20
MIN_TOTAL_2011_ONLY_GPS_HOURS_IN_FIXED_PERIOD=2000

def original_year_source(path,site,year,*,expected_raw=None):
    if site not in SITES or year not in YEARS:
        raise ValueError("SOURCE_STOP_V87_ORIGINAL_YEAR_OR_SITE_NOT_FROZEN")
    needed={"event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible"}
    seen=set()
    latest=defaultdict(dict)
    invalid=Counter()
    n=0
    bbox=SITE_BBOX[site]
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        if not needed.issubset(reader.fieldnames or ()):
            raise ValueError("SOURCE_STOP_V87_ORIGINAL_WILD_ZENODO_GPS_FIELDS_CHANGED")
        for r in reader:
            n+=1
            ev=(r.get("event-id") or "").strip()
            if not ev or ev in seen:
                invalid["event_ID_missing_or_duplicate"]+=1
                continue
            seen.add(ev)
            if (r.get("visible") or "").strip().upper() in ("FALSE","0"):
                invalid["original_undisclosed_sensor_event"]+=1
                continue
            bird=(r.get("individual-local-identifier") or "").strip()
            if not bird:
                invalid["source_no_original_animal_identifier"]+=1
                continue
            try:
                t=parse_stamp(r["timestamp"])
                lat=float(r["location-lat"])
                lon=float(r["location-long"])
            except (TypeError,ValueError):
                invalid["source_bad_original_clock_or_geo"]+=1
                continue
            if (t.year!=year or not math.isfinite(lat) or
                not math.isfinite(lon) or not
                (bbox[0]<=lat<=bbox[1] and bbox[2]<=lon<=bbox[3])):
                invalid["original_annual_or_site_geographic_source_excluded"]+=1
                continue
            hr=t.replace(minute=0,second=0,microsecond=0)
            prev=latest[bird].get(hr)
            if prev is None or t<prev:
                latest[bird][hr]=t
    if expected_raw is not None and n!=expected_raw:
        raise ValueError("SOURCE_STOP_V87_2010_ORIGINAL_RAW_ROWS_DRIFT")
    month=defaultdict(Counter)
    for bird,fixes in latest.items():
        for t in fixes.values():
            month[t.month][bird]+=1
    # The internal raw bird ID dictionaries remain ONLY in process memory.
    summary={}
    for m in range(1,13):
        summary[f"{m:02d}"]={
            "original_hourly_GPS_positions":sum(month[m].values()),
            "actual_original_distinct_bird_IDs":len(month[m]),
            "original_birds_with_ge20_native_hourly_fixes":
                sum(v>=MIN_SOURCE_FIXES_PER_BIRD_PER_MONTH for v in month[m].values())}
    if year==2010:
        known=SCHIER_SOURCE if site=="Schier" else AMELAND_SOURCE
        for m in TARGET_MONTHS:
            actual=(summary[f"{m:02d}"]["original_hourly_GPS_positions"],
                    summary[f"{m:02d}"]["actual_original_distinct_bird_IDs"])
            if actual!=known[m]:
                raise ValueError("SOURCE_STOP_V87_2010_ORIGINAL_V82_MONTH_COUNT_DRIFT")
    qa={
        "original_site":site,"original_published_year":year,
        "original_raw_full_gps_year_records":n,
        "original_source_site_area_hourly_unique_positions":
            sum(x["original_hourly_GPS_positions"] for x in summary.values()),
        "original_distinct_bird_IDs_whole_nominal_year":len(latest),
        "original_all_twelve_calendar_month_source":summary,
        "original_source_filter_reasons":dict(invalid),
        "original_GPS_source_clock_UTC_vs_GPS_NOT_HARDWARE_VERIFIED":True,
        "private_individual_IDs_and_native_times_NOT_exported":True}
    return month,set(latest),qa

def independent_2011_source(year2010,ids2010,year2011,ids2011,*,site):
    if site not in SITES:
        raise ValueError("SOURCE_STOP_V87_ORIGINAL_WILD_SITE")
    new=ids2011-ids2010
    older=ids2010&ids2011
    source_by_month={}
    period=Counter()
    for m in range(1,13):
        observed=year2011[m]
        native_new={b:c for b,c in observed.items() if b in new}
        for b,c in native_new.items():
            if m in TARGET_MONTHS:period[b]+=c
        source_by_month[f"{m:02d}"]={
            "original_2011_new_only_IDs_with_hourly_GPS_this_month":
                len(native_new),
            "original_2011_new_only_birds_with_ge20_hourly_fixes_this_month":
                sum(x>=MIN_SOURCE_FIXES_PER_BIRD_PER_MONTH for x in native_new.values()),
            "original_2011_new_only_GPS_hourly_positions_this_month":
                sum(native_new.values()),
            "source_year_2011_only_vs_actual_2010_original_bird_ID_membership":True}
    eligible_new={b for b,count in period.items()
                  if count>=MIN_SOURCE_FIXES_PER_NEW_BIRD_PERIOD}
    source_months=[]
    for m in TARGET_MONTHS:
        native={b:c for b,c in year2011[m].items() if b in eligible_new}
        eligible_month_birds=sum(c>=MIN_SOURCE_FIXES_PER_BIRD_PER_MONTH for c in native.values())
        count=sum(c for b,c in native.items() if c>=MIN_SOURCE_FIXES_PER_BIRD_PER_MONTH)
        if (eligible_month_birds>=MIN_NOVEL_BIRDS_PER_MONTH and
            count>=MIN_SOURCE_FIXES_EACH_MONTH):
            source_months.append(m)
    n_target=sum(source_by_month[f"{m:02d}"][
        "original_2011_new_only_GPS_hourly_positions_this_month"] for m in TARGET_MONTHS)
    prospective=(len(eligible_new)>=MIN_NOVEL_BIRDS_IN_FIXED_YEAR_PERIOD
           and len(source_months)>=MIN_MONTHS_WITH_NOVEL_SOURCE
           and n_target>=MIN_TOTAL_2011_ONLY_GPS_HOURS_IN_FIXED_PERIOD)
    return {
        "original_source_site":site,
        "original_distinct_2010_source_birds":len(ids2010),
        "original_distinct_2011_source_birds":len(ids2011),
        "original_same_literal_bird_IDs_in_both_years":len(older),
        "original_2011_only_distinct_IDs_not_in_2010_original_source":len(new),
        "original_2011_new_only_birds_ge20_original_GPS_in_JunDec":len(eligible_new),
        "original_2011_JunDec_new_only_GPS_positions":n_target,
        "original_2011_JunDec_months_with_ge5_novel_birds_and_ge200_GPS":source_months,
        "all_original_2011_month_new_only_bird_and_GPS_source":source_by_month,
        "frozen_source_prospect":{
            "original_2011_only_birds_need_at_least":MIN_NOVEL_BIRDS_IN_FIXED_YEAR_PERIOD,
            "distinct_2011_JunDec_months_5new_bird_support_min":MIN_MONTHS_WITH_NOVEL_SOURCE,
            "original_2011_only_GPS_hours_min":MIN_TOTAL_2011_ONLY_GPS_HOURS_IN_FIXED_PERIOD,
            "2011_true_physical_RWS_tidal_solar_fourway_NOT_TESTED":True,
            "source_status":(
               "CANDIDATE_2011_NEW_ORIGINAL_BIRDS_FOR_LATER_OUT_OF_YEAR_TIDE_SOLAR_TEST"
               if prospective else
               "NOT_ADMITTED_V87_2011_NEW_BIRD_SOURCE_OR_CALENDAR_SUPPORT")},
        "same_species_same_Wadden_not_independent_taxon_or_ocean":True,
        "original_bird_IDs_exact_times_and_site_GPS_location_NOT_EXPORT":True}

def run(output):
    sources={}
    prospects={}
    for site in SITES:
        bags={}
        monthly={}
        ids={}
        for year in YEARS:
            with tempfile.TemporaryDirectory(prefix=f"v87_{site}_{year}_") as d:
                p=Path(d)/"original_year.csv.gz"
                origin=(download_and_pin(year,p) if site=="Schier"
                        else original_gps(year,p))
                if (site=="Schier" and not origin["provider_md5_match"]
                    or site=="Ameland" and not origin["provider_original_md5_matched"]):
                    raise ValueError("SOURCE_STOP_V87_ZENODO_PUBLISHER_MD5_MISMATCH")
                if year==2010 and origin["original_sha256"]!=ORIGINAL_2010_SOURCE_SHA[site]:
                    raise ValueError("SOURCE_STOP_V87_KNOWN_2010_SHA_CHANGED")
                monthly[year],ids[year],qa=original_year_source(
                    p,site,year,expected_raw=KNOWN_ORIGINAL_RAW_2010[site]
                    if year==2010 else None)
                qa["source_original_provider_MD5_verified"]=True
                qa["original_source_file_SHA256"]=origin["original_sha256"]
                qa["original_source_compressed_bytes"]=origin["original_bytes"]
                bags[str(year)]=qa
        sources[site]=bags
        prospects[site]=independent_2011_source(
            monthly[2010],ids[2010],monthly[2011],ids[2011],site=site)
        print("V87_GENUINE_ZENODO_WILD_2011_NEW_ID_ONLY_YEAR_SOURCE "+
            json.dumps({
                "site":site,
                "original_2011_raw_GPS_records":bags["2011"][
                    "original_raw_full_gps_year_records"],
                "original_2010_birds":prospects[site][
                    "original_distinct_2010_source_birds"],
                "original_2011_birds":prospects[site][
                    "original_distinct_2011_source_birds"],
                "source_genuinely_new_2011_only_literal_IDs":prospects[site][
                    "original_2011_only_distinct_IDs_not_in_2010_original_source"],
                "2011_only_historical_GPS_original_JunDec":prospects[site][
                    "original_2011_JunDec_new_only_GPS_positions"],
                "source_2011_prospective_status":prospects[site][
                    "frozen_source_prospect"]["source_status"],
                "source_year_2011_months":bags["2011"][
                    "original_all_twelve_calendar_month_source"]},
                sort_keys=True),flush=True)
    out={
        "analysis":"V87_AUTHENTIC_2011_ORIGINAL_SCHIER_AMELAND_UNSEEN_YEAR_BIRD_ID_SOURCE_ONLY",
        "executed_commit":os.environ.get("GITHUB_SHA","local"),
        "frozen_source_protocol":"docs/V87_FROZEN_REAL_2011_GPS_NEW_INDIVIDUALS_YEAR_SOURCE_ONLY.md",
        "original_2010_2011_all_four_Zenodo_publisher_MD5_and_SHA_source":sources,
        "real_2011_not_recorded_in_2010_literal_bird_ID_source_support":prospects,
        "new_2011_original_both_islands_new_ID_bird_source_prospect_met":
            all(x["frozen_source_prospect"]["source_status"].startswith(
                "CANDIDATE") for x in prospects.values()),
        "original_public_WMR_2021_corrected_v2_version_UNVERIFIED":True,
        "2011_original_NIOZ_source_lat_NOT_CLAIMED_OR_READ":True,
        "NO_2011_WMR_GPS_habitat_Y_RWS_solar_or_tide_index_scored":True,
        "2010_original_v86_true_binary_tideflat_result_UNCHANGED":True,
        "no_original_bird_tags_exact_times_latlon_or_tracks_saved":True}
    file=Path(output);file.parent.mkdir(parents=True,exist_ok=True)
    file.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    print("V87_GENUINE_INDEPENDENT_2011_BIRD_YEAR_SOURCE_DECISION "+
          json.dumps({site:prospects[site]["frozen_source_prospect"][
             "source_status"] for site in SITES},sort_keys=True),flush=True)
    print("V87_2010_2011_ANON_BIRD_ID_SOURCE_PROVENANCE_COMPLETE",flush=True)
    return out

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--output",required=True)
    run(a.parse_args().output)
