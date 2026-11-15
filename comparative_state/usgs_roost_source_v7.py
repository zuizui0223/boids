#!/usr/bin/env python3
"""Public original USGS 2021 source-only provenance check, never inspect bird responses.

The 2021 USGS record may contain tracked duck roost/night-feeding endpoints,
but the record title is not a valid individual-origin + availability crosswalk.
"""
from __future__ import annotations
import argparse, json, urllib.request, urllib.parse
from pathlib import Path

DOI="10.5066/P922KDU6"
ITEM="601478d0d34edf5c66ea0ead"
URL=f"https://www.sciencebase.gov/catalog/item/{ITEM}?format=json"


def valid_source(url: str) -> bool:
    p=urllib.parse.urlparse(url)
    return p.scheme=="https" and p.hostname in {"www.sciencebase.gov", "sciencebase.gov"} and p.path.startswith("/catalog/item/")


def parse_inventory(payload: dict) -> dict:
    if not isinstance(payload,dict): raise ValueError("invalid source metadata")
    files=payload.get("files",[])
    if not isinstance(files,list):raise ValueError("invalid file list")
    out=[]
    for f in files:
        if not isinstance(f,dict):continue
        out.append({
            "name":str(f.get("name", "")),
            "size":f.get("size"),
            "provider_checksum":f.get("checksum",f.get("md5")),
            "metadata_only":True,
        })
    return {"metadata_title":payload.get("title"),"file_count":len(out),"files":out,
            "true_step_origin_schema_admitted":False,
            "matched_option_set_schema_admitted":False,
            "source_bird_independence_from_Overton_2023":False}


def main(out_path: str) -> None:
    result={"schema":"ecostate.usgs_roost_source_v7","source_doi":DOI,"sciencebase_id":ITEM,
      "source_url":URL,"status":"SOURCE_STOP","original_animal_values_opened":False,
      "new_ecological_effects_computed":False}
    try:
        if not valid_source(URL):raise ValueError("blocked unverified source URL")
        req=urllib.request.Request(URL,headers={"User-Agent":"ecostate-source-only-v7/1.0", "Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as resp:
            content=resp.read(1_500_001)
        if len(content)>1_500_000:raise ValueError("oversized metadata")
        parsed=parse_inventory(json.loads(content))
        result.update(parsed)
        result["status"]="SOURCE_INVENTORY_ONLY" if parsed["file_count"]>0 else "SOURCE_STOP_NO_FILES"
    except Exception as exc:
        result["status"]="SOURCE_STOP"
        result["reason"]=f"{type(exc).__name__}: {str(exc)[:250]}"
    out=Path(out_path);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("ROOST_SOURCE_V7",result["status"],"files",result.get("file_count",0))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",default="comparative_state/results/usgs_roost_source_v7.json")
    a=p.parse_args();main(a.out)
