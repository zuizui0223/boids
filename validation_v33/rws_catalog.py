#!/usr/bin/env python3
"""v33-B official RWS DDAPI station catalog lookup, no tide heights, no GPS."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import urllib.request
import urllib.error

URL="https://ddapi20-waterwebservices.rijkswaterstaat.nl/METADATASERVICES/OphalenCatalogus"
MAX_BYTES=40_000_000
TARGETS=("schiermonnikoog","lauwersoog")
def catalog():
    body=json.dumps({"CatalogusFilter":{"Compartimenten":True,"Grootheden":True}},
         separators=(",",":")).encode()
    req=urllib.request.Request(URL,data=body,method="POST",
      headers={"Content-Type":"application/json","Accept":"application/json",
               "User-Agent":"boids-v33-official-rws-source-only-catalog/1.0"})
    with urllib.request.urlopen(req,timeout=90) as response:
        raw=response.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError("RWS metadata exceeded 40 MB source cap")
    return json.loads(raw),len(raw)
def scrutinize(obj):
    if not isinstance(obj,dict):raise ValueError("RWS catalog not a JSON object")
    loc=obj.get("LocatieLijst") or []
    if not isinstance(loc,list):raise ValueError("RWS catalog missing location list")
    matches=[]
    for x in loc:
        if not isinstance(x,dict):continue
        fields=" ".join(str(x.get(k) or "") for k in ("Naam","Code","Omschrijving","LocatieNaam")).casefold()
        if any(t in fields for t in TARGETS):
            matches.append(x)
    return {"catalog_top_keys":list(obj),"total_original_location_count":len(loc),
       "filtered_original_source_locations":matches,
       "source_metadata_list_count":len(obj.get("AquoMetadataLijst") or []),
       "source_metadata_location_link_count":len(obj.get("AquoMetadataLocatieLijst") or []),
       "no_tide_numeric_value_or_bird_position_read":True}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("validation_v33/results/rws_station_catalog.json"))
    args=ap.parse_args()
    try:
        obj,n=catalog()
        x=scrutinize(obj)
        x["catalog_response_bytes"]=n
        x["status"]="RWS_OFFICIAL_STATION_CATALOG_MATCHES" if x["filtered_original_source_locations"] else "RWS_OFFICIAL_CATALOG_NO_MATCH"
    except (urllib.error.URLError,ValueError,TimeoutError) as e:
        msg=str(e)
        if isinstance(e,urllib.error.HTTPError):
            msg+="; "+e.read(10000).decode("utf-8",errors="replace")[:2000]
        x={"status":"RWS_OFFICIAL_CATALOG_NOT_ADMITTED","error_type":type(e).__name__,
           "error":msg[:3000],"no_tide_numeric_value_or_bird_position_read":True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("V33_RWS_CATALOG",json.dumps(x,sort_keys=True,separators=(",",":")))
if __name__=="__main__":main()
