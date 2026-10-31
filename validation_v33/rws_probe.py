#!/usr/bin/env python3
"""v33-A official RWS historical water-height source-only probe.

No animal GPS opened; response numeric tide values are NOT exported at this stage.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import urllib.request
import urllib.error

RWS_API="https://ddapi20-waterwebservices.rijkswaterstaat.nl/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen"
PROBES=(
    ("schiermonnikoog","astronomisch","2010-05-12T00:00:00.000+01:00","2010-05-13T00:00:00.000+01:00"),
    ("schiermonnikoog","meting","2010-05-12T00:00:00.000+01:00","2010-05-13T00:00:00.000+01:00"),
    ("lauwersoog","astronomisch","2010-05-12T00:00:00.000+01:00","2010-05-13T00:00:00.000+01:00"),
)
MAX_BYTES=5_000_000
AGENT="boids-v33-original-RWS-tide-source-probe/1.0"
def payload(station,process,start,end):
    if station not in ("schiermonnikoog","lauwersoog") or process not in ("astronomisch","meting"):
        raise ValueError("Unexpected source station or process")
    return {"Locatie":{"Code":station},
      "AquoPlusWaarnemingMetadata":{"AquoMetadata":{
          "Compartiment":{"Code":"OW"},"Grootheid":{"Code":"WATHTE"},
          "ProcesType":process}},
      "Periode":{"Begindatumtijd":start,"Einddatumtijd":end}}

def request_one(args):
    station,process,start,end=args
    msg=json.dumps(payload(*args),separators=(",",":")).encode()
    req=urllib.request.Request(RWS_API,data=msg,method="POST",
           headers={"Content-Type":"application/json","Accept":"application/json",
                    "User-Agent":AGENT})
    with urllib.request.urlopen(req,timeout=45) as f:raw=f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError("Tide source probe exceeds 5MB")
    obj=json.loads(raw)
    return obj,len(raw)

def inspect_shape(obj):
    """Do not export any numerical tide observation value at preflight."""
    if not isinstance(obj,dict):return {"object_type":type(obj).__name__,"source_list_count":0}
    lists=obj.get("WaarnemingenLijst") or obj.get("WaarnemingenLijsten") or []
    if not isinstance(lists,list):lists=[]
    result={"api_top_level_keys":sorted(obj),
        "source_list_count":len(lists),
        "root_error":str(obj.get("Foutmelding") or obj.get("Error") or "")[:150],
        "response_succeeded_field":str(obj.get("Succesvol") or obj.get("success") or "")[:60],
        "lists":[]}
    for lst in lists[:5]:
        samples=lst.get("MetingenLijst") or lst.get("Metingen") or []
        loc=lst.get("Locatie") or {}
        meta=lst.get("AquoMetadata") or lst.get("AquoPlusWaarnemingMetadata") or {}
        if not isinstance(samples,list):samples=[]
        exemplar=samples[0] if samples else {}
        result["lists"].append({
            "location_code":loc.get("Code") if isinstance(loc,dict) else None,
            "location_name":loc.get("Naam") if isinstance(loc,dict) else None,
            "location_fields":sorted(loc) if isinstance(loc,dict) else [],
            "metadata":meta, # source units/quality codes, NOT numerical tide observations
            "measurement_count":len(samples),
            "measurement_object_fields":sorted(exemplar) if isinstance(exemplar,dict) else [],
            "timestamp_shape_only":str(exemplar.get("Tijdstip") or exemplar.get("TijdstipWaarneming") or "")[:40],
        })
    return result

def run():
    attempts=[]
    for spec in PROBES:
        station,process,_,_=spec
        try:
            out,n=request_one(spec)
            shape=inspect_shape(out)
            attempts.append({"requested_location_code":station,"requested_process_type":process,
                 "api_bytes":n,**shape,"retrieved_no_original_animal_GPS":True})
        except (urllib.error.URLError,ValueError,TimeoutError,ConnectionError) as e:
            # Source provider may explain 400 parameter errors; it is not animal data.
            provider_error=""
            if isinstance(e,urllib.error.HTTPError):
                provider_error=e.read(6000).decode("utf-8",errors="replace")[:6000]
            attempts.append({"requested_location_code":station,"requested_process_type":process,
                 "request_failed":True,"error_type":type(e).__name__,
                 "error_message":str(e)[:180],
                 "provider_error_body":provider_error,
                 "retrieved_no_original_animal_GPS":True})
    good=[x for x in attempts if x.get("source_list_count",0)>0 and
          any(y.get("measurement_count",0)>0 for y in x.get("lists",[]))]
    return {"study":"v33 official Rijkswaterstaat Schiermonnikoog tide source-only",
        "status":"RWS_PRELIMINARY_SOURCE_RESPONDED" if good else "RWS_HISTORICAL_SOURCE_NOT_ADMITTED",
        "official_documentation":"https://rijkswaterstaatdata.nl/waterdata/",
        "requests":[{"station":s[0],"process_type":s[1],"period_fixed_DST_plus_0100":s[2]+" to "+s[3]}
                    for s in PROBES],
        "source_only_probes":attempts,
        "no_animal_GPS_coordinates_or_tidal_values_exported":True,
        "no_tide_movement_effect_or_forecast_computed":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("validation_v33/results/rws_station_source_probe.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("V33_RWS_SOURCE_PROBE",json.dumps(result,sort_keys=True,separators=(",",":")))

if __name__=="__main__":main()
