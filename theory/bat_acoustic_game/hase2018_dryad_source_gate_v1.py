"""2018 same-species archived ultrasound source admission: metadata/headers ONLY.

Official Dryad DOI 10.5061/dryad.4f99c46; original published CC0
SoundFile.zip ~614MB. NO original .bin acoustic amplitudes, bat IDs or
waveform-curvature outcomes read here. Range requests are tiny and bounded.
"""
from __future__ import annotations
import hashlib,json,urllib.request,urllib.error,re
from pathlib import Path
DOI="10.5061/dryad.4f99c46"
BASE="https://datadryad.org/api/v2/"
OUT=Path(__file__).resolve().parent/"HASE2018_ULTRASOUND_SOURCE_METADATA_V1.json"
U=[
 BASE+"datasets/doi%3A10.5061%2Fdryad.4f99c46",
 BASE+"datasets/doi:10.5061/dryad.4f99c46",
]
HEADERS={"User-Agent":"source-only-original-bat-acoustic-preflight-v1/1.0",
         "Accept":"application/json,*/*"}
def request(url,method="GET",range_value=None,maxread=128000):
    headers=HEADERS.copy()
    if range_value:headers["Range"]=range_value
    req=urllib.request.Request(url,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=35) as r:
        if method=="HEAD":return {"status":r.status,"headers":dict(r.headers)}
        b=r.read(maxread+1)
        if len(b)>maxread:raise ValueError("STOP_RESPONSE_EXCEEDS_PREDECLARED_CAP")
        return {"status":r.status,"headers":dict(r.headers),"data":b}
def safe_meta(url):
    record={"url":url,"status":"NOT_CHECKED"}
    try:
        r=request(url,maxread=100000)
        data=r["data"]
        j=json.loads(data)
        record.update(status="METADATA_AVAILABLE",http_status=r["status"],
                      sha256=hashlib.sha256(data).hexdigest(),
                      keys=list(j.keys()),
                      id=j.get("id"),doi=j.get("identifier"),title=j.get("title"),
                      publicationDate=j.get("publicationDate"),
                      license=j.get("license"),
                      relationships=j.get("_links"),
                      file_count=j.get("fileCount"),
                      total_size=j.get("totalSize"),
                      data_files=j.get("dataFiles"))
        # Do not preserve curator/private identities beyond source article DOI.
    except Exception as e:
        record.update(status="STOP_API_ACCESS",error=type(e).__name__+":"+str(e)[:230])
    return record

def main():
    out={"schema":1,"status":"SOURCE_ONLY_NO_AUDIO_BYTES",
         "new_bat_measurements":False,
         "original_audio_observations_opened":False,
         "no_raw_bat_ID_or_audio_redistribution":True,
         "source_doi":DOI,
         "metadata_attempts":[],
         "file_catalog":None,
         "file_byte_access":None}
    for url in U:
        x=safe_meta(url)
        out["metadata_attempts"].append(x)
        print("DRYAD_DATASET",x["status"],url,"error",x.get("error"))
        if x["status"]=="METADATA_AVAILABLE":
            links=x.get("relationships") or {}
            print("DATASET_LICENSE",x.get("license"),"TOTAL_SIZE",x.get("total_size"),
                  "LINK_KEYS",list(links))
            # Files can be present via inline data or HAL link in _links
            uri=None
            for k,v in links.items():
                if "file" in k.lower():
                    if isinstance(v,dict):
                        uri=v.get("href") or v.get("url")
                    elif isinstance(v,str):
                        uri=v
                    break
            if uri is None:
                # Dryad dataset records point to an immutable version. Files
                # are listed under the version, not dataset/<doi>/files.
                version_link=links.get("stash:version") or {}
                version_url=(version_link.get("href") if isinstance(version_link,dict) else version_link)
                if not version_url:
                    raise ValueError("STOP_NO_SOURCE_VERSION_LINK")
                if version_url.startswith("/"):version_url="https://datadryad.org"+version_url
                print("DATASET_VERSION_ROUTE",version_url)
                version_data=json.loads(request(version_url,maxread=200000)["data"])
                version_links=version_data.get("_links") or {}
                print("VERSION_LINK_KEYS",list(version_links))
                for k,v in version_links.items():
                    if "file" in k.lower():
                        uri=(v.get("href") if isinstance(v,dict) else v)
                        break
                if not uri:
                    uri=version_url.rstrip("/")+"/files"
            if uri.startswith("/"):uri="https://datadryad.org"+uri
            row={"url":uri,"status":"NOT_CHECKED"}
            try:
                resp=request(uri,maxread=150000)
                j=json.loads(resp["data"])
                arr=j.get("_embedded",{}).get("stash:files") or j.get("data") or j.get("files") or []
                if isinstance(arr,dict):arr=arr.get("data") or []
                row.update(status="FILE_CATALOG_AVAILABLE",n_files=len(arr),
                           file_metadata=[{
                             "id":z.get("id"),
                             "filename":z.get("path") or z.get("filename"),
                             "size":z.get("size") or z.get("filesize"),
                             "checksum":z.get("digest") or z.get("md5") or z.get("sha256"),
                             "links":z.get("_links")} for z in arr[:30] if isinstance(z,dict)],
                           keys=list(j.keys()))
            except Exception as e:
                row.update(status="STOP_FILE_CATALOG",error=type(e).__name__+":"+str(e)[:230])
            out["file_catalog"]=row
            print("FILE_CATALOG",row["status"],"keys",row.get("keys"),
                  "n",row.get("n_files"),"files",row.get("file_metadata"),"error",row.get("error"))
            z=(row.get("file_metadata") or [])
            for f in z:
                if "SoundFile" not in str(f.get("filename")): continue
                id=f.get("id")
                if not id:continue
                endpoint=BASE+"files/"+str(id)+"/download"
                access={"url":endpoint,"status":"NOT_CHECKED"}
                try:
                    h=request(endpoint,method="HEAD")
                    access.update(status="HEAD_AVAILABLE",http_status=h["status"],
                                  content_type=h["headers"].get("Content-Type"),
                                  length=h["headers"].get("Content-Length"),
                                  accept_ranges=h["headers"].get("Accept-Ranges"))
                    # Get only first 1024 bytes if provider honors the range,
                    # and stop before any full-file streaming on HTTP200.
                    a=request(endpoint,range_value="bytes=0-1023",maxread=1024)
                    access["range_status"]=a["status"]
                    access["range_content_range"]=a["headers"].get("Content-Range")
                    access["range_returned_bytes"]=len(a["data"])
                    access["range_magic_zip"]=a["data"][:4].hex()
                    access["status"]="TINY_ORIGINAL_HEADER_OBTAINED" if a["status"]==206 else "STOP_NO_RANGE_VERIFIED"
                except Exception as e:
                    access.update(status="STOP_BYTE_ACCESS",error=type(e).__name__+":"+str(e)[:230])
                out["file_byte_access"]=access
                print("SOURCE_BYTE_ACCESS",access)
            break
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print("SOURCE_METADATA_GATE_RESULT",out["status"])
    return 0

if __name__=="__main__":raise SystemExit(main())
