"""v40 source-only 2012 original field GPS eligibility for untouched tide test.

No tide is downloaded here. Passing this gate never implies tidal association.
Original source birds, coordinates and GPS timestamps stay on ephemeral runner.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from source_preflight import download_and_pin, parse_stamp, haversine_m

RECORD_AMELAND = "https://zenodo.org/records/10053853"
AMELAND_2012_MD5 = "12d5d3045578538f6a6ac9f8e78766df"
SCHIER_2012_MD5 = "a2ccce5afe2a6cad09a27e2957beacaf"
REGIONS = {"schiermonnikoog": (53.2,53.7,5.7,6.6),
           "ameland": (53.2,53.6,5.3,6.1)}
REQUIRED = {"event-id","timestamp","location-lat","location-long",
            "individual-local-identifier","visible"}

def get_ameland_original(path):
    filename="O_AMELAND-gps-2012.csv.gz"
    url=f"{RECORD_AMELAND}/files/{filename}?download=1"
    md5=hashlib.md5();sha=hashlib.sha256();n=0
    request=Request(url,headers={"User-Agent":"Boids-v40-original-2012-source-gate/1.0"})
    with urlopen(request,timeout=80) as inp, Path(path).open("wb") as out:
        while True:
            part=inp.read(1<<18)
            if not part:break
            n+=len(part)
            if n>10_000_000:
                raise ValueError("2012 Ameland original file exceeds 10MB cap")
            md5.update(part);sha.update(part);out.write(part)
    if md5.hexdigest()!=AMELAND_2012_MD5:
        Path(path).unlink(missing_ok=True)
        raise ValueError("Ameland 2012 original GPS provider MD5 mismatch")
    return {"year":2012,"source":RECORD_AMELAND,"filename":filename,
            "original_bytes":n,"original_sha256":sha.hexdigest(),
            "provider_md5_match":True}

def eligible_source_steps(path,site):
    if site not in REGIONS:raise ValueError("Unfrozen site")
    bounds=REGIONS[site];bybird=defaultdict(dict)
    source_rows=0;reasons=Counter();event_ids=set()
    with gzip.open(path,"rt",encoding="utf-8-sig",newline="") as inp:
        reader=csv.DictReader(inp)
        if not REQUIRED<=set(reader.fieldnames or ()):
            raise ValueError("Original Movebank GPS source columns mismatch")
        for r in reader:
            source_rows+=1
            event=(r.get("event-id") or "").strip()
            if not event or event in event_ids:
                reasons["missing_or_duplicate_event"]+=1;continue
            event_ids.add(event)
            if r.get("visible","").strip().upper() in ("FALSE","0"):
                reasons["source_invisible"]+=1;continue
            animal=(r.get("individual-local-identifier") or "").strip()
            if not animal:
                reasons["source_missing_bird"]+=1;continue
            try:
                t=parse_stamp(r["timestamp"])
                lat=float(r["location-lat"]);lon=float(r["location-long"])
            except (ValueError,TypeError):
                reasons["bad_location_or_original_clock"]+=1;continue
            if not all(map(math.isfinite,(lat,lon))) or not (
                t.year==2012 and bounds[0]<=lat<=bounds[1] and bounds[2]<=lon<=bounds[3]
            ):
                reasons["outside_frozen_2012_site_window"]+=1;continue
            bucket=t.replace(minute=0,second=0,microsecond=0)
            if bucket not in bybird[animal] or bybird[animal][bucket][0]>t:
                bybird[animal][bucket]=(t,lat,lon)
    stepcount=0;birds=set();weeks=set();monthset=set();steplength=[]
    for bird,records in bybird.items():
        ordered=sorted(records.values())
        for a,b in zip(ordered,ordered[1:]):
            dt=(b[0]-a[0]).total_seconds()/3600.
            if not .5<=dt<=2.0:
                reasons["step_not_30min_to_2h"]+=1;continue
            speed=haversine_m((None,a[1],a[2]),(None,b[1],b[2]))/(1000*dt)
            if not math.isfinite(speed) or speed>120:
                reasons["step_speed_outside_0_to_120"]+=1;continue
            birds.add(bird)
            weeks.add(a[0].isocalendar()[:2])
            monthset.add(a[0].month)
            stepcount+=1
    admission=(len(birds)>=3 and len(weeks)>=4 and stepcount>=1000)
    return {"site":site,"source_type":"ORIGINAL_2012_GPS_ONLY_NO_TIDE",
            "source_raw_gps_rows":source_rows,
            "native_hourly_first_fix_count":sum(map(len,bybird.values())),
            "source_individuals_in_geographic_gate":len(bybird),
            "candidate_individuals_with_2012_steps":len(birds),
            "candidate_2012_hourly_step_count":stepcount,
            "candidate_2012_iso_week_count":len(weeks),
            "candidate_2012_month_count":len(monthset),
            "original_source_filter_counts":dict(reasons),
            "tide_test_admission":"SOURCE_FEASIBLE_ONLY" if admission else "NOT_ADMITTED_INSUFFICIENT_2012_SOURCE",
            "source_clock":"NATIVE_UTC_OR_GPS_TIME_UNVERIFIED",
            "source_tide_joined":False,"biological_tide_effect":"NOT_ESTIMATED"}

def run(output):
    receipt={"analysis":"V40_PREOUTCOME_2012_GPS_SOURCE_ONLY",
             "source_statistic":"native GPS year source eligibility, NO phase test",
             "sites":{}}
    with tempfile.TemporaryDirectory(prefix="boids_v40_source_") as td:
        for site in ("schiermonnikoog","ameland"):
            path=Path(td)/f"{site}_2012_original.csv.gz"
            if site=="schiermonnikoog":
                orig=download_and_pin(2012,path)
                if orig["year"]!=2012 or not orig["provider_md5_match"]:
                    raise ValueError("Schier 2012 original source check fail")
            else:
                orig=get_ameland_original(path)
            quality=eligible_source_steps(path,site)
            path.unlink(missing_ok=True)
            receipt["sites"][site]={"original_manifest":orig,"source_admission":quality}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
