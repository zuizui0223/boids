"""v129 genuinely observed 2018 June–September 10minute Rijkswaterstaat
Vlieland Haven RWS WATHTE measured cm NAP source. No interpolated tides.
Historical 2018 source after v127 2019 result, fixed station and source years.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timedelta,timezone
from hashlib import sha256
import json,math,time
from real_2019_RWS_Vlieland_Haven_source import STATION_CODE
from rws_roompot_2020_source import (
    publisher_post,DATA_ROUTE,NATIVE_META,SourceStop as OfficialRWSStop)

YEAR=2018
MONTHS=(6,7,8,9)
DAYS={6:30,7:31,8:31,9:30}
MIN_10MIN_COVERAGE=.8
FIXED_SOURCE_CLOCK=timedelta(hours=1)
MAX_RWS_CM_NAP=500

class NativeSourceStop(Exception):pass

def request_month_original_RWS(month):
    if month not in MONTHS:
        raise NativeSourceStop('SOURCE_STOP_2018_NOT_FROZEN_RWS_MONTH')
    first=datetime(YEAR,month,1)
    end=datetime(YEAR,month+1,1)
    period={'Begindatumtijd':first.strftime('%Y-%m-%dT%H:%M:%S.000+01:00'),
            'Einddatumtijd':end.strftime('%Y-%m-%dT%H:%M:%S.000+01:00')}
    return publisher_post(DATA_ROUTE,{'Locatie':{'Code':STATION_CODE},
      'AquoPlusWaarnemingMetadata':{'AquoMetadata':NATIVE_META},'Periode':period})

def parse_true_original_RWS_2018_month(month,source):
    if month not in MONTHS:raise NativeSourceStop('SOURCE_STOP_2018_NON_FROZEN_RWS_MONTH')
    if source.get('Succesvol') is not True:
        raise NativeSourceStop('SOURCE_STOP_ORIGINAL_RWS_2018_REJECTED_MONTH')
    readings={};qa=Counter();nrows=0
    for series in source.get('WaarnemingenLijst') or []:
        meta=series.get('AquoMetadata') or {}
        if ((meta.get('Grootheid') or {}).get('Code')!='WATHTE' or
            (meta.get('Eenheid') or {}).get('Code')!='cm' or
            (meta.get('Hoedanigheid') or {}).get('Code')!='NAP'):
            qa['not_verified_measured_WATHTE_cm_NAP']+=1;continue
        for v in series.get('MetingenLijst') or []:
            nrows+=1
            try:
                ts=datetime.fromisoformat(v['Tijdstip'].replace('Z','+00:00'))
                if ts.utcoffset()!=FIXED_SOURCE_CLOCK or ts.year!=YEAR:
                    qa['native_year_or_RWS_clock_not_2018_source_plus01']+=1;continue
                cm=float((v.get('Meetwaarde') or {}).get('Waarde_Numeriek'))
                if not math.isfinite(cm) or abs(cm)>MAX_RWS_CM_NAP:
                    qa['invalid_native_observed_cm_NAP']+=1;continue
                utc=ts.astimezone(timezone.utc)
                if utc in readings and abs(readings[utc]-cm/100)>1e-8:
                    raise NativeSourceStop('SOURCE_STOP_REAL_RWS_2018_DUPLICATE_CONFLICT')
                readings[utc]=cm/100
            except (ValueError,TypeError,KeyError):
                qa['native_2018_gauge_row_unreadable']+=1
    expected=6*24*DAYS[month]
    if len(readings)<MIN_10MIN_COVERAGE*expected:
        raise NativeSourceStop('SOURCE_STOP_2018_MONTH_LT80PCT_TRUE_RWS_10MIN')
    if len(readings)>expected+2:
        raise NativeSourceStop('SOURCE_STOP_2018_RWS_SOURCE_UNEXPECTED_EXCESS_PER_MONTH')
    stamp=sorted(readings)
    return readings,{'true_original_RWS_source_month':month,
         'original_2018_native_observed_10minute_time_count':len(readings),
         'expected_exact_10minute_month_slots':expected,
         'original_2018_native_RWS_valid_fraction':len(readings)/expected,
         'original_first_real_UTC':stamp[0].isoformat(),
         'original_last_real_UTC':stamp[-1].isoformat(),
         'source_native_raw_RWS_rows':nrows,
         'native_rws_rejections':dict(qa),
         'original_hourly_or_missing_10minute_tide_NOT_INTERPOLATED':True}

def exact_original_RWS_transport_retry(month,sleeper=time.sleep):
    transport=[]
    for n in range(3):
        try:
            (obj,sha)=request_month_original_RWS(month)
            return (obj,sha),{'original_same_2018_RWS_month_attempts':n+1,
                   'original_RWS_transport_failures_before_success':transport}
        except (OfficialRWSStop,NativeSourceStop,TimeoutError,OSError) as e:
            v=str(e)
            if not any(x in v for x in ('SOURCE_UNAVAILABLE_OR_RATE_LIMITED',
                  'HTTP Error 429','HTTP Error 502','HTTP Error 503',
                  'HTTP Error 504','timed out','TimeoutError')):
                raise
            transport.append({'2018_original_month':month,'attempt':n+1,
                  'original_provider_transport_only':v[:160]})
            if n==2:raise
            sleeper(3*(n+1))
    raise AssertionError('unreachable')

def original_2018_vlieland_fourmonth_measured_tide(request_fn=exact_original_RWS_transport_retry):
    readings={};provenance=[]
    for month in MONTHS:
        (source,sha),transport=request_fn(month)
        row,proof=parse_true_original_RWS_2018_month(month,source)
        for t,v in row.items():
            if t in readings and abs(readings[t]-v)>1e-8:
                raise NativeSourceStop('SOURCE_STOP_2018_RWS_JUNE_SEPT_NATIVE_MONTH_OVERLAP_CONFLICT')
            readings[t]=v
        provenance.append({**proof,'native_RWS_response_SHA256':sha,
                           'source_original_transport_only':transport})
        print('V129_TRUE_VLIELAND_2018_RWS_MONTH '+json.dumps({
           'month':month,'real_2018_10min_n':proof['original_2018_native_observed_10minute_time_count'],
           'coverage':proof['original_2018_native_RWS_valid_fraction']},sort_keys=True),flush=True)
    return readings,{'2018_native_RWS_station':'vlieland.haven',
       'source_status':'TRUE_ORIGINAL_2018_VLIELAND_HAVEN_MEASURED_FOURMONTH_TIDE_ADMITTED',
       'source_year':YEAR,'native_original_real_RWS_months':provenance,
       'total_distinct_original_10min_2018_RWS_measured_times':len(readings),
       'NO_RWS_native_water_values_exported':True,
       'source_harbour_tide_NOT_local_2018_bird_h_x_t':True}
