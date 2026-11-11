"""v126 official RWS 2019 Vlieland Haven 48-hour measured NAP tide
source-only pilot, before native 2019 Vlieland forage/inactive behavioural Y.
No astronomical predicted tide, fixed solar results or proxy h(x,t) inferred.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime,timedelta,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,math,re
from rws_roompot_2020_source import (
    publisher_post,META_ROUTE,DATA_ROUTE,NATIVE_META,SourceStop)

STATION_CODE='vlieland.haven'
STATION_STRING='Vlieland haven'
START='2019-06-01T00:00:00.000+01:00'
END='2019-06-03T00:00:00.000+01:00'
MIN_AUTHENTIC_NATIVE_10MIN_N=200
ORIGINAL_SOURCE_YEAR=2019

def validate_original_vlieland_station_catalogue(obj):
    if obj.get('Succesvol') is False:raise SourceStop('SOURCE_STOP_ORIGINAL_RWS_CATALOGUE_REJECTED')
    stations=obj.get('LocatieLijst') or []
    if not isinstance(stations,list) or len(stations)<50:
        raise SourceStop('SOURCE_STOP_OFFICIAL_RWS_LOCATION_CATALOG_TOO_SMALL')
    possible=[x for x in stations if ('vlieland' in (
        str(x.get('Naam') or '')+' '+str(x.get('Code') or '')).lower())]
    exact=[x for x in possible if str(x.get('Code') or '').lower()==STATION_CODE]
    if len(exact)!=1:raise SourceStop('SOURCE_STOP_OFFICIAL_VLIELAND_HAVEN_EXACT_CODE_NOT_FOUND')
    original=exact[0]
    if 'vlieland' not in str(original.get('Naam') or '').lower():
        raise SourceStop('SOURCE_STOP_OFFICIAL_VLIELAND_HAVEN_NAME_CODE_DISAGREE')
    return {'original_native_RWS_station_code':original['Code'],
         'original_publisher_name':original['Naam'],
         'source_WGS84_geography_from_nonofficial_published_station':(53.30,5.09),
         'original_coordinate_system_in_RWS_catalogue':original.get('Coordinatenstelsel'),
         'original_catalogue_location_X_Y_source_present':original.get('X') is not None and original.get('Y') is not None,
         'source_gauge_at_harbour_NOT_same_tide_every_bird_forage_position':True,
         'other_vlieland_stations_not_chosen_by_effect_n':len(possible)-1}

def original_2019_vlieland_haven_gauge_48h():
    request={'Locatie':{'Code':STATION_CODE},
         'AquoPlusWaarnemingMetadata':{'AquoMetadata':NATIVE_META},
         'Periode':{'Begindatumtijd':START,'Einddatumtijd':END}}
    obj,original_SHA=publisher_post(DATA_ROUTE,request)
    if obj.get('Succesvol') is not True:
        raise SourceStop('SOURCE_STOP_ORIGINAL_2019_RWS_WATERHEIGHT_PUBLISHER_REJECTION')
    native={}
    qa=Counter()
    n_raw=0
    for series in obj.get('WaarnemingenLijst') or []:
        aq=series.get('AquoMetadata') or {}
        if (aq.get('Grootheid') or {}).get('Code')!='WATHTE' or (
             (aq.get('Eenheid') or {}).get('Code')!='cm') or (
             (aq.get('Hoedanigheid') or {}).get('Code')!='NAP'):
            qa['wrong_native_water_height_unit_or_datum']+=1;continue
        for record in series.get('MetingenLijst') or []:
            n_raw+=1
            try:
                stamp=datetime.fromisoformat(record['Tijdstip'].replace('Z','+00:00'))
                value=float((record.get('Meetwaarde') or {}).get('Waarde_Numeriek'))
            except (KeyError,TypeError,ValueError):
                qa['unparsed_native_observation']+=1;continue
            if stamp.utcoffset()!=timedelta(hours=1):
                qa['native_RWS_UTC_plus1_clock_not_verified']+=1;continue
            if not math.isfinite(value) or abs(value)>500:
                qa['implausible_or_missing_cm_NAP']+=1;continue
            utc=stamp.astimezone(timezone.utc)
            if utc in native and abs(native[utc]-value/100)>1e-8:
                raise SourceStop('SOURCE_STOP_CONTRADICTORY_REAL_RWS_VLIELAND_HAVEN_2019_HEIGHTS')
            native[utc]=value/100
    if len(native)<MIN_AUTHENTIC_NATIVE_10MIN_N:
        raise SourceStop('SOURCE_STOP_NOT_200_GENUINE_2019_VLIELAND_HAVEN_10MIN_NAP_MEASUREMENTS')
    times=sorted(native)
    gaps=[(b-a).total_seconds()/60 for a,b in zip(times,times[1:])]
    return {'source_status':'REAL_OFFICIAL_RWS_2019_VLIELAND_HAVEN_10MIN_WATHTE_cmNAP_SOURCE_ADMITTED',
      'original_publisher_JSON_SHA256':original_SHA,
      'native_original_2019_waterheight_observed_10min_n':len(native),
      'original_2019_native_first_UTC':times[0].isoformat(),
      'original_2019_native_last_UTC':times[-1].isoformat(),
      'source_original_10min_interval_max_gap_minutes':max(gaps) if gaps else None,
      'native_original_cm_NAP_gauge_mNAPA_minmax':[float(min(native.values())),float(max(native.values()))],
      'source_n_original_reported_rows':n_raw,
      'original_native_rejected_source_counts':dict(qa),
      'NO_forage_OR_SUN_OR_INDIVIDUAL_GPS_effect_scored':True}

def run(path):
    out={'analysis':'V126_RWS_2019_ORIGINAL_VLIELAND_HAVEN_JUNE_48H_TRUE_MEASURED_TIDAL_SOURCE',
         'source_status':'SOURCE_PENDING',
         'native_source_station_locked_before_2019_true_waterlevels':STATION_CODE,
         'original_time_period_locked':{'start':START,'end':END},
         'no_local_h_x_t_at_bird_used_forage_flat_measured':True}
    try:
        catalogue,sourceSHA=publisher_post(META_ROUTE,{
           'CatalogusFilter':{'Grootheden':True,'Eenheden':True,'Compartimenten':True}})
        info=validate_original_vlieland_station_catalogue(catalogue)
        out['original_official_RWS_catalogue_metadata_SHA256']=sourceSHA
        out['original_publisher_RWS_station_identity']=info
        measured=original_2019_vlieland_haven_gauge_48h()
        out['original_2019_true_tide_source_quality']=measured
        out['source_status']='ORIGINAL_RWS_2019_VLIELAND_HAVEN_MEASURED_TIDE_SOURCE_ADMITTED'
    except (SourceStop,ValueError,TimeoutError,OSError) as e:
        out['source_status']='SOURCE_STOP_NATIVE_2019_VLIELAND_HAVEN_RWS'
        out['source_blocker']=str(e)[:240]
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(out,sort_keys=True,indent=2,allow_nan=False)+'\n')
    print('V126_REAL_RWS_2019_VLIELAND_HAVEN_SOURCE_FINAL '+json.dumps({
        'status':out['source_status'],
        'original_RWS_station':out.get('original_publisher_RWS_station_identity'),
        '2019_real_original_NAP_height_source':out.get('original_2019_true_tide_source_quality'),
        'official_source_blocker':out.get('source_blocker'),
        'no_time_niche_biology_estimated':True},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
