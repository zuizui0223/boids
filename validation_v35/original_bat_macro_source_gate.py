#!/usr/bin/env python3
"""v35 original 49-species macro bat telemetry SOURCE ONLY, no outcomes."""
import argparse,csv,hashlib,io,json,urllib.error,urllib.request
from collections import Counter
from pathlib import Path

DOI="10.5061/dryad.qnk98sfhh"
ROOT="https://zenodo.org/records/5794471/files/"
FILES={
    "published_meta":{"file":"Meta_data_bat_home_ranges.csv","md5":"bf24d4f5bde98ee696a6f8f7745577a2"},
    "published_landscape":{"file":"Lanscape_data_bat_home_ranges.csv","md5":"a8a501e5e426cbf79447fda6b23f1e5e"},
}
OUT=Path("validation_v35/results/original_bat_telemetry_macro_source_v35.json")
MAX_BYTES=1_500_000
ID_TERMS=("study","source","reference","ref","paper","country","species","colony","roost","author","site","population","location","guild","continent")


def download_original(file,fetcher=None):
    url=ROOT+file["file"]+"?download=1"
    if fetcher is None:
        def fetcher(u):
            req=urllib.request.Request(u,headers={"Accept":"text/csv,text/plain,application/octet-stream,*/*;q=0.4",
                                                  "User-Agent":"boids-macro-telemetry-original-source-audit/1.0"})
            with urllib.request.urlopen(req,timeout=18) as r:
                return r.status,r.headers.get("Content-Type",""),r.read(MAX_BYTES+1)
    try: status,mime,payload=fetcher(url)
    except urllib.error.HTTPError as e:
        return {"status":"SOURCE_HTTP_STOP","http":e.code}
    except (urllib.error.URLError,OSError,TimeoutError) as e:
        return {"status":"SOURCE_TRANSPORT_STOP","error_type":type(e).__name__}
    kind="HTML" if payload.lstrip().lower().startswith((b"<!doctype",b"<html")) else "OTHER"
    ret={"source_url":url,"http":status,"mime":str(mime)[:100],
         "published_md5":file["md5"],"bytes_received":len(payload),
         "body_type":kind if kind=="HTML" else "CSV_OR_OTHER"}
    if len(payload)>MAX_BYTES or status!=200 or kind=="HTML":
        ret["status"]="ORIGINAL_CSV_NOT_RECEIVED"
        return ret
    md5=hashlib.md5(payload).hexdigest()
    ret["derived_md5"]=md5
    ret["derived_sha256"]=hashlib.sha256(payload).hexdigest()
    if md5!=file["md5"]:
        ret["status"]="ORIGINAL_MD5_MISMATCH_STOP"
        return ret
    ret["status"]="ORIGINAL_CSV_PINNED"
    try: ret["_csv_text"]=payload.decode("utf-8-sig")
    except UnicodeDecodeError:ret["_csv_text"]=payload.decode("latin-1")
    return ret


def structural_columns(text):
    first=text.splitlines()[0]
    delim=max((";",",","\t"),key=first.count)
    reader=csv.DictReader(io.StringIO(text),delimiter=delim)
    cols=[x.strip() for x in reader.fieldnames or []]
    counts=Counter()
    distinct={k:set() for k in cols if any(term in k.lower() for term in ID_TERMS)}
    rows=0
    for row in reader:
        rows+=1
        for k in distinct:
            value=(row.get(k) or "").strip()
            if value:
                counts[k]+=1
                if len(distinct[k])<10000: distinct[k].add(value)
    return {
       "delimiter":repr(delim),"columns":cols,"rows":rows,
       "structure_only_candidate_category_support":{
           k:{"nonempty_rows":counts[k],"distinct_labels_at_most_10000":len(v)}
           for k,v in distinct.items()},
       "numeric_home_range_movement_or_habitat_values_opened":False,
    }


def run(fetcher=None):
    out={"data_doi":DOI,"zenodo_record_id":5794471,"source_stage":"OUTCOME_BLIND_FILE_STRUCTURE_ONLY",
         "source_outcomes_opened":False,"ecological_model_fitted":False,
         "metadata_files":{}}
    for k,v in FILES.items():
        f=download_original(v,fetcher)
        if f["status"]=="ORIGINAL_CSV_PINNED":
            f.update(structural_columns(f.pop("_csv_text")))
        out["metadata_files"][k]=f
    keys=["published_meta","published_landscape"]
    if not all(out["metadata_files"][k]["status"]=="ORIGINAL_CSV_PINNED" for k in keys):
        out["status"]="ORIGINAL_MACRO_CSV_SOURCE_ACCESS_OR_INTEGRITY_STOP"
    else:
        a=out["metadata_files"][keys[0]];b=out["metadata_files"][keys[1]]
        shared=sorted(set(a["columns"]).intersection(b["columns"]))
        out["shared_original_field_names"]=shared
        out["status"]="ORIGINAL_MACRO_SOURCE_SCHEMA_AVAILABLE_NEEDS_JOIN_GRAIN_AUDIT"
    return out

if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",type=Path,default=OUT);args=a.parse_args()
    z=run();args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(z,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("V35_BAT_MACRO_SOURCE="+json.dumps({
        "status":z["status"],"shared_fields":z.get("shared_original_field_names"),
        "files":{k:{p:v.get(p) for p in ("status","bytes_received","derived_md5","derived_sha256","rows","columns","structure_only_candidate_category_support")}
                 for k,v in z["metadata_files"].items()}
    },sort_keys=True))
    assert z["source_outcomes_opened"] is False and z["ecological_model_fitted"] is False
