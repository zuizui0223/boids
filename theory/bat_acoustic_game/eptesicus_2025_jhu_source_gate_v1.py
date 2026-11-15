"""Source-only official JHU Dataverse bat acoustic/head-target metadata admission.

No animal values, full ZIPs, individual records, original audio/video positions
or full published scripts are opened/rehosted. All source read bounded.
"""
from __future__ import annotations
import hashlib,json,urllib.request,urllib.error,re
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"EPTESICUS_2025_JHU_SOURCE_METADATA_V1.json"
DOI="10.7281/T1WF3NZ7"
API="https://archive.data.jhu.edu/api"
META=API+"/datasets/:persistentId?persistentId=doi%3A"+DOI.replace("/","%2F")
CONTRACT=ROOT/"EPTESICUS_2025_INDEPENDENT_AUDIO_HEAD_TARGET_SOURCE_GATE_2026_11_15.md"
HEADERS={"User-Agent":"source-only-2025-perched-bat-dataverse-audit/1.0",
 "Accept":"application/json,text/markdown,text/plain,*/*"}

def read_bounded(url,limit=300_000,range_spec=None):
    header=HEADERS.copy()
    if range_spec:header["Range"]=range_spec
    request=urllib.request.Request(url,headers=header)
    with urllib.request.urlopen(request,timeout=45) as r:
        data=r.read(limit+1)
        if len(data)>limit:
            raise ValueError("STOP_MORE_THAN_PREDECLARED_ORIGINAL_SOURCE_READ_LIMIT")
        h={"status":r.status,"content_type":r.headers.get("Content-Type"),
            "content_length":r.headers.get("Content-Length"),
            "accept_ranges":r.headers.get("Accept-Ranges"),
            "content_range":r.headers.get("Content-Range"),
            "response_url":r.url}
        return data,h

def head_only(url):
    req=urllib.request.Request(url,headers=HEADERS,method="HEAD")
    with urllib.request.urlopen(req,timeout=35) as r:
        return {"status":r.status,"size_header":r.headers.get("Content-Length"),
                "accept_ranges":r.headers.get("Accept-Ranges"),
                "content_type":r.headers.get("Content-Type")}

def summarize_small_doc(data,name):
    text=data.decode("utf-8","replace")
    # Metadata only: line and source token incidence, no original text copied.
    words=("AudioData","VideoData","angle_data","pulse_data","pulse_freqs",
           "trial","time","frame","timestamp","head","mealworm",
           "clutter","target","bat","align","sync","yaw","pitch","roll")
    lines=text.splitlines()
    positions={}
    for word in words:
        indices=[i+1 for i,line in enumerate(lines) if word.lower() in line.lower()]
        if indices:positions[word]={"line_count":len(indices),"first_ten_lines":indices[:10]}
    fields=sorted(set(re.findall(r"(?:pulse|angle|video|audio|head|target|trial|time)[A-Za-z0-9_]{1,45}",text,re.I)))[:90]
    return {"name":name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
      "lines":len(lines),"matched_keyword_positions":positions,
      "code_or_doc_variable_name_candidates":fields,
      "text_or_source_values_exported":False}

def manifest(api):
    response,h=read_bounded(api,limit=700_000)
    result=json.loads(response)
    if result.get("status") not in ("OK","ok"):
        raise ValueError("STOP_DATAVERSE_SOURCE_NOT_OK")
    ver=result.get("data",{}).get("latestVersion",{})
    fs=ver.get("files") or []
    if not isinstance(fs,list) or not fs:
        raise ValueError("STOP_PUBLIC_ARCHIVE_NO_ORIGINAL_FILE_RECORDS")
    files=[]
    for rec in fs:
        item=rec.get("dataFile") or {}
        files.append({
           "id":item.get("id"),"name":item.get("filename") or rec.get("label"),
           "size":item.get("filesize"),"md5":item.get("md5"),
           "content_type":item.get("contentType"),"restricted":item.get("restricted"),
           "storage_identifier":None})
    return {"dataset_id":result.get("data",{}).get("id"),
            "dataset_persistent_id":result.get("data",{}).get("persistentUrl"),
            "version_number":ver.get("versionNumber"),
            "version_minor":ver.get("versionMinorNumber"),
            "license":ver.get("license"),"terms_of_use":(ver.get("termsOfUse") or "")[:100],
            "files":files,"source_metadata_response_sha256":hashlib.sha256(response).hexdigest(),
            "original_metadata_http":h}

