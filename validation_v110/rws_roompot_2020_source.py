"""v110 genuine RWS DDAPI2 2020 Roompot Buiten/Binnen source ADMISSION ONLY.
Original DELTATRACK 2020 independent gull GPS already source-supported in v109.
No behavior, tide×sun interaction, coastal foraging or GPS/tide joined here.
"""
from __future__ import annotations
from datetime import datetime,timedelta,timezone
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json,argparse,math,re
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError

RWS_ROOT="https://ddapi20-waterwebservices.rijkswaterstaat.nl"
META_ROUTE="/METADATASERVICES/OphalenCatalogus"
DATA_ROUTE="/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
PERIOD=("2020-06-01T00:00:00.000+01:00","2020-06-03T00:00:00.000+01:00")
MIN_MEASUREMENTS_48H=200
PSMSL_OUTSIDE_FIXED=(51.619722,3.681944)
GEOGRAPHY="Neeltje Jans at the Roompot storm surge barrier; out/in water bodies differ"
NATIVE_META={"Compartiment":{"Code":"OW"},"Grootheid":{"Code":"WATHTE"},"ProcesType":"meting"}
MAX_SOURCE_BYTES=10_000_000

class SourceStop(Exception):pass

def publisher_post(path,data):
    if path not in (META_ROUTE,DATA_ROUTE):raise ValueError("STOP_NON_AUTHENTICATED_OFFICIAL_RWS_SOURCE_ENDPOINT")
    request=Request(RWS_ROOT+path,data=json.dumps(data).encode(),method='POST',
          headers={'Content-Type':'application/json','Accept':'application/json',
                   'User-Agent':'boids-v110-2020-original-RWS-Roompot-gauge-source-only/1.0'})
    try:
        with urlopen(request,timeout=55) as r:
            raw=r.read(MAX_SOURCE_BYTES+1)
        if len(raw)>MAX_SOURCE_BYTES:raise SourceStop('STOP_ORIGINAL_RWS_RESPONSE_TOO_LARGE')
        return json.loads(raw),sha256(raw).hexdigest()
    except (HTTPError,URLError,TimeoutError) as e:
        raise SourceStop('SOURCE_UNAVAILABLE_OR_RATE_LIMITED_OFFICIAL_RWS_'+str(e)[:160]) from e
    except json.JSONDecodeError as e:
        raise SourceStop('SOURCE_STOP_ORIGINAL_RWS_RESPONSE_NOT_JSON') from e

def native_roompot_stations(catalog):
    if catalog.get('Succesvol') is False:raise SourceStop('STOP_ORIGINAL_RWS_CATALOGUE_EXPLICIT_ERROR')
    allstations=catalog.get('LocatieLijst') or []
    if not isinstance(allstations,list) or len(allstations)<50:
        raise SourceStop('STOP_ORIGINAL_RWS_CATALOGUE_UNEXPECTED_STATION_LIST')
    result=[]
    for item in allstations:
        n=str(item.get('Naam') or '')
        code=str(item.get('Code') or '')
        key=(n+' '+code).lower()
        if 'roompot' not in key:continue
        result.append({'native_RWS_station_code':code,
            'original_RWS_station_name':n,
            'coordinate_system_original':item.get('Coordinatenstelsel'),
            'has_original_location_coordinates':bool(item.get('X') and item.get('Y'))})
    return sorted(result,key=lambda x:x['native_RWS_station_code'])

def prespecified_probes(roompot):
    # Fixed BEFORE any actual height values: include only native 'roompot'
    # stations whose literal official name/code distinguishes outside or inside.
    outside=[]
    inside=[]
    for x in roompot:
        key=(x['original_RWS_station_name']+' '+x['native_RWS_station_code']).lower()
        normalized=re.sub(r'[^a-z]','',key)
        if not (('roompot' in normalized) and ('buiten' in normalized or 'bui' in normalized
                                          or 'binnen' in normalized or 'bin' in normalized)):
            continue
        if 'buiten' in normalized or 'bui' in normalized:outside.append(x)
        if 'binnen' in normalized or 'bin' in normalized:inside.append(x)
    return {'primary_outside_station_source_candidates':outside,
            'secondary_inside_station_source_candidates':inside}

