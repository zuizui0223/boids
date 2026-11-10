"""v97: 2018 UHSLC real hourly water-level × astronomical solar opportunity.
TEST YEAR = 2018, fixed before reading any 2018 native source rows.
Candidate station IDs and 2019 datum version are selected purely from source-eligible
2019 v94 original station results. This is a different YEAR, not new animals.
No interpretation of station Q25 as actual coastal intertidal mudflat exposure.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
from hashlib import sha256
from statistics import mean
import argparse,csv,io,json,math,calendar,time
import numpy as np
from astral import Observer
from astral.sun import elevation
TEST_YEAR=2018
TEST_START=datetime(2018,1,1,tzinfo=timezone.utc)
TEST_END=datetime(2019,1,1,tzinfo=timezone.utc)
EXPECTED_HOURS=8760
SOURCE_RUN_V94=42616065580
MIN_YEAR_COVERAGE=.8
MIN_MONTH_COVERAGE=.8
MAX_MISSING_GAP=72
MIN_VALID_DAYS_FOR_OUTCOME=120
DAY_ALT_DEG=3
from real_global_UHSLC_hourly_station_manifest import PROVIDERS
def source_uri(base,uid):
    if base not in [x[1] for x in PROVIDERS]:
        raise ValueError('STOP_UNAUTHORIZED_RESEARCH_QUALITY_DATA_ENDPOINT')
    return (base+'.csv?uhslc_id,record_id,time,sea_level,quality'
       +f'&uhslc_id={uid}&time%3E=2018-01-01T00:00:00Z'
       +'&time%3C=2019-01-01T00:00:00Z')
def fetch_source(base,uid,timeout=25):
    with urlopen(Request(source_uri(base,uid),headers={
         'User-Agent':'boids-v97-real-2018-UHSLC-hourly-independent-year-physical/1.0',
         'Accept':'text/csv'}),timeout=timeout) as response:
        raw=response.read(8_000_001)
        if response.status!=200 or len(raw)>8_000_000:raise ValueError('2018_SOURCE_RESPONSE_INVALID')
        return raw
def parse_real_2018(raw,uid,record_id):
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig',errors='strict')))
    if not {'uhslc_id','record_id','time','sea_level','quality'} <= set(reader.fieldnames or []):
        raise ValueError('2018_REAL_UHSLC_SCHEMA_DRIFT')
    original={}
    for r in reader:
        try:
            if int(r['uhslc_id'])!=uid or int(r['record_id'])!=record_id or int(r['quality'])!=4:
                continue
            utc=datetime.fromisoformat(r['time'].replace('Z','+00:00'))
            x=float(r['sea_level'])
            off=(utc-TEST_START).total_seconds()/3600
            if not (utc.tzinfo is not None and 0<=off<EXPECTED_HOURS and off==int(off)
                    and math.isfinite(x) and x!=-32767):continue
            i=int(off)
            if i in original and original[i]!=x:raise ValueError('STOP_2018_ORIGINAL_HOURLY_DUPLICATE_CONFLICT')
            original[i]=x
        except (ValueError,TypeError) as e:
            if str(e).startswith('STOP_2018_ORIGINAL_HOURLY_DUPLICATE_CONFLICT'):raise
            continue
    return original
def quality_admitted(data):
    if len(data)<MIN_YEAR_COVERAGE*EXPECTED_HOURS:
        return False,'2018_YEAR_COVERAGE_LT80PCT'
    month=Counter((TEST_START+timedelta(hours=h)).month for h in data)
    if any(month.get(m,0)<MIN_MONTH_COVERAGE*24*calendar.monthrange(TEST_YEAR,m)[1]
           for m in range(1,13)):
        return False,'2018_MONTH_SOURCE_COVERAGE_LT80PCT'
    hs=sorted(data)
    gap=max([hs[0],EXPECTED_HOURS-1-hs[-1]]+[b-a-1 for a,b in zip(hs,hs[1:])])
    if gap>MAX_MISSING_GAP:return False,'2018_CONTINUOUS_SOURCE_GAP_GT72H'
    return True,gap
def score_2018_real_tide_sun(data,lat,lon):
    real=np.array([data[h] for h in data],dtype=float)
    q25=float(np.quantile(real,.25))
    observer=Observer(latitude=float(lat),longitude=float(lon),elevation=0)
    local_solar_time_delta=timedelta(hours=float(lon)/15.)
    day=defaultdict(Counter); totals=Counter()
    for h,lev in sorted(data.items()):
        utc=TEST_START+timedelta(hours=h)
        light=elevation(observer,utc)
        low=lev<=q25
        item={'observed':1,'low':int(low),'light':int(light>DAY_ALT_DEG),
              'dark':int(light< -DAY_ALT_DEG),
              'low_light':int(low and light>DAY_ALT_DEG)}
        key=(utc+local_solar_time_delta).date().isoformat()
        for name,val in item.items():
            day[key][name]+=val; totals[name]+=val
    eligible=[]
    for key,d in sorted(day.items()):
        if d['observed']<19 or d['low']<2:continue
        eligible.append({'date':key,'M':d['low_light']/d['low']-d['light']/d['observed'],
                         'low_light_hours':d['low_light'],'low_hour_n':d['low']})
    if len(eligible)<MIN_VALID_DAYS_FOR_OUTCOME:
        return {'status':'NOT_ENOUGH_SOURCE_LOW_HOURS','n_valid_days':len(eligible)}
    return {'status':'VALID_2018_ORIGINAL_DAILY_TIDE_SOLAR_OPPORTUNITY',
        '2018_Q25_original_station_datum_mm':q25,
        '2018_source_valid_hours':len(data),
        '2018_n_source_lowwater_day_records':len(eligible),
        '2018_mean_daily_abs_M':float(mean(abs(v['M']) for v in eligible)),
        '2018_mean_daily_signed_M':float(mean(v['M'] for v in eligible)),
        '2018_fraction_abs_M_at_least_025':float(mean(abs(v['M'])>=.25 for v in eligible)),
        '2018_light_low_gauge_hours':totals['low_light'],
        '2018_low_gauge_hours':totals['low']}
def run(v94_original_band_json,band,output):
    d=json.loads(Path(v94_original_band_json).read_text())
    if d.get('band')!=band or d.get('year')!=2019 or d.get('analysis')!='V94_ALL_STATIONS_2019_ORIGINAL_UHSLC_HOURLY_TIDE_SOLAR_PHYSICAL':
        raise ValueError('STOP_V97_2019_SOURCE_FRAME_DRIFT')
    frame=d['raw_station_outcomes']
    out={'analysis':'V97_INDEPENDENT_2018_UHSLC_TIDE_SOLAR_ORIGINAL_HOURLY_HOLDOUT',
         'original_2019_selection_artifact_run':SOURCE_RUN_V94,
         'year':TEST_YEAR,'band':band,'original_preselected_2019_source_eligible_site_n':len(frame),
         'site_outputs':[],'source_failures':[],'source_quality_not_admitted':[],
         '2018_results_MUST_NOT_BE_USED_FOR_2019_MODEL_FIT':True}
    for site in sorted(frame,key=lambda x:x['uid']):
        uid=site['uid'];rid=site['record_id'];accepted=None;attempts=[]
        for label,base in PROVIDERS:
            # fixed source provenance; mirror only if provider transport fails.
            for tries in range(2):
                try:
                    raw=fetch_source(base,uid)
                    parsed=parse_real_2018(raw,uid,rid)
                    good,reason=quality_admitted(parsed)
                    if not good:
                        out['source_quality_not_admitted'].append({'id':uid,'2019_record_id':rid,'reason':reason})
                    else:
                        score=score_2018_real_tide_sun(parsed,site['latitude'],site['longitude_signed'])
                        if score['status'].startswith('VALID_'):
                            accepted={'uid':uid,'2019_record_id':rid,
                                'latitude':site['latitude'],'longitude_signed':site['longitude_signed'],
                                'country':site['country'],'2019_regime':site['regime'],
                                '2019_form_factor_F':site['form_factor_F'],
                                '2019_amp_4const_mm':sum(site['harmonics_mm'].values()),
                                '2019_mean_daily_abs_M_SOURCE_ONLY':site['opportunity']['mean_daily_abs_M'],
                                '2018_hourly_real_provider':label,'2018_original_csv_sha256':sha256(raw).hexdigest(),
                                '2018_physical':score}
                        else:out['source_quality_not_admitted'].append({'id':uid,'reason':score['status']})
                    break
                except HTTPError as e:
                    attempts.append({'provider':label,'code':e.code,'try':tries})
                    if e.code==404: break
                except (URLError,OSError,TimeoutError,ValueError) as e:
                    attempts.append({'provider':label,'error':str(e)[:130],'try':tries})
                if tries==0:time.sleep(1)
            if accepted or (any(x['id']==uid for x in out['source_quality_not_admitted'])):break
        if accepted is None and not any(x['id']==uid for x in out['source_quality_not_admitted']):
            out['source_failures'].append({'id':uid,'attempts':attempts})
        elif accepted is not None:
            out['site_outputs'].append(accepted)
            print('V97_REAL_2018_SITE '+json.dumps({'band':band,'uid':uid,
              'absM2018':accepted['2018_physical']['2018_mean_daily_abs_M'],
              'absM2019':accepted['2019_mean_daily_abs_M_SOURCE_ONLY'],
              'real_hours':accepted['2018_physical']['2018_source_valid_hours']},sort_keys=True),flush=True)
    out['summary']={'2019_original_source_site_n':len(frame),
       '2018_original_hourly_qualified_site_n':len(out['site_outputs']),
       '2018_qc_failed_count':len(out['source_quality_not_admitted']),
       '2018_transport_or_provider_failed_count':len(out['source_failures'])}
    if sum(out['summary'].values())<0:raise AssertionError('never')
    if len(frame)!=(len(out['site_outputs'])+len(out['source_quality_not_admitted'])+len(out['source_failures'])):
        raise ValueError('STOP_2018_ORIGINAL_SOURCE_COUNTS_NOT_EXHAUSTIVE')
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print('V97_ORIGINAL_2018_BAND_FINAL '+json.dumps({'band':band,'summary':out['summary']},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--v94-band-2019-json',required=True)
    p.add_argument('--band',required=True)
    p.add_argument('--output',required=True)
    x=p.parse_args();run(x.v94_band_2019_json,x.band,x.output)