def run():
    if not CONTRACT.exists():raise ValueError("STOP_PREOUTPUT_CONTRACT_NOT_FOUND")
    out={"schema":1,"date":"2026-11-15","original_paper_doi":"10.1121/10.0036252",
       "original_archived_dataset_doi":DOI,"public_source_metadata_url":META,
       "status":"NOT_CHECKED","new_bat_measurements":False,
       "source_animal_outcomes_opened":False,
       "raw_original_bat_IDs_or_trajectories_exported":False,
       "whole_audio_video_zip_downloaded":False,
       "original_files_rehosted":False,"rights_and_grouping_gate":False}
    try:
        info=manifest(META)
        out["original_dataset_catalog"]=info
        out["source_short_document_structure"]=[]
        out["large_original_zip_bounded_probes"]=[]
        for f in info["files"]:
            if not isinstance(f.get("id"),int) or not f.get("name"):continue
            name=f["name"]
            url=f"{API}/access/datafile/{f['id']}?format=original"
            if name=="README.md" or (re.match(r"Fig\d+_code\.m$",name) and f.get("size",100000)<=100000):
                try:
                    b,h=read_bounded(url,limit=100_000)
                    x=summarize_small_doc(b,name);x["response_status"]=h["status"]
                    out["source_short_document_structure"].append(x)
                except Exception as e:
                    out["source_short_document_structure"].append({"name":name,
                           "status":"STOP_SMALL_DOC_ACCESS","error":type(e).__name__+":"+str(e)[:190]})
            if name in ("AudioData.zip","VideoData.zip"):
                probe={"name":name,"source_file_id":f["id"],"status":"NOT_CHECKED"}
                try:probe["HEAD"]=head_only(url)
                except Exception as e:
                    probe["HEAD_error"]=type(e).__name__+":"+str(e)[:130]
                try:
                    raw,h=read_bounded(url,limit=4096,range_spec="bytes=0-4095")
                    probe.update(range_HTTP_status=h["status"],
                       content_range=h["content_range"],received_bytes=len(raw),
                       source_header_zip_magic=raw[:4]==b"PK\x03\x04",
                       first_4096_sha256=hashlib.sha256(raw).hexdigest(),
                       status="AUTHORIZED_206_ORIGINAL_FILE_RANGE" if h["status"]==206
                         else "SOURCE_RANGE_NOT_HONORED_OR_UNCONFIRMED")
                except Exception as e:
                    probe.update(status="STOP_ORIGINAL_ZIP_BOUNDED_ACCESS",
                      error=type(e).__name__+":"+str(e)[:190])
                out["large_original_zip_bounded_probes"].append(probe)
        detected={f["name"] for f in info["files"]}
        critical={"AudioData.zip","VideoData.zip","README.md"}
        out["original_files_present_in_catalog"]=sorted(detected)
        out["original_critical_files_listed"]=critical.issubset(detected)
        out["any_original_source_public_range_verified"]=any(
           x["status"]=="AUTHORIZED_206_ORIGINAL_FILE_RANGE"
           for x in out["large_original_zip_bounded_probes"])
        out["status"]="PASS_CATALOG_ORIGINAL_BAT_SOURCE_PREFLIGHT" if out["original_critical_files_listed"] \
            else "STOP_MISSING_AUDIO_VIDEO_README_SOURCE"
    except Exception as e:
        out["status"]="STOP_DATAVERSE_ORIGINAL_SOURCE_CATALOG"
        out["error"]=type(e).__name__+":"+str(e)[:240]
    return out

if __name__=="__main__":
    result=run()
    OUT.write_text(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
    print("EPTESICUS_DATAVERSE_SOURCE_STATUS",result["status"])
    if "original_dataset_catalog" in result:
        print("SOURCE_FILE_CATALOG",json.dumps(result["original_dataset_catalog"]["files"],sort_keys=True))
        print("SOURCE_LICENSE",json.dumps(result["original_dataset_catalog"].get("license")))
        print("SOURCE_DOCUMENT_SCHEMA",json.dumps(result["source_short_document_structure"],sort_keys=True))
        print("SOURCE_ZIP_ACCESS",json.dumps(result["large_original_zip_bounded_probes"],sort_keys=True))
    else:print("SOURCE_STOP",result.get("error"))
