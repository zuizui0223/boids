"""v25 source-only original 2026 school lateral-line Dryad metadata gate.

Never fetch fish trajectory, experiment outcomes, native MAT, raw ZIP, or any
download endpoint. This is metadata; not fish motion or auditory data analysis.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse,urljoin
from urllib.request import Request,urlopen

DOI="10.5061/dryad.gxd25482b"
ROOT="https://datadryad.org"
URL=ROOT+"/api/v2/datasets/doi%3A10.5061%2Fdryad.gxd25482b"
MAX_METADATA=2*1024*1024
MAX_LISTING=3*1024*1024

class SourceStop(Exception):
    pass


def safe_link(text,root=ROOT):
    if not isinstance(text,str) or not text:
        raise SourceStop("UNSUPPORTED_OR_EMPTY_METADATA_LINK")
    url=urljoin(root,text)
    u=urlparse(url)
    if u.scheme!="https" or u.netloc!="datadryad.org" or not u.path.startswith("/api/v2/"):
        raise SourceStop("UNTRUSTED_OR_NON_API_DOWNLOAD_LINK")
    if "download" in u.path.lower() or "/files/" in u.path.lower() and "/download" in u.path.lower():
        raise SourceStop("RAW_DATA_DOWNLOAD_NOT_PERMITTED")
    return url


def only_json(url,opener=urlopen,limit=MAX_METADATA):
    req=Request(safe_link(url),headers={"User-Agent":"boids-v25-source-metadata-only/1.0",
         "Accept":"application/json"})
    try:
        with opener(req,timeout=25) as h:
            actual=h.geturl() if hasattr(h,"geturl") else url
            safe_link(actual)
            raw=h.read(limit+1)
    except HTTPError as exc:
        raise SourceStop("HTTP_"+str(exc.code)) from exc
    except (URLError,TimeoutError,OSError) as exc:
        raise SourceStop("NETWORK_OR_TIMEOUT_"+type(exc).__name__) from exc
    if len(raw)>limit:
        raise SourceStop("SOURCE_METADATA_TOO_LARGE")
    try:parsed=json.loads(raw)
    except (UnicodeError,ValueError) as exc:
        raise SourceStop("SOURCE_METADATA_NOT_JSON") from exc
    if not isinstance(parsed,dict):
        raise SourceStop("SOURCE_METADATA_UNEXPECTED_SCHEMA")
    return parsed,hashlib.sha256(raw).hexdigest()


def _links(obj):
    x=obj.get("_links",{})
    return x if isinstance(x,dict) else {}


def link_for(obj,*names):
    links=_links(obj)
    for name in names:
        item=links.get(name)
        if isinstance(item,dict) and isinstance(item.get("href"),str):
            return safe_link(item["href"])
    return None


def metadata_only(opener=urlopen):
    report={
       "status":"SOURCE_ACCESS_STOP",
       "original_paper":"Peterson et al 2026 60-fish mechanosensory lateral-line manipulation",
       "dryad_doi":DOI,
       "original_api_metadata_url":URL,
       "original_fish_values_or_files_downloaded":False,
       "original_fish_movement_models_fitted":False,
       "treatment_effect_reestimated":False,
    }
    try:
        obj,digest=only_json(URL,opener)
        # Official response may hold identifier in alternate fields:
        id_string=obj.get("identifier",obj.get("doi"))
        if not isinstance(id_string,str) or DOI.lower() not in id_string.lower():
            raise SourceStop("DOI_IDENTITY_NOT_VERIFIED")
        report["dataset_metadata_sha256"]=digest
        report["published_source_identifier"]=id_string
        for k in ("title","license","storageSize","publicationDate","publication_date","versionNumber"):
            if isinstance(obj.get(k),(str,int,float,bool)):
                report[k]=obj[k]
        linked=link_for(obj,"stash:versions","stash:version","versions","stash:latestVersion")
        if not linked:
            raise SourceStop("NO_OFFICIAL_VERSION_METADATA_LINK")
        version_obj, version_hash=only_json(linked,opener)
        report["version_metadata_sha256"]=version_hash
        # A version collection may have _embedded; no uncontrolled iteration.
        items=version_obj.get("_embedded",{})
        if isinstance(items,dict):
            versions=items.get("stash:versions") or items.get("versions")
        else: versions=None
        if isinstance(versions,list) and versions:
            if len(versions)>50:
                raise SourceStop("TOO_MANY_VERSIONS")
            v=versions[-1]
            if not isinstance(v,dict):
                raise SourceStop("VERSION_SCHEMA_STOP")
            version_obj=v
        version_id=version_obj.get("id",version_obj.get("versionId"))
        if not isinstance(version_id,(str,int)):
            raise SourceStop("NO_OFFICIAL_VERSION_ID")
        report["provider_version_id"]=str(version_id)
        listing_url=ROOT+"/api/v2/versions/"+str(version_id)+"/files"
        files_obj,files_hash=only_json(listing_url,opener,MAX_LISTING)
        report["file_metadata_sha256"]=files_hash
        possible=files_obj.get("_embedded",{})
        if isinstance(possible,dict):
            filelist=possible.get("stash:files") or possible.get("files")
        else:filelist=None
        if not isinstance(filelist,list):
            filelist=files_obj.get("files")
        if not isinstance(filelist,list) or not 0<len(filelist)<=200:
            raise SourceStop("NO_BOUNDED_PUBLISHED_FILES")
        actual_count=files_obj.get("count",files_obj.get("total"))
        if isinstance(actual_count,int) and actual_count>len(filelist):
            raise SourceStop("PAGINATION_INCOMPLETE")
        files=[]
        for item in filelist:
            if not isinstance(item,dict):
                raise SourceStop("SOURCE_FILE_SCHEMA_STOP")
            name=item.get("path",item.get("name",item.get("fileName")))
            if not isinstance(name,str) or not name or name.startswith("/") or ".." in name:
                raise SourceStop("SOURCE_FILE_NAME_STOP")
            size=item.get("size",item.get("fileSize"))
            if size is not None and (not isinstance(size,int) or isinstance(size,bool) or size<0):
                raise SourceStop("SOURCE_FILE_SIZE_STOP")
            files.append({"name":name,"size_bytes":size,
                          "mime_type":item.get("mimeType") if isinstance(item.get("mimeType"),str) else None,
                          "provider_checksum_if_listed":item.get("digest") if isinstance(item.get("digest"),str) else None})
        report["files"]=files
        report["file_count"]=len(files)
        report["status"]="METADATA_ONLY_NOT_YET_TRAJECTORIES"
    except SourceStop as exc:
        report["stop_reason"]=str(exc)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    result=metadata_only()
    payload=json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    print(payload,end="")


if __name__=="__main__":main()
