"""v5b frozen source-only structural admission of original 2024 8-fish trajectory CSVs.
Must be executed AFTER v5 protocol existed and BEFORE any movement response scoring.
Download original bytes to runner temp only. Never commit or upload animal trajectories.
"""
from __future__ import annotations
import csv,hashlib,json,os,tempfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib import request,error
from source_inventory import read_json,ZENODO
MAX_BYTES=70_000_000
RECORDINGS=tuple("Experimental_school_N=8_recording_"+str(i)+".csv" for i in range(6))
class SourceStop(Exception):
    def __init__(self,reason):super().__init__(reason)
def permitted_file_link(url):
    p=urlsplit(url)
    return p.scheme=="https" and p.netloc in ("zenodo.org","www.zenodo.org") and p.path.startswith(("/api/records/10890112/files/","/records/10890112/files/"))
def _open_url(url):
    req=request.Request(url,headers={"User-Agent":"boids-v5b-original-fish-source-gate/1.0",
                                    "Accept":"text/csv,application/octet-stream,*/*"})
    try:return request.urlopen(req,timeout=55)
    except error.HTTPError as ex:raise SourceStop("HTTP_"+str(ex.code)) from None
    except error.URLError as ex:raise SourceStop("NETWORK_"+type(ex.reason).__name__) from None
def _as_float(x):
    try:return float(x.strip())
    except ValueError:return None
def row_structure(path):
    with Path(path).open("r",encoding="utf-8-sig",newline="") as f:
        first=f.readline(131072)
        if not first or "\n" not in first:raise SourceStop("CSV_FIRSTLINE_STOP")
        row=next(csv.reader([first]))
        if not row or len(row)>1000:raise SourceStop("CSV_COLUMN_STOP")
        numeric=sum(_as_float(x) is not None for x in row)
        is_header=numeric<len(row)
        ncol=len(row)
        # source support not any animal behavior data
        return {"columns":ncol,"has_header":is_header,
                "header_columns":row if is_header and ncol<=80 else None,
                "first_row_numeric_fields":numeric}
def download_and_audit(item,path):
    name=str(item.get("key",""));size=int(item.get("size") or 0)
    ck=str(item.get("checksum") or "")
    url=str(item.get("links",{}).get("self",""))
    if name not in RECORDINGS or not permitted_file_link(url) or not ck.startswith("md5:") or size>MAX_BYTES or size<=0:
        raise SourceStop("ORIGINAL_SOURCE_METADATA_STOP")
    md5=hashlib.md5();sha=hashlib.sha256();total=0
    with _open_url(url) as r,Path(path).open("wb") as dst:
        while True:
            b=r.read(1024*1024)
            if not b:break
            total+=len(b)
            if total>MAX_BYTES:raise SourceStop("SOURCE_DOWNLOAD_CAP_STOP")
            md5.update(b);sha.update(b);dst.write(b)
    if total!=size or md5.hexdigest()!=ck.split(":",1)[1].lower():
        raise SourceStop("PROVIDER_MD5_SIZE_MISMATCH")
    with Path(path).open("rb") as f:
        nlines=0
        while True:
            b=f.read(2*1024*1024)
            if not b:break
            nlines+=b.count(b"\n")
    fmt=row_structure(path)
    if nlines<3000:raise SourceStop("SOURCE_TRIAL_TOO_SHORT")
    return {"filename":name,"provider_md5_verified":True,"bytes":total,
            "sha256":sha.hexdigest(),"n_newlines":nlines,**fmt}
def run():
    receipt={"version":"v5b_true_original_fish_source_schema_20261120",
            "source":"Puy 2024 Zenodo 10890112","n_required_trials":6,
            "download_cap_bytes_each":MAX_BYTES,
            "numerical_kinematic_effect_fitted":False,"source_rows_redistributed":False,
            "trial_files":[]}
    try:
        meta=read_json(ZENODO)
        files={f.get("key"):f for f in meta.get("files",[]) if isinstance(f,dict)}
        if not set(RECORDINGS).issubset(files):raise SourceStop("SOURCE_8FISH_6TRIALS_MISSING")
        with tempfile.TemporaryDirectory(prefix="boids_v5_source_") as d:
            for name in RECORDINGS:
                record=download_and_audit(files[name],Path(d)/name)
                receipt["trial_files"].append(record)
        if len(receipt["trial_files"])!=6:raise SourceStop("SIX_TRIAL_SOURCE_STOP")
        receipt["status"]="ORIGINAL_SIX_TRIAL_SOURCE_STRUCTURE_PASS"
    except SourceStop as ex:
        receipt["status"]="SOURCE_ACCESS_OR_SCHEMA_STOP"
        receipt["reason"]=str(ex)
    except (error.HTTPError,error.URLError,OSError,UnicodeError,csv.Error,ValueError) as ex:
        receipt["status"]="SOURCE_ACCESS_OR_SCHEMA_STOP"
        receipt["reason"]=type(ex).__name__
    return receipt
def main():
    res=run()
    path=Path("validation_fish_school_v5/results/trajectory_source_structure.json")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":res["status"],"reason":res.get("reason"),"n_verified":len(res["trial_files"]),
                      "trials":[{"name":x["filename"],"columns":x["columns"],
                                 "rows":x["n_newlines"],"header":x["header_columns"]}
                                for x in res["trial_files"]]}))
if __name__=="__main__":main()