def probe_original_gauge(source_code):
    payload={'Locatie':{'Code':source_code},
          'AquoPlusWaarnemingMetadata':{'AquoMetadata':NATIVE_META},
          'Periode':{'Begindatumtijd':PERIOD[0],'Einddatumtijd':PERIOD[1]}}
    obj,originsha=publisher_post(DATA_ROUTE,payload)
    if obj.get('Succesvol') is not True:
        return {'source_status':'SOURCE_NOT_AVAILABLE_OFFICIAL_EXPLICIT_RWS_REJECTION',
                'original_response_sha256':originsha}
    byseries=[]
    valid_times={}
    invalid=Counter()
    for series in obj.get('WaarnemingenLijst') or []:
        m=series.get('AquoMetadata') or {}
        if (m.get('Grootheid') or {}).get('Code')!='WATHTE':
            invalid['not_WATHTE']+=1;continue
        unit=(m.get('Eenheid') or {}).get('Code')
        datum=(m.get('Hoedanigheid') or {}).get('Code')
        if unit!='cm' or datum!='NAP':
            invalid['not_verified_cm_NAP']+=1;continue
        for record in series.get('MetingenLijst') or []:
            try:
                ts=datetime.fromisoformat(record['Tijdstip'].replace('Z','+00:00'))
                if ts.utcoffset()!=timedelta(hours=1):
                    invalid['not_fixed_UTCplus1']+=1;continue
                y=float((record.get('Meetwaarde') or {}).get('Waarde_Numeriek'))
                if not math.isfinite(y) or abs(y)>500:
                    invalid['invalid_original_water_level_value']+=1;continue
                original=ts.astimezone(timezone.utc)
                if original in valid_times and abs(valid_times[original]-y)>1e-8:
                    raise ValueError('STOP_CONFLICTING_ORIGINAL_GAUGE_OBSERVATION')
                valid_times[original]=y
            except (KeyError,TypeError,ValueError) as e:
                if str(e)=='STOP_CONFLICTING_ORIGINAL_GAUGE_OBSERVATION':raise
                invalid['native_measurement_decode']+=1
        byseries.append({'source_original_WATHTE_unit':unit,'source_original_datum':datum,
              'n_raw_native_readings':len(series.get('MetingenLijst') or [])})
    timestamps=sorted(valid_times)
    if len(valid_times)<MIN_MEASUREMENTS_48H:status='NOT_ADMITTED_2020_RWS_NATIVE_PILOT_SOURCE_TOO_FEW_TRUE_MEASUREMENTS'
    else:status='ORIGINAL_2020_RWS_ROOMPO_GAUGE_10MIN_NAP_MEASURED_SOURCE_ADMITTED'
    gaps=[(b-a).total_seconds()/60 for a,b in zip(timestamps,timestamps[1:])]
    return {'source_status':status,'original_response_SHA256':originsha,
       'original_n_unique_true_observed_timestamps':len(timestamps),
       'original_first_UTC':timestamps[0].isoformat() if timestamps else None,
       'original_last_UTC':timestamps[-1].isoformat() if timestamps else None,
       'original_gauge_time_gap_minutes_max':max(gaps) if gaps else None,
       'original_verified_native_NAP_cm_series':byseries,
       'rejected_source_measured_records':dict(invalid),
       'no_original_tide_array_or_bird_positions_exported':True}
def run(path):
    results={'analysis':'V110_OFFICIAL_RWS_ROOMPOT_2020_TRUE_WATHTE_TIDAL_GAUGE_SOURCE_FIRST',
        'official_endpoint':RWS_ROOT,'probe_original_publisher_2020_period':PERIOD,
        'outside_Roompot_PSMLS_reference_latlon':PSMSL_OUTSIDE_FIXED,
        'gull_2020_native_original_GPS_source_from_prior_v109':42746796941,
        'NO_actual_tide_gull_daynight_or_habitat_effect':True,
        'source_status':'SOURCE_UNAVAILABLE'}
    try:
        cat,sha=publisher_post(META_ROUTE,{'CatalogusFilter':{
             'Grootheden':True,'Eenheden':True,'Compartimenten':True}})
        roompot=native_roompot_stations(cat)
        source=prespecified_probes(roompot)
        results['original_metadata_SHA256']=sha
        results['all_original_RWS_roompot_station_names']=roompot
        results['original_external_barrier_source_candidate_selection']=source
        if len(source['primary_outside_station_source_candidates'])==0:
            raise SourceStop('STOP_NO_EXACT_ROOMPOT_BUITEN_IN_ORIGINAL_GAUGE_CATALOGUE')
        results['source_probe_2020_true_observed_48h']={}
        for site_group in ('primary_outside_station_source_candidates','secondary_inside_station_source_candidates'):
            for v in source[site_group][:3]:
                try:
                    result=probe_original_gauge(v['native_RWS_station_code'])
                except SourceStop as e:
                    result={'source_status':'SOURCE_TRANSPORT_BLOCKED','reason':str(e)}
                results['source_probe_2020_true_observed_48h'][v['native_RWS_station_code']]={
                    'identity':v,**result}
        n_admitted=sum(v.get('source_status')=='ORIGINAL_2020_RWS_ROOMPO_GAUGE_10MIN_NAP_MEASURED_SOURCE_ADMITTED' for v in results['source_probe_2020_true_observed_48h'].values())
        results['source_status']='ORIGINAL_RWS_ROOMPOT_2020_TIDE_PILOT_ADMITTED' if n_admitted else 'ORIGINAL_RWS_CATALOGUE_ONLY_NO_MEASURED_TIDE_PILOT'
    except (SourceStop,ValueError) as e:
        results['source_status']='SOURCE_STOP_ORIGINAL_ROOMPOT_GAUGE'
        results['source_failure']=str(e)
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(results,sort_keys=True,indent=2)+'\n')
    print('V110_TRUE_RWS_ROOMPOT_2020_TIDE_METADATA '+json.dumps({
        'source_status':results['source_status'],
        'original_RWS_roompot_stations':results.get('all_original_RWS_roompot_station_names'),
        'authentic_2020_measured_pilot':results.get('source_probe_2020_true_observed_48h'),
        'blocker':results.get('source_failure'),
        'NO_2020_GULL_BEHAVIOR_ANALYSIS':True},sort_keys=True),flush=True)
    return results
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    run(p.parse_args().output)
