"""v31 exploratory original GPS × measured RWS tide phase validation.

Source: original Zenodo v5 2009 provider-MD5 and RWS DDAPI2 station
Schiermonnikoog Waddenzee WATHTE meting in cm NAP, fixed +01 time.
The original Movebank clock is UTC/GPS ambiguous, provisionally read UTC.
No DEM, prey, causal tidal-front or social force is identified.
"""
from __future__ import annotations
import argparse, csv, gzip, json, math, tempfile
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import numpy as np
from source_preflight import download_and_pin, parse_stamp, haversine_m
from rws_source_probe import post_json, WATHTE
from tidal_front import TideSeries
UTC=timezone.utc
STATION='schiermonnikoog.waddenzee'

def real_rws_tide(year):
    rows={}; receipts=[]
    for m in range(1,13):
        start=datetime(year,m,1)
        stop=datetime(year+1,1,1) if m==12 else datetime(year,m+1,1)
        s=start.strftime('%Y-%m-%dT%H:%M:%S.000+01:00')
        e=stop.strftime('%Y-%m-%dT%H:%M:%S.000+01:00')
        query={'Locatie':{'Code':STATION},
               'AquoPlusWaarnemingMetadata':{'AquoMetadata':dict(WATHTE,ProcesType='meting')},
               'Periode':{'Begindatumtijd':s,'Einddatumtijd':e}}
        response=post_json('/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen',
                           query,max_bytes=15_000_000)
        if response.get('Succesvol') is False:
            raise ValueError(f'RWS historical month {year}-{m:02d} rejected by API')
        count=0
        for series in response.get('WaarnemingenLijst',[]):
            meta=series.get('AquoMetadata') or {}
            if (meta.get('Grootheid') or {}).get('Code')!='WATHTE':continue
            if (meta.get('Eenheid') or {}).get('Code')!='cm':
                raise ValueError('Measured station water unit not cm')
            if (meta.get('Hoedanigheid') or {}).get('Code')!='NAP':
                raise ValueError('Measured station reference not NAP')
            for rec in series.get('MetingenLijst') or []:
                dt=datetime.fromisoformat(rec['Tijdstip'].replace('Z','+00:00'))
                if dt.utcoffset()!=timedelta(hours=1):
                    raise ValueError('Unexpected Dutch gauge offset, no DST allowed')
                value=(rec.get('Meetwaarde') or {}).get('Waarde_Numeriek')
                if value is None:continue
                v=float(value)
                if not math.isfinite(v) or abs(v)>500:continue
                t=dt.astimezone(UTC)
                if t in rows and abs(rows[t]-v/100)>1e-4:
                    raise ValueError('Contradictory duplicate original gauge reading')
                rows[t]=v/100
                count+=1
        receipts.append({'month':f'{year}-{m:02d}','observed_nap_cm_values':count})
    if len(rows)<12000:
        raise ValueError('Insufficient measured local gauge coverage for a full year')
    tide=TideSeries(sorted(rows.items()),datum='NAP_m',provenance='observed')
    return tide,{'station':STATION,'source':'RWS_DDAPI2_measured_WATHTE_NAP_cm',
                 'utc_offset_verified':'+01:00_fixed','gauge_rows':len(rows),
                 'monthly_counts':receipts,
                 'not_verified_same_instrument_as_Dryad':True}

def gps_hourly_steps(gz_path,tide, *,clock_shift_s=0):
    by_bird=defaultdict(dict);raw=visible=0
    with gzip.open(gz_path,'rt',newline='',encoding='utf-8-sig') as stream:
        reader=csv.DictReader(stream)
        needed={'timestamp','location-lat','location-long','individual-local-identifier','visible'}
        if not needed<=set(reader.fieldnames or ()):
            raise ValueError('Original GPS source schema changed')
        for r in reader:
            raw+=1
            if r['visible'].strip().upper() in ('FALSE','0'):continue
            ident=r['individual-local-identifier'].strip()
            if not ident:continue
            t=parse_stamp(r['timestamp']).replace(tzinfo=UTC)+timedelta(seconds=clock_shift_s)
            lat=float(r['location-lat']);lon=float(r['location-long'])
            if not (53.2<=lat<=53.7 and 5.7<=lon<=6.6):continue
            visible+=1
            bucket=t.replace(minute=0,second=0,microsecond=0)
            if bucket not in by_bird[ident] or by_bird[ident][bucket][0]>t:
                by_bird[ident][bucket]=(t,lat,lon)
    obs=[];drop=Counter()
    for ident,data in by_bird.items():
        fixes=sorted(data.values())
        for a,b in zip(fixes,fixes[1:]):
            dt=(b[0]-a[0]).total_seconds()/3600.
            if dt<0.5 or dt>2:
                drop['gap_rejection']+=1;continue
            speed=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))/(1000*dt)
            if speed>120:
                drop['implausible_speed']+=1;continue
            t=a[0]
            try:h,phase,rate=tide.at_with_phase(t)
            except ValueError:
                drop['gauge_gap']+=1;continue
            if phase==0:
                drop['slack_tide']+=1;continue
            hour=t.hour+t.minute/60
            day=t.timetuple().tm_yday
            obs.append({'id':ident,'t':t,'h':h,'phase':phase,'rate':rate,
                        'response':math.log1p(speed),'lat':a[1],'lon':a[2],
                        'clocksin':math.sin(2*math.pi*hour/24),
                        'clockcos':math.cos(2*math.pi*hour/24),
                        'yearsin':math.sin(2*math.pi*day/365.25),
                        'yearcos':math.cos(2*math.pi*day/365.25)})
    return obs,{'raw_original_rows':raw,'visible_local_original_rows':visible,
                'same_bird_first_fix_hourly_step_rows':len(obs),
                'individuals_with_steps':len(set(x['id'] for x in obs)),
                'dropping':dict(drop),
                'source_clock_assumption':f'ORIGINAL_TIMESTAMP_INTERPRETED_AS_UTC_PLUS_{clock_shift_s}_SECONDS',
                'sampling_scheme':'first_visible_fix_per_native_UTC_hour; displacement 0.5-2h; speed_km_h'}

