"""v79 original 2010 Ameland entire-year SOURCE-ONLY bird-month census.

This new source opportunity follows failed v78 Ameland 7-bird Aug–Dec source
gate but DOES NOT change v78 or compute a tide/model habitat effect.
No external original GPS tag/track/timestamp/coords or model pixel emitted.
"""
from __future__ import annotations

import csv,gzip,json,math,os,tempfile
from collections import Counter,defaultdict
from pathlib import Path

from ameland_external_site import original_gps,BBOX
from source_preflight import parse_stamp

ORIGINAL_AMELAND_GPS_YEAR=2010
ORIGINAL_AMELAND_RAW=119507
EXPECTED_AMELAND_GPS_SHA="c92f1a21ee95c41f59e0c3ef4567a0d953b86b134bb895186cab40bb2e6cb61c"
ORIGINAL_OLD_V78_2010_SOURCE={
    8:(5106,7),9:(4581,7),10:(3629,7),11:(3220,6),12:(3076,6)}
MODEL_NATIVE_GEO_VALID_2010_MONTHS=(1,2,3,4,5,8,9,10,11,12)
MODEL_NATIVE_GEO_BAD_MONTHS=(6,7)
ORIGINAL_FUTURE_SEPARATE_SITE_ANIMALS_GATE=8

def source_month_counts(path,*,expected_raw=ORIGINAL_AMELAND_RAW,
                        verify_v78_late_source=True):
    """Immutable real original event/qc, earliest native per bird-hour."""
    needed={"event-id","individual-local-identifier","timestamp",
            "location-lat","location-long","visible"}
    unique_events=set()
    native_bybird=defaultdict(dict)
    dropped=Counter();raw=0
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as src:
        reader=csv.DictReader(src)
        if not needed<=set(reader.fieldnames or []):
            raise ValueError("SOURCE_STOP_V79_UNEXPECTED_PUBLISHED_AMELAND_GPS_COLUMNS")
        for v in reader:
            raw+=1
            eid=(v.get("event-id") or "").strip()
            if not eid or eid in unique_events:
                dropped["source_duplicate_or_missing_event_id"]+=1;continue
            unique_events.add(eid)
            if (v.get("visible") or "").strip().upper() in ("FALSE","0"):
                dropped["source_invisible_original_record"]+=1;continue
            bird=(v.get("individual-local-identifier") or "").strip()
            if not bird:
                dropped["source_missing_original_bird"]+=1;continue
            try:
                t=parse_stamp(v["timestamp"])
                lat=float(v["location-lat"]);lon=float(v["location-long"])
            except (TypeError,ValueError):
                dropped["source_invalid_GPS_time_or_location"]+=1;continue
            if (t.year!=ORIGINAL_AMELAND_GPS_YEAR or
                not(math.isfinite(lat) and math.isfinite(lon)) or
                not (BBOX[0]<=lat<=BBOX[1] and BBOX[2]<=lon<=BBOX[3])):
                dropped["outside_frozen_original_2010_Ameland_site"]+=1;continue
            hour=t.replace(minute=0,second=0,microsecond=0)
            previous=native_bybird[bird].get(hour)
            if previous is None or t<previous:
                native_bybird[bird][hour]=t
    if raw!=expected_raw:
        raise ValueError("SOURCE_STOP_V79_ORIGINAL_2010_AMELAND_GPS_119507_DRIFT")
    monthcount=defaultdict(Counter)
    for bird,fixes in native_bybird.items():
        for t in fixes.values():
            monthcount[t.month][bird]+=1
    receipt={}
    for m in range(1,13):
        positions=sum(monthcount[m].values())
        n_birds=len(monthcount[m])
        supported=sum(n>=20 for n in monthcount[m].values())
        receipt[f"{m:02d}"]={
            "original_Ame_gps_native_earliest_hour_source_fixes":positions,
            "original_Ame_distinct_bird_IDs":n_birds,
            "original_Ame_birds_with_ge20_hourly_gps_source":supported,
            "2010_native_NIOZ_model_geographic_status_previously_audited":
                "2010_NATIVE_GEO_PRIOR_SOURCE_CANDIDATE_ONLY"
                if m in MODEL_NATIVE_GEO_VALID_2010_MONTHS else
                "2010_NATIVE_GEO_SOURCE_MISSING_LAT_FROM_V74"}
        if verify_v78_late_source and m in ORIGINAL_OLD_V78_2010_SOURCE and (
            positions,n_birds)!=ORIGINAL_OLD_V78_2010_SOURCE[m]:
            raise ValueError("SOURCE_STOP_V79_PREVIOUS_V78_AUG_DEC_SOURCE_DRIFT")
    early={b for m in range(1,6) for b in monthcount[m]}
    late={b for m in range(8,13) for b in monthcount[m]}
    geocoded_candidate=early|late
    other={b for m in range(6,8) for b in monthcount[m]}
    status=(
        "CANDIDATE_EXPANDED_AMELAND_SOURCE_FRAME_REQUIRES_NEW_MODEL_GPS_JOIN"
        if len(geocoded_candidate)>=ORIGINAL_FUTURE_SEPARATE_SITE_ANIMALS_GATE
        else "NOT_ADMITTED_V79_FULL_2010_AMELAND_GEO_CANDIDATE_BIRD_COUNT")
    return {
        "analysis":"V79_ORIGINAL_AMELAND_ALL_2010_BIRDS_MONTHS_SOURCE_ONLY",
        "source_original_gps_annual_raw_records":raw,
        "all_twelve_original_months":receipt,
        "original_2010_total_distinct_bird_IDs_after_geographic_visible_hour_filter":
            len(native_bybird),
        "original_2010_month_01_05_birds_union_count":len(early),
        "original_2010_month_08_12_birds_union_count":len(late),
        "original_2010_birds_both_early_and_late_count":len(early&late),
        "original_2010_early_only_birds_not_in_v78_late_source":len(early-late),
        "original_2010_2010JanMay_AugDec_geo_candidate_birds_union":
            len(geocoded_candidate),
        "original_2010_JunJul_with_model_native_lat_missing_birds":
            len(other),
        "original_geocodable_month_list_from_separate_prior_v74_NIOZ_source_audit":
            list(MODEL_NATIVE_GEO_VALID_2010_MONTHS),
        "original_missing_native_model_lat_2010months":[6,7],
        "old_AugDec_v78_original_7bird_source_still_NOT_ADMITTED":True,
        "new_full_year_candidate_status":status,
        "no_model_used_value_rank_tide_phase_or_solar_daynight_scored":True,
        "no_original_source_bird_ID_GPS_fix_time_or_location_saved":True,
        "source_gps_original_clock_UTC_or_GPS_unverified":True,
        "excluded_original_source_reason_counts":dict(dropped)}

