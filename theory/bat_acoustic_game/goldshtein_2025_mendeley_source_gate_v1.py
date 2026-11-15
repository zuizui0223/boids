"""Original Mendeley Data bat sound+movement SOURCE META ONLY.

No bat records, raw ZIPs, location fixes, acoustic waveforms or source
individual IDs read in this admission step. CC BY and file availability must
be verified. No authentication workaround.
"""
from __future__ import annotations
import hashlib,json,urllib.request,urllib.error,re
from pathlib import Path

OUT=Path(__file__).resolve().parent/"GOLDSHTEIN_2025_MOVEMENT_AUDIO_SOURCE_GATE_V1.json"
DOI="10.17632/k7pt2j84f7.1"
ROOT="https://api.data.mendeley.com"
DATASET_ID="k7pt2j84f7"
URIS={
  "dataset":ROOT+"/datasets/"+DATASET_ID+"?version=1",
  "public_dataset":ROOT+"/datasets/publics/"+DATASET_ID+"?version=1",
  "public_files":ROOT+"/datasets/publics/"+DATASET_ID+"/files?version=1",
  "published_versions":ROOT+"/datasets/"+DATASET_ID+"/versions"
}
HEAD={"User-Agent":"original-bat-movement-sound-source-admission/1.0",
      "Accept":"application/json"}
LIMIT=600_000

def get_json(url):
    req=urllib.request.Request(url,headers=HEAD)
    with urllib.request.urlopen(req,timeout=40) as response:
        data=response.read(LIMIT+1)
        if len(data)>LIMIT:raise ValueError("STOP_METADATA_RESPONSE_TOO_LARGE")
        j=json.loads(data.decode("utf-8-sig"))
        return j,hashlib.sha256(data).hexdigest()

def compact_file(obj):
    return {
       "file_id":obj.get("id") or obj.get("file_id"),
       "file_name":obj.get("filename") or obj.get("name") or obj.get("file_name"),
       "file_size_bytes":obj.get("size") or obj.get("file_size"),
       "sha256":obj.get("sha256_hash") or obj.get("sha256"),
       "md5":obj.get("md5") or obj.get("md5_hash"),
       "format":obj.get("mime_type"),
       "contains_id":bool(obj.get("id"))
    }

def main():
    result={
      "schema":1,"source_doi":DOI,"status":"NOT_CHECKED",
      "original_source_paper_doi":"10.1073/pnas.2407810122",
      "external_bat_species":"Rhinopoma microphyllum",
      "new_bat_measurements":False,
      "original_code_or_data_zip_bytes_opened":False,
      "original_participant_and_acoustic_rows_opened":False,
      "source_provider_permissions_not_bypassed":True,
      "api_metadata_responses":{},
      "original_files":[]
    }
    for name,url in URIS.items():
        item={"url":url,"status":"NOT_CHECKED"}
        try:
            raw,sha=get_json(url)
            item.update(status="PUBLIC_METADATA_READ",sha256=sha,
                       response_type="array" if isinstance(raw,list) else "object")
            if isinstance(raw,dict):
                item["keys"]=list(raw)
                item["id"]=raw.get("id")
                item["name"]=raw.get("name") or raw.get("title")
                item["doi"]=raw.get("doi")
                item["data_licence"]=raw.get("data_licence") or raw.get("license")
                nested=raw.get("files")
                if isinstance(nested,list):
                    item["n_files_embedded"]=len(nested)
                    item["files"]=[compact_file(v) for v in nested if isinstance(v,dict)][:30]
                    result["original_files"]+=item["files"]
                if "results" in raw and isinstance(raw["results"],list):
                    item["results_count"]=len(raw["results"])
            elif isinstance(raw,list):
                item["item_count"]=len(raw)
                item["files"]=[compact_file(v) for v in raw if isinstance(v,dict)][:50]
                if name=="public_files":result["original_files"]=item["files"]
        except Exception as e:
            item.update(status="STOP_ACCESS_OR_FORMAT",
                        error=type(e).__name__+":"+str(e)[:220])
        result["api_metadata_responses"][name]=item
        print("MENDELEY_SOURCE",name,item["status"],"keys",item.get("keys"),
              "nfiles",len(item.get("files",[])),"error",item.get("error"))
        if item.get("files"):
            print("ORIGINAL_PUBLISHED_FILE_LIST",name,item["files"])
    access=result["api_metadata_responses"].get("public_files",{})
    has=(access.get("status")=="PUBLIC_METADATA_READ"
         and any(x.get("file_name")=="Code.zip" for x in result["original_files"])
         and any(x.get("file_name")=="Data.zip" for x in result["original_files"]))
    result["status"]="PASS_PUBLIC_METADATA_SOURCE" if has else "STOP_EXTERNAL_SOURCE_NOT_ADMITTED"
    # Not a claim files can yet be downloaded; code and data binary downloads
    # require a separate authorized gate.
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("INDEPENDENT_BAT_SOURCE_ADMISSION",result["status"])
    return 0
if __name__=="__main__":
    raise SystemExit(main())
