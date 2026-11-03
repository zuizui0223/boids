"""v34 FROZEN independent-island oystercatcher tide phase prediction.

No biological outcomes read before docs/V34_FROZEN_AMELAND_EXTERNAL_SITE.md.
Original Ameland GPS 2010-11 provider MD5 + original Rijkswaterstaat measured
Ameland.Nes tide. Metadata/source clocks and representative gauge uncertainty
remain explicit. Raw fixes/IDs and gauge time series are ephemeral only.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,tempfile
from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from source_preflight import parse_stamp,haversine_m
from rws_source_probe import post_json,WATHTE
from tidal_front import TideSeries
from observed_phase import same_height_hysteresis
from phase_rate_ablation import compare

RECORD="https://zenodo.org/records/10053853"
SITE="O_AMELAND"
STATION="ameland.nes"
GPS_MD5={2010:"71e0b66230b508873897c99464146167",
         2011:"ab74f7443bb09bd5be90bde69fc612eb"}
UTC=timezone.utc
BBOX=(53.2,53.6,5.3,6.1)

def original_gps(year,path):
    if year not in GPS_MD5:raise ValueError("Only prespecified 2010/2011 source")
    filename=f"{SITE}-gps-{year}.csv.gz"
    url=f"{RECORD}/files/{filename}?download=1"
    md5=hashlib.md5();sha=hashlib.sha256();n=0
    req=Request(url,headers={"User-Agent":"Boids-v34-Ameland-Original-Source/1.0"})
    with urlopen(req,timeout=100) as stream,Path(path).open("wb") as out:
        while True:
            block=stream.read(1<<19)
            if not block:break
            n+=len(block)
            if n>30_000_000:raise ValueError("Unexpectedly large original gzip")
            md5.update(block);sha.update(block);out.write(block)
    if md5.hexdigest()!=GPS_MD5[year]:
        Path(path).unlink(missing_ok=True)
        raise ValueError("Original Ameland provider MD5 mismatch")
    return {"source":RECORD,"year":year,"filename":filename,
            "provider_original_md5_matched":True,"original_bytes":n,
            "original_sha256":sha.hexdigest()}

def measured_nes(year,request=post_json):
    if year not in GPS_MD5:raise ValueError("Only frozen 2010/11 measured gauge")
    observed={};receipt=[]
    for month in range(1,13):
        begin=datetime(year,month,1)
        end=datetime(year+1,1,1) if month==12 else datetime(year,month+1,1)
        query={"Locatie":{"Code":STATION},
               "AquoPlusWaarnemingMetadata":{"AquoMetadata":dict(WATHTE,ProcesType="meting")},
               "Periode":{"Begindatumtijd":begin.strftime("%Y-%m-%dT%H:%M:%S.000+01:00"),
                          "Einddatumtijd":end.strftime("%Y-%m-%dT%H:%M:%S.000+01:00")}}
        raw=request("/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen",query,
                    max_bytes=15_000_000)
        if raw.get("Succesvol") is not True:
            raise ValueError(f"RWS Ameland.Nes not successful in month {month}")
        matched=0
        for s in raw.get("WaarnemingenLijst",[]):
            m=s.get("AquoMetadata") or {}
            if (m.get("Grootheid") or {}).get("Code")!="WATHTE":continue
            if (m.get("Eenheid") or {}).get("Code")!="cm":
                raise ValueError("Wrong gauge unit: not original measured cm")
            if (m.get("Hoedanigheid") or {}).get("Code")!="NAP":
                raise ValueError("Wrong gauge vertical reference: not original NAP")
            for sample in s.get("MetingenLijst",[]):
                rawtime=datetime.fromisoformat(sample["Tijdstip"].replace("Z","+00:00"))
                if rawtime.utcoffset()!=timedelta(hours=1):
                    raise ValueError("Dutch RWS timestamps must use fixed +01, not DST")
                value=(sample.get("Meetwaarde") or {}).get("Waarde_Numeriek")
                if value is None:continue
                value=float(value)
                if not math.isfinite(value) or abs(value)>500:continue
                t=rawtime.astimezone(UTC)
                if t in observed and abs(observed[t]-value/100)>1e-4:
                    raise ValueError("Contradictory RWS overlapping water observation")
                observed[t]=value/100
                matched+=1
        receipt.append({"month":str(year)+"-"+str(month).zfill(2),
                        "admitted_observations":matched})
    if len(observed)<12000:
        raise ValueError("Source gate: <12000 original measured Ameland tide readings")
    tide=TideSeries(sorted(observed.items()),datum="NAP_m",provenance="observed")
    gaps=[(b-a).total_seconds()/60 for a,b in zip(tide.times,tide.times[1:])]
    return tide,{"station":STATION,"measured_rws_gauge":True,
                 "original_datum":"NAP","unit":"cm→m",
                 "historical_time_offset":"+01:00_fixed",
                 "n_original_unique_gauge_fixes":len(observed),
                 "n_gauge_gaps_over_30min":sum(x>30 for x in gaps),
                 "largest_gauge_gap_min":max(gaps) if gaps else None,
                 "monthly_coverage":receipt,
                 "local_inundation_coverage":"NOT_ESTIMATED"}

def ameland_original_steps(gzip_path,tide,clock_shift_s=0):
    if clock_shift_s not in (0,-15):raise ValueError("Unfrozen clock offset")
    bybird=defaultdict(dict);drops=Counter();raw_count=0
    with gzip.open(gzip_path,"rt",newline="",encoding="utf-8-sig") as data:
        reader=csv.DictReader(data)
        needed={"event-id","timestamp","location-lat","location-long",
                "individual-local-identifier","visible"}
        if not needed<=set(reader.fieldnames or []):
            raise ValueError("Source file field dictionary not expected Movebank GPS")
        event_ids=set()
        for r in reader:
            raw_count+=1
            eid=r["event-id"].strip()
            if not eid or eid in event_ids:
                drops["bad_event_id"]+=1;continue
            event_ids.add(eid)
            if r["visible"].strip().upper() in ("FALSE","0"):
                drops["not_visible"]+=1;continue
            bird=r["individual-local-identifier"].strip()
            if not bird:
                drops["no_bird_id"]+=1;continue
            try:
                t=parse_stamp(r["timestamp"]).replace(tzinfo=UTC)+timedelta(seconds=clock_shift_s)
                lat=float(r["location-lat"]);lon=float(r["location-long"])
            except (ValueError,TypeError):
                drops["invalid_position_or_clock"]+=1;continue
            if not all(map(math.isfinite,[lat,lon])) or not(BBOX[0]<=lat<=BBOX[1] and BBOX[2]<=lon<=BBOX[3]):
                drops["outside_prefrozen_ameland_envelope"]+=1;continue
            bucket=t.replace(minute=0,second=0,microsecond=0)
            if bucket not in bybird[bird] or bybird[bird][bucket][0]>t:
                bybird[bird][bucket]=(t,lat,lon)
    rows=[]
    for bird, fixes in bybird.items():
        ordered=sorted(fixes.values())
        for a,b in zip(ordered,ordered[1:]):
            diff=(b[0]-a[0]).total_seconds()/3600
            if not (.5<=diff<=2):
                drops["bad_hourly_gap"]+=1;continue
            speed=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))/(1000*diff)
            if not(0<=speed<=120):
                drops["implausible_speed"]+=1;continue
            t=a[0]
            try:
                h,phase,rate=tide.at_with_phase(t)
            except ValueError:
                drops["gauge_no_matching_water_level"]+=1;continue
            if not phase:
                drops["slack_phase"]+=1;continue
            hour=t.hour+t.minute/60
            day=t.timetuple().tm_yday
            rows.append({"id":bird,"t":t,"h":h,"phase":phase,"rate":rate,
                        "response":math.log1p(speed),"lat":a[1],"lon":a[2],
                        "clocksin":math.sin(2*math.pi*hour/24),
                        "clockcos":math.cos(2*math.pi*hour/24),
                        "yearsin":math.sin(2*math.pi*day/365.25),
                        "yearcos":math.cos(2*math.pi*day/365.25)})
    return rows,{"year_source_rows":raw_count,
                 "source_animals_in_region":len(bybird),
                 "source_first_hourly_fixes":sum(map(len,bybird.values())),
                 "eligible_real_movement_intervals":len(rows),
                 "birds_with_steps":len({r["id"] for r in rows}),
                 "drop_reasons":dict(drops),
                 "original_GPS_clock_status":"UTC_OR_GPS_TIME_UNRESOLVED"}

def run(output):
    info={};rows={}
    with tempfile.TemporaryDirectory(prefix="original_ameland_v34_") as tmp:
        for year in (2010,2011):
            path=Path(tmp)/f"{year}.gz"
            manifest=original_gps(year,path)
            tide,gauge=measured_nes(year)
            rows[year]={};audit={}
            for delta in (0,-15):
                this,s=ameland_original_steps(path,tide,clock_shift_s=delta)
                rows[year][delta]=this
                audit[str(delta)]=s
            info[str(year)]={"manifest":manifest,"gauge":gauge,"steps":audit}
            path.unlink(missing_ok=True)
    tests={}
    for delta in (0,-15):
        train,test=rows[2010][delta],rows[2011][delta]
        enough=(len(train)>=1000 and len(test)>=1000 and
                len({r["id"] for r in test})>=3 and
                len({r["t"].isocalendar()[:2] for r in test})>=4)
        if enough:
            result=compare(train,test)
            result["primary"]="M0_minus_Mphase"
            result["primary_admission"]="OBSERVED_EXTERNAL_SITE_EXPLORATORY_CLOCK_UNVERIFIED"
        else:
            result={"primary_admission":"NOT_ADMITTED",
                    "reason":"Less than 3 test birds, 4 test weeks, or 1000 train/test steps",
                    "n_train_rows":len(train),"n_test_rows":len(test),
                    "n_test_birds":len({r["id"] for r in test}),
                    "n_test_weeks":len({r["t"].isocalendar()[:2] for r in test})}
        result["matched_height_2010"]=same_height_hysteresis(train)
        result["matched_height_2011"]=same_height_hysteresis(test)
        tests[f"native_clock_shift_{delta}s"]=result
    out={"analysis":"V34_FROZEN_EXTERNAL_AMELAND_2010_TO_2011",
         "original_site":"O_AMELAND","gauge_station":STATION,
         "primary":"M0_equal_bird_MSE_minus_Mphase_equal_bird_MSE",
         "source_manifest":info,"scenarios":tests,
         "claim_boundary":"one species, different island, original GPS time standard uncertain, no prey, DEM or social-force mechanism",
         "source_bytes_exposed":False}
    path=Path(output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,sort_keys=True,indent=2)+"\n")
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    a=p.parse_args()
    report=run(a.output)
    # Only aggregated, source-audited field metrics. No IDs or raw GPS coordinates.
    print(json.dumps(report,sort_keys=True))
