"""v92 first ORIGINAL 2019 UHSLC hourly tide × solar physical pilot.
This is environmental opportunity, NOT an animal-activity observation.
Predeclared one lowest-ID quality-eligible station / 15 degree hemisphere band.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import csv, io, json, math, calendar
import numpy as np
from astral import Observer
from astral.sun import elevation
from real_global_UHSLC_hourly_station_manifest import (
    PROVIDERS, source_URL, _download, parse_original_station_manifest, _latitude_band)
YEAR=2019
START=datetime(2019,1,1,tzinfo=timezone.utc)
END=datetime(2020,1,1,tzinfo=timezone.utc)
N=8760
MAX_CANDIDATES=8
PERIODS={'M2':12.4206012,'S2':12.,'K1':23.93447213,'O1':25.81933871}
def native_hourly(base,uid):
    url=(base+'.csv?uhslc_id,record_id,time,sea_level,quality'
        +f'&uhslc_id={uid}&time%3E=2019-01-01T00:00:00Z'
        +'&time%3C=2020-01-01T00:00:00Z')
    with urlopen(Request(url,headers={'User-Agent':'boids-v92-2019-original-RQDS-physical-pilot/1.0'}),timeout=55) as r:
        data=r.read(8_000_001)
        if r.status!=200 or len(data)>8_000_000:raise ValueError('hourly source error/too large')
        return data
def parse_native(raw,uid):
    d=defaultdict(dict)
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    if not {'uhslc_id','record_id','time','sea_level','quality'}<=set(reader.fieldnames or []):
        raise ValueError('native hourly columns missing')
    for row in reader:
        try:
            if int(row['uhslc_id'])!=uid or int(row['quality'])!=4:continue
            rec=int(row['record_id'])
            ts=datetime.fromisoformat(row['time'].replace('Z','+00:00'))
            lvl=float(row['sea_level'])
            offset=(ts-START).total_seconds()/3600
            if not 0<=offset<N or offset!=int(offset) or not math.isfinite(lvl) or lvl==-32767:continue
            h=int(offset)
            if h in d[rec] and d[rec][h]!=lvl:raise ValueError('conflicting source hourly duplicate')
            d[rec][h]=lvl
        except (TypeError,OverflowError):continue
        except ValueError as e:
            if str(e)=='conflicting source hourly duplicate':raise
            continue
    return d
def choose_original_segment(recmap,allowed_records):
    candidates=[]
    for rec,d in recmap.items():
        if rec not in allowed_records or len(d)<.8*N:continue
        months=Counter((START+timedelta(hours=h)).month for h in d)
        if any(months.get(m,0)<.8*24*calendar.monthrange(YEAR,m)[1] for m in range(1,13)):continue
        hh=sorted(d)
        max_missing=max([hh[0],N-1-hh[-1]]+[b-a-1 for a,b in zip(hh,hh[1:])])
        if max_missing>72:continue
        candidates.append((-len(d),rec,max_missing))
    if not candidates:return None
    _,rec,gap=min(candidates)
    return rec,recmap[rec],gap
def harmonic_form(data):
    hh=np.array(sorted(data),dtype=float)
    yy=np.array([data[int(h)] for h in hh],dtype=float)
    cols=[np.ones(len(hh)),(hh-hh.mean())/N]
    for period in PERIODS.values():
        theta=2*np.pi*hh/period
        cols.extend([np.sin(theta),np.cos(theta)])
    x=np.column_stack(cols)
    coef=np.linalg.lstsq(x,yy,rcond=None)[0]
    a={key:float(np.hypot(coef[2+2*j],coef[3+2*j])) for j,key in enumerate(PERIODS)}
    f=(a['K1']+a['O1'])/max(1.e-9,a['M2']+a['S2'])
    return {'constituents_amplitude_mm':a,'F':float(f),
        'regime':('semidiurnal' if f<.25 else 'mixed_semidiurnal' if f<1.5
                  else 'mixed_diurnal' if f<3 else 'diurnal'),
        'four_constituent_R2':float(1-np.var(yy-x@coef)/np.var(yy))}
def opportunity(data,lat,lon):
    observer=Observer(latitude=lat,longitude=lon,elevation=0)
    q=float(np.quantile(list(data.values()),.25))
    daily=defaultdict(lambda:Counter())
    monthly=defaultdict(lambda:Counter())
    total=Counter()
    shift=timedelta(hours=lon/15.)
    for hour,level in sorted(data.items()):
        when=START+timedelta(hours=hour)
        day=(when+shift).date().isoformat()
        sun=elevation(observer,when)
        indicators={'observed':1,'low':int(level<=q),'light':int(sun>3),
                    'dark':int(sun< -3),'twilight':int(-3<=sun<=3),
                    'low_light':int(level<=q and sun>3),
                    'low_dark':int(level<=q and sun< -3)}
        for bucket in (daily[day],monthly[when.month],total):
            bucket.update(indicators)
    valid=[]
    for date,r in sorted(daily.items()):
        if r['observed']<19 or r['low']<2:continue
        frac=r['low_light']/r['low'];base=r['light']/r['observed']
        valid.append({'date':date,'O':frac,'A':base,'M':frac-base,
                      'joint_original_hours':r['low_light']})
    if len(valid)<200:raise ValueError('too few well-observed source low-water days')
    dif=np.array([x['M'] for x in valid])
    return {'source_hours':len(data),'year_hour_coverage':len(data)/N,
       'Q25_original_mm':q,'sunlit_low_hours':total['low_light'],
       'dark_low_hours':total['low_dark'],'twilight_total_hours':total['twilight'],
       'annual_O':total['low_light']/total['low'],
       'annual_A':total['light']/total['observed'],
       'annual_M':total['low_light']/total['low']-total['light']/total['observed'],
       'n_valid_days':len(valid),
       'daily_mean_abs_M':float(np.mean(np.abs(dif))),
       'daily_sd_M':float(np.std(dif)),
       'fraction_valid_days_abs_M_at_least_025':float(np.mean(np.abs(dif)>=.25)),
       'daily_joint_hours_p10_p50_p90':np.quantile([x['joint_original_hours'] for x in valid],[.1,.5,.9]).tolist(),
       'monthly':{str(m):{'observed':r['observed'],'low':r['low'],'light':r['light'],
           'low_light':r['low_light'],'O_minus_A':r['low_light']/r['low']-r['light']/r['observed'] if r['low'] else None}
           for m,r in sorted(monthly.items())},
       'daily':valid}
def run(path):
    out={'analysis':'v92_original_2019_global_UHSLC_hourly_tide_solar_physical_only',
         'tide_low_definition':'station-year actual native source sea level <= Q25',
         'day':'solar_elevation_gt_3_degrees','night':'solar_elevation_lt_minus_3_degrees',
         'year':YEAR,'year_coverage_min':.8,'each_month_coverage_min':.8,
         'longest_gap_max_hours':72,'max_source_candidates_per_lat_band':MAX_CANDIDATES,
         'outcome_type':'PUBLIC_ENVIRONMENT_ONLY_NO_ORGANISM_ACTIVITY_OR_DRY_MUDFLAT',
         'sites':{},'errors':{}}
    source=None
    for provider,base in PROVIDERS:
        try:
            raw=_download(source_URL(base))
            records,skipped=parse_original_station_manifest(raw)
            if len({r['uhslc_id'] for r in records})<30:raise ValueError('manifest too small')
            source=(provider,records)
            out['source']={'provider':provider,'manifest_SHA256':sha256(raw).hexdigest(),
                           'station_ids':len({r['uhslc_id'] for r in records}),
                           'record_versions':len(records)}
            break
        except Exception as e:out['errors']['manifest_'+provider]=str(e)[:170]
    if source:
        groups=defaultdict(lambda:defaultdict(list))
        for r in source[1]:groups[_latitude_band(r['latitude'])][r['uhslc_id']].append(r)
        for band,station_map in sorted(groups.items()):
            selected=None;failures=[]
            for uid in sorted(station_map)[:MAX_CANDIDATES]:
                m=station_map[uid][0]
                for provider,base in PROVIDERS:
                    try:
                        raw=native_hourly(base,uid)
                        seg=choose_original_segment(parse_native(raw,uid),{r['record_id'] for r in station_map[uid]})
                        if seg is None:
                            failures.append({'id':uid,'reason':'2019 source coverage insufficient'})
                            break  # don't use alternate copy to cherry-pick a station
                        rec,data,gap=seg
                        phy=opportunity(data,m['latitude'],m['longitude_signed'])
                        harm=harmonic_form(data)
                        selected={'uid':uid,'record_id':rec,'station':m['original_station_name'],
                                  'country':m['original_station_country'],'latitude':m['latitude'],
                                  'longitude':m['longitude_signed'],'max_gap':gap,
                                  'hourly_provider':provider,'source_SHA256':sha256(raw).hexdigest(),
                                  'physical':phy,'harmonics':harm}
                        break
                    except (ValueError,HTTPError,URLError,TimeoutError) as e:
                        failures.append({'id':uid,'provider':provider,'error':str(e)[:110]})
                if selected:break
            out['sites'][band]={'selected':selected,'source_failures':failures}
            if selected:
                p=selected['physical'];h=selected['harmonics']
                print('V92_OBSERVED_SITE '+json.dumps({'band':band,'uid':selected['uid'],
                   'country':selected['country'],'lat':selected['latitude'],
                   'hours':p['source_hours'],'n_days':p['n_valid_days'],
                   'daily_abs_M':round(p['daily_mean_abs_M'],6),
                   'annual_M':round(p['annual_M'],6),'F':round(h['F'],4),
                   'regime':h['regime']},sort_keys=True),flush=True)
            else:print('V92_SOURCE_STOP_BAND '+band+' '+json.dumps(failures[-3:]),flush=True)
        sites=[v['selected'] for v in out['sites'].values() if v['selected']]
        out['summary']={'eligible_sites':len(sites),'total_bands_with_original_station_metadata':len(groups)}
        if sites:
            xx=[s['physical']['daily_mean_abs_M'] for s in sites]
            out['summary'].update({'station_mean_daily_abs_M':float(np.mean(xx)),
               'station_range_daily_abs_M':[float(min(xx)),float(max(xx))],
               'regimes':dict(Counter(s['harmonics']['regime'] for s in sites)),
               'latitude_abs_M_r_descriptive_only':float(np.corrcoef(
                   [abs(s['latitude']) for s in sites],xx)[0,1]) if len(sites)>2 else None})
        out['status']='OBSERVED_PHYSICAL_PILOT' if len(sites)>=6 else 'PILOT_SOURCE_NOT_ADMITTED_LT6_BANDS'
    else:out['status']='SOURCE_UNAVAILABLE_NO_NEW_GLOBAL_OUTCOME'
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('V92_FINAL '+json.dumps({'status':out['status'],'source':out.get('source'),
      'summary':out.get('summary'),'errors':out['errors']},sort_keys=True),flush=True)
    return out
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--output',required=True)
    run(a.parse_args().output)
