"""v5 source-only discovery: actual field fish tracks, audio-video archives.
NEVER read numeric fish movement outcomes in this script.
Access errors are SOURCE_STOP, not ecological negative results.
"""
from __future__ import annotations
import json, re
from urllib import request,error
from pathlib import Path
ZENODO="https://zenodo.org/api/records/10890112"
OSF="https://api.osf.io/v2/nodes/q8dz4/files/"
MAX_JSON=2_000_000
def read_json(url):
    if not url.startswith(("https://zenodo.org/api/","https://api.osf.io/v2/")):
        raise ValueError("Unapproved source host")
    try:
        req=request.Request(url,headers={"Accept":"application/json",
           "User-Agent":"boids-fish-schooling-source-audit/1.0"})
        with request.urlopen(req,timeout=25) as r:
            raw=r.read(MAX_JSON+1)
            if len(raw)>MAX_JSON:raise ValueError("Oversized source JSON")
            if "json" not in r.headers.get("content-type","").lower():
                raise ValueError("Non-JSON source response")
        return json.loads(raw.decode())
    except error.HTTPError as ex:raise RuntimeError("HTTP_"+str(ex.code)) from None
    except error.URLError as ex:raise RuntimeError("NETWORK_"+type(ex.reason).__name__) from None
def zenodo_metadata(get=read_json):
    j=get(ZENODO)
    fs=j.get("files",[])
    if not isinstance(fs,list) or not fs:raise ValueError("files missing")
    allowed=[]
    for f in fs:
        size=int(f.get("size",-1));key=str(f.get("key",""))
        if size<0 or not key or ".." in key:raise ValueError("invalid original file")
        ck=f.get("checksum","")
        allowed.append({"filename":key,"size_bytes":size,"checksum":ck,
                        "links_file_present":bool(f.get("links",{}).get("self"))})
    return {"source":"Puy et al 2024 Zenodo","doi":"10.5281/zenodo.10890112",
            "record_id":j.get("id"),"title":j.get("metadata",{}).get("title"),
            "license":j.get("metadata",{}).get("license",{}),
            "original_file_count":len(allowed),"files":allowed,
            "movement_data_opened":False,"candidate_status":"METADATA_ONLY"}
def osf_metadata(get=read_json):
    j=get(OSF)
    v=j.get("data",[])
    if not isinstance(v,list):raise ValueError("OSF storage metadata not list")
    entries=[{"provider":str(x.get("attributes",{}).get("name","")),
              "node_url":x.get("relationships",{}).get("files",{}).get("links",{}).get("related",{}).get("href")}
              for x in v]
    return {"source":"Mouy et al XAV OSF","url":"https://osf.io/q8dz4",
            "storage_provider_count":len(entries),"provider_links":entries,
            "file_outcomes_opened":False,"candidate_status":"METADATA_ONLY"}
def safe_get(fun):
    try:return {"status":"SOURCE_METADATA_PASS","result":fun()}
    except (RuntimeError,ValueError,TypeError,KeyError) as ex:
        return {"status":"SOURCE_METADATA_STOP","reason":str(ex)}
def run():
    return {"version":"v5_original_two-source_inventory_20261120",
      "never_pool_source_subjects":True,"fish_trajectories":safe_get(zenodo_metadata),
      "audio_video":safe_get(osf_metadata),
      "fish_motion_result":"NOT_TESTED","fish_call_response":"NOT_IDENTIFIED"}
if __name__=="__main__":
    result=run()
    p=Path("validation_fish_school_v5/results/source_inventory.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"trajectory_status":result["fish_trajectories"]["status"],
      "trajectory_reason":result["fish_trajectories"].get("reason"),
      "trajectory_files":result["fish_trajectories"].get("result",{}).get("original_file_count"),
      "osf_status":result["audio_video"]["status"],
      "osf_reason":result["audio_video"].get("reason"),
      "field_effect":"NOT_TESTED"}))