def run(output):
    with tempfile.TemporaryDirectory(prefix="v79_original_amELAND_2010_") as tmp:
        f=Path(tmp)/"original_Ame_2010.csv.gz"
        origin=original_gps(2010,f)
        if (origin.get("provider_original_md5_matched") is not True or
            origin["original_sha256"]!=EXPECTED_AMELAND_GPS_SHA):
            raise ValueError("SOURCE_STOP_V79_PUBLISHED_AMELAND_2010_MD5_SHA_DRIFT")
        result=source_month_counts(f)
    result["source_Zenodo_original_publisher_MD5_authenticated"]=True
    result["source_Zenodo_original_2010_gps_sha256"]=origin["original_sha256"]
    result["source_Zenodo_original_gps_bytes"]=origin["original_bytes"]
    result["source_model_native_prior_source_document"]="docs/V74_ORIGINAL_WILD_2010_ALL_NIOZ_MONTHS_SOURCE_RESULT_JA.md"
    result["executed_commit"]=os.environ.get("GITHUB_SHA","local")
    p=Path(output)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("V79_GENUINE_ALL_YEAR_AMELAND_BIRD_MONTH_SOURCE "+
          json.dumps({
             "original_gps_all_year_unique_birds":
                result["original_2010_total_distinct_bird_IDs_after_geographic_visible_hour_filter"],
             "original_early_JanMay_birds":
                result["original_2010_month_01_05_birds_union_count"],
             "original_prior_AugDec_birds":
                result["original_2010_month_08_12_birds_union_count"],
             "original_additional_early_only_birds":
                result["original_2010_early_only_birds_not_in_v78_late_source"],
             "native_model_candidate_month_bird_union":
                result["original_2010_2010JanMay_AugDec_geo_candidate_birds_union"],
             "new_source_opportunity_status":result["new_full_year_candidate_status"],
             "no_new_biological_tide_or_solar_effect":True,
             "months":result["all_twelve_original_months"]},
          sort_keys=True),flush=True)
    print("V79_ALL_2010_AMELAND_SOURCE_CENSUS_COMPLETE",flush=True)
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--output",required=True)
    run(p.parse_args().output)