def make_x(r,level):
    h=r['h']
    out=[1.,h,h*h,(r['lat']-53.45)*10,(r['lon']-6.2)*5,
         r['clocksin'],r['clockcos'],r['yearsin'],r['yearcos']]
    if level==1:out.extend([r['phase'],r['phase']*h,r['rate']])
    return out

def predict(train,test,level):
    a=np.asarray([make_x(r,level) for r in train],dtype=float)
    b=np.asarray([make_x(r,level) for r in test],dtype=float)
    y=np.asarray([r['response'] for r in train])
    center=a[:,1:].mean(axis=0);sd=a[:,1:].std(axis=0)
    sd[sd<1e-9]=1
    a[:,1:]=(a[:,1:]-center)/sd
    b[:,1:]=(b[:,1:]-center)/sd
    count=Counter(r['id'] for r in train)
    w=np.asarray([1/count[r['id']] for r in train])
    w*=len(train)/w.sum()
    p=np.eye(a.shape[1])*10.;p[0,0]=0
    beta=np.linalg.solve(a.T@(a*w[:,None])+p,a.T@(w*y))
    return b@beta

def heldout_compare(rows):
    blocks=sorted(set(r['t'].date().toordinal()//7 for r in rows))
    if len(blocks)<10:raise ValueError('Not enough distinct weekly source blocks')
    split=int(0.7*len(blocks))
    trainblocks=set(blocks[:split]);testblocks=set(blocks[split+1:])
    train=[r for r in rows if r['t'].date().toordinal()//7 in trainblocks]
    test=[r for r in rows if r['t'].date().toordinal()//7 in testblocks]
    if len(test)<100:raise ValueError('Too few test steps')
    losses={}
    for m in (0,1):
        yhat=predict(train,test,m)
        by_bird=defaultdict(list)
        for r,p in zip(test,yhat):by_bird[r['id']].append((r['response']-p)**2)
        losses['M'+str(m)]={b:float(np.mean(v)) for b,v in by_bird.items()}
    ids=sorted(set(losses['M0'])&set(losses['M1']))
    increments=np.asarray([losses['M0'][b]-losses['M1'][b] for b in ids])
    rng=np.random.default_rng(31102)
    ci=np.quantile(np.mean(rng.choice(increments,size=(5000,len(increments)),replace=True),axis=1),[.025,.975])
    return {'n_train':len(train),'n_test':len(test),'n_week_blocks':len(blocks),
            'embargo_week_blocks':1,'n_heldout_birds':len(ids),
            'M0_mean_equal_bird_MSE':float(np.mean(list(losses['M0'].values()))),
            'M1_mean_equal_bird_MSE':float(np.mean(list(losses['M1'].values()))),
            'M0_minus_M1_equal_bird_MSE_gain':float(np.mean(increments)),
            'birds_with_M1_gain':int(np.sum(increments>0)),
            'bird_bootstrap_95':list(map(float,ci)),
            'note':'Out-of-week GPS-step prediction conditional on assumed UTC original clock; association only'}

def same_height_hysteresis(rows):
    groups=defaultdict(lambda:defaultdict(list))
    for r in rows:
        key=(r['id'],r['t'].month,math.floor(r['h']/0.15),r['t'].hour//6)
        groups[key][r['phase']].append(r['response'])
    birdstrata=defaultdict(list);total_obs=0
    for (bird,*_),val in groups.items():
        e,f=val.get(-1,[]),val.get(1,[])
        if len(e)>=3 and len(f)>=3:
            diff=float(np.mean(e)-np.mean(f))
            birdstrata[bird].append((diff,min(len(e),len(f))))
            total_obs+=len(e)+len(f)
    bybird={b:float(np.average([x for x,n in v],weights=[min(n,10) for x,n in v]))
            for b,v in birdstrata.items()}
    return {'strata':sum(len(v) for v in birdstrata.values()),
            'candidate_records_in_strata':total_obs,
            'animals_with_ebb_flood_matched_strata':len(bybird),
            'ebb_minus_flood_equal_bird_mean_log1p_speed':float(np.mean(list(bybird.values()))) if bybird else None,
            'birds_ebb_faster':sum(x>0 for x in bybird.values()),
            'note':'Within-bird/month/height 0.15m bin/fixed 6h clock bin; descriptive association'}

def run(output,year=2009,clock_shift_s=0):
    with tempfile.TemporaryDirectory() as d:
        filename=Path(d)/f'{year}.csv.gz'
        pin=download_and_pin(year,filename)
        tide,gauge=real_rws_tide(year)
        rows,audit=gps_hourly_steps(filename,tide,clock_shift_s=clock_shift_s)
    if len(rows)<1000:raise ValueError('Insufficient joined observed movement steps')
    score=heldout_compare(rows)
    matching=same_height_hysteresis(rows)
    result={'evidence':'EXPLORATORY_ORIGINAL_GPS_AND_MEASURED_RWS_ASSOCIATION',
            'claim_limit':'No DEM/prey/moving-front or causal social force. Assumed source clock UTC not independently verified.',
            'year':year,'gps_source_manifest':pin,'rws_source_audit':gauge,
            'movement_join_audit':audit,'prediction':score,'matched_water_height':matching}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--year',type=int,default=2009)
    p.add_argument('--clock-shift-s',type=int,default=0)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    print(json.dumps(run(a.output,a.year,a.clock_shift_s),sort_keys=True))
