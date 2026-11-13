"""v127 first genuine 2019 Vlieland Haven RWS June-Sep measured 10-minute tide.

Official station vlieland.haven, original WATHTE measured cm NAP, source +01
timestamp converted to actual UTC. Four fixed original months, each >=80%
real 10-minute coverage. NO interpolation or astronomical height substitute.
This is a harbour tide PROXY, not h(x,t) at GPS forage site.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import json,math,time
from original_2019_Vlieland_behaviour_source import SourceStop
from real_2019_RWS_Vlieland_Haven_source import (
    STATION_CODE,validate_original_vlieland_station_catalogue,
    publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META)

SOURCE_YEAR=2019
MONTHS=(6,7,8,9)
ORIGINAL_RWS_48H_PILOT_RUN=43030597916
MIN_MONTH_COVERAGE=.80
MAX_ABS_HEIGHT_CM=500
MEASURED_TIMEZONE_OFFSET=timedelta(hours=1)
MONTH_DAYS={6:30,7:31,8:31,9:30}

class NativeTideSourceStop(SourceStop):pass

def validate_previous_RWS_48h_pilot(proof):
    if (proof.get('analysis')!='V126_RWS_2019_ORIGINAL_VLIELAND_HAVEN_JUNE_48H_TRUE_MEASURED_TIDAL_SOURCE' or
        proof.get('source_status')!='ORIGINAL_RWS_2019_VLIELAND_HAVEN_MEASURED_TIDE_SOURCE_ADMITTED' or
        proof.get('original_publisher_RWS_station_identity',{}).get('original_native_RWS_station_code')!=STATION_CODE or
        proof.get('original_2019_true_tide_source_quality',{}).get('native_original_2019_waterheight_observed_10min_n')!=289):
        raise NativeTideSourceStop('STOP_V127_ORIGINAL_RWS_V126_2019_48H_SOURCE_IDENTITY_DRIFT')
    return {'same_native_v126_RWS_gauge_station':'vlieland.haven',
      'native_true_48h_10min_measurements':289,
      'source_previous_RWS_pilot_action':ORIGINAL_RWS_48H_PILOT_RUN}

def request_real_month(month):
    if month not in MONTHS:
        raise NativeTideSourceStop('STOP_V127_NOT_FROZEN_2019_REAL_TIDE_MONTH')
    begin=datetime(SOURCE_YEAR,month,1)
    end=datetime(SOURCE_YEAR,month+1,1)
    payload={'Locatie':{'Code':STATION_CODE},
         'AquoPlusWaarnemingMetadata':{'AquoMetadata':NATIVE_META},
         'Periode':{'Begindatumtijd':begin.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
                    'Einddatumtijd':end.strftime('%Y-%m-%dT%H:%M:%S.000+01:00')}}
    obj,sha=publisher_post(DATA_ROUTE,payload)
    return obj,sha

def parse_native_month(month,obj):
    if month not in MONTHS:raise NativeTideSourceStop('STOP_V127_UNFROZEN_RWS_MONTH')
    if obj.get('Succesvol') is not True:
        raise NativeTideSourceStop('STOP_V127_REAL_RWS_OFFICIAL_SOURCE_MONTH_EXPLICIT_REJECTION')
    result={};raw_count=0;reasons=Counter()
    for series in obj.get('WaarnemingenLijst') or []:
        aq=series.get('AquoMetadata') or {}
        if ((aq.get('Grootheid') or {}).get('Code')!='WATHTE' or
            (aq.get('Eenheid') or {}).get('Code')!='cm' or
            (aq.get('Hoedanigheid') or {}).get('Code')!='NAP'):
            reasons['not_native_measured_WATHTE_cm_NAP']+=1
            continue
        for rec in series.get('MetingenLijst') or []:
            raw_count+=1
            try:
                dt=datetime.fromisoformat(rec['Tijdstip'].replace('Z','+00:00'))
                if dt.utcoffset()!=MEASURED_TIMEZONE_OFFSET:
                    reasons['real_native_clock_offset_not_plus_01']+=1
                    continue
                v=float((rec.get('Meetwaarde') or {}).get('Waarde_Numeriek'))
                if not math.isfinite(v) or abs(v)>MAX_ABS_HEIGHT_CM:
                    reasons['real_source_invalid_cm_NAP']+=1
                    continue
                utc=dt.astimezone(timezone.utc)
                if utc in result and abs(result[utc]-v/100)>1e-8:
                    raise NativeTideSourceStop('STOP_V127_CONTRADICTORY_REAL_RWS_MONTH_SAME_TIME')
                result[utc]=v/100
            except (ValueError,KeyError,TypeError):
                reasons['real_source_timestamp_or_cm_parse_error']+=1
    expected=6*24*MONTH_DAYS[month]
    if len(result)<MIN_MONTH_COVERAGE*expected:
        raise NativeTideSourceStop('STOP_V127_ORIGINAL_RWS_2019_MONTH_COVERAGE_LT80PCT')
    stamps=sorted(result)
    gaps=[(b-a).total_seconds()/60 for a,b in zip(stamps,stamps[1:])]
    return result,{'source_month':month,
       'true_original_2019_10min_unique_count':len(result),
       'expected_10min_slots_per_native_month':expected,
       'source_native_month_coverage':len(result)/expected,
       'original_UTC_first_2019':stamps[0].isoformat(),
       'original_UTC_last_2019':stamps[-1].isoformat(),
       'original_max_native_source_gap_min':max(gaps) if gaps else None,
       'source_original_raw_measurement_rows':raw_count,
       'native_rejected_original_readings':dict(reasons),
       'real_waterheight_cmNAP_to_metres_divide_by100_only':True}

def fetch_all_2019_Vlieland_real_RWS_months(previous_pilot,request_fn=request_real_month,
                                             sleeper=time.sleep):
    prior=validate_previous_RWS_48h_pilot(previous_pilot)
    result={};sources=[]
    for i,month in enumerate(MONTHS):
        if i:sleeper(1)
        obj,sha=request_fn(month)
        values,qa=parse_native_month(month,obj)
        for t,v in values.items():
            if t in result and abs(result[t]-v)>1e-8:
                raise NativeTideSourceStop('STOP_V127_REAL_ORIGINAL_MONTH_BOUNDARY_CONFLICT')
            result[t]=v
        sources.append({**qa,'original_RWS_2019_month_JSON_SHA256':sha})
        print('V127_ORIGINAL_2019_VLIELAND_REAL_TIDE_MONTH_SOURCE '+json.dumps({
          'month':month,'n_original_10min_heights':qa['true_original_2019_10min_unique_count'],
          'native_80pct_source_gate':qa['source_native_month_coverage']>=MIN_MONTH_COVERAGE},
          sort_keys=True),flush=True)
    return result,{'source_status':'TRUE_ORIGINAL_2019_VLIELAND_HAVEN_JUNE_SEPT_ALL4_MONTHS_MEASURED_ADMITTED',
         'source_prior_genuine_RWS_48hour':prior,
         'original_true_2019_months':sources,
         'native_RWS_true_2019_10min_unique_readings_four_months':len(result),
         'original_source_no_real_waterheight_values_exported':True,
         'original_2019_harbour_tide_not_local_foraging_patch':True}
