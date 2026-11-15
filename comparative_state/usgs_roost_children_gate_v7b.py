#!/usr/bin/env python3
"""Inventory original USGS P922KDU6 ScienceBase child records without GPS access.

Parent item metadata alone has one XML, so child catalog is required. Report
only child titles, IDs, source license and file metadata. No original rows,
individual identifiers, coordinates or ecological effects are downloaded.
"""
import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

PARENT="601478d0d34edf5c66ea0ead"
URL=f"https://www.sciencebase.gov/catalog/items?parentId={PARENT}&format=json&max=100"


def validate_url(url):
    p=urllib.parse.urlparse(url)
    return p.scheme=="https" and p.hostname in ("www.sciencebase.gov","sciencebase.gov") and p.path=="/catalog/items"


def parse_children(payload):
    if not isinstance(payload,dict): raise ValueError("catalog children not JSON object")
    raw=payload.get("items",[])
    if not isinstance(raw,list): raise ValueError("invalid child array")
    child=[]
    for e in raw:
        if not isinstance(e,dict):continue
        fs=e.get("files",[])
        if not isinstance(fs,list):fs=[]
        files=[]
        for f in fs:
            if isinstance(f,dict):
                files.append({"name":f.get("name"),"size":f.get("size"),"checksum":f.get("checksum",f.get("md5"))})
        child.append({"id":e.get("id"),"title":e.get("title"),"files":files,"num_direct_files":len(files),"parentId":e.get("parentId")})
    return {"child_items":len(child),"entries":child,"total_direct_files":sum(e["num_direct_files"] for e in child),
            "verified_true_movement_origins":False,"verified_matched_choice_sets":False,
            "verified_distinct_biological_cohort":False}


def main(out):
    result={"schema":"ecostate.usgs_roost_children_v7b","source_doi":"10.5066/P922KDU6","parent_id":PARENT,
            "source_url":URL,"status":"SOURCE_STOP","actual_bird_values_opened":False,
            "model_effects_estimated":False}
    try:
        if not validate_url(URL):raise ValueError("source catalog URL blocked")
        req=urllib.request.Request(URL,headers={"User-Agent":"ecostate-usgs-child-catalog-v7b/1.0", "Accept":"application/json"})
        with urllib.request.urlopen(req,timeout=30) as r:
            b=r.read(1_500_001)
        if len(b)>1_500_000:raise ValueError("source metadata too large")
        v=parse_children(json.loads(b))
        result.update(v)
        result["status"]="SOURCE_CHILDREN_INVENTORY_ONLY" if v["child_items"] else "SOURCE_STOP_NO_CHILDREN"
    except Exception as exc:
        result["status"]="SOURCE_STOP"
        result["reason"]=f"{type(exc).__name__}: {str(exc)[:250]}"
    dst=Path(out);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("USGS_ROOST_CHILDREN_V7B",result["status"],"children",result.get("child_items",0),"files",result.get("total_direct_files",0))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",default="comparative_state/results/usgs_roost_children_v7b.json")
    main(ap.parse_args().out)
