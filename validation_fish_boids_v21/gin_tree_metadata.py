"""v21d GIN/GOGS Git tree metadata-only schema probe; no fish data.

Four predetermined API paths. No GET for any blob, /raw, /media or file.
"""
import argparse, hashlib, json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError,URLError

BASE="https://gin.g-node.org/api/v1/repos/danionella/veith_et_al_2024"
ENDPOINTS={
    "branch_master":BASE+"/branches/master",
    "root_tree_master":BASE+"/git/trees/master",
    "commit_master":BASE+"/git/commits/master",
    "git_tree_recursive":BASE+"/git/trees/master?recursive=true",
}
MAX_BODY=2*1024*1024


def probe(opener=urlopen):
    out={"status":"SOURCE_ACCESS_STOP","calls":[],"raw_original_data_read":False,"fish_behavior_scores":None}
    seen_tree=False
    for label,url in ENDPOINTS.items():
        row={"endpoint":label,"url":url}
        try:
            with opener(Request(url,headers={"User-Agent":"boids-v21d-metadata-only/1.0","Accept":"application/json"}),timeout=25) as r:
                data=r.read(MAX_BODY+1)
        except HTTPError as e:
            row.update({"status":"HTTP_STOP","http_code":e.code});out["calls"].append(row);continue
        except (URLError,OSError,TimeoutError) as e:
            row.update({"status":"NETWORK_STOP","error":type(e).__name__});out["calls"].append(row);continue
        if len(data)>MAX_BODY:
            row["status"]="OVERSIZE_STOP";out["calls"].append(row);continue
        row["sha256_response"]=hashlib.sha256(data).hexdigest()
        try: obj=json.loads(data)
        except (ValueError,UnicodeDecodeError):
            row["status"]="NON_JSON_STOP";out["calls"].append(row);continue
        if not isinstance(obj,dict):
            row["status"]="UNEXPECTED_SCHEMA";out["calls"].append(row);continue
        if label.startswith("root_tree") or label=="git_tree_recursive":
            tree=obj.get("tree")
            if isinstance(tree,list) and len(tree)<=4000:
                entries=[]
                for e in tree:
                    if not isinstance(e,dict) or not isinstance(e.get("path"),str) or not isinstance(e.get("type"),str):
                        entries=None;break
                    entries.append({k:e.get(k) for k in ("path","mode","type","sha","size")
                                    if isinstance(e.get(k),(str,int))})
                if entries is not None:
                    row["status"]="TREE_METADATA_OK"
                    row["truncated"]=obj.get("truncated")
                    row["entries"]=entries
                    seen_tree=True
                else: row["status"]="TREE_SCHEMA_STOP"
            else:row["status"]="TREE_SCHEMA_STOP"
        elif label=="branch_master":
            row["status"]="BRANCH_METADATA_OK" if isinstance(obj.get("name"),str) else "BRANCH_SCHEMA_STOP"
            if row["status"]=="BRANCH_METADATA_OK":
                row["name"]=obj.get("name")
                commit=obj.get("commit")
                if isinstance(commit,dict) and isinstance(commit.get("sha"),str):
                    row["commit_sha"]=commit["sha"]
        else:
            row["status"]="COMMIT_METADATA_OK" if "sha" in obj else "COMMIT_SCHEMA_STOP"
            if isinstance(obj.get("sha"),str):row["sha"]=obj["sha"]
        out["calls"].append(row)
    if seen_tree:out["status"]="TREE_METADATA_FOUND_NOT_RAW_ADMITTED"
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    payload=json.dumps(probe(),indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf8")
    print(payload,end="")


if __name__=="__main__":main()
