"""v221: real original 2018/19 oystercatcher GPS+ACC previous-15min cohort
versus genuine BAW year-NL time-resolved WCS2 domain and 20min model clock.

This is native source JOIN ADMISSION only, no water height at GPS, no bird
Y model, no raw tag identity/position/timestamp output and no model GetCoverage.
Only prior genuine Zenodo/RWS SHA-pinned v168 source recovery.

A "nearer future WCS time" could leak information into an online estimate;
report both the purely past and nearest source-clock alignment strategies.
2025 retrospective BAW hindcast was NOT a prospective 2018/19 forecast.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path

from v168_true_year_transfer import (
    source_receipts_exact,source_input_and_replay,verified_2019_source,
    corrected_previous_bin
)
from original_BAW_ncHydro_yearly_WCS_candidate_metadata import (
    CANDIDATE,original_GET,describe_URL
)
from BAW_ncHydro_2018_2019_WCS_supported_formats_axes_source import (
    FROZEN_WCS_CAP_SHA,FROZEN_DESCRIBE_SHA,FROZEN_COVERAGE_IDS,
    source_native_description_axes
)

YEAR_COHORT={
    2018:{"raw_common":193088,"prior15":157863},
    2019:{"raw_common":155387,"prior15":125241}
}
FOUR_MONTHS=(6,7,8,9)
BAW_NATIVE_GRID_INTERVAL_SEC=1200
FROZEN_NATIVE_SPACE_LAT=(52.863260107482425,53.94115222955482)
FROZEN_NATIVE_SPACE_LONG=(4.176920490043966,7.3396245354662515)
FROZEN_NIL="9.999999848243207E30"
TIME_BINS=("nearest_le_60sec","nearest_60to300sec","nearest_300to600sec")
OUT=Path(__file__).resolve().parent/"results/real_original_Vlieland_oystercatcher_GPS_15min_to_BAW_WCS20min_source_admission_v221.json"

def chronological_WCS20min_UTC_join_clock(t,year):
    """No forecast invention: times are ORIGINAL UTC event timestamps."""
    if not isinstance(t,datetime) or t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("SOURCE_STOP_ORIGINAL_BIRD_EVENT_TIME_NOT_UTC_AWARE")
    if year not in YEAR_COHORT:
        raise ValueError("SOURCE_STOP_UNFROZEN_GPS_YEAR")
    utc=t.astimezone(timezone.utc)
    if utc.year!=year:
        raise ValueError("SOURCE_STOP_BIRD_EVENT_YEAR_DIFFERENT_FROM_COHORT")
    epoch=datetime(year,1,1,tzinfo=timezone.utc)
    seconds=(utc-epoch).total_seconds()
    if not math.isfinite(seconds) or not(0<=seconds<366*86400):
        raise ValueError("SOURCE_STOP_ORIGINAL_BIRD_TIMESTAMP_OUTSIDE_MODEL_YEAR")
    k=math.floor(seconds/BAW_NATIVE_GRID_INTERVAL_SEC)
    lag=seconds-k*BAW_NATIVE_GRID_INTERVAL_SEC
    use_future=lag>BAW_NATIVE_GRID_INTERVAL_SEC/2
    abs_offset=min(lag,BAW_NATIVE_GRID_INTERVAL_SEC-lag)
    if abs_offset<=60:
        category=TIME_BINS[0]
    elif abs_offset<=300:
        category=TIME_BINS[1]
    else:
        category=TIME_BINS[2]
    nearest_index=k+(1 if use_future else 0)
    return {
        "past_lag_sec":float(lag),
        "nearest_abs_offset_sec":float(abs_offset),
        "nearest_requires_future_model_clock":bool(use_future),
        "nearest_bin":category,
        "selected_past_model_timestamp":epoch+timedelta(
            seconds=k*BAW_NATIVE_GRID_INTERVAL_SEC),
        "selected_nearest_model_timestamp":epoch+timedelta(
            seconds=nearest_index*BAW_NATIVE_GRID_INTERVAL_SEC),
    }

def native_space_from_WCS_description(source,year):
    if year not in YEAR_COHORT:
        raise ValueError("SOURCE_STOP_UNFROZEN_BAW_WCS_YEAR")
    env=source.get("source_native_envelopes",[])
    if len(env)!=1 or env[0].get("native_axisLabels")!="Lat Long time":
        raise ValueError("SOURCE_STOP_ORIGINAL_BAW_ENVELOPE_NOT_LAT_LONG_TIME")
    lower=[float(x) for x in env[0].get("source_lowerCorner","").split()]
    upper=[float(x) for x in env[0].get("source_upperCorner","").split()]
    if len(lower)!=2 or len(upper)!=2 or not (
        lower[0]<upper[0] and lower[1]<upper[1]):
        raise ValueError("SOURCE_STOP_NATIVE_BAW_WCS2_ENVELOPE_NOT_SPATIAL_TWOAXIS")
    if any(abs(a-b)>1e-8 for a,b in zip(
            (lower[0],upper[0],lower[1],upper[1]),
            (*FROZEN_NATIVE_SPACE_LAT,*FROZEN_NATIVE_SPACE_LONG))):
        raise ValueError("SOURCE_STOP_ORIGINAL_NATIVE_BAW_SOURCE_ENVELOPE_CHANGED")
    times=source.get("source_time_positions_if_any",[])
    stamps={x.get("source_time") for x in times}
    if f"{year}-01-01T00:00:00.000Z" not in stamps or (
        f"{year+1}-01-01T00:00:00.000Z" not in stamps):
        raise ValueError("SOURCE_STOP_NATIVE_WCS_ORIGINAL_YEAR_TIME_EXTENT_CHANGED")
    if FROZEN_NIL not in [x.get("native_literal") for x in source.get("source_nil_values",[])]:
        raise ValueError("SOURCE_STOP_NATIVE_WCS_NIL_SOURCE_CHANGED")
    if "m" not in [x.get("native_uom_code") for x in source.get("source_UOM_tags",[])]:
        raise ValueError("SOURCE_STOP_NATIVE_WCS_HEIGHT_UNIT_SOURCE_CHANGED")
    return tuple(lower),tuple(upper)

def native_WCS_potential_GPS_geography(lat,lon,lower,upper):
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in
       (lat,lon,*lower,*upper)):
        raise ValueError("SOURCE_STOP_NATIVE_BIRD_GPS_COORDINATE_NOT_FINITE")
    if not (-90<=lat<=90 and -180<=lon<=180):
        raise ValueError("SOURCE_STOP_ORIGINAL_TAGGED_GPS_OUTSIDE_GEOGRAPHIC_COORDINATES")
    return lower[0]<=lat<=upper[0] and lower[1]<=lon<=upper[1]

def make_source_counter():
    return {
       "n_original_tagged_GPS_ACC_bins":0,
       "n_inside_published_BAW_WCS2_NL_geographical_envelope":0,
       "n_outside_published_BAW_WCS2_NL_envelope":0,
       "n_nearest_model20min_clock_requires_future_value":0,
       "n_exact_native_20min_clock_events":0,
       "nearest_abs_offset_seconds_sum":0.,
       "source_past_model_clock_lag_seconds_sum":0.,
       "max_nearest_offset_sec":0.,
       "fixed_nearest_offset_bins":{label:0 for label in TIME_BINS},
    }

def source_counter_add(row,inbounds,join):
    row["n_original_tagged_GPS_ACC_bins"]+=1
    row["n_inside_published_BAW_WCS2_NL_geographical_envelope"]+=int(inbounds)
    row["n_outside_published_BAW_WCS2_NL_envelope"]+=int(not inbounds)
    row["n_nearest_model20min_clock_requires_future_value"]+=int(
       join["nearest_requires_future_model_clock"])
    row["n_exact_native_20min_clock_events"]+=int(join["nearest_abs_offset_sec"]<=1e-9)
    row["nearest_abs_offset_seconds_sum"]+=join["nearest_abs_offset_sec"]
    row["source_past_model_clock_lag_seconds_sum"]+=join["past_lag_sec"]
    row["max_nearest_offset_sec"]=max(row["max_nearest_offset_sec"],join["nearest_abs_offset_sec"])
    row["fixed_nearest_offset_bins"][join["nearest_bin"]]+=1

def source_counter_final(row):
    n=row["n_original_tagged_GPS_ACC_bins"]
    if n==0:
        return {"source_status":"NO_ORIGINAL_SOURCE_BINS_IN_THIS_FROZEN_STRATUM",
                "n_original_tagged_GPS_ACC_bins":0}
    if (row["n_inside_published_BAW_WCS2_NL_geographical_envelope"]+
        row["n_outside_published_BAW_WCS2_NL_envelope"]!=n or
        sum(row["fixed_nearest_offset_bins"].values())!=n):
        raise ValueError("SOURCE_STOP_BIRD_GEO_OR_TIME_GRID_SOURCE_PARTITION_NOT_EXHAUSTIVE")
    return {
      "source_status":"ORIGINAL_BIRD_15MIN_GPS_AND_BAW_20MIN_AXIS_SOURCE_AUDITED",
      "n_original_tagged_GPS_ACC_bins":n,
      "n_inside_published_BAW_WCS2_NL_geographical_envelope":
         row["n_inside_published_BAW_WCS2_NL_geographical_envelope"],
      "n_outside_published_BAW_WCS2_NL_envelope":
         row["n_outside_published_BAW_WCS2_NL_envelope"],
      "source_fraction_inside_geographic_envelope_not_actual_native_height_validity":
         round(row["n_inside_published_BAW_WCS2_NL_geographical_envelope"]/n,8),
      "n_nearest_model20min_clock_requires_future_value":
         row["n_nearest_model20min_clock_requires_future_value"],
      "fraction_nearest_model_time_later_than_bird_observation":
         round(row["n_nearest_model20min_clock_requires_future_value"]/n,8),
      "n_exact_native_20min_clock_events":
         row["n_exact_native_20min_clock_events"],
      "nearest_source_offset_seconds_mean":
         round(row["nearest_abs_offset_seconds_sum"]/n,6),
      "past_only_source_model_clock_lag_seconds_mean":
         round(row["source_past_model_clock_lag_seconds_sum"]/n,6),
      "max_source_nearest_time_offset_sec":round(row["max_nearest_offset_sec"],3),
      "native_20min_nearest_clock_offset_bins":row["fixed_nearest_offset_bins"],
      "real_time_model_Nil_at_original_GPS_NOT_sampled":True,
      "original_bird_tag_GPS_ACC_positions_times_not_persisted":True,
    }

def authentic_year_source_cohort(common,source_indices,year,lower,upper):
    if year not in YEAR_COHORT or len(common)!=YEAR_COHORT[year]["raw_common"]:
        raise ValueError("SOURCE_STOP_ORIGINAL_YEAR_BIRD_GPS_COMMON_N_CHANGED")
    if len(source_indices)!=YEAR_COHORT[year]["prior15"]:
        raise ValueError("SOURCE_STOP_ORIGINAL_YEAR_PREV15_COHORT_CHANGED")
    overall=make_source_counter()
    months={m:make_source_counter() for m in FOUR_MONTHS}
    solar={s:make_source_counter() for s in ("day","night")}
    distinct_birds=set()
    for index in source_indices:
        e,light,_,_=common[int(index)]
        t=e.get("source_utc_event")
        mon=e.get("source_month")
        if mon not in FOUR_MONTHS or light not in ("day","night"):
            raise ValueError("SOURCE_STOP_ORIGINAL_BIRD_MONTH_OR_SOURCE_SOLAR_CATEGORY_CHANGED")
        if e.get("private_bird") is None:
            raise ValueError("SOURCE_STOP_ORIGINAL_TAGGED_BIRD_PRIVATE_IDENTIFICATION_MISSING")
        distinct_birds.add(e["private_bird"])
        try:
            lat=float(e["source_lat"])
            lon=float(e["source_lon"])
        except (KeyError,TypeError,ValueError) as exc:
            raise ValueError("SOURCE_STOP_ORIGINAL_BIRD_GPS_LAT_LON_NOT_RETRIEVED") from exc
        join=chronological_WCS20min_UTC_join_clock(t,year)
        inside=native_WCS_potential_GPS_geography(lat,lon,lower,upper)
        source_counter_add(overall,inside,join)
        source_counter_add(months[mon],inside,join)
        source_counter_add(solar[light],inside,join)
    source=source_counter_final(overall)
    source["source_distinct_tagged_birds_count_only"]=len(distinct_birds)
    source["original_source_within_GPS_20min_join_does_NOT_check_Nil"]=True
    source["by_original_month"]={str(m):source_counter_final(v)
                                 for m,v in months.items()}
    source["by_original_solar_day_night"]={name:source_counter_final(v)
                                         for name,v in solar.items()}
    if sum(v["n_original_tagged_GPS_ACC_bins"] for v in source["by_original_month"].values())!=len(source_indices):
        raise ValueError("SOURCE_STOP_YEAR_FOUR_MONTH_GPS_SOURCE_COUNTS_NOT_EXHAUSTIVE")
    if sum(v["n_original_tagged_GPS_ACC_bins"] for v in source["by_original_solar_day_night"].values())!=len(source_indices):
        raise ValueError("SOURCE_STOP_DAY_NIGHT_ORIGINAL_ACC_SOURCE_COUNTS_NOT_EXHAUSTIVE")
    return source

def run(v128,v129,v126gps,v126rws,v127,out=OUT):
    report={"version":"v221-real-2018-2019-oystercatcher-ACC-GPS-to-BAW-source-20minute",
      "frozen_2018_and2019_true_GPS_ACC_with_prev15_source_denominators":YEAR_COHORT,
      "frozen_BAW_native_envelope_lat":FROZEN_NATIVE_SPACE_LAT,
      "frozen_BAW_native_envelope_long":FROZEN_NATIVE_SPACE_LONG,
      "native_BAW_model_time_grid_seconds":BAW_NATIVE_GRID_INTERVAL_SEC,
      "BAW_2025_product_retrospective_not_2018_year_ahead_forecast":True,
      "no_raw_bird_ID_GPS_UTC_ACC_Y_or_BAW_h_s_t_values_exported":True,
      "status":"SOURCE_STOP"}
    years={}
    try:
        verified_source={}
        for year in (2018,2019):
            c,cap=original_GET(str(year),CANDIDATE[str(year)],"GetCapabilities")
            if c is None or cap["original_SHA256"]!=FROZEN_WCS_CAP_SHA[str(year)]:
                raise ValueError("SOURCE_STOP_BAW_NATIVE_YEAR_CAPABILITIES_SHA_CHANGED")
            raw,desc=original_GET(str(year),describe_URL(str(year),FROZEN_COVERAGE_IDS[str(year)]),
                      "DescribeCoverage",FROZEN_COVERAGE_IDS[str(year)],max_bytes=2000000)
            if raw is None or desc["original_SHA256"]!=FROZEN_DESCRIBE_SHA[str(year)]:
                raise ValueError("SOURCE_STOP_BAW_NATIVE_YEAR_DESCRIBE_SHA_CHANGED")
            m=source_native_description_axes(raw,FROZEN_COVERAGE_IDS[str(year)])
            lower,upper=native_space_from_WCS_description(m,year)
            verified_source[year]=(lower,upper)
        report["both_years_authentic_native_WCS_Cap_and_Describe_source_verified"]=True
        source_receipts_exact()
        tr,sha18=source_input_and_replay(v128,v129)
        te,sha19=verified_2019_source(v126gps,v126rws,v127)
        if len(tr)!=YEAR_COHORT[2018]["raw_common"] or len(te)!=YEAR_COHORT[2019]["raw_common"]:
            raise ValueError("SOURCE_STOP_BIRD_YEAR_TOTAL_COMMON_SOURCE_CHANGED")
        idx18,_,_=corrected_previous_bin(tr)
        idx19,_,_=corrected_previous_bin(te)
        years["2018"]=authentic_year_source_cohort(tr,idx18,2018,*verified_source[2018])
        years["2019"]=authentic_year_source_cohort(te,idx19,2019,*verified_source[2019])
        report["original_bird_2018_and_2019_native_zenodo_rws_source_replay_verified"]=True
        report["status"]="REAL_OYSTERCATCHER_2018_2019_GPS_ACC_SOURCE_BAW_SPACE_TIME_ADMISSION_AUDITED"
    except Exception as exc:
        report["source_error_kind"]=type(exc).__name__
        report["source_error_summary"]=str(exc)[:250]
    report["original_observed_bird_source_clock_and_geography"]=years
    report["scientific_gates"]={
      "both_years_true_original_Zenodo_GPS_ACC_RWS_and_BAW_native_source_admitted":
         report["status"]=="REAL_OYSTERCATCHER_2018_2019_GPS_ACC_SOURCE_BAW_SPACE_TIME_ADMISSION_AUDITED",
      "source_2018_prev15_animal_bins_preserved":
         years.get("2018",{}).get("n_original_tagged_GPS_ACC_bins")==YEAR_COHORT[2018]["prior15"],
      "source_2019_prev15_animal_bins_preserved":
         years.get("2019",{}).get("n_original_tagged_GPS_ACC_bins")==YEAR_COHORT[2019]["prior15"],
      "original_bird_cell_BAW_WCS_water_height_or_missingness_observed":False,
      "original_BAW_h_and_native20m_DEM_z_datum_and_surveyday_calibrated":False,
      "true_bird_local_dryflat_foraging_tide_solar_or_Boids_social_effect_estimated":False}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("V221_REAL_BIRD_GPS_ACC_WCS20MIN_SOURCE="+json.dumps({
      "status":report["status"],"gates":report["scientific_gates"],
      "year":{y:{
        "n":v["n_original_tagged_GPS_ACC_bins"],
        "birds":v["source_distinct_tagged_birds_count_only"],
        "inside_n":v["n_inside_published_BAW_WCS2_NL_geographical_envelope"],
        "inside_frac":v["source_fraction_inside_geographic_envelope_not_actual_native_height_validity"],
        "nearest_future_fraction":v["fraction_nearest_model_time_later_than_bird_observation"],
        "mean_abs_nearest_sec":v["nearest_source_offset_seconds_mean"],
        "mean_past_lag_sec":v["past_only_source_model_clock_lag_seconds_mean"],
        "offset_bins":v["native_20min_nearest_clock_offset_bins"],
        "months":{m:{"n":a["n_original_tagged_GPS_ACC_bins"],"inside":a["n_inside_published_BAW_WCS2_NL_geographical_envelope"]}
                  for m,a in v["by_original_month"].items()},
        "solar":{m:{"n":a["n_original_tagged_GPS_ACC_bins"],"inside":a["n_inside_published_BAW_WCS2_NL_geographical_envelope"]}
                  for m,a in v["by_original_solar_day_night"].items()},
      } for y,v in years.items()},
      "source_error":report.get("source_error_summary"),
      "NO_original_bird_identity_or_GPS_or_model_height_exported":True
    },sort_keys=True))
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    for name in ("v128","v129","v126-gps","v126-rws","v127"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--output",type=Path,default=OUT)
    args=p.parse_args()
    run(args.v128,args.v129,args.v126_gps,args.v126_rws,args.v127,args.output)
