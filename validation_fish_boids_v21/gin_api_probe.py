"""v21c bounded multi-endpoint GIN API diagnostic; metadata only.

No original fish trajectories or sensory response labels may be downloaded.
Expected 404/403 are scientific SOURCE_ACCESS_STOP, not job failure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT="https://gin.g-node.org/api/v1/repos/danionella/veith_et_al_2024"
ENDPOINTS={
    "repository_metadata": ROOT,
    "directory_default_ref": ROOT+"/contents",
    "behavior_master": ROOT+"/contents/behavior?ref=master",
    "behavior_main": ROOT+"/contents/behavior?ref=main",
}
MAX_RESPONSE_BYTES=1024*1024


def _entry_summary(item):
    if not isinstance(item,dict):
        return None
    name=item.get("name")
    path=item.get("path")
    typ=item.get("type")
    if not all(isinstance(v,str) for v in (name,path,typ)):
        return None
    if "/" in name or name in (".",".."):
        return None
    size=item.get("size")
    if size is not None and (not isinstance(size,int) or isinstance(size,bool) or size<0):
        return None
    return {"name":name,"path":path,"type":typ,"size":size,
            "provider_sha":item.get("sha") if isinstance(item.get("sha"),str) else None}


def probe(opener=urlopen):
    result={
       "status":"SOURCE_ACCESS_STOP",
       "study":"Veith_et_al_2024",
       "raw_fish_trajectory_bytes_read":False,
       "acoustic_or_movement_outcomes_read":False,
       "field_model_scores":None,
       "endpoint_records":[],
    }
    listed=False
    for key,url in ENDPOINTS.items():
        row={"key":key,"url":url}
        try:
            req=Request(url,headers={"User-Agent":"boids-v21c-gin-metadata/1.0","Accept":"application/json"})
            with opener(req,timeout=25) as response:
                blob=response.read(MAX_RESPONSE_BYTES+1)
        except HTTPError as exc:
            row.update({"result":"HTTP_STOP","http_status":exc.code})
            result["endpoint_records"].append(row)
            continue
        except (URLError,TimeoutError,OSError) as exc:
            row.update({"result":"NETWORK_STOP","error_type":type(exc).__name__})
            result["endpoint_records"].append(row)
            continue
        if len(blob)>MAX_RESPONSE_BYTES:
            row["result"]="OVERSIZE_STOP"
            result["endpoint_records"].append(row)
            continue
        row["response_sha256"]=hashlib.sha256(blob).hexdigest()
        try:
            parsed=json.loads(blob)
        except (ValueError,UnicodeDecodeError):
            row["result"]="NON_JSON_STOP"
            result["endpoint_records"].append(row)
            continue
        if key=="repository_metadata":
            if not isinstance(parsed,dict):
                row["result"]="UNEXPECTED_METADATA_SCHEMA"
            else:
                row["result"]="METADATA_OK"
                for field in ("name","full_name","default_branch","private","empty"):
                    if field in parsed and isinstance(parsed[field],(str,bool,int)):
                        row[field]=parsed[field]
        elif isinstance(parsed,list) and 0<len(parsed)<=1000:
            entries=[_entry_summary(x) for x in parsed]
            if None in entries:
                row["result"]="INVALID_DIRECTORY_ENTRY"
            else:
                row["result"]="DIRECTORY_LISTED"
                row["file_count"]=len(entries)
                row["entries"]=entries
                if key in ("behavior_master","behavior_main"):
                    listed=True
        else:
            row["result"]="UNEXPECTED_DIRECTORY_SCHEMA"
        result["endpoint_records"].append(row)
    if listed:
        result["status"]="METADATA_LISTED_NOT_DATA_ADMITTED"
    result["interpretation"]="Never infer repository or raw file absence from one failed API route. No original scientific scores were computed."
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    opts=ap.parse_args()
    data=probe()
    payload=json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__=="__main__":
    main()
