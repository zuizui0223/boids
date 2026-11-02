"""RWS DDAPI2 original station/historical date probe, no bird/tide inference.

API documents fixed +01:00 timestamps even in summer. Do not apply Dutch DST
or mistake levels relative to LAT for levels relative to NAP.
"""
from __future__ import annotations
import argparse, json, math
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.request import Request,urlopen

ROOT="https://ddapi20-waterwebservices.rijkswaterstaat.nl"
WATHTE={"Compartiment":{"Code":"OW"},"Grootheid":{"Code":"WATHTE"}}


def post_json(path, payload, max_bytes=7_000_000):
    req=Request(ROOT+path, data=json.dumps(payload).encode(), method="POST",
                headers={"Content-Type":"application/json","Accept":"application/json",
                         "User-Agent":"boids-source-preflight/1.0"})
    with urlopen(req, timeout=65) as resp:
        data=resp.read(max_bytes+1)
        if len(data)>max_bytes:
            raise ValueError("RWS response exceeded declared size cap")
    return json.loads(data)


def extract_station_catalog(catalog, place="schiermonnikoog"):
    stations=[]
    for v in catalog.get("LocatieLijst",[]):
        code=(v.get("Code") or "").lower();name=(v.get("Naam") or "").lower()
        if place in (code+" "+name):
            stations.append({"code":v.get("Code"),"name":v.get("Naam")})
    return stations


def describe_water_response(payload):
    if payload.get("Succesvol") is False:
        return {"status":"API_EXPLICIT_FAILURE",
                "reason":str(payload.get("Foutmelding",payload.get("Melding","")))[:240]}
    series=[]
    for row in payload.get("WaarnemingenLijst",[]):
        meta=row.get("AquoMetadata") or {}
        unit=meta.get("Eenheid") or {}
        reference=meta.get("Hoedanigheid") or {}
        bsoort=meta.get("BemonsteringsSoort") or {}
        vals=row.get("MetingenLijst") or []
        times=[];magnitudes=[]; invalid_time=0
        for x in vals:
            stamp=x.get("Tijdstip")
            if not stamp: continue
            try: t=datetime.fromisoformat(stamp.replace("Z","+00:00"))
            except ValueError:
                invalid_time+=1;continue
            if t.utcoffset() is None:invalid_time+=1;continue
            times.append(t)
            try:
                y=float((x.get("Meetwaarde") or {}).get("Waarde_Numeriek"))
                if math.isfinite(y) and y != -999999999: magnitudes.append(y)
            except (TypeError,ValueError): pass
        series.append({"measurement_count":len(vals),"timestamp_count":len(times),
                       "finite_values":len(magnitudes),"unit_code":unit.get("Code"),
                       "reference_code":reference.get("Code"),
                       "reference_description":reference.get("Omschrijving"),
                       "sample_type_code":bsoort.get("Code"),
                       "grootheid_code":(meta.get("Grootheid") or {}).get("Code"),
                       "first_time_original_offset":min(times).isoformat() if times else None,
                       "last_time_original_offset":max(times).isoformat() if times else None,
                       "timestamp_offsets_seconds":dict(Counter(str(int(t.utcoffset().total_seconds()))
                                                        for t in times)),
                       "time_decode_errors":invalid_time})
    available=sum(x["finite_values"] for x in series)
    nap=[x for x in series if "NAP" in
         (str(x["reference_code"])+str(x["reference_description"])).upper()]
    allfixed=all(k=="3600" for x in series for k in x["timestamp_offsets_seconds"])
    return {"status":"HISTORICAL_GAUGE_METADATA_CHECK" if available else "NO_HISTORICAL_STATION_VALUES",
            "api_successful":payload.get("Succesvol"),"n_series":len(series),
            "finite_values":available,"explicit_NAP_series_count":len(nap),
            "offsets_fixed_one_hour":allfixed if series else None,"series":series,
            "field_tide_join_allowed":bool(available and nap and allfixed),
            "paired_bird_effect":"NOT_ESTIMATED"}


def run(output):
    r={"endpoint":ROOT,"reference_date_UTC":"2008-08-14_to_2008-08-16",
       "evidence":"RWS_HISTORICAL_SOURCE_ONLY"}
    catalog=post_json("/METADATASERVICES/OphalenCatalogus",
                      {"CatalogusFilter":{"Grootheden":True,"Eenheden":True,
                                          "Compartimenten":True}})
    stations=extract_station_catalog(catalog)
    r["stations_matching_name"]=stations
    if not stations:
        r["status"]="STOP_NO_SCHIERMONNIKOOG_STATION_IN_CATALOGUE"
    else:
        # Distinct water bodies/instruments must NOT silently become the
        # historical Schiermonnikoog mainland tide gauge from the Dryad paper.
        candidates = [
            "schiermonnikoog.waddenzee",
            "schiermonnikoog.westgat",
            "gatvanschiermonnikoog",
            "schiermonnikoog.noord",
            "schiermonnikoog.eilanderbalg",
        ]
        r["candidate_probes"]={}
        available=[]
        for code in candidates:
            if not any(x["code"]==code for x in stations):
                r["candidate_probes"][code]={"status":"NOT_IN_ORIGINAL_CATALOGUE"}
                continue
            post={"Locatie":{"Code":code},
                  "AquoPlusWaarnemingMetadata":{"AquoMetadata":dict(WATHTE,ProcesType="meting")},
                  "Periode":{"Begindatumtijd":"2008-08-14T00:00:00.000+01:00",
                             "Einddatumtijd":"2008-08-16T00:00:00.000+01:00"}}
            try:
                sample=post_json("/ONLINEWAARNEMINGENSERVICES/OphalenWaarnemingen",post)
                summary=describe_water_response(sample)
            except Exception as exc:
                summary={"status":"SOURCE_PROBE_ERROR","detail":str(exc)[:180]}
            r["candidate_probes"][code]=summary
            if summary.get("finite_values",0)>0:available.append(code)
        r["candidate_codes_with_historical_values"]=available
        r["dryad_exact_instrument_identity_verified"]=False
        r["status"]="CANDIDATE_STATIONS_FOUND_IDENTITY_AND_NAP_STILL_UNVERIFIED" if available else "STOP_NO_HISTORICAL_CANDIDATE_VALUES"
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    args=p.parse_args()
    print(json.dumps(run(args.output),sort_keys=True))
