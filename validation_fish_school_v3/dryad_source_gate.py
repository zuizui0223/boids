"""Strict original-source structural admission for Ota et al. Dryad fish chorus.
Source-only: do not read signal values or create behavioral effects.
401/403/ambiguous schemas are scientific SOURCE_STOP, not negative ecology.
"""
from __future__ import annotations
import csv, hashlib, io, json, re, zipfile
from pathlib import Path
from urllib import request, error, parse

DOI="10.5061/dryad.zkh1893qn"
BASE="https://datadryad.org/api/v2/"
URL=BASE+"datasets/"+parse.quote("doi:"+DOI,safe="")
FILES={"q25_autoChorusDetect4.zip":2_000_000,"mic_location_xycoordinate.csv":30_000}

class SourceStop(Exception):
    def __init__(self,code,message):
        super().__init__(message)
        self.code=code

def read(url,limit=3_000_000):
    if not url.startswith(BASE):
        raise SourceStop("SOURCE_URL_STOP","outside official Dryad API")
    req=request.Request(url,headers={"User-Agent":"fish-school-v3-source-gate/1.0",
                                    "Accept":"application/json,application/octet-stream,*/*"})
    try:
        with request.urlopen(req,timeout=30) as resp:
            b=resp.read(limit+1)
    except error.HTTPError as exc:
        raise SourceStop("SOURCE_ACCESS_STOP","HTTP "+str(exc.code)) from None
    except error.URLError as exc:
        raise SourceStop("SOURCE_TRANSPORT_STOP",type(exc.reason).__name__) from None
    if len(b)>limit:
        raise SourceStop("SOURCE_SIZE_STOP","fixed byte cap exceeded")
    return b

def json_get(url):
    try: return json.loads(read(url))
    except (ValueError,UnicodeDecodeError):
        raise SourceStop("SOURCE_SCHEMA_STOP","official reply is not JSON") from None

def collection(payload,name):
    for key,val in payload.get("_embedded",{}).items():
        if name in key.lower() and isinstance(val,list):
            return val
    for key in (name,name+"s"):
        if isinstance(payload.get(key),list):return payload[key]
    raise SourceStop("SOURCE_SCHEMA_STOP",name+" collection absent")

def numeric_id(record,kind):
    if record.get("id") is not None: return int(record["id"])
    href=record.get("_links",{}).get("self",{}).get("href","")
    m=re.search(r"/"+kind+r"/(\d+)",href)
    if not m: raise SourceStop("SOURCE_SCHEMA_STOP",kind+" id missing")
    return int(m.group(1))

def file_name(record):
    return str(record.get("path") or record.get("filename") or record.get("name") or "").split("/")[-1]

def zip_structure(payload):
    try: z=zipfile.ZipFile(io.BytesIO(payload))
    except zipfile.BadZipFile:
        raise SourceStop("SOURCE_FORMAT_STOP","chorus archive not a ZIP") from None
    records=z.infolist()
    if not records or sum(x.file_size for x in records)>15_000_000:
        raise SourceStop("SOURCE_SIZE_STOP","ZIP structure exceeds fixed expanded cap")
    if any(x.filename.startswith("/") or ".." in x.filename.split("/") for x in records):
        raise SourceStop("SOURCE_FORMAT_STOP","unsafe ZIP entry")
    return {"n_zip_members":len(records),
            "extensions":{k:sum(Path(x.filename).suffix.lower()==k for x in records)
                          for k in sorted({Path(x.filename).suffix.lower() for x in records})}}

def receiver_structure(payload):
    try: data=list(csv.DictReader(payload.decode("utf-8-sig").splitlines()))
    except (UnicodeDecodeError,csv.Error):
        raise SourceStop("SOURCE_FORMAT_STOP","receiver coordinate CSV invalid") from None
    if len(data)<5: raise SourceStop("SOURCE_SUPPORT_STOP","less than five receiver rows")
    return {"receiver_coordinate_rows":len(data),"receiver_columns":list(data[0])}

def run():
    out={"version":"v3_original_source_only","doi":DOI,
         "acoustic_outcomes_read":False,"field_effect_fitted":False,
         "original_files_redistributed":False,"files":{}}
    try:
        json_get(URL)
        versions=collection(json_get(URL+"/versions"),"version")
        v=max(versions,key=lambda z:int(z.get("versionNumber") or z.get("id") or 0))
        version=numeric_id(v,"versions")
        out["published_version_id"]=version
        source_files=collection(json_get(BASE+"versions/"+str(version)+"/files"),"file")
        by_name={file_name(x):x for x in source_files}
        if not set(FILES).issubset(by_name):
            raise SourceStop("SOURCE_SCHEMA_STOP","required two official source members absent")
        for name,limit in FILES.items():
            item=by_name[name]
            reported=int(item.get("size") or 0)
            if reported>limit:
                raise SourceStop("SOURCE_SIZE_STOP",name+" exceeds official cap")
            payload=read(BASE+"files/"+str(numeric_id(item,"files"))+"/download",limit)
            digest=item.get("digest")
            alg=str(item.get("digestType") or "").lower().replace("-","")
            if digest and alg in ("md5","sha256"):
                if hashlib.new(alg,payload).hexdigest().lower()!=str(digest).lower():
                    raise SourceStop("SOURCE_DIGEST_STOP",name+" provider digest mismatch")
            record={"original_nbytes":len(payload),"computed_sha256":hashlib.sha256(payload).hexdigest(),
                    "provider_digest_verified":bool(digest and alg in ("md5","sha256"))}
            record.update(zip_structure(payload) if name.endswith(".zip") else receiver_structure(payload))
            out["files"][name]=record
        out["status"]="SOURCE_STRUCTURE_PASS_NOT_FISH_RESULT"
    except SourceStop as exc:
        out["status"]=exc.code
        out["stop_reason"]=str(exc)
    return out

if __name__=="__main__":
    result=run()
    p=Path("validation_fish_school_v3/results/ota_original_source_gate.json")
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"stop_reason":result.get("stop_reason"),"doi":DOI}))
